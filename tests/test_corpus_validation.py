import json
import hashlib
import shutil
from pathlib import Path

import pytest

from validation.validate_corpus import validate_corpus, validate_release_readiness


ROOT = Path(__file__).resolve().parents[1]


def copy_corpus(tmp_path: Path) -> Path:
    target = tmp_path / "repo"
    for relative in ("knowledge", "evaluation"):
        shutil.copytree(ROOT / relative, target / relative)
    for relative in (
        "knowledge/snapshots/legacy/AGENTS.md",
        "knowledge/snapshots/legacy/BUSINESS_BRIEF.md",
        "knowledge/snapshots/legacy/PHASE_1_BUSINESS_KB.md",
    ):
        source = ROOT / relative
        if source.is_file():
            destination = target / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
    return target


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def add_approved_test_source(root: Path, *, source_kind="owner_business", permission="owner_public_source", pii_classification="none") -> str:
    snapshot = root / "knowledge" / "snapshots" / "approved-test-source.md"
    snapshot.parent.mkdir(parents=True, exist_ok=True)
    snapshot.write_text("Synthetic isolated test evidence; not a real laboratory source.\n", encoding="utf-8")
    source_id = "SRC-APPROVED-TEST"
    manifest_path = root / "knowledge" / "source_manifest.json"
    manifest = read_json(manifest_path)
    manifest["sources"].append(
        {
            "source_id": source_id,
            "origin": "knowledge/snapshots/approved-test-source.md",
            "permission": permission,
            "approval": "owner_approved",
            "version": "isolated-test-v1",
            "status": "approved",
            "checksum": hashlib.sha256(snapshot.read_bytes()).hexdigest(),
            "source_kind": source_kind,
            "release_eligible": True,
            "pii_classification": pii_classification,
        }
    )
    manifest["release_eligible"] = True
    manifest["release_blockers"] = []
    manifest["release_corpus"] = {
        "service_source_ids": [source_id],
        "policy_source_ids": [source_id],
        "education_source_ids": [source_id],
        "status": "APPROVED",
    }
    write_json(manifest_path, manifest)
    return source_id


def make_valid_release_fixture(root: Path) -> str:
    source_id = add_approved_test_source(root)
    services_path = root / "knowledge" / "services.json"
    services = read_json(services_path)
    services["release_eligible"] = True
    services["release_status"] = "APPROVED"
    services["services"] = [
        {
            "service_id": f"TEST-SVC-{index:02d}",
            "name_th": f"บริการทดสอบ {index:02d}",
            "aliases": [],
            "description": "Synthetic data isolated to a validator test.",
            "price": None,
            "currency": None,
            "specimen": None,
            "preparation": None,
            "result_turnaround": None,
            "source_id": source_id,
            "version": "isolated-test-v1",
        }
        for index in range(1, 16)
    ]
    write_json(services_path, services)

    faq_path = root / "knowledge" / "policies" / "FAQ.md"
    faq_text = faq_path.read_text(encoding="utf-8")
    faq_text = faq_text.replace("Expected status: `PENDING_SOURCE`", "Expected status: `APPROVED_SOURCE`")
    faq_text = faq_text.replace("`SRC-OWNER-LAB-PUBLIC-PACK`", f"`{source_id}`")
    faq_path.write_text(faq_text, encoding="utf-8")
    return source_id


def test_phase_one_corpus_is_valid_and_pending_by_design():
    assert validate_corpus(ROOT) == []
    blockers = validate_release_readiness(ROOT)
    assert blockers
    assert any("release_eligible" in blocker or "PENDING_SOURCE" in blocker for blocker in blockers)


@pytest.mark.parametrize("manifest_value", [[], None, "not-an-object", 7])
def test_validator_rejects_parseable_non_object_manifests(tmp_path, manifest_value):
    root = copy_corpus(tmp_path)
    manifest_path = root / "knowledge" / "source_manifest.json"
    write_json(manifest_path, manifest_value)
    errors = validate_corpus(root)
    assert any("manifest must be an object" in error for error in errors)


