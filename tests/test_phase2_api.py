import asyncio
import json

import pytest
from fastapi.testclient import TestClient

from main import app
from routers import chat as chat_router
from services import answer_service
from services.store import MemoryConversationStore


def _events(response):
    return [
        json.loads(line.removeprefix("data: "))
        for line in response.text.splitlines()
        if line.startswith("data: ")
    ]


def test_business_faq_is_allowed_but_abstains_without_a_source(monkeypatch):
    store = MemoryConversationStore()
    monkeypatch.setattr(chat_router, "conversation_store", store)
    monkeypatch.setattr("config.settings.KNOWLEDGE_MODE", "synthetic")

    async def unexpected_call(*args, **kwargs):
        raise AssertionError("a no-hit FAQ must not call the provider")

    monkeypatch.setattr(answer_service.llm_client, "chat", unexpected_call)
    client = TestClient(app)
    scope = client.post("/api/v1/scope/check", json={"message": "What are the lab opening hours?"})
    response = client.post("/api/v1/chat", json={"message": "What are the lab opening hours?"})

    assert scope.json()["allowed"] is True
    assert scope.json()["intent"] == "business"
    assert response.status_code == 200
    assert response.json()["status"] == "abstained"
    assert response.json()["citations"] == []
    assert response.json()["demo"] is True
    assert response.json()["data_class"] == "synthetic"
    assert response.json()["demo_notice"] == "ข้อมูลธุรกิจสมมติสำหรับการเรียน ไม่รับบริการจริง"


def test_synthetic_mode_shows_demo_notice_on_product_surface(monkeypatch):
    monkeypatch.setattr("config.settings.KNOWLEDGE_MODE", "synthetic")
    response = TestClient(app).get("/")

    assert response.status_code == 200
    assert "ข้อมูลธุรกิจสมมติสำหรับการเรียน ไม่รับบริการจริง" in response.text


def test_unrelated_and_unsafe_requests_bypass_provider_in_sync_and_stream(monkeypatch):
    monkeypatch.setattr(chat_router, "conversation_store", MemoryConversationStore())
    monkeypatch.setattr("config.settings.KNOWLEDGE_MODE", "synthetic")

    async def unexpected_call(*args, **kwargs):
        raise AssertionError("blocked intents must not call the provider")

    monkeypatch.setattr(chat_router.llm_client, "chat", unexpected_call)
    client = TestClient(app)
    unrelated = client.post("/api/v1/chat", json={"message": "Help me write Python"})
    unsafe = client.post("/api/v1/chat/stream", json={"message": "My Hb is low; should I change my dose?"})

    assert unrelated.json()["status"] == "refused"
    events = _events(unsafe)
    assert not any("delta" in event for event in events)
    assert sum("done" in event for event in events) == 1
    assert any(event.get("response_meta", {}).get("status") == "refused" for event in events)


def test_release_mode_is_blocked_and_never_falls_back_to_synthetic(monkeypatch):
    monkeypatch.setattr(chat_router, "conversation_store", MemoryConversationStore())
    monkeypatch.setattr("config.settings.KNOWLEDGE_MODE", "release")

    async def unexpected_call(*args, **kwargs):
        raise AssertionError("release corpus rejection must happen before provider call")

    monkeypatch.setattr(chat_router.llm_client, "chat", unexpected_call)
    client = TestClient(app)
    response = client.post("/api/v1/chat", json={"message": "Tell me about synthetic basic panel"})
    stream = client.post("/api/v1/chat/stream", json={"message": "Tell me about synthetic basic panel"})

    assert response.status_code == 503
    assert response.json()["code"] == "release_not_ready"
    assert response.json()["metadata"]["demo"] is False
    events = _events(stream)
    assert not any("delta" in event for event in events)
    assert sum("done" in event for event in events) == 1
    assert any(event.get("error", False) and event.get("code") == "release_not_ready" for event in events)


def test_sync_and_stream_share_the_same_validated_answer(monkeypatch):
    monkeypatch.setattr(chat_router, "conversation_store", MemoryConversationStore())
    monkeypatch.setattr("config.settings.KNOWLEDGE_MODE", "synthetic")

    async def fake_chat(history, message, rule_grounding):
        return "This is a synthetic service example."

    monkeypatch.setattr(chat_router.llm_client, "chat", fake_chat)
    client = TestClient(app)
    sync = client.post("/api/v1/chat", json={"message": "Tell me about synthetic basic panel"})
    stream = client.post("/api/v1/chat/stream", json={"message": "Tell me about synthetic basic panel"})
    events = _events(stream)
    meta = next(event["response_meta"] for event in events if "response_meta" in event)
    answer = next(event["delta"] for event in events if "delta" in event)

    assert sync.status_code == 200
    assert sync.json()["reply"] == answer
    assert sync.json()["status"] == meta["status"] == "answered"
    assert sync.json()["citations"] == meta["citations"]
    assert sync.json()["data_class"] == meta["data_class"] == "synthetic"
    assert sync.json()["demo_notice"] == meta["demo_notice"]


def test_provider_error_stream_has_no_unvalidated_delta_and_done_once(monkeypatch):
    monkeypatch.setattr(chat_router, "conversation_store", MemoryConversationStore())
    monkeypatch.setattr("config.settings.KNOWLEDGE_MODE", "synthetic")

    async def failing_chat(*args, **kwargs):
        from services.llm_client import LLMConnectionError

        raise LLMConnectionError("Provider temporarily unavailable", status_code=502)

    monkeypatch.setattr(chat_router.llm_client, "chat", failing_chat)
    response = TestClient(app).post(
        "/api/v1/chat/stream", json={"message": "Tell me about synthetic basic panel"}
    )
    events = _events(response)

    assert not any("delta" in event for event in events)
    assert sum("done" in event for event in events) == 1
    assert sum(bool(event.get("error")) for event in events) == 1
