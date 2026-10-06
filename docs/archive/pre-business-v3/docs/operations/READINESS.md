# Readiness — ResultScope 2.0

Updated 2026-10-05. This is a replacement source package with Vercel configuration,
not evidence of a clinical release or a completed external deployment.

| Area | Status | Evidence/limit |
|---|---|---|
| LLM conversation architecture | IMPLEMENTED | Planner, grounded generator, evidence review, multilingual prompts; no v1 intent router in v2. |
| Real reference retrieval | IMPLEMENTED | 35 integrity-checked records, 25 distinct source URLs; BM25 active by default. |
| LightRAG adapter | IMPLEMENTED / LIVE NOT_RUN | Read-only `/query/data`, known source IDs, rank fusion; external service not provisioned. |
| Input/output safety | IMPLEMENTED / LIVE NOT_RUN | Llama Guard contract and failure tests; no measured multilingual effectiveness. |
| Report reading | IMPLEMENTED / LIVE NOT_RUN | PNG/JPEG and 1–3 page PDF pixels; user confirmation; actual OCR quality not measured. |
| Supplied demo artifacts | INCLUDED | All six synthetic reports and original companions, checked against supplied manifest. |
| Python suite | PASS | 301 offline tests, including 51 v2 cases. One upstream test-client deprecation warning. |
| Desktop/mobile UI | PASS | 12 browser checks, 10 labeled screenshots; explicit API doubles for model/report flows. |
| Hyperframes motion | PASS | Lint 0 errors/warnings; 38 text elements pass contrast; sampled layout frames clear. |
| Windows starter | IMPLEMENTED / NOT_RUN | Windows batch/PowerShell path preserved; session runs on Linux. |
| Vercel entrypoint | LOCAL PASS / DEPLOY NOT_RUN | Fresh-process cloud guard tests and ASGI routes; no actual cloud deployment. |
| Shared Redis budget | IMPLEMENTED / REMOTE NOT_RUN | Atomic Lua contract tested offline; no remote concurrency/billing validation. |
| Clinical/reviewer approval | NOT_RUN | No human clinical or independent FO review in this cycle. |
| Course live evaluations/video | PENDING | Protocol and script included; no fabricated answers, scores or timings. |

Live provider calls during implementation: **0**. A normal chat turn requires about five
upstream calls. Configure keys, guard, stable session secret, access code, shared Redis
and an explicit cycle/cap before enabling cloud AI. See [Vercel guide](VERCEL_PREVIEW.md).

The ZIP excludes private configuration/state, budgets, virtual environments and installed
dependencies. Preserve those from your installation. Historical v1 documents and artifacts
remain labeled in the archive; their old results do not establish v2 model readiness.
