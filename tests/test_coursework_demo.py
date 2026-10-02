import asyncio
import hashlib
from pathlib import Path

from services import answer_service
from services.answer_service import answer_query
from services.intent_router import route_intent
from services.knowledge import KnowledgeLoadError, _demo_source_snapshot, load_knowledge_base
from services.retrieval import retrieve

ROOT = Path(__file__).resolve().parents[1]


def test_coursework_demo_loads_15_services_with_verified_provenance():
    base = load_knowledge_base(ROOT, mode="synthetic", environment="test")
    services = [record for record in base.records if record.kind == "service" and record.data["service_id"].startswith("SVC-")]

    assert len(services) == 15
    assert base.corpus_version == "promptlab-synthetic-v1"
    assert {record.source_ids for record in services} == {("DEMO-SERVICES",)}
    assert base.sources["DEMO-SERVICES"].checksum == "962868d34a30925fac9f458ac7e1d67cd89a79452c4acd471138bb7923d51116"
    assert base.sources["DEMO-SERVICES"].origin.endswith("corpus/04_SERVICES.md")
    assert {record.data["price"]["amount"] for record in services} >= {120, 250, 350, 550}


def test_coursework_demo_indexes_one_service_representation_and_no_evaluation_inputs():
    base = load_knowledge_base(ROOT, mode="synthetic", environment="test")
    service_records = [record for record in base.records if record.kind == "service" and record.data["service_id"].startswith("SVC-")]
    origins = {source.origin for source in base.sources.values()}

    assert len(service_records) == len({record.data["service_id"] for record in service_records}) == 15
    assert all("services.json" not in source.origin for source in base.sources.values() if source.source_id == "DEMO-SERVICES")
    assert all("questions.jsonl" not in record.content for record in base.records)
    assert all("expected answers" not in record.content.casefold() for record in base.records)
    assert all("02_NORMAL_PATCH_PROMPT" not in record.content for record in base.records)
    assert all("images/" not in origin for origin in origins)
    assert all(source_id.startswith("DEMO-") or source_id == "SRC-SYNTHETIC-SERVICE-FIXTURE" for source_id in base.sources)


def test_coursework_demo_checksum_mismatch_fails_closed(tmp_path):
    demo_root = tmp_path / "demo"
    source_path = demo_root / "corpus" / "source.md"
    source_path.parent.mkdir(parents=True)
    source_path.write_text("canonical demo source\n", encoding="utf-8")
    row = {
        "source_id": "DEMO-TEST",
        "canonical_path": "corpus/source.md",
        "version": "test-v1",
        "sha256": hashlib.sha256(b"different bytes").hexdigest(),
        "data_class": "synthetic",
        "commercial_release_eligible": False,
    }

    try:
        _demo_source_snapshot(tmp_path, demo_root, row)
    except KnowledgeLoadError as error:
        assert error.code == "invalid_provenance"
    else:
        raise AssertionError("checksum mismatch must fail closed")


def test_demo_unknown_service_abstains_without_provider(monkeypatch):
    base = load_knowledge_base(ROOT, mode="synthetic", environment="test")

    async def unexpected_call(*args, **kwargs):
        raise AssertionError("unknown service must not call the provider")

    monkeypatch.setattr(answer_service.llm_client, "chat", unexpected_call)
    query = "มีบริการ MRI ไหม"
    result = asyncio.run(answer_query(query, route_intent(query), [], None, base=base))

    assert result.status == "abstained"
    assert result.citations == ()
    assert result.demo is True


def test_demo_missing_preparation_abstains_without_inventing_hours(monkeypatch):
    base = load_knowledge_base(ROOT, mode="synthetic", environment="test")

    async def unexpected_call(*args, **kwargs):
        raise AssertionError("missing preparation evidence must not call the provider")

    monkeypatch.setattr(answer_service.llm_client, "chat", unexpected_call)
    query = "ตรวจ FPG ต้องงดอาหารกี่ชั่วโมง"
    result = asyncio.run(answer_query(query, route_intent(query), [], None, base=base))

    assert result.status == "abstained"
    assert "price" not in result.text.casefold()


def test_demo_citation_and_q09_history_are_real_multi_turn(monkeypatch):
    base = load_knowledge_base(ROOT, mode="synthetic", environment="test")
    history = [
        {"role": "user", "content": "ขอถามเกี่ยวกับ HbA1c"},
        {"role": "assistant", "content": "สอบถามเรื่อง HbA1c ได้ครับ"},
    ]
    query = "แล้วรายการนั้นราคาเท่าไร"
    intent = route_intent(query, history)
    seen = {}

    async def fake_chat(fake_history, prompt, rule_grounding):
        seen["prompt"] = prompt
        return "HbA1c ราคา 350 THB"

    monkeypatch.setattr(answer_service.llm_client, "chat", fake_chat)
    result = asyncio.run(answer_query(query, intent, history, None, base=base))

    assert intent.kind == "business"
    assert intent.reason == "business_faq"
    assert result.status == "answered"
    assert result.citations
    assert result.citations[0].source_id == "DEMO-SERVICES"
    assert result.citations[0].version == "promptlab-synthetic-v1"
    assert "HbA1c" in seen["prompt"]
    assert "ข้อมูลธุรกิจสมมติสำหรับการเรียน ไม่รับบริการจริง" in result.metadata()["demo_notice"]


def test_demo_multi_service_price_derivations_are_grounded(monkeypatch):
    base = load_knowledge_base(ROOT, mode="synthetic", environment="test")
    query = "CBC กับ HbA1c ราคาต่างกันเท่าไร"
    result = retrieve(query, base)
    ids = {item.record.data.get("service_id") for item in result.items}
    assert {"SVC-001", "SVC-003"}.issubset(ids)

    async def fake_chat(history, prompt, rule_grounding):
        return "CBC 250 THB และ HbA1c 350 THB ต่างกัน 100 บาท"

    monkeypatch.setattr(answer_service.llm_client, "chat", fake_chat)
    answer = asyncio.run(answer_query(query, route_intent(query), [], None, base=base))
    assert answer.status == "answered"
    assert answer.citations
    assert "DEMO-SERVICES" in {citation.source_id for citation in answer.citations}
