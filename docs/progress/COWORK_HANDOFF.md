# Cowork handoff — ResultScope full business completion

Started 2026-10-06 (Asia/Bangkok). Owner brief: `ResultScope_Claude_Cowork_Master_Prompt_TH.md` (pack `ResultScope_Cowork_Launch_Pack_20261006`).
This file is the resume point. Read it first; do not restart planning, reset budgets or reuse historical PASS results as new evidence.

## Environment (observed)

| Item | Observed value |
|---|---|
| Workspace | Isolated Linux cloud container (Claude Cowork cloud session), not the owner's Windows host |
| Repo | `https://github.com/siriponsri/ResultScope`, branch `main` |
| Base commit | `ff1b2f7d36d93303f51040027996fb539b1e3eba` ("feat: replace ResultScope with full business app baseline"), a fast-forward from `4ac870a` |
| Starter identity | 654 of 655 `DELIVERY_MANIFEST.json` hashes match; `docs/business-v3/tests/results_template.csv` differs only by CRLF→LF (1917→1843 bytes) |
| Starter commits `35c7430`/`2069389` | Not present in the GitHub history (the owner imported the starter as one commit) |
| Python | 3.12.3 in `/home/claude/venv` (repo pins 3.12) |
| Node / Playwright | Node 22.22.0, playwright 1.56.1, Chromium build 1194 preinstalled |
| Git | 2.43; pushing is not authorised by the owner for this task |
| Network | fastwork.com, api.opentyphoon.ai, openrouter.ai and drive.usercontent.google.com are **blocked** by the sandbox egress policy |
| Owner computer link | Requested by the owner (`C:\Users\siripon.sri\Desktop\my_project\ResultScope`), **not linked yet** in this session |
| Budget | Owner states 0 THB spent so far of the 300 THB project total |

## Round A — baseline on `ff1b2f7` (actually run, this container)

| Check | Result | Evidence |
|---|---|---|
| `compileall` main/config/routers/services/tests | PASS | console |
| `pytest -q` | PASS — 344 passed, 1 warning, 19.8 s | `docs/evidence/cowork-20261006/baseline/pytest-baseline.xml` |
| `scripts/verify_medical_sources.py` | PASS — 58 runtime records, 68 source URLs, 0 network calls | console |
| `npm run uat:business` (`TEST_PYTHON` = venv) | PASS — 16/16, LLM/OCR doubles | `docs/evidence/cowork-20261006/baseline/browser-uat-baseline.json` |
| `scripts/check.ps1` | NOT_RUN — Linux container | — |

Note: `tests/browser/uat.cjs` overwrites `docs/business-v3/evidence/*` (historical evidence). The baseline run was restored with `git checkout` on those files. New runs write to a candidate-specific folder instead (see Round E).

## Gap map (baseline `ff1b2f7`)

| Core | Capability | Status | Notes |
|---|---|---|---|
| A | Guest session, register, login, logout, CSRF, ownership | IMPLEMENTED_OBSERVED | pytest + browser |
| B | Catalog listing (18 packages) | IMPLEMENTED_OBSERVED | |
| B | Search / filter / sort / compare / package detail | MISSING | Home shows 3 cards; workspace lists all with "Discuss" only |
| C | LLM chat, multi-turn, citations, stop | IMPLEMENTED_NOT_VERIFIED | Only doubles; live NOT_RUN |
| C | Retry after error, THB cost ledger, budget status | MISSING / PARTIAL | Call-count cap only; no THB accounting; R12 says "monthly" |
| D | Report upload, review, confirm, compare, delete | IMPLEMENTED_OBSERVED (doubles) | OCR quality NOT_RUN |
| E | Multi-branch slots, capacity, idempotency | PARTIAL | `/slots` hard-codes 3 instead of branch capacity |
| E | Request → staff confirmation | MISSING | Customer confirmation creates a `confirmed` booking immediately |
| E | Direct booking form outside chat, `.ics` | MISSING | |
| F | Organization intake form | MISSING | Only via chat/handoff |
| F | Quote versions, downloadable quotation file | MISSING | Single offer, no file |
| G | Website handoff, claim, reply, bot pause/resume, close | IMPLEMENTED_OBSERVED | two sessions in browser UAT |
| H | Notifications from events | MISSING | Toasts only |
| I | Manager price/active edits persist and reach LLM | IMPLEMENTED_OBSERVED (API) | |
| J | Help / privacy / sources pages; footer links | MISSING | Footer links to `/settings` only |
| — | Payment simulator (pending/success/failure/expiry/cancel/refund) | MISSING | Stripe test mode only, needs keys |
| — | LINE simulator through the same adapter | PARTIAL | Adapter real; no simulated transport |
| — | Server-owned integration mode labels | MISSING | |
| — | Fastwork `/selling` observation | BLOCKED | Sandbox egress; waiting for computer link |

