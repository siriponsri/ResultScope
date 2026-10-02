import json

from fastapi.testclient import TestClient

from main import app
from routers import chat as chat_router
from services.store import MemoryConversationStore


client = TestClient(app)


def test_rulebook_endpoint_and_home_surface():
    rulebook = client.get("/api/v1/rules")
    assert rulebook.status_code == 200
    assert rulebook.json()["version"] == "2026.08"

    home = client.get("/")
    assert home.status_code == 200
    assert "Read the signal" in home.text
    assert "Open full rulebook" in home.text
    assert 'id="image-input"' in home.text
    assert 'id="image-review"' in home.text


def test_default_same_origin_configuration_does_not_emit_wildcard_cors():
    response = client.get("/health", headers={"Origin": "https://untrusted.example"})
    assert response.headers.get("access-control-allow-origin") is None


def test_stream_uses_validated_answer_pipeline_and_resolves_citations(monkeypatch):
    captured = {}

    async def fake_chat(history, message, rule_grounding):
        captured["grounding"] = rule_grounding
        return "Grounded synthetic answer"

    monkeypatch.setattr(chat_router, "conversation_store", MemoryConversationStore())
    monkeypatch.setattr("config.settings.KNOWLEDGE_MODE", "synthetic")
    monkeypatch.setattr(chat_router.llm_client, "chat", fake_chat)

    response = client.post(
        "/api/v1/chat/stream",
        json={"message": "Tell me about synthetic basic panel"},
    )
    assert response.status_code == 200
    events = [
        json.loads(line.removeprefix("data: "))
        for line in response.text.splitlines()
        if line.startswith("data: ")
    ]
    meta_index = next(index for index, event in enumerate(events) if "response_meta" in event)
    delta_index = next(index for index, event in enumerate(events) if "delta" in event)
    assert meta_index < delta_index
    assert events[meta_index]["response_meta"]["demo"] is True
    assert events[meta_index]["response_meta"]["citations"][0]["source_id"] == "SRC-SYNTHETIC-SERVICE-FIXTURE"
    assert events[delta_index]["delta"].startswith("Grounded synthetic answer")
    assert "retrieved source facts" in captured["grounding"]


def test_lab_abstention_retains_context_for_follow_up(monkeypatch):
    store = MemoryConversationStore()
    monkeypatch.setattr(chat_router, "conversation_store", store)
    monkeypatch.setattr("config.settings.KNOWLEDGE_MODE", "synthetic")

    response = client.post(
        "/api/v1/chat/stream", json={"message": "Hb 10.8 g/dL (12-16)"}
    )
    assert response.status_code == 200

    scope = client.post("/api/v1/scope/check", json={"message": "Why does that matter?"})
    assert scope.status_code == 200
    assert scope.json()["allowed"] is True
    assert scope.json()["reason"] == "lab_follow_up"
