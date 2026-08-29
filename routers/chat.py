from __future__ import annotations

import json
import logging
import uuid

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from config import settings
from services import llm_client
from services.lab_parser import build_symbolic_context, extract_lab_values
from services.lab_scope import (
    OUT_OF_SCOPE_MESSAGE_TH,
    SCOPE_SUGGESTIONS,
    classify_lab_scope,
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


@router.post("/scope/check")
async def post_scope_check(scope_request: ScopeRequest, request: Request):
    session_id, _ = _session_id(request)
    history = await conversation_store.get(session_id)
    decision = classify_lab_scope(scope_request.message, history)
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
    decision = classify_lab_scope(chat_request.message, history)

    if is_new:
        _set_session_cookie(response, session_id)

    if not decision.allowed:
        return ChatResponse(reply=OUT_OF_SCOPE_MESSAGE_TH, scope="blocked")

    parsed_values = extract_lab_values(chat_request.message)
    symbolic_context = build_symbolic_context(parsed_values)

    try:
        reply_text = await llm_client.chat(history, chat_request.message, symbolic_context)
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
    decision = classify_lab_scope(chat_request.message, history)

    async def event_generator():
        if not decision.allowed:
            yield "data: " + json.dumps(
                {
                    "guardrail": True,
                    "message": OUT_OF_SCOPE_MESSAGE_TH,
                    "suggestions": SCOPE_SUGGESTIONS,
                },
                ensure_ascii=False,
            ) + "\n\n"
            yield 'data: {"done": true}\n\n'
            return

        parsed_values = extract_lab_values(chat_request.message)
        symbolic_context = build_symbolic_context(parsed_values)
        if parsed_values:
            yield "data: " + json.dumps(
                {
                    "analysis_meta": {
                        "category": decision.category,
                        "count": len(parsed_values),
                        "flagged_count": sum(1 for item in parsed_values if item.flag in {"low", "high"}),
                        "values": [item.to_dict() for item in parsed_values],
                    }
                },
                ensure_ascii=False,
            ) + "\n\n"

        received_done = False
        accumulated_text = ""
        try:
            async for event in llm_client.chat_stream(
                history, chat_request.message, symbolic_context
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
