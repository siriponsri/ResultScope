# ResultScope Phase 1 report — business knowledge foundation

Date: **2026-10-02**

## Gate summary

- Historical G0: **BLOCKED**, preserved from Phase 0.
- Phase 1 non-blocked foundation work: **READY_FOR_REVIEW / MAIN-integrated locally**.
- G1-data: **BLOCKED**. No owner-approved public laboratory source pack, real service catalog, approved contact/policy facts, or approved educational corpus is present. No quantity claim was fabricated.
- Runtime RAG, retrieval/indexing, Vision/OCR, UI redesign, Phase 2, provider calls, deployment, credentials, and real business data: **NOT_STARTED / NOT_RUN**.

## Repository and orchestration identity

- Repository: `C:\Users\User\Desktop\myProject\ResultScope`
- Branch: local `main`; no branch/worktree creation, push, deploy, or remote change.
- Base HEAD before Phase 1 work: `4a95899c39b5c045a4dd46576d98e4bf4ee74ae0`.
- MAIN/IMPLEMENT configured account: MaxPlus. REVIEW configured account: O1. Account independence is configured, but the O1 worker could not independently inspect this candidate.
- IMPLEMENT dispatch `e70db769cc954d1ba67bfc6181beeb17`: `TIMED_OUT`, exit `-1`; diagnostic showed `CreateProcessWithLogonW failed: 1326` before a worker handoff or repository write.
- REVIEW dispatch `5c38fac985144c4092fd319a74eb35b4`: terminal receipt `SUCCEEDED`, route `review`, but the worker reported `CreateProcessWithLogonW failed: 1909`, could not inspect the repository, and marked all checks `NOT_RUN`. This is not technical approval.
- MAIN therefore completed the explicitly authorized bounded work and performed a separate non-independent integration audit. No FO worker completion or independent review approval is claimed.

## Work items

| ID | Result | Evidence | Limitation / next gate |
|---|---|---|---|
| P1-F01 | PASS for confirmed/pending brief | `docs/business/BRIEF.md`, `docs/business/OWNER_QUESTIONS.md` | Real identity and operational facts await owner approval |
| P1-F02 | PASS for schema and provenance posture | `knowledge/source_manifest.json`, validator checksum checks | Owner source origin/permission/version/checksum remains pending |
| P1-F03 | PASS for schema/separation; quantity gate BLOCKED | `knowledge/services.json`, `knowledge/fixtures/services.synthetic.json` | Release catalog is intentionally empty; no claim of 15 real services or five source pages |
| P1-F04 | PASS as pending-source FAQ contract | `knowledge/policies/FAQ.md` | All ten topics abstain until approved facts arrive |
| P1-F05 | PASS as draft policy contract | `docs/business/BOT_POLICY.md` | Runtime enforcement belongs to later phases |
| P1-F06 | PASS as frozen pending-source evaluation contract | `evaluation/cases.jsonl` | Actual answers, latency, and live-provider runs remain NOT_RUN |
| P1-F07 | PASS | `validation/validate_corpus.py`, `tests/test_corpus_validation.py` | Future approved corpus must rerun the same checks |

## Validation and test evidence

| Check | Result | Evidence |
|---|---|---|
| Corpus validator | PASS | `rtk .\\.venv\\Scripts\\python.exe validation\\validate_corpus.py`; empty/pending release corpus, isolated synthetic fixtures, 10 mandatory + 5 holdout minimum |
| Focused corpus tests | PASS | `rtk .\\.venv\\Scripts\\python.exe -m pytest -q tests\\test_corpus_validation.py`; 6 passed |
| Project check | PASS | `rtk pwsh -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File .\\scripts\\check.ps1`; compileall and 31 tests passed, exit 0 |
| Diff whitespace check | PASS | `git diff --check`; no content errors; wrapper reported expected LF/CRLF warnings for modified Markdown |
| Secret-like artifact scan | PASS | No token/key/password/bearer matches in Phase 1 artifacts; `.env` and credentials were not read |
| Browser/manual verification | NOT_RUN | Phase 1 makes no UI/runtime changes |
| Provider/live business source evaluation | NOT_RUN | No approved source pack or credential was supplied |

The project check emitted one existing Starlette/httpx TestClient deprecation warning; it did not fail any test.

## Provenance and fixture posture

`knowledge/source_manifest.json` records six sources: three repository/planning references with verified local SHA-256 values, one absent owner source with explicit pending checksum reason, and two non-release synthetic sources with verified checksums. There are zero release-eligible sources and zero release services. The three synthetic service records cannot satisfy the real-service quantity gate.

The FAQ and evaluation cases intentionally use `PENDING_SOURCE`. Expected answers were not generated from a model. The validator rejects missing metadata, bad checksums, duplicate IDs/names, unknown source references, draft/synthetic release sources, human-facing PII patterns, and invalid evaluation counts/references.

## Phase 0 reconciliation carried forward

