from __future__ import annotations

import asyncio
import json
from pathlib import Path

from fastapi.testclient import TestClient

from main import app
from routers import chat as chat_router
from services import answer_service
from services.intent_router import route_intent
from services.public_reference import PublicReferenceAdapter, PublicReferenceLoadError
from services.store import MemoryConversationStore


ROOT = Path(__file__).resolve().parents[1]


def test_public_adapter_keeps_numeric_and_guideline_namespaces_separate():
    adapter = PublicReferenceAdapter(ROOT / "addons" / "resultscope_evidence_v1")

    numeric = adapter.search("ALT")
    guidance = adapter.search("ferritin")

    assert numeric is not None
    assert all(item.record.kind == "public_reference" for item in numeric.items)
    assert all(item.record.data["data_class"] == "public_reference" for item in numeric.items)
    assert guidance is not None
    assert all(item.record.kind == "open_guideline" for item in guidance.items)
    assert all(item.record.data["numeric_rule"] is False for item in guidance.items)
    assert {citation.source_id for citation in _citations(numeric)} == {"siriraj-alt", "kku-alt"}


def test_public_adapter_fails_closed_when_a_snapshot_is_missing(tmp_path):
    addon_root = tmp_path / "resultscope_evidence_v1"
    source_root = ROOT / "addons" / "resultscope_evidence_v1"
    import shutil

    shutil.copytree(source_root, addon_root)
    (addon_root / "data" / "sources" / "siriraj-alt.pdf").unlink()

    try:
        PublicReferenceAdapter(addon_root)
    except PublicReferenceLoadError:
        pass
    else:
        raise AssertionError("missing public source must fail closed")


def test_public_reference_is_disabled_by_default(monkeypatch):
    monkeypatch.setattr("config.settings.PUBLIC_REFERENCE_ENABLED", False)
    query = "What is the ALT reference range?"

    async def unexpected_provider(*args, **kwargs):
        raise AssertionError("provider must not run without normal approved evidence")

    monkeypatch.setattr(answer_service.llm_client, "chat", unexpected_provider)
    result = asyncio.run(answer_service.answer_query(query, route_intent(query), [], None))

    assert result.status == "error"
    assert result.citations == ()


def test_public_reference_answer_has_server_resolved_metadata(monkeypatch):
    monkeypatch.setattr("config.settings.PUBLIC_REFERENCE_ENABLED", True)
    query = "What is the ALT reference range?"

    async def fake_provider(*args, **kwargs):
        return "The sources [siriraj-alt] and [kku-alt] report different ALT intervals, so no single patient range is selected."

    monkeypatch.setattr(answer_service.llm_client, "chat", fake_provider)
    result = asyncio.run(answer_service.answer_query(query, route_intent(query), [], None))

    assert result.status == "answered"
    assert result.corpus_mode == "public_reference"
    assert result.metadata()["data_class"] == "public_reference"
    assert {citation.source_id for citation in result.citations} == {"siriraj-alt", "kku-alt"}
    assert {citation.page for citation in result.citations} == {1, 2}
    assert all(citation.source_url.startswith("https://") for citation in result.citations)
    assert all(citation.data_class == "public_reference" for citation in result.citations)


def test_public_guideline_citation_preserves_license_and_section(monkeypatch):
    monkeypatch.setattr("config.settings.PUBLIC_REFERENCE_ENABLED", True)
    query = "What context matters for ferritin?"

    async def fake_provider(*args, **kwargs):
        return "The educational guidance says ferritin needs context such as inflammation; it is not a numeric rule."

    monkeypatch.setattr(answer_service.llm_client, "chat", fake_provider)
    result = asyncio.run(answer_service.answer_query(query, route_intent(query), [], None))

    assert result.status == "answered"
    assert result.corpus_mode == "public_reference"
    assert result.citations
    assert all(citation.data_class == "open_guideline" for citation in result.citations)
    assert all(citation.license_text == "CC BY-NC-SA 3.0 IGO" for citation in result.citations)
    assert all(citation.section for citation in result.citations)
    assert {citation.page for citation in result.citations} == {37}
    assert all("iris.who.int" in citation.source_url and "download" in citation.source_url for citation in result.citations)


def test_public_reference_no_hit_and_corrupt_root_abstain(monkeypatch):
    monkeypatch.setattr("config.settings.PUBLIC_REFERENCE_ENABLED", True)
    monkeypatch.setattr("config.settings.PUBLIC_REFERENCE_ROOT", "missing-public-reference")
    query = "What is the ALT reference range?"

    async def unexpected_provider(*args, **kwargs):
        raise AssertionError("provider must not run when public source loading fails")

    monkeypatch.setattr(answer_service.llm_client, "chat", unexpected_provider)
    result = asyncio.run(answer_service.answer_query(query, route_intent(query), [], None))

    assert result.status == "abstained"
    assert result.error_code == "public_reference_unavailable"
    assert not result.citations


def test_public_reference_rejects_forged_citation_and_arbitrary_url(monkeypatch):
    monkeypatch.setattr("config.settings.PUBLIC_REFERENCE_ENABLED", True)
    query = "What is the ALT reference range?"

    async def fake_provider(*args, **kwargs):
        return "Reference [fake-source] https://evil.example/claim"

    monkeypatch.setattr(answer_service.llm_client, "chat", fake_provider)
    result = asyncio.run(answer_service.answer_query(query, route_intent(query), [], None))

    assert result.status == "abstained"
    assert result.error_code is None
    assert not result.citations


def test_public_reference_sync_and_sse_citations_match(monkeypatch):
    monkeypatch.setattr("config.settings.PUBLIC_REFERENCE_ENABLED", True)
    monkeypatch.setattr(chat_router, "conversation_store", MemoryConversationStore())

    async def fake_provider(*args, **kwargs):
        return "The sources disagree, so the report's own range remains primary."

    monkeypatch.setattr(chat_router.llm_client, "chat", fake_provider)
    client = TestClient(app)
    sync = client.post("/api/v1/chat", json={"message": "What is the ALT reference range?"})
    stream = client.post("/api/v1/chat/stream", json={"message": "What is the ALT reference range?"})

    assert sync.status_code == 200
    assert stream.status_code == 200
    events = [
        json.loads(line.removeprefix("data: "))
        for line in stream.text.splitlines()
        if line.startswith("data: ")
    ]
    stream_meta = next(event["response_meta"] for event in events if "response_meta" in event)
    assert sync.json()["data_class"] == "public_reference"
    assert stream_meta["data_class"] == "public_reference"
    assert sync.json()["citations"] == stream_meta["citations"]
    assert events[-1]["done"] is True


def _citations(bundle):
    return tuple(
        type(
            "CitationView",
            (),
            {
                "source_id": item.record.source_ids[0],
            },
        )()
        for item in bundle.items
    )
