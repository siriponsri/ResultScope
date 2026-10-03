import asyncio
from pathlib import Path

import httpx
import pytest

from services.store import ConversationStoreError, MemoryConversationStore, SQLiteConversationStore, UpstashConversationStore


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


def test_sqlite_reset_recovery_journal_survives_store_reopen(tmp_path: Path):
    async def scenario():
        path = tmp_path / "conversation.sqlite3"
        payload = {
            "state": "pending",
            "history": [{"role": "user", "content": "CBC"}],
            "extractions": [],
        }
        first = SQLiteConversationStore(str(path))
        await first.save_reset_recovery("session-1", payload)

        reopened = SQLiteConversationStore(str(path))
        assert await reopened.get_reset_recovery("session-1") == payload
        await reopened.clear_reset_recovery("session-1")
        assert await reopened.get_reset_recovery("session-1") is None

    asyncio.run(scenario())


def test_memory_reset_recovery_ignores_completed_journal():
    async def scenario():
        store = MemoryConversationStore()
        await store.save_reset_recovery("session-1", {"state": "completed", "history": [], "extractions": []})
        assert await store.get_reset_recovery("session-1") is None

    asyncio.run(scenario())


def test_upstash_reset_recovery_uses_session_ttl(monkeypatch):
    async def scenario():
        store = UpstashConversationStore("https://store.invalid", "synthetic-test-token")
        commands = []

        async def fake_command(command):
            commands.append(command)
            return "OK"

        monkeypatch.setattr(store, "_command", fake_command)
        await store.save_reset_recovery("session-1", {"state": "pending", "history": [], "extractions": []})
        assert commands[0][0:3] == ["SETEX", "resultscope:reset-recovery:session-1", 86400]

    asyncio.run(scenario())
