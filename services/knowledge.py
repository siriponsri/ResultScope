from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlsplit

from validation.validate_corpus import validate_corpus, validate_release_readiness

KnowledgeMode = Literal["release", "synthetic"]


class KnowledgeLoadError(Exception):
    def __init__(self, message: str, code: str = "knowledge_unavailable") -> None:
        self.message = message
        self.code = code
        super().__init__(message)


@dataclass(frozen=True)
class SourceProvenance:
    source_id: str
    version: str
    checksum: str
    origin: str
    source_kind: str


@dataclass(frozen=True)
class KnowledgeRecord:
    record_id: str
    chunk_id: str
    corpus_version: str
    source_ids: tuple[str, ...]
    content: str
    kind: str
    data: dict[str, Any]


@dataclass(frozen=True)
class KnowledgeBase:
    mode: KnowledgeMode
    corpus_version: str
    sources: dict[str, SourceProvenance]
    records: tuple[KnowledgeRecord, ...]

    @property
    def demo(self) -> bool:
        return self.mode == "synthetic"

    def metadata(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "demo": self.demo,
            "corpus_version": self.corpus_version,
            "record_count": len(self.records),
        }


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise KnowledgeLoadError(f"Knowledge file is unavailable or malformed: {label}") from exc
    if not isinstance(value, dict):
        raise KnowledgeLoadError(f"Knowledge file has an invalid root type: {label}")
    return value


def _source_snapshot(root: Path, source: dict[str, Any]) -> tuple[Path, str]:
    origin = source.get("origin")
    snapshot = source.get("snapshot_path")
    local_value = snapshot if isinstance(origin, str) and urlsplit(origin).scheme else origin
    if not isinstance(local_value, str) or not local_value.strip():
        raise KnowledgeLoadError("Knowledge source has no verifiable local snapshot.", "invalid_provenance")
    candidate = (root / local_value).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise KnowledgeLoadError("Knowledge source snapshot is outside the repository root.", "invalid_provenance") from exc
    if not candidate.is_file():
        raise KnowledgeLoadError("Knowledge source snapshot is missing.", "invalid_provenance")
    digest = hashlib.sha256(candidate.read_bytes()).hexdigest()
    if source.get("checksum") != digest:
        raise KnowledgeLoadError("Knowledge source snapshot checksum does not match.", "invalid_provenance")
    return candidate, digest


def _provenance(source: dict[str, Any]) -> SourceProvenance:
    source_id = source.get("source_id")
    version = source.get("version")
    checksum = source.get("checksum")
    origin = source.get("origin")
    kind = source.get("source_kind")
    if not all(isinstance(value, str) and value for value in (source_id, version, checksum, origin, kind)):
        raise KnowledgeLoadError("Knowledge source is missing provenance fields.", "invalid_provenance")
    return SourceProvenance(source_id, version, checksum, origin, kind)


def _stable_record_id(corpus_version: str, source_ids: tuple[str, ...], key: str, content: str) -> str:
    material = "\0".join((corpus_version, ",".join(source_ids), key, content))
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:24]


def _service_content(service: dict[str, Any]) -> str:
    labels = {
        "service_id": "Service ID",
        "name_th": "Thai service name",
        "aliases": "Aliases",
        "description": "Description",
        "price": "Price",
        "currency": "Currency",
        "specimen": "Specimen",
        "preparation": "Preparation",
        "result_turnaround": "Result turnaround",
    }
    parts = []
    for field, label in labels.items():
        value = service.get(field)
        if value is None or value == "":
            continue
        rendered = ", ".join(map(str, value)) if isinstance(value, list) else str(value)
        parts.append(f"{label}: {rendered}")
    return "\n".join(parts)


def _service_records(
    services: list[Any], source_map: dict[str, SourceProvenance], corpus_version: str
) -> list[KnowledgeRecord]:
    records: list[KnowledgeRecord] = []
    for index, value in enumerate(services):
        if not isinstance(value, dict):
            raise KnowledgeLoadError(f"Service record {index} is not an object.", "invalid_corpus")
        source_id = value.get("source_id")
        if not isinstance(source_id, str) or source_id not in source_map:
            raise KnowledgeLoadError(f"Service record {index} has no eligible source.", "invalid_corpus")
        content = _service_content(value)
        if not content:
            continue
        service_id = str(value.get("service_id", index))
        record_id = _stable_record_id(corpus_version, (source_id,), service_id, content)
        records.append(KnowledgeRecord(record_id, record_id, corpus_version, (source_id,), content, "service", value))
    return records


