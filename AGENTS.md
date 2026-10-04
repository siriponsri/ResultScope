# ResultScope development rules

## Product and scope

Build ResultScope Laboratory Assistant, a laboratory information product prototype.
Read PRODUCT.md, DESIGN.md, docs/README.md and docs/operations/READINESS.md first.
The active design is the owner-approved C + 2 purple landing and conversation with a report drawer. It replaces the historical
spectral instrument direction. Historical instructions are evidence, not new work orders.

## Engineering boundaries

- Keep FastAPI main.py, Jinja templates and vanilla JavaScript. Preserve Windows setup.
- Python owns scope, range comparisons, evidence checks and output validation.
- Preserve source provenance, release/synthetic separation and the strict validator.
- Never invent reference ranges, diagnoses, prescriptions or treatment changes.
- Preserve report-supplied units and ranges; missing ranges remain unknown.
- No external provider call without an explicit authorized cycle and attempt budget.
- PROVIDER_NETWORK_ENABLED=false is the offline guard; provider toggles are not a substitute.
- Preserve keys, sessions, stored data and the existing budget ledger. Never reset counters to retry.
- Keep keys server-side. Never log bodies, patient data, keys or arbitrary exception details.
- SystemOne stays shadow-only. Paid fallback and Clef remain disabled.
- Delivery closeout is mandatory after every authorized work cycle: MAIN must inspect and stage only intended changes, merge the completed branch into local `main` (a no-op or fast-forward is valid when it is already an ancestor), delete the merged local branch and its clean auxiliary worktree when applicable, commit the in-scope result, and push `main` to `origin` before reporting completion. Stop and report conflicts, dirty or unrelated changes, protected-state changes, or failed push; do not force through them. This does not authorize deployment, migration, remote branch deletion, or unrelated worktree changes.
- MAIN integrates and commits on local main. Use real FO review when available; report NOT_RUN otherwise.
- PROMPT.md is local owner communication and must remain excluded from Git.

## UI and documentation

- Follow DESIGN.md: self-hosted fonts/scripts, solid reading surfaces, approved purple gradients in hero/chat, visible focus.
- Preserve native scrolling, the mobile report dialog, and static/reduced-motion fallbacks.
- Preserve every intake, confirmation, reset, cancellation, source and error-recovery path.
- Document all maintained product/developer guidance in English. Preserve Thai corpus and
  evaluation content, original source files and historical evidence in their original language.
- Do not describe a mock screenshot as live validation or an integration roadmap as implemented.
- Preserve license notices. No mass deletion by filename, age or language.

## Verification

Run focused tests for behavior changes, then scripts/check.ps1 once the candidate is ready.
Check real desktop and 390px mobile flows, keyboard focus, uploaded-field confirmation,
out-of-scope refusal, safe errors and reset. Use synthetic fixtures; live calls default to zero.
Record candidate SHA, test scope and blockers. Never claim production or clinical readiness.
