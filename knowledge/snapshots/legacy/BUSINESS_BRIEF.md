# ResultScope — business brief

## Positioning

**Do not sell “AI chatbot for lab results.”**

Position the product as a **laboratory-result intelligence layer** that turns a result release into a guided understanding and follow-up journey.

### One-line pitch

> ResultScope helps diagnostic labs and clinics turn static laboratory reports into clear, controlled, branded explanations that improve patient understanding and create a reason to re-engage.

## Initial ICP

### Primary: private diagnostic laboratories / clinic chains
Pain points:
- results are delivered as PDFs or portal rows with little explanation;
- staff repeatedly answer similar “what does this value mean?” questions;
- patient relationship often ends when the report is delivered;
- generic LLM use is difficult to govern or brand.

### Secondary: corporate wellness / annual health-check providers
Pain points:
- high-volume screening creates large numbers of borderline results;
- employees receive data but little structured follow-up;
- providers want a scalable education layer without turning every result into a doctor visit.

## V0.1 value proposition

For users:
- understand what each value represents;
- see what stands out without alarmist language;
- see which values should be read together;
- know what context is missing;
- prepare better questions for a clinician.

For organizations:
- branded result-explanation experience;
- controlled lab-only scope;
- provider/model portability;
- lower cost than a free-form general assistant;
- foundation for post-result engagement.

## Product wedge

The wedge is **not model quality**. Models can be swapped.

Defensibility should accumulate in:
- laboratory ontology and parsing;
- organization-specific reference ranges;
- explanation policy and versioning;
- structured report schema;
- longitudinal marker history;
- quality feedback / human review;
- integrations with LIS/LIMS/portal workflows;
- provenance and auditability.

## Monetization hypotheses

These are hypotheses to validate, not pricing claims.

1. **B2B SaaS / white label** — monthly platform fee + usage tier.
2. **Per-result explanation** — organization pays per generated explanation/report.
3. **Corporate screening bundle** — per employee / health-check campaign.
4. **B2C later** — premium history/trends/family profiles, only after trust/privacy foundation is stronger.

## Demo story for a CEO or instructor

1. Paste a CBC panel.
2. Show structured interpretation instead of a chatty paragraph.
3. Ask a follow-up such as “แล้วอันนี้ต้องกังวลไหม” to demonstrate context.
4. Ask “ช่วยเขียน Python” to demonstrate the symbolic gate and zero unnecessary LLM call.
5. Explain the business path: white-label result education → trend tracking → lab re-engagement.

This 60-second demo communicates product discipline, cost control, safety boundary, and commercialization path.

## Critical boundary before real commercialization

A real launch requires a deliberate regulatory and privacy workstream. At minimum assess:
- intended use and whether claims could place the software inside medical-device regulation;
- Thailand PDPA and health-data handling;
- authentication/authorization;
- retention/deletion policy;
- encryption and secrets management;
- vendor data-use terms;
- model output evaluation;
- clinical/laboratory expert review;
- incident and escalation handling;
- terms, consent, and disclaimers.

The coursework V0.1 deliberately avoids claiming diagnosis or treatment.
