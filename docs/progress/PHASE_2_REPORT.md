# ResultScope Phase 2 Report - RAG and API development

Date: **2026-10-02**

## Checkpoint and scope

- Base: `6f7ae8cbf0843dbb7c6d70bdcfb5924778635028`.
- Implementation checkpoint: `d4bd1b7350b576f6d9020696cfd30f225e305463`.
- Final documentation closeout checkpoint: `eb2afa9` before this metadata refresh.
- Branch: local `main`, ahead of `origin/main`; no push, deploy, branch, or worktree creation.
- Scope: P2 development routing, versioned synthetic knowledge/indexing, deterministic retrieval, source-bound answer contracts, sync/SSE policy convergence, session integrity, provider/store failure handling, and regression evidence.
- Exclusions: approved business-data ingestion, live provider/embedding evaluation, Vision/OCR, UI redesign, Phase 3, runtime multi-agent/graph/MCP, deployment, and unrelated projects.

## Gate summary

| Gate | Status | Evidence |
|---|---|---|
| Historical G0 | **BLOCKED** | Preserved from Phase 0 and Phase 1; this Phase 2 development work does not close it. |
| Structural validation | **PASS** | `validation/validate_corpus.py` on the pending/development corpus. |
| Release readiness / G1-data | **BLOCKED** | No owner-approved public sources, approved FAQ/policy/education facts, or release service catalog are present. `--mode release` exits 1. |
| P2 development contract | **PASS for implemented synthetic/mocked scope** | 102 project tests, compile check, scripts/check.ps1, synthetic index, and retrieval evidence pass. This is not semantic-quality or release evidence. |
| Live provider/embedding evaluation | **BLOCKED / NOT_RUN** | No credential was read, printed, stored, or used; no live provider or embedding call was made. |
| Independent REVIEW | **NOT_RUN** | The authorized FO IMPLEMENT run did not produce a handoff, so the helper did not provide an inspectable REVIEW candidate. MAIN self-review is explicitly non-independent. |

## P2 development implementation/tests

### Implemented findings and behavior

- Added `services/intent_router.py` for business FAQ, lab, mixed, unsafe, local, and unrelated intent decisions. Business FAQ questions are allowed into the policy pipeline without inventing facts. `Should I be concerned?` is a lab follow-up only when prior lab history contains a result; unrelated requests bypass the provider.
- Added `services/knowledge.py` and `scripts/build_index.py`. Release mode runs structural and release-readiness validation and fails closed. Synthetic mode requires explicit `KNOWLEDGE_MODE=synthetic` and a local/test environment, exposes `demo=true` in response metadata, verifies the fixture checksum, and indexes only the non-release synthetic service fixture. The generated index is `data/indexes/synthetic-resultscope-lab-demo-pending-v1.json`.
- Added versioned records with deterministic `record_id`/`chunk_id`, corpus version, source IDs, source version, checksum, origin, and source kind. Evaluation cases, expected answers, project instructions, planning documents, and the untracked `docs/coursework-demo/` pack are not loader inputs.
- Added `services/retrieval.py` with deterministic lexical/character-ngram retrieval, no-hit and ambiguity outcomes, bounded top-k, and measured local retrieval latency. `scripts/evaluate_retrieval.py` records expected IDs, actual IDs, source IDs, latency, corpus version, and the fact that no live embedding/provider was used.
- Added `services/answer_service.py`. Answers carry status (`answered`, `clarify`, `abstained`, `refused`, or `error`), citations resolved from retrieved records, corpus/demo metadata, and retrieval evidence. Unsupported business/lab facts abstain; fabricated numeric facts, unsafe output, and fabricated source markers are rejected before any text is emitted.
- Sync and SSE routes call the same pipeline. SSE sends only the final validated answer as one delta, sends response metadata first, emits one terminal `done`, and does not forward provider deltas directly.
- Added signed session cookies, invalid-cookie replacement, reset rotation, per-session async serialization, and session-isolation tests. Upstash storage failures and malformed history no longer silently become empty history.
- Sanitized provider status, timeout, malformed-payload, and stream-error paths. Mock tests verify private provider response text and token-like values do not escape.

