# ResultScope Lab Demo — business brief

Status: **development draft; owner-approved business sources pending**

## Confirmed scope

| Field | Confirmed value | Evidence |
|---|---|---|
| Business type | One health diagnostic laboratory for the coursework prototype | `docs/final-project-plan/phases/PHASE_1_BUSINESS_KB.md` |
| Working name | `ResultScope Lab Demo` — development-only label, not a real legal or public name | `docs/final-project-plan/phases/PHASE_1_BUSINESS_KB.md` |
| Product boundary | A controlled laboratory-information experience; not a general medical chatbot | `AGENTS.md`, `BUSINESS_BRIEF.md` |
| Primary audience | Laboratory customers who need help locating and understanding published service information | Phase 1 plan and master plan |
| Operational truth | Only owner-approved public business sources may establish hours, address, contact, prices, preparation, turnaround, booking, payment, cancellation, or refund facts | Phase 1 plan |

## Pending owner facts

The following are intentionally unknown and must not be filled from model output, search snippets, or synthetic fixtures:

- legal/public laboratory name and approved brand wording;
- public address, map/location instructions, phone, email, website, and social channels;
- opening hours, holidays, walk-in and booking rules;
- service catalog, prices, currency, specimen/preparation requirements, and result turnaround;
- payment, cancellation, refund, privacy, and escalation policies;
- owner-approved educational content and the source/version that permits release.

Until those facts are supplied and approved, customer-facing answers for them must return `PENDING_SOURCE` with a real contact fallback only after a contact source exists.

## User and organization jobs

Customers should be able to ask about published services, prices, preparation, opening hours, result delivery, and what to do when information is missing. Laboratory owners should be able to trace each answer to a versioned source and see which questions remain unanswered. The prototype must not claim a booking, payment, diagnosis, prescription, dose change, treatment plan, or access to another customer's information.

## Evidence and release posture

This brief is a planning artifact, not an approved business corpus. The source manifest records the planning references and the pending owner source pack separately. Synthetic services and evaluation cases are development fixtures and are never release-eligible.
