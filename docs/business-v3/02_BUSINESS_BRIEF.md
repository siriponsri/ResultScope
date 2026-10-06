# Business design

ResultScope is a simulated multi-branch health-check center. Its business purpose is to help individuals and organizations understand available services, book suitable checks and coordinate follow-up through a conversational assistant and staff. Revenue comes from checkup packages, justified follow-up services and organization contracts. Prices are own demo prices, not competitor offers or clinical recommendations.

## Reference businesses and original differentiation

HealthLab's public test/service catalog informs clear item-level explanations and branch navigation. BRIA's official booking catalog informs package comparison and an understandable route to booking. N Health's service and test-catalog material informs operational details such as specimen and turnaround metadata. These are design observations, not evidence that ResultScope is better or affiliated with them.

ResultScope's design distinction is a single evidence-aware conversation spanning questions, confirmed report data, package alternatives, booking, payment status and staff takeover. A user can ask why an add-on is suggested, reject it, compare total costs or ask a person without restarting. Employer coordination and employee medical data stay separate.

## Segments and journeys

An individual first describes goals, budget and existing tests. The LLM asks only missing relevant questions, searches the catalog, explains options with source IDs and presents a draft quote. The user confirms before any booking mutation. A returning customer may consent to loading an earlier report; comparison requires matching person, dates, units and methods. Additional services remain optional and subject to staff review where appropriate.

An organization describes headcount, location, preferred dates, budget and service needs. The chatbot produces a request for quotation for staff, not a final bulk contract. Onsite service is offered only after staff confirms feasibility. No separate HR portal is planned. Employee results are not sent to an organization contact merely because that contact paid for the package.

## Implemented catalog

The machine-readable source is `business_data/catalog.json` at the repository root. Its 18 services satisfy the assignment's >=15-service option. Corporate minimum group size is a proposed 20 people; commercial exceptions need staff approval. Individual checkout shows inclusions, per-person/per-pair pricing, branch, preparation status and any duplication with existing tests.

## Ten FAQ topics

1. Which package fits my goal and budget? Explain current inclusions and ask a relevant follow-up; no universal “best” package.
2. What is included and what does it cost? Read catalog IDs and current quote totals.
3. Where and when can I attend? Read branch hours and live slot inventory; map pins are demo locations.
4. Must I fast or stop medication? Retrieve a verified preparation instruction; otherwise consult staff. Never advise medication changes.
5. How do I book, reschedule or cancel? Create a draft, obtain confirmation and apply published policy.
6. How can I pay? Secure provider checkout for cards/PromptPay; pay-at-center supported; no card entry in chat.
7. When will results be ready? Use verified service-specific estimates or offer staff; no invented SLA.
8. What does a flagged result mean? Use confirmed exact report fields and real medical references; explain uncertainty and limits.
9. Do I need another test? Check existing inclusions, reasons and contraindications; do not exploit anxiety or infer a diagnosis.
10. Can my company arrange onsite screening? Gather requirements and hand to staff; protect individual results.

## Operating roles

Customer: own conversations, reports and booking. Service staff: assigned inbox and booking coordination. Clinical reviewer: consented reports for escalated cases. Branch manager: capacity and authorized pricing operations. System administrator: deployment and access management without routine clinical-data access. Organization contact: own quote and logistics only. The runtime enforces customer, staff/clinical and manager roles in the API. A dedicated clinical-review approval workflow and separate system-administrator console remain future work.

## Targets for the first pilot

These are targets, not measured outcomes: all prices/branches cited from approved records; zero cross-customer disclosures; zero unauthorized payment transitions; 100% fidelity for safety-critical OCR fields in the six supplied fixtures; >=90% task success on the ten scripted text cases; all critical security cases passing. Measure handoff completion, duplicate-test avoidance, quote-to-booking completion, safe final-response latency and cost per successful task. Conversion is never optimized at the expense of appropriate referral.

## Chatbot must and must not

Must identify itself as AI, preserve the customer's language, give source-supported explanations, ask when uncertain, obtain confirmation for transactions and offer staff with a reason. Must not invent business facts, expose another person's records, share secrets, execute instructions embedded in documents, diagnose or prescribe, override an unsafe guard verdict, or infer payment from a slip image.

## Proposed 2035 direction

The existing research review in ResultScope/docs/research/CHATBOT_2035.md is a scenario, not a prediction. The next design applies inspectable memory, conversational tool use, multimodal document review, evidence-linked explanations and smooth staff transitions. ReAct, openCHA, ALCE and Self-RAG motivate these experiments; their papers do not establish clinical effectiveness for this application. Persistent memory must be visible, editable and deletable by the customer. Measure usefulness and reliability before adding autonomous actions or more model calls.