### Baseline and development evidence

- Baseline before P2 changes: `docs/progress/evidence/phase2-baseline-20261002.md`. At base `6f7ae8c`, the existing API/scope suite passed 15 tests; an opening-hours FAQ and `Should I be concerned?` without the new follow-up routing were outside scope; B01 and B03 remained historical NOT_RUN items.
- Focused P2 checks passed during development, including routing, knowledge provenance, retrieval, citation/abstention, API sync/SSE, sessions, provider errors, store errors, and script entrypoints.
- `rtk .\\.venv\\Scripts\\python.exe -m pytest -q`: **PASS, 102 passed**, one existing Starlette/httpx deprecation warning.
- `rtk pwsh -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File .\\scripts\\check.ps1`: **PASS**, compileall and 102 tests.
- `rtk .\\.venv\\Scripts\\python.exe scripts\\evaluate_retrieval.py --mode synthetic`: **PASS, 5/5** on the isolated synthetic development set. Method is `lexical-char-ngram-v1`; this is not semantic embedding quality evidence.
- `rtk .\\.venv\\Scripts\\python.exe scripts\\build_index.py --mode synthetic`: **PASS**, 3 synthetic records, `demo=true`.
- `rtk .\\.venv\\Scripts\\python.exe scripts\\build_index.py --mode release`: **BLOCKED**, `release_not_ready`; no synthetic fallback.
- `git diff --cached --check`: **PASS** before the implementation checkpoint. No staged whitespace errors.

## Live provider and embedding evaluation

**BLOCKED / NOT_RUN.** No API key, provider credential, `.env` value, or private token was read or saved. All provider behavior evidence is mocked/local contract evidence. There is no claim of Thai LLM quality, semantic embedding quality, live latency, or provider capability. The next live run requires owner-approved authorization and credentials that can be used without exposing or persisting secrets.

## Approved-data and release readiness

**G1-data remains BLOCKED.** The working corpus still has zero release-eligible owner-approved sources and zero release services. Structural validation passing means only that the pending/development corpus is well-formed. `validation/validate_corpus.py --mode release` exits 1 with the existing owner-source, FAQ, policy/education, and quantity blockers. The synthetic index and synthetic fixture are explicitly non-release and are not business approval.

## Independent review

**NOT_RUN.** The standard helper was invoked once under the verified PowerShell Core runtime with IMPLEMENT MaxPlus and configured REVIEW O1. IMPLEMENT run `8a3cc240cca8468fb210735468d4e60f` started but did not produce a handoff; its child environment repeatedly failed to resolve the repository Python command after tool-read attempts. MAIN stopped that same run through the canonical stop route. The helper then terminated with a finalization error because the run had already been removed; no REVIEW receipt or independent inspection exists. The unchanged launcher was not retried, and no global Agent Kit/account settings were changed.

Configured accounts are distinct (`MAIN/IMPLEMENT=MaxPlus`, `REVIEW=O1`), so no same-account independence reduction is claimed. Actual reviewer inspection is nevertheless absent. MAIN performed a separate non-independent self-review of the exact staged diff, resolved the script-import and explicit-chunk-ID issues, and reran the tests. This self-review is not a substitute for O1 approval.

## Remaining blockers and next action

- Obtain owner-approved public source snapshots, permissions, facts, FAQ/policy/education content, and service quantity evidence before attempting release readiness or G1-data closure.
- Restore an inspectable authorized O1 review path before claiming independent review. Do not treat a future receipt as approval unless the worker inspected this exact candidate.
- Run live provider/embedding evaluation only after explicit authorization and credential-safe handling.
- Do not start Phase 3, Vision/OCR, UI redesign, runtime RAG deployment, or release publication from this checkpoint.

## Dated coursework demo integration addendum — 2026-10-02

This addendum records the owner-authorized local integration from base checkpoint `21f14f541a99f7271f99810390ba21bea550dd59`. It does not revise the historical G0 or G1-data claims above.

