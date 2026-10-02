import asyncio

import httpx
import pytest

from services import llm_client
from services.llm_client import LLMConnectionError


def _mock_provider(monkeypatch, handler):
    original_client = httpx.AsyncClient

    def factory(*args, **kwargs):
        return original_client(transport=httpx.MockTransport(handler), timeout=kwargs.get("timeout"))

    monkeypatch.setattr(llm_client.httpx, "AsyncClient", factory)
    monkeypatch.setattr(llm_client.settings, "LLM_API_KEY", "synthetic-test-token")


@pytest.mark.parametrize("status", [400, 401, 404, 429, 500])
def test_provider_status_errors_are_sanitized(monkeypatch, status):
    private_detail = "provider-private-detail-must-not-escape"

    def handler(request):
        return httpx.Response(status, json={"error": {"message": private_detail}})

    _mock_provider(monkeypatch, handler)
    with pytest.raises(LLMConnectionError) as error:
        asyncio.run(llm_client.chat([], "synthetic request"))

    assert error.value.status_code == 502
    assert private_detail not in error.value.message
    assert "synthetic-test-token" not in error.value.message


def test_provider_timeout_is_sanitized(monkeypatch):
    def handler(request):
        raise httpx.ReadTimeout("synthetic private timeout detail")

    _mock_provider(monkeypatch, handler)
    with pytest.raises(LLMConnectionError) as error:
        asyncio.run(llm_client.chat([], "synthetic request"))

    assert error.value.message == "ผู้ให้บริการ AI ตอบสนองช้าเกินไป"
    assert "synthetic private timeout detail" not in error.value.message


def test_malformed_provider_payload_is_a_safe_error(monkeypatch):
    def handler(request):
        return httpx.Response(200, json={"choices": []})

    _mock_provider(monkeypatch, handler)
    with pytest.raises(LLMConnectionError) as error:
        asyncio.run(llm_client.chat([], "synthetic request"))

    assert "ไม่ถูกต้อง" in error.value.message


def test_missing_provider_configuration_does_not_open_transport(monkeypatch):
    monkeypatch.setattr(llm_client.settings, "LLM_API_KEY", "")
    monkeypatch.setattr(llm_client.httpx, "AsyncClient", lambda **kwargs: pytest.fail("network must not start"))

    with pytest.raises(LLMConnectionError) as error:
        asyncio.run(llm_client.chat([], "synthetic request"))

    assert error.value.status_code == 503


def test_stream_status_error_does_not_return_provider_body(monkeypatch):
    private_detail = "provider-private-stream-detail"

    def handler(request):
        return httpx.Response(401, json={"error": {"message": private_detail}})

    _mock_provider(monkeypatch, handler)

    async def collect():
        return [event async for event in llm_client.chat_stream([], "synthetic request")]

    events = asyncio.run(collect())

    assert len(events) == 1
    assert events[0]["type"] == "error"
    assert private_detail not in events[0]["message"]
