# ResultScope Laboratory Assistant

## Purpose

Help a reader understand laboratory information while keeping supplied values, units, reference ranges, uncertainty, and evidence visible. The product is an educational assistant, with Python-owned limits around what may be answered and how returned statements are checked.

## People and jobs

| Audience | Intended job | Evidence still needed |
|---|---|---|
| People reading a report | Understand what was measured and what context to bring to a professional | Comprehension, error recovery, and accessibility studies |
| Laboratory or clinic staff | Present a consistent explanation workflow around issued results | Workflow fit and content approval responsibilities |
| Product and operations leaders | Evaluate a bounded explanation layer for a future service | Commercial rights, unit economics, support load, and partner demand |
| Local administrators | Configure and inspect providers without exposing stored keys | Production identity, secret management, and multi-instance operation |

These audiences describe product intent, not customers, contracts, deployment, or clinical adoption.

## Core experience

1. Enter a laboratory question or values, or choose a JPEG/PNG report image.
2. For an image, inspect and correct every extracted field before confirmation.
3. Review deterministic values and supplied-range status alongside the explanation.
4. Open available sources and calculation details when useful.
5. Ask a follow-up in the same context or start a new analysis for a different report.

Text and image inputs converge into one analysis experience. Unrelated requests are rejected locally. Missing source evidence, missing ranges, and failed validation remain explicit rather than being filled with guessed facts.

## Durable boundaries

- Laboratory education only; no diagnosis, prescriptions, dose changes, or treatment plans.
- User-supplied reference ranges determine personal low/high/within flags. A missing range stays unknown.
- Python remains authoritative for routing, deterministic facts, and output checks. Provider language cannot redefine these controls.
- Public references, guideline notes, synthetic business fixtures, and approved business facts remain separate data classes.
- Provider transport requires explicit network opt-in and an active attempt cycle. Local demonstration must remain inspectable offline.
- English navigation supports English and Thai input; responses are instructed to preserve the user's chosen language.
- A screenshot, mocked answer, test pass, or interface improvement is not clinical validation.

## Product character

ResultScope should feel like a clear, professional medical workspace: calm, formal, readable, and precise. Its approved C + 2 visual identity uses ghost-white surfaces, dark purple ink and diffuse violet/lavender atmosphere in the hero and conversation. Labels describe actions directly; uncertainty is written in ordinary language. The owner explicitly permits diffuse gradients in the hero and chat, overriding the no-slop default ban. The landing recedes on native desktop scroll into the conversation; a document drawer supports report review. No science-fiction HUD, fake workflow editor, decorative canvas or AI-character imagery belongs in this direction. Motion must have reduced-motion and static fallbacks.

The public product name is **ResultScope Laboratory Assistant**. Keep repository names, imports, API identifiers, environment variables, and existing technical IDs as `ResultScope` or their existing code forms. See [DESIGN.md](DESIGN.md) for implemented tokens and [brand guidance](docs/product/BRAND.md) for editorial usage.

## Business hypotheses

An explanation layer could help a laboratory or clinic make issued results easier to discuss, support consistent educational language, and surface useful follow-up questions. These outcomes require measured evaluation. Initial discovery should test comprehension, source traceability, staff review effort, and whether the workflow solves a problem a partner will fund.

Future HIS and pharmacy proposals must retain the current educational limits until a separately governed product scope is approved. There is no current claim of patient-management, ordering, dispensing, prescribing, billing, or interoperability capability.

## Current authority and historical records

This file, [DESIGN.md](DESIGN.md), and documentation under `docs/product`, `docs/operations`, and `docs/engineering` describe the successor product direction. Code remains authoritative for runtime behavior. Retained phase reports and source snapshots may describe earlier visuals, aspirations, or checks. They remain historical evidence and do not change the current candidate's approval status.
