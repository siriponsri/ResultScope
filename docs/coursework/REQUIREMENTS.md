# Coursework requirement map

This map records the supplied coursework requirements against the current
repository evidence. It is an English developer record; Thai corpus and
evaluation inputs remain unchanged in `examples/coursework_demo_v1/`. A fixture
or expected answer is not an observed live result.

| Requirement | Existing implementation or evidence | Evidence mode | Status | Remaining gap |
|---|---|---|---|---|
| Selected business identity, audience, services, policies, chatbot must/must-not rules, and at least 10 FAQ topics | `examples/coursework_demo_v1/corpus/01_BUSINESS.md`, `02_POLICIES.md`, `04_SERVICES.md`, `evaluation/FAQ.md` | Synthetic source corpus and expected evaluation input | PARTIAL | The business is explicitly fictional; owner-approved real-business evidence is absent. |
| Sufficient knowledge: five document pages or 15 products/services | `examples/coursework_demo_v1/corpus/04_SERVICES.md`, `corpus/services.json` | Synthetic corpus inspection | PRESENT for synthetic demo | This does not prove approved real-business knowledge. |
| No real personal data without permission | `AGENTS.md`, `docs/engineering/DATA_GOVERNANCE.md`, synthetic package labels | Source policy and implementation boundary | PRESENT for documented boundary | Human consent and operational privacy approval are not established. |
| Customer usability, loading states, and meaningful errors | `templates/`, `static/js/`, `docs/user/USER_GUIDE.md`, `docs/assets/screenshots/` | Local UI implementation and labelled screenshots | PRESENT locally | Independent human usability evidence is not run. |
| LLM, matching APIs, Thai RAG, prompt constraints, and safety behavior | `services/`, `routers/`, Thai corpus under `examples/coursework_demo_v1/`, `tests/` | Offline implementation and regression tests | PARTIAL | No new live provider cycle or live quality evidence is authorized in this task. |
| Ten question cases with actual response, pass/fail, and response time | `examples/coursework_demo_v1/evaluation/questions.jsonl` | Expected-case fixture only | NOT_RUN | Actual responses, timings, and signed evaluation receipts are missing. |
| Five image cases with analysis, pass/fail, and response time | `examples/coursework_demo_v1/evaluation/images_expected.json`, five images, `tests/test_phase3_images.py` | Fixture and offline validation | PARTIAL | Actual image analysis results and timings are not established. |
| Five safety cases with result, pass/fail, and response time | `examples/coursework_demo_v1/evaluation/safety.json`, safety tests | Fixture and offline regression | PARTIAL | Timed observed-case report is missing. |
| Three improvements with honest before/after evidence | `docs/evidence/LOCAL_PRODUCT_REFRESH_CLOSEOUT.md`, `docs/evidence/DESIGN_REVIEW.md` | Local implementation/review records | PARTIAL | Controlled before/after user or quality measurements are missing. |
| Architecture and one-message data-flow diagrams match implementation | `docs/assets/diagrams/architecture.svg`, `message-flow.svg`, `docs/engineering/ARCHITECTURE.md` | Source diagrams and code guide | PRESENT for current prototype | Future integrations remain proposals and are not implemented. |
| Reproducible source, developer role/progress record, and demonstration video | Repository source, `AGENTS.md`, `docs/product/DEMO_SCRIPT_180S.md` | Repository and planning evidence | PARTIAL | A completed demonstration video and submission progress record are absent. |
| Google Doc/PDF submission with shared-folder link | `docs/user/ResultScope_User_Guide.pdf` is a product guide | Local document artifact only | NOT_RUN | No Google Doc, shared-folder link, or submission package is created by this task. |

## Supplied-source notes

The supplied course materials identify a three-minute demonstration target in
one place and a four-minute limit in another. The current target remains three
minutes because it satisfies both statements. Supplied course dates are not
deployment dates. This repository hygiene task does not create business data,
run live evaluation, or publish coursework attachments.
