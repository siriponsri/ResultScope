import asyncio

import httpx
import pytest

from services import llm_client
from services.llm_client import LLMConnectionError
from services.provider_budget import SQLiteAttemptBudget


def _enable_test_budget(monkeypatch, tmp_path):
    ledger = tmp_path / "provider-budget.sqlite3"
    cycle_id = "test-cycle"
    SQLiteAttemptBudget.create_cycle(ledger, cycle_id, {"llm": 5, "ocr": 5, "systemone": 5})
    monkeypatch.setattr(llm_client.settings, "PROVIDER_NETWORK_ENABLED", True)
    monkeypatch.setattr(llm_client.settings, "PROVIDER_BUDGET_PATH", str(ledger))
    monkeypatch.setattr(llm_client.settings, "PROVIDER_BUDGET_CYCLE_ID", cycle_id)


def _mock_provider(monkeypatch, tmp_path, handler):
    _enable_test_budget(monkeypatch, tmp_path)
    original_client = httpx.AsyncClient

    def factory(*args, **kwargs):
        return original_client(transport=httpx.MockTransport(handler), timeout=kwargs.get("timeout"))

    monkeypatch.setattr(llm_client.httpx, "AsyncClient", factory)
    monkeypatch.setattr(llm_client.settings, "LLM_API_KEY", "synthetic-test-token")


@pytest.mark.parametrize("status", [400, 401, 404, 429, 500])
def test_provider_status_errors_are_sanitized(monkeypatch, tmp_path, status):
    private_detail = "provider-private-detail-must-not-escape"

    def handler(request):
        return httpx.Response(status, json={"error": {"message": private_detail}})

    _mock_provider(monkeypatch, tmp_path, handler)
    with pytest.raises(LLMConnectionError) as error:
        asyncio.run(llm_client.chat([], "synthetic request"))

    assert error.value.status_code == 502
    assert private_detail not in error.value.message
    assert "synthetic-test-token" not in error.value.message


def test_provider_timeout_is_sanitized(monkeypatch, tmp_path):
    def handler(request):
        raise httpx.ReadTimeout("synthetic private timeout detail")

    _mock_provider(monkeypatch, tmp_path, handler)
    with pytest.raises(LLMConnectionError) as error:
        asyncio.run(llm_client.chat([], "synthetic request"))

    assert error.value.message == "The AI provider took too long to respond."
    assert "synthetic private timeout detail" not in error.value.message


def test_malformed_provider_payload_is_a_safe_error(monkeypatch, tmp_path):
    def handler(request):
        return httpx.Response(200, json={"choices": []})

    _mock_provider(monkeypatch, tmp_path, handler)
    with pytest.raises(LLMConnectionError) as error:
        asyncio.run(llm_client.chat([], "synthetic request"))

    assert "invalid" in error.value.message


def test_successful_chat_returns_safe_attempt_receipt_with_text(monkeypatch, tmp_path):
    def handler(request):
        return httpx.Response(200, json={"choices": [{"message": {"content": "synthetic answer"}}]})

    _mock_provider(monkeypatch, tmp_path, handler)
    result = asyncio.run(llm_client.chat([], "synthetic request"))

    assert isinstance(result, str)
    assert result == "synthetic answer"
    assert result.provider_attempt.provider_slot == "llm"
    assert result.provider_attempt.source_path == "chat"
    assert result.provider_attempt.outcome == "succeeded"


def test_missing_provider_configuration_does_not_open_transport(monkeypatch):
    monkeypatch.setattr(llm_client.settings, "LLM_API_KEY", "")
    monkeypatch.setattr(llm_client.httpx, "AsyncClient", lambda **kwargs: pytest.fail("network must not start"))

    with pytest.raises(LLMConnectionError) as error:
        asyncio.run(llm_client.chat([], "synthetic request"))

    assert error.value.status_code == 503


def test_stream_status_error_does_not_return_provider_body(monkeypatch, tmp_path):
    private_detail = "provider-private-stream-detail"

    def handler(request):
        return httpx.Response(401, json={"error": {"message": private_detail}})

    _mock_provider(monkeypatch, tmp_path, handler)

    async def collect():
        return [event async for event in llm_client.chat_stream([], "synthetic request")]

    events = asyncio.run(collect())

    assert len(events) == 1
    assert events[0]["type"] == "error"
    assert private_detail not in events[0]["message"]
    assert events[0]["code"] == "provider_authorization"


def test_non_openai_stream_error_keeps_stable_code(monkeypatch, tmp_path):
    _enable_test_budget(monkeypatch, tmp_path)
    provider = llm_client.RuntimeProvider(
        "synthetic-anthropic", "https://provider.invalid/v1", "model", "synthetic-key", 5, True, "anthropic_messages"
    )
    monkeypatch.setattr(llm_client, "_provider", lambda: provider)

    async def unavailable(*args, **kwargs):
        raise LLMConnectionError("safe provider failure", code="provider_unavailable")

    monkeypatch.setattr(llm_client, "chat", unavailable)

    async def collect():
        return [event async for event in llm_client.chat_stream([], "synthetic request")]

    events = asyncio.run(collect())
    assert events == [{"type": "error", "message": "safe provider failure", "code": "provider_unavailable"}]
