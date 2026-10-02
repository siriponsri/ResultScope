from __future__ import annotations

import json
import logging
import os
import sqlite3
import threading
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import httpx

from config import settings

logger = logging.getLogger(__name__)


class ExtractionStoreError(Exception):
    pass


class ExtractionConflictError(Exception):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


@dataclass(frozen=True)
class ExtractionRecord:
    extraction_id: str
    session_id: str
    revision: int
    status: str
    document_type: str
    fields: list[dict[str, Any]]
    warnings: list[str]
    created_at: float
    expires_at: float
    confirmed_at: float | None = None

    def public(self) -> dict[str, Any]:
        return {
            "extraction_id": self.extraction_id,
            "revision": self.revision,
            "status": self.status,
            "document_type": self.document_type,
            "fields": self.fields,
            "warnings": self.warnings,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "confirmed_at": self.confirmed_at,
        }


class ExtractionStore(ABC):
    @abstractmethod
    async def create(self, session_id: str, document_type: str, fields: list[dict[str, Any]], warnings: list[str]) -> ExtractionRecord:
        raise NotImplementedError

    @abstractmethod
    async def get(self, session_id: str, extraction_id: str) -> ExtractionRecord | None:
        raise NotImplementedError

    @abstractmethod
    async def confirm(self, session_id: str, extraction_id: str, revision: int, fields: list[dict[str, Any]]) -> ExtractionRecord:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, session_id: str, extraction_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def clear(self, session_id: str) -> None:
        raise NotImplementedError


def _record_from_dict(data: dict[str, Any]) -> ExtractionRecord:
    return ExtractionRecord(
        extraction_id=str(data["extraction_id"]),
        session_id=str(data["session_id"]),
        revision=int(data["revision"]),
        status=str(data["status"]),
        document_type=str(data.get("document_type") or "unknown"),
        fields=list(data.get("fields") or []),
        warnings=list(data.get("warnings") or []),
        created_at=float(data["created_at"]),
        expires_at=float(data["expires_at"]),
        confirmed_at=float(data["confirmed_at"]) if data.get("confirmed_at") is not None else None,
    )


class MemoryExtractionStore(ExtractionStore):
    def __init__(self) -> None:
        self._data: dict[str, ExtractionRecord] = {}

    def _get(self, session_id: str, extraction_id: str) -> ExtractionRecord | None:
        record = self._data.get(extraction_id)
        if not record or record.session_id != session_id:
            return None
        if record.expires_at <= time.time():
            self._data.pop(extraction_id, None)
            return None
        return record

    async def create(self, session_id: str, document_type: str, fields: list[dict[str, Any]], warnings: list[str]) -> ExtractionRecord:
        now = time.time()
        record = ExtractionRecord(
            str(uuid.uuid4()), session_id, 1, "review_required", document_type,
            fields, warnings, now, now + settings.EXTRACTION_TTL_SECONDS,
        )
        self._data[record.extraction_id] = record
        return record

    async def get(self, session_id: str, extraction_id: str) -> ExtractionRecord | None:
        return self._get(session_id, extraction_id)

    async def confirm(self, session_id: str, extraction_id: str, revision: int, fields: list[dict[str, Any]]) -> ExtractionRecord:
        record = self._get(session_id, extraction_id)
        if record is None:
            raise ExtractionConflictError("extraction_not_found", "The extraction is not available for this session.")
        if record.status != "review_required":
            raise ExtractionConflictError("extraction_already_confirmed", "This extraction has already been confirmed.")
        if record.revision != revision:
            raise ExtractionConflictError("extraction_revision_conflict", "The extraction changed before confirmation; review it again.")
        confirmed = ExtractionRecord(
            record.extraction_id, record.session_id, record.revision + 1, "confirmed", record.document_type,
            fields, record.warnings, record.created_at, record.expires_at, time.time(),
        )
        self._data[extraction_id] = confirmed
        return confirmed

    async def delete(self, session_id: str, extraction_id: str) -> None:
        record = self._data.get(extraction_id)
        if record and record.session_id == session_id:
            self._data.pop(extraction_id, None)

    async def clear(self, session_id: str) -> None:
        for extraction_id, record in list(self._data.items()):
            if record.session_id == session_id:
                self._data.pop(extraction_id, None)


