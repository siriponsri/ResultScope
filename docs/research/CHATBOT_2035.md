# Designing a laboratory chatbot toward 2035

Research and implementation decision record · 2026-10-05

## Scope and method

The design question is how ResultScope can become a capable conversational assistant
without making unsupported clinical decisions. “2035” is a scenario for product design,
not an established forecast. This review uses original papers, model documentation,
platform documentation and the repositories supplied by the owner. It distinguishes
published findings, engineering inference and what this package actually implements.
It is a focused technical review, not a systematic clinical literature review or a
claim that all current research has been covered. No patient study or live model
benchmark was conducted during this change.

The research favors capabilities that a user can inspect: conversational continuity,
selective tool use, visible evidence, reversible context, uncertainty and control over
sharing. An impressive interface cannot compensate for wrong values or unsupported
medical advice. The resulting product is a bounded educational chatbot, with a path
toward richer interaction if later evidence and governance support it.

## Evidence and implications

| Primary source | What it supports | ResultScope interpretation and limit |
|---|---|---|
| ReAct [1] | Combining model reasoning with actions can help interactive information tasks. | Let the model choose a read-only search step. This implementation uses structured decisions; it does not reproduce ReAct training or expose reasoning traces. |
| openCHA [2] | A health-agent framework combines orchestration, external information, multilingual dialogue and multimodal inputs. | Treat reports as optional conversational context. A framework demonstration is not clinical validation of this app. |
| AMIE [3] | Research explores LLM clinical dialogue in a controlled text-chat evaluation. | Evaluate multi-turn clarification and communication, not just a single correct-looking paragraph. The study's setting does not justify autonomous diagnosis here. |
| ALCE [4] | Citation evaluation separates answer correctness, fluency and citation quality. | Validate source IDs and also inspect claim support. A clickable citation alone is insufficient. |
| Self-RAG [5] | A trained model can learn to retrieve selectively and critique generations. | Use a bounded planner and separate support-review call. This is an inspired design, not a Self-RAG-trained implementation. |
| LightRAG [6] | Graph and vector structures support retrieval at different levels of detail. | Keep lexical test-name matches and add an optional graph/semantic ranking service. Published benchmark gains are not assumed for these reports. |
| Generative Agents [7] | Memory, reflection and planning support behavior in a simulated environment. | Long-term memory requires explicit user control and correction. Simulation results do not establish health-memory accuracy or consent design. |
| Anthropic's agent engineering guidance [8] | Composable patterns and well-designed tool boundaries can be preferable to unnecessary complexity. | Use a bounded planning loop with read-only retrieval and separately confirmed business actions. Add complexity only for a measured failure. |
| Llama Guard 4 model card [9] | A dedicated safety classifier checks specified hazard categories in input/output contexts. | Use a separate safety boundary, while treating factual support and language coverage as separate evaluation problems. |
| MedlinePlus result guidance [10] | Laboratory intervals and interpretation depend on the testing context. | Preserve report values and intervals; do not replace them with a generic threshold. |

The strongest common thread is separation of responsibilities. A conversational model
can interpret a request and decide how to proceed, while software enforces exactness
and access boundaries. This does not require a deterministic intent tree. It also does
not require handing the model every tool or allowing it to bypass a guard. ResultScope
therefore moves the conversational decision into the LLM while retaining explicit
checks on values, citations, sessions and resource use.

The review also changes the meaning of “good chat.” A successful turn is not merely
fluent. It must use the current context, explain its evidence, avoid adding unavailable
facts and leave the user able to ask a useful next question. Evaluation should include
whether the model asks for clarification at the right time, preserves a changed language
preference and declines a diagnosis request without making the rest of the conversation
unusable. These are engineering objectives inferred from the sources, not outcomes
already demonstrated by this build.

## A plausible 2035 experience

**Conversation as the primary interface.** A user should be able to say “Why is this
flagged?” and then “Explain that in Thai” without navigating a separate workflow for
every intention. The assistant should know which report field is being discussed and
ask when the referent is ambiguous. In this release, recent turns and a confirmed report
are carried forward; the model selects an action and search query. This is bounded
context, not unlimited memory. The UI remains a familiar, quiet chat workspace because
complexity is better spent on reliable conversation than on decorative futuristic controls.

