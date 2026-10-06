import json

from fastapi.testclient import TestClient

from main import app
from routers import chat as chat_router
from services.store import MemoryConversationStore
from services.extraction_store import MemoryExtractionStore


client = TestClient(app)


def test_rulebook_endpoint_and_home_surface():
    rulebook = client.get("/api/v1/rules")
    assert rulebook.status_code == 200
    assert rulebook.json()["version"] == "2026.08"

    home = client.get("/")
    assert home.status_code == 200
    assert "Book the check. Understand the result." in home.text  # v5 home: two products (owner direction 2026-10-06)
    assert "/lab-reports" in home.text and "฿355" in home.text
    assert 'lang="en"' in home.text
    assert '/app' in home.text
    lab = client.get('/lab')
    assert 'id="report-dialog"' in lab.text
    assert '/static/js/conversation.js' in lab.text


def test_default_same_origin_configuration_does_not_emit_wildcard_cors():
    response = client.get("/health", headers={"Origin": "https://untrusted.example"})
    assert response.headers.get("access-control-allow-origin") is None


def test_stream_uses_validated_answer_pipeline_and_resolves_citations(monkeypatch):
    captured = {}

    async def fake_chat(history, message, rule_grounding):
        captured["grounding"] = rule_grounding
        return "Grounded synthetic answer"

    monkeypatch.setattr(chat_router, "conversation_store", MemoryConversationStore())
    monkeypatch.setattr("config.settings.KNOWLEDGE_MODE", "synthetic")
    monkeypatch.setattr(chat_router.llm_client, "chat", fake_chat)

    response = client.post(
        "/api/v1/chat/stream",
        json={"message": "Tell me about synthetic basic panel"},
    )
    assert response.status_code == 200
    events = [
        json.loads(line.removeprefix("data: "))
        for line in response.text.splitlines()
        if line.startswith("data: ")
    ]
    meta_index = next(index for index, event in enumerate(events) if "response_meta" in event)
    delta_index = next(index for index, event in enumerate(events) if "delta" in event)
    assert meta_index < delta_index
    assert events[meta_index]["response_meta"]["demo"] is True
    assert events[meta_index]["response_meta"]["citations"][0]["source_id"] == "SRC-SYNTHETIC-SERVICE-FIXTURE"
    assert events[delta_index]["delta"].startswith("Grounded synthetic answer")
    assert "retrieved source facts" in captured["grounding"]


def test_lab_abstention_retains_context_for_follow_up(monkeypatch):
    store = MemoryConversationStore()
    monkeypatch.setattr(chat_router, "conversation_store", store)
    monkeypatch.setattr("config.settings.KNOWLEDGE_MODE", "synthetic")

    response = client.post(
        "/api/v1/chat/stream", json={"message": "Hb 10.8 g/dL (12-16)"}
    )
    assert response.status_code == 200

    scope = client.post("/api/v1/scope/check", json={"message": "Why does that matter?"})
    assert scope.status_code == 200
    assert scope.json()["allowed"] is True
    assert scope.json()["reason"] == "lab_follow_up"


def test_focus_field_context_is_session_bound_and_limited_to_selected_field(monkeypatch):
    from services.extraction_store import MemoryExtractionStore

    extraction_store = MemoryExtractionStore()
    monkeypatch.setattr(chat_router, "extraction_store", extraction_store)
    monkeypatch.setattr(chat_router, "conversation_store", MemoryConversationStore())
    monkeypatch.setattr("config.settings.KNOWLEDGE_MODE", "synthetic")

    record = __import__("asyncio").run(
        extraction_store.create(
            "focus-session",
            "synthetic laboratory report",
            [
                {
                    "field_id": "hb", "marker": "Hb", "raw_value": "10.8",
                    "numeric_value": "10.8", "unit": "g/dL", "reference_low": "12",
                    "reference_high": "16", "reference_range_raw": "12-16",
                    "flag": "low",
                },
                {
                    "field_id": "mcv", "marker": "MCV", "raw_value": "72",
                    "numeric_value": "72", "unit": "fL", "reference_low": "80",
                    "reference_high": "100", "reference_range_raw": "80-100",
                    "flag": "low",
                },
            ],
            [],
        )
    )
    # The route helper is the authority; use a confirmed record without a provider call.
    record = record.__class__(
        record.extraction_id, record.session_id, record.revision, "confirmed",
        record.document_type, record.fields, record.warnings, record.created_at,
        record.expires_at, record.confirmed_at,
    )
    extraction_store._data[record.extraction_id] = record

    focused = __import__("asyncio").run(
        chat_router._load_confirmed_extraction("focus-session", record.extraction_id, "hb")
    )
    assert focused["focus_field_id"] == "hb"
    assert [field["field_id"] for field in focused["fields"]] == ["hb"]
    assert focused["fields"][0]["reference_range_raw"] == "12-16"
    assert "provenance" not in focused["fields"][0]


