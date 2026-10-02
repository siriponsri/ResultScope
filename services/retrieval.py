from __future__ import annotations

import re
import time
import unicodedata
from dataclasses import dataclass

from services.knowledge import KnowledgeBase, KnowledgeRecord

STOP_WORDS = {
    "the", "a", "an", "is", "are", "what", "how", "much", "please", "for", "me", "about",
    "where", "in", "real", "laboratory", "nearest", "bangkok",
}
POLICY_QUERY_HINTS = (
    "prepare", "preparation", "specimen", "งดอาหาร", "เตรียมตัว", "สิ่งส่งตรวจ",
    "turnaround", "result time", "how long", "กี่วัน", "กี่ชั่วโมง", "ออกใน", "ใช้เวลา", "รับผล",
    "book", "booking", "appointment", "walk-in", "จอง", "คิว",
    "refund", "คืนเงิน", "cancel", "ยกเลิก", "ส่วนลด", "discount", "ลดให้",
)


def _normalized(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).casefold().split())


def _terms(value: str) -> set[str]:
    normalized = _normalized(value)
    terms = {term for term in re.findall(r"[a-z0-9]+", normalized) if term not in STOP_WORDS}
    for run in re.findall(r"[\u0e00-\u0e7f]+", normalized):
        if len(run) == 1:
            terms.add(run)
            continue
        for size in (2, 3):
            terms.update(run[index : index + size] for index in range(len(run) - size + 1))
    return terms


@dataclass(frozen=True)
class RetrievedRecord:
    record: KnowledgeRecord
    score: float


@dataclass(frozen=True)
class RetrievalResult:
    items: tuple[RetrievedRecord, ...]
    reason: str
    latency_ms: float


def _score(query: str, record: KnowledgeRecord) -> float:
    query_norm = _normalized(query).replace(" ", "")
    content = record.content
    aliases = record.data.get("aliases", []) if isinstance(record.data, dict) else []
    if isinstance(aliases, list):
        alias_values = [value for value in aliases if isinstance(value, str)]
    else:
        alias_values = []
    candidates = [record.data.get("service_id", ""), record.data.get("name_th", ""), *alias_values]
    for candidate in candidates:
        if isinstance(candidate, str):
            candidate_norm = _normalized(candidate).replace(" ", "")
            if candidate_norm and (candidate_norm in query_norm or query_norm in candidate_norm):
                return 1.0
    query_terms = _terms(query)
    if not query_terms:
        return 0.0
    ascii_terms = {
        term
        for term in re.findall(r"[a-z0-9]+", _normalized(query))
        if term not in STOP_WORDS
    }
    if ascii_terms:
        ascii_overlap = ascii_terms & {
            term for term in re.findall(r"[a-z0-9]+", _normalized(content)) if term not in STOP_WORDS
        }
        if not ascii_overlap:
            return 0.0
    overlap = query_terms & _terms(content)
    return len(overlap) / len(query_terms)


def _has_exact_alias_match(query: str, record: KnowledgeRecord) -> bool:
    query_norm = _normalized(query).replace(" ", "")
    aliases = record.data.get("aliases", []) if isinstance(record.data, dict) else []
    candidates = [record.data.get("service_id", ""), record.data.get("name_th", ""), *aliases]
    return any(
        isinstance(candidate, str)
        and (candidate_norm := _normalized(candidate).replace(" ", ""))
        and candidate_norm in query_norm
        for candidate in candidates
    )


def retrieve(
    query: str,
    base: KnowledgeBase,
    *,
    top_k: int = 4,
    min_score: float = 0.12,
    ambiguity_margin: float = 0.04,
) -> RetrievalResult:
    started = time.perf_counter()
    ranked = sorted(
        (RetrievedRecord(record, _score(query, record)) for record in base.records),
        key=lambda item: (item.score, item.record.record_id),
        reverse=True,
    )
    qualified = [item for item in ranked if item.score >= min_score][: max(1, top_k)]
    if any(term in _normalized(query) for term in POLICY_QUERY_HINTS):
        seen = {item.record.record_id for item in qualified}
        qualified.extend(
            RetrievedRecord(record, 0.5)
            for record in base.records
            if record.kind == "policy" and record.record_id not in seen
        )
        qualified = sorted(qualified, key=lambda item: (item.score, item.record.record_id), reverse=True)[: max(1, top_k)]
    if not qualified:
        reason = "no_match"
    elif (
        len(qualified) > 1
        and qualified[0].record.record_id != qualified[1].record.record_id
        and abs(qualified[0].score - qualified[1].score) < 1e-9
        and not (
            _has_exact_alias_match(query, qualified[0].record)
            and _has_exact_alias_match(query, qualified[1].record)
        )
    ):
        reason = "ambiguous"
        qualified = []
    else:
        reason = "matched"
    elapsed = (time.perf_counter() - started) * 1000
    return RetrievalResult(tuple(qualified), reason, round(elapsed, 3))
