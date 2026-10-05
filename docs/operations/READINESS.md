# Readiness and evidence

**Current decision: controlled local evaluation only. Online readiness remains BLOCKED.** A polished interface and passing offline checks do not establish clinical, product-market, or production readiness.

This document distinguishes retained evidence from tests of a new candidate. It does not issue a new approval or claim a deployment.

## Evidence status

| Area | Known evidence | What it does not establish |
|---|---|---|
| Earlier Phase 6 candidate | Phase 6 records 195 repository tests and local/mocked browser checks | A pass for this redesign or the final candidate |
| Offline provider remediation | Report records 225 tests at `acbcffc6c79985b91ec611c25e6eba4a4837e42e`, exit 0, one existing warning | Live provider quality or independent approval of a later candidate |
| Owner-reported local checkpoint | Owner reports 225 tests passing at `6b095ccd` | An independently reproduced receipt for this redesign |
| Public-reference addon | Phase 6 records 50 addon tests and a 15/15 tree versus 12/15 flat fixture comparison | A clinical study, broad retrieval superiority, or live RAG quality |
| Historical live calls | LLM transport and some OCR/SystemOne behavior were observed | Acceptance of the complete workflow or release readiness |
| Post-remediation live validation | `NOT_RUN` | No later live result may be inferred from offline fixes |
| Historical repository migration candidate review | `PASS` for exact pre-integration candidate `dd323ac00237b4ab2472c5052aa068e15620dd3`; earlier pushed `c184f6d` and later documentation-only closeout commits add closeout metadata only | This receipt is not an exact-head review of current HEAD `12ccb8a27428f819386fa17c4412c764de0f1867` or the current dirty worktree. O1 review was read-only and did not rerun tests or browser capture |
| Current Report Canvas candidate `1684c41c3a6db782bf546264a34c0253982aacf7` | Offline browser capture, focused/full tests, sanitized synthetic evaluator receipt, and provenance tooling are maintained for the candidate | This evidence does not establish live provider quality, clinical safety, production readiness, or independent final review |
| Current independent final review | `NOT_RUN` | No independent reviewer/route receipt is available for the exact current candidate |
| HyperFrames runtime/toolchain | Unavailable in the application; HyperFrames player/artifact and CLI/export checks are `NOT_RUN` | Local GSAP and static/reduced-motion fallbacks are presentation support, not a HyperFrames implementation or provider evidence |
| Independent human usability validation | `NOT_RUN` in the retained Phase 6 record | Screenshots are not evidence of user comprehension |

Sources: the original offline-remediation, Phase 6, and live-verification reports preserved in the [historical archive](../archive/README.md), indexed by [evidence history](../evidence/HISTORY.md). The owner-reported checkpoint is separate session evidence, not a rewritten version of those reports.

The redesign's actual checks, screenshots and scoped visual review are recorded in [redesign verification](../evidence/REDESIGN_VERIFICATION.md). Those checks do not close the live or online gates. No provider call is authorized or implied by this documentation.

The historical repository migration, clean Git closeout, focused checks, and O1
receipt are recorded in [repository hygiene closeout](../evidence/REPO_HYGIENE_CLOSEOUT.md).
That closeout is bound to the candidate and scope named in its receipt. The
current candidate's offline evidence is maintained in the screenshot manifest,
the sanitized coursework receipt, and the provenance record; none of those
records upgrades the controlled-local, online, clinical, or production decision.

The audit mapping and review-language rules are maintained in
[audit remediation](../evidence/AUDIT_REMEDIATION_20261005.md), with asset
ownership and license boundaries in
[asset ownership](../engineering/ASSET_OWNERSHIP.md).

The later local UI-refresh closeout is recorded in
[LOCAL_PRODUCT_REFRESH_CLOSEOUT.md](../evidence/LOCAL_PRODUCT_REFRESH_CLOSEOUT.md).
It records the earlier application candidate `b67cca1` and Windows verification;
it is not an exact-head review of this repository migration and does not upgrade
online or release readiness.

## Preserve the historical budget record

| Slot | Historical attempts / limit | Status |
|---|---|---|
| LLM | 5 / 5 | Budget exhausted |
| OCR | 6 / 5 | Historical overrun |
| SystemOne | 6 / 5 | Historical overrun |

The remediation adds a deny-by-default guard and persistent attempt reservations; it does not erase the overruns. Three historical main-app generated answers were rejected. Their causes must not be reconstructed as citation failures without evidence from a new authorized run.

Failed, timed-out, malformed, output-rejected, blocked-after-reservation, and unfinished reservations remain consumed. An active cycle is not created by application startup. The SQLite ledger coordinates processes on one machine sharing that file; it is not a cloud or multi-instance quota control.

## Open release gates

| Gate | Required evidence or work |
|---|---|
| Exact-candidate verification | Reproducible checks, recorded browser findings, and an inspectable independent receipt naming the full exact SHA, scope, verdict, and limitations. Without that receipt, status is `NOT_VERIFIABLE_FROM_REPOSITORY` |
| Provider contracts and quality | Explicitly authorized bounded live validation, accepted quality cases, and retained sanitized attempt receipts |
| Corpus and rights | Owner-approved business/education content; source provenance; permitted distribution and commercial use |
| Application rights | Resolution of the upstream code-rights issue recorded in `NOTICE.md` |
| Privacy and access | Intended-use review, appropriate identity/roles, consent, retention, deletion, and access controls |
| Production operations | Approved secret storage, distributed quota controls, monitoring, backup/recovery, incident handling, and support ownership |
| Human usability | Independent evaluation of comprehension, correction, source use, error recovery, and accessibility |
| PDF OCR | Separate contract, runtime, and workflow validation; currently unsupported |
| Partner integrations | Defined HIS/pharmacy scope, partner agreements, interface contracts, and separately evaluated behavior |

The local admin UI, signed conversation cookies, and secret-file encryption are prototype controls. They do not justify a compliance certification, clinical claim, or launch declaration.

## Demonstration conditions

Use loopback binding, explicit local-demo mode only when administration is needed, and `PROVIDER_NETWORK_ENABLED=false` for offline work. Preserve `.env`, local keys, and ledgers. Use synthetic or de-identified material. Label mocked explanations and OCR results where shown. Record failures and unavailable states alongside successful screens.

A decision to conduct live validation must define its inputs, provider slots, limits, owner, and stopping conditions separately. This page is a readiness record, not a live-run procedure.
