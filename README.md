# ResultScope 3.0

A complete coursework business web app for a health-check center, led by an LLM conversation. English interface; multilingual AI responses. Original purple identity with six owner-supplied laboratory photographs. Business packages and locations are realistic simulations; medical evidence is sourced from real references.

## Start

Python 3.12. Windows: use `START.bat`. macOS/Linux:

```sh
python3.12 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
# For a NEW installation only; preserve an existing .env.
cp .env.example .env
uvicorn main:app --reload
```

Open http://127.0.0.1:8000, `/app` for customers, `/staff` for staff, `/lab` for the retained laboratory workspace. The business catalog, account, booking, staff and report-management routes are implemented. AI and external integrations require owner credentials; without them, requests fail visibly rather than fabricate replies.

Create staff with `python scripts/create_staff.py --help`; no production password is shipped. Add business variables from `.env.business.example` to your existing configuration. Local data uses encrypted SQLite; hosted use requires PostgreSQL and a persistent encryption key.

## Included

- 18 own-price packages, 3 branches, Google Maps Embed integration, organization quotations.
- LLM planner, real-source retrieval, grounded answer, evidence critic and two-sided Llama Guard.
- Explicit booking/payment previews, durable history, report review/correction, comparison context and deletion.
- Staff inbox/takeover/replies, manager catalog controls, sandbox checkout/webhooks/refunds, pay-at-center receipts.
- LINE signature verification, durable worker/outbox, text/image chatbot and explicit account linking.
- Typhoon default; configurable compatible endpoint; iApp OCR option; clear NECTEC OpenThaiLLM limitations.
- 58 runtime evidence records, 68-source discovery manifest, downloaded source files and 23 new verified intervals.
- Six original synthetic OCR reports, isolated answer key, 73-case UAT plan, Week 11 checklist and report.

## Deploy and test

[Vercel and Render setup](docs/business-v3/DEPLOYMENT.md) includes the required database, key and provider configuration. Source is prepared for deployment; no external deployment or live integration test was performed in this delivery.

```sh
pip install -r requirements-dev.txt
python -m pytest -q
python scripts/verify_medical_sources.py
npm install
npx playwright install chromium
npm run uat:business
```

The browser harness starts a temporary isolated database and explicit LLM/OCR doubles. It does not validate real model quality. Read [verification](docs/business-v3/VERIFICATION.md) and [local-agent handoff](docs/business-v3/LOCAL_AGENT_HANDOFF.md) before live testing. Never deploy the fixture server.

[Full documentation](docs/README.md) · [Replacement instructions](REPLACE_README.md) · [Medical provenance](knowledge/medical_sources/README.md)
