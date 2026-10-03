# ResultScope as-built message flow (local candidate)

This is an as-built description of the local FastAPI application after the
public-reference and first-use changes. Items marked proposed are not runtime
integrations.

```text
Browser home
  ├─ typed lab result/question
  └─ JPEG/PNG upload
       ↓
FastAPI request boundary
  ├─ file magic bytes/size/pixels, then optional Vision adapter
  └─ session-bound extraction review and user confirmation
       ↓
scope gate / intent router
  ├─ unrelated, unsafe, or local → deterministic response; no LLM
  └─ lab → deterministic parser + supplied-range rules
                  ↓
          public-reference flag?
            ├─ off → configured synthetic/release knowledge path
            └─ on → hash-checked addon adapter
                       ├─ no hit/corrupt → abstain; no provider
                       └─ matched → untrusted context packet + allowlist
                                      ↓
                           OpenAI-compatible provider
                                      ↓
                         output validation and citation resolution
                                      ↓
                    sync JSON or SSE metadata/delta/done events
                                      ↓
                        integrated value + explanation surface
```

## Trust and ownership

- The server owns scope decisions, numeric flags, session signing, source
  allowlists, provider calls, and output validation.
- Browser JavaScript only presents returned metadata. It never chooses a
  clinical interval or trusts an arbitrary URL from model text.
- Confirmed OCR remains user-supplied/untrusted data. It cannot establish
  business prices or policies.
- Public numeric records are `public_reference`; WHO notes are
  `open_guideline` and explicitly non-numeric. Both remain `release_eligible=false`.

## Proposed, not implemented

- No OCR framework, RAG/embedding service, authentication, patient profile,
  HIS/pharmacy connector, production database, Clef route control, or live
  provider evaluation is added here.
- A future HIS/pharmacy integration needs an approved schema, consent,
  retention, and partner authorization before any connector is implemented.
