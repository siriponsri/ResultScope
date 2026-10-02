"""Validate the Phase 1 development corpus and its release readiness."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


ALLOWED_SOURCE_STATUS = {"draft", "approved", "retired"}
RELEASE_SOURCE_KINDS = {"owner_business", "public_business"}
RELEASE_PERMISSIONS = {"owner_public_source", "public_website"}
FAQ_STATUSES = {"PENDING_SOURCE", "APPROVED_SOURCE"}
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
SERVICE_FIELDS = {
    "service_id",
    "name_th",
    "aliases",
    "description",
    "price",
    "currency",
    "specimen",
    "preparation",
    "result_turnaround",
    "source_id",
    "version",
}
EXPECTED_FAQ_IDS = {f"FAQ-{index:02d}" for index in range(1, 11)}
EMAIL_PATTERN = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PHONE_PATTERN = re.compile(r"\+?\d[\d ()-]{7,}\d")
MACHINE_METADATA_FIELDS = {
    "approval",
    "checksum",
    "case_id",
    "generated_at",
    "origin",
    "permission",
    "retrieved_at",
    "service_id",
    "snapshot_path",
    "source_id",
    "version",
}
PUBLIC_CONTACT_FIELDS = {"public_business_email", "public_business_phone"}
_INVALID = object()


def _display_path(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def _load_json(path: Path, root: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing JSON file: {_display_path(root, path)}")
    except (OSError, UnicodeDecodeError) as exc:
        errors.append(f"cannot read JSON {_display_path(root, path)}: {exc}")
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON {_display_path(root, path)}: {exc}")
    return _INVALID


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _resolve_local_file(root: Path, raw_path: Any, location: str, errors: list[str]) -> Path | None:
    if not isinstance(raw_path, str) or not raw_path.strip():
        errors.append(f"{location} must identify a local snapshot path")
        return None
    candidate_path = Path(raw_path)
    if candidate_path.is_absolute():
        errors.append(f"{location} escapes allowed root: {raw_path}")
        return None
    try:
        allowed_root = root.resolve()
        candidate = (allowed_root / candidate_path).resolve()
    except (OSError, RuntimeError, ValueError) as exc:
        errors.append(f"{location} is not a valid local path: {exc}")
        return None
    try:
        candidate.relative_to(allowed_root)
    except ValueError:
        errors.append(f"{location} escapes allowed root: {raw_path}")
        return None
    try:
        if not candidate.is_file():
            errors.append(f"{location} file does not exist: {raw_path}")
            return None
    except OSError as exc:
        errors.append(f"{location} cannot be inspected: {exc}")
        return None
    return candidate


def _source_snapshot(root: Path, source: dict[str, Any], source_id: str, errors: list[str]) -> Path | None:
    origin = source.get("origin")
    snapshot_path = source.get("snapshot_path")
    location = f"{source_id}.origin"
    if origin is None:
        if source.get("release_eligible"):
            errors.append(f"{source_id} release source needs a verifiable origin")
        if source.get("checksum") is not None:
            errors.append(f"{source_id} checksum has no verifiable source content")
        if snapshot_path is not None:
            errors.append(f"{source_id}.snapshot_path requires a URL origin")
        return None
    if not isinstance(origin, str) or not origin.strip():
        errors.append(f"{location} must be a local relative path, HTTPS URL, or null")
        return None

    try:
        parsed = urlsplit(origin)
    except ValueError as exc:
        errors.append(f"{location} is not a valid origin: {exc}")
        return None
    if parsed.scheme:
        if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
            errors.append(f"{location} must use an HTTPS URL")
            return None
        if snapshot_path is None:
            errors.append(f"{source_id} URL origin requires snapshot_path")
            return None
        # The URL records provenance; release integrity is established from snapshot bytes.
        return _resolve_local_file(root, snapshot_path, f"{source_id}.snapshot_path", errors)

    if snapshot_path is not None:
        errors.append(f"{source_id}.snapshot_path is only valid for a URL origin")
    return _resolve_local_file(root, origin, location, errors)


def _allows_public_contacts(source: dict[str, Any] | None) -> bool:
    if not source:
        return False
    permission = source.get("permission")
    source_kind = source.get("source_kind")
    return bool(
        source.get("release_eligible") is True
        and source.get("status") == "approved"
        and source.get("approval") == "owner_approved"
        and isinstance(permission, str)
        and permission in RELEASE_PERMISSIONS
        and isinstance(source_kind, str)
        and source_kind in RELEASE_SOURCE_KINDS
        and source.get("pii_classification") == "public_business_contact"
    )


def _scan_pii(value: Any, location: str, errors: list[str], *, allow_public_contacts: bool = False) -> None:
    def visit(item: Any, path: str, depth: int = 0) -> bool:
        if isinstance(item, dict):
            found = False
            for key, child in item.items():
                if key in MACHINE_METADATA_FIELDS:
                    continue
                child_path = f"{path}.{key}"
                if depth == 0 and key in PUBLIC_CONTACT_FIELDS and allow_public_contacts:
                    pattern = EMAIL_PATTERN if key == "public_business_email" else PHONE_PATTERN
                    if isinstance(child, str) and pattern.fullmatch(child.strip()):
                        continue
                found = visit(child, child_path, depth + 1) or found
            return found
        if isinstance(item, list):
            return any(visit(child, f"{path}[{index}]", depth + 1) for index, child in enumerate(item))
        if isinstance(item, str):
            return bool(EMAIL_PATTERN.search(item) or PHONE_PATTERN.search(item))
        return False

    if visit(value, location):
        errors.append(f"possible PII pattern in {location}")


def _check_source_shape(root: Path, source: Any, index: int, errors: list[str]) -> tuple[str | None, dict[str, Any] | None]:
    location = f"manifest.sources[{index}]"
    if not isinstance(source, dict):
        errors.append(f"{location} must be an object")
        return None, None

    missing = REQUIRED_SOURCE_FIELDS - source.keys()
    if missing:
        errors.append(f"{location} missing fields: {sorted(missing)}")
    source_id = source.get("source_id")
    if not isinstance(source_id, str) or not source_id.strip():
        errors.append(f"{location}.source_id must be a non-empty string")
        source_id = None
    label = source_id or location

    status = source.get("status")
    if not isinstance(status, str) or status not in ALLOWED_SOURCE_STATUS:
        errors.append(f"{label} has invalid status")
    for field in ("permission", "approval", "version", "source_kind", "pii_classification"):
        if not isinstance(source.get(field), str) or not source[field].strip():
            errors.append(f"{label} requires non-empty {field}")
    if not isinstance(source.get("release_eligible"), bool):
        errors.append(f"{label}.release_eligible must be boolean")

    checksum = source.get("checksum")
    snapshot = _source_snapshot(root, source, label, errors)
    pending_reason = source.get("checksum_pending_reason")
    if "checksum_pending_reason" in source and not isinstance(pending_reason, str):
        errors.append(f"{label}.checksum_pending_reason must be a string")
    if checksum is None:
        if not isinstance(pending_reason, str) or not pending_reason.strip():
            errors.append(f"{label} needs checksum_pending_reason when checksum is null")
        if snapshot is not None:
            errors.append(f"{label} needs checksum for its source snapshot")
    elif not isinstance(checksum, str) or not re.fullmatch(r"[0-9a-f]{64}", checksum):
        errors.append(f"{label} checksum must be lowercase SHA-256")
    elif snapshot is not None:
        try:
            if _sha256(snapshot) != checksum:
                errors.append(f"{label} checksum does not match {_display_path(root, snapshot)}")
        except OSError as exc:
            errors.append(f"{label} snapshot cannot be hashed: {exc}")

    if source.get("release_eligible") is True:
        if source.get("status") != "approved":
            errors.append(f"{label} release source must be approved")
        if source.get("approval") != "owner_approved":
            errors.append(f"{label} release source needs owner_approved approval")
        permission = source.get("permission")
        if not isinstance(permission, str) or permission not in RELEASE_PERMISSIONS:
            errors.append(f"{label} release source needs public business permission")
        source_kind = source.get("source_kind")
        if not isinstance(source_kind, str) or source_kind not in RELEASE_SOURCE_KINDS:
            errors.append(f"{label} source kind cannot be release evidence")
        pii_classification = source.get("pii_classification")
        if not isinstance(pii_classification, str) or pii_classification not in {"none", "public_business_contact"}:
            errors.append(f"{label} release source needs an approved PII classification")
        if not isinstance(checksum, str) or not re.fullmatch(r"[0-9a-f]{64}", checksum):
            errors.append(f"{label} release source needs a verified SHA-256 checksum")

    _scan_pii(source, label, errors, allow_public_contacts=_allows_public_contacts(source))
    return source_id, source


def _validate_service_record(
    service: Any,
    location: str,
    source_by_id: dict[str, dict[str, Any]],
    errors: list[str],
    *,
    release_catalog: bool,
) -> tuple[str | None, str | None]:
    if not isinstance(service, dict):
        errors.append(f"{location} must be an object")
        return None, None
    missing = SERVICE_FIELDS - service.keys()
    if missing:
        errors.append(f"{location} missing fields: {sorted(missing)}")

    service_id = service.get("service_id")
    if not isinstance(service_id, str) or not service_id.strip():
        errors.append(f"{location}.service_id must be a non-empty string")
        service_id = None
    name = service.get("name_th")
    if not isinstance(name, str) or not name.strip():
        errors.append(f"{location}.name_th must be a non-empty string")
        name = None
    aliases = service.get("aliases")
    if not isinstance(aliases, list) or any(not isinstance(alias, str) for alias in aliases):
        errors.append(f"{location}.aliases must be a list of strings")
    for field in ("description", "currency", "specimen", "preparation", "result_turnaround", "version"):
        if service.get(field) is not None and not isinstance(service.get(field), str):
            errors.append(f"{location}.{field} must be a string or null")

    price = service.get("price")
    if price is not None:
        if not isinstance(price, dict):
            errors.append(f"{location}.price must be an object or null")
        else:
            amount = price.get("amount")
            valid_amount = (isinstance(amount, int) and not isinstance(amount, bool)) or (
                isinstance(amount, float) and math.isfinite(amount)
            )
            if not valid_amount:
                errors.append(f"{location}.price.amount must be a finite number")
            elif amount < 0:
                errors.append(f"{location}.price.amount cannot be negative")
            currency = service.get("currency")
            if not isinstance(currency, str) or not currency.strip():
                errors.append(f"{location}.currency is required when price is present")

    source_id = service.get("source_id")
    if not isinstance(source_id, str) or source_id not in source_by_id:
        errors.append(f"{location} references unknown source_id: {source_id}")
        source = None
    else:
        source = source_by_id[source_id]
        if release_catalog and source.get("release_eligible") is not True:
            errors.append(f"release service references non-release source: {source_id}")

    _scan_pii(service, location, errors, allow_public_contacts=_allows_public_contacts(source))
    return service_id, name


def _faq_entries(path: Path, root: Path, source_by_id: dict[str, dict[str, Any]], errors: list[str]) -> dict[str, dict[str, Any]]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append(f"missing FAQ file: {_display_path(root, path)}")
        return {}
    except (OSError, UnicodeDecodeError) as exc:
        errors.append(f"cannot read FAQ file {_display_path(root, path)}: {exc}")
        return {}

    headings = list(re.finditer(r"^## (FAQ-\d{2})\s+[^\r\n]*", text, flags=re.MULTILINE))
    entries: dict[str, dict[str, Any]] = {}
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        section = text[heading.start():end]
        faq_id = heading.group(1)
        status_matches = re.findall(r"^- Expected status: `([^`]+)`\s*$", section, flags=re.MULTILINE)
        refs_matches = re.findall(r"^- Source refs:\s*(.*)$", section, flags=re.MULTILINE)
        if len(status_matches) != 1 or status_matches[0] not in FAQ_STATUSES:
            errors.append(f"{faq_id} must declare one supported Expected status")
            status = None
        else:
            status = status_matches[0]
        if len(refs_matches) != 1:
            errors.append(f"{faq_id} must declare Source refs")
            refs: list[str] = []
        else:
            refs = re.findall(r"`([^`]+)`", refs_matches[0])
        for source_id in refs:
            if source_id not in source_by_id:
                errors.append(f"{faq_id} references unknown source_id: {source_id}")
        if not re.search(r"^- Answer contract:\s*\S", section, flags=re.MULTILINE):
            errors.append(f"{faq_id} requires a non-empty Answer contract")
        _scan_pii(section, faq_id, errors)
        entries[faq_id] = {"status": status, "source_ids": refs}

    if len(headings) != len(entries):
        errors.append("FAQ IDs must not be duplicated")
    if set(entries) != EXPECTED_FAQ_IDS:
        errors.append(f"FAQ IDs must be exactly {sorted(EXPECTED_FAQ_IDS)}")
    return entries


def _validate_message_list(case: dict[str, Any], case_id: str, errors: list[str]) -> list[dict[str, str]]:
    messages = case.get("prior_messages")
    if messages is None:
        return []
    if not isinstance(messages, list):
        errors.append(f"evaluation {case_id}.prior_messages must be a list")
        return []
    valid: list[dict[str, str]] = []
    for index, message in enumerate(messages):
        if not isinstance(message, dict):
            errors.append(f"evaluation {case_id}.prior_messages[{index}] must be an object")
            continue
        role = message.get("role")
        content = message.get("content")
        if not isinstance(role, str) or role not in {"user", "assistant"}:
            errors.append(f"evaluation {case_id}.prior_messages[{index}].role is invalid")
        if not isinstance(content, str) or not content.strip():
            errors.append(f"evaluation {case_id}.prior_messages[{index}].content must be non-empty")
        if isinstance(role, str) and role in {"user", "assistant"} and isinstance(content, str) and content.strip():
            valid.append({"role": role, "content": content})
    return valid


def _validate_evaluations(path: Path, root: Path, source_by_id: dict[str, dict[str, Any]], errors: list[str]) -> list[dict[str, Any]]:
    try:
        lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    except FileNotFoundError:
        errors.append(f"missing evaluation cases: {_display_path(root, path)}")
        return []
    except (OSError, UnicodeDecodeError) as exc:
        errors.append(f"cannot read evaluation cases {_display_path(root, path)}: {exc}")
        return []

    case_ids: set[str] = set()
    cases: list[dict[str, Any]] = []
    mandatory = holdout = 0
    for line_number, line in enumerate(lines, start=1):
        try:
            case = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"invalid evaluation JSONL line {line_number}: {exc}")
            continue
        if not isinstance(case, dict):
            errors.append(f"evaluation line {line_number} must be an object")
            continue
        cases.append(case)
        case_id = case.get("case_id")
        if not isinstance(case_id, str) or not case_id.strip():
            errors.append(f"evaluation line {line_number} missing case_id")
            case_id = f"line {line_number}"
        elif case_id in case_ids:
            errors.append(f"duplicate evaluation case_id: {case_id}")
        else:
            case_ids.add(case_id)
        if not isinstance(case.get("question_th"), str) or not case["question_th"].strip():
            errors.append(f"evaluation {case_id} requires a non-empty question_th")
        if not isinstance(case.get("intent"), str) or not case["intent"].strip():
            errors.append(f"evaluation {case_id} requires a non-empty intent")
        if case.get("set") == "mandatory":
            mandatory += 1
        elif case.get("set") == "holdout":
            holdout += 1
        else:
            errors.append(f"evaluation {case_id}.set must be mandatory or holdout")

        expected_sources = case.get("expected_source_ids")
        if not isinstance(expected_sources, list) or any(not isinstance(source_id, str) for source_id in expected_sources):
            errors.append(f"evaluation {case_id}.expected_source_ids must be a list of strings")
        else:
            for source_id in expected_sources:
                if source_id not in source_by_id:
                    errors.append(f"evaluation {case_id} references unknown source_id: {source_id}")
        for field in ("expected_facts", "pass_criteria"):
            field_value = case.get(field)
            if not isinstance(field_value, list) or any(not isinstance(item, str) for item in field_value):
                errors.append(f"evaluation {case_id}.{field} must be a list of strings")
        expected_status = case.get("expected_status")
        if not isinstance(expected_status, str) or not expected_status.strip():
            errors.append(f"evaluation {case_id}.expected_status must be a non-empty string")
        elif expected_status == "PENDING_SOURCE" and isinstance(expected_sources, list) and expected_sources:
            errors.append(f"pending evaluation {case_id} must have no expected source IDs")

        prior_messages = _validate_message_list(case, str(case_id), errors)
        if case_id == "Q09":
            roles = [message["role"] for message in prior_messages]
            alternating = all(left != right for left, right in zip(roles, roles[1:]))
            if (
                len(prior_messages) < 2
                or roles[0] != "user"
                or roles[-1] != "assistant"
                or not alternating
            ):
                errors.append("Q09 requires at least two prior messages including user and assistant turns")
            question = case.get("question_th")
            if isinstance(question, str) and any(question.strip() == message["content"].strip() for message in prior_messages):
                errors.append("Q09 follow-up question must be separate from prior message content")
        _scan_pii(case, f"evaluation {case_id}", errors)

    if mandatory != 10:
        errors.append(f"evaluation must contain 10 mandatory cases, found {mandatory}")
    if holdout < 5:
        errors.append(f"evaluation must contain at least 5 holdout cases, found {holdout}")
    if "Q09" not in case_ids:
        errors.append("evaluation must contain Q09 multi-turn follow-up case")
    return cases


def _validate_structure(root: Path) -> dict[str, Any]:
    errors: list[str] = []
    manifest_path = root / "knowledge" / "source_manifest.json"
    services_path = root / "knowledge" / "services.json"
    fixture_path = root / "knowledge" / "fixtures" / "services.synthetic.json"
    faq_path = root / "knowledge" / "policies" / "FAQ.md"
    cases_path = root / "evaluation" / "cases.jsonl"

    manifest = _load_json(manifest_path, root, errors)
    services = _load_json(services_path, root, errors)
    fixtures = _load_json(fixture_path, root, errors)
    if manifest is not _INVALID and not isinstance(manifest, dict):
        errors.append("manifest must be an object")
        manifest = _INVALID
    if services is not _INVALID and not isinstance(services, dict):
        errors.append("knowledge/services.json must be an object")
        services = _INVALID
    if fixtures is not _INVALID and not isinstance(fixtures, dict):
        errors.append("synthetic fixture file must be an object")
        fixtures = _INVALID

    source_by_id: dict[str, dict[str, Any]] = {}
    if isinstance(manifest, dict):
        if not isinstance(manifest.get("manifest_version"), str) or not manifest["manifest_version"].strip():
            errors.append("manifest_version must be a non-empty string")
        for field in ("corpus_version", "business_id", "generated_at"):
            if not isinstance(manifest.get(field), str) or not manifest[field].strip():
                errors.append(f"manifest.{field} must be a non-empty string")
        if not isinstance(manifest.get("release_eligible"), bool):
            errors.append("manifest.release_eligible must be boolean")
        blockers = manifest.get("release_blockers")
        if not isinstance(blockers, list) or any(not isinstance(item, str) for item in blockers):
            errors.append("manifest.release_blockers must be a list of strings")
        sources = manifest.get("sources")
        if not isinstance(sources, list) or not sources:
            errors.append("manifest.sources must be a non-empty list")
            sources = []
        seen_source_ids: set[str] = set()
        for index, item in enumerate(sources):
            source_id, source = _check_source_shape(root, item, index, errors)
            if source_id is None or source is None:
                continue
            if source_id in seen_source_ids:
                errors.append(f"duplicate source_id: {source_id}")
            else:
                seen_source_ids.add(source_id)
                source_by_id[source_id] = source

        release_corpus = manifest.get("release_corpus")
        if not isinstance(release_corpus, dict):
            errors.append("manifest.release_corpus must be an object")
            release_corpus = {}
        release_status = release_corpus.get("status")
        if not isinstance(release_status, str) or release_status not in {"PENDING_SOURCE", "APPROVED"}:
            errors.append("manifest.release_corpus.status is invalid")
        for field in ("service_source_ids", "policy_source_ids", "education_source_ids"):
            values = release_corpus.get(field)
            if not isinstance(values, list) or any(not isinstance(value, str) for value in values):
                errors.append(f"manifest.release_corpus.{field} must be a list of strings")
                continue
            for source_id in values:
                if source_id not in source_by_id:
                    errors.append(f"manifest.release_corpus.{field} references unknown source_id: {source_id}")
        page_evidence = release_corpus.get("source_page_evidence")
        if page_evidence is not None:
            if not isinstance(page_evidence, dict):
                errors.append("manifest.release_corpus.source_page_evidence must be an object")
            else:
                page_count = page_evidence.get("page_count")
                page_source_ids = page_evidence.get("source_ids")
                if not isinstance(page_count, int) or isinstance(page_count, bool) or page_count < 0:
                    errors.append("manifest.release_corpus.source_page_evidence.page_count must be a nonnegative integer")
                if not isinstance(page_source_ids, list) or any(not isinstance(value, str) for value in page_source_ids):
                    errors.append("manifest.release_corpus.source_page_evidence.source_ids must be a list of strings")
                else:
                    if len(page_source_ids) != len(set(page_source_ids)):
                        errors.append("manifest.release_corpus.source_page_evidence.source_ids must be unique")
                    for source_id in page_source_ids:
                        if source_id not in source_by_id:
                            errors.append(f"source_page_evidence references unknown source_id: {source_id}")
    else:
        manifest = {}

    if isinstance(services, dict):
        if not isinstance(services.get("schema_version"), str) or not services["schema_version"].strip():
            errors.append("knowledge/services.json.schema_version must be a non-empty string")
        if not isinstance(services.get("release_eligible"), bool):
            errors.append("knowledge/services.json.release_eligible must be boolean")
        field_contract = services.get("service_field_contract")
        if not isinstance(field_contract, dict):
            errors.append("knowledge/services.json.service_field_contract must be an object")
        else:
            required_fields = field_contract.get("required")
            if not isinstance(required_fields, list) or any(not isinstance(field, str) for field in required_fields):
                errors.append("service_field_contract.required must be a list of strings")
            elif set(required_fields) != SERVICE_FIELDS:
                errors.append("service_field_contract.required does not match the service schema")
            if field_contract.get("unknown_value") is not None:
                errors.append("service_field_contract.unknown_value must be null")
            if not isinstance(field_contract.get("price_rule"), str) or not field_contract["price_rule"].strip():
                errors.append("service_field_contract.price_rule must be a non-empty string")
        blocking_reasons = services.get("blocking_reasons")
        if not isinstance(blocking_reasons, list) or any(not isinstance(reason, str) for reason in blocking_reasons):
            errors.append("knowledge/services.json.blocking_reasons must be a list of strings")
        release_catalog = services.get("release_eligible") is True
        if release_catalog and services.get("release_status") != "APPROVED":
            errors.append("release service catalog must have release_status=APPROVED")
        if not release_catalog and services.get("release_status") != "PENDING_SOURCE":
            errors.append("pending service catalog must have release_status=PENDING_SOURCE")
        service_records = services.get("services")
        if not isinstance(service_records, list):
            errors.append("knowledge/services.json.services must be a list")
            service_records = []
        service_ids: set[str] = set()
        service_names: set[str] = set()
        for index, service in enumerate(service_records):
            location = f"services[{index}]"
            service_id, name = _validate_service_record(
                service, location, source_by_id, errors, release_catalog=release_catalog
            )
            if service_id:
                if service_id in service_ids:
                    errors.append(f"duplicate service_id: {service_id}")
                service_ids.add(service_id)
            if name:
                normalized_name = re.sub(r"\s+", " ", name.strip().casefold())
                if normalized_name in service_names:
                    errors.append(f"duplicate service name: {name}")
                service_names.add(normalized_name)
    else:
        services = {}

    if isinstance(fixtures, dict):
        fixture_source_id = fixtures.get("source_id")
        if not isinstance(fixtures.get("schema_version"), str) or not fixtures["schema_version"].strip():
            errors.append("synthetic fixture schema_version must be a non-empty string")
        if not isinstance(fixtures.get("business_id"), str) or not fixtures["business_id"].strip():
            errors.append("synthetic fixture business_id must be a non-empty string")
        if fixtures.get("release_eligible") is not False or fixtures.get("fixture_status") != "SYNTHETIC_DEVELOPMENT_ONLY":
            errors.append("synthetic services fixture must be explicitly non-release")
        if not isinstance(fixture_source_id, str) or fixture_source_id not in source_by_id:
            errors.append("synthetic services fixture references unknown source_id")
        else:
            fixture_source = source_by_id[fixture_source_id]
            if fixture_source.get("source_kind") != "synthetic" or fixture_source.get("release_eligible") is not False:
                errors.append("synthetic services fixture source must be non-release synthetic")
        records = fixtures.get("services")
        if not isinstance(records, list) or not records:
            errors.append("synthetic services fixture must contain at least one record")
            records = []
        fixture_ids: set[str] = set()
        fixture_names: set[str] = set()
        for index, service in enumerate(records):
            location = f"synthetic_services[{index}]"
            service_id, name = _validate_service_record(service, location, source_by_id, errors, release_catalog=False)
            if service_id:
                if service_id in fixture_ids:
                    errors.append(f"duplicate synthetic service_id: {service_id}")
                fixture_ids.add(service_id)
            if name:
                normalized_name = re.sub(r"\s+", " ", name.strip().casefold())
                if normalized_name in fixture_names:
                    errors.append(f"duplicate synthetic service name: {name}")
                fixture_names.add(normalized_name)
            if isinstance(service, dict) and service.get("source_id") != fixture_source_id:
                errors.append(f"{location} must use fixture source_id {fixture_source_id}")
        _scan_pii(fixtures, "synthetic services fixture", errors)

    faq_entries = _faq_entries(faq_path, root, source_by_id, errors)
    cases = _validate_evaluations(cases_path, root, source_by_id, errors)
    return {
        "errors": errors,
        "manifest": manifest,
        "services": services,
        "sources": source_by_id,
        "faq_entries": faq_entries,
        "cases": cases,
    }


def validate_corpus(root: Path | None = None) -> list[str]:
    """Return structural/data-contract errors; pending owner inputs are allowed."""
    resolved_root = (root or Path(__file__).resolve().parents[1]).resolve()
    return _validate_structure(resolved_root)["errors"]


def validate_release_readiness(root: Path | None = None) -> list[str]:
    """Return release blockers separately from structural validation errors."""
    resolved_root = (root or Path(__file__).resolve().parents[1]).resolve()
    report = _validate_structure(resolved_root)
    if report["errors"]:
        return [f"structural validation failed: {error}" for error in report["errors"]]

    manifest = report["manifest"]
    services = report["services"]
    sources = report["sources"]
    faq_entries = report["faq_entries"]
    blockers: list[str] = []
    eligible_sources = {
        source_id: source
        for source_id, source in sources.items()
        if source.get("release_eligible") is True
    }

    if manifest.get("release_eligible") is not True:
        blockers.append("manifest.release_eligible is false; owner-approved corpus is pending")
    release_blockers = manifest.get("release_blockers", [])
    if release_blockers:
        blockers.extend(f"manifest release blocker: {item}" for item in release_blockers)
    if manifest.get("release_corpus", {}).get("status") != "APPROVED":
        blockers.append("manifest.release_corpus.status is not APPROVED")
    if not eligible_sources:
        blockers.append("no release-eligible owner-approved public business sources are present")

    release_corpus = manifest.get("release_corpus", {})
    service_source_ids = set(release_corpus.get("service_source_ids", []))
    policy_source_ids = set(release_corpus.get("policy_source_ids", []))
    for field in ("service_source_ids", "policy_source_ids", "education_source_ids"):
        source_ids = release_corpus.get(field, [])
        if not source_ids:
            blockers.append(f"manifest.release_corpus.{field} is empty")
        for source_id in source_ids:
            if source_id not in eligible_sources:
                blockers.append(f"manifest.release_corpus.{field} includes non-release evidence: {source_id}")

    if services.get("release_eligible") is not True or services.get("release_status") != "APPROVED":
        blockers.append("knowledge/services.json is not an approved release catalog")
    service_records = services.get("services", [])
    for index, service in enumerate(service_records):
        source_id = service.get("source_id") if isinstance(service, dict) else None
        if source_id not in eligible_sources:
            blockers.append(f"release service {index} lacks approved public source evidence")
        if source_id not in service_source_ids:
            blockers.append(f"release service {index} is absent from manifest.service_source_ids")

    page_evidence = release_corpus.get("source_page_evidence")
    page_evidence_passes = False
    if isinstance(page_evidence, dict):
        page_count = page_evidence.get("page_count")
        page_source_ids = page_evidence.get("source_ids", [])
        if isinstance(page_count, int) and not isinstance(page_count, bool) and isinstance(page_source_ids, list):
            distinct_origins: set[str] = set()
            distinct_snapshots: set[str] = set()
            all_eligible = True
            for source_id in page_source_ids:
                source = eligible_sources.get(source_id)
                if source is None:
                    all_eligible = False
                    break
                origin = source.get("origin")
                if not isinstance(origin, str) or not origin:
                    all_eligible = False
                    break
                distinct_origins.add(origin.casefold().rstrip("/"))
                snapshot_path = source.get("snapshot_path") if urlsplit(origin).scheme else origin
                if not isinstance(snapshot_path, str):
                    all_eligible = False
                    break
                try:
                    distinct_snapshots.add(str((resolved_root / snapshot_path).resolve()).casefold())
                except (OSError, RuntimeError, ValueError):
                    all_eligible = False
                    break
            page_evidence_passes = (
                page_count >= 5
                and page_count == len(page_source_ids)
                and all_eligible
                and len(distinct_origins) == page_count
                and len(distinct_snapshots) == page_count
            )

    if len(service_records) < 15 and not page_evidence_passes:
        blockers.append(
            f"release quantity evidence is incomplete: {len(service_records)} distinct services "
            "(15 required) and fewer than five distinct verified source pages"
        )

    if set(faq_entries) != EXPECTED_FAQ_IDS:
        blockers.append("the ten required FAQ entries are incomplete")
    for faq_id in sorted(EXPECTED_FAQ_IDS):
        entry = faq_entries.get(faq_id)
        if not entry:
            continue
        if entry.get("status") != "APPROVED_SOURCE":
            blockers.append(f"{faq_id} remains PENDING_SOURCE")
        refs = entry.get("source_ids", [])
        if not refs or any(source_id not in eligible_sources for source_id in refs):
            blockers.append(f"{faq_id} does not cite approved release sources")
        if any(source_id not in policy_source_ids for source_id in refs):
            blockers.append(f"{faq_id} source references are absent from manifest.policy_source_ids")

    return blockers


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=("structural", "release"),
        default="structural",
        help="validate structure only or require release readiness",
    )
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    structural_errors = validate_corpus(root)
    if structural_errors:
        print("STRUCTURAL VALIDATION: FAIL")
        for error in structural_errors:
            print(f"- {error}")
        print("RELEASE READINESS: NOT_READY (structural validation failed)")
        return 1

    print("STRUCTURAL VALIDATION: PASS")
    release_blockers = validate_release_readiness(root)
    if not release_blockers:
        print("RELEASE READINESS: PASS")
        print("- approved public business sources and release corpus satisfy configured gates")
        return 0

    print("RELEASE READINESS: BLOCKED")
    for blocker in release_blockers:
        print(f"- {blocker}")
    return 1 if args.mode == "release" else 0


if __name__ == "__main__":
    sys.exit(main())
