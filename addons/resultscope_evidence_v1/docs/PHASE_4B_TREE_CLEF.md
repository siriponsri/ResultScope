# Phase 4B — hierarchical evidence retrieval and optional Clef

## Implemented here

The tree is corpus → institution → document → analyte → evidence. Retrieval traverses relevant analyte branches based on known Thai/English aliases, applies explicit source/sex filters, ranks matching records and returns citations. It is deterministic metadata-guided hierarchical retrieval; there are no embeddings, recursive LLM summaries, RAPTOR or learned tree traversal in this package.

An input without a recognized analyte alias abstains. The main application's scope gate must run first; the presence of 'ALT' in an otherwise malicious request does not make that request safe. Contextual follow-up is owned by the existing session/history pipeline.

The experimental flat method and tree method are evaluated on the same 15 visible cases. Result in this build: flat 12/15, tree 15/15. These are small regression cases authored with the implementation, not a blinded evaluation, not a comparison against local Phase 2, and not proof of general quality improvement. `evaluate.py` gates tree cases and records flat failures without treating the baseline as the candidate gate.

## Clef contract

The adapter targets Cloudflare's typed choice output and checks response shape, route labels, finite probabilities, probability sum and confidence consistency. Routes are `reference_lookup`, `business`, `report_explanation`, `out_of_scope`. Unexpected schemas fail closed to `unavailable`. Requests are bounded, single attempt, timeout 15 seconds, with redirects rejected and errors sanitized.

Clef stays **disabled or shadow-only**. It does not replace Python rules, select a clinical interval, authorize tool use, bypass scope/output guards or establish that retrieved text is true. It is not required for the working reference demo. No live Clef call or model-quality evaluation was performed here.

A future bounded experiment can provide a short de-identified question and a compact list of allowed evidence categories to Clef, compare its recommendation against a deterministic route, and measure disagreement. Do not send raw patient reports/identifiers by default. Do not claim 'Tree → Clef → LLM' is integrated until that exact path has actual local traces and tests. Start with shadow measurements before considering route control in a separately approved change.

## Local acceptance

1. Inject retrieved records as untrusted external evidence through the existing LLM/provider abstraction; preserve citation allowlists, output policy, session signing and sync/SSE parity.
2. Compare current local retrieval and new retrieval on identical queries/corpus and record retrieval latency separately from provider latency. Record cost only when actually measured.
3. Check Thai aliases, conflicts, wrong units, missing context, no hit, prompt injection and tampered citations. Preserve synthetic/release/public-reference separation.
4. Keep current deterministic path as fallback. Absence or failure of Clef must not disable report interpretation rules or reference browsing.
5. Live Typhoon and Clef require available owner-authorized server credentials and observed API compatibility. Typhoon's free access does not authorize paid Cloudflare calls. Missing live evidence stays NOT_RUN.

Official implementation references checked while preparing this patch:

- https://blog.cloudflare.com/clef-decision-models/
- https://developers.cloudflare.com/workers-ai/models/clef/
- https://developers.cloudflare.com/workers-ai/models/clef-flash/

API products can change; inspect current official schema before any live smoke test. Tests in this ZIP validate the implemented contract, not the external service's availability.
