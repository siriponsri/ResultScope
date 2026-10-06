from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import logging
import os
import time
import uuid
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Request, Response, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel, ConfigDict, Field

from config import settings
from services import conversation_agent as agent, conversation_state as state, evidence_search
from services.conversation_transport import ConversationError, provider_for
from services.lab_fields_v2 import ReportField, normalize
from services.report_reader_v2 import read_report
from services.request_limits import request_rate_limiter
from services.sessions import new_session_id, sign_session_id, verify_session_cookie

router = APIRouter(prefix="/api/v2")
logger = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[1]
DEMO_ROOT = ROOT / "examples" / "thai_lab_reference_v3"
COOKIE = "resultscope_v2"
DEMOS = [
    ("01_A_Liver", "Liver panel", "Enzymes, proteins and bilirubin", "A"),
    ("02_A_Renal", "Kidney & electrolytes", "Renal markers and a printed critical flag", "A"),
    ("03_B_Lipid", "Lipid profile", "Measured and calculated results", "B"),
    ("04_B_Glucose_Urine", "Glucose & urine", "Numeric and qualitative results together", "B"),
    ("05_C_Hematology", "Complete blood count", "Blood-cell indices and morphology", "C"),
    ("06_C_Thyroid", "Thyroid panel", "Hormones and antibody results", "C"),
]


class ChatInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    message: str = Field(min_length=1, max_length=8000)
    state_token: str | None = Field(default=None, max_length=140000)


class ConfirmInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    draft_token: str = Field(min_length=1, max_length=140000)
    state_token: str | None = Field(default=None, max_length=140000)
    fields: list[ReportField] = Field(min_length=1, max_length=60)


def error_response(exc: ConversationError | state.StateError, request_id: str = "") -> JSONResponse:
    return JSONResponse(status_code=getattr(exc, "status", 409), content={
        "code": getattr(exc, "code", "context_expired"), "message": str(exc), "request_id": request_id},
        headers={"Cache-Control": "no-store"})


def session(request: Request) -> str:
    sid = verify_session_cookie(request.cookies.get(COOKIE))
    if not sid:
        raise state.StateError("Your conversation session expired. Start a new chat.")
    return sid


def set_cookie(response: Response, sid: str) -> None:
    response.set_cookie(COOKIE, sign_session_id(sid), httponly=True,
        secure=bool(os.getenv("VERCEL")) or settings.APP_ENV == "production", samesite="strict",
        max_age=settings.CONTEXT_TTL_SECONDS, path="/")
    response.headers["Cache-Control"] = "no-store"


def authorize(request: Request) -> None:
    origin = request.headers.get("origin")
    if origin and origin.rstrip("/") != str(request.base_url).rstrip("/"):
        from urllib.parse import urlparse
        # Proxies may report http for an HTTPS browser origin. Compare the
        # full browser authority to the forwarded Host, never a suffix match.
        parsed = urlparse(origin)
        if parsed.netloc != request.headers.get("host") or parsed.scheme not in {"https", "http"}:
            raise ConversationError("origin_rejected", "Use this application's own page to send requests.", 403)
    if settings.DEMO_ACCESS_CODE:
        supplied = request.headers.get("X-ResultScope-Access", "")
        if not hmac.compare_digest(supplied.encode(), settings.DEMO_ACCESS_CODE.encode()):
            raise ConversationError("access_required", "Enter the demo access code in Settings to connect.", 401)
    elif os.getenv("VERCEL") and settings.PROVIDER_NETWORK_ENABLED:
        raise ConversationError("access_not_configured", "Set a demo access code before enabling the cloud models.")
    if not request_rate_limiter.allow(request):
        raise ConversationError("rate_limited", "Too many requests. Please wait a moment.", 429)


