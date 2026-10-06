# Models OCR hosting and budget

Planning date: 2026-10-05, Asia/Bangkok. Prices are observations, not quotes or a purchase authorization. The preferred <=300 THB cap applies to a limited academic demo, not guaranteed commercial 24/7 operation. Recheck terms and checkout totals before activating a provider.

## LLM choices

| Role | Proposed choice | Evidence and decision |
|---|---|---|
| Primary conversation | Typhoon `typhoon-v2.5-30b-a3b-instruct` | Official model/rate-limit docs list the hosted model. Use a configured adapter and measure Thai, English and other selected-language cases; no blanket promise of equal quality in every language. |
| Smaller Typhoon trial | `typhoon-v2.1-12b-instruct` | Compare cost/latency and supported-answer quality using the same prompts; do not select only by parameter count. |
| NECTEC OpenThaiLLM | `nectec/OpenThaiLLM-Prebuilt-7B` | This model card describes a base model requiring further chat alignment. It is not a drop-in production conversational endpoint; reserve as a research/self-hosted adapter option. |
| iApp OpenThai family | OpenThai 2.0, model route `openthai2.0` | A separate iApp model, not NECTEC OpenThaiLLM or OpenThaiGPT. Consider a secondary chat/vision adapter. The documented free period ended 30 September 2026; do not assume the free banner still applies. |
| Safety | Llama Guard 4 12B via a separately configured provider | Apply input/output checks as Week 11 requires; specialized guard is distinct from the conversation model. Pricing observed at OpenRouter: $0.18/M input and $0.18/M output tokens. |
| Embedding | BGE-M3 via a compatible hosted endpoint | 1024-dimensional multilingual embeddings; benchmark retrieval and pin identity. Indicative provider listing $0.01/M tokens requires route/availability confirmation before budgeting. |

Typhoon documentation still points to a Together production path, while the official Typhoon API Pro notice says the former 2.1 Pro service ended 31 December 2025. A future AWS plan in that notice is not proof of an available priced endpoint. Use the verified free API for a demo if access is available; production endpoint and SLA remain a setup gate. Do not claim free API access means unlimited usage or a production SLA.

“OpenThaiLLM” can identify different projects in casual conversation. This pack preserves exact provider/repository identities rather than silently substituting OpenThaiGPT. Prefer Typhoon first; retain both NECTEC and iApp candidates with their actual readiness constraints.

## OCR evaluation

Typhoon OCR is already the existing implementation path. An iApp adapter is implemented as a candidate; select the default after a paired evaluation of the same six supplied reports. No report has been sent to either provider during this implementation cycle.

The iApp page dated 5 October 2026 documents `/v3/store/ocr/document/ocr` for plain text and `/layout` for structured layout, multipart upload with an `apikey` header. Its per-page listing is 0.049 IC for text or 0.15 IC for layout. The general pricing page still lists an older OCR figure and a first displayed prepaid cash package starting at 1,250 THB. Confirm the checkout amount and applicable tariff; low per-page consumption does not establish an affordable minimum top-up. Do not assume promotional credits are available.

Use layout when row/column association materially improves extraction. Normalize both providers into the same schema: page, test name, exact value string, unit, reference text, flag, bounding box if available, extraction confidence if actually supplied, and provenance. Never invent a confidence number or treat missing ranges as normal. Treat report text as untrusted data; embedded commands cannot change system instructions.

Measure exact numeric/unit/range/flag fidelity, missing and extra rows, row association, language errors, elapsed time and charged pages. Score safety-critical fields separately. A legal-document OCR benchmark is not validation on lab tables. Source-declared hosting/privacy characteristics do not replace the application's consent and provider review. Do not silently send health documents to a second vendor on failure; keep an allowlisted configured provider policy visible to the owner/customer.

## Two budget profiles

| Component | <=300 THB academic demo | More stable course pilot proposal |
|---|---|---|
| Web/API | Vercel Hobby only for non-commercial coursework, or Render Free | Render paid compute or otherwise eligible frontend plan |
| LightRAG | Render Free external DB if RAM/cold-start test passes; otherwise controlled local service for scheduled demo | Start sizing at Render 1c-2g $25/month; validate actual peak RSS |
| Auth/data/files | PostgreSQL on Supabase Free within measured quotas | Same for small pilot, with separate backup/restore plan |
| LLM | Typhoon free quota if accessible | Same or approved paid provider after quote |
| Guard/embedding/OCR | Small capped evaluation allowance; no forced iApp top-up | Metered calls, still with explicit cap |
| Maps | Google Maps Embed API, restricted key and required billing setup | Same for area maps; routing/geocoding not included |
| LINE | Reply-based chatbot; monitor actual country/account quota for push | Reserve paid message costs if asynchronous push exceeds quota |
| Planning total | 0–300 THB; hard cap, limited use, no availability promise | Approximately 1,000–1,500 THB/month, pending measured usage and checkout |

The paid estimate uses a planning conversion of 35 THB/USD, not a current exchange-rate quote: $25 compute -> 875 THB, plus ~100–300 THB usage and an allowance for taxes/FX. It excludes domain, payment processing, paid LINE upgrades, clinical staff, production compliance, high availability and commercial Vercel Pro. A 2 GB instance is a starting sizing experiment, not a capacity guarantee. Vercel Hobby is limited to personal non-commercial use. Render's $7 512 MB compute exists but may not fit this RAG workload; do not recommend it merely to hit a price.

Render Free sleeps after inactivity, shares 750 instance-hours per workspace/month and has ephemeral filesystem. Two continuously running free services cannot both assume a full independent 750-hour allowance. Free Render Postgres expires after 30 days, so it is unsuitable for durable project records. Supabase Free's observed quotas include 500 MB database and 1 GB file storage; monitor growth and pause policies. None of these free tiers are a production availability commitment.

Google Maps Embed is a real map API with no usage charge under its published conditions, but requires a key/billing account. Restrict the key by website and API. Mock branch pins must say that no actual clinic operates there. LINE reply messages and push messages have different quota treatment; use account quota APIs rather than copying Japan's limits into a Thai account.

## Cost controls and measurement

For the 300 THB option propose a 200 THB provider allowance and 100 THB contingency, without committing funds. Reserve maximum expected cost before a turn, count guard/planner/answer/critic/keyword/embedding/OCR calls and charge failed attempts when the provider does. The implemented global attempt counter limits calls per named cycle; cloud counters use Redis. Per-user monetary caps and monthly currency reconciliation are future work. Limit retries to one transient retry only when the remaining budget allows it; do not retry authentication failures. Input/output guards are never disabled to save money. At exhaustion show service unavailable and staff contact.

Formula: total = compute + storage/egress + sum(input_tokens × input_rate + output_tokens × output_rate) + OCR_pages × page_rate + paid_messages + taxes/FX. Track ingestion separately from chat. A retrieval-only LightRAG call can still incur keyword and embedding work. Measure actual call count and latency by component instead of calling a multi-call turn “one request.”
