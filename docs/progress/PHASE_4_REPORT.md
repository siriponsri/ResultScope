# Phase 4 Report

สถานะ: DOCUMENTED LOCAL CLOSEOUT; local controls verified, fallback review NOT_READY, independent O1/O2 gate unavailable

- Phase / date / MAIN / IMPLEMENT / REVIEW: Phase 4 / 2026-10-03 / MaxPlus / MaxPlus (dispatch timed out; MAIN completed bounded fallback) / O1 configured but unavailable at final review; O2 owner-authorized fallback also unavailable
- Baseline SHA / final local SHA / integration SHA: `80e7a5986141d96db0d52f1c0a8f629476e6543c` / `d280bd2b3bf048225ea70a3da15bcb982a5ba2da` / `d280bd2b3bf048225ea70a3da15bcb982a5ba2da`
- Corpus version / prompt-policy version / model-provider: synthetic `promptlab-synthetic-v1` for tests; deterministic rulebook `2026.08`; provider calls mocked or unavailable only
- Scope completed / deferred: Phase 4 trust/output/session/resource/rendering controls completed locally; live-provider quality, external guard, authentication, and Phase 5 deferred

## Work items

| ID | Status | Changed files/commit | Acceptance evidence | Open issue |
|---|---|---|---|---|
| P4-F01 threat model | VERIFIED | `docs/security/THREAT_MODEL.md` | Assets, boundaries, attacks, controls, and residual risk map to P4 cases | Not a certification |
| P4-F02 input policy | VERIFIED | `services/intent_router.py`, `services/answer_service.py` | Privileged business request refuses before provider; normal price wording remains supported | More language variants need future evaluation |
| P4-F03 output validation | VERIFIED | `services/output_validation.py`, `services/answer_service.py`, `routers/chat.py` | Forged citation syntax/case/attribution, day-bound canonical hours, canonical booking claims, unsupported business numbers/concepts, definitive diagnosis wording, unsafe clinical output, and sync/SSE parity tests pass | Mocked provider cannot prove live model behavior |
| P4-F04 session/ownership | VERIFIED | Existing session/extraction routes plus regression coverage | Foreign extraction and reset isolation tests pass | No authentication/patient identity layer |
| P4-F05 resource controls | VERIFIED | `config.py`, `services/request_limits.py`, `routers/chat.py`, `services/llm_client.py` | Message/history/output bounds, timeout, image limits, and sync/SSE rate-limit tests pass | Rate limiter is process-local; shared limiter required for multi-instance deployment |
| P4-F06 XSS/error/log hygiene | VERIFIED | `static/js/chat.js`, `services/llm_client.py`, `routers/chat.py` | Sanitized/escaped browser probe has zero unsafe nodes; friendly errors contain no provider payload | Browser CDN failure fallback is only escaped text |
| P4-F07 adversarial evaluation | VERIFIED locally | `tests/test_phase4_safety.py`, evidence file | Exact S01-S05 plus forged output, benign hours, medication/diagnosis, sync/SSE, timeout, reset-failure, and rate-limit cases PASS | Live provider cases NOT_RUN |
| P4-F08 guard adapter decision | VERIFIED | `docs/security/ADR-GUARD.md` | Deterministic guard is mandatory; optional external guard is fail-closed and not installed | Revisit before production |

## Verification

| Command/case | Environment | Actual result/exit code | Mock or live | Evidence path |
|---|---|---|---|---|
| `.venv\\Scripts\\python.exe -m pytest -q` | Windows local `.venv` | `161 passed`, exit 0, 1 existing warning | deterministic + mocked | `docs/progress/evidence/phase4-after-20261003.md` |
| Focused coursework/Phase 4 tests | Windows local `.venv` | `41 passed`, exit 0, 1 existing warning | deterministic + mocked | same evidence |
| `scripts/check.ps1` | Windows local `.venv` | PASS, exit 0; includes `161 passed` | deterministic | same evidence |
| `node --check static/js/chat.js` | Node 24.19.0 | PASS, exit 0 | local | same evidence |
| `git diff --check` | Git local | PASS, exit 0 | local | final closeout command |
| Desktop/mobile browser | System Chrome via external Playwright | PASS; no horizontal overflow | mocked/local, no live provider | `docs/progress/evidence/phase4-browser-20261003/` |
| Reset failure browser probe | System Chrome via external Playwright | PASS; current analysis remained visible and error was shown after mocked HTTP 503 | local UI route mock | `docs/progress/evidence/phase4-after-20261003.md` |
| SSE error terminal browser probe | System Chrome via external Playwright | PASS; mocked error followed by `done` kept `has-error`, cleared loading, and did not mark the response complete | local UI route mock | `docs/progress/evidence/phase4-after-20261003.md` |
| Truncated SSE terminal browser probe | System Chrome via external Playwright | PASS; mocked error without `done` cleared loading, preserved `has-error`, and did not mark the response complete | local UI route mock | `docs/progress/evidence/phase4-after-20261003.md` |
| Live LLM/Vision/guard | owner-constrained | NOT_RUN | live | explicitly recorded above |