def test_invalid_focus_field_is_rejected_before_provider(monkeypatch):
    from services.extraction_store import MemoryExtractionStore

    extraction_store = MemoryExtractionStore()
    monkeypatch.setattr(chat_router, "extraction_store", extraction_store)
    monkeypatch.setattr(chat_router, "conversation_store", MemoryConversationStore())
    called = False

    async def unexpected_call(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("invalid focus must not call the provider")

    monkeypatch.setattr(chat_router.llm_client, "chat", unexpected_call)
    client = TestClient(app)
    response = client.post(
        "/api/v1/chat",
        json={"message": "Explain this result", "focus_field_id": "hb"},
    )
    assert response.status_code == 422
    assert response.json()["code"] == "focus_field_requires_extraction"
    assert called is False


def _confirmed_record(store, session_id="focus-session"):
    import asyncio
    record = asyncio.run(
        store.create(
            session_id,
            "synthetic laboratory report",
            [
                {
                    "field_id": "hb", "marker": "Hb", "raw_value": "10.8",
                    "numeric_value": "10.8", "unit": "g/dL", "reference_low": "12",
                    "reference_high": "16", "reference_range_raw": "12-16",
                    "flag": "low",
                },
                {
                    "field_id": "mcv", "marker": "MCV", "raw_value": "72",
                    "numeric_value": "72", "unit": "fL", "reference_low": "80",
                    "reference_high": "100", "reference_range_raw": "80-100",
                    "flag": "low",
                },
            ],
            [],
        )
    )
    confirmed = record.__class__(
        record.extraction_id, record.session_id, record.revision, "confirmed",
        record.document_type, record.fields, record.warnings, record.created_at,
        record.expires_at, record.confirmed_at,
    )
    store._data[record.extraction_id] = confirmed
    return confirmed


def test_focus_field_is_sent_to_the_authoritative_analysis_prompt(monkeypatch):
    store = MemoryExtractionStore()
    record = _confirmed_record(store)
    monkeypatch.setattr(chat_router, "extraction_store", store)
    monkeypatch.setattr(chat_router, "conversation_store", MemoryConversationStore())
    monkeypatch.setattr(chat_router, "_session_id", lambda request: ("focus-session", False))
    monkeypatch.setattr("config.settings.KNOWLEDGE_MODE", "synthetic")
    captured = {}

    async def fake_chat(history, prompt, rule_grounding):
        captured["prompt"] = prompt
        return "Hb 10.8 g/dL is below the supplied range of 12-16 g/dL. This is educational information, not a diagnosis."

    monkeypatch.setattr(chat_router.llm_client, "chat", fake_chat)
    response = TestClient(app).post(
        "/api/v1/chat",
        json={
            "message": "Please explain this Hb result and why it is below the supplied range.",
            "extraction_id": record.extraction_id,
            "focus_field_id": "hb",
        },
    )
    assert response.status_code == 200
    assert "Hb" in captured["prompt"]
    assert "10.8" in captured["prompt"]
    assert "MCV" not in captured["prompt"]
    # A random extraction UUID can contain "72"; inspect the clinical fields.
    assert '"raw_value": "72"' not in captured["prompt"]
    assert '"numeric_value": "72"' not in captured["prompt"]


def test_unknown_focus_field_and_unconfirmed_extraction_fail_closed(monkeypatch):
    store = MemoryExtractionStore()
    confirmed = _confirmed_record(store)
    import asyncio
    review = asyncio.run(store.create("focus-session", "synthetic report", confirmed.fields, []))
    monkeypatch.setattr(chat_router, "extraction_store", store)
    monkeypatch.setattr(chat_router, "conversation_store", MemoryConversationStore())
    monkeypatch.setattr(chat_router, "_session_id", lambda request: ("focus-session", False))
    monkeypatch.setattr(chat_router.llm_client, "chat", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("provider must not run")))
    client = TestClient(app)

    unknown = client.post("/api/v1/chat", json={"message": "Explain this", "extraction_id": confirmed.extraction_id, "focus_field_id": "missing"})
    assert unknown.status_code == 422
    assert unknown.json()["code"] == "focus_field_not_found"

    unconfirmed = client.post("/api/v1/chat", json={"message": "Explain this", "extraction_id": review.extraction_id, "focus_field_id": "hb"})
    assert unconfirmed.status_code == 409
    assert unconfirmed.json()["code"] == "extraction_confirmation_required"


def test_stream_focus_validation_returns_sanitized_error_without_provider(monkeypatch):
    store = MemoryExtractionStore()
    confirmed = _confirmed_record(store)
    monkeypatch.setattr(chat_router, "extraction_store", store)
    monkeypatch.setattr(chat_router, "conversation_store", MemoryConversationStore())
    monkeypatch.setattr(chat_router, "_session_id", lambda request: ("focus-session", False))
    called = False

    async def unexpected_call(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("invalid focus must not call the provider")

    monkeypatch.setattr(chat_router.llm_client, "chat", unexpected_call)
    response = TestClient(app).post(
        "/api/v1/chat/stream",
        json={"message": "Explain this", "extraction_id": confirmed.extraction_id, "focus_field_id": "missing"},
    )
    events = [
        json.loads(line.removeprefix("data: "))
        for line in response.text.splitlines()
        if line.startswith("data: ")
    ]
    assert response.status_code == 200
    assert events[0]["code"] == "focus_field_not_found"
    assert events[0]["message"] == "The selected report field is not available in this extraction."
    assert called is False
