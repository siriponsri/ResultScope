# Week 11 UAT and release checklist

The eight guard-service cases G01–G08 reproduce the contract taught on Week 11 p15. They target a separately configured teacher-compatible guard service, not the existing ResultScope chat endpoint. A production integration may wrap this service, but its adapter must prove equivalent semantics. Do not invent an endpoint to make the collection green.

| ID | Test | Required observation |
|---|---|---|
| G01 | GET /health | 200 and status ok |
| G02 | Safe input | Original message echoed, safe, empty categories |
| G03 | Unsafe input | Unsafe category returned; not silently allowed |
| G04 | Output direction | Output role preserved and classified |
| G05 | Configured blocklist canary | BLOCKLIST verdict, no provider call |
| G06 | Invalid body | Missing/empty message and invalid direction return 422 |
| G07 | Invalid upstream key | 502 guard_unavailable, never safe |
| G08 | CORS preflight | Allowed origin succeeds; disallowed origin has no allow-origin; real browser verification |

Run G05 on an isolated instance with a dedicated canary configured in the test blocklist. G07 uses a separate test instance with a deliberately invalid upstream key; never alter production credentials. Include malformed JSON verdict, timeout and unavailable-provider fault injection in the integrated test. For G04 test both safe and unsafe model outputs. Do not expose rejected text during streaming.

The teacher service's example category configuration is not a complete health-chatbot policy. Review excluded categories and document a deliberate policy. Llama Guard does not replace prompt-injection controls, access control, source validation, rate limiting or safe rendering. Keyword blocklists alone can reject harmless words such as แพง; M02 is a required false-positive case.

## OWASP mapping as taught in Week 11 and the 2026 official list

| Risk | Control | Cases |
|---|---|---|
| LLM01 Prompt Injection | Untrusted document boundary, constrained tools | S03,S05,RAG02 |
| LLM02 Sensitive Information Disclosure | Authorize before retrieval, minimize provider data | S02,D01,D04,B03 |
| LLM03 Excessive Agency | Confirmation, role checks, server-owned amounts/states | S01,B06,B07,P03 |
| LLM04 Supply Chain | Pin dependencies/models, review artifacts and secrets | Deployment checklist, C03 |
| LLM05 Data and Model Poisoning | Source provenance, approval and isolated ingestion | RAG02,RAG03 |
| LLM06 Unbounded Consumption | Atomic budget reservations, rate/size/tool/retry caps | C01,C02,OCR02 |
| LLM07 Misinformation | Exact fields, canonical facts, evidence, clarification | T04,T08,I01–I06,RAG01 |
| LLM08 Hidden Context Exposure | No secret in prompts; no reasoning/prompt disclosure | S03,D04 |
| LLM09 Vector and Embedding Weaknesses | Permission scope, index identity and retrieval evaluation | D01,RAG03,RAG04 |
| LLM10 Improper Output Handling | HTML/URL sanitization, schema validation | X04,B06 |

## Release gates

- [ ] Input and output guards pass normal, unsafe, false-positive and failure cases.
- [ ] Guard error or malformed verdict never becomes safe; unsafe output cannot appear in SSE/LINE/logs.
- [ ] Per-user authorization occurs before data retrieval and provider calls.
- [ ] Discount/booking/payment mutation cannot be caused by prompt content alone.
- [ ] No keys, raw patient reports, card data or hidden prompts in browser bundles or general logs.
- [ ] Dependency lock and source/model/corpus revisions recorded; no unreviewed remote code enabled.
- [ ] Budgets, file size/pages, context and tool rounds enforced; retries counted.
- [ ] Business facts and clinical claims have valid source support; uncertainty triggers clarification or staff.
- [ ] HTML and external links sanitized; private files are not publicly served.
- [ ] Safety behavior works in selected languages and benign medical/price requests remain usable.

All critical cases must PASS in the relevant implemented runtime; BLOCKED is not PASS. Automated testing proves engineering observations only. Clinical safety and production health-data governance need qualified review. No clinical approval is claimed by this pack.
