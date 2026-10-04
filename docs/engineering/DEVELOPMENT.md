# Development guide

Work from the current `AGENTS.md`, [product contract](../../PRODUCT.md), and [design system](../../DESIGN.md). Keep the root `main.py` FastAPI entry point, lightweight HTML/CSS/JavaScript stack, inspectable Python rules, and Windows-friendly workflow.

## Set up without changing local state

Use [local setup](../operations/LOCAL_SETUP.md). Preserve `.env`, any existing Windows `.venv`, local settings, and provider ledgers. Use a separate non-Windows environment outside the repository if needed. Set `PROVIDER_NETWORK_ENABLED=false` in the process used for development and tests. Explicitly select local SQLite when an existing environment may have external storage configured.

Do not add a new provider, change keys, open a budget cycle, call a live endpoint, deploy, or treat a catalog entry as verification merely to complete a UI task.

## Where to make changes

| Change | Primary files | Related checks |
|---|---|---|
| Page structure | `templates/index.html` | `tests/test_phase5_ui.py`, actual browser inspection |
| Landing and report drawer | `static/js/experience.js` | Native scroll, modal focus, reduced-motion/no-GSAP fallbacks; no provider transport |
| Shared visual system | `static/css/tokens.css`, `style.css`, `admin.css` | Keyboard, responsive layout, legibility, reduced motion |
| UI behavior | `static/js/chat.js`, `static/js/admin.js` | API contracts, browser state/error/reset checks |
| Scope and ranges | `services/lab_scope.py`, `lab_parser.py`, `deterministic_engine.py` | Scope, parser, deterministic-engine tests |
| Knowledge and references | `services/knowledge.py`, `retrieval.py`, `public_reference.py`, evidence addon | Corpus, retrieval, public-reference tests |
| Answer validation | `services/answer_service.py`, `output_validation.py` | Safety, answer, public-reference, API tests |
| Images | `routers/images.py`, `services/image_extraction.py`, `vision_client.py`, `extraction_store.py` | Image, vision, safety, session tests |
| Provider limits | `services/provider_budget.py`, provider clients/adapters | Budget, boundary, runner tests |
| Administration | `routers/admin.py`, `services/admin_auth.py`, `provider_config.py` | Admin-settings and provider-boundary tests |

A significant behavior change needs a meaningful regression test for the changed boundary. Avoid tests that merely reproduce an implementation detail. The browser displays server-owned flags; do not move scope, range, or safety decisions into JavaScript.

## Verification workflow

Run the required Windows repository check after the candidate is complete:

```powershell
$env:PROVIDER_NETWORK_ENABLED = "false"
$env:STORAGE_BACKEND = "sqlite"
powershell -ExecutionPolicy Bypass -File .\scripts\check.ps1
```

The script installs development requirements, runs `compileall`, and executes pytest. From an existing compatible non-Windows environment, the component checks are:

```bash
python -m compileall -q main.py config.py routers services tests
PROVIDER_NETWORK_ENABLED=false STORAGE_BACKEND=sqlite python -m pytest -q
node --check static/js/chat.js
node --check static/js/admin.js
git diff --check
```

Mock provider verification is available through `python scripts/provider_verification_runner.py` with provider transport disabled. Its default is mock-only; do not add `--live`. The pinned vendor check is `python vendor/resultscope_evidence_v1/verify.py`; the synthetic coursework evaluator is `python scripts/evaluate_coursework_demo.py --provider mocked`. Fixture comparisons measure only those fixtures.

Then inspect the actual UI on desktop and a narrow mobile viewport: text intake, laboratory follow-up, unrelated refusal, image validation/review, unavailable-provider state, sources, reset/retry, keyboard focus, and reduced motion. Keep synthetic examples labelled. If a stage requires a mock, state that in the evidence caption. Never report a screenshot as a live-provider check.

## Evidence and source integrity

Record the candidate identifier, command, exit code, test count, warnings, and any unavailable checks. An earlier passing count does not transfer to a later source tree. Exact final independent review remains a separate gate from local tests.

Knowledge manifests bind byte-level source snapshots. Formatting and line-ending changes can affect checksums. Inspect a mismatch; do not disable validation, automatically bless new content, or alter release eligibility to make a check pass. Preserve historical source bytes and provenance during cleanup. Follow [repository cleanup](REPOSITORY_CLEANUP.md) for the packaged migration and hash-guarded removal procedure.

## Security and product invariants

- Keep secrets server-side and out of logs, browser responses, fixtures, screenshots, and Git.
- Treat retrieved context and provider output as untrusted data.
- Bind attributed source IDs and URLs to retrieved evidence; keep validation fail-closed.
- Require image correction/confirmation before using extracted fields as confirmed context.
- Preserve local refusals for unrelated, unsafe, or unsupported claims.
- Keep SystemOne shadow-only, Clef off, and local provider guard/ledger behavior intact.
- Keep future HIS/pharmacy interfaces in the roadmap until their contracts and scope exist.

For visual changes, update both `DESIGN.md` and `.impeccable/design.json` from the actual implementation. For runtime changes, update the specific guide and source map that describes them. Retained historical reports are evidence, not documents to rewrite into a new success narrative.
