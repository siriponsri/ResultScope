# Course traceability

Priority: latest explicit owner decisions -> Final Project + Week 12 deliverables -> Week 11 security and relevant weekly implementation guidance -> current design references. Owner reports instructor permission for a realistic simulated business on 2026-10-05; this clarification resolves the real-business ambiguity and is not presented as a quote from the uploaded DOCX.

| Source | Applied guidance | Artifact / acceptance |
|---|---|---|
| Final Project.docx, business selection | Own credible business data, >=15 services or equivalent 5 pages, reasonable images, no real personal data | 18 implemented services; six synthetic reports; provenance labels |
| Week 1 pp6–9 | Working LLM/API/UI/Vision; report outline; explain architecture and one's contribution | As-built scope distinction; report; oral questions below |
| Week 2, NLP/tokenization examples | Thai word boundaries matter | Thai-aware lexical preprocessing; preserve original numeric strings |
| Week 3, preprocessing/training/evaluation | Separate preparation and evaluation | Held-out fixtures; no test oracle in RAG; no invented training claims |
| Week 4, local LLM deployment | Model size/hardware/quantization constrain deployment | Hosted inference; OpenThaiLLM base not loaded in a free 512 MB service |
| Week 5, REST/API/SSE/model evaluation | Correct schemas/status/auth and latency evidence | OpenAPI-backed adapters; Postman; no unguarded SSE tokens |
| Week 6, UI and backend | Usable messages/status/error/cancel and clear components | UI brief and X01–X05 |
| Week 7, cloud/API context | Stateless service and explicit conversation context | Durable database; no reliance on ephemeral process memory |
| Week 8 pp1–22 and setup screenshots | LINE OA, Messaging API, signatures and reply flow | Shared channel adapter, idempotency, L01–L05 |
| Week 9, LightRAG | Knowledge retrieval, embedding and query modes | BM25 + LightRAG mix distinguished; source-preserving fusion |
| Week 10, vision/API/render | Pass image content, structured extraction, limitations | Six PNG inputs; exact fields; confirmation and OCR comparison |
| Week 11 pp3–18 | Input/output guards, OWASP risks, fail-closed, eight endpoint tests | G01–G08 and extended security checklist |
| Week 12 p7 | LLM/API/UI/RAG/Prompt/Safety all work | UAT evidence by scope; missing features BLOCKED |
| Week 12 p8 | Ten text, five image, five safety cases with outputs, verdicts and times | T01–T10, I01–I06, S01–S05 in tests/uat_cases.json |
| Final Project improvement requirement | Three before/after improvements | tests/improvements_template.json; identical cases/revisions recorded |
| Final Project diagrams | Architecture and one-message flow match real system | As-built business architecture and one-message sequence in 03_ARCHITECTURE.md |
| Week 12 p8 | Google Doc and PDF, developer role table, Drive folder | DOCX/PDF report included; native Google Doc and upload still pending |
| Final Project and Week 12 p6 | Video <=3 minutes | 180-second script; use stricter limit despite p9 saying 4 minutes |

## Course calendar in Asia/Bangkok

3 October 2026: business-name notification date (past; do not claim submitted). 10 October: progress and exam. 17 October: submission. 24 October: presentation. The attachment is the authority for these dates; no calendar action was taken.

## Submission gates

- [ ] Actual application runs from source on a clean machine, with Windows launch instructions and pinned dependencies.
- [ ] Every endpoint shown in the final as-built diagram works and has evidence.
- [ ] T01–T10, >=5 I-cases and S01–S05 contain actual outputs, pass/fail and elapsed times.
- [ ] Three matched before/after results contain actual evidence and explanations of regressions as well as improvements.
- [ ] Staff identity, selected model/provider, retrieval configuration and deployment revision recorded.
- [ ] Developer name/student ID and truthful role/progress table completed; AI assistance is disclosed without claiming AI as a student partner.
- [ ] Report imported to Google Docs, PDF verified, source archive and <=180-second demo placed in the submission folder.
- [ ] No fabricated result, real patient data, payment credential or API key included.

## Individual oral-exam preparation

1. Trace one Thai question through the actual runtime, including each model call and guard.
2. Why does the LLM choose intent while the backend validates prices and access?
3. What evidence distinguishes BM25 from embeddings and LightRAG graph retrieval?
4. How are test oracles prevented from leaking into the knowledge base?
5. What does the image pipeline actually read, and how are unreadable values handled?
6. Which failure does Llama Guard not solve, and which backend control covers it?
7. How can a payment be confirmed without trusting an uploaded screenshot?
8. What happens if a LINE event is delivered twice or its reply token expires?
9. Which free-tier constraint fails first at 10x users, and what measurements support that answer?
10. Which three changes demonstrably improved outcomes, and which outcomes remain unmeasured?
