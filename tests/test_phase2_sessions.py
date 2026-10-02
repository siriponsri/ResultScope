import asyncio

from fastapi.testclient import TestClient

from main import app
from routers import chat as chat_router
from services.sessions import sign_session_id, verify_session_cookie
from services.store import MemoryConversationStore


def test_tampered_cookie_gets_replaced_and_reset_rotates_session(monkeypatch):
    store = MemoryConversationStore()
    monkeypatch.setattr(chat_router, "conversation_store", store)
    client = TestClient(app)
    client.cookies.set(
        chat_router.SESSION_COOKIE,
        "00000000-0000-0000-0000-000000000000.invalid",
        domain="testserver.local",
        path="/",
    )

    first = client.post("/api/v1/chat", json={"message": "Help me write Python"})
    old_token = client.cookies.get(chat_router.SESSION_COOKIE, domain="testserver.local", path="/")
    old_id = verify_session_cookie(old_token)
    reset = client.post("/api/v1/chat/reset")
    new_token = client.cookies.get(chat_router.SESSION_COOKIE, domain="testserver.local", path="/")

    assert first.status_code == 200
    assert old_id is not None
    assert reset.status_code == 200
    assert verify_session_cookie(new_token) is not None
    assert new_token != old_token


def test_sessions_are_isolated_for_lab_followups(monkeypatch):
    store = MemoryConversationStore()
    monkeypatch.setattr(chat_router, "conversation_store", store)
    monkeypatch.setattr("config.settings.KNOWLEDGE_MODE", "synthetic")
    first = TestClient(app)
    second = TestClient(app)

    initial = first.post("/api/v1/chat", json={"message": "Ferritin 7 ng/mL"})
    followup_a = first.post("/api/v1/scope/check", json={"message": "Should I be concerned?"})
    followup_b = second.post("/api/v1/scope/check", json={"message": "Should I be concerned?"})

    assert initial.status_code == 200
    assert initial.json()["status"] == "abstained"
    assert followup_a.json()["allowed"] is True
    assert followup_a.json()["intent"] == "lab"
    assert followup_b.json()["allowed"] is False


def test_same_session_concurrent_turns_are_serialized(monkeypatch):
    store = MemoryConversationStore()
    monkeypatch.setattr(chat_router, "conversation_store", store)
    monkeypatch.setattr("config.settings.KNOWLEDGE_MODE", "synthetic")

    async def fake_chat(history, message, rule_grounding):
        await asyncio.sleep(0.01)
        return "A synthetic service example."

    monkeypatch.setattr(chat_router.llm_client, "chat", fake_chat)
    session_id = "1374fd94-45eb-4ad9-b4cc-d013f2be48c3"
    cookie = f"{chat_router.SESSION_COOKIE}={sign_session_id(session_id)}"

    async def scenario():
        import httpx

        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test", headers={"Cookie": cookie}) as client:
            responses = await asyncio.gather(
                client.post("/api/v1/chat", json={"message": "Tell me about synthetic basic panel"}),
                client.post("/api/v1/chat", json={"message": "Tell me about synthetic chemistry panel"}),
            )
        return responses

    responses = asyncio.run(scenario())
    history = asyncio.run(store.get(session_id))

    assert all(response.status_code == 200 for response in responses)
    assert len(history) == 4
    assert [item["role"] for item in history] == ["user", "assistant", "user", "assistant"]