@router.get("/config")
async def configuration(response: Response):
    response.headers["Cache-Control"] = "no-store"
    llm, vision = provider_for("llm"), provider_for("vision")
    missing = []
    if not settings.PROVIDER_NETWORK_ENABLED:
        missing.append("Enable provider network access")
    if not llm.enabled:
        missing.append("Enable the conversation model")
    if not llm.api_key:
        missing.append("Connect the conversation model")
    if not settings.GUARD_SERVICE_URL and not (provider_for("guard").enabled and provider_for("guard").api_key):
        missing.append("Connect the safety model")
    if not settings.PROVIDER_BUDGET_CYCLE_ID:
        missing.append("Configure a provider usage cycle")
    if os.getenv("VERCEL"):
        if len(settings.SESSION_SIGNING_KEY) < 32:
            missing.append("Set a session secret of at least 32 characters")
        if len(settings.DEMO_ACCESS_CODE) < 12:
            missing.append("Set a demo access code of at least 12 characters")
        if not settings.UPSTASH_REDIS_REST_URL or not settings.UPSTASH_REDIS_REST_TOKEN:
            missing.append("Connect the shared usage store")
    return {"version": "2.0.0", "mode": "connected" if not missing else "setup",
        "model": llm.model, "vision_model": vision.model, "vision": settings.VISION_ENABLED and vision.enabled and bool(vision.api_key),
        "guard": "service" if settings.GUARD_SERVICE_URL else "llama-guard",
        "retrieval": "hybrid_vector" if settings.VECTOR_SEARCH_ENABLED else "hybrid" if settings.LIGHTRAG_ENABLED else "lexical",
        "needs_access_code": bool(settings.DEMO_ACCESS_CODE), "missing": missing,
        "cloud": bool(os.getenv("VERCEL")), "references": len(evidence_search.corpus())}


@router.post("/session")
async def start_session(request: Request, response: Response):
    sid = verify_session_cookie(request.cookies.get(COOKIE)) or new_session_id()
    set_cookie(response, sid)
    return {"ok": True}


@router.post("/reset")
async def reset(response: Response):
    set_cookie(response, new_session_id())
    return {"ok": True}


def prepare_turn(payload: ChatInput, request: Request) -> tuple[str, dict]:
    authorize(request)
    sid = session(request)
    if not payload.message.strip():
        raise ConversationError("empty_message", "Type a message first.", 422)
    context = state.unseal(payload.state_token, sid)
    return sid, context


@router.post("/chat")
async def chat(payload: ChatInput, request: Request):
    rid = uuid.uuid4().hex
    try:
        sid, context = prepare_turn(payload, request)
        async def emit(*_):
            pass
        async with asyncio.timeout(220):
            result = await agent.run(payload.message, context, emit)
        result["state_token"] = state.seal(result.pop("state"), sid)
        return JSONResponse({**result, "request_id": rid}, headers={"Cache-Control": "no-store"})
    except (ConversationError, state.StateError) as exc:
        return error_response(exc, rid)
    except TimeoutError:
        return error_response(ConversationError("timeout", "The request took too long. Please try again.", 504), rid)
    except Exception:
        logger.warning("conversation_v2 outcome=failed request_id=%s", rid)
        return error_response(ConversationError("unavailable", "This request could not be completed. Please try again.", 502), rid)


@router.post("/chat/stream")
async def chat_stream(payload: ChatInput, request: Request):
    rid = uuid.uuid4().hex
    try:
        sid, context = prepare_turn(payload, request)
    except (ConversationError, state.StateError) as exc:
        return error_response(exc, rid)

    async def events():
        queue: asyncio.Queue = asyncio.Queue()
        started = time.monotonic()
        async def emit(kind, data):
            await queue.put((kind, data))
        async def work():
            try:
                async with asyncio.timeout(220):
                    result = await agent.run(payload.message, context, emit)
                result["state_token"] = state.seal(result.pop("state"), sid)
                await emit("answer", {**result, "request_id": rid})
                logger.info("conversation_v2 outcome=completed request_id=%s duration_ms=%d", rid, (time.monotonic()-started)*1000)
            except (ConversationError, state.StateError) as exc:
                await emit("error", {"code": getattr(exc, "code", "context_expired"), "message": str(exc), "request_id": rid})
            except TimeoutError:
                await emit("error", {"code": "timeout", "message": "The request took too long. Please try again.", "request_id": rid})
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.warning("conversation_v2 outcome=failed request_id=%s", rid)
                await emit("error", {"code": "unavailable", "message": "This request could not be completed. Please try again.", "request_id": rid})
            finally:
                await queue.put(None)
        task = asyncio.create_task(work())
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    item = await asyncio.wait_for(queue.get(), timeout=10)
                except TimeoutError:
                    yield ": keep-alive\n\n"
                    continue
                if item is None:
                    break
                kind, data = item
                yield f"event: {kind}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
        finally:
            if not task.done():
                task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    return StreamingResponse(events(), media_type="text/event-stream", headers={
        "Cache-Control": "no-store", "X-Accel-Buffering": "no", "X-Request-ID": rid})


