# ResultScope 3 verification

Verified 5 October 2026 UTC. This is engineering verification of a complete coursework source package. It is not live-model, external-integration or clinical approval. The delivered candidate commit and per-file hashes are recorded in the ZIP's DELIVERY_MANIFEST.json. Baseline: 2069389d718c3bacbc6ef4a064a3d618ca96615f.

| Check | Observed outcome | Evidence and boundary |
|---|---|---|
| Clean Python dependency installation | PASS | Fresh Python 3.12 environment; requirements-dev.txt installed. |
| Python compilation | PASS | compileall for main.py, config.py, routers, services and tests. |
| Full Python regression/API suite | PASS — 344 tests | evidence/pytest.txt and pytest.xml; 7.731 seconds in JUnit; one upstream Starlette httpx deprecation warning. No live calls. |
| Browser UAT | PASS — 16 checks | evidence/browser-uat.json plus seven screenshots; real UI/API/SQLite, explicit LLM and OCR doubles. |
| Medical/demo source integrity | PASS | evidence/source-integrity.json; 58 runtime records, 68 discovery URLs; source files and original demo bytes match their manifests. |
| Report layout | PASS — 12 pages | DOCX rendered to PDF; all pages visually inspected, tables and architecture diagram checked. |
| Full-package extraction | PASS; evidence/package-verification.json | CRC, per-file hashes, exclusion rules, source loader and isolated ASGI routes are checked on an extracted candidate. |
| Windows check.ps1 | NOT_RUN | This execution environment is Linux; its install/compile/test steps were run with Linux commands. |
| Real Typhoon/OpenThai/OCR/guard | NOT_RUN | Provider network remained disabled; no fabricated model answers or timings. |
| PostgreSQL/Redis/cloud/LINE/Stripe/Maps | LIVE NOT_RUN | Local adapters and boundary tests are implemented; owner credentials and integration acceptance remain required. |
| LightRAG ingestion and semantic relevance | LIVE NOT_RUN | Export and read-only adapter provided; no hosted index or measured live relevance claimed. |
| Independent FO/security/clinical review | NOT_RUN | No reviewer approval is implied by software tests. |

## What the tests establish

Business tests cover ownership, CSRF, roles and branch restrictions, canonical pricing, stale proposals, explicit confirmation, idempotency, capacity races, payment signatures/amounts, refund terminal states, account linking, job cancellation, encrypted report storage, source separation and failed/stale model drafts. Retained v1/v2 tests cover their separate regression surfaces. Browser checks cover account creation, a chat booking preview, explicit booking, pending center payment, source-image decoding, editable report fields, confirmation, archive/reload, customer-to-staff handoff, staff takeover/reply, manager catalog, keyboard focus, reduced motion and 390px layout.

A final review fixed a financial state issue: repeated center settlement now returns the same receipt; refunded/refund-pending records cannot be repaid by late checkout events, expired events or another center settlement. Seven focused cases were added. A pre-existing legacy test's raw `72` substring check could match a random UUID; it now checks clinical value fields. This was a test false positive, not a reason to weaken field isolation.

The browser OCR double deliberately carries an OFFLINE UI TEST DOUBLE notice and does not represent the supplied image's measured extraction. The fixture server is test-only and never part of the deployment entrypoint. A safe provider-unavailable state is expected without configured credentials; the production code does not synthesize an assistant answer to hide that state.

## Remaining acceptance and submission

The 73-case plan remains a blank execution plan, separate from the completed automated suite. A local agent must record real results for the ten text, six image, five safety and Week 11 guard cases, plus channel/storage/deployment scenarios. Complete three measured before/after improvements. Critical numeric, privacy, authorization or guard failures block acceptance.

Production gaps are explicit: email verification/recovery, account deletion and retention automation, fine-grained clinical roles, independent security/clinical review, load testing, merchant onboarding and provider-side privacy review. Only Stripe test-mode charges are supported. Native Google Docs/Drive submission, student contribution details and the final <=180-second video remain owner/team tasks.

No live inference/OCR spending, real payment, remote push or deployment was performed in this delivery. Preserve existing .env, data, encryption keys and provider ledger when replacing source.
