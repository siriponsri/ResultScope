# Requirements baseline

Date: 2026-10-05 (Asia/Bangkok). Owner instructions take precedence over lecture examples. CONFIRMED denotes interview intent, not implemented software.

| ID | State | Requirement | Acceptance evidence |
|---|---|---|---|
| R01 | CONFIRMED | A realistic simulated health-check business selling its own packages; ResultScope is a provisional brand. | All mock records carry is_demo=true; no affiliation claims. |
| R02 | CONFIRMED | Serve individuals/families and organizations through conversation. | T01–T10 and B01–B04 cover both segments; no employer access to employee reports. |
| R03 | CONFIRMED | LLM chooses intent, clarification, retrieval and proposed actions. | Paraphrases and follow-up changes work without an intent keyword tree; X01–X03. |
| R04 | CONFIRMED | English website interface, multilingual conversation. | UI controls remain English; Thai/English/Japanese cases preserve values and evidence; unsupported language confidence triggers clarification. |
| R05 | CONFIRMED | Full sales journey including additional packages based on confirmed current lab reports. | Recommendations explain evidence, alternatives and staff-review needs; no automated diagnosis or abnormal-result upsell. |
| R06 | CONFIRMED | Website live chat, staff dashboard and full LINE OA chatbot. | H01–H04 and L01–L05; staff takeover prevents simultaneous bot replies. |
| R07 | CONFIRMED | Multiple credible mock branches with a real map API. | Three clearly marked demo locations; live map loads with attribution and restricted key. |
| R08 | CONFIRMED | In-center and organization onsite services. | No home collection promise; organization quote stays with chat and staff. |
| R09 | CONFIRMED | Customer accounts, history, saved reports and longitudinal comparison. | Identity and report access enforced before retrieval; account-link and unit mismatch tests pass. |
| R10 | CONFIRMED | Booking and payment through conversation and staff; PromptPay, cards and pay at center. | Server owns totals and statuses; signed sandbox webhook and idempotency tests pass. |
| R11 | CONFIRMED | Prioritize Typhoon and OpenThaiLLM; use LightRAG with embeddings and lexical retrieval. | Record exact model identity and embedding dimension; LightRAG mix and BM25 tested separately. |
| R12 | CONFIRMED | Free or <=300 THB monthly preferred; expansion may be proposed. | No spending permission inferred; cost cap and resource measurements are release evidence. |
| R13 | CONFIRMED | Use teacher sources as primary implementation and assessment guidance. | Week 11 eight guard tests and Week 12 submission matrix included. |
| R14 | CONFIRMED | Modern minimal professional UI, original purple, animation; design autonomy granted. | Composer is primary; optional cards; reduced motion and accessibility cases pass. |
| R15 | CONFIRMED | Use supplied report artifacts for demo and local-agent automated tests. | Six source PNG hashes match; five minimum image tests plus sixth coverage; oracle excluded from runtime. |
| R16 | CONFIRMED | Medical references real; expert referral for cases needing assessment; off-topic guard redirects or offers staff. | S03,S04,S05,M01–M03 and G01–G08; benign health questions are not indiscriminately blocked. |
| R17 | CONFIRMED | Provide updated business/architecture documents, question sets and UAT checklist. | Traceability and evidence templates included; actual results remain NOT_RUN until executed. |
| R18 | IMPLEMENTED ADAPTER | Evaluate iApp document OCR as an alternative to Typhoon OCR. | Same six held-out reports, critical-field fidelity, latency and actual cost compared; no automatic provider switch for health data. |

## Implemented coursework defaults

18 catalog entries, 3 branch locations, operating hours, booking windows, staff roles and demo refund policy are implemented simulation defaults, not final commercial commitments. Sign-in methods, exact clinical escalation service, retention periods and merchant/provider accounts are open. Do not invent answers to earlier interview replies whose option text is unavailable; the labels “1 and 3” and “all three” alone do not define additional scope.

## Explicitly excluded

Home blood collection; an employer HR portal; autonomous diagnosis, prescriptions or treatment; real payment during UAT; making a production readiness claim from mocked tests; using patient reports as a shared RAG knowledge base; exposing full model reasoning; automatic purchases, refunds or discounts chosen solely by an LLM.

## As built

The v3 package implements the business catalog, encrypted SQLite/PostgreSQL storage, accounts, booking, sandbox payment adapter, staff inbox/takeover, organization quotation, LINE worker/linking, saved reports and history. The primary API is /api/business. LLM and medical evidence modules are shared with the retained /lab workspace. Source verification and offline integration checks are complete; real provider quality, PostgreSQL hosting, LINE delivery, Stripe sandbox and map credentials require live UAT.

Runtime roles are customer, staff, clinical and manager. Clinical is currently a staff-class operational role, not a separate clinician approval workflow. Email verification, password recovery, formal retention automation, granular clinical access segregation and real-money merchant operations are not implemented. These are production extensions, not hidden prerequisites for the offline coursework demo.
