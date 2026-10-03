from __future__ import annotations

import asyncio
import json

import httpx
from fastapi.testclient import TestClient

from main import app
from routers import admin as admin_router
from services import admin_auth, provider_adapters, systemone_client
from services.admin_auth import clear_rate_limits, hash_password
from services.provider_config import ProviderSettingsStore


def _enable_local_demo(monkeypatch, tmp_path):
    monkeypatch.setattr("config.settings.LOCAL_DEMO_MODE", True)
    monkeypatch.setattr("config.settings.APP_ENV", "development")
    monkeypatch.setattr("config.settings.ADMIN_SETTINGS_PATH", str(tmp_path / "admin_settings.json"))
    monkeypatch.setattr("config.settings.ADMIN_SECRET_STORAGE_KEY", "synthetic-admin-storage-key")
    monkeypatch.setattr("config.settings.ADMIN_PASSWORD_HASH", hash_password("synthetic-password"))
    admin_router._test_windows.clear()
    admin_router.store = ProviderSettingsStore()
    clear_rate_limits()


def _login(client: TestClient):
    response = client.post(
        "/api/v1/admin/login",
        json={"username": "admin", "password": "synthetic-password"},
    )
    assert response.status_code == 200
    return response.json()["csrf_token"]


def _config_payload(key: str | None = None):
    return {
        "providers": {
            "llm": {
                "provider_id": "typhoon_llm", "enabled": bool(key),
                "model": "typhoon-v2.5-30b-a3b-instruct", "timeout_seconds": 30,
                "api_key": key,
            },
            "ocr": {
                "provider_id": "typhoon_ocr", "enabled": bool(key),
                "model": "typhoon-ocr", "timeout_seconds": 30, "api_key": key,
            },
            "systemone": {
                "provider_id": "openthai_systemone", "enabled": False,
                "model": "openthai-systemone", "timeout_seconds": 30, "api_key": key,
            },
        }
    }


def test_admin_is_not_available_without_explicit_local_demo(monkeypatch):
    monkeypatch.setattr("config.settings.LOCAL_DEMO_MODE", False)
    assert TestClient(app).get("/admin/login").status_code == 404
    assert TestClient(app).get("/api/v1/admin/config").status_code == 404
    assert TestClient(app).post("/api/v1/admin/login", json={"username": "admin", "password": "1234"}).status_code == 404


def test_default_password_is_rejected_for_online_or_production(monkeypatch):
    monkeypatch.setattr("config.settings.LOCAL_DEMO_MODE", True)
    monkeypatch.setattr("config.settings.APP_ENV", "production")
    client = TestClient(app)
    response = client.post("/api/v1/admin/login", json={"username": "admin", "password": "1234"})
    assert response.status_code == 404


def test_default_password_is_available_only_in_explicit_local_demo(monkeypatch):
    monkeypatch.delenv("VERCEL", raising=False)
    monkeypatch.setattr("config.settings.LOCAL_DEMO_MODE", True)
    monkeypatch.setattr("config.settings.APP_ENV", "development")
    monkeypatch.setattr("config.settings.ADMIN_PASSWORD_HASH", "")
    assert TestClient(app).post("/api/v1/admin/login", json={"username": "admin", "password": "1234"}).status_code == 200


def test_admin_login_cookie_csrf_logout_and_unauthorized_access(monkeypatch, tmp_path):
    _enable_local_demo(monkeypatch, tmp_path)
    client = TestClient(app)
    assert client.get("/api/v1/admin/config").status_code == 401
    login = client.post("/api/v1/admin/login", json={"username": "admin", "password": "synthetic-password"})
    assert login.status_code == 200
    cookie = login.headers["set-cookie"]
    assert "resultscope_admin_session=" in cookie
    assert "HttpOnly" in cookie
    assert "SameSite=lax" in cookie
    assert "Secure" not in cookie
    csrf = login.json()["csrf_token"]
    assert client.get("/api/v1/admin/config").status_code == 200
    no_csrf = client.put("/api/v1/admin/config", json=_config_payload())
    assert no_csrf.status_code == 403
    logout = client.post("/api/v1/admin/logout", headers={"X-CSRF-Token": csrf})
    assert logout.status_code == 200
    assert client.get("/api/v1/admin/config").status_code == 401


def test_admin_protected_endpoints_reject_anonymous_requests(monkeypatch, tmp_path):
    _enable_local_demo(monkeypatch, tmp_path)
    client = TestClient(app)
    assert client.get("/api/v1/admin/csrf").status_code == 401
    assert client.put("/api/v1/admin/config", json=_config_payload()).status_code == 401
    assert client.post("/api/v1/admin/logout").status_code == 401
    assert client.post("/api/v1/admin/providers/llm/test", json={"live": False}).status_code == 401


def test_admin_https_cookie_session_expiry_and_login_rate_limit(monkeypatch, tmp_path):
    _enable_local_demo(monkeypatch, tmp_path)
    https_client = TestClient(app, base_url="https://testserver")
    login = https_client.post("/api/v1/admin/login", json={"username": "admin", "password": "synthetic-password"})
    assert login.status_code == 200
    assert "Secure" in login.headers["set-cookie"]

    now = [1000.0]
    monkeypatch.setattr(admin_auth.time, "time", lambda: now[0])
    expiring_client = TestClient(app)
    assert expiring_client.post("/api/v1/admin/login", json={"username": "admin", "password": "synthetic-password"}).status_code == 200
    assert expiring_client.get("/api/v1/admin/config").status_code == 200
    now[0] += admin_auth.settings.ADMIN_SESSION_TTL_SECONDS + 1
    assert expiring_client.get("/api/v1/admin/config").status_code == 401

    monkeypatch.setattr("config.settings.ADMIN_LOGIN_RATE_LIMIT_REQUESTS", 1)
    clear_rate_limits()
    rate_limited_client = TestClient(app)
    assert rate_limited_client.post("/api/v1/admin/login", json={"username": "admin", "password": "wrong"}).status_code == 401
    assert rate_limited_client.post("/api/v1/admin/login", json={"username": "admin", "password": "wrong"}).status_code == 429


