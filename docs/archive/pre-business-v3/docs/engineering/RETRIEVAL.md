# Verified lexical and semantic retrieval

`knowledge/evidence/catalog.json` is the sole v2 knowledge collection. It has 35
records with stable IDs, HTTPS origin URLs, publisher, checked date, source class and
SHA-256 of the local content. Nine are brief, attributed MedlinePlus paraphrases;
26 retain provenance from the pinned Thai laboratory manual bundle in
`vendor/resultscope_evidence_v1`. A content hash verifies local integrity, not medical
approval. Source-specific manual ranges are context, never substitutes for report ranges.

BM25 ranks titles, aliases and content locally. Latin tokens and Thai character bigrams
support literal retrieval; the LLM planner supplies translated English test aliases for
other languages. This is lexical search, not an embedding model. Default mode is lexical.

## LightRAG connection

The reviewed teacher repositories serve different roles:

| Repository | Adopted contribution | Boundary |
|---|---|---|
| `chacharin/light-rag` | Deployment/environment pattern for a remote LightRAG service | Do not host a mutable graph/vector store inside Vercel functions. |
| `chacharin/render-rag` | LightRAG server with graph/vector retrieval | Provision separately with persistent storage and matching embedding dimensions. |
| `chacharin/mcp-lightrag` | Read-only `query_data`, `/query/data`, `X-API-Key`, explicit errors | No ingestion/deletion/MCP administration tools are exposed to the chatbot. |

Run `python scripts/export_lightrag.py --output build/lightrag-import.json` to create a
reviewable, deterministic import payload from verified records. It performs no network
operation. Import its `texts` and corresponding `file_sources` using your LightRAG
administrator workflow. Each file source must be exactly `resultscope://evidence/<id>`.
Do not index the demo reports, answer key, conversations, secrets or old synthetic KB.
Use a dedicated workspace so unrelated material cannot supply context.

Set `LIGHTRAG_ENABLED=true`, `LIGHTRAG_URL` and `LIGHTRAG_API_KEY`. The server calls
`POST /query/data` with `mode=mix`, bounded top-k/context and `X-API-Key`. The adapter
expects `{status: "success", data: {chunks: [{file_path: "resultscope://evidence/id"}]}}`.
The teacher render-rag QueryDataResponse contract was checked at query_routes.py blob
`622afa26b3f00986ee205edcfa57bb2ad048f7bf`. Pin and verify the complete service behavior before enabling it.
The teacher MCP implementation was reviewed at query.py blob
`be72811cbf1ac0a7a716c4a1ed7253580cec455b`.

Only known exact source IDs from remote chunks are admitted. Text, URLs and instructions
returned by the remote service are discarded; trusted content comes from the local
catalog. Reciprocal rank fusion (k=60) combines the lexical and remote rankings.
No mapped remote result is honestly labeled `lexical_no_semantic_match`. A service
failure is visible and fails the turn; it is not disguised as successful hybrid search.

LightRAG may make embedding/reranking/model calls internally even though `/query/data`
skips final answer generation. Its cost/retention budget is separate. The app sends a
planner-written topical query, not report objects or conversation history; the prompt
asks it to omit identities and values, but this is not a certified de-identification system.

## Extension path

For a larger Vercel-native corpus, implement the same stable-ID retrieval boundary over
Postgres full-text search plus pgvector or another managed index. Version the embedding
model/dimension, chunker, ingestion revision and source approval metadata. Test exact
abbreviations, multilingual paraphrases, conflicting manuals and missing source IDs.
Evaluate Recall@k, citation correctness/coverage, no-evidence abstention and latency
against the current BM25 baseline before enabling a new retriever. Lexical means text
retrieval here; the Meta Lexical rich-text editor is not part of the requirement.
