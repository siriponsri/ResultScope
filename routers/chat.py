from __future__ import annotations

import json
import logging
import uuid
import asyncio
import time
from dataclasses import asdict
from typing import Any

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from config import settings
from services import llm_client
from services import answer_service
from services.answer_service import AnswerResult, answer_query
from services.deterministic_engine import analyze_message, get_rulebook
from services.extraction_store import ExtractionRecord, ExtractionStoreError, extraction_store
from services.intent_router import IntentDecision, route_intent
from services.lab_scope import SCOPE_SUGGESTIONS, local_scope_reply
from services.llm_client import LLMConnectionError
from services.output_validation import GENERIC_VALIDATION_REASON, OutputValidationError, validate_answer_result
from services.request_limits import request_rate_limiter
from services.sessions import new_session_id, session_locks, sign_session_id, verify_session_cookie
from services.store import ConversationStoreError, conversation_store
from services import systemone_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1")

SESSION_COOKIE = "resultscope_session"
SESSION_MAX_AGE = settings.SESSION_TTL_SECONDS


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=settings.MAX_MESSAGE_CHARS)
    extraction_id: str | None = Field(default=None, max_length=64)


class ChatResponse(BaseModel):
    reply: str
    scope: str
    status: str
    intent: str
    citations: list[dict[str, Any]] = Field(default_factory=list)
    corpus_mode: str
    corpus_version: str | None = None
    demo: bool
    data_class: str
    demo_notice: str | None = None
    retrieval_reason: str = "not_run"
    retrieval_latency_ms: float = 0.0
    request_id: str


class ScopeRequest(BaseModel):
    message: str = Field(min_length=1, max_length=settings.MAX_MESSAGE_CHARS)


class ExtractionRequestError(Exception):
    def __init__(self, code: str, message: str, status_code: int) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def _session_id(request: Request) -> tuple[str, bool]:
    existing = verify_session_cookie(request.cookies.get(SESSION_COOKIE))
    return (existing, False) if existing else (new_session_id(), True)


def _request_id(request: Request) -> str:
    return uuid.uuid4().hex


def _audit_event(
    request_id: str,
    outcome: str,
    started_at: float,
    *,
    event: str = "chat_request",
    result: AnswerResult | None = None,
) -> None:
    corpus_version = result.corpus_version if result else None
    retrieval_latency_ms = result.retrieval_latency_ms if result else None
    attempt = result.provider_attempt if result else None
    audit_fields = {
        "event": event,
        "request_id": request_id,
        "outcome": outcome,
        "intent": result.intent if result else "unknown",
        "corpus_version": corpus_version or "unknown",
        "retrieval_latency_ms": retrieval_latency_ms,
        "validation_reason": result.validation_reason if result else None,
        "provider_slot": attempt.provider_slot if attempt else None,
        "cycle_id": attempt.cycle_id if attempt else None,
        "reservation_id": attempt.attempt_id if attempt else None,
        "provider_source_path": attempt.source_path if attempt else None,
        "provider_outcome": attempt.outcome if attempt else None,
        "provider_reason_code": attempt.reason_code if attempt else None,
        "duration_ms": round((time.perf_counter() - started_at) * 1000, 3),
    }
    logger.info(
        "ResultScope audit %s",
        json.dumps(audit_fields, ensure_ascii=True, sort_keys=True, separators=(",", ":")),
        extra=audit_fields,
    )


def _audit_result(request_id: str, result: AnswerResult, started_at: float) -> None:
    _audit_event(request_id, result.error_code or result.status, started_at, result=result)


def _result_metadata(result: AnswerResult, request_id: str) -> dict[str, Any]:
    metadata = result.metadata()
    metadata["request_id"] = request_id
    return metadata


async def _recover_pending_reset(session_id: str) -> None:
    payload = await conversation_store.get_reset_recovery(session_id)
    if payload is None:
        return
    history = payload.get("history")
    serialized_extractions = payload.get("extractions")
    if not isinstance(history, list) or not isinstance(serialized_extractions, list):
        raise ConversationStoreError("Conversation reset recovery is invalid.")
    try:
        extractions = [ExtractionRecord(**record) for record in serialized_extractions]
    except (TypeError, ValueError) as exc:
        raise ConversationStoreError("Conversation reset recovery is invalid.") from exc
    await extraction_store.restore(session_id, extractions)
    await conversation_store.set(session_id, history)
    await conversation_store.clear_reset_recovery(session_id)


