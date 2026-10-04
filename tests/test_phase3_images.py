from __future__ import annotations

import io
import time
from dataclasses import replace
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from main import app
from routers import chat as chat_router
from routers import images as images_router
from services import answer_service
from services.extraction_store import MemoryExtractionStore
from services.image_extraction import normalize_fields
from services.vision_client import VisionError, VisionExtractionPayload
from services.store import MemoryConversationStore


ROOT = Path(__file__).resolve().parents[1]
DEMO_IMAGES = ROOT / "examples" / "coursework_demo_v1" / "images"


def _png_bytes(width: int = 120, height: int = 80) -> bytes:
    image = Image.new("RGB", (width, height), color="white")
    output = io.BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


def _install_stores(monkeypatch):
    extraction_store = MemoryExtractionStore()
    monkeypatch.setattr(images_router, "extraction_store", extraction_store)
    monkeypatch.setattr(chat_router, "extraction_store", extraction_store)
    monkeypatch.setattr(chat_router, "conversation_store", MemoryConversationStore())
    return extraction_store


def _payload(*fields, document_type="synthetic_lab_report"):
    return VisionExtractionPayload.model_validate(
        {"document_type": document_type, "fields": list(fields), "warnings": []}
    )


def _upload(client: TestClient, data: bytes, filename: str = "report.png", content_type: str = "image/png"):
    return client.post(
        "/api/v1/images/extract",
        files={"file": (filename, data, content_type)},
    )


@pytest.mark.parametrize(
    "filename",
    ["I01_services.png", "I02_report.png", "I03_unreadable.png", "I04_missing_range.png", "I05_injection.png"],
)
def test_coursework_images_are_accepted_by_the_upload_boundary(monkeypatch, filename):
    _install_stores(monkeypatch)

    async def fake_extract(image_bytes, media_type):
        assert image_bytes.startswith((b"\x89PNG", b"\xff\xd8\xff"))
        assert media_type in {"image/png", "image/jpeg"}
        return _payload()

    monkeypatch.setattr(images_router.vision_client, "extract_image", fake_extract)
    response = _upload(TestClient(app), (DEMO_IMAGES / filename).read_bytes(), filename, "text/plain")

    assert response.status_code == 200
    assert response.json()["status"] == "review_required"
    assert "fields" in response.json()
    assert "raw_image" not in response.json()


