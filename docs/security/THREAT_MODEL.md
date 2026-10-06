# Threat model — ResultScope 3

| Threat | Implemented control | Remaining limitation |
|---|---|---|
| Prompt injection in chat, report or retrieved content | Separate input/output guard, untrusted-data prompts, schema validation, local known source IDs and answer review | Model false negatives and multilingual effectiveness require live evaluation. |
| Changed values or invented sources | Confirmed-field equality, citation allowlist and hashed local evidence | Prose/evidence review is model fallible; clinical review is not performed. |
| Unauthorized business action | Opaque expiring proposal, explicit confirmation, current-price/capacity/ownership checks in a transaction | Deployment and concurrent production load remain untested. |
| Cross-customer access | Digest-stored sessions, CSRF and same-origin checks, record ownership, staff branch/assignment checks | Fine-grained clinical role separation and account lifecycle need further work. |
| Payment spoof or replay | Test-only keys, raw HMAC check, amount/currency/checkout match, event dedup, terminal refund protection | No real merchant or external payment acceptance test is included. |
| Duplicate LINE delivery or wrong account | Signed events, persisted dedup, job leases, one-use account linking, ownership recheck and unlink cancellation | An outbound send already in flight cannot be recalled; quota/cold starts affect delivery. |
| Provider spend | Explicit network gate, named cycle, atomic Redis cloud attempt cap, no hidden paid fallback | Attempt counting is not a per-customer currency budget; local rate limits are per instance. |
| Stored health data disclosure | Encrypted entity payloads and originals; no body/key logging; report deletion clears conversation copies | Metadata remains visible; backup expiry, account erasure and provider-side deletion need policy. |
| Unsafe HTML or untrusted links | Sanitized Markdown and server-resolved source URLs; CSP and no-store business responses | Browser/dependency patch management and independent review remain necessary. |

The retained /lab route separately uses signed encrypted browser context. Business accounts use durable encrypted database entities and revocable server-side sessions. These are different storage models. This coursework package is not a security certification or a clinical release.
