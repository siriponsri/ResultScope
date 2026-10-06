"""Short-lived encrypted, browser-carried conversation state; no server disk writes.

Tokens are bound to the signed HttpOnly session cookie. They provide integrity and
confidentiality, not durable memory. Refresh/reset drops the UI's copy.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
import time
from typing import Any

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from config import settings

_LOCAL_KEY = secrets.token_bytes(32)
_AAD = b"resultscope:conversation:v2"


class StateError(Exception):
    pass


def _key() -> bytes:
    if settings.SESSION_SIGNING_KEY:
        return hashlib.sha256(("v2:" + settings.SESSION_SIGNING_KEY).encode()).digest()
    if os.getenv("VERCEL"):
        raise StateError("Set SESSION_SIGNING_KEY before starting a conversation.")
    return _LOCAL_KEY


def seal(data: dict[str, Any], session_id: str, purpose: str = "conversation") -> str:
    payload = {"data": data, "session": session_id, "purpose": purpose,
               "expires": int(time.time()) + settings.CONTEXT_TTL_SECONDS}
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode()
    if len(raw) > 100_000:
        raise StateError("Conversation is full. Start a new chat.")
    nonce = secrets.token_bytes(12)
    return base64.urlsafe_b64encode(nonce + AESGCM(_key()).encrypt(nonce, raw, _AAD)).decode()


def unseal(token: str | None, session_id: str, purpose: str = "conversation") -> dict[str, Any]:
    if not token:
        return {"history": [], "report": None}
    try:
        if len(token) > 140_000:
            raise ValueError
        raw = base64.b64decode(token, altchars=b"-_", validate=True)
        payload = json.loads(AESGCM(_key()).decrypt(raw[:12], raw[12:], _AAD))
        if (payload["session"] != session_id or payload["purpose"] != purpose
                or payload["expires"] <= time.time() or not isinstance(payload["data"], dict)):
            raise ValueError
        return payload["data"]
    except Exception:
        raise StateError("This conversation has expired or changed. Start a new chat.") from None
