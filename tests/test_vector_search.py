"""MongoDB Atlas Vector Search adapter. Doubles: the embeddings endpoint and the Atlas
collection (no network). Fusion, catalog admission and hash checks are real."""
from __future__ import annotations

import asyncio

import pytest

from config import settings
from scripts import index_evidence_vectors as indexer
from services import evidence_search, vector_search
from services.conversation_transport import ConversationError


class FakeCollection:
    def __init__(self, hits=None):
        self.hits = hits or []; self.docs = {}; self.pipelines = []

    def aggregate(self, pipeline, maxTimeMS=0):
        self.pipelines.append(pipeline); return list(self.hits)

    def find(self, query, projection):
        return [dict(d) for d in self.docs.values()]

    def bulk_write(self, ops):
        for op in ops:
            doc = op._doc; self.docs[doc["_id"]] = doc

    def delete_many(self, query):
        for rid in query["record_id"]["$in"]:
            self.docs.pop(rid, None)


@pytest.fixture
def enabled(monkeypatch):
    monkeypatch.setattr(settings, "VECTOR_SEARCH_ENABLED", True)
    monkeypatch.setattr(settings, "MONGODB_URI", "mongodb+srv://test.invalid")
    monkeypatch.setattr(settings, "EMBEDDING_API_KEY", "test-only")
    calls = []

    async def post_json(url, headers, body, slot, timeout):
        calls.append(body)
        return {"data": [{"index": i, "embedding": [0.1] * settings.EMBEDDING_DIMENSIONS} for i in range(len(body["input"]))],
                "usage": {"prompt_tokens": 10}}
    monkeypatch.setattr(vector_search, "post_json", post_json)
    return calls


def test_disabled_by_default_means_no_embedding_call_and_lexical_mode():
    assert settings.VECTOR_SEARCH_ENABLED is False
    docs, mode = asyncio.run(evidence_search.search("ALT liver enzyme"))
    assert mode == "lexical" and docs


def test_index_definition_matches_the_atlas_tutorial_shape():
    d = vector_search.index_definition()
    vec = d["fields"][0]
    assert vec == {"type": "vector", "path": "embedding", "numDimensions": 1536, "similarity": "cosine"}


def test_atlas_can_only_reorder_verified_records(monkeypatch, enabled):
    records = evidence_search.corpus()
    target = records[-1]
    fake = FakeCollection([
        {"record_id": "invented-record", "content_sha256": "x", "score": 0.99},          # not in the catalog
        {"record_id": records[0]["id"], "content_sha256": "stale-hash", "score": 0.98},  # hash no longer matches
        {"record_id": target["id"], "content_sha256": target["content_sha256"], "score": 0.97},
    ])
    monkeypatch.setattr(vector_search, "collection", lambda: fake)
    docs, mode = asyncio.run(evidence_search.search(target["title"]))
    assert mode == "hybrid_vector"
    ids = [d["id"] for d in docs]
    assert "invented-record" not in ids and target["id"] in ids
    # Evidence text is the local catalog record, not anything from Atlas.
    assert next(d for d in docs if d["id"] == target["id"]) is next(r for r in records if r["id"] == target["id"])
    assert fake.pipelines[0][0]["$vectorSearch"]["index"] == settings.MONGODB_VECTOR_INDEX
    assert enabled[0]["model"] == "text-embedding-3-small"


def test_enabled_without_credentials_fails_closed(monkeypatch):
    monkeypatch.setattr(settings, "VECTOR_SEARCH_ENABLED", True)
    monkeypatch.setattr(settings, "MONGODB_URI", "")
    with pytest.raises(ConversationError) as exc:
        asyncio.run(vector_search.semantic_ids("ALT", {}))
    assert exc.value.code == "retrieval_unavailable"


def test_driver_errors_are_not_surfaced(monkeypatch, enabled):
    class Broken:
        def aggregate(self, *a, **k):
            raise RuntimeError("mongodb+srv://user:secret@cluster.example")
    monkeypatch.setattr(vector_search, "collection", lambda: Broken())
    with pytest.raises(ConversationError) as exc:
        asyncio.run(vector_search.semantic_ids("ALT", {}))
    assert "secret" not in str(exc.value) and exc.value.code == "retrieval_unavailable"


def test_wrong_embedding_size_is_rejected(monkeypatch, enabled):
    async def post_json(url, headers, body, slot, timeout):
        return {"data": [{"index": 0, "embedding": [0.1] * 8}]}
    monkeypatch.setattr(vector_search, "post_json", post_json)
    with pytest.raises(ConversationError) as exc:
        asyncio.run(vector_search.embed(["ALT"]))
    assert exc.value.code == "retrieval_invalid"


def test_indexer_is_incremental_and_removes_stale_records(monkeypatch, enabled):
    fake = FakeCollection()
    fake.docs["old-record"] = {"_id": "old-record", "record_id": "old-record", "content_sha256": "x", "embedding_model": "text-embedding-3-small"}
    monkeypatch.setattr(vector_search, "collection", lambda: fake)
    first = asyncio.run(indexer.apply())
    n = len(evidence_search.corpus())
    assert first == {"records": n, "embedded": n, "unchanged": 0, "removed": 1}
    assert "old-record" not in fake.docs and len(enabled) == (n + indexer.BATCH - 1) // indexer.BATCH
    second = asyncio.run(indexer.apply())
    assert second["embedded"] == 0 and second["unchanged"] == n and len(enabled) == (n + indexer.BATCH - 1) // indexer.BATCH


def test_indexer_dry_run_sends_nothing(capsys, enabled):
    assert indexer.main([]) == 0
    assert "Dry run only" in capsys.readouterr().out and enabled == []
