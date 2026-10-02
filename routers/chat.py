from __future__ import annotations

import json
import logging
import uuid
from typing import Any

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from config import settings
from services import llm_client
from services.answer_service import AnswerResult, answer_query
from services.deterministic_engine import analyze_message, get_rulebook
from services.intent_router import IntentDecision, route_intent
from services.lab_scope import SCOPE_SUGGESTIONS, local_scope_reply
from services.llm_client import LLMConnectionError
from services.sessions import new_session_id, session_locks, sign_session_id, verify_session_cookie
from services.store import ConversationStoreError, conversation_store

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1")

SESSION_COOKIE = "resultscope_session"
SESSION_MAX_AGE = settings.SESSION_TTL_SECONDS


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=settings.MAX_MESSAGE_CHARS)


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


def _session_id(request: Request) -> tuple[str, bool]:
    existing = verify_session_cookie(request.cookies.get(SESSION_COOKIE))
    return (existing, False) if existing else (new_session_id(), True)


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
        {"role": row["role"], "content": row["content"]}
        for row in history
        if isinstance(row, dict)
        and row.get("role") in {"user", "assistant"}
        and isinstance(row.get("content"), str)
    ]
    return valid[-settings.MAX_HISTORY_MESSAGES :]


def _local_result(intent: IntentDecision, message: str) -> AnswerResult:
    return AnswerResult(
        status="refused",
        text=local_scope_reply(intent.scope, message),
        intent=intent.kind,
        corpus_mode=settings.KNOWLEDGE_MODE,
        demo=settings.KNOWLEDGE_MODE == "synthetic",
    )


async def _run_pipeline(
    message: str, history: list[dict[str, str]]
) -> tuple[IntentDecision, Any, AnswerResult]:
    intent = route_intent(message, history)
    analysis = analyze_message(message, history)
    if intent.kind in {"local", "unrelated"}:
        return intent, analysis, _local_result(intent, message)
    answer = await answer_query(message, intent, history, analysis)
    return intent, analysis, answer


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
                await conversation_store.clear(session_id)
    except ConversationStoreError:
        return _store_error_response()
    rotated_id = new_session_id()
    _set_session_cookie(response, rotated_id)
    return {"ok": True}


@router.post("/chat", response_model=ChatResponse)
async def post_chat(chat_request: ChatRequest, request: Request, response: Response):
    session_id, is_new = _session_id(request)
    try:
        async with session_locks.lock(session_id):
            history = _bounded_history(await conversation_store.get(session_id))
            intent, _, result = await _run_pipeline(chat_request.message, history)
            await _persist_turn(session_id, history, chat_request.message, result)
    except ConversationStoreError:
        return _store_error_response(response)
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
            async with session_locks.lock(session_id):
                history = _bounded_history(await conversation_store.get(session_id))
                intent, analysis, result = await _run_pipeline(chat_request.message, history)
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
        except ConversationStoreError:
            yield "data: " + json.dumps(
                {"error": True, "code": "session_unavailable", "message": "Conversation history is temporarily unavailable."},
                ensure_ascii=False,
            ) + "\n\n"
            yield 'data: {"done": true}\n\n'
        except Exception:
            logger.exception("Chat pipeline failed")
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
