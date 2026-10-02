from __future__ import annotations

import asyncio
import hashlib
import hmac
import secrets
import threading
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncIterator

from config import settings

_PROCESS_KEY = secrets.token_bytes(32)
_REGISTRY_GUARD = threading.Lock()


def _signing_key() -> bytes:
    configured = settings.SESSION_SIGNING_KEY
    return configured.encode("utf-8") if configured else _PROCESS_KEY


def new_session_id() -> str:
    return str(uuid.uuid4())


def sign_session_id(session_id: str) -> str:
    signature = hmac.new(_signing_key(), session_id.encode("ascii"), hashlib.sha256).hexdigest()
    return f"{session_id}.{signature}"


def verify_session_cookie(value: str | None) -> str | None:
    if not isinstance(value, str) or value.count(".") != 1:
        return None
    session_id, supplied = value.split(".", 1)
    try:
        uuid.UUID(session_id)
    except (ValueError, AttributeError):
        return None
    expected = hmac.new(_signing_key(), session_id.encode("ascii"), hashlib.sha256).hexdigest()
    return session_id if hmac.compare_digest(expected, supplied) else None


@dataclass
class _LockEntry:
    loop: asyncio.AbstractEventLoop
    lock: asyncio.Lock
    users: int = 0


class SessionLockPool:
    def __init__(self) -> None:
        self._entries: dict[tuple[int, str], _LockEntry] = {}

    @asynccontextmanager
    async def lock(self, session_id: str) -> AsyncIterator[None]:
        loop = asyncio.get_running_loop()
        key = (id(loop), session_id)
        with _REGISTRY_GUARD:
            entry = self._entries.get(key)
            if entry is None or entry.loop is not loop:
                entry = _LockEntry(loop, asyncio.Lock())
                self._entries[key] = entry
            entry.users += 1
        try:
            async with entry.lock:
                yield
        finally:
            with _REGISTRY_GUARD:
                entry.users -= 1
                if entry.users == 0 and self._entries.get(key) is entry:
                    del self._entries[key]


session_locks = SessionLockPool()
