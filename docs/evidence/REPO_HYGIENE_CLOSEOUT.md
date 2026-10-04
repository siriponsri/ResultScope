# Repository Hygiene Closeout

Status: candidate reviewed; local integration and push remain the final MAIN actions.

## Candidate and scope

- Audited starting HEAD: `44ff6b95d6493df062e786791cbdfd66bf352549`.
- Application candidate: `aac1200c07790890a55dcfd066a8b32d806df549`.
- Evidence/manual candidate before this closeout fix: `b289518d073c5b2da109c9e583c56161c3c69b1b`.
- Branch: `codex/resultscope-restructure-20261004`.
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
| `git diff --cached --check` | PASS | Run before both commits |
| Isolated browser capture | PASS | Temporary loopback `127.0.0.1:8787`; 16 captures; zero overflow, JS errors, and external browser requests; desktop and 390px mobile interactions passed |
| User manual rebuild | PASS | `scripts/build_product_manual.py`; 14 steps |
| PDF export | PASS | `scripts/export_product_manual.cjs` with the installed Playwright module and local Chrome |
| Coursework evaluator | BLOCKED | `6/10` mandatory and `5/5` holdout; retrieval-only plus mocked provider; exit `1`; release readiness remains `BLOCKED` |
| Full `scripts/check.ps1` | NOT_RUN | The script attempted dependency installation despite an existing venv; it was stopped and the existing-venv equivalent compile/test check was run instead |
| Live providers | NOT_RUN | `PROVIDER_NETWORK_ENABLED=false`; no LLM, OCR, SystemOne, models, key-save, or new-cycle call |

The capture manifest records its source fingerprint, offline conditions, and
candidate metadata. Mocked OCR/SSE stages remain visibly labelled and are not
live validation. The isolated server and temporary settings/ledger paths were
stopped and removed. Owner port `8765`, `.env`, keys, sessions, databases,
ledgers, and the locked `C:\Users\User\orca\workspaces\ResultScope\cod`
directory were not touched.

## Independent review

Fresh configured O1 REVIEW inspected exact candidate `b289518` through the
headless read-only route `c7ef6167f0744bb9868bc84660d8e796`. Account
independence was present: MAIN/IMPLEMENT MaxPlus and REVIEW O1. The review
reported two findings: this closeout file was missing/broken-linked, and the
capture manifest did not identify the final evidence candidate precisely. Both
are addressed by this closeout change and the manifest update; a fresh O1
review of the resulting candidate is required before integration.

## Git closeout

- Branch merge into local `main`: pending MAIN integration after fresh review.
- Local branch deletion and clean auxiliary worktree deletion: pending; only
  the completed in-scope branch/worktree may be removed.
- Commit and normal `git push origin main`: pending MAIN integration.
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
