from __future__ import annotations

import threading
import time
from typing import Any

from fastapi import APIRouter, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel, Field, field_validator

from config import settings
from services import provider_adapters
from services.admin_auth import (
    DEFAULT_ADMIN_USERNAME,
    AdminSession,
    clear_session,
    configured_admin_hash,
    create_session,
    get_session,
    local_demo_enabled,
    login_allowed,
    require_csrf,
    set_session_cookies,
    verify_password,
)
from services.provider_config import (
    PROVIDER_CATALOG,
    ProviderConfigError,
    ProviderSettingsStore,
    RuntimeProvider,
    public_snapshot,
)


router = APIRouter()
store = ProviderSettingsStore()


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=1, max_length=256)


class ProviderUpdate(BaseModel):
    provider_id: str = Field(min_length=1, max_length=64)
    enabled: bool = False
    model: str = Field(default="", max_length=160)
    timeout_seconds: float = Field(default=60, ge=1, le=300)
    api_key: str | None = Field(default=None, max_length=4096)
    clear_api_key: bool = False

    @field_validator("api_key")
    @classmethod
    def clean_api_key(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None


class ConfigUpdate(BaseModel):
    providers: dict[str, ProviderUpdate]


class TestRequest(BaseModel):
    live: bool = False


_test_windows: dict[str, tuple[float, int]] = {}
_test_lock = threading.Lock()


def _json_error(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"error": True, "code": code, "message": message})


def _client_key(request: Request) -> str:
    return request.client.host if request.client and request.client.host else "unknown-client"


def _test_allowed(request: Request) -> bool:
    key = _client_key(request)
    now = time.monotonic()
    limit = max(1, settings.ADMIN_TEST_RATE_LIMIT_REQUESTS)
    window = max(1, settings.ADMIN_TEST_RATE_LIMIT_WINDOW_SECONDS)
    with _test_lock:
        started, count = _test_windows.get(key, (now, 0))
        if now - started >= window:
            _test_windows[key] = (now, 1)
            return True
        if count >= limit:
            return False
        _test_windows[key] = (started, count + 1)
        return True


def _require_session(request: Request) -> AdminSession | JSONResponse:
    if not local_demo_enabled():
        return _json_error(404, "admin_unavailable", "Admin Settings is available only in explicit local-demo mode.")
    session_result = get_session(request)
    if session_result is None:
        return _json_error(401, "admin_auth_required", "Admin authentication is required.")
    _, session = session_result
    return session


def _require_write(request: Request) -> AdminSession | JSONResponse:
    result = _require_session(request)
    if isinstance(result, JSONResponse):
        return result
    if not require_csrf(request, result):
        return _json_error(403, "csrf_failed", "The admin form token is missing or expired.")
    return result


def _runtime_provider(slot: str, state: dict[str, Any]) -> RuntimeProvider:
    row = state["providers"].get(slot)
    if not isinstance(row, dict):
        raise ProviderConfigError("Unknown provider slot.")
    definition = PROVIDER_CATALOG[row["provider_id"]]
    return RuntimeProvider(
        row["provider_id"], definition.base_url, row["model"], row.get("api_key") or "",
        float(row["timeout_seconds"]), bool(row["enabled"]), definition.protocol,
    )


@router.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page() -> HTMLResponse:
    if not local_demo_enabled():
        return HTMLResponse("Admin Settings is disabled outside local-demo mode.", status_code=404)
    return HTMLResponse(
        """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Administrator sign in | ResultScope Laboratory Assistant</title><link rel="stylesheet" href="/static/css/style.css"><link rel="stylesheet" href="/static/css/admin.css"></head><body class="admin-shell"><main class="admin-panel"><a class="brand" href="/"><img src="/static/img/mark.svg" alt="" width="36" height="36"><span class="brand-copy"><strong>ResultScope</strong><span>Laboratory Assistant</span></span></a><h1>Administrator sign in</h1><p class="admin-muted">This page is available only in local-demo mode. Never use the default password on an online deployment.</p><form id="admin-login-form"><label for="admin-username">Username</label><input id="admin-username" name="username" autocomplete="username" required value="admin"><label for="admin-password">Password</label><input id="admin-password" name="password" type="password" autocomplete="current-password" required><button type="submit" class="primary-button">Sign in</button><p id="admin-login-error" class="admin-error" role="alert"></p></form><a class="admin-back" href="/">Return to workspace</a></main><script src="/static/js/admin.js" defer></script></body></html>"""
    )