**Multimodal input with visible correction.** A future assistant may combine images,
speech and longitudinal measurements. The near-term requirement is more concrete:
show the original report beside extracted rows, let the user correct them and keep
qualitative text intact. ResultScope implements actual image/PDF reading, not gold-label
prefilling. It requires confirmation before extracted fields become trusted conversation
context. Voice, live camera and wearable streams are not included. Each new modality
would need its own consent, quality limits and failure recovery.

**Evidence that survives follow-up questions.** A user may ask for an explanation,
request a simpler version and then ask where a claim came from. Sources should remain
inspectable across that interaction. The new planner retrieves even for medical
simplification/translation tasks, the answer carries explicit source IDs, and the server
resolves source metadata. A review call checks whether the explanation is supported.
This does not eliminate hallucination: the critic can share the generator's errors.
The test plan therefore separates mechanically valid citations from correct and complete
support. An unsupported answer should be withheld or changed into a focused clarification.

**Memory with an off switch.** Persistent memory could reduce repetition, but health
context becomes dangerous when it silently mixes people, dates or corrected results.
The v3 business release implements durable encrypted accounts, saved reports, visible current/previous report selection and archived conversations. Report deletion clears report-bearing histories; automatic provider-side erasure and retention automation remain future work. Identity, dates and compatible methods still require review before comparison. A persistent database is not proof that memory is clinically correct.

**Appropriate initiative.** A useful assistant may suggest the next question, notice
missing context or recommend professional assessment for serious symptoms. That is
not authority to diagnose or change treatment. The implemented model can choose an
urgent/clarifying response and propose follow-ups. In v3 it can propose booking, quotation, payment and staff handoff previews; the user must confirm and the backend must revalidate authority and current business facts. It cannot prescribe or autonomously order treatment. This is particularly important when the request mixes education
with a real-world clinical decision.

**Transparency without revealing private reasoning.** Users need to know whether the
assistant is reading a report, looking for evidence or checking an answer. They do not
need fabricated thought processes. The interface therefore streams actual processing
stages and releases only the checked answer. It includes source links, report context,
clear failure messages and stop/retry controls. A failed model call never becomes a
scripted educational answer masquerading as AI. The optional motion introduction helps
explain the product; it is not used to simulate cognition or conceal latency.

## Teacher repository review

The supplied `light-rag` repository [11] demonstrates environment-based deployment of
a remote LightRAG service. Its configuration makes the LLM endpoint, embedding model
and embedding dimension deployment concerns. This supports keeping the index outside
an ephemeral Vercel function. The package does not copy example credentials or assume
that choosing a model name provisions an index.

The supplied `render-rag` repository [12] provides a fuller LightRAG server workflow.
ResultScope adopts the separation between ingestion and query-time retrieval. Corpus
updates should be reviewed, hashed, indexed and evaluated independently of the web
request. A remote server must have durable storage and compatible embedding settings.
The web app's optional adapter is implemented; the remote server is not provisioned by
this ZIP and no live hybrid-search success is claimed.

The `mcp-lightrag` repository [13] is useful for its explicit `query_data` boundary:
retrieve context without requesting a final answer from LightRAG. Its query tool uses
`/query/data`; service authentication uses `X-API-Key`. ResultScope uses the HTTP
contract directly and exposes no ingestion, deletion or administrative MCP tools to the
model. Remote chunks can suggest only known manifest-backed IDs; their text and URLs
are discarded. The local catalog supplies the actual evidence. This narrows the effect
of an untrusted remote response, though it cannot guarantee that a retrieved known
record is relevant.

The `llama-guard-layer` repository [14] supplies the two-sided classification pattern.
ResultScope retains a separate guard model and role-sensitive input/output checks, with
stricter malformed-verdict handling. The direct integration blocks every unsafe category
reported by the selected Llama Guard model. The external service option must be deployed
with equivalent category policy. An unavailable guard blocks the answer; it never
silently falls back to the conversational model as its own safety boundary.

