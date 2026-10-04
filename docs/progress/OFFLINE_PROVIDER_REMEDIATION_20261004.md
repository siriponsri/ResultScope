# ResultScope Offline Provider Remediation

Date: 2026-10-04
Branch: local `main`
Base checkpoint: `486265e1c099093c8f2a495afd4eda58d3b38fdb`
Live provider usage during this remediation: `0` requests

## Scope

This is a bounded offline remediation after the live-provider audit. It covers
provider attempt accounting, deny-by-default network protection, safe validator
diagnostics, public-reference attribution, and mock-only verification tooling.
It does not change provider keys, provider catalog choices, historical usage, or
the online-readiness decision.

Historical usage remains recorded as observed: LLM `5/5`, OCR `6/5`, and
SystemOne `6/5`. The causes of the three historical main-app output rejections
are not reconstructed from the available evidence; they must not be attributed
to citation failures without a new authorized live run.

## Guard And Budget

- `PROVIDER_NETWORK_ENABLED` defaults to `false`.
- Every live-capable provider boundary reserves before HTTP and checks the guard
  immediately before transport. Redirects are disabled and no SDK retry is
  configured.
- The SQLite ledger uses an explicit persistent `cycle_id`, server-side limits,
  and `BEGIN IMMEDIATE` reservations. Failed, malformed, timed-out, blocked,
  output-rejected, and unfinished reservations remain consumed.
- Slots are independent: `llm`, `ocr`, and `systemone`. `/models` uses `llm`;
  one SystemOne request is one decision; source paths identify Admin Test,
  chat, stream, models, OCR, shadow, and runner.
- Missing/inactive cycles and unavailable ledgers fail closed before transport.
- A local ledger created by the earlier remediation schema is upgraded in-place
  before new reservations are used; existing attempts and usage counts are
  preserved.
- `scripts/provider_budget_cycle.py` is the only explicit cycle-management
  helper. It never creates a cycle on application startup or from a request;
  it requires a configured cycle ID, configured limits, and explicit network
  opt-in for creation.

The ledger is local-only. It protects processes that share the same SQLite file
on one machine; it is not a cloud or multi-instance quota coordinator.

## Verification Runner

`scripts/provider_verification_runner.py` is mock-only by default and calls the
same `provider_adapters.test_provider` boundary as Admin Test. It prints only
slot, provider identifier, status, network flag, quota flag, and stable error
code. It never prints keys or provider bodies. `--live` is explicit and cannot
bypass the network guard, existing cycle, or reservation; it does not create a
cycle. The runner's default test ledger is not the runtime ledger because the
mock path makes no reservation.

Failed live-probe errors retain only system-generated attempt facts internally:
whether a reservation/outbound attempt occurred, its slot/source/outcome, and a
stable reason code. This prevents a transport failure from being reported as
`network_called=false` or `quota_used=false` after an actual reserved attempt.

## Validation And Citation

`OutputValidationError` now carries stable reason codes. Unknown validator
failures map to `provider_output_rejected` and remain fail-closed without raw
exception text. Public-reference and guideline factual answers require a
bracketed source ID that belongs to retrieved evidence. Source URLs remain
server-resolved and allowlisted. Forged IDs, URLs, numbers, unsupported claims,
and contradictory laboratory status remain rejected. Short generic abstentions
or clarification requests may omit citations without manufacturing one.

JSON and SSE route validation share the same fail-closed path. The public
response remains sanitized; reason codes are limited to safe metadata/audit
fields.

## Offline Evidence

The following checks use temporary SQLite files, fake transports, or synthetic
fixtures only:

- Provider budget tests cover limit five, sixth-attempt blocking, failed-attempt
  consumption, restart persistence, missing cycles, offline zero reservation,
  concurrent threads, and multiple processes.
- Boundary tests cover the adapter, `/models`, LLM stream, OCR, SystemOne
  shadow, and the mock-only runner.
- Existing public-reference, safety, API, LLM, and vision regressions remain in
  the focused suite.
- The real `/api/v1/chat/stream` route is covered with a fake transport and a
  temporary ledger to prove one shared LLM reservation and one outbound attempt.
- `/models` returns only an allowlisted `{id}` shape; provider-owned fields are
  not returned to clients.
- A completed provider attempt can be marked `output_rejected` with the stable
  validator reason without refunding its consumed quota.
- `scripts/check.ps1` is the required final repository check; it is run only
  after the candidate is complete. It must not be treated as live validation.

Latest offline evidence for the completed offline candidate:

- Focused provider/citation/safety suite after the timeout and citation-fragment
  fixes: `77 passed`, 1 existing
  Starlette/httpx warning.
- Provider boundary, budget, runner, OCR, Admin, public-reference, safety, and
  LLM subset: `103 passed`, 1 existing warning.
- `powershell -ExecutionPolicy Bypass -File .\scripts\check.ps1` on the
  previous candidate: `224 passed`, exit 0, 1 existing Starlette/httpx warning.
- O1 review receipt `aabba2fabea44061bcc37a057d3cca4d` inspected exact commit
  `944572ce6b2ed22af75f90938f0f20f991749e24` and found three issues. The high
  unsupported-claim issue is addressed with source-specific structured evidence
  checks and a valid-ID contradictory-claim regression. The medium URL issue is
  addressed by binding provider-written URLs to the attributed source ID. The
  check-receipt issue is addressed below for the final commit.
- The final review receipt `8b11863175f5452db98c5f40c54baa10` inspected exact
  `cb98bd007ee4e698de336fc5d69d85033c04cad7` and found a remaining reversed
  numeric-interval relationship gap, a duplicate-URL occurrence concern, and
  the stale exact-check receipt above. The interval regression and occurrence
  binding fix are now in the follow-up candidate; the exact final check will
  be rerun after its commit.
- Follow-up focused provider/citation/safety suite: `78 passed`, 1 existing
  Starlette/httpx warning. Full exact-candidate check on
  `acbcffc6c79985b91ec611c25e6eba4a4837e42e`: `powershell -ExecutionPolicy
  Bypass -File .\scripts\check.ps1`, exit `0`, `225 passed`, one existing
  Starlette/httpx warning, completed on `2026-10-04` local time. No live
  provider transport was enabled or called.
- `compileall` and `git diff --check` passed. Tests use fake transports, temporary
  ledgers, or synthetic fixtures; no live provider request was made in this
  remediation.
- The first independent O1 review findings now have targeted fixes and passing
  regressions in the current candidate. A fresh exact-candidate independent
  review has not been run; final approval is therefore `NOT_RUN`.

## Status And Blockers

- Live re-validation after remediation: `NOT_RUN` by instruction; live budget
  for this remediation is zero.
- Online readiness: `BLOCKED` by the historical budget breaches, missing
  independent exact-candidate approval until review is recorded, cloud secret
  and multi-instance controls, approved corpus/rights, and absent live quality
  evidence.
- No Supabase/Redis/Upstash migration, new provider, deployment, push, key
  change, or runtime ledger is part of this remediation.
