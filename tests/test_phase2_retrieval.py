import json
from pathlib import Path

from services.knowledge import load_knowledge_base
from services.retrieval import retrieve

ROOT = Path(__file__).resolve().parents[1]


def test_retrieval_cases_cover_english_thai_and_no_hit():
    base = load_knowledge_base(ROOT, mode="synthetic", environment="test")
    cases = [
        json.loads(line)
        for line in (ROOT / "evaluation" / "retrieval_cases.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert len(cases) >= 5
    for case in cases:
        result = retrieve(case["query"], base)
        actual = [item.record.data.get("service_id") for item in result.items]
        expected = case["expected_record_ids"]
        assert actual[: len(expected)] == expected if expected else not actual


def test_retrieval_preserves_version_and_source_boundaries():
    base = load_knowledge_base(ROOT, mode="synthetic", environment="test")
    result = retrieve("synthetic chemistry panel", base)

    assert result.reason == "matched"
    assert result.items[0].record.data["service_id"] == "SYN-SVC-002"
    assert result.items[0].record.corpus_version == base.corpus_version
    assert result.items[0].record.chunk_id == result.items[0].record.record_id
    assert result.items[0].record.source_ids == ("SRC-SYNTHETIC-SERVICE-FIXTURE",)


def test_retrieval_marks_equal_matches_as_ambiguous():
    base = load_knowledge_base(ROOT, mode="synthetic", environment="test")

    result = retrieve("synthetic", base)

    assert result.reason == "ambiguous"
    assert result.items == ()