### Scope and source audit

- The checked package `docs/coursework-demo/ResultScope_Coursework_Demo_v1/` contains 19 files including its checksum list; the 18 files listed by `CHECKSUMS.json` were verified with **18/18 SHA-256 values matched**. `CHECKSUMS.json` is not self-hashed. The four `SOURCE_MANIFEST.json` canonical corpus sources were separately verified before loading.
- Only `corpus/01_BUSINESS.md`, `corpus/02_POLICIES.md`, `corpus/03_READING_GUIDE.md`, and `corpus/04_SERVICES.md` are indexed. `corpus/services.json` is checked for checksum/schema/equivalence only; it is not indexed as a second service source.
- README, integration prompt, source manifest, evaluation questions/expected answers/holdouts/safety cases, checksum file, and all images remain outside the index. Vision/OCR and Phase 3 were not started.

### Implementation and gates

| Gate | Status | Evidence |
|---|---|---|
| Historical G0 | **BLOCKED** | Preserved from earlier reports. |
| Working-corpus structural validation | **PASS** | Existing `validation/validate_corpus.py`; demo loader adds manifest/path/checksum/representation checks. |
| Coursework demo readiness | **PASS for isolated local synthetic demo** | `promptlab-synthetic-v1`; 15 services plus business/policy/reading records; isolated synthetic index has 21 records. |
| Instructor acceptance | **PENDING** | Demo README states fictional-business acceptance remains pending instructor confirmation. |
| Real-business release readiness / G1-data | **BLOCKED** | Release source/catalog gates remain unchanged; release index build exits 1 and never falls back to demo. |
| Live provider/embedding | **NOT_RUN** | The evaluator uses a local mocked provider and makes no live call. |
| Independent REVIEW | **NOT_RUN** | The configured IMPLEMENT run stalled after source inspection, was stopped once, produced no handoff, and no REVIEW route was started. |

### Behavior and evidence

- Existing `synthetic` routing/index/session/cache behavior is reused. Demo metadata identifies `data_class=synthetic`, corpus version, and the Thai notice `ข้อมูลธุรกิจสมมติสำหรับการเรียน ไม่รับบริการจริง` in API responses and the page header.
- Citations resolve to `DEMO-BUSINESS`, `DEMO-POLICIES`, `DEMO-READING`, or `DEMO-SERVICES` with the verified source version/checksum and record/chunk IDs. Null preparation/specimen/turnaround fields abstain instead of being invented; unknown services abstain before provider invocation.
- Q09 is evaluated as two prior turns plus a separate final follow-up question. Retrieval uses the stored history for that contextual follow-up and does not rely on a textual “after asking A” marker.
- Retrieval-only plus mocked coursework evaluation: **10/10 mandatory and 5/5 holdout**. This is not live-provider or production-quality evidence.
- `.venv\\Scripts\\python.exe -m pytest -q`: **110 passed**, one existing Starlette/httpx deprecation warning.
- `scripts/check.ps1`: **PASS**, compile check and 110 tests.
- `scripts/build_index.py --mode synthetic`: **PASS**, 21 records, `demo=true`, output `data/indexes/synthetic-promptlab-synthetic-v1.json`.
- `scripts/build_index.py --mode release`: **BLOCKED**, exit 1, `release_not_ready`.
- `git diff --check`: **PASS**; line-ending warnings are Git normalization notices only.

### FO limitation and exclusions

The canonical FO helper was invoked once with the bounded IMPLEMENT and fresh O1 REVIEW packets. IMPLEMENT run `f8b777b32222428696b4dc51ce6bc977` stalled after reading repository/source context, made no worktree changes, and was stopped through `stop-route.ps1`; no review handoff or independent inspection exists. No receipt is treated as approval, no global Agent Kit/account settings were changed, and the launcher was not retried unchanged. MAIN performed the authorized implementation and local verification only.

No credentials, `.env` values, live provider calls, deployment, push, Vision/OCR, UI redesign, Phase 3, or release approval were performed.
