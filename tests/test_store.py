import asyncio

from services.store import MemoryConversationStore


def test_memory_store_roundtrip():
    async def scenario():
        store = MemoryConversationStore()
        await store.set("abc", [{"role": "user", "content": "CBC"}])
        history = await store.get("abc")
        assert history[0]["content"] == "CBC"
        await store.clear("abc")
        assert await store.get("abc") == []

    asyncio.run(scenario())
