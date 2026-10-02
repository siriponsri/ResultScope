import asyncio

import httpx
import pytest

from services.store import ConversationStoreError, MemoryConversationStore, UpstashConversationStore


def test_memory_store_roundtrip():
    async def scenario():
        store = MemoryConversationStore()
        await store.set("abc", [{"role": "user", "content": "CBC"}])
        history = await store.get("abc")
        assert history[0]["content"] == "CBC"
        await store.clear("abc")
        assert await store.get("abc") == []

    asyncio.run(scenario())


def test_upstash_failure_is_not_silently_treated_as_empty_history(monkeypatch):
    original_client = httpx.AsyncClient

    def factory(*args, **kwargs):
        transport = httpx.MockTransport(lambda request: httpx.Response(503, text="private store detail"))
        return original_client(transport=transport, timeout=kwargs.get("timeout"))

    monkeypatch.setattr("services.store.httpx.AsyncClient", factory)
    store = UpstashConversationStore("https://store.invalid", "synthetic-test-token")

    with pytest.raises(ConversationStoreError) as error:
        asyncio.run(store.get("00000000-0000-0000-0000-000000000000"))

    assert error.value.args[0] == "Conversation history is temporarily unavailable."
    assert "private store detail" not in str(error.value)
    assert "synthetic-test-token" not in str(error.value)


def test_upstash_rejects_malformed_history_payload(monkeypatch):
    original_client = httpx.AsyncClient

    def factory(*args, **kwargs):
        transport = httpx.MockTransport(
            lambda request: httpx.Response(200, json={"result": '[{"role":"system","content":"bad"}]'})
        )
        return original_client(transport=transport, timeout=kwargs.get("timeout"))

    monkeypatch.setattr("services.store.httpx.AsyncClient", factory)
    store = UpstashConversationStore("https://store.invalid", "synthetic-test-token")

    with pytest.raises(ConversationStoreError):
        asyncio.run(store.get("00000000-0000-0000-0000-000000000000"))