The historical substantive checkpoint was `576977535f858ef71287361e255d42976eba8f42`; metadata/follow-up commits `1612cc4` and current pre-Phase-1 HEAD `4a95899c39b5c045a4dd46576d98e4bf4ee74ae0` were observed in order. G0 remains BLOCKED. B01 is NOT_RUN because no approved business corpus existed. B03 is NOT_RUN because synthetic-local before inputs and transport trace were not captured in Phase 0; no external or production security testing was attempted. Mobile pipeline clipping remains P5 backlog, and `Should I be concerned?` remains P2 scope/test backlog. P0-F06 is grounded in `AGENTS.md` lines 9–18, 33–43, the architecture direction beginning at line 45, and Project Brain decision `RS-DEC-003`.

## Owner decisions required

See `docs/business/OWNER_QUESTIONS.md`. The blocking decisions are the real laboratory identity, approved public source pack and permissions, operational facts, service catalog, policy facts, approved educational content, and synthetic-fixture disclosure. Schema and validation work can continue without them; G1-data cannot close without them.

## Scope exclusions confirmed

No application source, FastAPI route, runtime store, LLM client, UI asset, `.env`, API key, runtime database, external provider, OCR/Vision path, RAG index, authentication, billing, patient profile, deployment, remote state, or unrelated DR-screening worktree was changed.

## Closeout status

The scoped Phase 1 foundation is ready for owner review and local checkpointing, with G1-data explicitly blocked. A future phase may consume this schema only after owner sources are approved and the same validator passes against the approved corpus.

## Dated correction addendum — 2026-10-02

This addendum records a targeted correction after review of base checkpoint `68b6e256ac074c0714e39aa5c0edd5d69ce936c9`. The implementation and verification claims above describe that earlier checkpoint; the P1-F07 summary and validator behavior are superseded by the evidence below. The historical Phase 0 report and G0 decision were not changed.

### Current gate states

- Structural validation: **PASS**. The pending/development corpus is structurally valid; this result does not imply release readiness.
- Release readiness / G1-data: **BLOCKED**. The working corpus still has zero release-eligible sources and zero release services. Owner-approved source material and the service/policy/education facts remain absent.
- Historical G0: **BLOCKED**, unchanged.
- Independent review of this correction: **NOT_RUN**. The configured roles use MAIN/IMPLEMENT MaxPlus and REVIEW O1, but no independent reviewer inspected this candidate. The accounts are configured separately; actual independent inspection is not established.

### Corrections made

- Parseable empty, null, or non-object manifests and malformed nested records now produce validation errors. Path, URL, enum, and record type failures are guarded and return errors rather than raising unhandled exceptions.
- A local source origin must resolve to an existing file inside the repository root and match its SHA-256. HTTPS origins require `snapshot_path` to an in-root local snapshot; the checksum is verified against those snapshot bytes. A URL or checksum without verifiable local content is insufficient.
- Structural validation and release readiness are separate. FAQ entries may transition from `PENDING_SOURCE` to `APPROVED_SOURCE`. Release readiness requires approved public-business source provenance, source-category references, all ten source-backed FAQ entries, and either at least 15 distinct services or five distinct verified source snapshots. Project instructions, planning references, and synthetic sources cannot be release evidence.
- PII detection remains active. Only top-level `public_business_email` and `public_business_phone` fields are exempt, and only when the linked source is owner-approved, public, release-eligible, and classified `public_business_contact`. Contacts elsewhere or without that provenance remain rejected.
- Q09 now contains separate prior user/assistant messages and a distinct follow-up question. The evaluation source checksum was updated to match the new JSONL bytes.
- Release-positive fixtures are generated only inside isolated temporary test roots; the working synthetic service fixture remains development-only and non-release.

### Verification

- `rtk .\\.venv\\Scripts\\python.exe -m pytest -q tests\\test_corpus_validation.py`: **PASS**, 40 passed.
- `rtk proxy powershell -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File .\\scripts\\check.ps1`: **PASS**, 65 passed; compile check passed. One existing Starlette/httpx deprecation warning remains.
- `rtk .\\.venv\\Scripts\\python.exe validation\\validate_corpus.py`: **PASS** for structural validation; release readiness is reported **BLOCKED**.
- `rtk .\\.venv\\Scripts\\python.exe validation\\validate_corpus.py --mode release`: structural validation **PASS**, release readiness **BLOCKED**, exit code 1 as required for that mode.
- Isolated tests demonstrate passing release paths using synthetic test-only evidence for both the 15-service and five-snapshot quantity alternatives. These test records are not business evidence and do not alter G1-data.
- `git diff --check`: **PASS**. The working-tree change list is limited to the validator, its focused tests, Q09/checksum, this addendum, and the two correction dispatch packets; MAIN owns staging and the local checkpoint.

### FO dispatch limitation

The standard `run-implementation-review.ps1` path was invoked once for the correction and failed in `dispatch-route.ps1` before any route or worker started: the loaded PowerShell/.NET runtime does not provide `System.IO.Path.IsPathFullyQualified`. No IMPLEMENT or REVIEW receipt was created, no global Agent Kit or account setting was changed, and the failing launcher was not retried. MAIN completed only the explicitly authorized local correction and non-independent self-audit. A functioning independent REVIEW remains outstanding.

### Remaining blockers and exclusions

Owner answers and approved public sources are still required before G1-data can pass. No application/runtime behavior, RAG, Vision/OCR, UI, or Phase 2 work was started. Nothing was pushed or deployed.
