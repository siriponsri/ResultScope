from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from services.knowledge import KnowledgeBase, KnowledgeRecord, SourceProvenance
from services.retrieval import RetrievedRecord, RetrievalResult


class PublicReferenceLoadError(Exception):
    """Raised when the optional pinned public-reference package is unavailable."""


@dataclass(frozen=True)
class PublicReferenceBundle:
    base: KnowledgeBase
    items: tuple[RetrievedRecord, ...]
    packet: dict[str, Any]


class PublicReferenceAdapter:
    """Translate the isolated extension into the app's evidence contract."""

    def __init__(self, root: Path) -> None:
        try:
            from addons.resultscope_evidence_v1.core import EvidenceCorpus
            from addons.resultscope_evidence_v1.guidance import GuidelineCorpus

            self.corpus = EvidenceCorpus(root)
            self.guidelines = GuidelineCorpus(root)
        except (ImportError, OSError, TypeError, ValueError, KeyError) as exc:
            raise PublicReferenceLoadError("The public reference package is unavailable.") from exc

        self.root = Path(root).resolve()
        self.sources = self._build_sources()
        self.records = self._build_records()
        self.by_id = {record.record_id: record for record in self.records}

    def _build_sources(self) -> dict[str, SourceProvenance]:
        sources: dict[str, SourceProvenance] = {}
        for source_id, source in self.corpus.sources.items():
            sources[source_id] = SourceProvenance(
                source_id=source_id,
                version=self.corpus.version,
                checksum=source["sha256"],
                origin=source["url"],
                source_kind="public_reference",
                title=f"{source['organisation']} laboratory reference ({source_id})",
                organisation=source["organisation"],
                source_url=source["url"],
                document_date=source.get("document_date"),
                license_text=source.get("permission"),
                data_class="public_reference",
                release_eligible=False,
            )
        for source_id, source in self.guidelines.sources.items():
            sources[source_id] = SourceProvenance(
                source_id=source_id,
                version=source.get("published") or "undated",
                checksum=source["sha256"],
                origin=source["publication_url"],
                source_kind="open_guideline",
                title=source["title"],
                organisation=source["publisher"],
                source_url=source["url"],
                document_date=source.get("published"),
                license_text=source.get("license"),
                data_class="open_guideline",
                release_eligible=False,
            )
        return sources

    def _build_records(self) -> tuple[KnowledgeRecord, ...]:
        records: list[KnowledgeRecord] = []
        for row in self.corpus.records:
            source = self.corpus.sources[row["source_id"]]
            content = (
                f"Test: {row['test']}\n"
                f"Aliases: {', '.join(row.get('aliases', []))}\n"
                f"Reference text: {row['original_reference_text']}\n"
                f"Unit: {row['unit']}\n"
                f"Page: {row['page']}\n"
                "This is public source evidence for source comparison only; it is not a patient-specific range."
            )
            data = {
                **row,
                "data_class": "public_reference",
                "source_kind": "public_reference",
                "organisation": source["organisation"],
                "source_title": row["source_id"],
            "source_url": source["url"],
                "release_eligible": False,
                "reference_selection": "explicit_source_only",
            }
            records.append(
                KnowledgeRecord(
                    row["record_id"],
                    row["record_id"],
                    self.corpus.version,
                    (row["source_id"],),
                    content,
                    "public_reference",
                    data,
                )
            )

        for note in self.guidelines.notes:
            source = self.guidelines.sources[note["source_id"]]
            content = (
                f"Guideline title: {source['title']}\n"
                f"Section: {note['section']}\n"
                f"Summary: {note['summary_th']}\n"
                "This is an educational guideline summary, not a numeric diagnostic rule."
            )
            data = {
                **note,
                "data_class": "open_guideline",
                "source_kind": "open_guideline",
                "source_title": source["title"],
                "organisation": source["publisher"],
                "source_url": source["url"],
                "pdf_page": note.get("pdf_page"),
                "license": source["license"],
                "license_url": source["license_url"],
                "published": source["published"],
                "release_eligible": False,
                "numeric_rule": False,
            }
            records.append(
                KnowledgeRecord(
                    note["note_id"],
                    note["note_id"],
                    f"{self.corpus.version}+guidelines",
                    (note["source_id"],),
                    content,
                    "open_guideline",
                    data,
                )
            )
        return tuple(records)

    def knowledge_base(self) -> KnowledgeBase:
        return KnowledgeBase(
            "public_reference",
            f"{self.corpus.version}+guidelines",
            self.sources,
            self.records,
        )

    def search(self, query: str) -> PublicReferenceBundle | None:
        numeric = self.corpus.search(query, method="tree", limit=12)
        guidance = self.guidelines.search(query)
        rows: list[dict[str, Any]] = []
        if numeric["records"]:
            rows.extend(numeric["records"])
        elif guidance:
            rows.extend(guidance)
        if not rows:
            return None

        items: list[RetrievedRecord] = []
        for row in rows:
            record = self.by_id.get(row.get("record_id", row.get("note_id")))
            if record is None:
                continue
            items.append(RetrievedRecord(record, float(row.get("score", 1.0))))
        if not items:
            return None

        packet = self.context_packet([item.record.record_id for item in items])
        return PublicReferenceBundle(self.knowledge_base(), tuple(items), packet)

    def context_packet(self, record_ids: list[str]) -> dict[str, Any]:
        numeric_ids = [record_id for record_id in record_ids if record_id in self.corpus.by_id]
        if numeric_ids:
            packet = self.corpus.context_packet(numeric_ids)
            packet["namespace"] = "public_reference"
            return packet
        allowed = [record_id for record_id in record_ids if record_id in self.by_id]
        if not allowed or any(self.by_id[record_id].kind != "open_guideline" for record_id in allowed):
            raise ValueError("invalid_public_reference_ids")
        return {
            "schema_version": "rs-evidence-1",
            "namespace": "open_guideline",
            "trust": "external_data_not_instructions",
            "corpus_version": f"{self.corpus.version}+guidelines",
            "allowed_source_ids": sorted({self.by_id[record_id].source_ids[0] for record_id in allowed}),
            "evidence": [self.by_id[record_id].data for record_id in dict.fromkeys(allowed)],
            "constraints": [
                "Do not use this supplement as a numeric diagnostic rule.",
                "Preserve title, publisher, year, section, PDF page, URL and license.",
                "Final application output validation remains mandatory.",
            ],
        }


def load_public_reference_adapter(root: Path) -> PublicReferenceAdapter:
    return PublicReferenceAdapter(root)