def _faq_records(
    path: Path, sources: dict[str, SourceProvenance], corpus_version: str
) -> list[KnowledgeRecord]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise KnowledgeLoadError("Approved FAQ source is unavailable.", "invalid_corpus") from exc
    sections = re.split(r"(?m)^##\s+", text)[1:]
    records: list[KnowledgeRecord] = []
    for section in sections:
        heading, _, body = section.partition("\n")
        faq_match = re.match(r"(FAQ-\d+)\s+—\s+(.+)", heading.strip())
        status_match = re.search(r"(?m)^- Expected status:\s*(\S+)", body)
        answer_match = re.search(r"(?m)^- Answer contract:\s*(.+)", body)
        refs_match = re.search(r"(?m)^- Source refs:\s*(.+)", body)
        if not (faq_match and status_match and answer_match and refs_match):
            continue
        if status_match.group(1) != "APPROVED_SOURCE":
            continue
        source_ids = tuple(
            source_id.strip()
            for source_id in refs_match.group(1).split(",")
            if source_id.strip() in sources
        )
        if not source_ids:
            continue
        content = f"Question: {faq_match.group(2).strip()}\nAnswer: {answer_match.group(1).strip()}"
        faq_id = faq_match.group(1)
        record_id = _stable_record_id(corpus_version, source_ids, faq_id, content)
        records.append(KnowledgeRecord(record_id, record_id, corpus_version, source_ids, content, "faq", {"faq_id": faq_id}))
    return records


def load_knowledge_base(
    root: Path | None = None,
    *,
    mode: KnowledgeMode,
    environment: str = "development",
) -> KnowledgeBase:
    resolved_root = (root or Path(__file__).resolve().parents[1]).resolve()
    if mode not in {"release", "synthetic"}:
        raise KnowledgeLoadError("KNOWLEDGE_MODE must be release or synthetic.", "invalid_mode")
    if mode == "synthetic" and environment.casefold() not in {"development", "test", "local"}:
        raise KnowledgeLoadError("Synthetic knowledge is disabled outside local development and tests.", "invalid_mode")

    structural_errors = validate_corpus(resolved_root)
    if structural_errors:
        raise KnowledgeLoadError("Knowledge corpus failed structural validation.", "invalid_corpus")

    manifest = _read_json(resolved_root / "knowledge" / "source_manifest.json", "source_manifest.json")
    corpus_version = manifest.get("corpus_version")
    source_rows = manifest.get("sources")
    if not isinstance(corpus_version, str) or not corpus_version or not isinstance(source_rows, list):
        raise KnowledgeLoadError("Source manifest has invalid version or source records.", "invalid_corpus")
    source_by_id = {
        row.get("source_id"): row for row in source_rows if isinstance(row, dict) and isinstance(row.get("source_id"), str)
    }

    if mode == "release":
        release_blockers = validate_release_readiness(resolved_root)
        if structural_errors or release_blockers:
            raise KnowledgeLoadError(
                "Release knowledge corpus is not ready; synthetic fallback is disabled.",
                "release_not_ready",
            )
        release_ids = {
            source_id
            for source_id, row in source_by_id.items()
            if row.get("release_eligible") is True
            and row.get("status") == "approved"
            and row.get("approval") == "owner_approved"
            and row.get("permission") == "owner_public_source"
        }
        if not release_ids:
            raise KnowledgeLoadError("Release corpus has no approved owner sources.", "release_not_ready")
        sources: dict[str, SourceProvenance] = {}
        for source_id in release_ids:
            row = source_by_id[source_id]
            _source_snapshot(resolved_root, row)
            sources[source_id] = _provenance(row)
        catalog = _read_json(resolved_root / "knowledge" / "services.json", "services.json")
        records = _service_records(catalog.get("services", []), sources, corpus_version)
        records.extend(_faq_records(resolved_root / "knowledge" / "policies" / "FAQ.md", sources, corpus_version))
        if not records:
            raise KnowledgeLoadError("Release corpus has no indexed records.", "release_not_ready")
        return KnowledgeBase("release", corpus_version, sources, tuple(records))

    fixture_path = resolved_root / "knowledge" / "fixtures" / "services.synthetic.json"
    fixture = _read_json(fixture_path, "services.synthetic.json")
    fixture_source_id = fixture.get("source_id")
    source = source_by_id.get(fixture_source_id) if isinstance(fixture_source_id, str) else None
    if (
        not source
        or source.get("source_kind") != "synthetic"
        or source.get("release_eligible") is not False
        or source.get("status") != "draft"
        or fixture.get("fixture_status") != "SYNTHETIC_DEVELOPMENT_ONLY"
    ):
        raise KnowledgeLoadError("Synthetic fixture provenance is invalid.", "invalid_provenance")
    _source_snapshot(resolved_root, source)
    sources = {fixture_source_id: _provenance(source)}
    records = _service_records(fixture.get("services", []), sources, corpus_version)
    if not records:
        raise KnowledgeLoadError("Synthetic development fixture has no service records.", "invalid_corpus")
    return KnowledgeBase("synthetic", corpus_version, sources, tuple(records))


def knowledge_base_to_dict(base: KnowledgeBase) -> dict[str, Any]:
    return {
        "schema_version": "knowledge-index-v1",
        **base.metadata(),
        "sources": {key: asdict(value) for key, value in sorted(base.sources.items())},
        "records": [asdict(record) for record in base.records],
    }
