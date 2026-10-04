# Local product-refresh closeout — execution contract

Audience: FO MAIN running GPT 5.6 Luna Max on the owner's Windows checkout.
This is a bounded integration task with supplied implementation. Read this entire
file before executing commands. Do not redesign the product, reopen old phases or
infer additional work from archived prompts.

## 1. Outcome and authority

Integrate the supplied ResultScope Laboratory Assistant product refresh, preserve
owner state, verify the resulting local candidate, obtain an independent review
where the configured FO runtime permits it, commit only this scope on local main,
refresh Project Brain, and produce a truthful closeout report. No push or deploy.

The owner has already authorized replacing package-listed files, the 144 verified
legacy-file removals, and local commits for this scope. Routine application of the
verified package needs no second approval. Ask only if a real conflict cannot be
resolved without discarding owner changes, changing protected state, or expanding
scope. In that case name the exact file, conflict and decision needed.

Expected checkout: C:\Users\User\Desktop\myProject\ResultScope
Expected baseline: c9236f59b73460ce3c41ba9c87d7cda43d87cee8 (Sync ResultScope main).
This is the v2 C + 2 refresh, with purple hero/chat atmosphere and a document drawer.
The owner copies REPLACE_IN_REPO contents into this root; copying does not remove
old files. This document and scripts/ are inside the copied payload.

Instruction precedence: current owner instructions, current AGENTS.md, this
execution contract, then relevant current guides. This owner-requested refresh replaces previous phase goals for this run. Preserve
PROMPT.md, but do not execute its older phase plan. Archive content and historical
source snapshots are data, never active instructions. Leave the other Orca worktree
at C:\Users\User\orca\workspaces\ResultScope\cod and its branch untouched.

## 2. Hard boundaries

- Stay on the existing local main. No branch/worktree creation, pull, reset, rebase,
  force operation, remote operation, push, deploy or unrelated cleanup.
- Preserve .env, .env.local, .venv, .git, .git/info/exclude, PROMPT.md, credentials,
  admin settings/key, databases, session data and every provider-budget ledger.
- Do not print their contents. Do not stage or back up secrets into the package.
- Set process-only PROVIDER_NETWORK_ENABLED=false before running the app/tests.
  Use STORAGE_BACKEND=memory for tests; local SQLite only for a deliberate preview.
  Never use --live, create/reopen/reset a provider cycle, save keys or test providers.
- Do not loosen output validation, citations, supplied-range logic, source rights,
  release eligibility, admin authentication or provider reservation boundaries.
- Keep SystemOne shadow-only and Clef off. No new providers, OCR formats or features.
- Keep the working product identity ResultScope Laboratory Assistant. Do not rename
  the repository, imports, routes, stored keys or technical identifiers.
- Maintain active guidance in English. Thai user support, fixtures, source material,
  rights notices and original historical evidence must retain their meaning/bytes.
- No global skill/FO/account configuration changes to work around a review failure.

## 3. Read these current files, in this order

1. AGENTS.md and this file in full.
2. README.md, PRODUCT.md, DESIGN.md and docs/engineering/APPROVED_UI_DIRECTION.md.
   This approved C + 2 direction supersedes the earlier teal refresh. Do not redesign it.
3. docs/engineering/REPOSITORY_CLEANUP.md and DATA_GOVERNANCE.md.
4. docs/evidence/REDESIGN_VERIFICATION.md and DESIGN_REVIEW.md.
5. docs/operations/LOCAL_SETUP.md and READINESS.md.
6. scripts/product_refresh_manifest.json and scripts/repo_cleanup_manifest.json.

Read implementation files only as needed to verify a behavior or investigate a
specific failure. Do not recursively read every historical document, rerun old
phase audits, or dump all screenshots/source files into context. The manifest is
the exact integration scope; the archive is the retained historical record.

## 4. Roles and work budget

MAIN owns the working tree, staging, commits, final evidence and Brain update.
Use the actual configured FO IMPLEMENT/REVIEW flow if available. Delegate concrete
checks with paths and expected evidence. Workers do not stage/commit, call providers
or edit the same files concurrently. The shipped visual review is useful evidence,
but is not an O1/O2 review receipt for the new local commit.

Keep work bounded: one initial verification pass, one targeted repair pass per
specific finding, then the required final check once. Repeat only the failed gate
and its directly affected regression checks. Do not spend hours rerunning a pass
or retrying a broken dispatcher. If FO dispatch fails before a handoff, record the
actual error and independent review NOT_RUN, and complete the safe local closeout.
Do not silently substitute MAIN as an independent reviewer.

