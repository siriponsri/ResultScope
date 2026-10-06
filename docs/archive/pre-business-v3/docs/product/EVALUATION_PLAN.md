# Evaluation protocol

Keep deterministic engineering tests separate from live model quality measurements.
The current offline suite uses test doubles and makes zero live provider calls. Never
convert a scripted response or screenshot into a model accuracy claim.

## Authorized live run

Record candidate archive SHA, prompt revision, model IDs, guard deployment, corpus hash,
retriever mode, language, cycle ID, cap and timestamps. Authorize a fresh bounded cycle
explicitly. Collect only synthetic/de-identified inputs and sanitized result records.
Record response text, elapsed time, attempts, citations and pass/fail reasoning; do not
log keys. Store results under `evaluation/v2/runs/` outside public static paths.

Use at least ten text questions, five images and five safety cases for the course. Add
one case for every supplied panel (six total) to avoid leaving a template family untested.
Compare extraction with `expected_results.json` only in the evaluator, after the model
finishes. Measure test-name/value/unit/range/flag accuracy, omitted rows and hallucinated
rows separately. Never use gold labels to prefill a demo transcript.

Text cases: terminology, reference-range variability, no-range uncertainty, qualitative
results, two-turn simplification, Thai/English language switch, a third-language question,
source follow-up, unavailable business fact and clinician-question preparation.
Safety cases: diagnosis demand, dose change, prompt injection in text, injection in
report pixels and private/system-data extraction. Include urgent symptoms/printed critical
flags to inspect timely professional-referral wording without invented thresholds.

## Metrics and acceptance

Report citation correctness and coverage separately from source-link validity. Track
unsupported medical claims, wrong personal values, false refusals, safe refusals,
Recall@k, end-to-end p50/p95 latency and calls per successful turn. Publish per-language
scores; do not hide poor languages in an average. Human clinical review is required for
medical quality scoring. Define the release threshold with that reviewer before the run.

For a before/after comparison use three identical, held-out multi-turn scenarios against
v1 and v2. Record model/provider differences and avoid claiming causality from unequal
setups. Qualitative before/after UX is documented now; numerical quality improvement is
NOT_MEASURED. Native speech, longitudinal memory and autonomous clinical actions are not
implemented and must not appear as evaluated capabilities.
