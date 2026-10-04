# Product roadmap

This roadmap is a sequence of proposed decisions, not a delivery commitment. The current code is a laboratory-education prototype. HIS, pharmacy, FHIR, patient records, ordering, dispensing, and billing are not implemented integrations.

## Stage 1 — Establish the local product baseline

**Outcome:** a coherent workspace and reproducible evidence of behavior within the stated scope.

- Maintain the approved C + 2 interface and consistent English documentation.
- Verify intake, image review, sources, errors, reset, keyboard use, and narrow screens on the actual application.
- Label screenshots of mocked stages explicitly.
- Record exact-candidate checks and reviews; retain historical failures and budget overruns.

**Gate:** a complete offline candidate, reproducible checks, and an independent review receipt. A visual redesign alone does not close this gate.

## Stage 2 — Controlled evidence and usability evaluation

**Outcome:** establish whether readers and reviewers understand the workflow and its limits.

- Obtain owner-approved educational and business content with provenance and usable rights.
- Define comprehension, source-attribution, extraction-correction, and safety cases.
- Plan bounded provider validation with synthetic inputs, explicit attempt accounting, and an owner-approved cycle.
- Resolve provider contract and output-quality questions; treat PDF support as separate proposed work.

**Gate:** exact-candidate review, documented provider evidence, source-rights approval, and human evaluation against agreed criteria. Mock tests do not satisfy live quality validation.

## Stage 3 — A named laboratory or clinic pilot

**Outcome:** test the explanation experience in a defined operating process with accountable owners.

- Establish identity, roles, tenant separation, consent, retention, audit, and incident response.
- Replace local-only secrets and quota coordination with approved deployment controls.
- Define staff review, escalation, downtime behavior, and support.
- Resolve upstream code and corpus rights before commercial distribution.
- Measure operating effort and user understanding without assuming clinical benefit.

**Gate:** partner-approved scope, governance review, operating runbook, deployment approval, and a documented oversight decision. No contract or deployment is claimed today.

## Stage 4 — Proposed HIS connection

**Outcome:** bring approved result context into the assistant without re-entry, subject to partner design and validation.

| Proposed area | Questions to resolve |
|---|---|
| Result ingestion | Which HIS/LIS owns each result, amendment, identifier, unit, and range? |
| Interoperability | Which partner contract and format apply? Would an HL7/FHIR interface be appropriate? |
| Patient context | What minimum context is necessary, who can access it, and how is consent recorded? |
| Review and delivery | Who approves an explanation, where is it displayed, and how are amendments handled? |
| Reliability | How are duplicate events, stale results, outages, and reconciliation handled? |

Any connector must preserve the originating report's values and provenance. No implemented FHIR resource model, endpoint, conformance claim, or interoperability certification is implied.

## Stage 5 — Proposed pharmacy workflow

**Outcome:** evaluate a distinct, professionally governed use case around laboratory context in pharmacy practice.

Discovery could examine a pharmacist's review of relevant laboratory context and documented handoff of questions needing clinical judgment. The current assistant must continue refusing medication changes. A future product needs a separately approved scope, authorized clinical content, professional oversight, role design, and intended-use evaluation.

No prescribing, dispensing, dose adjustment, interaction checking, medication reconciliation, or pharmacy-system write-back is currently available. These are not implied extensions of laboratory explanation.

## Proposed measures

Track task completion, comprehension errors, extraction corrections, unsupported-answer rates, source attribution, abstention quality, provider-attempt consumption, support effort, and staff review time. Establish baselines and targets during evaluation; this roadmap makes no benefit or performance claim.
