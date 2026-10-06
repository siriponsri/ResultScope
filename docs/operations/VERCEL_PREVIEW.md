# Vercel preview deployment

The complete, current instructions are in [business deployment](../business-v3/DEPLOYMENT.md). Use the repository root, Python 3.12 and api.index:app with the included native FastAPI configuration. The business API requires durable PostgreSQL and BUSINESS_DATA_KEY in hosted environments. Configure a shared Redis attempt budget before enabling AI. LightRAG and the LINE worker are external services.

A successful /health response establishes API liveness only. Test /api/business/session, database persistence across instances, guard failure, signed payment callbacks, LINE delivery and the real map embed separately. This delivery contains configuration and local evidence; it does not claim a completed Vercel deployment. Vercel Hobby eligibility for coursework must not be treated as permission to run a commercial clinic.