@router.get("/admin/settings", response_class=HTMLResponse, response_model=None)
async def admin_settings_page(request: Request) -> HTMLResponse | RedirectResponse:
    if not local_demo_enabled():
        return HTMLResponse("Admin Settings is disabled outside local-demo mode.", status_code=404)
    if get_session(request) is None:
        return RedirectResponse("/admin/login", status_code=303)
    return HTMLResponse(
        """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Provider settings | ResultScope Laboratory Assistant</title><link rel="stylesheet" href="/static/css/style.css"><link rel="stylesheet" href="/static/css/admin.css"></head><body class="admin-shell"><main class="admin-panel admin-settings"><header class="admin-heading"><div><a class="brand" href="/"><img src="/static/img/mark.svg" alt="" width="36" height="36"><span class="brand-copy"><strong>ResultScope</strong><span>Laboratory Assistant</span></span></a><h1>Provider settings</h1><p class="admin-muted">Settings are stored only for local demo use. Existing API keys are never displayed.</p></div><button id="admin-logout" class="secondary-button" type="button">Log out</button></header><div id="admin-status" class="admin-status" role="status"></div><section id="provider-list" class="provider-list" aria-live="polite"></section><div class="provider-actions admin-save-row"><button id="admin-save" class="primary-button" type="button">Save settings</button><span class="admin-muted">Save does not call a provider. Tests are separate and use a mock by default.</span></div><a class="admin-back" href="/">Return to workspace</a></main><script src="/static/js/admin.js" defer></script></body></html>"""
    )


@router.post("/api/v1/admin/login")
async def admin_login(payload: LoginRequest, request: Request, response: Response):
    if not local_demo_enabled():
        return _json_error(404, "admin_unavailable", "Admin Settings is available only in explicit local-demo mode.")
    if not login_allowed(_client_key(request)):
        return _json_error(429, "admin_login_rate_limited", "Too many login attempts. Try again later.")
    valid = hmac_compare_username(payload.username, DEFAULT_ADMIN_USERNAME) and verify_password(payload.password, configured_admin_hash())
    if not valid:
        return _json_error(401, "admin_login_failed", "The username or password is incorrect.")
    token, session = create_session(payload.username)
    set_session_cookies(response, request, token, session)
    return {"ok": True, "csrf_token": session.csrf_token, "expires_in": max(60, settings.ADMIN_SESSION_TTL_SECONDS)}


def hmac_compare_username(supplied: str, expected: str) -> bool:
    import hmac

    return hmac.compare_digest(supplied, expected)


@router.get("/api/v1/admin/csrf")
async def admin_csrf(request: Request):
    result = _require_session(request)
    if isinstance(result, JSONResponse):
        return result
    return {"csrf_token": result.csrf_token, "expires_at": result.expires_at}


@router.post("/api/v1/admin/logout")
async def admin_logout(request: Request, response: Response):
    result = _require_write(request)
    if isinstance(result, JSONResponse):
        return result
    clear_session(response, request)
    return {"ok": True}


@router.get("/api/v1/admin/config")
async def admin_config(request: Request):
    result = _require_session(request)
    if isinstance(result, JSONResponse):
        return result
    try:
        return public_snapshot(store.read())
    except ProviderConfigError as exc:
        return _json_error(503, "admin_config_unavailable", str(exc))


@router.put("/api/v1/admin/config")
async def admin_update_config(payload: ConfigUpdate, request: Request):
    result = _require_write(request)
    if isinstance(result, JSONResponse):
        return result
    if set(payload.providers) != {"llm", "ocr", "systemone"}:
        return _json_error(422, "invalid_provider_slots", "Update llm, ocr, and systemone together.")
    try:
        updates = {
            slot: update.model_dump(exclude_none=True)
            for slot, update in payload.providers.items()
        }
        state = store.update_many(updates)
        return {"ok": True, "saved": True, "config": public_snapshot(state)}
    except ProviderConfigError as exc:
        return _json_error(422, "invalid_provider_config", str(exc))


@router.post("/api/v1/admin/providers/{slot}/test")
async def admin_test_provider(slot: str, payload: TestRequest, request: Request):
    result = _require_write(request)
    if isinstance(result, JSONResponse):
        return result
    if slot not in {"llm", "ocr", "systemone"}:
        return _json_error(404, "unknown_provider_slot", "Unknown provider slot.")
    if not _test_allowed(request):
        return _json_error(429, "admin_test_rate_limited", "Provider tests are rate limited to protect quota.")
    try:
        provider = _runtime_provider(slot, store.read())
        result = await provider_adapters.test_provider(provider, live=payload.live)
        return {"ok": True, **result, "message": "Live test used one provider request." if payload.live else "Mocked test used no provider request."}
    except ProviderConfigError as exc:
        return _json_error(503, "admin_config_unavailable", str(exc))
    except provider_adapters.ProviderAdapterError as exc:
        return _json_error(exc.status_code, exc.code, exc.message)
