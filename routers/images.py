from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, File, Request, Response, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from config import settings
from routers.chat import SESSION_COOKIE, _session_id, _set_session_cookie
from services import vision_client
from services.extraction_store import (
    ExtractionConflictError,
    ExtractionStoreError,
    extraction_store,
)
from services.image_extraction import (
    ExtractionValidationError,
    ImageValidationError,
    normalize_fields,
    validate_image_bytes,
)
from services.sessions import session_locks

router = APIRouter(prefix="/api/v1")


class ConfirmField(BaseModel):
    field_id: str = Field(min_length=1, max_length=32)
    marker: str = Field(min_length=1, max_length=120)
    raw_value: str | None = Field(default=None, max_length=160)
    unit: str | None = Field(default=None, max_length=80)
    reference_low: str | None = Field(default=None, max_length=80)
    reference_high: str | None = Field(default=None, max_length=80)
    reference_range_raw: str | None = Field(default=None, max_length=160)


class ConfirmRequest(BaseModel):
    revision: int = Field(ge=1)
    fields: list[ConfirmField] = Field(min_length=1, max_length=settings.MAX_EXTRACTION_FIELDS)


def _error(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"error": True, "code": code, "message": message})


def _extraction_response(record: Any) -> dict[str, Any]:
    return {"ok": True, **record.public()}


def _valid_extraction_id(value: str) -> bool:
    try:
        uuid.UUID(value)
        return True
    except (ValueError, AttributeError, TypeError):
        return False


@router.post("/images/extract")
async def post_image_extract(request: Request, response: Response, file: UploadFile = File(...)):
    session_id, is_new = _session_id(request)
    image_bytes = b""
    validated = None
    try:
        image_bytes = await file.read(settings.IMAGE_MAX_BYTES + 1)
        validated = validate_image_bytes(image_bytes)
    except ImageValidationError as exc:
        image_bytes = b""
        return _error(exc.status_code, exc.code, exc.message)
    finally:
        await file.close()
    try:
        try:
            payload = await vision_client.extract_image(validated.normalized_bytes, validated.media_type)
            fields, warnings = normalize_fields(payload.fields)
            warnings = [*payload.warnings[:20], *warnings]
            async with session_locks.lock(session_id):
                record = await extraction_store.create(session_id, payload.document_type, fields, warnings)
        except vision_client.VisionError as exc:
            return _error(exc.status_code, exc.code, exc.message)
        except (ExtractionValidationError, ExtractionStoreError) as exc:
            code = "invalid_extraction" if isinstance(exc, ExtractionValidationError) else "extraction_store_unavailable"
            return _error(422 if isinstance(exc, ExtractionValidationError) else 503, code, exc.message)
    finally:
        # The normalized bytes exist only for the provider call and are never persisted.
        image_bytes = b""
        validated = None

    if is_new:
        _set_session_cookie(response, session_id)
    return _extraction_response(record)


@router.post("/images/{extraction_id}/confirm")
async def post_image_confirm(extraction_id: str, confirm_request: ConfirmRequest, request: Request, response: Response):
    if not _valid_extraction_id(extraction_id):
        return _error(404, "extraction_not_found", "The extraction is not available for this session.")
    session_id, is_new = _session_id(request)
    try:
        async with session_locks.lock(session_id):
            current = await extraction_store.get(session_id, extraction_id)
            if current is None:
                return _error(404, "extraction_not_found", "The extraction is not available for this session.")
            if current.status != "review_required":
                return _error(409, "extraction_already_confirmed", "This extraction has already been confirmed.")
            if current.revision != confirm_request.revision:
                return _error(409, "extraction_revision_conflict", "The extraction changed before confirmation; review it again.")
            if {field.field_id for field in confirm_request.fields} != {field["field_id"] for field in current.fields}:
                return _error(422, "extraction_fields_mismatch", "Confirm every extracted field without adding or removing fields.")
            fields, correction_warnings = normalize_fields(
                [field.model_dump() for field in confirm_request.fields], provenance="user"
            )
            record = await extraction_store.confirm(session_id, extraction_id, confirm_request.revision, fields)
            if correction_warnings:
                record = record.__class__(
                    record.extraction_id, record.session_id, record.revision, record.status,
                    record.document_type, record.fields, [*record.warnings, *correction_warnings],
                    record.created_at, record.expires_at, record.confirmed_at,
                )
    except ExtractionConflictError as exc:
        status = 404 if exc.code == "extraction_not_found" else 409
        return _error(status, exc.code, exc.message)
    except ExtractionStoreError as exc:
        return _error(503, "extraction_store_unavailable", str(exc))
    except ExtractionValidationError as exc:
        return _error(422, "invalid_extraction", exc.message)
    if is_new:
        _set_session_cookie(response, session_id)
    return _extraction_response(record)


@router.post("/images/{extraction_id}/cancel")
@router.delete("/images/{extraction_id}")
async def cancel_image_extraction(extraction_id: str, request: Request):
    if not _valid_extraction_id(extraction_id):
        return _error(404, "extraction_not_found", "The extraction is not available for this session.")
    session_id, _ = _session_id(request)
    try:
        async with session_locks.lock(session_id):
            await extraction_store.delete(session_id, extraction_id)
    except ExtractionStoreError as exc:
        return _error(503, "extraction_store_unavailable", str(exc))
    return {"ok": True, "extraction_id": extraction_id, "status": "cancelled"}
