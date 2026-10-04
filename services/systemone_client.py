from __future__ import annotations

from typing import Any

import httpx

from config import settings
from services.provider_adapters import (
    ProviderAdapterError,
    build_systemone_payload,
    parse_systemone_response,
)
from services.provider_budget import (
    AttemptReservation,
    ProviderBudgetError,
    SQLiteAttemptBudget,
    finish_provider_attempt,
    reserve_provider_attempt,
)
from services.provider_config import ProviderConfigError, ProviderSettingsStore, RuntimeProvider


class SystemOneError(Exception):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


def _finish(reservation: AttemptReservation | None, outcome: str, reason_code: str | None = None) -> None:
    if reservation is None:
        return
    try:
        finish_provider_attempt(reservation, outcome, reason_code)
    except ProviderBudgetError:
        # A consumed reservation is never restored when outcome persistence fails.
        pass


def _configured_provider() -> RuntimeProvider | None:
    try:
        state = ProviderSettingsStore().read()
        row = state["providers"]["systemone"]
        if not row.get("enabled") or not row.get("shadow_mode") or not row.get("api_key"):
            return None
        from services.provider_config import PROVIDER_CATALOG

        definition = PROVIDER_CATALOG[row["provider_id"]]
        return RuntimeProvider(
            row["provider_id"], definition.base_url, row["model"], row["api_key"],
            float(row["timeout_seconds"]), True, definition.protocol,
        )
    except (KeyError, ProviderConfigError, TypeError, ValueError):
        return None


async def shadow_decide(message: str, python_intent: str, python_allowed: bool) -> dict[str, Any] | None:
    """Observe a Python decision without changing the authoritative route."""
    if not settings.SYSTEMONE_SHADOW_ENABLED or not python_allowed:
        return None
    provider = _configured_provider()
    if provider is None:
        return None
    try:
        payload = build_systemone_payload(
            {"message": message, "python_intent": python_intent},
            {
                "scope": {
                    "type": "choice",
                    "instructions": "Choose the applicable ResultScope route for this laboratory request.",
                    "criteria": {"lab": "laboratory explanation", "business": "laboratory business information", "mixed": "both", "other": "not allowed"},
                }
            },
        )
        reservation = reserve_provider_attempt("systemone", "systemone_shadow")
        SQLiteAttemptBudget.ensure_network_enabled()
        async with httpx.AsyncClient(timeout=provider.timeout_seconds, follow_redirects=False) as client:
            response = await client.post(
                provider.base_url,
                headers={"apikey": provider.api_key, "Content-Type": "application/json"},
                json=payload,
            )
        if response.status_code >= 400:
            raise SystemOneError("provider_request_failed", "SystemOne shadow request was rejected.")
        result = parse_systemone_response(response.json())
        _finish(reservation, "succeeded")
        return {"python_intent": python_intent, "shadow": result}
    except ProviderBudgetError as exc:
        _finish(locals().get("reservation"), "blocked", exc.code)
        raise SystemOneError(exc.code, exc.message) from exc
    except (httpx.TimeoutException, httpx.HTTPError) as exc:
        _finish(locals().get("reservation"), "failed", "provider_unavailable")
        raise SystemOneError("provider_unavailable", "SystemOne shadow response was unavailable.") from exc
    except (ValueError, ProviderAdapterError) as exc:
        _finish(locals().get("reservation"), "failed", "provider_invalid_response")
        raise SystemOneError("provider_invalid_response", "SystemOne shadow response was invalid.") from exc
    except SystemOneError as exc:
        _finish(locals().get("reservation"), "failed", exc.code)
        raise