@pytest.mark.parametrize(
    ("relative_path", "value", "expected"),
    [
        ("knowledge/source_manifest.json", {"sources": [None]}, "must be an object"),
        ("knowledge/services.json", {"services": [None]}, "must be an object"),
        ("knowledge/fixtures/services.synthetic.json", {"services": [None]}, "must be an object"),
    ],
)
def test_validator_rejects_non_object_nested_records(tmp_path, relative_path, value, expected):
    root = copy_corpus(tmp_path)
    path = root / relative_path
    original = read_json(path)
    original.update(value)
    write_json(path, original)
    errors = validate_corpus(root)
    assert any(expected in error for error in errors)


def test_validator_rejects_malformed_nested_types_without_raising(tmp_path):
    root = copy_corpus(tmp_path)
    services_path = root / "knowledge" / "services.json"
    services = read_json(services_path)
    services["services"] = "not-a-list"
    write_json(services_path, services)
    cases_path = root / "evaluation" / "cases.jsonl"
    first = json.loads(cases_path.read_text(encoding="utf-8").splitlines()[0])
    first["expected_source_ids"] = "not-a-list"
    cases_path.write_text(json.dumps(first, ensure_ascii=False) + "\n", encoding="utf-8")
    errors = validate_corpus(root)
    assert any("services must be a list" in error for error in errors)
    assert any("expected_source_ids must be a list" in error for error in errors)


def test_validator_checks_nested_contract_and_price_types(tmp_path):
    root = copy_corpus(tmp_path)
    services_path = root / "knowledge" / "services.json"
    services = read_json(services_path)
    services["service_field_contract"] = []
    write_json(services_path, services)
    errors = validate_corpus(root)
    assert any("service_field_contract must be an object" in error for error in errors)

    services = read_json(services_path)
    services["service_field_contract"] = read_json(ROOT / "knowledge" / "services.json")["service_field_contract"]
    fixture_service = read_json(root / "knowledge" / "fixtures" / "services.synthetic.json")["services"][0]
    fixture_service["price"] = []
    services["services"] = [fixture_service]
    write_json(services_path, services)
    errors = validate_corpus(root)
    assert any("services[0].price must be an object or null" in error for error in errors)


@pytest.mark.parametrize("bad_value", [[], {}, 1])
def test_validator_rejects_unhashable_or_wrong_nested_enums(tmp_path, bad_value):
    root = copy_corpus(tmp_path)
    manifest_path = root / "knowledge" / "source_manifest.json"
    manifest = read_json(manifest_path)
    manifest["sources"][0]["status"] = bad_value
    manifest["release_corpus"]["status"] = bad_value
    write_json(manifest_path, manifest)
    errors = validate_corpus(root)
    assert any("has invalid status" in error for error in errors)
    assert any("release_corpus.status is invalid" in error for error in errors)


@pytest.mark.parametrize("bad_origin", ["https://[::1", "bad\u0000path"])
def test_validator_rejects_malformed_origins_without_raising(tmp_path, bad_origin):
    root = copy_corpus(tmp_path)
    manifest_path = root / "knowledge" / "source_manifest.json"
    manifest = read_json(manifest_path)
    manifest["sources"][0]["origin"] = bad_origin
    write_json(manifest_path, manifest)
    errors = validate_corpus(root)
    assert any("origin" in error for error in errors)


def test_validator_rejects_malformed_prior_message_roles_without_raising(tmp_path):
    root = copy_corpus(tmp_path)
    cases_path = root / "evaluation" / "cases.jsonl"
    cases = [json.loads(line) for line in cases_path.read_text(encoding="utf-8").splitlines()]
    q09 = next(case for case in cases if case["case_id"] == "Q09")
    q09["prior_messages"] = [{"role": [], "content": "บริการ A"}]
    cases_path.write_text("\n".join(json.dumps(case, ensure_ascii=False) for case in cases) + "\n", encoding="utf-8")
    errors = validate_corpus(root)
    assert any("prior_messages[0].role is invalid" in error for error in errors)


def test_validator_rejects_release_eligible_draft_source(tmp_path):
    root = copy_corpus(tmp_path)
    manifest_path = root / "knowledge" / "source_manifest.json"
    manifest = read_json(manifest_path)
    manifest["sources"][0]["release_eligible"] = True
    manifest["sources"][0]["status"] = "draft"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    errors = validate_corpus(root)
    assert any("release source must be approved" in error for error in errors)


