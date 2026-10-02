# Phase 2 baseline — 2026-10-02

## Identity and boundaries

- Base revision: `6f7ae8cbf0843dbb7c6d70bdcfb5924778635028` on local `main`.
- Worktree was clean and one commit ahead of `origin/main`; no push or deployment is in scope.
- Project Brain reported `FRESH` at the same HEAD.
- No `.env` contents or credential values were read, printed, or recorded. Baseline API tests used local code and no external provider.
- Phase 1 at this exact HEAD: structural validation PASS; release readiness/G1-data BLOCKED; historical G0 BLOCKED. Its recorded verification is 40 focused corpus tests and 65 project tests.

## Pre-change observations

| Area | Result | Evidence |
|---|---|---|
| API and scope baseline | PASS, 15 tests | `rtk .\\.venv\\Scripts\\python.exe -m pytest -q tests/test_api_contract.py tests/test_lab_scope.py`; exit 0; one existing Starlette/httpx deprecation warning. |
| Business FAQ routing | Baseline limitation reproduced | `classify_lab_scope("What are the lab opening hours?")` returned `outside_lab_scope`; business facts have no approved source. |
| Concern follow-up | Baseline limitation reproduced | With prior user history `Ferritin 7 ng/mL`, `classify_lab_scope("Should I be concerned?", history)` returned `outside_lab_scope`. |
| Unrelated routing | PASS | `Help me write Python` returned `outside_lab_scope`; preserve provider bypass. |
| B01 business retrieval | NOT_RUN at Phase 0; current route baseline is no retrieval | The Phase 0 report records B01 NOT_RUN. Current code inspection confirms no knowledge/retrieval service; Q01/Q03 must not be treated as answered from the planning corpus. |
| B03 output/session security | Baseline gap observed by source inspection | At base HEAD, SSE forwards provider `delta` values directly before any answer/citation validation; `_session_id` trusts the raw cookie value. Existing `tests/test_api_contract.py::test_stream_sends_deterministic_meta_before_llm_delta` covers ordering only, not output validation. No cookie value was captured. |
| Provider/live checks | NOT_RUN | No live provider or embedding call was made. Mocked/local verification is kept separate from live evaluation. |

The historical Phase 0 statements are preserved. This baseline adds evidence about the current Phase 2 candidate start and does not rewrite B01/B03 history.
