# Product refresh verification — v2 C + 2

Preparation date: 2026-10-04. This v2 replaces the earlier teal visual direction with the owner-approved purple hero/chat and document drawer. Baseline commit:
`c9236f59b73460ce3c41ba9c87d7cda43d87cee8`.

This is an offline preparation-session candidate, not a commit on the owner's
Windows machine. The delivered payload manifest identifies every replacement file.
The runtime aggregate SHA-256 is `a70ef6e5ef13477d3f9738f299365e28f0c20b00c27f64f46fe267a8ae0bf28f`; see
[RUNTIME_FILE_HASHES.json](RUNTIME_FILE_HASHES.json) for its construction and inputs.
No commit, push, deployment, owner Brain update or local FO review is claimed here.

## Results

| Check | Actual result | Scope and limitation |
| --- | --- | --- |
| Full pytest | **237 passed**, one existing Starlette/httpx deprecation warning; exit 0 | Linux, Python 3.12, provider guard off; [log](checks/repository-pytest.txt) |
| Cleanup regression tests | 12 passed, included in 237 | Dry run, verified backup, CRLF preservation, drift/corrupt archive/path/symlink rejection, idempotence |
| Public-reference addon verifier | **50 passed**, exit 0 | 17 numeric sources / 26 records and 2 guideline sources / 3 notes; [log](checks/addon-verifier.txt) |
| Corpus structural validation | PASS, exit 0 | Release readiness separately remains BLOCKED |
| Python compileall | PASS, exit 0 | main.py, config.py, routers, services, tests and scripts |
| Node syntax checks | PASS | chat.js, experience.js, admin.js and documentation capture/render scripts |
| git diff --check | PASS | CSV-specific cr-at-eol attribute preserves pinned CRLF while retaining other whitespace checks |
| Actual UI captures | **16 views**, no horizontal overflow or JavaScript errors | 1440px desktop and 390px mobile; [manifest](../assets/screenshots/CAPTURE_MANIFEST.json) |
| Active documentation links | PASS: no broken local Markdown links in the maintained product/operator/engineering/user/evidence guides | Historical archives and immutable source bundles are not rewritten |
| External browser requests | Zero attempted in the captured flows | Fonts and renderer/sanitizer scripts are local |
| Provider calls | **0** during this work | Guard false; capture keys empty and local settings isolated; no budget file created by capture |
| User manual | 14 illustrated steps; HTML and 16-page PDF | Actual UI with explicitly marked mocked answer/OCR stages; visual page inspection |
| Diagrams | Two original SVG/HTML/PNG diagrams inspected | Architecture and message flow; future integrations identified as future |
| Optional Hyperframes introduction | Browser seek/render PASS; 12-second paused timeline, all images loaded, no JS errors | Editable composition and poster only; Hyperframes CLI lint/render and MP4 export NOT_RUN |
| Design documentation | Token-bearing DESIGN.md and synchronized JSON sidecar; 17 CSS colors and 10 component previews checked | Separate documenter; no additional UI edits |
| Independent visual review | Four v2 findings scored resolved; scoped ship recommendation | See [DESIGN_REVIEW.md](DESIGN_REVIEW.md); not a final local FO approval |
| Clean-baseline overlay rehearsal | PASS: copied package, applied cleanup, 237 repository tests, 50 addon tests, staged diff check | Tested in a separate clone; pinned source bytes also matched after Git staging; no unrelated staged files |
| Cleanup applied in preparation checkout | 144 listed files removed after verified sibling backup | Archive retains 154 exact baseline originals; no recursive deletion |
| Windows scripts/check.ps1 | NOT_RUN here | Required local integration gate |
| Final local-candidate FO review / Brain | NOT_RUN here | Must be performed or disclosed by local MAIN |
| Live provider re-validation / clinical validation | NOT_RUN | Not authorized by this work |

## Capture interpretation

The homepage, example control, provider-unavailable state, scope refusal, local login,
settings read and mobile workspace were captured from the actual app. OCR extraction,
confirmation, completed generated answers, source display and follow-up success use
labelled browser-intercepted fixtures. Those screenshots verify UI presentation only;
they do not verify live provider output or bypass the backend contract in production.

The capture environment used memory storage, a synthetic corpus, local public lookup,
no real credentials, temporary admin/ledger paths and disabled provider transport.
It did not Save settings or invoke provider tests. The source panel uses DOC-DEMO,
an explicitly synthetic documentation source. All known test servers were stopped.

Browser assertions also checked alignment of supplied-range labels with their band,
terminal failure wording, reset to intake, image-review/confirmation controls, and
follow-up rendering. Screenshots used reduced-motion preference; separate assertions checked native desktop scroll, preference changes and missing-GSAP fallback. Mobile dialog and report-state assertions are recorded individually in the capture manifest. Complete keyboard,
assistive-technology and independent human comprehension evaluation is not claimed.

## Baseline issues reconciled without weakening validation

1. The untouched baseline's AGENTS.md and BUSINESS_BRIEF.md did not match their
   knowledge-manifest hashes. The API citation test failed there. Three legacy source
   snapshots now bind the exact c9236f5 document bytes independently of active guide
   edits. Their source approval and release eligibility remain unchanged.
2. The untouched baseline's addon verifier failed at data/records-review.csv.
   Restoring only CRLF produces its already-pinned package SHA-256 exactly. No data
   field or checksum policy was changed. Other addon files remain unchanged.

See [repository cleanup](../engineering/REPOSITORY_CLEANUP.md) for hashes and safeguards.
The original failures are not caused by a new clinical algorithm, and their repair
must not be presented as approval of the business corpus.

## Packaging and local closeout

scripts/product_refresh_manifest.json lists every payload file and SHA-256 (excluding
itself). scripts/verify_product_refresh.py checks the copied bytes and baseline ancestry.
--integrated additionally checks that listed obsolete files have been removed.
The ZIP includes an outer package inventory and a short goal prompt. Its packaging
check verifies member paths, sizes, checksums and absence of private/runtime files.

The owner applies this overlay to the existing repository, then follows
[LOCAL_CLOSEOUT.md](../engineering/LOCAL_CLOSEOUT.md). No package pass substitutes for
the final local Windows gate or authorization to call providers or deploy.

Online readiness, approved business data/rights, cloud secret/quota operation,
post-remediation live validation, final independent review, PDF OCR and proposed
HIS/pharmacy work remain separate open decisions. See [readiness](../operations/READINESS.md).
