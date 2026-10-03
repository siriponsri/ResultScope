from __future__ import annotations

import json
import logging
import uuid
import asyncio
import time
from typing import Any

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from config import settings
from services import llm_client
from services import answer_service
from services.answer_service import AnswerResult, answer_query
from services.deterministic_engine import analyze_message, get_rulebook
from services.extraction_store import ExtractionStoreError, extraction_store
from services.intent_router import IntentDecision, route_intent
from services.lab_scope import SCOPE_SUGGESTIONS, local_scope_reply
from services.llm_client import LLMConnectionError
from services.output_validation import OutputValidationError, validate_answer_result
from services.request_limits import request_rate_limiter
from services.sessions import new_session_id, session_locks, sign_session_id, verify_session_cookie
from services.store import ConversationStoreError, conversation_store

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1")

SESSION_COOKIE = "resultscope_session"
SESSION_MAX_AGE = settings.SESSION_TTL_SECONDS
RESET_RECOVERY_TTL_SECONDS = min(SESSION_MAX_AGE, 15 * 60)
MAX_PENDING_RESET_RECOVERIES = 64
_pending_reset_recovery: dict[str, tuple[float, list[dict[str, str]], list[Any]]] = {}


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=settings.MAX_MESSAGE_CHARS)
    extraction_id: str | None = Field(default=None, max_length=64)


class ChatResponse(BaseModel):
    reply: str
    scope: str
    status: str
    intent: str
    citations: list[dict[str, str]] = Field(default_factory=list)
    corpus_mode: str
    corpus_version: str | None = None
    demo: bool
    data_class: str
    demo_notice: str | None = None
    retrieval_reason: str = "not_run"
    retrieval_latency_ms: float = 0.0


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


async def _recover_pending_reset(session_id: str) -> None:
    pending = _pending_reset_recovery.get(session_id)
    if pending is None:
        return
    expires_at, history, extractions = pending
    if expires_at <= time.time():
        _pending_reset_recovery.pop(session_id, None)
        raise ConversationStoreError("Session reset recovery expired; start a new session.")
    await extraction_store.restore(session_id, extractions)
    await conversation_store.set(session_id, history)
    _pending_reset_recovery.pop(session_id, None)


async def _expire_pending_reset(session_id: str, expires_at: float) -> None:
    await asyncio.sleep(max(0.0, expires_at - time.time()))
    pending = _pending_reset_recovery.get(session_id)
    if pending is not None and pending[0] <= time.time():
        _pending_reset_recovery.pop(session_id, None)


def _prune_pending_reset_recovery() -> None:
    now = time.time()
    for session_id, pending in list(_pending_reset_recovery.items()):
        if pending[0] <= now:
            _pending_reset_recovery.pop(session_id, None)
    if len(_pending_reset_recovery) > MAX_PENDING_RESET_RECOVERIES:
        oldest = sorted(_pending_reset_recovery.items(), key=lambda item: item[1][0])
        for session_id, _ in oldest[: len(_pending_reset_recovery) - MAX_PENDING_RESET_RECOVERIES]:
            _pending_reset_recovery.pop(session_id, None)


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
) -> AnswerResult:
    try:
        validate_answer_result(
            result,
            message,
            result.validation_items,
            analysis,
            confirmed_extraction,
        )
    except OutputValidationError:
        logger.warning("Chat output rejected by deterministic validation")
        return answer_service.fail_closed_result(result)
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
    intent = route_intent(message, history)
    analysis = analyze_message(message, history)
    if intent.kind in {"local", "unrelated"}:
        return intent, analysis, _local_result(intent, message)
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


def _response_model(intent: IntentDecision, result: AnswerResult) -> ChatResponse:
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
    )


def _store_error_response(response: Response | None = None) -> JSONResponse:
    error = JSONResponse(
        status_code=503,
        content={"error": True, "code": "session_unavailable", "message": "Conversation history is temporarily unavailable."},
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


def _extraction_error_response(error: ExtractionRequestError) -> JSONResponse:
    return JSONResponse(
        status_code=error.status_code,
        content={"error": True, "code": error.code, "message": error.message},
    )


def _rate_limit_response() -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={
            "error": True,
            "code": "rate_limited",
            "message": "Too many requests. Please try again later.",
        },
        headers={"Retry-After": str(max(1, settings.CHAT_RATE_LIMIT_WINDOW_SECONDS))},
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
        "demo_notice": "ข้อมูลธุรกิจสมมติสำหรับการเรียน ไม่รับบริการจริง" if settings.KNOWLEDGE_MODE == "synthetic" else None,
    }


@router.get("/rules")
async def get_rules():
    """Inspectable source of truth for the deterministic pre-answer layer."""
    return get_rulebook()


@router.post("/scope/check")
async def post_scope_check(scope_request: ScopeRequest, request: Request, response: Response):
    session_id, is_new = _session_id(request)
    try:
        async with session_locks.lock(session_id):
            await _recover_pending_reset(session_id)
            history = _bounded_history(await conversation_store.get(session_id))
    except ConversationStoreError:
        return _store_error_response()
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
        return JSONResponse(status_code=exc.status_code, content={"error": True, "message": exc.message})