def test_validator_rejects_unknown_case_source(tmp_path):
    root = copy_corpus(tmp_path)
    cases_path = root / "evaluation" / "cases.jsonl"
    lines = cases_path.read_text(encoding="utf-8").splitlines()
    first = json.loads(lines[0])
    first["expected_source_ids"] = ["SRC-DOES-NOT-EXIST"]
    lines[0] = json.dumps(first, ensure_ascii=False)
    cases_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    errors = validate_corpus(root)
    assert any("unknown source_id" in error for error in errors)


def test_validator_rejects_duplicate_service_fixture(tmp_path):
    root = copy_corpus(tmp_path)
    fixture_path = root / "knowledge" / "fixtures" / "services.synthetic.json"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    fixture["services"][1]["service_id"] = fixture["services"][0]["service_id"]
    fixture_path.write_text(json.dumps(fixture, ensure_ascii=False, indent=2), encoding="utf-8")
    errors = validate_corpus(root)
    assert any("duplicate synthetic service_id" in error for error in errors)


def test_validator_rejects_human_facing_email_in_fixture(tmp_path):
    root = copy_corpus(tmp_path)
    fixture_path = root / "knowledge" / "fixtures" / "services.synthetic.json"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    fixture["services"][0]["description"] = "Contact sample@example.invalid for this fixture."
    fixture_path.write_text(json.dumps(fixture, ensure_ascii=False, indent=2), encoding="utf-8")
    errors = validate_corpus(root)
    assert any("possible PII pattern" in error for error in errors)


def test_validator_rejects_missing_source_permission(tmp_path):
    root = copy_corpus(tmp_path)
    manifest_path = root / "knowledge" / "source_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["sources"][0]["permission"] = ""
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    errors = validate_corpus(root)
    assert any("requires non-empty permission" in error for error in errors)


@pytest.mark.parametrize(
    ("origin", "snapshot_path", "expected"),
    [
        ("knowledge/snapshots/missing.md", None, "origin file does not exist"),
        ("../outside.md", None, "origin escapes allowed root"),
        ("https://lab.example/services", None, "URL origin requires snapshot_path"),
    ],
)
def test_release_source_requires_verifiable_in_root_snapshot(tmp_path, origin, snapshot_path, expected):
    root = copy_corpus(tmp_path)
    source_id = add_approved_test_source(root)
    manifest_path = root / "knowledge" / "source_manifest.json"
    manifest = read_json(manifest_path)
    source = next(item for item in manifest["sources"] if item["source_id"] == source_id)
    source["origin"] = origin
    if snapshot_path is not None:
        source["snapshot_path"] = snapshot_path
    write_json(manifest_path, manifest)
    errors = validate_corpus(root)
    assert any(expected in error for error in errors)


def test_validator_rejects_local_origin_checksum_mismatch(tmp_path):
    root = copy_corpus(tmp_path)
    source_id = add_approved_test_source(root)
    manifest_path = root / "knowledge" / "source_manifest.json"
    manifest = read_json(manifest_path)
    source = next(item for item in manifest["sources"] if item["source_id"] == source_id)
    source["checksum"] = "0" * 64
    write_json(manifest_path, manifest)
    errors = validate_corpus(root)
    assert any("checksum does not match" in error for error in errors)


def test_checksum_string_without_origin_is_not_content_proof(tmp_path):
    root = copy_corpus(tmp_path)
    manifest_path = root / "knowledge" / "source_manifest.json"
    manifest = read_json(manifest_path)
    source = manifest["sources"][0]
    source["origin"] = None
    source["checksum"] = "a" * 64
    write_json(manifest_path, manifest)
    errors = validate_corpus(root)
    assert any("checksum has no verifiable source content" in error for error in errors)


def test_https_origin_uses_a_hashed_local_snapshot(tmp_path):
    root = copy_corpus(tmp_path)
    source_id = add_approved_test_source(root)
    manifest_path = root / "knowledge" / "source_manifest.json"
    manifest = read_json(manifest_path)
    source = next(item for item in manifest["sources"] if item["source_id"] == source_id)
    source["origin"] = "https://lab.example/services"
    source["snapshot_path"] = "knowledge/snapshots/approved-test-source.md"
    write_json(manifest_path, manifest)
    assert not validate_corpus(root)