def _reset_recovery_payload(history: list[dict[str, str]], extractions: list[ExtractionRecord]) -> dict[str, Any]:
    return {
        "state": "pending",
        "history": history,
        "extractions": [asdict(record) for record in extractions],
    }


def _set_session_cookie(response: Response, session_id: str) -> None:
    response.set_cookie(
        key=SESSION_COOKIE,
        value=sign_session_id(session_id),
        httponly=True,
        samesite="lax",
        secure=settings.APP_ENV.lower() == "production",
        max_age=SESSION_MAX_AGE,
    )


def _bounded_history(history: list[dict[str, str]]) -> list[dict[str, str]]:
    valid = [
        {
            "role": row["role"],
            "content": row["content"][: settings.MAX_HISTORY_MESSAGE_CHARS],
        }
        for row in history
        if isinstance(row, dict)
        and row.get("role") in {"user", "assistant"}
        and isinstance(row.get("content"), str)
    ]
    bounded = valid[-settings.MAX_HISTORY_MESSAGES :]
    total = 0
    retained: list[dict[str, str]] = []
    for row in reversed(bounded):
        if total + len(row["content"]) > settings.MAX_HISTORY_CHARS:
            break
        retained.append(row)
        total += len(row["content"])
    return list(reversed(retained))


def _validated_result(
    result: AnswerResult,
    message: str,
    analysis: Any,
    confirmed_extraction: dict[str, Any] | None,
    request_id: str,
    started_at: float,
) -> AnswerResult:
    try:
        validate_answer_result(
            result,
            message,
            result.validation_items,
            analysis,
            confirmed_extraction,
        )
    except OutputValidationError as exc:
        rejected = answer_service.fail_closed_result(
            answer_service.mark_provider_output_rejected(result, exc.code),
            validation_reason=exc.code,
        )
        _audit_event(request_id, "output_rejected", started_at, result=rejected)
        return rejected
    except Exception:
        rejected = answer_service.fail_closed_result(
            answer_service.mark_provider_output_rejected(result, GENERIC_VALIDATION_REASON),
            validation_reason=GENERIC_VALIDATION_REASON,
        )
        _audit_event(request_id, "output_rejected", started_at, result=rejected)
        return rejected
    return result


def _local_result(intent: IntentDecision, message: str) -> AnswerResult:
    return AnswerResult(
        status="refused",
        text=local_scope_reply(intent.scope, message),
        intent=intent.kind,
        corpus_mode=settings.KNOWLEDGE_MODE,
        demo=settings.KNOWLEDGE_MODE == "synthetic",
    )


async def _run_pipeline(
    message: str, history: list[dict[str, str]], confirmed_extraction: dict[str, Any] | None = None
) -> tuple[IntentDecision, Any, AnswerResult]:
    intent = route_intent(message, history, confirmed_extraction)
    analysis = analyze_message(message, history, confirmed_extraction)
    if intent.kind in {"local", "unrelated"}:
        return intent, analysis, _local_result(intent, message)
    if intent.allowed:
        try:
            # SystemOne is an optional observer; Python rules remain authoritative.
            await systemone_client.shadow_decide(message, intent.kind, intent.allowed)
        except systemone_client.SystemOneError as exc:
            logger.info("SystemOne shadow observation unavailable", extra={"reason_code": exc.code})
    answer = await answer_query(message, intent, history, analysis, confirmed_extraction=confirmed_extraction)
    return intent, analysis, answer


async def _load_confirmed_extraction(session_id: str, extraction_id: str | None) -> dict[str, Any] | None:
    if not extraction_id:
        return None
    try:
        import uuid

        uuid.UUID(extraction_id)
    except (ValueError, AttributeError, TypeError):
        raise ExtractionRequestError("extraction_not_found", "The extraction is not available for this session.", 404)
    record = await extraction_store.get(session_id, extraction_id)
    if record is None:
        raise ExtractionRequestError("extraction_not_found", "The extraction is not available for this session.", 404)
    if record.status != "confirmed":
        raise ExtractionRequestError("extraction_confirmation_required", "Review and confirm the image fields before asking about them.", 409)
    return {
        "extraction_id": record.extraction_id,
        "document_type": record.document_type,
        "fields": record.fields,
        "warnings": record.warnings,
    }


