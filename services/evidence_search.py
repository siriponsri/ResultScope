"""BM25 lexical retrieval plus an optional LightRAG semantic/graph ranking adapter.

Remote text is never promoted into evidence. Only exact manifest-backed document
IDs are admitted, and their content/URL comes from the local verified corpus.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter
from functools import lru_cache
from pathlib import Path

from config import settings
from services.conversation_transport import ConversationError, post_json

ROOT = Path(__file__).resolve().parents[1]


@lru_cache(maxsize=1)
def corpus() -> list[dict]:
    path = ROOT / "knowledge" / "evidence" / "catalog.json"
    try:
        package = json.loads(path.read_text(encoding="utf-8"))
        records = package["records"]
        seen = set()
        for row in records:
            if row["id"] in seen or row["data_class"] not in {"public_reference", "public_education"}:
                raise ValueError
            seen.add(row["id"])
            if hashlib.sha256(row["content"].encode()).hexdigest() != row["content_sha256"]:
                raise ValueError
            if row.get("source_file"):
                source = (ROOT / row["source_file"]).resolve()
                if not source.is_relative_to((ROOT / "knowledge").resolve()) or hashlib.sha256(source.read_bytes()).hexdigest() != row.get("source_sha256"):
                    raise ValueError
            if not row["url"].startswith("https://"):
                raise ValueError
        return records
    except (OSError, ValueError, KeyError, TypeError):
        raise ConversationError("evidence_unavailable", "The verified reference collection is unavailable.") from None


def tokens(text: str) -> list[str]:
    text = text.casefold()
    latin = re.findall(r"[a-z0-9]+", text)
    # LLM query translation handles arbitrary languages. Thai bigrams also
    # support local lexical lookup without pretending this is semantic search.
    thai = re.findall(r"[\u0e00-\u0e7f]+", text)
    return latin + [word[i:i+2] for word in thai for i in range(len(word)-1)]


def lexical(query: str, limit: int = 6) -> list[dict]:
    docs = corpus()
    vectors = [Counter(tokens(r["title"] + " " + " ".join(r.get("aliases", [])) + " " + r["content"])) for r in docs]
    n = len(docs)
    lengths = [sum(d.values()) for d in vectors]
    avg = sum(lengths) / max(1, n)
    q = set(tokens(query))
    scores = []
    for index, vector in enumerate(vectors):
        score = 0.0
        for term in q:
            freq = vector[term]
            if not freq:
                continue
            df = sum(term in v for v in vectors)
            idf = math.log(1 + (n - df + .5) / (df + .5))
            score += idf * (freq * 2.5) / (freq + 1.5 * (.25 + .75 * lengths[index] / max(1, avg)))
        if score > 0:
            scores.append((score, index))
    return [docs[i] for _, i in sorted(scores, key=lambda x: (-x[0], docs[x[1]]["id"]))[:limit]]


async def semantic_ids(query: str) -> list[str]:
    if not settings.LIGHTRAG_ENABLED:
        return []
    if not settings.LIGHTRAG_URL or not settings.LIGHTRAG_API_KEY:
        raise ConversationError("retrieval_unavailable", "The configured semantic search service is incomplete.")
    data = await post_json(settings.LIGHTRAG_URL.rstrip("/") + "/query/data",
        {"X-API-Key": settings.LIGHTRAG_API_KEY, "Content-Type": "application/json"},
        {"query": query, "mode": "mix", "chunk_top_k": 8, "top_k": 8,
         "max_total_tokens": 2500, "include_references": True, "include_chunk_content": True},
        "retrieval", settings.RETRIEVAL_TIMEOUT_SECONDS)
    if data.get("status") != "success" or not isinstance(data.get("data"), dict):
        raise ConversationError("retrieval_invalid", "Semantic search did not return a valid evidence result.", 502)
    chunks = data["data"].get("chunks")
    if not isinstance(chunks, list):
        raise ConversationError("retrieval_invalid", "Semantic search did not return evidence chunks.", 502)
    known = {r["id"] for r in corpus()}
    ids = []
    for chunk in chunks:
        if not isinstance(chunk, dict):
            continue
        path = chunk.get("file_path", "")
        if isinstance(path, str) and path.startswith("resultscope://evidence/"):
            candidate = path.removeprefix("resultscope://evidence/")
            if candidate in known and candidate not in ids:
                ids.append(candidate)
    return ids


async def search(query: str, limit: int = 6) -> tuple[list[dict], str]:
    local = lexical(query, limit=10)
    remote = await semantic_ids(query)
    if not settings.LIGHTRAG_ENABLED:
        return local[:limit], "lexical"
    # Reciprocal rank fusion preserves lexical exact-test matches.
    scores: dict[str, float] = {}
    for ranking in ([r["id"] for r in local], remote):
        for rank, record_id in enumerate(ranking, 1):
            scores[record_id] = scores.get(record_id, 0) + 1 / (60 + rank)
    by_id = {r["id"]: r for r in corpus()}
    ranked = sorted(scores, key=lambda rid: (-scores[rid], rid))
    return [by_id[rid] for rid in ranked[:limit]], "hybrid" if remote else "lexical_no_semantic_match"
