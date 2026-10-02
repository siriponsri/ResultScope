import asyncio

from services import answer_service
from services.intent_router import route_intent
from services.knowledge import load_knowledge_base


def test_grounded_answer_returns_resolved_source_and_version(monkeypatch):
    base = load_knowledge_base(mode="synthetic", environment="test")

    async def fake_chat(history, message, rule_grounding):
        assert "SRC-SYNTHETIC-SERVICE-FIXTURE" in message
        return "This is a synthetic service example."

    monkeypatch.setattr(answer_service.llm_client, "chat", fake_chat)
    intent = route_intent("Tell me about synthetic basic panel")
    result = asyncio.run(answer_service.answer_query("Tell me about synthetic basic panel", intent, [], None, base=base))

    assert result.status == "answered"
    assert result.demo is True
    assert result.citations[0].source_id == "SRC-SYNTHETIC-SERVICE-FIXTURE"
    assert result.citations[0].version == "synthetic-services-v1"
    assert result.citations[0].chunk_id == result.citations[0].record_id
    assert "Sources:" in result.text


def test_fabricated_numeric_fact_abstains(monkeypatch):
    base = load_knowledge_base(mode="synthetic", environment="test")

    async def fake_chat(history, message, rule_grounding):
        return "The synthetic service costs 99 baht."

    monkeypatch.setattr(answer_service.llm_client, "chat", fake_chat)
    query = "Tell me about synthetic basic panel"
    result = asyncio.run(answer_service.answer_query(query, route_intent(query), [], None, base=base))

    assert result.status == "abstained"
    assert not result.citations


def test_fabricated_source_marker_abstains(monkeypatch):
    base = load_knowledge_base(mode="synthetic", environment="test")

    async def fake_chat(history, message, rule_grounding):
        return "This example is confirmed [SRC-FAKE-SOURCE]."

    monkeypatch.setattr(answer_service.llm_client, "chat", fake_chat)
    query = "Tell me about synthetic basic panel"
    result = asyncio.run(answer_service.answer_query(query, route_intent(query), [], None, base=base))

    assert result.status == "abstained"
    assert result.citations == ()


def test_no_matching_or_approved_lab_evidence_never_calls_provider(monkeypatch):
    base = load_knowledge_base(mode="synthetic", environment="test")

    async def unexpected_call(*args, **kwargs):
        raise AssertionError("provider must not run without relevant evidence")

    monkeypatch.setattr(answer_service.llm_client, "chat", unexpected_call)
    business_query = "What are the lab opening hours?"
    result = asyncio.run(
        answer_service.answer_query(business_query, route_intent(business_query), [], None, base=base)
    )
    lab_query = "Should I be concerned?"
    lab_intent = route_intent(lab_query, [{"role": "user", "content": "Ferritin 7 ng/mL"}])
    lab_result = asyncio.run(answer_service.answer_query(lab_query, lab_intent, [], None, base=base))

    assert result.status == "abstained"
    assert lab_result.status == "abstained"
    assert not result.citations
    assert not lab_result.citations