def test_invalid_content_and_limits_are_rejected_before_provider(monkeypatch):
    _install_stores(monkeypatch)
    called = False

    async def unexpected_extract(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("invalid upload must not call Vision")

    monkeypatch.setattr(images_router.vision_client, "extract_image", unexpected_extract)
    invalid = _upload(TestClient(app), b"not an image", "../../prompt-injection.png", "image/png")
    assert invalid.status_code == 415
    assert invalid.json()["code"] == "unsupported_image"
    assert called is False

    monkeypatch.setattr("config.settings.IMAGE_MAX_BYTES", 20)
    too_large = _upload(TestClient(app), _png_bytes(), "large.png")
    assert too_large.status_code == 413
    assert too_large.json()["code"] == "image_too_large"

    monkeypatch.setattr("config.settings.IMAGE_MAX_BYTES", 3 * 1024 * 1024)
    monkeypatch.setattr("config.settings.IMAGE_MAX_PIXELS", 1000)
    huge = _upload(TestClient(app), _png_bytes(100, 100), "huge.png")
    assert huge.status_code == 413
    assert huge.json()["code"] == "image_dimensions_too_large"


def test_missing_and_invalid_vision_provider_are_explicit(monkeypatch):
    _install_stores(monkeypatch)
    monkeypatch.setattr("config.settings.VISION_ENABLED", False)
    unavailable = _upload(TestClient(app), _png_bytes())
    assert unavailable.status_code == 503
    assert unavailable.json()["code"] == "vision_unavailable"

    async def invalid_provider(*args, **kwargs):
        raise VisionError("vision_invalid_response", "Vision provider returned invalid extraction data.")

    monkeypatch.setattr(images_router.vision_client, "extract_image", invalid_provider)
    invalid = _upload(TestClient(app), _png_bytes())
    assert invalid.status_code == 502
    assert invalid.json()["code"] == "vision_invalid_response"


def test_normalization_preserves_comparators_and_unknown_ranges():
    fields, warnings = normalize_fields(
        [
            {"marker": "Marker-A", "raw_value": "<5.0", "unit": "demo-unit"},
            {"marker": "Marker-B", "raw_value": "12,5", "unit": "demo-unit", "reference_low": "10", "reference_high": "15"},
            {"marker": "Marker-C", "raw_value": "18.0", "unit": None, "reference_low": None, "reference_high": None},
        ]
    )

    assert fields[0]["raw_value"] == "<5.0"
    assert fields[0]["comparator"] == "<"
    assert fields[0]["flag"] == "unknown"
    assert fields[1]["raw_value"] == "12,5"
    assert fields[1]["numeric_value"] == "12,5"
    assert fields[1]["flag"] == "within"
    assert fields[2]["status"] == "read"
    assert fields[2]["flag"] == "unknown"
    assert warnings


def test_upload_review_correction_confirmation_and_grounded_answer(monkeypatch):
    _install_stores(monkeypatch)
    monkeypatch.setattr("config.settings.KNOWLEDGE_MODE", "synthetic")
    payload = _payload(
        {"marker": "Marker-A", "raw_value": "12.5", "unit": "demo-unit", "reference_low": "10", "reference_high": "15"},
        {"marker": "Marker-B", "raw_value": "18.0", "unit": "demo-unit", "reference_low": "10", "reference_high": "15"},
    )

    async def fake_extract(*args, **kwargs):
        return payload

    async def fake_chat(history, message, rule_grounding):
        assert "Confirmed image extraction" in message
        assert "12,5" in message
        return "Marker-A 12,5 demo-unit is within the supplied range [DEMO-READING]."

    monkeypatch.setattr(images_router.vision_client, "extract_image", fake_extract)
    monkeypatch.setattr(answer_service.llm_client, "chat", fake_chat)
    client = TestClient(app)
    extracted = _upload(client, _png_bytes()).json()
    extraction_id = extracted["extraction_id"]

    before_confirm = client.post(
        "/api/v1/chat",
        json={"message": "Marker-A", "extraction_id": extraction_id},
    )
    assert before_confirm.status_code == 409
    assert before_confirm.json()["code"] == "extraction_confirmation_required"

    corrected = [
        {
            "field_id": field["field_id"],
            "marker": field["marker"],
            "raw_value": field["raw_value"],
            "unit": field["unit"],
            "reference_low": field["reference_low"],
            "reference_high": field["reference_high"],
            "reference_range_raw": field["reference_range_raw"],
        }
        for field in extracted["fields"]
    ]
    corrected[0]["raw_value"] = "12,5"
    confirmed = client.post(
        f"/api/v1/images/{extraction_id}/confirm",
        json={"revision": extracted["revision"], "fields": corrected},
    )
    assert confirmed.status_code == 200
    assert confirmed.json()["status"] == "confirmed"
    assert confirmed.json()["revision"] == 2
    assert confirmed.json()["fields"][0]["provenance"] == "user"

    answer = client.post(
        "/api/v1/chat",
        json={"message": "Marker-A", "extraction_id": extraction_id},
    )
    assert answer.status_code == 200
    assert answer.json()["status"] == "answered"
    assert answer.json()["citations"][0]["source_id"] == "DEMO-READING"

    repeated = client.post(
        f"/api/v1/images/{extraction_id}/confirm",
        json={"revision": 2, "fields": corrected},
    )
    assert repeated.status_code == 409
    assert repeated.json()["code"] == "extraction_already_confirmed"


def test_image_values_cannot_override_canonical_business_prices(monkeypatch):
    store = _install_stores(monkeypatch)
    monkeypatch.setattr("config.settings.KNOWLEDGE_MODE", "synthetic")

    async def fake_extract(*args, **kwargs):
        return _payload({"marker": "CBC", "raw_value": "1", "unit": "THB"}, document_type="service_list")

    async def fake_chat(history, message, rule_grounding):
        return "CBC ราคา 1 THB [DEMO-SERVICES]"

    monkeypatch.setattr(images_router.vision_client, "extract_image", fake_extract)
    monkeypatch.setattr(answer_service.llm_client, "chat", fake_chat)
    client = TestClient(app)
    extracted = _upload(client, _png_bytes()).json()
    fields = extracted["fields"]
    confirmed = client.post(
        f"/api/v1/images/{extracted['extraction_id']}/confirm",
        json={"revision": 1, "fields": fields},
    )
    assert confirmed.status_code == 200
    answer = client.post(
        "/api/v1/chat",
        json={"message": "CBC ราคาเท่าไร", "extraction_id": extracted["extraction_id"]},
    )
    assert answer.status_code == 200
    assert answer.json()["status"] == "abstained"
    assert store is not None


def test_extractions_are_session_bound_and_reset_clears_them(monkeypatch):
    _install_stores(monkeypatch)

    async def fake_extract(*args, **kwargs):
        return _payload({"marker": "Marker-A", "raw_value": "12.5"})

    monkeypatch.setattr(images_router.vision_client, "extract_image", fake_extract)
    first = TestClient(app)
    second = TestClient(app)
    extracted = _upload(first, _png_bytes()).json()
    fields = extracted["fields"]
    foreign = second.post(
        f"/api/v1/images/{extracted['extraction_id']}/confirm",
        json={"revision": 1, "fields": fields},
    )
    assert foreign.status_code == 404

    reset = first.post("/api/v1/chat/reset")
    assert reset.status_code == 200
    stale = first.post(
        f"/api/v1/images/{extracted['extraction_id']}/confirm",
        json={"revision": 1, "fields": fields},
    )
    assert stale.status_code == 404


def test_confirmation_requires_current_revision_and_nonexpired_record(monkeypatch):
    store = _install_stores(monkeypatch)

    async def fake_extract(*args, **kwargs):
        return _payload({"marker": "Marker-A", "raw_value": "12.5"})

    monkeypatch.setattr(images_router.vision_client, "extract_image", fake_extract)
    client = TestClient(app)
    extracted = _upload(client, _png_bytes()).json()
    fields = extracted["fields"]
    stale_revision = client.post(
        f"/api/v1/images/{extracted['extraction_id']}/confirm",
        json={"revision": 2, "fields": fields},
    )
    assert stale_revision.status_code == 409
    assert stale_revision.json()["code"] == "extraction_revision_conflict"

    record = store._data[extracted["extraction_id"]]
    store._data[record.extraction_id] = replace(record, expires_at=time.time() - 1)
    expired = client.post(
        f"/api/v1/images/{extracted['extraction_id']}/confirm",
        json={"revision": 1, "fields": fields},
    )
    assert expired.status_code == 404
    assert expired.json()["code"] == "extraction_not_found"
