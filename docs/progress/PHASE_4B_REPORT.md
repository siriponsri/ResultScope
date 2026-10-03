# Phase 4B report — evidence context and provider boundary

Date: 2026-10-03  
Branch: local `main`

## Status

| Gate | Status | Evidence |
|---|---|---|
| External context enters existing provider contract | PASS | `services/answer_service.py` sends the adapter packet as untrusted external data; public-reference tests pass |
| Citation allowlist and arbitrary URL rejection | PASS | `tests/test_public_reference.py::test_public_reference_rejects_forged_citation_and_arbitrary_url` |
| Sync/SSE citation parity | PASS | `test_public_reference_sync_and_sse_citations_match` |
| Metadata-guided tree retrieval | PASS | Addon verifier and 50 addon tests; tree fixture 15/15 vs flat 12/15 |
| Runtime latency comparison | NOT_RUN | The addon comparison is a small fixture result; this patch does not claim production retrieval/provider latency |
| Clef route control/live call | NOT_RUN | Clef remains disabled/shadow-only; no external guard call was made |
| Live Typhoon/provider quality | NOT_RUN | No live credential or model compatibility smoke test was authorized |

## Design decision

The addon tree is described as deterministic metadata/alias-guided hierarchical
retrieval. It is not embeddings, RAPTOR, a learned clinical tree, or a general
RAG framework. The existing scope gate remains first, and absence/failure of
the optional package does not silently fall back to a public source or let the
LLM invent one.

The provider sees retrieved records and `context_packet` as untrusted facts,
never as instructions. The server resolves citation metadata and validates
source markers and URLs before sync or SSE output.
