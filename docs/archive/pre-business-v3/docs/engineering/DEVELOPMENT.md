# Development

Install `requirements-dev.txt`, then run `python -m pytest -q`. On Windows use
`scripts/check.ps1`; it installs dependencies, compiles Python and executes the suite.
Use `python -m compileall -q main.py config.py routers services tests` on other systems.
All current automated tests are offline. Explicit provider doubles are not live quality scores.

`tests/test_conversation_v2.py` covers encrypted contexts, guard verdicts/roles, LLM
planning, evidence review, exact observations, retrieval provenance, six PDF fixtures,
report confirmation, cloud limits, origin/access checks and guarded SSE. Legacy tests
remain regression evidence for preserved v1/local components.

For browser checks, install pinned Node development dependencies in the project root:
`npm ci`, `npx playwright install chromium`, then `npm run verify:ui`. The script starts
and stops its own local server using `.venv`, exercises desktop/mobile/reduced-motion,
and saves screenshots plus a manifest under `docs/assets/screenshots-v2`. Some report
and answer flows use explicit API doubles; the manifest distinguishes them from real
local API and screenshot checks. The Windows shell verification was not run on Linux.

Keep the current API free of imports from the old intent/rule answer pipeline. Changes
to model prompts require a new evaluated candidate. Do not add live test calls, automatic
retries/fallbacks or cycle creation to startup. Preserve original fixture/source bytes,
keys, stored settings and ledgers. Check `docs/operations/READINESS.md` before claiming readiness.