@router.get("/demos")
async def demos():
    return {"data_class": "synthetic", "notice": "Six owner-supplied fictional reports. No real patient records.",
        "reports": [{"id": rid, "title": title, "description": desc, "template": template,
                     "image": f"/api/v2/demos/{rid}/png", "pdf": f"/api/v2/demos/{rid}/pdf"}
                    for rid, title, desc, template in DEMOS]}


def demo_path(demo_id: str, format: str) -> Path:
    if demo_id not in {d[0] for d in DEMOS} or format not in {"png", "pdf"}:
        raise ConversationError("demo_not_found", "That demo report is unavailable.", 404)
    return DEMO_ROOT / format / f"{demo_id}.{format}"


@router.get("/demos/{demo_id}/{format}")
async def demo_file(demo_id: str, format: str):
    try:
        path = demo_path(demo_id, format)
    except ConversationError as exc:
        return error_response(exc)
    return FileResponse(path, media_type="image/png" if format == "png" else "application/pdf",
                        headers={"X-Content-Type-Options": "nosniff"})


async def extract_bytes(raw: bytes, sid: str, demo_id: str | None = None):
    digest = hashlib.sha256(raw).hexdigest()
    if not demo_id:
        # Preserve the supplied fixture provenance even when selected through Upload.
        for rid, *_ in DEMOS:
            if any(hashlib.sha256(demo_path(rid, fmt).read_bytes()).hexdigest() == digest for fmt in ("png", "pdf")):
                demo_id = rid
                break
    report = await read_report(raw)
    report["data_class"] = "synthetic" if demo_id else "user_upload"
    report["demo_id"] = demo_id
    report["document_sha256"] = digest
    return {"draft_token": state.seal(report, sid, "report-draft"), "report": report}


@router.post("/demos/{demo_id}/read")
async def read_demo(demo_id: str, request: Request):
    try:
        authorize(request)
        sid = session(request)
        return await extract_bytes(demo_path(demo_id, "png").read_bytes(), sid, demo_id)
    except (ConversationError, state.StateError) as exc:
        return error_response(exc)


@router.post("/reports/read")
async def read_upload(request: Request, file: UploadFile = File(...)):
    try:
        authorize(request)
        sid = session(request)
        raw = await file.read(settings.IMAGE_MAX_BYTES + 1)
        return await extract_bytes(raw, sid)
    except (ConversationError, state.StateError) as exc:
        return error_response(exc)
    finally:
        await file.close()


@router.post("/reports/confirm")
async def confirm_report(payload: ConfirmInput, request: Request):
    try:
        authorize(request)
        sid = session(request)
        context = state.unseal(payload.state_token, sid)
        report = state.unseal(payload.draft_token, sid, "report-draft")
        report.update({"fields": normalize(payload.fields), "confirmed": True, "confirmed_at": int(time.time())})
        # A new report always starts a new context to prevent patient mixing.
        context = {"history": [], "report": report}
        return {"state_token": state.seal(context, sid), "report": report}
    except (ConversationError, state.StateError) as exc:
        return error_response(exc)


@router.get("/references")
async def references():
    return {"records": [{k: r.get(k) for k in ("id", "title", "url", "publisher", "data_class", "reviewed_at", "page")}
                        for r in evidence_search.corpus()]}
