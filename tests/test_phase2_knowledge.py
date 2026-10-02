from pathlib import Path

import pytest

from services.knowledge import KnowledgeLoadError, load_knowledge_base

ROOT = Path(__file__).resolve().parents[1]


def test_synthetic_index_is_explicit_and_contains_only_fixture_records():
    base = load_knowledge_base(ROOT, mode="synthetic", environment="test")

    assert base.mode == "synthetic"
    assert base.demo is True
    assert base.corpus_version == "resultscope-lab-demo-pending-v1"
    assert {record.data["service_id"] for record in base.records} == {
        "SYN-SVC-001",
        "SYN-SVC-002",
        "SYN-SVC-003",
    }
    assert {source.source_kind for source in base.sources.values()} == {"synthetic"}
    assert all("PENDING_SOURCE" not in record.content for record in base.records)
    assert all("evaluation" not in source.origin for source in base.sources.values())
    assert all("AGENTS.md" not in record.content for record in base.records)


def test_synthetic_index_is_rejected_outside_local_development():
    with pytest.raises(KnowledgeLoadError) as error:
        load_knowledge_base(ROOT, mode="synthetic", environment="production")

    assert error.value.code == "invalid_mode"


def test_release_index_fails_closed_and_never_substitutes_synthetic():
    with pytest.raises(KnowledgeLoadError) as error:
        load_knowledge_base(ROOT, mode="release", environment="development")

    assert error.value.code == "release_not_ready"
    assert "synthetic fallback is disabled" in error.value.message


def test_synthetic_index_rejects_structurally_invalid_corpus(tmp_path, monkeypatch):
    def structural_errors(root):
        return ["fixture structural error"]

    monkeypatch.setattr("services.knowledge.validate_corpus", structural_errors)

    with pytest.raises(KnowledgeLoadError) as error:
        load_knowledge_base(ROOT, mode="synthetic", environment="test")

    assert error.value.code == "invalid_corpus"
