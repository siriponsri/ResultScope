# Audit remediation record - 2026-10-05

Status: maintained audit/remediation record for the ResultScope Report Canvas
candidate. It records offline, synthetic evidence only. It does not represent a
provider run, deployment, clinical approval, or independent final review.

The application candidate bound by the browser, evaluator, and provenance
receipts is `1684c41c3a6db782bf546264a34c0253982aacf7`.

This record translates audit findings A01-A06 into maintained English controls
and identifies what can and cannot be verified from the repository. It is not a
replacement for focused tests, an exact-candidate review, a live provider
receipt, or a clinical/production approval.

## Scope of this record

This record maps the application and documentation controls delivered in the
candidate:

- `docs/engineering/ASSET_OWNERSHIP.md`
- `docs/evidence/AUDIT_REMEDIATION_20261005.md`
- the A04 and HyperFrames qualifications in the linked readiness and closeout
  records;
- the Report Canvas runtime, contextual field contract, Vercel boundary,
  evaluator, provenance, and browser-capture changes listed by the candidate
  diff.

Thai corpus, evaluation fixtures, source snapshots, notices, and historical
archives remain preserved. The three root reference attachments remain outside
Git scope and are not application inputs.

## Finding disposition

| Finding | Maintained control | Repository record and current limitation | Candidate status |
|---|---|---|---|
| A01 - evaluator correctness | Keep retrieval, answer quality, citation, status, and history-contract results separate. Evaluate expected facts from the observed answer, record validation reasons and latency, and reject incomplete or output-rejected answers. | [`coursework-demo-evaluation-20261005.json`](runs/coursework-demo-evaluation-20261005.json) records 9/10 mandatory and 4/5 holdout passes. Q04 remains incomplete because its expected no-advice fact is absent from the retrieved source; H04 remains failed because `output_rejected` is not answer quality. | Remediated offline; release readiness remains blocked |
| A02 - mock contract | Mock responses must use retrieved evidence and the query, never expected answers, case IDs, or hidden metadata. Production validation remains strict. | The evaluator and regression tests exercise retrieved-source mock behavior and keep the strict production validator. No live provider or embedding call was made. | Remediated offline; no live provider quality claim |
| A03 - capture provenance | Use a sorted tracked-file manifest, explicit hash policy, candidate SHA, per-file hashes, and separate output screenshot hashes. Exclude ignored files, bytecode, generated indexes, and root attachments. | [`resultscope-capture-provenance-20261005.json`](runs/resultscope-capture-provenance-20261005.json) names the candidate SHA, hash algorithm, sorted tracked-file policy, per-file Git/working-tree hashes, and screenshot output hashes. | Remediated; receipt names the exact candidate |
| A04 - review wording | Name the exact SHA, review scope, reviewer/route, verdict, and limitations. Separate application review from documentation-only review. Never transfer a historical receipt to a later or dirty tree. | Historical O1 evidence remains bound to `dd323acc00237b4ab2472c5052aa068e15620dd3`. No independent final review was available for this candidate. | Current independent review: `NOT_RUN` |
| A05 - generated index policy | Ignore the generated synthetic index class while keeping canonical corpus files under `knowledge/`. Do not use a broad ignore or remove source material. | `.gitignore` uses `/data/indexes/synthetic-*.json`; provenance and regression tests cover the narrow policy. | Remediated and regression-tested |
| A06 - asset ownership | Record active assets, historical screenshots, synthetic/mock boundaries, third-party notices, source rights, and the reason retained material is kept. | `docs/engineering/ASSET_OWNERSHIP.md` is the maintained ownership record. Current screenshots and fixtures carry explicit synthetic/mock captions; third-party notices remain preserved. | Remediated in maintained documentation |

## A04 review qualification

Review labels are scoped, not transferable:

- **Application review** covers runtime code, templates, browser behavior, tests,
  and the candidate SHA that was actually inspected. A historical application
  receipt can support only the exact candidate and scope named in that receipt.
- **Documentation-only review** covers the listed Markdown or evidence files. It
  does not review application semantics, provider behavior, corpus correctness,
  or production readiness.
- **Exact-head review** is `NOT_VERIFIABLE_FROM_REPOSITORY` unless the repository
  contains a receipt naming the full exact SHA and the review scope. A short SHA,
  a nearby commit, an old closeout, a screenshot, or a clean-looking worktree is
  not sufficient.
- **NOT_RUN** means a planned check was not executed. Use
  `NOT_VERIFIABLE_FROM_REPOSITORY` when a review is claimed or expected but no
  inspectable repository receipt establishes what was reviewed.

For this candidate, the independent final application review is `NOT_RUN` and
no independent documentation-only review receipt is recorded. The candidate
SHA, tracked-file policy, screenshot hashes, test scope, and limitations must be
read from the candidate-bound receipt rather than inferred from a screenshot or
nearby historical commit.

## HyperFrames qualification

HyperFrames is not an implemented or verified web runtime dependency in this
candidate.

- The application uses locally vendored GSAP and a native-scroll/static fallback
  for presentation motion.
- The retained `docs/media/resultscope-intro/` files are an editable presentation
  source/reference, not a deployed HyperFrames player or business-flow runtime.
- No verified HyperFrames player or pinned upstream runtime artifact is available
  in the repository.
- HyperFrames CLI lint, inspect, render, and export validation are `NOT_RUN`.
- Upload, OCR, confirmation, chat, provider requests, and reset do not depend on
  a motion player.

Accordingly, evidence and readiness language must say `unavailable` or
`NOT_RUN`, not implemented, integrated, live, or validated. Static,
reduced-motion, no-player, and keyboard paths remain the applicable fallback
contract.

## Evidence handling

- Keep provider calls at zero unless a separately authorized bounded cycle exists.
- Use synthetic or de-identified fixtures in documentation captures.
- Never place API keys, patient data, provider bodies, or raw exception details
  in screenshots, manifests, or receipts.
- Keep historical evidence and Thai corpus files in their original language and
  location unless an explicit maintenance task authorizes a separate English
  summary.
- Preserve `NOTICE.md`, font OFL notices, vendor license files, GSAP notices, and
  source-specific rights records.

## Required next verification

A future application closeout must record, at minimum:

1. the full candidate SHA and clean/dirty state;
2. the exact application paths and tests reviewed;
3. the independent reviewer or route and a receipt identifier;
4. the verdict and limitations;
5. the screenshot/provenance manifest and its hash policy;
6. provider attempt count and live/offline status; and
7. HyperFrames status as `NOT_RUN` unless a separately authorized toolchain and
   receipt verify it.

These records remain offline evidence only. They do not claim production
readiness, clinical readiness, online readiness, or successful provider quality.