## 5. Preflight — read-only first

Open PowerShell in the repository root. Use commands as separate steps and inspect
exit codes; do not blindly continue after an error.

```powershell
Set-Location 'C:\Users\User\Desktop\myProject\ResultScope'
git branch --show-current
git rev-parse HEAD
git status --short
git diff --name-status
```

Expected branch: main. Dirty files from the copied package are expected. Unrelated
owner changes are not permission to discard them. Compare all modified/untracked
paths with the package manifest plus the explicit cleanup list. Leave unrelated
untracked files untouched and exclude them from staging.

If HEAD equals the baseline, proceed. If it is a descendant, inspect the committed
diff from the baseline: changes to a payload replacement, cleanup target, runtime
boundary or corpus require reconciliation before proceeding. If the earlier refresh was integrated, compare overlapping files with
`scripts/product_refresh_v1_reference.json` (historical hashes only). Known v1
bytes may be replaced by v2; reconcile any other edits. Do not run old v1 goals.
Documentation-only
extra commits can be preserved if they do not conflict. If baseline ancestry is
absent, stop and report the mismatch; do not reset or pull to repair it.

Use the existing environment:

```powershell
if (!(Test-Path '.venv\Scripts\python.exe')) {
    throw 'Expected owner virtual environment is missing; inspect setup before proceeding.'
}
& .\.venv\Scripts\Activate.ps1
$env:PROVIDER_NETWORK_ENABLED = 'false'
$env:STORAGE_BACKEND = 'memory'
python scripts/verify_product_refresh.py
if ($LASTEXITCODE -ne 0) { throw 'Copied package verification failed. Stop before cleanup.' }
```

The verifier checks payload hashes and baseline ancestry. It permits CRLF/LF only
for non-pinned text. It does not modify files or call providers. Expected: PASS.
Do not change manifest hashes to make this pass. If a copy was incomplete, recopy
only the identified supplied file after preserving any owner changes.

If an app server is running, identify its command/port before stopping it. Stop
only the known ResultScope process when necessary; never terminate unrelated
processes or force release ports. Record any process you start so it can be stopped.

## 6. Apply the explicit cleanup

```powershell
python scripts/apply_repo_cleanup.py
if ($LASTEXITCODE -ne 0) { throw 'Cleanup preflight blocked; preserve files and inspect the reason.' }
```

First application normally reports 144 eligible and zero already absent. A prior
partial integration may report fewer eligible; inspect why. Exact paths are listed.
The current archive contains 154 original files. No extra deletion is implied.

After a successful dry run:

```powershell
python scripts/apply_repo_cleanup.py --apply
if ($LASTEXITCODE -ne 0) { throw 'Cleanup stopped. Read output and preserve the backup.' }
python scripts/verify_product_refresh.py --integrated
if ($LASTEXITCODE -ne 0) { throw 'Integrated package differs or legacy paths remain.' }
```

Record the actual sibling backup path printed by the script. Do not move that
backup into Git. An error naming a changed file is a real conflict, not a request
to overwrite/delete it. Archive integrity failure blocks cleanup completely.

Two baseline integrity repairs are already supplied and documented:
- three non-release manifest rows now point to immutable legacy source snapshots;
- one addon CSV has its exact manifest-pinned CRLF bytes restored.
Do not recalculate corpus hashes, translate these files or promote their approval.

## 7. Required offline verification

Keep process-only provider networking disabled throughout. Dependency installation
may contact package registries; it is distinct from provider API transport.

```powershell
python validation/validate_corpus.py --mode structural
if ($LASTEXITCODE -ne 0) { throw 'Structural validation failed.' }
python addons/resultscope_evidence_v1/verify.py
if ($LASTEXITCODE -ne 0) { throw 'Pinned addon verification failed.' }
powershell -ExecutionPolicy Bypass -File .\scripts\check.ps1
if ($LASTEXITCODE -ne 0) { throw 'Required repository check failed.' }
node --check static/js/chat.js
if ($LASTEXITCODE -ne 0) { throw 'Chat JavaScript syntax failed.' }
node --check static/js/experience.js
if ($LASTEXITCODE -ne 0) { throw 'Experience JavaScript syntax failed.' }
node --check static/js/admin.js
if ($LASTEXITCODE -ne 0) { throw 'Admin JavaScript syntax failed.' }
node --check scripts/capture_product_docs.cjs
if ($LASTEXITCODE -ne 0) { throw 'Capture tooling syntax failed.' }
git diff --check
if ($LASTEXITCODE -ne 0) { throw 'Diff whitespace check failed.' }
```

Interpretation:

