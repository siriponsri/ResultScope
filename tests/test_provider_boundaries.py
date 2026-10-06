from __future__ import annotations

import asyncio
import json

import httpx
import pytest
from fastapi.testclient import TestClient

from main import app
from routers import chat as chat_router
from services import answer_service, llm_client, provider_adapters, systemone_client
from services.extraction_store import MemoryExtractionStore
from services.intent_router import route_intent
from services.knowledge import load_knowledge_base
from services.provider_budget import ProviderBudgetError, SQLiteAttemptBudget
from services.provider_config import RuntimeProvider
from services.store import MemoryConversationStore


def _budget(monkeypatch, tmp_path, *, llm=5, ocr=5, systemone=5):
    ledger = tmp_path / "provider-boundaries.sqlite3"
    cycle_id = "boundary-cycle"
    SQLiteAttemptBudget.create_cycle(
        ledger,
        cycle_id,
        {"llm": llm, "ocr": ocr, "systemone": systemone},
    )
    monkeypatch.setattr("config.settings.PROVIDER_NETWORK_ENABLED", True)
    monkeypatch.setattr("config.settings.PROVIDER_BUDGET_PATH", str(ledger))
    monkeypatch.setattr("config.settings.PROVIDER_BUDGET_CYCLE_ID", cycle_id)


def test_adapter_reserves_before_transport_and_blocks_sixth_attempt(monkeypatch, tmp_path):
    _budget(monkeypatch, tmp_path, llm=1)
    calls = []
    provider = RuntimeProvider("synthetic", "https://provider.invalid/v1", "model", "synthetic-key", 5, True, "openai_chat")

    def handler(request):
        calls.append(request.url.path)
        return httpx.Response(200, json={"choices": [{"message": {"content": "ok"}}]})

    original_client = httpx.AsyncClient

    def factory(*args, **kwargs):
        return original_client(transport=httpx.MockTransport(handler), timeout=kwargs.get("timeout"))

    monkeypatch.setattr(provider_adapters.httpx, "AsyncClient", factory)
    assert asyncio.run(provider_adapters.test_provider(provider, live=True))["network_called"] is True
    with pytest.raises(provider_adapters.ProviderAdapterError) as error:
        asyncio.run(provider_adapters.test_provider(provider, live=True))

    assert error.value.code == "provider_budget_exhausted"
    assert calls == ["/v1/chat/completions"]


def test_models_and_stream_use_one_mock_transport_per_attempt(monkeypatch, tmp_path):
    _budget(monkeypatch, tmp_path, llm=2)
    provider = RuntimeProvider("synthetic", "https://provider.invalid/v1", "model", "synthetic-key", 5, True, "openai_chat")
    monkeypatch.setattr(llm_client, "_provider", lambda: provider)
    calls = []

    def handler(request):
        calls.append(request.url.path)
        if request.url.path.endswith("/models"):
            return httpx.Response(
                200,
                json={"data": [{"id": "synthetic-model", "owned_by": "provider-secret-detail"}]},
            )
        return httpx.Response(
            200,
            content=(
                b'data: {"choices":[{"delta":{"content":"synthetic"}}]}\n\n'
                b'data: [DONE]\n\n'
            ),
            headers={"content-type": "text/event-stream"},
        )

    original_client = httpx.AsyncClient

    def factory(*args, **kwargs):
        return original_client(transport=httpx.MockTransport(handler), timeout=kwargs.get("timeout"))

    monkeypatch.setattr(llm_client.httpx, "AsyncClient", factory)
    assert asyncio.run(llm_client.list_models()) == [{"id": "synthetic-model"}]

    async def collect():
        return [event async for event in llm_client.chat_stream([], "synthetic request")]

    events = asyncio.run(collect())
    assert {event["type"] for event in events} == {"delta", "done"}
    assert calls == ["/v1/models", "/v1/chat/completions"]


def test_chat_stream_route_uses_shared_llm_budget_once(monkeypatch, tmp_path):
    _budget(monkeypatch, tmp_path, llm=1)
    provider = RuntimeProvider("synthetic", "https://provider.invalid/v1", "model", "synthetic-key", 5, True, "openai_chat")
    monkeypatch.setattr(llm_client, "_provider", lambda: provider)
    monkeypatch.setattr(chat_router, "conversation_store", MemoryConversationStore())
    monkeypatch.setattr(chat_router, "extraction_store", MemoryExtractionStore())
    monkeypatch.setattr("config.settings.KNOWLEDGE_MODE", "synthetic")
    monkeypatch.setattr("config.settings.SYSTEMONE_SHADOW_ENABLED", False)

    calls = []

    def handler(request):
        calls.append(request.url.path)
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": "Grounded synthetic answer"}}]},
        )

    original_client = httpx.AsyncClient

    def factory(*args, **kwargs):
        return original_client(transport=httpx.MockTransport(handler), timeout=kwargs.get("timeout"))

    monkeypatch.setattr(llm_client.httpx, "AsyncClient", factory)
    response = TestClient(app).post(
        "/api/v1/chat/stream",
        json={"message": "Tell me about synthetic basic panel"},
    )

    assert response.status_code == 200
    events = [
        json.loads(line.removeprefix("data: "))
        for line in response.text.splitlines()
        if line.startswith("data: ")
    ]
    assert any("delta" in event for event in events)
    assert events[-1]["done"] is True
    assert calls == ["/v1/chat/completions"]
    assert SQLiteAttemptBudget(tmp_path / "provider-boundaries.sqlite3", "boundary-cycle", True).snapshot()["llm_used"] == 1


