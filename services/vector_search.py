"""MongoDB Atlas Vector Search as a semantic ranking adapter (the Render + Atlas RAG pattern).

What it does: embeds the question with an OpenAI-compatible embeddings endpoint, runs
`$vectorSearch` against an Atlas collection that holds one vector per verified evidence
record, and returns record IDs in ranked order.

What it never does: promote remote text into evidence. Atlas returns IDs and hashes only;
an ID is admitted only when it exists in the local verified catalog *and* its stored
content hash still matches, so a stale or tampered index cannot change what the assistant
cites. The answer text always comes from `knowledge/evidence/catalog.json`.

Off by default (`VECTOR_SEARCH_ENABLED=false`). The embedding call goes through the same
offline guard, call budget and 300 THB project ledger as every other provider call.
"""
from __future__ import annotations

import asyncio
from functools import lru_cache

from config import settings
from services.conversation_transport import ConversationError, post_json

DIMENSIONS = 1536  # text-embedding-3-small; must match the Atlas index definition


def index_definition() -> dict:
    """The Atlas Vector Search index this adapter expects (same shape as the Render tutorial)."""
    return {"fields": [
        {"type": "vector", "path": "embedding", "numDimensions": settings.EMBEDDING_DIMENSIONS, "similarity": "cosine"},
        {"type": "filter", "path": "data_class"},
    ]}


def configured() -> bool:
    return bool(settings.VECTOR_SEARCH_ENABLED and settings.MONGODB_URI and settings.EMBEDDING_API_KEY)


async def embed(texts: list[str]) -> list[list[float]]:
    if not settings.EMBEDDING_API_KEY:
        raise ConversationError("retrieval_unavailable", "The embeddings service is not configured.")
    data = await post_json(settings.EMBEDDING_BASE_URL.rstrip("/") + "/embeddings",
                           {"Authorization": "Bearer " + settings.EMBEDDING_API_KEY, "Content-Type": "application/json"},
                           {"model": settings.EMBEDDING_MODEL, "input": texts, "dimensions": settings.EMBEDDING_DIMENSIONS},
                           "retrieval", settings.RETRIEVAL_TIMEOUT_SECONDS)
    rows = data.get("data")
    if not isinstance(rows, list) or len(rows) != len(texts):
        raise ConversationError("retrieval_invalid", "The embeddings service returned an invalid result.", 502)
    vectors = [r.get("embedding") for r in sorted(rows, key=lambda r: r.get("index", 0))]
    if any(not isinstance(v, list) or len(v) != settings.EMBEDDING_DIMENSIONS for v in vectors):
        raise ConversationError("retrieval_invalid", "The embeddings have the wrong size for the vector index.", 502)
    return vectors


@lru_cache(maxsize=1)
def _client():
    from pymongo import MongoClient
    return MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=5000, connectTimeoutMS=5000,
                       socketTimeoutMS=int(settings.RETRIEVAL_TIMEOUT_SECONDS * 1000), appname="resultscope")


def collection():
    return _client()[settings.MONGODB_DB][settings.MONGODB_COLLECTION]


def _query(vector: list[float], limit: int) -> list[dict]:
    pipeline = [
        {"$vectorSearch": {"index": settings.MONGODB_VECTOR_INDEX, "path": "embedding", "queryVector": vector,
                           "numCandidates": max(50, limit * 10), "limit": limit}},
        {"$project": {"_id": 0, "record_id": 1, "content_sha256": 1, "score": {"$meta": "vectorSearchScore"}}},
    ]
    return list(collection().aggregate(pipeline, maxTimeMS=int(settings.RETRIEVAL_TIMEOUT_SECONDS * 1000)))


async def semantic_ids(query: str, known: dict[str, str], limit: int = 8) -> list[str]:
    """Ranked record IDs from Atlas, filtered to the verified catalog. `known` maps id -> content hash."""
    if not settings.VECTOR_SEARCH_ENABLED:
        return []
    if not configured():
        raise ConversationError("retrieval_unavailable", "Vector search is enabled but MONGODB_URI or the embeddings key is missing.")
    vector = (await embed([query[:2000]]))[0]
    try:
        hits = await asyncio.to_thread(_query, vector, limit)
    except Exception:
        # Never surface driver errors (they can contain hostnames or user names).
        raise ConversationError("retrieval_unavailable", "The vector search service did not respond.", 502) from None
    ids: list[str] = []
    for hit in hits:
        rid = hit.get("record_id") if isinstance(hit, dict) else None
        if isinstance(rid, str) and known.get(rid) == hit.get("content_sha256") and rid not in ids:
            ids.append(rid)
    return ids
