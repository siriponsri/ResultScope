"""Run mock-only provider probes through the shared adapter boundary.

Live mode is explicit and still requires the provider network guard, an existing
active cycle, and a configured provider. This script never creates a cycle.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import settings
from services import provider_adapters, systemone_client
from services.provider_config import PROVIDER_CATALOG, RuntimeProvider, runtime_provider


SLOTS = ("llm", "ocr", "systemone")


def _error_result(slot: str, error: provider_adapters.ProviderAdapterError) -> dict[str, Any]:
    attempt = error.provider_attempt
    return {
        "slot": slot,
        "status": "error",
        "error_code": error.code,
        "network_called": bool(attempt and attempt.outcome != "blocked"),
        "quota_used": bool(attempt),
    }


def _provider_for(slot: str) -> RuntimeProvider:
    if slot == "llm":
        return runtime_provider(
            "llm",
            fallback_base_url=settings.LLM_BASE_URL,
            fallback_model=settings.LLM_MODEL,
            fallback_key=settings.LLM_API_KEY,
            fallback_timeout=settings.LLM_TIMEOUT_SECONDS,
        )
    if slot == "ocr":
        return runtime_provider(
            "ocr",
            fallback_base_url=settings.VISION_BASE_URL or settings.LLM_BASE_URL,
            fallback_model=settings.VISION_MODEL,
            fallback_key=settings.VISION_API_KEY if settings.VISION_ENABLED else "",
            fallback_timeout=settings.VISION_TIMEOUT_SECONDS,
        )
    configured = systemone_client._configured_provider()
    if configured is not None:
        return configured
    definition = PROVIDER_CATALOG["openthai_systemone"]
    return RuntimeProvider(
        definition.provider_id,
        definition.base_url,
        definition.default_model,
        "",
        60.0,
        False,
        definition.protocol,
    )


async def _run(slots: tuple[str, ...], live: bool) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for slot in slots:
        provider = _provider_for(slot)
        try:
            result = await provider_adapters.test_provider(
                provider,
                live=live,
                source_path="runner",
            )
            results.append(
                {
                    "slot": slot,
                    "status": result["status"],
                    "provider_id": result["provider_id"],
                    "network_called": bool(result["network_called"]),
                    "quota_used": bool(result["quota_used"]),
                }
            )
        except provider_adapters.ProviderAdapterError as exc:
            results.append(_error_result(slot, exc))
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slot", choices=(*SLOTS, "all"), default="all")
    parser.add_argument("--live", action="store_true", help="Use live transport; never creates a budget cycle.")
    args = parser.parse_args()
    slots = SLOTS if args.slot == "all" else (args.slot,)
    results = asyncio.run(_run(slots, args.live))
    print(json.dumps({"live_requested": args.live, "results": results}, sort_keys=True))
    return 1 if any(row["status"] == "error" for row in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
