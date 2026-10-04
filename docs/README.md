# ResultScope documentation

This is the English documentation entry point for **ResultScope Laboratory Assistant**. It separates the current local prototype from proposed integrations and preserves evaluation records without treating them as approval of the current candidate.

| Start here if you are… | Read |
|---|---|
| Reviewing the product or business direction | [Product overview](product/OVERVIEW.md), [roadmap](product/ROADMAP.md), [readiness](operations/READINESS.md) |
| Using the application | [Illustrated user guide](user/USER_GUIDE.md), also served at `/static/docs/user-guide.html` |
| Running a local demonstration | [Local setup](operations/LOCAL_SETUP.md), [administrator guide](operations/ADMIN_GUIDE.md) |
| Building or reviewing code | [Architecture](engineering/ARCHITECTURE.md), [development](engineering/DEVELOPMENT.md), [data governance](engineering/DATA_GOVERNANCE.md) |
| Extending the interface | [Brand guide](product/BRAND.md), [product contract](../PRODUCT.md), [design system](../DESIGN.md) |

## How to read the evidence

Current documentation guides the implementation; it is not an approval receipt. [Readiness](operations/READINESS.md) identifies known gates and historical evidence. The [evidence history](evidence/HISTORY.md) indexes original reports retained in a verified archive. Some original evidence and source fixtures contain Thai; these are preserved data, not current instructions.

See [redesign verification](evidence/REDESIGN_VERIFICATION.md), [visual review](evidence/DESIGN_REVIEW.md), and the [historical archive](archive/README.md). Mocked behavior is labelled; previous test totals stay attached to their candidate or report.

## Documentation map

- `product/`: proposition, scope, roadmap, and brand language.
- `operations/`: safe local startup, administration, and release gates.
- `engineering/`: code boundaries, development checks, and data handling.
- `user/`: illustrated user workflow.
- `assets/screenshots/`: captured application screens described by the guide.
- `assets/diagrams/`: architecture and workflow illustrations.
- `security/`: current threat model and guard decision.
- `evidence/`: current checks, visual review, and an English history index.
- `archive/`: original phase instructions and evidence in a checksum-indexed ZIP.
- `vendor/resultscope_evidence_v1/`: pinned public-reference evidence package and offline verifier.
- `examples/coursework_demo_v1/`: synthetic coursework corpus, images, and evaluator inputs.

When a historical instruction conflicts with current setup, use [local setup](operations/LOCAL_SETUP.md). Preserve existing `.env` and virtual environments, keep provider transport disabled for offline work, and never infer authorization for a live call from a screenshot or a catalog label.

## Migration and evaluation

- [Repository hygiene](engineering/REPOSITORY_CLEANUP.md): canonical ownership, archive boundaries, and migration rules.
- [Latest local product refresh closeout](evidence/LOCAL_PRODUCT_REFRESH_CLOSEOUT.md): earlier UI evidence, not a new exact-head review.
- [Documentation tooling](engineering/DOCUMENTATION_TOOLING.md): maintain screenshots and manuals.
- [Owner decisions](product/OWNER_DECISIONS.md): information needed before a pilot.
- [Evaluation plan](product/EVALUATION_PLAN.md): product and academic evidence boundaries.
- [Three-minute demonstration](product/DEMO_SCRIPT_180S.md) and [optional introduction](media/README.md).

## Approved interface direction

- [C + 2 direction and source boundaries](engineering/APPROVED_UI_DIRECTION.md)
- [Motion and document drawer behavior](engineering/MOTION.md)