def _response_model(intent: IntentDecision, result: AnswerResult, request_id: str) -> ChatResponse:
    meta = result.metadata()
    return ChatResponse(
        reply=result.text,
        scope=intent.reason,
        status=result.status,
        intent=result.intent,
        citations=meta["citations"],
        corpus_mode=result.corpus_mode,
        corpus_version=result.corpus_version,
        demo=result.demo,
        data_class=meta["data_class"],
        demo_notice=meta["demo_notice"],
        retrieval_reason=result.retrieval_reason,
        retrieval_latency_ms=result.retrieval_latency_ms,
        request_id=request_id,
    )


def _store_error_response(response: Response | None = None, request_id: str | None = None) -> JSONResponse:
    content = {"error": True, "code": "session_unavailable", "message": "Conversation history is temporarily unavailable."}
    if request_id:
        content["request_id"] = request_id
    error = JSONResponse(
        status_code=503,
        content=content,
        headers={"X-Request-ID": request_id} if request_id else None,
    )
    if response and response.headers.get("set-cookie"):
        error.headers.append("set-cookie", response.headers["set-cookie"])
    return error


def _error_status(result: AnswerResult) -> int:
    return 503


async def _persist_turn(
    session_id: str,
    history: list[dict[str, str]],
    message: str,
    result: AnswerResult,
) -> None:
    if result.intent in {"unrelated", "local", "unsafe"}:
        return
    updated = history + [{"role": "user", "content": message}]
    if result.status not in {"error"}:
        updated.append({"role": "assistant", "content": result.text})
    await conversation_store.set(session_id, _bounded_history(updated))


def _extraction_error_response(error: ExtractionRequestError, request_id: str | None = None) -> JSONResponse:
    content = {"error": True, "code": error.code, "message": error.message}
    if request_id:
        content["request_id"] = request_id
    return JSONResponse(
        status_code=error.status_code,
        content=content,
        headers={"X-Request-ID": request_id} if request_id else None,
    )


def _rate_limit_response(request_id: str | None = None) -> JSONResponse:
    content = {
        "error": True,
        "code": "rate_limited",
        "message": "Too many requests. Please try again later.",
    }
    if request_id:
        content["request_id"] = request_id
    headers = {"Retry-After": str(max(1, settings.CHAT_RATE_LIMIT_WINDOW_SECONDS))}
    if request_id:
        headers["X-Request-ID"] = request_id
    return JSONResponse(
        status_code=429,
        content=content,
        headers=headers,
    )


@router.get("/product")
async def get_product():
    return {
        "name": settings.APP_NAME,
        "tagline": settings.APP_TAGLINE,
        "owner": settings.OWNER_NAME,
        "lab_only": True,
        "storage": settings.STORAGE_BACKEND,
        "data_class": "synthetic" if settings.KNOWLEDGE_MODE == "synthetic" else "release",
        "demo_notice": "Synthetic business data for demonstration only; no real service is provided." if settings.KNOWLEDGE_MODE == "synthetic" else None,
    }


@router.get("/rules")
async def get_rules():
    """Inspectable source of truth for the deterministic pre-answer layer."""
    return get_rulebook()


@router.post("/scope/check")
async def post_scope_check(scope_request: ScopeRequest, request: Request, response: Response):
    session_id, is_new = _session_id(request)
    request_id = _request_id(request)
    try:
        async with session_locks.lock(session_id):
            await _recover_pending_reset(session_id)
            history = _bounded_history(await conversation_store.get(session_id))
    except ConversationStoreError:
        return _store_error_response(request_id=request_id)
    intent = route_intent(scope_request.message, history)
    if is_new:
        _set_session_cookie(response, session_id)
    return {
        "allowed": intent.allowed,
        "reason": intent.reason,
        "intent": intent.kind,
        "category": intent.scope.category,
        "matched_terms": intent.scope.matched_terms,
    }


