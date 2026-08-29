# DEPLOY_CHECKLIST.md — ResultScope

## Environment variables
Required:
- APP_NAME=ResultScope
- APP_TAGLINE=Laboratory results, in context.
- OWNER_NAME=<your actual name>
- APP_ENV=production
- LLM_BASE_URL=https://openrouter.ai/api/v1
- LLM_API_KEY=<set in Vercel only>
- LLM_MODEL=<your selected model>
- STORAGE_BACKEND=auto
- CORS_ALLOWED_ORIGINS= (leave empty for the same-origin web app)

Optional:
- UPSTASH_REDIS_REST_URL
- UPSTASH_REDIS_REST_TOKEN

## Pre-deploy checks
- .env is not committed
- API key is not printed in logs
- local app runs
- /health returns ok
- /api/v1/rules returns rulebook version 2026.08
- in-scope lab prompt works
- stream emits analysis_meta before the first LLM delta
- selecting extracted values updates the range inspector
- “How this answer was grounded” opens and is keyboard accessible
- out-of-scope prompt is blocked
- reset conversation works
- mobile layout looks acceptable
- reduced-motion preference removes nonessential motion
- owner name is visible in UI

## Vercel checks
- root main.py exports the FastAPI app for zero-config discovery
- removed legacy api/index.py and vercel.json have not been recreated
- static files load in deployment
- homepage works
- streaming chat works or gracefully degrades
- no server crash on first load

## Submission smoke test
1. Open deployed URL
2. Verify branding and owner name
3. Ask: HbA1c 6.1% หมายความว่าอย่างไร
4. Ask: ช่วยเขียน Python ให้หน่อย
5. Verify second prompt is blocked
6. Start new analysis
7. Capture final URL for submission
