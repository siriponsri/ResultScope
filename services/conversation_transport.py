"""Bounded provider calls for v2; no retry, fallback, request-body logging or secrets in errors."""
from __future__ import annotations

import asyncio
import os
import re
from typing import Any
from urllib.parse import urlparse

import httpx
from config import settings
from services.provider_budget import reserve_provider_attempt, finish_provider_attempt, ProviderBudgetError
from services.provider_config import runtime_provider, RuntimeProvider


class ConversationError(Exception):
    def __init__(self, code: str, message: str, status: int = 503):
        self.code, self.message, self.status = code, message, status
        super().__init__(message)


def provider_for(slot: str) -> RuntimeProvider:
    if slot == "guard":
        return runtime_provider("guard", fallback_base_url=settings.GUARD_BASE_URL,
            fallback_model=settings.GUARD_MODEL, fallback_key=settings.GUARD_API_KEY,
            fallback_timeout=settings.GUARD_TIMEOUT_SECONDS)
    vision = slot == "vision"
    return runtime_provider("ocr" if vision else "llm",
        fallback_base_url=settings.VISION_BASE_URL if vision else settings.LLM_BASE_URL,
        fallback_model=settings.VISION_MODEL if vision else settings.LLM_MODEL,
        fallback_key=settings.VISION_API_KEY if vision else settings.LLM_API_KEY,
        fallback_timeout=settings.VISION_TIMEOUT_SECONDS if vision else settings.LLM_TIMEOUT_SECONDS)


def validate_server_url(url: str) -> str:
    """Only server configuration supplies endpoints; never accept a model/user URL."""
    parsed = urlparse(url)
    local = parsed.hostname in {"localhost", "127.0.0.1", "::1"}
    if parsed.username or parsed.password or parsed.query or parsed.fragment or not parsed.hostname:
        raise ConversationError("endpoint_invalid", "A provider endpoint is invalid.")
    if parsed.scheme != "https" and not (local and parsed.scheme == "http" and not os.getenv("VERCEL")):
        raise ConversationError("endpoint_invalid", "Provider endpoints must use HTTPS.")
    return url.rstrip("/")


async def redis_command(command: list[Any]) -> Any:
    url = validate_server_url(settings.UPSTASH_REDIS_REST_URL)
    try:
        async with httpx.AsyncClient(timeout=8, follow_redirects=False) as client:
            response = await client.post(url, headers={"Authorization": f"Bearer {settings.UPSTASH_REDIS_REST_TOKEN}"}, json=command)
            response.raise_for_status()
            body = response.json()
            if not isinstance(body, dict) or body.get("error") or "result" not in body:
                raise ValueError
            return body["result"]
    except (httpx.HTTPError, ValueError):
        raise ConversationError("budget_unavailable", "The shared usage limit is unavailable. Please try later.") from None


# Persist cycle limit and consumed calls atomically. No expiry: cold starts,
# failed calls and redeploys cannot replenish an exhausted cycle.
_RESERVE = """
local cap = redis.call('HGET', KEYS[1], 'limit')
if not cap then redis.call('HSET', KEYS[1], 'limit', ARGV[1]); cap = ARGV[1] end
if tonumber(cap) ~= tonumber(ARGV[1]) then return -2 end
local used = tonumber(redis.call('HGET', KEYS[1], 'used') or '0')
if used >= tonumber(cap) then return -1 end
redis.call('HINCRBY', KEYS[1], 'used', 1)
redis.call('HINCRBY', KEYS[1], ARGV[2], 1)
return used + 1
"""