@router.get("/models")
async def get_models():
    try:
        models = await llm_client.list_models()
        return {"models": models}
    except LLMConnectionError as exc:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": True, "code": exc.code, "message": exc.message},
        )


@router.post("/chat/reset")
async def post_chat_reset(request: Request, response: Response):
    session_id, is_new = _session_id(request)
    request_id = _request_id(request)
    started_at = time.perf_counter()
    try:
        if not is_new:
            async with session_locks.lock(session_id):
                await _recover_pending_reset(session_id)
                history = _bounded_history(await conversation_store.get(session_id))
                extractions = await extraction_store.snapshot(session_id)
                await conversation_store.save_reset_recovery(
                    session_id,
                    _reset_recovery_payload(history, extractions),
                )
                recovery_payload = _reset_recovery_payload(history, extractions)
                try:
                    await extraction_store.clear(session_id)
                    await conversation_store.clear(session_id)
                    await conversation_store.save_reset_recovery(
                        session_id,
                        {**recovery_payload, "state": "completed"},
                    )
                except (ConversationStoreError, ExtractionStoreError):
                    try:
                        await extraction_store.restore(session_id, extractions)
                        await conversation_store.set(session_id, history)
                    except (ConversationStoreError, ExtractionStoreError):
                        _audit_event(request_id, "rollback_pending", started_at, event="conversation_reset")
                        raise
                    try:
                        await conversation_store.clear_reset_recovery(session_id)
                    except ConversationStoreError:
                        _audit_event(request_id, "recovery_journal_retained", started_at, event="conversation_reset")
                    raise
                try:
                    await conversation_store.clear_reset_recovery(session_id)
                except ConversationStoreError:
                    _audit_event(request_id, "completed_journal_retained", started_at, event="conversation_reset")
                _audit_event(request_id, "reset", started_at, event="conversation_reset")
    except (ConversationStoreError, ExtractionStoreError):
        _audit_event(request_id, "session_unavailable", started_at, event="conversation_reset")
        return _store_error_response(request_id=request_id)
    if is_new:
        _audit_event(request_id, "reset", started_at, event="conversation_reset")
    response.headers["X-Request-ID"] = request_id
    rotated_id = new_session_id()
    _set_session_cookie(response, rotated_id)
    return {"ok": True, "request_id": request_id}


@router.post("/chat", response_model=ChatResponse)
async def post_chat(chat_request: ChatRequest, request: Request, response: Response):
    session_id, is_new = _session_id(request)
    request_id = _request_id(request)
    started_at = time.perf_counter()
    if not request_rate_limiter.allow(request):
        _audit_event(request_id, "rate_limited", started_at)
        return _rate_limit_response(request_id)
    try:
        async with session_locks.lock(session_id):
            await _recover_pending_reset(session_id)
            history = _bounded_history(await conversation_store.get(session_id))
            confirmed_extraction = await _load_confirmed_extraction(session_id, chat_request.extraction_id)
            intent, analysis, result = await _run_pipeline(chat_request.message, history, confirmed_extraction)
            result = _validated_result(result, chat_request.message, analysis, confirmed_extraction, request_id, started_at)
            await _persist_turn(session_id, history, chat_request.message, result)
    except ExtractionRequestError as exc:
        _audit_event(request_id, exc.code, started_at)
        return _extraction_error_response(exc, request_id)
    except (ConversationStoreError, ExtractionStoreError):
        _audit_event(request_id, "session_unavailable", started_at)
        return _store_error_response(response, request_id)
    except asyncio.TimeoutError:
        _audit_event(request_id, "provider_timeout", started_at)
        return JSONResponse(
            status_code=504,
            content={"error": True, "code": "provider_timeout", "message": "The AI provider took too long to respond.", "request_id": request_id},
            headers={"X-Request-ID": request_id},
        )
    _audit_result(request_id, result, started_at)
    if is_new:
        _set_session_cookie(response, session_id)
    if result.status == "error":
        error = JSONResponse(
            status_code=_error_status(result),
            content={"error": True, "code": result.error_code, "message": result.text, "metadata": _result_metadata(result, request_id)},
            headers={"X-Request-ID": request_id},
        )
        if is_new:
            _set_session_cookie(error, session_id)
        return error
    model = _response_model(intent, result, request_id)
    response.headers["X-Request-ID"] = request_id
    return model


