"""Vercel ASGI entrypoint for the ResultScope 2.0.

The application remains defined in ``main.py`` so local uvicorn usage and the
existing test surface stay unchanged. This module only applies cloud-safe,
fail-closed defaults before importing the application.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def _truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def _prepare_vercel_runtime() -> None:
    """Set safe preview defaults and reject local-only runtime choices.

    Vercel starts a fresh process for the function, so this runs before
    ``config.settings`` is constructed by ``main``. Explicit unsafe values are
    rejected rather than silently changed, which keeps the provider and storage
    boundaries fail-closed.
    """

    if not os.getenv("VERCEL"):
        return

    defaults = {
        "APP_ENV": "preview",
        "KNOWLEDGE_MODE": "release",
        "LOCAL_DEMO_MODE": "false",
        "PROVIDER_NETWORK_ENABLED": "false",
        "STORAGE_BACKEND": "auto",
    }
    for name, value in defaults.items():
        os.environ.setdefault(name, value)

    # Landing and sample library deploy without secrets; live mode enforces them.

    storage_backend = os.getenv("STORAGE_BACKEND", "auto").strip().lower()
    if storage_backend == "sqlite":
        raise RuntimeError("STORAGE_BACKEND=sqlite is not supported on Vercel; configure Upstash or use auto.")

    if _truthy(os.getenv("PROVIDER_NETWORK_ENABLED")):
        if len(os.getenv("SESSION_SIGNING_KEY", "")) < 32:
            raise RuntimeError("SESSION_SIGNING_KEY must contain at least 32 characters for live cloud use.")
        if len(os.getenv("DEMO_ACCESS_CODE", "")) < 12:
            raise RuntimeError("DEMO_ACCESS_CODE must contain at least 12 characters for live cloud use.")
        for required in ("UPSTASH_REDIS_REST_URL", "UPSTASH_REDIS_REST_TOKEN", "PROVIDER_BUDGET_CYCLE_ID"):
            if not os.getenv(required, "").strip():
                raise RuntimeError(f"{required} is required for live cloud use.")


_prepare_vercel_runtime()

from main import app  # noqa: E402  (guard must run before settings import)

__all__ = ["app"]
