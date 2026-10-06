# Local setup

Use Python 3.12. `START.bat` enters the project directory and invokes
`scripts/start.ps1`. It creates `.venv` and `.env` only if missing; existing `.env`,
keys, data and usage ledgers are preserved. The first run installs dependencies.
A setup-mode interface is available before connecting any provider.

To activate chat, edit `.env` server-side:

1. Set `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL` for an OpenAI-compatible JSON-capable model.
   The defaults target OpenTyphoon; the existing local admin catalog also supports
   explicitly selected native Anthropic LLM configurations.
2. Set `GUARD_BASE_URL`, `GUARD_API_KEY`, `GUARD_MODEL` for Llama Guard, or set
   `GUARD_SERVICE_URL` for the teacher-compatible `/check` service.
3. Generate `SESSION_SIGNING_KEY` with `python -c "import secrets; print(secrets.token_urlsafe(48))"`.
4. Choose a unique `PROVIDER_BUDGET_CYCLE_ID`, explicit `PROVIDER_BUDGET_LLM_LIMIT`
   and `PROVIDER_BUDGET_OCR_LIMIT`, then set `PROVIDER_NETWORK_ENABLED=true`.
5. Run `python scripts/provider_budget_cycle.py create` once to authorize this local cycle.
   Run `snapshot` to inspect it and `close` to close it. Existing cycles cannot be replenished
   by restarting, retrying or changing a configured limit.
6. Restart the app, open Settings, and send a small laboratory question.

A normal conversational turn makes five provider calls: input guard, planner, answer,
evidence reviewer and output guard. Some failures stop earlier. Semantic search adds
one HTTP request to LightRAG, whose own embedding/model costs are outside this app's
counter. Guard and retrieval requests consume the local LLM allowance. Vision consumes
OCR allowance (one call per page for Typhoon); report reading also needs input/output
guard checks, plus one LLM structuring call for Typhoon.
Set limits deliberately; the old default of five LLM calls permits about one full turn.

Optional report reading: set `VISION_ENABLED=true` plus vision key, base URL and model.
Typhoon OCR transcribes images, then the LLM structures them. A compatible vision chat
model can directly emit the report schema. Provider compatibility must be checked with
your selected model; no successful live call is represented by the offline tests.

Optional local admin: the legacy `/admin/settings` requires `LOCAL_DEMO_MODE=true`, a
configured admin password hash and encryption key. It is disabled on Vercel. Do not
expose this development server publicly. See [admin guide](ADMIN_GUIDE.md).