def test_chat_timeout_preserves_attempt_receipt(monkeypatch, tmp_path):
    _budget(monkeypatch, tmp_path, llm=1)
    provider = RuntimeProvider("synthetic", "https://provider.invalid/v1", "model", "synthetic-key", 5, True, "openai_chat")
    monkeypatch.setattr(llm_client, "_provider", lambda: provider)
    monkeypatch.setattr(answer_service.settings, "LLM_TIMEOUT_SECONDS", 0.01)

    async def handler(request):
        await asyncio.sleep(0.1)
        return httpx.Response(200, json={"choices": [{"message": {"content": "late"}}]})

    original_client = httpx.AsyncClient

    def factory(*args, **kwargs):
        return original_client(transport=httpx.MockTransport(handler), timeout=kwargs.get("timeout"))

    monkeypatch.setattr(llm_client.httpx, "AsyncClient", factory)
    query = "Tell me about synthetic basic panel"
    result = asyncio.run(
        answer_service.answer_query(
            query,
            route_intent(query),
            [],
            None,
            base=load_knowledge_base(mode="synthetic", environment="test"),
        )
    )

    assert result.status == "error"
    assert result.error_code == "provider_timeout"
    assert result.provider_attempt is not None
    assert result.provider_attempt.outcome == "failed"
    assert result.provider_attempt.reason_code == "provider_timeout"
    assert SQLiteAttemptBudget(tmp_path / "provider-boundaries.sqlite3", "boundary-cycle", True).snapshot()["llm_used"] == 1


def test_failed_adapter_transport_reports_consumed_attempt_without_provider_detail(monkeypatch, tmp_path):
    _budget(monkeypatch, tmp_path, llm=1)
    provider = RuntimeProvider("synthetic", "https://provider.invalid/v1", "model", "synthetic-key", 5, True, "openai_chat")

    def handler(request):
        return httpx.Response(503, json={"error": {"message": "private provider detail"}})

    original_client = httpx.AsyncClient

    def factory(*args, **kwargs):
        return original_client(transport=httpx.MockTransport(handler), timeout=kwargs.get("timeout"))

    monkeypatch.setattr(provider_adapters.httpx, "AsyncClient", factory)
    with pytest.raises(provider_adapters.ProviderAdapterError) as error:
        asyncio.run(provider_adapters.test_provider(provider, live=True))

    assert error.value.provider_attempt is not None
    assert error.value.provider_attempt.outcome == "failed"
    assert error.value.provider_attempt.source_path == "admin_test"
    assert "private provider detail" not in error.value.message


def test_systemone_shadow_uses_shared_reservation_and_sanitized_parser(monkeypatch, tmp_path):
    monkeypatch.setattr("config.settings.SYSTEMONE_SHADOW_ENABLED", True)
    _budget(monkeypatch, tmp_path, systemone=1)
    provider = RuntimeProvider(
        "openthai_systemone",
        "https://provider.invalid/systemone",
        "systemone-model",
        "synthetic-key",
        5,
        True,
        "systemone",
    )
    monkeypatch.setattr(systemone_client, "_configured_provider", lambda: provider)

    def handler(request):
        return httpx.Response(200, json={"answers": {"scope": {"type": "choice", "value": "lab"}}})

    original_client = httpx.AsyncClient

    def factory(*args, **kwargs):
        return original_client(transport=httpx.MockTransport(handler), timeout=kwargs.get("timeout"))

    monkeypatch.setattr(systemone_client.httpx, "AsyncClient", factory)
    result = asyncio.run(systemone_client.shadow_decide("Hb 10.8 g/dL", "lab", True))
    assert result["shadow"]["answers"]["scope"]["value"] == "lab"

    with pytest.raises(systemone_client.SystemOneError) as error:
        asyncio.run(systemone_client.shadow_decide("Hb 10.8 g/dL", "lab", True))
    assert error.value.code == "provider_budget_exhausted"
    assert "synthetic-key" not in json.dumps(result)
