# Threat model — educational demo

| Threat | Implemented control | Remaining limitation |
|---|---|---|
| Prompt injection in chat/report/source | Two-sided guard; untrusted-data prompts; narrow read-only retrieval; known source IDs | Prompt-based/model safeguards can fail; multilingual attacks need evaluation. |
| Invented citations/changed values | Exact citation set, report observation equality, LLM prose/evidence review | Semantic support and prose parsing are model fallible. |
| Unauthorized provider spend | Cloud access code, same-origin checks, request limits, atomic shared attempt cap | Shared code is not user authentication; local rate limits are instance-local. |
| Token tampering/mixing users | AES-GCM, signed HttpOnly cookie, purpose/session/expiry checks | Stolen cookie+token can be replayed until expiry; no central revocation. |
| Unsafe model output/HTML | Guard before release; strict JSON; DOMPurify allowlist; server-owned links | Model/guard false negatives remain possible. |
| Malicious/oversized uploads | 3 MB file cap, pixel caps, bounded PDF pages, rasterization and signature checks | PDF/image parsers need regular security updates. |
| Secret/data disclosure | Server-side keys, bounded sanitized errors, no body logs, no persisted v2 images | Provider retention is outside application control; browser exports contain content. |
| Cold-start budget reset | Persistent atomic Redis cycle cap; no TTL or automatic refunds | Redis/operator misconfiguration remains operational risk. |
| Remote retrieval poisoning | Discard remote text/URLs; accept only exact manifest IDs | A wrong but known source can still be ranked; benchmark retrieval. |
| Legacy route bypass | `/api/v1` blocked on Vercel | Local v1 remains for migration; do not publicly expose development mode. |

This package does not include patient authentication, organizational tenancy, consent
records, deletion workflows, clinical governance or audited health-data hosting. Those
are deployment projects, not properties implied by a working Vercel URL.
