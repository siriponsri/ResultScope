# Phase 4A report — public reference evidence

Date: 2026-10-03  
Branch: local `main`  
Scope: integrate `addons/resultscope_evidence_v1` without promoting it to the
business or release corpus.

## Status

| Gate | Status | Evidence |
|---|---|---|
| Addon structural/hash integrity | PASS | `addons/resultscope_evidence_v1/verify.py`: 17 sources/26 numeric records and 2 guideline sources/3 notes; addon tests 50 passed |
| Runtime adapter and namespace separation | PASS | `tests/test_public_reference.py`; focused project suite 68 passed |
| Source metadata preservation | PASS | Adapter tests assert source IDs, URLs, pages, public class, guideline sections, and CC BY-NC-SA license |
| Corrupt/missing/no-hit fail-closed behavior | PASS | `test_public_reference_no_hit_and_corrupt_root_abstain` and missing snapshot test |
| Approved business/release readiness | BLOCKED | Public hospital references are not owner-approved business sources and remain `release_eligible=false` |
| Live provider/OCR quality | NOT_RUN | No owner-authorized live credentials or calls were used |

## Implemented boundary

`services/public_reference.py` lazily loads the pinned addon and translates its
records to the existing `KnowledgeBase`/`RetrievedRecord` contract. Numeric
hospital records use `public_reference`; WHO educational notes use
`open_guideline` and carry title, publisher, year, section, PDF URL, page and
license metadata. A missing or corrupt package, unknown analyte, or empty match
returns a clear abstention before the provider call.

The adapter does not select a universal patient range, infer age/pregnancy/sex/
method, convert units, average conflicting institutions, or claim complete
hospital coverage. The report-supplied interval remains primary.

## Source rights and limitations

The addon preserves the original source URLs, snapshot hashes, permission text,
and corpus version. WHO notes are educational and licensed `CC BY-NC-SA 3.0
IGO`; that is not unrestricted commercial approval. Publication or commercial
redistribution needs a separate rights decision.
