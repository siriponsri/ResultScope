import json
import shutil
from pathlib import Path

from validation.validate_corpus import validate_corpus


ROOT = Path(__file__).resolve().parents[1]


def copy_corpus(tmp_path: Path) -> Path:
    target = tmp_path / "repo"
    for relative in ("knowledge", "evaluation"):
        shutil.copytree(ROOT / relative, target / relative)
    return target


def test_phase_one_corpus_is_valid_and_pending_by_design():
    assert validate_corpus(ROOT) == []


def test_validator_rejects_release_eligible_draft_source(tmp_path):
    root = copy_corpus(tmp_path)
    manifest_path = root / "knowledge" / "source_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
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
