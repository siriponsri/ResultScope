"""Build or refresh the MongoDB Atlas vector index for the verified evidence catalog.

    python scripts/index_evidence_vectors.py               # dry run: counts and the index JSON, no network
    python scripts/index_evidence_vectors.py --create-index  # create the Atlas Vector Search index (once)
    python scripts/index_evidence_vectors.py --apply       # embed new or changed records and upsert them

One vector per catalog record (records are already short, at most about 500 characters).
Re-running is incremental: a record whose content hash and embedding model are unchanged
is skipped, so a second run costs nothing. Records removed from the catalog are removed
from Atlas. Credentials are read from environment variables and are never printed.

`--apply` makes paid embedding calls. It needs PROVIDER_NETWORK_ENABLED=true and goes
through the project THB ledger like every other provider call.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import settings  # noqa: E402
from services import vector_search  # noqa: E402
from services.evidence_search import corpus  # noqa: E402

BATCH = 64


def text_for(record: dict) -> str:
    return "\n".join([record["title"], " ".join(record.get("aliases", [])), record["content"]]).strip()


def plan(existing: dict[str, dict]) -> tuple[list[dict], list[str]]:
    records = corpus()
    todo = [r for r in records if (existing.get(r["id"]) or {}).get("content_sha256") != r["content_sha256"]
            or (existing.get(r["id"]) or {}).get("embedding_model") != settings.EMBEDDING_MODEL]
    ids = {r["id"] for r in records}
    stale = [rid for rid in existing if rid not in ids]
    return todo, stale


async def apply() -> dict:
    col = vector_search.collection()
    existing = {d["record_id"]: d for d in col.find({}, {"_id": 0, "record_id": 1, "content_sha256": 1, "embedding_model": 1})}
    todo, stale = plan(existing)
    written = 0
    for start in range(0, len(todo), BATCH):
        batch = todo[start:start + BATCH]
        vectors = await vector_search.embed([text_for(r) for r in batch])
        from pymongo import ReplaceOne
        col.bulk_write([ReplaceOne({"_id": r["id"]}, {
            "_id": r["id"], "record_id": r["id"], "content_sha256": r["content_sha256"], "data_class": r["data_class"],
            "title": r["title"], "publisher": r.get("publisher", ""), "url": r["url"], "embedding": v,
            "embedding_model": settings.EMBEDDING_MODEL, "indexed_at": time.time()}, upsert=True) for r, v in zip(batch, vectors)])
        written += len(batch)
    if stale:
        col.delete_many({"record_id": {"$in": stale}})
    return {"records": len(corpus()), "embedded": written, "unchanged": len(corpus()) - written, "removed": len(stale)}


def create_index() -> str:
    from pymongo.operations import SearchIndexModel
    col = vector_search.collection()
    names = {i.get("name") for i in col.list_search_indexes()}
    if settings.MONGODB_VECTOR_INDEX in names:
        return "exists"
    col.create_search_index(SearchIndexModel(definition=vector_search.index_definition(), name=settings.MONGODB_VECTOR_INDEX, type="vectorSearch"))
    return "created (Atlas builds it in the background; wait until it shows READY)"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="embed and upsert (paid embedding calls)")
    ap.add_argument("--create-index", action="store_true", help="create the Atlas Vector Search index")
    args = ap.parse_args(argv)
    records = corpus()
    chars = sum(len(text_for(r)) for r in records)
    print(json.dumps({"catalog_records": len(records), "characters": chars, "estimated_tokens": chars // 3 + len(records),
                      "embedding_model": settings.EMBEDDING_MODEL, "dimensions": settings.EMBEDDING_DIMENSIONS,
                      "database": settings.MONGODB_DB, "collection": settings.MONGODB_COLLECTION,
                      "index_name": settings.MONGODB_VECTOR_INDEX, "index_definition": vector_search.index_definition()}, indent=2))
    if not (args.apply or args.create_index):
        print("Dry run only. Nothing was sent.")
        return 0
    if not settings.MONGODB_URI:
        print("MONGODB_URI is not set.", file=sys.stderr)
        return 2
    try:
        if args.create_index:
            print("Vector index:", create_index())
        if args.apply:
            if not (settings.VECTOR_SEARCH_ENABLED and settings.PROVIDER_NETWORK_ENABLED and settings.EMBEDDING_API_KEY):
                print("Set VECTOR_SEARCH_ENABLED=true, PROVIDER_NETWORK_ENABLED=true and EMBEDDING_API_KEY first.", file=sys.stderr)
                return 2
            print(json.dumps(asyncio.run(apply())))
    except Exception as exc:  # report the kind of failure without driver details (they can include hosts or users)
        print("Failed:", getattr(exc, "code", type(exc).__name__), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