def test_admin_config_is_write_only_local_persistent_and_save_does_not_test_provider(monkeypatch, tmp_path):
    _enable_local_demo(monkeypatch, tmp_path)
    client = TestClient(app)
    csrf = _login(client)
    secret = "typhoon-secret-must-not-escape"

    async def unexpected_test(*args, **kwargs):
        raise AssertionError("save must not call a provider")

    monkeypatch.setattr(provider_adapters, "test_provider", unexpected_test)
    saved = client.put(
        "/api/v1/admin/config",
        headers={"X-CSRF-Token": csrf},
        json=_config_payload(secret),
    )
    assert saved.status_code == 200
    body = saved.json()
    assert secret not in json.dumps(body)
    assert body["config"]["providers"]["llm"]["configured"] is True
    raw = (tmp_path / "admin_settings.json").read_text(encoding="utf-8")
    assert secret not in raw
    fresh = ProviderSettingsStore().read()
    assert fresh["providers"]["llm"]["api_key"] == secret
    fetched = client.get("/api/v1/admin/config")
    assert secret not in fetched.text
    assert "api_key" not in fetched.json()["providers"]["llm"]


def test_admin_can_delete_a_key_and_rejects_arbitrary_provider_ids(monkeypatch, tmp_path):
    _enable_local_demo(monkeypatch, tmp_path)
    client = TestClient(app)
    csrf = _login(client)
    saved = client.put("/api/v1/admin/config", headers={"X-CSRF-Token": csrf}, json=_config_payload("synthetic-delete-key"))
    assert saved.status_code == 200

    clear_payload = _config_payload()
    for row in clear_payload["providers"].values():
        row["clear_api_key"] = True
    deleted = client.put("/api/v1/admin/config", headers={"X-CSRF-Token": csrf}, json=clear_payload)
    assert deleted.status_code == 200
    assert deleted.json()["config"]["providers"]["llm"]["configured"] is False
    assert ProviderSettingsStore().read()["providers"]["llm"]["api_key"] is None

    invalid = _config_payload()
    invalid["providers"]["llm"]["provider_id"] = "https://attacker.invalid/collect"
    rejected = client.put("/api/v1/admin/config", headers={"X-CSRF-Token": csrf}, json=invalid)
    assert rejected.status_code == 422
    assert ProviderSettingsStore().read()["providers"]["llm"]["provider_id"] == "typhoon_llm"


def test_mock_provider_test_is_separate_bounded_and_does_not_use_network(monkeypatch, tmp_path):
    _enable_local_demo(monkeypatch, tmp_path)
    client = TestClient(app)
    csrf = _login(client)
    assert client.put("/api/v1/admin/config", headers={"X-CSRF-Token": csrf}, json=_config_payload("synthetic-key")).status_code == 200

    async def fail_network(*args, **kwargs):
        raise AssertionError("mock test must not use network")

    monkeypatch.setattr(httpx, "AsyncClient", fail_network)
    tested = client.post(
        "/api/v1/admin/providers/llm/test",
        headers={"X-CSRF-Token": csrf},
        json={"live": False},
    )
    assert tested.status_code == 200
    assert tested.json()["status"] == "mocked"
    assert tested.json()["network_called"] is False
    assert tested.json()["quota_used"] is False


def test_provider_contracts_are_separate_and_systemone_parser_is_fail_closed():
    typhoon = provider_adapters.RuntimeProvider("typhoon_ocr", "https://api.opentyphoon.ai/v1", "typhoon-ocr", "key", 10, True, "typhoon_ocr_document")
    payload = provider_adapters.build_typhoon_ocr_payload(typhoon, b"synthetic-image", "image/png")
    assert payload["model"] == "typhoon-ocr"
    assert payload["messages"][0]["content"][1]["type"] == "image_url"
    systemone = provider_adapters.build_systemone_payload("synthetic state", {"scope": {"type": "noul", "instructions": "lab?"}})
    assert set(systemone) == {"state", "questions"}
    parsed = provider_adapters.parse_systemone_response({"model": "openthai-systemone", "answers": {"scope": {"type": "noul", "noul": 0.9}}, "usage": {"output_tokens": 0}})
    assert parsed["answers"]["scope"]["noul"] == 0.9
    try:
        provider_adapters.parse_systemone_response({"answers": {"scope": {"type": "free_text", "text": "unsafe"}}})
    except provider_adapters.ProviderAdapterError as exc:
        assert exc.code == "systemone_invalid_response"
    else:
        raise AssertionError("invalid SystemOne answer must be rejected")


def test_systemone_shadow_never_replaces_python_route(monkeypatch):
    calls = []

    async def fake_shadow(message, python_intent, python_allowed):
        calls.append((message, python_intent, python_allowed))
        return {"shadow": {"answers": {"scope": {"choice": "other"}}}}

    monkeypatch.setattr(systemone_client, "shadow_decide", fake_shadow)
    from services.intent_router import route_intent

    python_decision = route_intent("Hb 10.8 g/dL")
    assert python_decision.kind == "lab"
    assert python_decision.allowed is True
    asyncio.run(systemone_client.shadow_decide("Hb 10.8 g/dL", python_decision.kind, python_decision.allowed))
    assert calls[0][1:] == ("lab", True)
    assert route_intent("Help me write Python").kind == "unrelated"