Hyperframes [15] is a motion composition/runtime project, not a chatbot intelligence
framework. It is used for a genuine, self-hosted 12-second composition and player with
finite GSAP timing and explicit controls. The rest of the workspace uses small,
reduced-motion-aware animations. This keeps the original visual identity while ensuring
motion has a clear explanatory purpose.

## Implementation map and next experiments

| Capability | Delivered now | Evidence required before expansion |
|---|---|---|
| LLM conversation decisions | Structured planner, answer, critic; no v1 intent router | Multilingual multi-turn pass/fail review and false-refusal analysis |
| Multimodal context | Six supplied synthetic documents, actual pixel reading, field correction/confirmation | Measured OCR accuracy for every panel/template and provider |
| Grounded explanations | BM25, stable citations, exact observations, support review | Human-scored citation support/coverage and unsupported-claim rate |
| Semantic/graph retrieval | Optional LightRAG adapter, rank fusion, import export tool | Provisioned service, contract test and Recall@k versus BM25 |
| Memory | Encrypted, session-bound, expiring tab context | Consent, identity separation, correction/deletion design before durable memory |
| Guardrails | Input/output Llama Guard, no unguarded streaming | Language-specific adversarial cases and clinical reviewer assessment |
| Deployment | Native FastAPI Vercel entrypoint and shared atomic call cap | Actual cloud deployment, Redis concurrency test and provider smoke run |
| Interaction | English UI, multilingual model prompts, mobile/reduced motion | Usability sessions with intended users; assistive-technology testing |

The next experiment should be small enough to audit: the six supplied synthetic panels,
ten text cases, five adversarial cases and three matched before/after conversations.
Record model versions, prompts, source revision, retriever mode, elapsed time and every
attempt. Score OCR fields separately from interpretation and citation quality. Publish
results by language and document template. If a component adds latency/cost without
improving supported answers, simplify it. If a language or task fails, constrain that
release honestly rather than relying on the “2035” label.

## Primary references

1. Yao et al., *ReAct: Synergizing Reasoning and Acting in Language Models* (2022/ICLR 2023): https://arxiv.org/abs/2210.03629
2. Abbasian et al., *Conversational Health Agents: A Personalized LLM-Powered Agent Framework* (2023; revised 2024): https://arxiv.org/abs/2310.02374
3. Tu et al., *Towards conversational diagnostic artificial intelligence* (Nature, 2025): https://research.google/pubs/towards-conversational-diagnostic-ai/ and https://doi.org/10.1038/s41586-025-08866-7
4. Gao et al., *Enabling Large Language Models to Generate Text with Citations* (2023): https://arxiv.org/abs/2305.14627
5. Asai et al., *Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection* (ICLR 2024): https://arxiv.org/abs/2310.11511
6. Guo et al., *LightRAG: Simple and Fast Retrieval-Augmented Generation* (2024 preprint): https://arxiv.org/abs/2410.05779
7. Park et al., *Generative Agents: Interactive Simulacra of Human Behavior* (2023): https://arxiv.org/abs/2304.03442
8. Anthropic, *Building effective agents* (2024; engineering guidance, not a clinical study): https://www.anthropic.com/engineering/building-effective-agents
9. Meta, *Llama Guard 4 12B model card*: https://huggingface.co/meta-llama/Llama-Guard-4-12B
10. U.S. National Library of Medicine, *How to Understand Your Lab Results*: https://medlineplus.gov/lab-tests/how-to-understand-your-lab-results/
11. https://github.com/chacharin/light-rag
12. https://github.com/chacharin/render-rag
13. https://github.com/chacharin/mcp-lightrag — query.py blob `be72811cbf1ac0a7a716c4a1ed7253580cec455b`
14. https://github.com/chacharin/llama-guard-layer — app/guard.py blob `40c849e67d5dd84d4473af20256abd33e92a08ef`
15. https://github.com/heygen-com/hyperframes — player/CLI version 0.8.131 used in this package
16. Vercel FastAPI deployment documentation: https://vercel.com/docs/frameworks/backend/fastapi

Research and documentation were checked on 2026-10-05. Repository and platform behavior
can change; pin compatible versions and review upstream changes before upgrading.