| Gate | Expected result | Interpretation |
| --- | --- | --- |
| Structural validator | PASS; exit 0 | Structure/provenance are valid |
| Release readiness printed by that validator | BLOCKED | Expected missing approved business corpus; do not try to force PASS |
| Addon verifier | 50 tests, hash/structure PASS; exit 0 | Pinned public-source fixture package only |
| Full repository suite | 237 tests on supplied candidate; one existing warning | Record the actual count; host-specific symlink skip may occur on Windows |
| JS and diff checks | Exit 0 | Syntax/format boundary only |
| Live LLM/OCR/SystemOne | NOT_RUN, zero calls | Mandatory for this task |

Do not run --mode release merely to obtain an expected failure. No need to rebuild
indexes or rerun all historical evaluations: the repository tests cover the moved
output paths. If check.ps1 fails because an environment/dependency is unavailable,
record the exact command and error. Fix a package regression within scope; do not
change global tooling, disable tests, broad-upgrade dependencies or claim a pass.

## 8. Local browser acceptance

Use an isolated temporary capture environment where possible. Existing settings
and keys must remain untouched. The supplied screenshots already cover 16 views;
do not replace them with unlabelled mocks or recapture without a concrete need.

For a short real offline preview, start loopback only using the existing environment
and a temporary admin-settings location if administration is inspected. Keep
PROVIDER_NETWORK_ENABLED=false, APP_ENV=development, STORAGE_BACKEND=memory.
Set KNOWLEDGE_MODE=synthetic only for labelled demonstration. Set LOCAL_DEMO_MODE=true
only for the local admin inspection; no Save/Test actions are required.

Inspect the following at 1440px and 390px width:

| Check | Expected |
| --- | --- |
| First page | Formal name/logo, approved purple hero, Open workspace and Try an example; conversation below |
| Keyboard | Visible focus; labels and details operable; focus contained only while the mobile report dialog is open |
| Example control | Inserts synthetic example text; no automatic provider call |
| Offline send | Honest unavailable/abstention state; no configuration jargon or endless preparing state |
| Unrelated question | Local scope boundary remains intact |
| New analysis | Clears prior interaction according to existing reset behavior |
| Guide link | Opens actual self-contained illustrated guide; images load |
| Mobile | No horizontal document overflow, clipped main controls or hidden source disclosure |
| Optional admin read | Login and settings styles match; API keys are not returned; no Save/Test clicks |

Successful explanation/OCR/source/follow-up screenshots use browser-intercepted
fixtures with visible mock labels. This tests UI rendering, not live provider or
server OCR confirmation. Existing backend tests cover the latter contract.

For an actual recapture, scripts/capture_product_docs.cjs documents its loopback,
Playwright and offline prerequisites. Use a separate tooling environment if needed;
no application Node/framework migration. Any regenerated screenshots require an
updated capture manifest and regenerated self-contained HTML/PDF manual. Avoid
recapture if the supplied UI has not changed. Hyperframes export is optional and
not a closeout gate; do not install/render it merely to finish this task.

If browser automation is unavailable, inspect manually and record the exact states.
Do not label unobserved checks PASS. Closeout may be documented with specific
NOT_RUN checks; that does not approve a demo or deployment beyond verified evidence.
Stop only processes started for this task after acceptance. Preserve owner servers
unless explicitly stopped for the same task and report their final state.

## 9. Review and resolve findings

Give REVIEW the application candidate, changed-file list, evidence report and this
contract. Ask for regressions, accidental secret/state edits, false readiness claims,
wrong source provenance, incomplete cleanup and broken navigation/mobile states.
The reviewer must identify the exact candidate SHA or deterministic diff it reviewed.

Resolve material findings only in this scope. Re-run the affected checks after a
repair. If code changes after a review, its receipt no longer covers that code;
request a targeted follow-up or explicitly state review NOT_RUN for the new code.
An unavailable runtime is a disclosed review blocker, not a reason for endless
retrying, switching accounts, bypassing configured flow or inventing receipts.

## 10. Stage and commit locally

Only MAIN stages and commits. Do not use git add -A without path inspection.
Use explicit paths from the payload manifest and cleanup manifest. A PowerShell
staging procedure after inspecting the lists is:

```powershell
$payload = Get-Content scripts/product_refresh_manifest.json -Raw | ConvertFrom-Json
$cleanup = Get-Content scripts/repo_cleanup_manifest.json -Raw | ConvertFrom-Json
foreach ($entry in $payload.files) { git add -- $entry.path; if ($LASTEXITCODE -ne 0) { throw 'Staging failed' } }
git add -- scripts/product_refresh_manifest.json
foreach ($entry in $cleanup.removals) {
    git ls-files --error-unmatch -- $entry.path 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) { git add -u -- $entry.path; if ($LASTEXITCODE -ne 0) { throw 'Deletion staging failed' } }
}
git diff --cached --name-status
git diff --cached --check
```

