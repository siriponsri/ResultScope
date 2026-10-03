from __future__ import annotations

import json
import logging
import os
import sqlite3
import threading
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import httpx

from config import settings

logger = logging.getLogger(__name__)


class ConversationStoreError(Exception):
    pass


class ConversationStore(ABC):
    @abstractmethod
    async def get(self, session_id: str) -> list[dict[str, str]]:
        raise NotImplementedError

    @abstractmethod
    async def set(self, session_id: str, history: list[dict[str, str]]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def clear(self, session_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def save_reset_recovery(self, session_id: str, payload: dict[str, Any]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_reset_recovery(self, session_id: str) -> dict[str, Any] | None:
        raise NotImplementedError

    @abstractmethod
    async def clear_reset_recovery(self, session_id: str) -> None:
        raise NotImplementedError


class MemoryConversationStore(ConversationStore):
    def __init__(self) -> None:
        self._data: dict[str, tuple[float, list[dict[str, str]]]] = {}
        self._reset_recovery: dict[str, dict[str, Any]] = {}

    def _prune(self) -> None:
        now = time.time()
        expired = [key for key, (expires, _) in self._data.items() if expires <= now]
        for key in expired:
            self._data.pop(key, None)

    async def get(self, session_id: str) -> list[dict[str, str]]:
        self._prune()
        item = self._data.get(session_id)
        return list(item[1]) if item else []

    async def set(self, session_id: str, history: list[dict[str, str]]) -> None:
        self._data[session_id] = (time.time() + settings.SESSION_TTL_SECONDS, list(history))

    async def clear(self, session_id: str) -> None:
        self._data.pop(session_id, None)

    async def save_reset_recovery(self, session_id: str, payload: dict[str, Any]) -> None:
        self._reset_recovery[session_id] = json.loads(json.dumps(payload, ensure_ascii=False))

    async def get_reset_recovery(self, session_id: str) -> dict[str, Any] | None:
        payload = self._reset_recovery.get(session_id)
        if not payload or payload.get("state") != "pending":
            return None
        return json.loads(json.dumps(payload, ensure_ascii=False))

    async def clear_reset_recovery(self, session_id: str) -> None:
        self._reset_recovery.pop(session_id, None)


class SQLiteConversationStore(ConversationStore):
    """Simple local persistence for development.

    SQLite is intentionally NOT presented as a durable Vercel production database because
    serverless filesystems are ephemeral. It is excellent for local coursework and demos.
    """

    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, timeout=5)
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def _init_db(self) -> None:
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    session_id TEXT PRIMARY KEY,
                    history_json TEXT NOT NULL,
                    updated_at INTEGER NOT NULL,
                    expires_at INTEGER NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS reset_recovery (
                    session_id TEXT PRIMARY KEY,
                    payload_json TEXT NOT NULL,
                    updated_at INTEGER NOT NULL
                )
                """
            )
            conn.commit()

    async def get(self, session_id: str) -> list[dict[str, str]]:
        now = int(time.time())
        with self._lock, self._connect() as conn:
            row = conn.execute(
                "SELECT history_json, expires_at FROM conversations WHERE session_id = ?",
                (session_id,),
            ).fetchone()
            if not row:
                return []
            history_json, expires_at = row
            if expires_at <= now:
                conn.execute("DELETE FROM conversations WHERE session_id = ?", (session_id,))
                conn.commit()
                return []
        try:
            data = json.loads(history_json)
            return data if isinstance(data, list) else []
        except json.JSONDecodeError:
            return []

    async def set(self, session_id: str, history: list[dict[str, str]]) -> None:
        now = int(time.time())
        expires = now + settings.SESSION_TTL_SECONDS
        payload = json.dumps(history, ensure_ascii=False)
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                INSERT INTO conversations(session_id, history_json, updated_at, expires_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    history_json = excluded.history_json,
                    updated_at = excluded.updated_at,
                    expires_at = excluded.expires_at
                """,
                (session_id, payload, now, expires),
            )
            conn.commit()

    async def clear(self, session_id: str) -> None:
        with self._lock, self._connect() as conn:
            conn.execute("DELETE FROM conversations WHERE session_id = ?", (session_id,))
            conn.commit()

    async def save_reset_recovery(self, session_id: str, payload: dict[str, Any]) -> None:
        now = int(time.time())
        with self._lock, self._connect() as conn:
            conn.execute(
                """
                INSERT INTO reset_recovery(session_id, payload_json, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    payload_json = excluded.payload_json,
                    updated_at = excluded.updated_at
                """,
                (session_id, json.dumps(payload, ensure_ascii=False), now),
            )
            conn.commit()

    async def get_reset_recovery(self, session_id: str) -> dict[str, Any] | None:
        with self._lock, self._connect() as conn:
            row = conn.execute(
                "SELECT payload_json FROM reset_recovery WHERE session_id = ?",
                (session_id,),
            ).fetchone()
        if not row:
            return None
        try:
            payload = json.loads(row[0])
        except (TypeError, json.JSONDecodeError) as exc:
            raise ConversationStoreError("Conversation reset recovery is unavailable.") from exc
        if not isinstance(payload, dict) or payload.get("state") != "pending":
            return None
        return payload

    async def clear_reset_recovery(self, session_id: str) -> None:
        with self._lock, self._connect() as conn:
            conn.execute("DELETE FROM reset_recovery WHERE session_id = ?", (session_id,))
            conn.commit()


class UpstashConversationStore(ConversationStore):
    """Tiny Redis-over-HTTP adapter requiring no extra dependency.

    Configure UPSTASH_REDIS_REST_URL/TOKEN. Messages are stored with a TTL and no user
    identity. For real healthcare deployment, add formal privacy/security controls first.
    """

    def __init__(self, url: str, token: str) -> None:
        self.url = url.rstrip("/")
        self.token = token
        self._headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def _key(self, session_id: str) -> str:
        return f"resultscope:session:{session_id}"

    def _reset_key(self, session_id: str) -> str:
        return f"resultscope:reset-recovery:{session_id}"

    async def _command(self, command: list[Any]) -> Any:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.post(self.url, headers=self._headers, json=command)
            response.raise_for_status()
            body = response.json()
            return body.get("result")

    async def get(self, session_id: str) -> list[dict[str, str]]:
        try:
            raw = await self._command(["GET", self._key(session_id)])
            if not raw:
                return []
            data = json.loads(raw)
            if not isinstance(data, list) or any(
                not isinstance(row, dict)
                or row.get("role") not in {"user", "assistant"}
                or not isinstance(row.get("content"), str)
                for row in data
            ):
                raise ValueError("invalid conversation payload")
            return data
        except Exception:
            logger.warning("Upstash conversation read failed")
            raise ConversationStoreError("Conversation history is temporarily unavailable.") from None

    async def set(self, session_id: str, history: list[dict[str, str]]) -> None:
        payload = json.dumps(history, ensure_ascii=False)
        try:
            await self._command(
                ["SETEX", self._key(session_id), settings.SESSION_TTL_SECONDS, payload]
            )
        except Exception:
            logger.warning("Upstash conversation write failed")
            raise ConversationStoreError("Conversation history could not be saved.") from None

    async def clear(self, session_id: str) -> None:
        try:
            await self._command(["DEL", self._key(session_id)])
        except Exception:
            logger.warning("Upstash conversation reset failed")
            raise ConversationStoreError("Conversation history could not be reset.") from None

    async def save_reset_recovery(self, session_id: str, payload: dict[str, Any]) -> None:
        try:
            await self._command(
                [
                    "SETEX",
                    self._reset_key(session_id),
                    max(1, settings.SESSION_TTL_SECONDS),
                    json.dumps(payload, ensure_ascii=False),
                ]
            )
        except Exception:
            logger.warning("Upstash reset recovery write failed")
            raise ConversationStoreError("Conversation reset recovery is unavailable.") from None

    async def get_reset_recovery(self, session_id: str) -> dict[str, Any] | None:
        try:
            raw = await self._command(["GET", self._reset_key(session_id)])
            if not raw:
                return None
            payload = json.loads(raw)
            if not isinstance(payload, dict) or payload.get("state") != "pending":
                return None
            return payload
        except Exception:
            logger.warning("Upstash reset recovery read failed")
            raise ConversationStoreError("Conversation reset recovery is unavailable.") from None

    async def clear_reset_recovery(self, session_id: str) -> None:
        try:
            await self._command(["DEL", self._reset_key(session_id)])
        except Exception:
            logger.warning("Upstash reset recovery clear failed")
            raise ConversationStoreError("Conversation reset recovery could not be cleared.") from None


def build_store() -> ConversationStore:
    backend = settings.STORAGE_BACKEND.lower().strip()
    has_upstash = bool(settings.UPSTASH_REDIS_REST_URL and settings.UPSTASH_REDIS_REST_TOKEN)
    on_vercel = bool(os.getenv("VERCEL"))

    if backend == "upstash" or (backend == "auto" and has_upstash):
        logger.info("Conversation storage: Upstash Redis")
        return UpstashConversationStore(
            settings.UPSTASH_REDIS_REST_URL,
            settings.UPSTASH_REDIS_REST_TOKEN,
        )

    if backend == "sqlite" or (backend == "auto" and not on_vercel):
        logger.info("Conversation storage: SQLite (%s)", settings.SQLITE_PATH)
        return SQLiteConversationStore(settings.SQLITE_PATH)

    logger.warning(
        "Conversation storage: in-memory. On Vercel this is non-durable; configure Upstash for persistence."
    )
    return MemoryConversationStore()


conversation_store = build_store()
