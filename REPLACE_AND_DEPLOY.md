# Replace your project and deploy

1. Back up the current project, especially `.env`, `data/`, saved provider settings and
   the budget ledger. These private files are deliberately absent from this ZIP.
2. Extract the `ResultScope/` folder. Replace the source files in the existing repository
   root with its contents; keep your private configuration/state. If using a new folder,
   copy `.env.example` to `.env` for local development.
3. Read `README.md`. Windows: double-click `START.bat` (Python 3.12 required). Other systems:
   create a virtual environment, install `requirements.txt`, run `uvicorn main:app`.
4. For Vercel, import the root project using the native FastAPI integration. The entrypoint
   is configured in `pyproject.toml`; no custom rewrite/build output is needed.
5. Add server environment variables from `docs/operations/VERCEL_PREVIEW.md`. Live chat
   requires LLM + guard configuration, a session secret, demo access code, Redis and an
   explicit cycle/call cap. Vision and LightRAG are optional separate connections.
6. Deploy/redeploy, open Settings, enter the demo code and test a small conversation,
   a multilingual follow-up and one synthetic report. Inspect usage before wider testing.

Without keys the complete UI, sources, original sample files and motion introduction
are available. AI remains in setup mode; there is no simulated chatbot response.
The package has been tested offline locally, not deployed to your Vercel account.
