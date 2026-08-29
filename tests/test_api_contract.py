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


def test_default_same_origin_configuration_does_not_emit_wildcard_cors():
    response = client.get("/health", headers={"Origin": "https://untrusted.example"})
    assert response.headers.get("access-control-allow-origin") is None


def test_stream_sends_deterministic_meta_before_llm_delta(monkeypatch):
    captured = {}

    async def fake_stream(history, message, rule_grounding):
        captured["grounding"] = rule_grounding
        yield {"type": "delta", "content": "Grounded answer"}
        yield {"type": "done"}

    monkeypatch.setattr(chat_router, "conversation_store", MemoryConversationStore())
    monkeypatch.setattr(chat_router.llm_client, "chat_stream", fake_stream)

    response = client.post(
        "/api/v1/chat/stream",
        json={"message": "Hb 10.8 g/dL (12-16) ช่วยอธิบาย"},
    )
    assert response.status_code == 200
    events = [
        json.loads(line.removeprefix("data: "))
        for line in response.text.splitlines()
        if line.startswith("data: ")
    ]
    meta_index = next(index for index, event in enumerate(events) if "analysis_meta" in event)
    delta_index = next(index for index, event in enumerate(events) if "delta" in event)
    assert meta_index < delta_index
    assert events[meta_index]["analysis_meta"]["values"][0]["flag"] == "low"
    assert "AUTHORITATIVE DETERMINISTIC PRE-ANSWER CONTRACT" in captured["grounding"]


def test_failed_allowed_stream_retains_lab_context_for_follow_up(monkeypatch):
    async def failing_stream(history, message, rule_grounding):
        yield {"type": "error", "message": "Provider unavailable"}

    store = MemoryConversationStore()
    monkeypatch.setattr(chat_router, "conversation_store", store)
    monkeypatch.setattr(chat_router.llm_client, "chat_stream", failing_stream)

    response = client.post(
        "/api/v1/chat/stream", json={"message": "Hb 10.8 g/dL (12-16)"}
    )
    assert response.status_code == 200

    scope = client.post("/api/v1/scope/check", json={"message": "Why does that matter?"})
    assert scope.status_code == 200
    assert scope.json()["allowed"] is True
    assert scope.json()["reason"] == "lab_follow_up"