## Reconciliation decisions

1. Budget: R12 "<=300 THB monthly" → **300 THB total until coursework submission** (owner decision 2026-10-06).
2. Booking: owner requires staff confirmation → customer submission now creates `requested`; staff confirms/declines. One legacy test assertion updated accordingly.
3. UI reference: Fastwork `/selling` replaces Bloom/Genomic as primary inspiration; Bloom/Genomic become secondary history.
4. AGENTS.md "push main to origin" closeout is overridden by the owner's no-push instruction for this task.
5. OpenThaiLLM: identity unconfirmed by owner; adapter stays disabled and labelled unconfirmed.

## Progress log

- 2026-10-06 Round A complete (baseline, gap map). Skills repos pinned for manual reference (see `docs/skills/SKILLS_LOCK.json`).

## Update 2026-10-06 (afternoon): v4 design and back office

- Commits (local only, not pushed): `229d762` v3 workspace, staff customers and payments, answer receipt, value rulers, inline citations, HTML 404; `38f037e` v4 light/dark design system.
- Owner direction: Vertex-style minimal UX with light and dark themes, purple used sparingly; Hallmark and skillui installed. Vertex and X Fitness could only be read as text (egress proxy blocks both hosts; the computer was not linked). See `docs/design/VERTEX_REFERENCE.md`, `docs/design/XFITNESS_BENCHMARK.md`, `docs/design/HALLMARK_AUDIT.md`.
- Verification: pytest 386 passed; browser UAT 27/27 (`docs/evidence/cowork-20261006/browser-v4`); approval bundle 58 screens per theme with no page errors or overflow (`tests/browser/screens.cjs`, sheets in `docs/evidence/cowork-20261006/screens-v4`).
- Root cause found for earlier unexplained UAT failures: the UAT attached to an already-running server on port 8098 and tested its old database. `uat.cjs` now refuses to run when the port is taken.
- Real defects fixed in this cycle: composer pushed below the fold in long conversations (flex sizing), conversation not scrolled to the latest turn, booking preview showing a center code, empty report label after confirmation, website 404 returned JSON, inline `[source-id]` markers shown raw.
- Still open: connected Typhoon/OpenRouter evaluation (NOT_RUN), visual Fastwork/Vertex inspection (needs the owner's computer or screenshots), deploy guide and source ZIP.

## Update 2026-10-06 (evening): v5, AI Lab Report product, Atlas Vector Search

- Owner directions: (1) follow the Vertex PDF and screenshots more closely with rich motion; Three.js and Next.js allowed; commit and push allowed; an operating and deployment manual instead of approval images. (2) Sell the AI chatbot that reads lab results as a second product next to health-check packages: Lab Report, personal lab dashboard, Gmail sign-in with a self-chosen password, and a 355 THB subscription for results over time and readings of more than one image. (3) Deploy on Render following the "AI chatbot with LangChain and MongoDB" tutorial for full RAG. (4) No single word alone on a last line.
- Interpretations stated to the owner: "login with Gmail" = register with a Gmail address and your own password (already supported); Google OAuth is NOT_BUILT because it needs the owner's Google client. Subscription = ResultScope Plus, 355 THB per 30 days, test payment through the signed simulator, no auto-renewal. Free = one AI reading of one image. The Render tutorial's Node app is not adopted; its MongoDB Atlas Vector Search pattern is added to the existing FastAPI retrieval as a ranking adapter (IDs only, hash-checked against the verified catalog, off by default). Next.js was not used.
- Commits: `c4eb4c9` plans, entitlements, Lab Report and trends API, multi-image reads, Atlas adapter and indexer; `4d37a37` v5 website and workspace; then docs and evidence.
- Verification: pytest 402 passed; browser UAT 29/29 on `4d37a37` with a clean tree (`docs/evidence/cowork-20261006/browser-v5`, UI-26 Lab Report flow, UI-27 v5 website); automated one-word-line check: 0 across 10 site pages at 7 widths and 10 workspace pages at 3 widths. Atlas, embeddings and live OCR: NOT_RUN (no credentials used; tests use doubles).
- Push: `git push` from this cloud session was refused by the session's repository policy (repository not in the authorized set). Before handing over, a scan of the unpushed commits found `data/business.key` (the local business-data encryption key) committed by an earlier commit. The commits were rebuilt on branch `main-clean` without that file, and `.gitignore` now lists it. Push `main-clean`, not the session's old `main`. The owner received a git bundle of `main-clean`.
- Operating and deployment manual (Claude Doc): Atlas vector search on Render, Plus operations, smoke test and verification results added.
- Still open: connected model evaluation (NOT_RUN), Google OAuth (NOT_BUILT), real payment provider (simulator only), Atlas cluster creation and first indexing (owner action, see the operating manual).