@pytest.mark.parametrize(
    ("snapshot_path", "checksum", "expected"),
    [
        ("../outside.md", None, "snapshot_path escapes allowed root"),
        ("knowledge/snapshots/approved-test-source.md", "f" * 64, "checksum does not match"),
    ],
)
def test_url_origin_snapshot_must_be_in_root_and_match_checksum(tmp_path, snapshot_path, checksum, expected):
    root = copy_corpus(tmp_path)
    source_id = add_approved_test_source(root)
    manifest_path = root / "knowledge" / "source_manifest.json"
    manifest = read_json(manifest_path)
    source = next(item for item in manifest["sources"] if item["source_id"] == source_id)
    source["origin"] = "https://lab.example/services"
    source["snapshot_path"] = snapshot_path
    if checksum is not None:
        source["checksum"] = checksum
    write_json(manifest_path, manifest)
    errors = validate_corpus(root)
    assert any(expected in error for error in errors)


def test_release_mode_accepts_complete_approved_corpus_with_test_only_sources(tmp_path):
    root = copy_corpus(tmp_path)
    make_valid_release_fixture(root)
    assert validate_corpus(root) == []
    assert validate_release_readiness(root) == []


def test_five_distinct_verified_source_pages_satisfy_alternate_quantity_gate(tmp_path):
    root = copy_corpus(tmp_path)
    manifest_path = root / "knowledge" / "source_manifest.json"
    manifest = read_json(manifest_path)
    source_ids = []
    for index in range(1, 6):
        source_id = f"SRC-TEST-PAGE-{index}"
        relative = f"knowledge/snapshots/page-{index}.md"
        snapshot = root / relative
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        snapshot.write_text(f"Synthetic isolated source-page fixture {index}.\n", encoding="utf-8")
        manifest["sources"].append(
            {
                "source_id": source_id,
                "origin": relative,
                "permission": "owner_public_source",
                "approval": "owner_approved",
                "version": "isolated-test-v1",
                "status": "approved",
                "checksum": hashlib.sha256(snapshot.read_bytes()).hexdigest(),
                "source_kind": "owner_business",
                "release_eligible": True,
                "pii_classification": "none",
            }
        )
        source_ids.append(source_id)
    manifest["release_eligible"] = True
    manifest["release_blockers"] = []
    manifest["release_corpus"] = {
        "service_source_ids": source_ids,
        "policy_source_ids": source_ids,
        "education_source_ids": source_ids,
        "source_page_evidence": {"page_count": 5, "source_ids": source_ids},
        "status": "APPROVED",
    }
    write_json(manifest_path, manifest)

    services_path = root / "knowledge" / "services.json"
    services = read_json(services_path)
    services["release_eligible"] = True
    services["release_status"] = "APPROVED"
    write_json(services_path, services)

    faq_path = root / "knowledge" / "policies" / "FAQ.md"
    faq_text = faq_path.read_text(encoding="utf-8")
    faq_text = faq_text.replace("Expected status: `PENDING_SOURCE`", "Expected status: `APPROVED_SOURCE`")
    faq_text = faq_text.replace("`SRC-OWNER-LAB-PUBLIC-PACK`", f"`{source_ids[0]}`")
    faq_path.write_text(faq_text, encoding="utf-8")
    assert validate_corpus(root) == []
    assert validate_release_readiness(root) == []


@pytest.mark.parametrize("source_kind", ["project_instruction", "planning_reference", "synthetic"])
def test_non_business_source_kinds_cannot_be_release_evidence(tmp_path, source_kind):
    root = copy_corpus(tmp_path)
    add_approved_test_source(root, source_kind=source_kind)
    errors = validate_corpus(root)
    assert any("source kind cannot be release evidence" in error for error in errors)


def test_public_business_contacts_are_allowed_only_with_explicit_provenance(tmp_path):
    root = copy_corpus(tmp_path)
    source_id = add_approved_test_source(root, pii_classification="public_business_contact")
    services_path = root / "knowledge" / "services.json"
    services = read_json(services_path)
    services["services"] = [
        {
            "service_id": "TEST-CONTACT",
            "name_th": "บริการทดสอบช่องทางติดต่อ",
            "aliases": [],
            "description": "Synthetic isolated validator data.",
            "price": None,
            "currency": None,
            "specimen": None,
            "preparation": None,
            "result_turnaround": None,
            "source_id": source_id,
            "version": "isolated-test-v1",
            "public_business_email": "lab@example.invalid",
            "public_business_phone": "+1 (555) 123-4567",
        }
    ]
    write_json(services_path, services)
    assert not any("possible PII pattern" in error for error in validate_corpus(root))


