# Product overview

**ResultScope Laboratory Assistant** is a local prototype for source-linked laboratory education. It organizes an explanation around the values a person supplied and keeps the calculation basis available for inspection.

## The problem and proposed value

A reader may have a number without knowing its unit, its report-specific reference range, or which contextual question to ask next. An unconstrained answer can make that uncertainty harder to see. ResultScope is designed to make the input, extracted facts, evidence, and limitations visible together.

For a laboratory or clinic, the commercial hypothesis is an explanation layer adjacent to existing result delivery. For an individual reader, the intended value is a clearer conversation with a qualified professional. Neither clinical benefit nor operating savings has been measured in this project.

## Current product surface

The application opens with a minimal landing page. **Open workspace** or normal scrolling leads directly into the conversation on the same page. **Try an example** loads synthetic text without submitting it. The composer action is **Send**. **Attach report** opens a JPEG/PNG document drawer beside the chat, or a full-screen panel on mobile. Extraction review permits corrections before values become confirmed context. Results combine selectable values, supplied-range visualization, explanation text, available sources, and optional calculation details. Follow-ups stay in the same laboratory context until the reader starts a new analysis.

Administrative configuration is separate from ordinary use. Explicit local-demo mode is required; it does not establish patient accounts or organizational access control.

| Product area | Local implementation | Dependency or limitation |
|---|---|---|
| Intake and review | English interface, English/Thai entry, bounded text, synthetic examples | Examples do not define universal ranges |
| Laboratory analysis | Python scope checks and supplied-range flags | Incomplete context remains incomplete |
| Explanations | Retrieval, provider prompt, validated final answer | Relevant available sources and authorized provider access |
| Image reading | Image validation, OCR boundary, correction and confirmation | Optional OCR configuration; no PDF support |
| Traceability | Source metadata and inspectable rulebook | Not a guarantee that all generated errors are caught |
| Administration | Local settings, masked state, mock probes | No production secret store or multi-tenant administration |

## Choices to evaluate

The key choices are supplied-range discipline, explicit image confirmation, laboratory scope, local evidence selection, and a unified result view. The formal medical interface makes them easier to inspect; it does not change the backend's authority or the evidence required for release.

Public-source lookup uses local metadata and aliases to find pinned records. It does not imply a hosted search platform or universal medical knowledge. Synthetic business fixtures and public hospital references cannot replace a partner's approved business facts.

## Questions for product evaluation

| Hypothesis | Practical evaluation | Evidence to record |
|---|---|---|
| Readers understand their input better | Ask users to identify a value, unit, source range, and missing context | Task outcomes, misunderstandings, assistance required |
| Review prevents transcription mistakes | Seed a known image extraction error and observe correction | Field-level correction and confirmation outcomes |
| Sources improve assessability | Ask reviewers to locate support and source limits | Attribution and source-identification errors |
| The workflow fits a partner service | Observe a named laboratory or clinic process | Handoffs, responsibilities, integration needs |
| A partner can operate it responsibly | Review rights, incidents, support, and provider controls | Named owners, gate receipts, unresolved risks |

Set acceptance criteria with intended users and clinical/governance owners before a pilot. No target percentage or commercial outcome is asserted here.

The next decision is whether to fund controlled evaluation with an approved corpus and a named partner workflow. It is not a launch decision. [Readiness](../operations/READINESS.md) records blockers; the [roadmap](ROADMAP.md) describes the proposed HIS and pharmacy path.