async def reserve(slot: str):
    if not settings.PROVIDER_NETWORK_ENABLED:
        raise ConversationError("offline", "AI is not connected. Open Settings to connect the language and safety models.")
    if os.getenv("VERCEL"):
        if len(settings.SESSION_SIGNING_KEY) < 32 or len(settings.DEMO_ACCESS_CODE) < 12:
            raise ConversationError("cloud_setup_required", "Complete the server secrets and demo access code in Vercel Settings.")
        if not settings.UPSTASH_REDIS_REST_URL or not settings.UPSTASH_REDIS_REST_TOKEN:
            raise ConversationError("cloud_budget_required", "Connect Upstash Redis to enable the shared usage limit.")
        cycle = settings.PROVIDER_BUDGET_CYCLE_ID
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,79}", cycle) or not 1 <= settings.CLOUD_CALL_LIMIT <= 100000:
            raise ConversationError("cycle_required", "Configure a named provider cycle and a positive call limit.")
        result = await redis_command(["EVAL", _RESERVE, 1, f"resultscope:v2:budget:{cycle}", settings.CLOUD_CALL_LIMIT, slot])
        if not isinstance(result, int) or result <= 0:
            raise ConversationError("budget_exhausted", "The configured call limit is exhausted or has changed. Contact the administrator.", 429)
        return None
    try:
        # Guard/retrieval calls consume the LLM allowance; vision consumes OCR.
        return reserve_provider_attempt("ocr" if slot == "vision" else "llm", "ocr" if slot == "vision" else "chat")
    except ProviderBudgetError as exc:
        raise ConversationError(exc.code, exc.message, 429 if "exhausted" in exc.code else 503) from None


def finish(reservation, outcome: str, reason: str | None = None):
    if reservation:
        try:
            finish_provider_attempt(reservation, outcome, reason)
        except ProviderBudgetError:
            pass  # Reservation remains consumed; never refund an uncertain call.


async def post_json(url: str, headers: dict[str, str], body: dict, slot: str, timeout: float) -> dict:
    endpoint = validate_server_url(url)
    reservation = await reserve(slot)
    try:
        async with httpx.AsyncClient(timeout=min(timeout, 75), follow_redirects=False) as client:
            async with client.stream("POST", endpoint, headers=headers, json=body) as response:
                if response.status_code >= 300:
                    raise ConversationError("provider_rejected", "A configured service rejected the request. Check its key, model and usage limit.", 502)
                data = bytearray()
                async for chunk in response.aiter_bytes():
                    data.extend(chunk)
                    if len(data) > 1_000_000:
                        raise ConversationError("provider_response_invalid", "A service returned an oversized response.", 502)
                import json
                result = json.loads(data)
                if not isinstance(result, dict):
                    raise ValueError
        finish(reservation, "succeeded")
        return result
    except asyncio.CancelledError:
        finish(reservation, "failed", "cancelled")
        raise
    except (httpx.HTTPError, ValueError, ConversationError) as exc:
        finish(reservation, "failed", "request_failed")
        if isinstance(exc, ConversationError):
            raise
        raise ConversationError("service_unavailable", "A connected service could not complete this request. Please try again.", 502) from None


async def complete(messages: list[dict], *, slot: str = "llm", json_mode: bool = False, max_tokens: int = 2400) -> str:
    provider = provider_for(slot)
    if not provider.enabled or not provider.api_key or not provider.model:
        raise ConversationError("provider_not_configured", f"The {slot} model is not configured. Open Settings for setup.")
    headers = {"Authorization": f"Bearer {provider.api_key}", "Content-Type": "application/json"}
    payload: dict[str, Any] = {"model": provider.model, "messages": messages, "stream": False, "max_tokens": max_tokens}
    endpoint = provider.base_url.rstrip("/") + "/chat/completions"
    if slot == "guard":
        payload["temperature"] = 0
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
    if provider.protocol == "anthropic_messages":
        payload = {"model": provider.model, "max_tokens": max_tokens,
            "system": "\n".join(m["content"] for m in messages if m["role"] == "system"),
            "messages": [m for m in messages if m["role"] != "system"]}
        headers = {"x-api-key": provider.api_key, "anthropic-version": "2023-06-01"}
        endpoint = provider.base_url.rstrip("/") + "/messages"
    data = await post_json(endpoint, headers, payload, slot, provider.timeout_seconds)
    try:
        if provider.protocol == "anthropic_messages":
            if data.get("stop_reason") in {"max_tokens", "refusal"}:
                raise ValueError
            raw = "".join(x["text"] for x in data["content"] if x.get("type") == "text")
        else:
            choice = data["choices"][0]
            if choice.get("finish_reason") in {"length", "content_filter"}:
                raise ValueError
            raw = choice["message"]["content"]
        if not isinstance(raw, str) or not raw.strip() or len(raw) > 50_000:
            raise ValueError
        return raw.strip()
    except (KeyError, IndexError, TypeError, ValueError):
        raise ConversationError("provider_response_invalid", "The model returned an incomplete response. Please try again.", 502) from None