class SQLiteExtractionStore(ExtractionStore):
    def __init__(self, path: str) -> None:
        self.path = path
        self._lock = threading.Lock()
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with self._lock, sqlite3.connect(self.path) as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS extractions (
                    extraction_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    revision INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    document_type TEXT NOT NULL,
                    fields_json TEXT NOT NULL,
                    warnings_json TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    expires_at REAL NOT NULL,
                    confirmed_at REAL
                )"""
            )
            conn.commit()

    def _read(self, session_id: str, extraction_id: str) -> ExtractionRecord | None:
        with self._lock, sqlite3.connect(self.path) as conn:
            row = conn.execute(
                "SELECT extraction_id, session_id, revision, status, document_type, fields_json, warnings_json, created_at, expires_at, confirmed_at FROM extractions WHERE extraction_id = ? AND session_id = ?",
                (extraction_id, session_id),
            ).fetchone()
            if not row:
                return None
            if row[8] <= time.time():
                conn.execute("DELETE FROM extractions WHERE extraction_id = ?", (extraction_id,))
                conn.commit()
                return None
        return ExtractionRecord(row[0], row[1], row[2], row[3], row[4], json.loads(row[5]), json.loads(row[6]), row[7], row[8], row[9])

    async def create(self, session_id: str, document_type: str, fields: list[dict[str, Any]], warnings: list[str]) -> ExtractionRecord:
        now = time.time()
        record = ExtractionRecord(str(uuid.uuid4()), session_id, 1, "review_required", document_type, fields, warnings, now, now + settings.EXTRACTION_TTL_SECONDS)
        with self._lock, sqlite3.connect(self.path) as conn:
            conn.execute("INSERT INTO extractions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (record.extraction_id, record.session_id, record.revision, record.status, record.document_type, json.dumps(record.fields, ensure_ascii=False), json.dumps(record.warnings, ensure_ascii=False), record.created_at, record.expires_at, record.confirmed_at))
            conn.commit()
        return record

    async def get(self, session_id: str, extraction_id: str) -> ExtractionRecord | None:
        return self._read(session_id, extraction_id)

    async def confirm(self, session_id: str, extraction_id: str, revision: int, fields: list[dict[str, Any]]) -> ExtractionRecord:
        record = self._read(session_id, extraction_id)
        if record is None:
            raise ExtractionConflictError("extraction_not_found", "The extraction is not available for this session.")
        if record.status != "review_required":
            raise ExtractionConflictError("extraction_already_confirmed", "This extraction has already been confirmed.")
        if record.revision != revision:
            raise ExtractionConflictError("extraction_revision_conflict", "The extraction changed before confirmation; review it again.")
        confirmed = ExtractionRecord(record.extraction_id, record.session_id, record.revision + 1, "confirmed", record.document_type, fields, record.warnings, record.created_at, record.expires_at, time.time())
        with self._lock, sqlite3.connect(self.path) as conn:
            conn.execute("UPDATE extractions SET revision = ?, status = ?, fields_json = ?, confirmed_at = ? WHERE extraction_id = ? AND session_id = ? AND revision = ?", (confirmed.revision, confirmed.status, json.dumps(fields, ensure_ascii=False), confirmed.confirmed_at, extraction_id, session_id, revision))
            if conn.total_changes != 1:
                raise ExtractionConflictError("extraction_revision_conflict", "The extraction changed before confirmation; review it again.")
            conn.commit()
        return confirmed

    async def delete(self, session_id: str, extraction_id: str) -> None:
        with self._lock, sqlite3.connect(self.path) as conn:
            conn.execute("DELETE FROM extractions WHERE extraction_id = ? AND session_id = ?", (extraction_id, session_id))
            conn.commit()

    async def clear(self, session_id: str) -> None:
        with self._lock, sqlite3.connect(self.path) as conn:
            conn.execute("DELETE FROM extractions WHERE session_id = ?", (session_id,))
            conn.commit()


class UpstashExtractionStore(ExtractionStore):
    def __init__(self, url: str, token: str) -> None:
        self.url = url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def _key(self, extraction_id: str) -> str:
        return f"resultscope:extraction:{extraction_id}"

    def _session_key(self, session_id: str) -> str:
        return f"resultscope:session-extractions:{session_id}"

    async def _command(self, command: list[Any]) -> Any:
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                response = await client.post(self.url, headers=self.headers, json=command)
                response.raise_for_status()
                body = response.json()
                return body.get("result")
        except Exception as exc:
            logger.warning("Upstash extraction operation failed")
            raise ExtractionStoreError("Image confirmation storage is temporarily unavailable.") from exc

    async def create(self, session_id: str, document_type: str, fields: list[dict[str, Any]], warnings: list[str]) -> ExtractionRecord:
        now = time.time()
        record = ExtractionRecord(str(uuid.uuid4()), session_id, 1, "review_required", document_type, fields, warnings, now, now + settings.EXTRACTION_TTL_SECONDS)
        await self._command(["SETEX", self._key(record.extraction_id), settings.EXTRACTION_TTL_SECONDS, json.dumps(record.__dict__, ensure_ascii=False)])
        await self._command(["SADD", self._session_key(session_id), record.extraction_id])
        return record

    async def get(self, session_id: str, extraction_id: str) -> ExtractionRecord | None:
        raw = await self._command(["GET", self._key(extraction_id)])
        if not raw:
            return None
        try:
            data = json.loads(raw)
            record = _record_from_dict(data)
        except (TypeError, ValueError, KeyError, json.JSONDecodeError) as exc:
            raise ExtractionStoreError("Image confirmation storage returned invalid data.") from exc
        return record if record.session_id == session_id and record.expires_at > time.time() else None

    async def confirm(self, session_id: str, extraction_id: str, revision: int, fields: list[dict[str, Any]]) -> ExtractionRecord:
        record = await self.get(session_id, extraction_id)
        if record is None:
            raise ExtractionConflictError("extraction_not_found", "The extraction is not available for this session.")
        if record.status != "review_required":
            raise ExtractionConflictError("extraction_already_confirmed", "This extraction has already been confirmed.")
        if record.revision != revision:
            raise ExtractionConflictError("extraction_revision_conflict", "The extraction changed before confirmation; review it again.")
        confirmed = ExtractionRecord(record.extraction_id, record.session_id, revision + 1, "confirmed", record.document_type, fields, record.warnings, record.created_at, record.expires_at, time.time())
        await self._command(["SETEX", self._key(extraction_id), max(1, int(record.expires_at - time.time())), json.dumps(confirmed.__dict__, ensure_ascii=False)])
        return confirmed

    async def delete(self, session_id: str, extraction_id: str) -> None:
        record = await self.get(session_id, extraction_id)
        if record:
            await self._command(["DEL", self._key(extraction_id)])
            await self._command(["SREM", self._session_key(session_id), extraction_id])

    async def clear(self, session_id: str) -> None:
        ids = await self._command(["SMEMBERS", self._session_key(session_id)])
        if isinstance(ids, list) and ids:
            await self._command(["DEL", *[self._key(str(extraction_id)) for extraction_id in ids]])
        await self._command(["DEL", self._session_key(session_id)])


class UnavailableExtractionStore(ExtractionStore):
    async def _unavailable(self) -> None:
        raise ExtractionStoreError("Image confirmation storage is unavailable on this deployment; configure Upstash first.")

    async def create(self, session_id: str, document_type: str, fields: list[dict[str, Any]], warnings: list[str]) -> ExtractionRecord:
        await self._unavailable()
        raise AssertionError

    async def get(self, session_id: str, extraction_id: str) -> ExtractionRecord | None:
        await self._unavailable()
        return None

    async def confirm(self, session_id: str, extraction_id: str, revision: int, fields: list[dict[str, Any]]) -> ExtractionRecord:
        await self._unavailable()
        raise AssertionError

    async def delete(self, session_id: str, extraction_id: str) -> None:
        await self._unavailable()

    async def clear(self, session_id: str) -> None:
        await self._unavailable()


def build_extraction_store() -> ExtractionStore:
    backend = settings.STORAGE_BACKEND.lower().strip()
    has_upstash = bool(settings.UPSTASH_REDIS_REST_URL and settings.UPSTASH_REDIS_REST_TOKEN)
    on_vercel = bool(os.getenv("VERCEL"))
    if backend == "upstash" or (backend == "auto" and has_upstash):
        return UpstashExtractionStore(settings.UPSTASH_REDIS_REST_URL, settings.UPSTASH_REDIS_REST_TOKEN)
    if backend == "memory":
        return MemoryExtractionStore()
    if backend == "sqlite" or (backend == "auto" and not on_vercel):
        return SQLiteExtractionStore(settings.SQLITE_PATH)
    if on_vercel:
        return UnavailableExtractionStore()
    return MemoryExtractionStore()


extraction_store = build_extraction_store()
