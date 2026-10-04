# Build and delivery evidence

Build date: 3 October 2026. Scope: standalone additive extension and local-integration kit.

## Verified

| Check | Actual result | Evidence |
|---|---|---|
| Hospital snapshots/text integrity and tree | PASS: 17 PDFs, 26 numeric records, 17 analytes | source manifest, records, tree, offline-tests.txt |
| WHO supplement integrity and tree | PASS: 2 PDFs, 3 educational notes | guideline manifest, notes, tree |
| Unit and loopback HTTP suite | 50 tests passed; verify.py exit 0 | evidence/offline-tests.txt |
| Fixed retrieval-only comparison | flat 12/15; tree 15/15; exit 0 gates tree | evidence/retrieval-comparison.json |
| Preview desktop/mobile | See exact browser-check.json | evidence/*-home/results/guidance.png |
| Additive installer safety | PASS: fresh/identical install, collision refusal; app bytes and git HEAD unchanged in temporary fixture | evidence/installer-check.json |
| JavaScript syntax | node --check ui/app.js, exit 0 | executed during final verification |

Tests use the pinned local corpus and mocked provider transport. Zero live provider calls. The fixture sets named 'mandatory' and 'holdout' are visible development cases, not independently blinded holdouts. Retrieval comparison is entirely within the extension and is not measured against the user's inaccessible Phase 2/4 runtime.

Browser evidence covers home, source search/details, guideline citation, Enter/Tab operation, reset, empty state, HTTP-error recovery and horizontal overflow at 1440×1000 and 390×844. The browser run used Chromium through Playwright 1.51.0 in an isolated verification environment. Its preview server was terminated after the run. Reproduce with an optional separate Playwright environment and `scripts/verify_ui.py --output OUTSIDE_PACKAGE_DIRECTORY`. This dependency is not needed to run the app preview or offline suite.

## Not verified / remaining work

- GitHub main read during this task is Phase 1 at `68b6e256ac074c0714e39aa5c0edd5d69ce936c9`. Owner reports private local Phase 4 at `b9bc97d`. No attempt was made to overwrite unseen application files with older code.
- Main Phase 4 integration, its reported 172-test suite, check.ps1, Windows execution, OCR/chat/sync/SSE behavior: NOT_RUN here. Tests in this package do not substitute for those gates.
- Live Typhoon, Clef and guard: NOT_RUN. Clef is disabled/shadow only; availability and accuracy are unverified.
- Independent FO review: NOT_RUN. This build used implementation checks, not an invented independent reviewer or FO receipt. Project Brain in the owner's machine was not accessed or updated.
- Real-business approval/catalog/contact/policies remain absent. Hospital manuals and WHO guidelines do not close G1-data. Historical gate statuses are unchanged.
- Public hospital snapshot redistribution/commercial rights unconfirmed; WHO guidance has explicit non-commercial restrictions. Resolve before commercial publication.
- Clinical approval, patient-specific reference selection, real HIS/pharmacy connection and human first-use comprehension study: NOT_RUN / NOT_IMPLEMENTED as applicable.
- No local Windows repo commit, push, deploy or coursework submission was performed.

## What can be shown now

The standalone preview can demonstrate real-source lookup, differing institutional references, Thai educational guideline summaries and source-page traceability without a model key. It does not demonstrate the main app's integrated OCR/chat. MAIN can complete the actual integration on local main using LOCAL_FINAL_GOAL.md and preserve honest blockers in the final local closeout.