@router.post("/chat/stream")
async def post_chat_stream(chat_request: ChatRequest, request: Request):
    session_id, is_new = _session_id(request)
    request_id = _request_id(request)
    started_at = time.perf_counter()

    async def event_generator():
        try:
            if not request_rate_limiter.allow(request):
                _audit_event(request_id, "rate_limited", started_at)
                yield "data: " + json.dumps(
                    {"error": True, "code": "rate_limited", "message": "Too many requests. Please try again later.", "request_id": request_id},
                    ensure_ascii=False,
                ) + "\n\n"
                yield 'data: {"done": true}\n\n'
                return
            async with session_locks.lock(session_id):
                await _recover_pending_reset(session_id)
                history = _bounded_history(await conversation_store.get(session_id))
                confirmed_extraction = await _load_confirmed_extraction(session_id, chat_request.extraction_id)
                intent, analysis, result = await _run_pipeline(chat_request.message, history, confirmed_extraction)
                result = _validated_result(result, chat_request.message, analysis, confirmed_extraction, request_id, started_at)
                await _persist_turn(session_id, history, chat_request.message, result)
                _audit_result(request_id, result, started_at)
                if analysis.scope.allowed:
                    yield "data: " + json.dumps(
                        {"analysis_meta": analysis.to_public_dict()}, ensure_ascii=False
                    ) + "\n\n"
                metadata = _result_metadata(result, request_id)
                yield "data: " + json.dumps({"response_meta": metadata}, ensure_ascii=False) + "\n\n"
                if result.status == "error":
                    yield "data: " + json.dumps(
                        {"error": True, "code": result.error_code, "message": result.text, "request_id": request_id}, ensure_ascii=False
                    ) + "\n\n"
                elif intent.kind in {"unrelated", "local", "unsafe"}:
                    yield "data: " + json.dumps(
                        {
                            "local_response": True,
                            "intent": intent.reason,
                            "message": result.text,
                            "suggestions": SCOPE_SUGGESTIONS if intent.kind == "unrelated" else [],
                        },
                        ensure_ascii=False,
                    ) + "\n\n"
                else:
                    yield "data: " + json.dumps({"delta": result.text}, ensure_ascii=False) + "\n\n"
                yield 'data: {"done": true}\n\n'
        except ExtractionRequestError as exc:
            _audit_event(request_id, exc.code, started_at)
            yield "data: " + json.dumps(
                {"error": True, "code": exc.code, "message": exc.message, "request_id": request_id}, ensure_ascii=False
            ) + "\n\n"
            yield 'data: {"done": true}\n\n'
        except (ConversationStoreError, ExtractionStoreError):
            _audit_event(request_id, "session_unavailable", started_at)
            yield "data: " + json.dumps(
                {"error": True, "code": "session_unavailable", "message": "Conversation history is temporarily unavailable.", "request_id": request_id},
                ensure_ascii=False,
            ) + "\n\n"
            yield 'data: {"done": true}\n\n'
        except asyncio.TimeoutError:
            _audit_event(request_id, "provider_timeout", started_at)
            yield "data: " + json.dumps(
                {"error": True, "code": "provider_timeout", "message": "The AI provider took too long to respond.", "request_id": request_id},
                ensure_ascii=False,
            ) + "\n\n"
            yield 'data: {"done": true}\n\n'
        except asyncio.CancelledError:
            _audit_event(request_id, "cancelled", started_at)
            return
        except Exception:
            _audit_event(request_id, "internal_error", started_at)
            yield "data: " + json.dumps(
                {"error": True, "code": "internal_error", "message": "An unexpected error occurred.", "request_id": request_id},
                ensure_ascii=False,
            ) + "\n\n"
            yield 'data: {"done": true}\n\n'

    response = StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
    response.headers["X-Request-ID"] = request_id
    if is_new:
        _set_session_cookie(response, session_id)
    return response
