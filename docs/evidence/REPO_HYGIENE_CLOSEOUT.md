# Repository Hygiene Closeout

Status: O1 reviewed; local integration, commit, and normal push are complete.

## Candidate and scope

- Audited starting HEAD: `44ff6b95d6493df062e786791cbdfd66bf352549`.
- Application candidate: `b7d7f68dcb0787ada9d0196f517b061b4d29d62d`.
- Reviewed evidence/manual candidate: `dd323acc00237b4ab2472c5052aa068e15620dd3`.
- Current documentation-alignment candidate: `1d90492c15244241ad22586365b8cea085219e88`.
- Integration branch: `codex/resultscope-restructure-20261004` (fast-forwarded into local `main` and deleted).
- Scope: relocate the pinned evidence and synthetic coursework bundles, update active consumers and guidance, untrack regenerable synthetic indexes, refresh documentation captures/manual, and preserve offline/provider safety.

The two bundle moves are unit-preserving. A Git-archive comparison against the
audited starting tree found matching relative paths and SHA-256 bytes for
`87/87` files in `vendor/resultscope_evidence_v1/` and `19/19` files in
`examples/coursework_demo_v1/`; content mismatches: `0` in both bundles.

## Changes

| Retired or changed path | Maintained destination or result | Evidence |
| --- | --- | --- |
| `addons/resultscope_evidence_v1/` | `vendor/resultscope_evidence_v1/` | Complete path/byte comparison; package verifier passed earlier in this cycle |
| `docs/coursework-demo/ResultScope_Coursework_Demo_v1/` | `examples/coursework_demo_v1/` | Complete path/byte comparison; evaluator uses the new path |
| `scripts/` cleanup utilities and old local closeout | `docs/archive/product-refresh-v2/` | Retained as labelled historical records, not supported commands |
| `data/indexes/synthetic-*.json` | Removed from Git index and ignored | Local files were preserved; source remains under `knowledge/` |
| Capture/manual artifacts | Refreshed under `docs/assets/screenshots/`, `docs/user/`, and `static/docs/` | 16 captures, 14 manual steps, PDF export |

Active imports, defaults, tests, evaluator paths, `.gitattributes`, and the
narrow exact legacy default alias were updated. Arbitrary custom public-reference
roots still fail closed. No bundle checksum or source content was rewritten.

## Verification evidence

| Check | Result | Notes |
| --- | --- | --- |
| Focused Python compile/test | PASS | `227 passed, 1 warning` using the existing `.venv`; warning is the existing Starlette/httpx deprecation |
| Bundle preservation | PASS | `87/87` vendor and `19/19` example paths and bytes; `0` mismatches |
| `git diff --cached --check` | PASS | Run before each commit |
| Isolated browser capture | PASS | Temporary loopback `127.0.0.1:8787`; 16 captures; zero overflow, JS errors, and external browser requests; desktop and 390px mobile interactions passed |
| User manual rebuild | PASS | `scripts/build_product_manual.py`; 14 steps |
| PDF export | PASS | `scripts/export_product_manual.cjs` with the installed Playwright module and local Chrome |
| Full `scripts/check.ps1` | PASS | Reproduced from a disposable clean checkout at `1d90492`; `227 passed, 1 warning`, exit `0` |
| Vendor package verifier | PASS | `50` tests passed from `vendor/resultscope_evidence_v1/` |
| Corpus/index/import checks | PASS | Structural corpus validation passed; synthetic index built `21` records; imports found `21` synthetic and `29` public-reference records |
| Clean-checkout startup smoke | PASS | Isolated `127.0.0.1:8787`: `/health`, `/`, and `/static/docs/user-guide.html` returned `200`; owner port `8765` remained untouched |
| Coursework evaluator | BLOCKED | `6/10` mandatory and `5/5` holdout; retrieval-only plus mocked provider; exit `1`; release readiness remains `BLOCKED` |
| Live providers | NOT_RUN | `PROVIDER_NETWORK_ENABLED=false`; no LLM, OCR, SystemOne, models, key-save, or new-cycle call |

The capture manifest records its source fingerprint, offline conditions, and
candidate metadata. Mocked OCR/SSE stages remain visibly labelled and are not
live validation. The isolated server and temporary settings/ledger paths were
stopped and removed. The clean-checkout evaluator writes its evidence artifact
as part of evaluation; that generated change was not copied into this
repository. Owner port `8765`, `.env`, keys, sessions, databases, ledgers, and
the locked `C:\Users\User\orca\workspaces\ResultScope\cod` directory were not
touched.

## Independent review

Fresh configured O1 REVIEW inspected exact candidate `dd323ac` through the
headless read-only route `0172f99a227e481fad72a3b1b745ea5e` and returned PASS
with no new specification or standards findings. Account independence was
present: MAIN/IMPLEMENT MaxPlus and REVIEW O1. The review verified exact
capture timing, application fingerprint, both bundle moves, active path
references, protected-state exclusions, provider guard, clean status, and
`git diff --check`. It did not rerun tests or browser capture; those receipts
remain recorded above.

## Git closeout

- Branch merge into local `main`: performed as a fast-forward after fetching and
  inspecting `origin/main`.
- Local branch deletion and clean auxiliary worktree deletion: performed for
  `codex/resultscope-restructure-20261004` and its clean auxiliary worktree.
- Final closeout commit and normal `git push origin main`: performed by MAIN
  immediately after this report is staged; final SHA and remote parity are
  recorded in the user handoff and Project Brain.
- Force push, deployment, migration, remote branch deletion, and unrelated
  worktree changes: not performed and not authorized.

## Remaining blockers

Coursework completeness, approved corpus/rights, online provider contracts and
quality, durable cloud secrets and distributed quota controls, production
operations, human usability validation, clinical validation, PDF OCR, and
future HIS/pharmacy integrations remain blocked or not run. This closeout does
not claim production, clinical, or release readiness.

Next proposed task: a separately authorized bounded manual API connection
cycle with an explicit provider, input set, attempt budget, stopping condition,
and sanitized receipt. It is not executed here.