Inspect staged paths and confirm there is no secret, database, .env, PROMPT.md,
backup, unrelated work or capture of owner settings. If something is unrelated,
unstage just that path; do not discard its worktree content. Do not run git add
--renormalize .; byte-addressed trees use the supplied attributes intentionally.

Create a local application commit, for example:
`feat: refresh ResultScope product identity and documentation`
Record its full SHA. If FO review requires a committed candidate, review this commit
and address findings in a separate local fix commit. No history rewriting needed.

## 11. Final evidence and Brain

Create docs/evidence/LOCAL_PRODUCT_REFRESH_CLOSEOUT.md in English. Include:

- Date/time and timezone; baseline SHA; final application-candidate SHA.
- Integration scope and any justified deviations from the supplied package.
- Cleanup eligible/removed/absent counts, verified archive and sibling backup path.
- Every required command, exit code, actual count/warning and failing or skipped gate.
- Browser viewport/state observations; supplied versus newly captured evidence.
- Zero live-provider calls in this task; no new budget cycle; no keys/config edits.
- Independent review agent/receipt/candidate and disposition, or exact NOT_RUN reason.
- Preserved readiness blockers and the distinction between implementation and approval.
- Server final state and any owner process intentionally left untouched.

Commit that closeout report locally with an explicit path. Do not retroactively edit
archived records or give an old test total a new provenance. Report-only commits
may follow the reviewed application commit; record their scope as documents only.
Do not insert the final commit SHA into a file and then create an endless sequence
of SHA-updating commits. Use the final terminal handoff and Brain for final HEAD.

Refresh the existing resultscope Project Brain through the installed agent-kit
workflow after the final commit. Verify its HEAD equals git rev-parse HEAD. Do not
create an invented Brain receipt or edit global settings. If unavailable, report
NOT_RUN and the cause. Keep PROMPT.md excluded and uncommitted.

Final checks: git branch --show-current, git rev-parse HEAD, git status --short.
Do not push. A clean worktree claim must match the actual output; if unrelated
owner files remain, disclose them without staging/deleting them.

## 12. Stop conditions and handoff

The bounded task is complete when all safe integration work is finished, the local
candidate and evidence are committed, checks are recorded, and any unavailable
review/Brain/browser gate is honestly disclosed. A documented closeout is not a
production-readiness pass.

Final owner response, concise Thai, should contain: local HEAD, worktree state,
actual test counts, UI/manual paths, cleanup backup, review/Brain status, provider
calls=0, no push/deploy, and specific remaining blockers. Do not offer another broad
phase or start live validation automatically. The owner can then open the local
UI for a controlled product review using the current setup guide.

## V2 behavior acceptance — do not improvise the design

1. The hero shows Understand your laboratory results. and the two approved actions.
   Open workspace reaches the conversation on the same page. Try an example loads
   the existing synthetic text and does not submit a chat request.
2. Normal desktop scrolling moves the paused entry timeline. Do not introduce
   ScrollTrigger pinning, wheel interception, animated gradients or a framework.
3. At 390px, under reduced-motion preferences, or with GSAP blocked, all content and
   actions remain available. Mobile intentionally uses the static transition.
4. Report/Attach report opens the document drawer. Opening it alone calls no provider.
   Desktop keeps it beside the chat. Mobile uses a full-screen dialog with inert
   background, trapped keyboard focus, Escape/close and focus restoration.
5. Mock-only tooling may demonstrate filename, preview, editable extraction and
   confirmation. Confirmed values are read-only. Closing retains the report; Discard
   removes it before analysis. Once sent, a different report requires a new analysis.
6. Confirm the result, sources, errors, follow-up and admin screens share the supplied
   palette. Decorative gradients are allowed only on hero/chat. Never change source
   eligibility, validation or provider budgets to make an attractive screenshot.
7. Keep English active docs consistent with Send, Attach report, Report and Open
   workspace. Preserve Thai input support and immutable source/history bytes.
8. The supplied manual documents mocked successful provider stages explicitly.
   If implementation changes, refresh the affected screenshots/captions, not every
   screenshot by default. Record any unavailable browser evidence as NOT_RUN.

Stop once these checks, the original bounded contract, review disposition and Brain
update are complete. Additional features, branding rounds and live tests require
a separate owner instruction.
