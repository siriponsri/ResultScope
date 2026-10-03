from __future__ import annotations

from typing import Any

import httpx

from config import settings
from services.provider_adapters import (
    ProviderAdapterError,
    build_systemone_payload,
    parse_systemone_response,
)
from services.provider_config import ProviderConfigError, ProviderSettingsStore, RuntimeProvider


class SystemOneError(Exception):
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
        async with httpx.AsyncClient(timeout=provider.timeout_seconds) as client:
            response = await client.post(
                provider.base_url,
                headers={"apikey": provider.api_key, "Content-Type": "application/json"},
                json=payload,
            )
        if response.status_code >= 400:
            raise SystemOneError("SystemOne shadow request was rejected.")
        result = parse_systemone_response(response.json())
        return {"python_intent": python_intent, "shadow": result}
    except (httpx.HTTPError, ValueError, ProviderAdapterError) as exc:
        raise SystemOneError("SystemOne shadow response was invalid or unavailable.") from exc
