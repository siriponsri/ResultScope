from __future__ import annotations

import json
import logging
from collections.abc import AsyncGenerator
from typing import Any

import httpx

from config import settings

logger = logging.getLogger(__name__)
REQUEST_TIMEOUT = httpx.Timeout(connect=5.0, write=10.0, read=120.0, pool=5.0)


class LLMConnectionError(Exception):
    def __init__(self, message: str, status_code: int = 502):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def _ensure_configured() -> None:
    if not settings.LLM_API_KEY or settings.LLM_API_KEY == "replace_me":
        raise LLMConnectionError(
            "LLM_API_KEY is not configured. Add it in .env or Vercel Environment Variables before requesting an AI explanation.",
            status_code=503,
        )


def _auth_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {settings.LLM_API_KEY}",
        "Content-Type": "application/json",
    }


def _build_messages(
    history: list[dict[str, str]], message: str, rule_grounding: str = ""
) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = []
    if settings.SYSTEM_PROMPT:
        messages.append({"role": "system", "content": settings.SYSTEM_PROMPT})
    if rule_grounding:
        # Kept as a system message for broad OpenAI-compatible provider support.
        # Semantically this is the output of a required deterministic tool call.
        messages.append({"role": "system", "content": rule_grounding})
    messages.extend(history[-settings.MAX_HISTORY_MESSAGES :])
    messages.append({"role": "user", "content": message})
    return messages


def _friendly_error_from_response(exc: httpx.HTTPStatusError) -> LLMConnectionError:
    status = exc.response.status_code
    try:
        body = exc.response.json()
        detail = body.get("error", {}).get("message", "")
    except (ValueError, AttributeError):
        detail = exc.response.text

    if status == 401:
        message = "The API key is invalid or expired. Check LLM_API_KEY and try again."
    elif status == 400:
        message = f"คำขอไปยังโมเดลไม่ถูกต้อง: {detail}" if detail else "คำขอไปยังโมเดลไม่ถูกต้อง"
    elif status == 404:
        message = f"ไม่พบโมเดลที่ตั้งค่าไว้: {detail}" if detail else "ไม่พบโมเดลที่ตั้งค่าไว้"
    elif status == 429:
        message = "ผู้ให้บริการจำกัดอัตราการเรียกใช้งาน กรุณาลองใหม่ภายหลัง"
    elif status == 503:
        message = "ผู้ให้บริการ AI ยังไม่พร้อมให้บริการในขณะนี้"
    else:
        message = f"ผู้ให้บริการ AI ตอบกลับด้วยข้อผิดพลาด ({status})"
    return LLMConnectionError(message, status_code=502)


async def list_models() -> list[dict[str, Any]]:
    _ensure_configured()
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        try:
            response = await client.get(
                f"{settings.LLM_BASE_URL.rstrip('/')}/models",
                headers=_auth_headers(),
            )
            response.raise_for_status()
        except httpx.ConnectError as exc:
            raise LLMConnectionError("เชื่อมต่อผู้ให้บริการ AI ไม่ได้") from exc
        except httpx.TimeoutException as exc:
            raise LLMConnectionError("ผู้ให้บริการ AI ตอบสนองช้าเกินไป") from exc
        except httpx.HTTPStatusError as exc:
            raise _friendly_error_from_response(exc) from exc
        return response.json().get("data", [])


async def chat(
    history: list[dict[str, str]], message: str, rule_grounding: str = ""
) -> str:
    _ensure_configured()
    payload: dict[str, Any] = {
        "model": settings.LLM_MODEL,
        "messages": _build_messages(history, message, rule_grounding),
    }
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        try:
            response = await client.post(
                f"{settings.LLM_BASE_URL.rstrip('/')}/chat/completions",
                headers=_auth_headers(),
                json=payload,
            )
            response.raise_for_status()
        except httpx.ConnectError as exc:
            raise LLMConnectionError("เชื่อมต่อผู้ให้บริการ AI ไม่ได้") from exc
        except httpx.TimeoutException as exc:
            raise LLMConnectionError("ผู้ให้บริการ AI ตอบสนองช้าเกินไป") from exc
        except httpx.HTTPStatusError as exc:
            raise _friendly_error_from_response(exc) from exc

        data = response.json()
        choices = data.get("choices", [])
        if not choices:
            return ""
        return choices[0].get("message", {}).get("content", "")


async def chat_stream(
    history: list[dict[str, str]],
    message: str,
    rule_grounding: str = "",
) -> AsyncGenerator[dict[str, Any], None]:
    try:
        _ensure_configured()
    except LLMConnectionError as exc:
        yield {"type": "error", "message": exc.message}
        return

    payload: dict[str, Any] = {
        "model": settings.LLM_MODEL,
        "messages": _build_messages(history, message, rule_grounding),
        "stream": True,
    }

    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            async with client.stream(
                "POST",
                f"{settings.LLM_BASE_URL.rstrip('/')}/chat/completions",
                headers=_auth_headers(),
                json=payload,
            ) as response_llm:
                if response_llm.status_code >= 400:
                    body = await response_llm.aread()
                    try:
                        detail = json.loads(body).get("error", {}).get("message", "")
                    except (ValueError, AttributeError):
                        detail = body.decode("utf-8", errors="ignore")
                    yield {
                        "type": "error",
                        "message": detail or f"ผู้ให้บริการ AI ตอบกลับด้วยสถานะ {response_llm.status_code}",
                    }
                    return

                async for line in response_llm.aiter_lines():
                    if not line.startswith("data:"):
                        continue
                    raw = line[len("data:") :].strip()
                    if not raw:
                        continue
                    if raw == "[DONE]":
                        yield {"type": "done"}
                        return
                    try:
                        event = json.loads(raw)
                    except ValueError:
                        continue
                    choices = event.get("choices", [])
                    if not choices:
                        continue
                    content = choices[0].get("delta", {}).get("content")
                    if content:
                        yield {"type": "delta", "content": content}
    except httpx.ConnectError:
        yield {"type": "error", "message": "เชื่อมต่อผู้ให้บริการ AI ไม่ได้"}
    except httpx.TimeoutException:
        yield {"type": "error", "message": "ผู้ให้บริการ AI ตอบสนองช้าเกินไป"}
    except httpx.HTTPError as exc:
        logger.exception("Unexpected HTTP error during stream")
        yield {"type": "error", "message": f"เกิดข้อผิดพลาดในการเชื่อมต่อ: {exc}"}
    except Exception:
        logger.exception("Unexpected stream failure")
        yield {"type": "error", "message": "เกิดข้อผิดพลาดที่ไม่คาดคิดระหว่างประมวลผล"}
