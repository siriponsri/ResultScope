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
