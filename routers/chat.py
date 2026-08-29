from __future__ import annotations

import json
import logging
import uuid

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from config import settings
from services import llm_client
from services.deterministic_engine import (
    analyze_message,
    build_rule_grounding,
    get_rulebook,
)
from services.lab_scope import (
    SCOPE_SUGGESTIONS,
    classify_lab_scope,
    local_scope_reply,
)
from services.llm_client import LLMConnectionError
from services.store import conversation_store

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1")

SESSION_COOKIE = "resultscope_session"
SESSION_MAX_AGE = settings.SESSION_TTL_SECONDS


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=settings.MAX_MESSAGE_CHARS)


class ChatResponse(BaseModel):
    reply: str
    scope: str = "lab"


class ScopeRequest(BaseModel):
    message: str = Field(min_length=1, max_length=settings.MAX_MESSAGE_CHARS)


def _session_id(request: Request) -> tuple[str, bool]:
    existing = request.cookies.get(SESSION_COOKIE)
    if existing:
        return existing, False
    return str(uuid.uuid4()), True


def _set_session_cookie(response: Response, session_id: str) -> None:
    response.set_cookie(
        key=SESSION_COOKIE,
        value=session_id,
        httponly=True,
        samesite="lax",
        secure=settings.APP_ENV.lower() == "production",
        max_age=SESSION_MAX_AGE,
    )


def _bounded_history(history: list[dict[str, str]]) -> list[dict[str, str]]:
    return history[-settings.MAX_HISTORY_MESSAGES :]


@router.get("/product")
async def get_product():
    return {
        "name": settings.APP_NAME,
        "tagline": settings.APP_TAGLINE,
        "owner": settings.OWNER_NAME,
        "lab_only": True,
        "storage": settings.STORAGE_BACKEND,
    }


@router.get("/rules")
async def get_rules():
    """Inspectable source of truth for the deterministic pre-answer layer."""
    return get_rulebook()


@router.post("/scope/check")
async def post_scope_check(scope_request: ScopeRequest, request: Request):
    session_id, _ = _session_id(request)
    history = await conversation_store.get(session_id)
    decision = analyze_message(scope_request.message, history).scope
    return {
        "allowed": decision.allowed,
        "reason": decision.reason,
        "category": decision.category,
        "matched_terms": decision.matched_terms,
    }


@router.get("/models")
async def get_models():
    try:
        models = await llm_client.list_models()
        return {"models": models}
    except LLMConnectionError as exc:
        return JSONResponse(status_code=200, content={"error": True, "message": exc.message})


@router.post("/chat/reset")
async def post_chat_reset(request: Request, response: Response):
    session_id, is_new = _session_id(request)
    await conversation_store.clear(session_id)
    if is_new:
        _set_session_cookie(response, session_id)
    return {"ok": True}


@router.post("/chat", response_model=ChatResponse)
async def post_chat(chat_request: ChatRequest, request: Request, response: Response):
    session_id, is_new = _session_id(request)
    history = await conversation_store.get(session_id)
    analysis = analyze_message(chat_request.message, history)
    decision = analysis.scope

    if is_new:
        _set_session_cookie(response, session_id)

    if not decision.allowed:
        return ChatResponse(reply=local_scope_reply(decision, chat_request.message), scope=decision.reason)

    rule_grounding = build_rule_grounding(analysis)

    try:
        reply_text = await llm_client.chat(history, chat_request.message, rule_grounding)
    except LLMConnectionError as exc:
        return JSONResponse(status_code=502, content={"error": True, "message": exc.message})

    updated = _bounded_history(
        history
        + [
            {"role": "user", "content": chat_request.message},
            {"role": "assistant", "content": reply_text},
        ]
    )
    await conversation_store.set(session_id, updated)
    return ChatResponse(reply=reply_text)


@router.post("/chat/stream")
async def post_chat_stream(chat_request: ChatRequest, request: Request):
    session_id, is_new = _session_id(request)
    history = await conversation_store.get(session_id)
    analysis = analyze_message(chat_request.message, history)
    decision = analysis.scope

    async def event_generator():
        if not decision.allowed:
            yield "data: " + json.dumps(
                {
                    "local_response": True,
                    "intent": decision.reason,
                    "message": local_scope_reply(decision, chat_request.message),
                    "suggestions": SCOPE_SUGGESTIONS if decision.reason == "outside_lab_scope" else [],
                },
                ensure_ascii=False,
            ) + "\n\n"
            yield 'data: {"done": true}\n\n'
            return

        rule_grounding = build_rule_grounding(analysis)
        yield "data: " + json.dumps(
            {"analysis_meta": analysis.to_public_dict()}, ensure_ascii=False
        ) + "\n\n"

        received_done = False
        accumulated_text = ""
        try:
            async for event in llm_client.chat_stream(
                history, chat_request.message, rule_grounding
            ):
                if event["type"] == "delta":
                    accumulated_text += event["content"]
                    payload = {"delta": event["content"]}
                elif event["type"] == "error":
                    payload = {"error": True, "message": event["message"]}
                elif event["type"] == "done":
                    received_done = True
                    payload = {"done": True}
                else:
                    continue
                yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
        except Exception:
            logger.exception("stream failed session=%s", session_id)
            yield "data: " + json.dumps(
                {"error": True, "message": "เกิดข้อผิดพลาดที่ไม่คาดคิด"},
                ensure_ascii=False,
            ) + "\n\n"
        finally:
            if accumulated_text and received_done:
                updated = _bounded_history(
                    history
                    + [
                        {"role": "user", "content": chat_request.message},
                        {"role": "assistant", "content": accumulated_text},
                    ]
                )
                await conversation_store.set(session_id, updated)
            elif not received_done:
                # Keep an accepted lab result as session context even when the
                # provider is unavailable. A follow-up can then remain inside
                # the same lab-only workflow instead of being rejected as an
                # unrelated question.
                updated = _bounded_history(
                    history + [{"role": "user", "content": chat_request.message}]
                )
                await conversation_store.set(session_id, updated)
            if not received_done:
                yield 'data: {"done": true}\n\n'

    resp = StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
    if is_new:
        _set_session_cookie(resp, session_id)
    return resp
