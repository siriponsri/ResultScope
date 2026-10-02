"""Validate the source-safe, synthetic-first Phase 1 corpus.

The validator is intentionally independent of the runtime application. It checks
release metadata, references, duplicate records, and evaluation case shape before
any future retrieval/indexing work is allowed to consume the corpus.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


ALLOWED_SOURCE_STATUS = {"draft", "approved", "retired"}
REQUIRED_SOURCE_FIELDS = {
    "source_id",
    "origin",
    "permission",
    "approval",
    "version",
    "status",
    "checksum",
    "source_kind",
    "release_eligible",
    "pii_classification",
}
EXPECTED_FAQ_IDS = {f"FAQ-{index:02d}" for index in range(1, 11)}
PII_PATTERNS = (
    re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    re.compile(r"\+?\d[\d ()-]{7,}\d"),
)
MACHINE_METADATA_FIELDS = {"checksum", "source_id", "service_id", "case_id", "version"}


def _load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing JSON file: {path.relative_to(path.parents[1])}")
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON {path}: {exc}")
    return None


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def _relative_origin(root: Path, origin: Any) -> Path | None:
    if not isinstance(origin, str) or not origin:
        return None
    candidate = (root / origin).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    return candidate


def _scan_pii(value: Any, location: str, errors: list[str]) -> None:
    def human_fields(item: Any) -> Any:
        if isinstance(item, dict):
            return {
                key: human_fields(child)
                for key, child in item.items()
                if key not in MACHINE_METADATA_FIELDS
            }
        if isinstance(item, list):
            return [human_fields(child) for child in item]
        return item

    sanitized = human_fields(value)
    text = json.dumps(sanitized, ensure_ascii=False) if not isinstance(sanitized, str) else sanitized
    for pattern in PII_PATTERNS:
        if pattern.search(text):
            errors.append(f"possible PII pattern in {location}")
            return


def validate_corpus(root: Path | None = None) -> list[str]:
    root = (root or Path(__file__).resolve().parents[1]).resolve()
    errors: list[str] = []
    manifest_path = root / "knowledge" / "source_manifest.json"
    services_path = root / "knowledge" / "services.json"
    fixture_path = root / "knowledge" / "fixtures" / "services.synthetic.json"
    faq_path = root / "knowledge" / "policies" / "FAQ.md"
    cases_path = root / "evaluation" / "cases.jsonl"

    manifest = _load_json(manifest_path, errors)
    services = _load_json(services_path, errors)
    fixtures = _load_json(fixture_path, errors)
    if not isinstance(manifest, dict):
        return errors

    sources = manifest.get("sources")
    if not isinstance(sources, list) or not sources:
        errors.append("manifest.sources must be a non-empty list")
        sources = []

    source_by_id: dict[str, dict[str, Any]] = {}
    for index, source in enumerate(sources):
        location = f"manifest.sources[{index}]"
        if not isinstance(source, dict):
            errors.append(f"{location} must be an object")
            continue
        missing = REQUIRED_SOURCE_FIELDS - source.keys()
        if missing:
            errors.append(f"{location} missing fields: {sorted(missing)}")
        source_id = source.get("source_id")
        if not isinstance(source_id, str) or not source_id:
            errors.append(f"{location}.source_id must be a non-empty string")
            continue
        if source_id in source_by_id:
            errors.append(f"duplicate source_id: {source_id}")
        source_by_id[source_id] = source
        if source.get("status") not in ALLOWED_SOURCE_STATUS:
            errors.append(f"{source_id} has invalid status")
        for field in ("permission", "approval", "version", "source_kind", "pii_classification"):
            if not isinstance(source.get(field), str) or not source.get(field).strip():
                errors.append(f"{source_id} requires non-empty {field}")
        if not isinstance(source.get("release_eligible"), bool):
            errors.append(f"{source_id}.release_eligible must be boolean")
        checksum = source.get("checksum")
        origin_path = _relative_origin(root, source.get("origin"))
        if checksum is None:
            if not source.get("checksum_pending_reason"):
                errors.append(f"{source_id} needs checksum_pending_reason when checksum is null")
            if origin_path and origin_path.is_file():
                errors.append(f"{source_id} needs checksum for its local origin")
        elif not isinstance(checksum, str) or not re.fullmatch(r"[0-9a-f]{64}", checksum):
            errors.append(f"{source_id} checksum must be lowercase SHA-256")
        elif origin_path and origin_path.is_file() and _sha256(origin_path) != checksum:
            errors.append(f"{source_id} checksum does not match {origin_path.relative_to(root)}")
        if source.get("release_eligible"):
            if source.get("status") != "approved":
                errors.append(f"{source_id} release source must be approved")
            if source.get("approval") != "owner_approved":
                errors.append(f"{source_id} release source needs owner_approved approval")
            if not checksum:
                errors.append(f"{source_id} release source needs checksum")
            if source.get("source_kind") == "synthetic":
                errors.append(f"synthetic source cannot be release-eligible: {source_id}")
        _scan_pii(source, source_id, errors)

    if not isinstance(services, dict):
        errors.append("knowledge/services.json must be an object")
        services = {}
    if services.get("release_eligible"):
        errors.append("knowledge/services.json must remain release_eligible=false until G1-data")
    service_records = services.get("services", [])
    if not isinstance(service_records, list):
        errors.append("knowledge/services.json.services must be a list")
        service_records = []
    service_ids: set[str] = set()
    service_names: set[str] = set()
    for index, service in enumerate(service_records):
        location = f"services[{index}]"
        if not isinstance(service, dict):
            errors.append(f"{location} must be an object")
            continue
        service_id = service.get("service_id")
        name = service.get("name_th")
        source_id = service.get("source_id")
        if not isinstance(service_id, str) or not service_id:
            errors.append(f"{location}.service_id must be non-empty")
        elif service_id in service_ids:
            errors.append(f"duplicate service_id: {service_id}")
        else:
            service_ids.add(service_id)
        normalized_name = re.sub(r"\s+", " ", str(name or "").strip().casefold())
        if not normalized_name:
            errors.append(f"{location}.name_th must be non-empty")
        elif normalized_name in service_names:
            errors.append(f"duplicate service name: {name}")
        else:
            service_names.add(normalized_name)
        if source_id not in source_by_id:
            errors.append(f"{location} references unknown source_id: {source_id}")
        elif not source_by_id[source_id].get("release_eligible"):
            errors.append(f"release service references non-release source: {source_id}")
        price = service.get("price")
        if price is not None:
            if not isinstance(price, dict) or not isinstance(price.get("amount"), (int, float)) or isinstance(price.get("amount"), bool):
                errors.append(f"{location}.price must contain a numeric amount or be null")
            elif price["amount"] < 0:
                errors.append(f"{location}.price.amount cannot be negative")
        _scan_pii(service, location, errors)

    if not isinstance(fixtures, dict):
        errors.append("synthetic fixture file must be an object")
        fixtures = {}
    fixture_source_id = fixtures.get("source_id")
    if fixtures.get("release_eligible") is not False or fixtures.get("fixture_status") != "SYNTHETIC_DEVELOPMENT_ONLY":
        errors.append("synthetic services fixture must be explicitly non-release")
    if fixture_source_id not in source_by_id:
        errors.append("synthetic services fixture references unknown source_id")
    elif source_by_id[fixture_source_id].get("source_kind") != "synthetic" or source_by_id[fixture_source_id].get("release_eligible"):
        errors.append("synthetic services fixture source must be non-release synthetic")
    fixture_records = fixtures.get("services", [])
    if not isinstance(fixture_records, list) or not fixture_records:
        errors.append("synthetic services fixture must contain at least one record")
    fixture_ids: set[str] = set()
    fixture_names: set[str] = set()
    for index, service in enumerate(fixture_records if isinstance(fixture_records, list) else []):
        location = f"synthetic_services[{index}]"
        if not isinstance(service, dict):
            errors.append(f"{location} must be an object")
            continue
        service_id = service.get("service_id")
        if service_id in fixture_ids:
            errors.append(f"duplicate synthetic service_id: {service_id}")
        fixture_ids.add(service_id)
        normalized_name = re.sub(r"\s+", " ", str(service.get("name_th") or "").strip().casefold())
        if normalized_name in fixture_names:
            errors.append(f"duplicate synthetic service name: {service.get('name_th')}")
        fixture_names.add(normalized_name)
        if service.get("source_id") != fixture_source_id:
            errors.append(f"{location} must use fixture source_id {fixture_source_id}")
    _scan_pii(fixtures, "synthetic services fixture", errors)

    try:
        faq_text = faq_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append(f"missing FAQ file: {faq_path}")
        faq_text = ""
    faq_ids = set(re.findall(r"^## (FAQ-\d{2})\s", faq_text, flags=re.MULTILINE))
    if faq_ids != EXPECTED_FAQ_IDS:
        errors.append(f"FAQ IDs must be exactly {sorted(EXPECTED_FAQ_IDS)}")
    if faq_text.count("Expected status: `PENDING_SOURCE`") != 10:
        errors.append("all ten FAQ entries must declare PENDING_SOURCE while sources are missing")

    case_ids: set[str] = set()
    mandatory = holdout = 0
    try:
        case_lines = [line for line in cases_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    except FileNotFoundError:
        errors.append(f"missing evaluation cases: {cases_path}")
        case_lines = []
    for line_number, line in enumerate(case_lines, start=1):
        try:
            case = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"invalid evaluation JSONL line {line_number}: {exc}")
            continue
        case_id = case.get("case_id")
        if not isinstance(case_id, str) or not case_id:
            errors.append(f"evaluation line {line_number} missing case_id")
        elif case_id in case_ids:
            errors.append(f"duplicate evaluation case_id: {case_id}")
        else:
            case_ids.add(case_id)
        if case.get("set") == "mandatory":
            mandatory += 1
        if case.get("set") == "holdout":
            holdout += 1
        for source_id in case.get("expected_source_ids", []):
            if source_id not in source_by_id:
                errors.append(f"evaluation {case_id} references unknown source_id: {source_id}")
        if case.get("expected_status") == "PENDING_SOURCE" and case.get("expected_source_ids") != []:
            errors.append(f"pending evaluation {case_id} must have no expected source IDs")
        _scan_pii(case, f"evaluation {case_id}", errors)
    if mandatory != 10:
        errors.append(f"evaluation must contain 10 mandatory cases, found {mandatory}")
    if holdout < 5:
        errors.append(f"evaluation must contain at least 5 holdout cases, found {holdout}")

    return errors


def main() -> int:
    errors = validate_corpus()
    if errors:
        print("CORPUS VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print("CORPUS VALIDATION PASSED")
    print("- release corpus: empty/pending by design")
    print("- synthetic fixtures: isolated and non-release")
    print("- evaluation cases: 10 mandatory + 5 holdout minimum")
    return 0


if __name__ == "__main__":
    sys.exit(main())