## Review

The canonical combined dispatch produced IMPLEMENT run
`561dad86bd0d4b69a1dd72d820abe3f3`, `TIMED_OUT`, exit `-1`, with diagnostic
`Access is denied`; it produced no IMPLEMENT handoff and no review stage. MAIN
did not treat the receipt as approval. A subsequent fresh O1 review
`ae0ac611328447a29a44b5278a991514` succeeded read-only and found four issues:
unsupported claims, reset-failure UI handling, inaccurate mandatory-case
evidence, and benign discount overblocking. MAIN resolved those findings in the
current candidate. The next configured O1 read-only fallback review found four
additional issues: business concept over-acceptance, narrow diagnosis matching,
partial reset erasure, and missing in-scope OCR coverage. MAIN resolved those
too. A third fresh direct O1 review then found citation-marker case handling,
medication/diagnosis wording coverage, and opening-hours numeric validation
issues. MAIN resolved those in the current candidate. The latest direct O1
review session `65404` found four grouped issues covering case-insensitive
forged citation markers, medication-change and diagnosis detection, canonical
opening-hours validation, Thai business claims and service-price association,
unrelated coding requests containing lab keywords, and contradictory
deterministic lab flags. MAIN resolved all of them in the current candidate.
A fifth fresh direct O1 review session `01a0ffd1-2f75-7ab0-8ca0-941d9d67459c`
then found four issues: day-specific opening-hours binding, missed definitive
"kidney disease" diagnosis wording, unbracketed forged source attribution,
and the browser marking an SSE error as complete. MAIN resolved all four in
the current candidate and verified them with focused tests and a targeted
mocked-SSE browser probe. The sixth fresh direct O1 review session
`01a0ffe1-20f5-7e80-a7db-f65bcecd9c2a` then found three issues: unsupported
Thai booking guarantees, incomplete source-ID attribution coverage, and
truncated SSE responses remaining in the loading state. MAIN resolved all three
in the current candidate and verified them with tests and a browser probe. A
seventh independent review could not complete. The canonical dispatcher failed
before worker creation because the loaded PowerShell runtime lacks
`System.IO.Path.IsPathFullyQualified`. Direct O1 review session
`01a1004f-5080-7e72-922e-bc1d9f9b9f92` inspected the candidate but ended at the
configured usage limit before returning findings. Owner-authorized O2 fallback
session `01a10052-e86b-74c1-ac8b-9e5b678fd323` could not authenticate because its
OAuth token was revoked. Two same-host fallback agents also produced no review
result. MAIN completed a serial read-only inspection and found no additional
concrete issue, but this is not an independent approval.

A same-host fallback review by Lorentz (`01a10053-faef-7fd2-8daa-8bdd3d30893f`)
reviewed the final local state read-only and returned **NOT_READY**; it is not
O1/O2 approval. It reported unresolved findings: lab-route output validation
does not apply canonical business-claim and complete citation checks, diagnosis
detection remains fail-open for hedged wording, reset recovery can be discarded
after expiry/pruning, and structured request/audit metadata is absent. The
review reran pytest, focused tests, compileall, Node syntax, and diff checks;
its `scripts/check.ps1` run was NOT_RUN because dependency installation was
prohibited. These findings remain unmodified in this continuation.

## Gate decision

**G4 NOT_CLAIMED.** The local
deterministic/mocked exact mandatory cases and browser safety checks pass, but
full acceptance is not claimed because the fallback review has unresolved
findings and the final independent O1/O2 review could not complete. Live
provider safety remains NOT_RUN and is not silently substituted by mocks.

Historical gates remain unchanged: G0 and G1-data/release readiness are
BLOCKED; G3 remains NOT_CLAIMED. Phase 5 was not started.

## Owner decisions and next step

| Decision | Needed by | Work blocked | Safe parallel work | Owner answer |
|---|---|---|---|---|
| Independent REVIEW on revised exact candidate | Phase 4 closeout | G4 claim and final integration signoff | MAIN serial inspection only | O1 configured; O2 owner-authorized fallback unavailable |
| Remediate Lorentz fallback findings | Before any G4 claim | Lab/business grounding, diagnosis safety, reset recovery, auditability | Documentation only | Application-code changes were not authorized in this continuation |
| Live provider safety run with test credentials/budget | Later authorized evaluation | Live quality claim only | Local tests/docs | NOT authorized this round |
| Shared limiter/authentication for deployment | Before multi-instance/real data | Production readiness | Coursework local demo | deferred |

The implementation remains locally integrated and this report records the
unresolved fallback findings. The next action requires owner authorization for
scoped remediation, followed by regression verification and a fresh
independent O1/O2 review. Project Brain refresh and this documentation commit
remain local-only. No push or deployment is authorized.