@router.post("/chat/reset")
async def post_chat_reset(request: Request, response: Response):
    session_id, is_new = _session_id(request)
    try:
        if not is_new:
            async with session_locks.lock(session_id):
                await _recover_pending_reset(session_id)
                history = _bounded_history(await conversation_store.get(session_id))
                extractions = await extraction_store.snapshot(session_id)
                _prune_pending_reset_recovery()
                expires_at = time.time() + RESET_RECOVERY_TTL_SECONDS
                _pending_reset_recovery[session_id] = (
                    expires_at,
                    history,
                    extractions,
                )
                asyncio.create_task(_expire_pending_reset(session_id, expires_at))
                try:
                    await extraction_store.clear(session_id)
                    await conversation_store.clear(session_id)
                except (ConversationStoreError, ExtractionStoreError):
                    try:
                        await extraction_store.restore(session_id, extractions)
                        await conversation_store.set(session_id, history)
                    except (ConversationStoreError, ExtractionStoreError):
                        logger.warning("Conversation reset rollback failed")
                        raise
                    _pending_reset_recovery.pop(session_id, None)
                    raise
                _pending_reset_recovery.pop(session_id, None)
    except (ConversationStoreError, ExtractionStoreError):
        return _store_error_response()
    rotated_id = new_session_id()
    _set_session_cookie(response, rotated_id)
    return {"ok": True}


@router.post("/chat", response_model=ChatResponse)
async def post_chat(chat_request: ChatRequest, request: Request, response: Response):
    session_id, is_new = _session_id(request)
    if not request_rate_limiter.allow(request):
        return _rate_limit_response()
    try:
        async with session_locks.lock(session_id):
            await _recover_pending_reset(session_id)
            history = _bounded_history(await conversation_store.get(session_id))
            confirmed_extraction = await _load_confirmed_extraction(session_id, chat_request.extraction_id)
            intent, analysis, result = await _run_pipeline(chat_request.message, history, confirmed_extraction)
            result = _validated_result(result, chat_request.message, analysis, confirmed_extraction)
            await _persist_turn(session_id, history, chat_request.message, result)
    except ExtractionRequestError as exc:
        return _extraction_error_response(exc)
    except (ConversationStoreError, ExtractionStoreError):
        return _store_error_response(response)
    except asyncio.TimeoutError:
        return JSONResponse(
            status_code=504,
            content={"error": True, "code": "provider_timeout", "message": "The AI provider took too long to respond."},
        )
    if is_new:
        _set_session_cookie(response, session_id)
    if result.status == "error":
        error = JSONResponse(
            status_code=_error_status(result),
            content={"error": True, "code": result.error_code, "message": result.text, "metadata": result.metadata()},
        )
        if is_new:
            _set_session_cookie(error, session_id)
        return error
    return _response_model(intent, result)


@router.post("/chat/stream")
async def post_chat_stream(chat_request: ChatRequest, request: Request):
    session_id, is_new = _session_id(request)

    async def event_generator():
        try:
            if not request_rate_limiter.allow(request):
                yield "data: " + json.dumps(
                    {"error": True, "code": "rate_limited", "message": "Too many requests. Please try again later."},
                    ensure_ascii=False,
                ) + "\n\n"
                yield 'data: {"done": true}\n\n'
                return
            async with session_locks.lock(session_id):
                await _recover_pending_reset(session_id)
                history = _bounded_history(await conversation_store.get(session_id))
                confirmed_extraction = await _load_confirmed_extraction(session_id, chat_request.extraction_id)
                intent, analysis, result = await _run_pipeline(chat_request.message, history, confirmed_extraction)
                result = _validated_result(result, chat_request.message, analysis, confirmed_extraction)
                await _persist_turn(session_id, history, chat_request.message, result)
                if analysis.scope.allowed:
                    yield "data: " + json.dumps(
                        {"analysis_meta": analysis.to_public_dict()}, ensure_ascii=False
                    ) + "\n\n"
                metadata = result.metadata()
                yield "data: " + json.dumps({"response_meta": metadata}, ensure_ascii=False) + "\n\n"
                if result.status == "error":
                    yield "data: " + json.dumps(
                        {"error": True, "code": result.error_code, "message": result.text}, ensure_ascii=False
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
            yield "data: " + json.dumps(
                {"error": True, "code": exc.code, "message": exc.message}, ensure_ascii=False
            ) + "\n\n"
            yield 'data: {"done": true}\n\n'
        except (ConversationStoreError, ExtractionStoreError):
            yield "data: " + json.dumps(
                {"error": True, "code": "session_unavailable", "message": "Conversation history is temporarily unavailable."},
                ensure_ascii=False,
            ) + "\n\n"
            yield 'data: {"done": true}\n\n'
        except asyncio.TimeoutError:
            yield "data: " + json.dumps(
                {"error": True, "code": "provider_timeout", "message": "The AI provider took too long to respond."},
                ensure_ascii=False,
            ) + "\n\n"
            yield 'data: {"done": true}\n\n'
        except asyncio.CancelledError:
            logger.info("Chat stream cancelled")
            return
        except Exception:
            logger.warning("Chat pipeline failed")
            yield "data: " + json.dumps(
                {"error": True, "code": "internal_error", "message": "เกิดข้อผิดพลาดที่ไม่คาดคิด"},
                ensure_ascii=False,
            ) + "\n\n"
            yield 'data: {"done": true}\n\n'

    response = StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
    if is_new:
        _set_session_cookie(response, session_id)
    return response
