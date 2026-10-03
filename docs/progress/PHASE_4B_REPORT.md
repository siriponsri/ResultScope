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
| Clef route control/live call | PASS: disabled | Clef is not wired into routing and no paid fallback is available |
| OpenThai-SystemOne decision adapter | PASS: local shadow boundary | Separate iApp adapter/parser is implemented; Python route and safety/output validation remain authoritative |
| Typhoon LLM/OCR separation | PASS: mocked/local | LLM answer and OCR document contracts use separate provider slots and adapters |
| Admin Settings provider boundary | PASS: local-demo | Server-side allowlist, write-only keys, CSRF-protected mutations, and local-only encrypted persistence |
| Live Typhoon/provider quality | NOT_RUN | No live credential or model compatibility smoke test was authorized |

## Design decision

The addon tree is described as deterministic metadata/alias-guided hierarchical
retrieval. It is not embeddings, RAPTOR, a learned clinical tree, or a general
RAG framework. The existing scope gate remains first, and absence/failure of
the optional package does not silently fall back to a public source or let the
LLM invent one.

The provider sees retrieved records and `context_packet` as untrusted facts,
never as instructions. The server resolves citation metadata and validates
source markers and URLs before sync or SSE output. Provider IDs are selected
from a server-side catalog; arbitrary browser-supplied endpoints are rejected.

## Current boundary note

The local Admin Settings page is implemented for an explicit local-demo mode.
It does not establish online or production readiness. Cloud secret persistence,
live provider verification, and independent review of the final candidate
remain outstanding.