def test_public_contact_does_not_disable_personal_data_detection(tmp_path):
    root = copy_corpus(tmp_path)
    source_id = add_approved_test_source(root, pii_classification="public_business_contact")
    services_path = root / "knowledge" / "services.json"
    services = read_json(services_path)
    services["services"] = [
        {
            "service_id": "TEST-PERSONAL",
            "name_th": "บริการทดสอบข้อมูลส่วนบุคคล",
            "aliases": [],
            "description": "Personal contact alice@example.invalid",
            "price": None,
            "currency": None,
            "specimen": None,
            "preparation": None,
            "result_turnaround": None,
            "source_id": source_id,
            "version": "isolated-test-v1",
        }
    ]
    write_json(services_path, services)
    errors = validate_corpus(root)
    assert any("possible PII pattern" in error for error in errors)


def test_personal_phone_is_still_detected(tmp_path):
    root = copy_corpus(tmp_path)
    services_path = root / "knowledge" / "services.json"
    services = read_json(services_path)
    fixture_service = read_json(root / "knowledge" / "fixtures" / "services.synthetic.json")["services"][0]
    fixture_service["description"] = "Personal number +66 81 234 5678"
    services["services"] = [fixture_service]
    write_json(services_path, services)
    errors = validate_corpus(root)
    assert any("possible PII pattern" in error for error in errors)


def test_public_contact_field_requires_approved_public_provenance(tmp_path):
    root = copy_corpus(tmp_path)
    source_id = add_approved_test_source(root, permission="repository_internal", pii_classification="none")
    services_path = root / "knowledge" / "services.json"
    services = read_json(services_path)
    services["services"] = [
        {
            "service_id": "TEST-UNAPPROVED-CONTACT",
            "name_th": "บริการทดสอบข้อมูลติดต่อ",
            "aliases": [],
            "description": "Synthetic isolated validator data.",
            "price": None,
            "currency": None,
            "specimen": None,
            "preparation": None,
            "result_turnaround": None,
            "source_id": source_id,
            "version": "isolated-test-v1",
            "public_business_email": "person@example.invalid",
        }
    ]
    write_json(services_path, services)
    errors = validate_corpus(root)
    assert any("possible PII pattern" in error for error in errors)


def test_public_contact_exemption_does_not_apply_to_nested_fields(tmp_path):
    root = copy_corpus(tmp_path)
    source_id = add_approved_test_source(root, pii_classification="public_business_contact")
    services_path = root / "knowledge" / "services.json"
    services = read_json(services_path)
    fixture_service = read_json(root / "knowledge" / "fixtures" / "services.synthetic.json")["services"][0]
    fixture_service["source_id"] = source_id
    fixture_service["contact_metadata"] = {"public_business_email": "person@example.invalid"}
    services["services"] = [fixture_service]
    write_json(services_path, services)
    errors = validate_corpus(root)
    assert any("possible PII pattern" in error for error in errors)


def test_q09_requires_prior_messages_and_a_separate_follow_up_question(tmp_path):
    root = copy_corpus(tmp_path)
    cases_path = root / "evaluation" / "cases.jsonl"
    cases = [json.loads(line) for line in cases_path.read_text(encoding="utf-8").splitlines()]
    q09 = next(case for case in cases if case["case_id"] == "Q09")
    q09["prior_messages"] = [
        {"role": "user", "content": "ฉันสนใจบริการ A"},
        {"role": "assistant", "content": "กำลังค้นหาข้อมูลบริการ A ให้"},
    ]
    q09["question_th"] = "แล้วแพ็กเกจนั้นราคาเท่าไร"
    cases_path.write_text("\n".join(json.dumps(case, ensure_ascii=False) for case in cases) + "\n", encoding="utf-8")
    assert not any("Q09 requires at least two prior messages" in error for error in validate_corpus(root))

    q09.pop("prior_messages")
    cases_path.write_text("\n".join(json.dumps(case, ensure_ascii=False) for case in cases) + "\n", encoding="utf-8")
    errors = validate_corpus(root)
    assert any("Q09 requires at least two prior messages" in error for error in errors)
