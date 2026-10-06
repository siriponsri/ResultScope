# Retrieval

58 approved real-source records are stored in knowledge/evidence/catalog.json. Content hashes are checked at load; records linked to downloaded PDFs also validate the source-file hash. The 68-URL discovery manifest distinguishes retrieved documents, landing/maintenance pages, historical files and failures. Source checking is not clinician approval.

BM25-style lexical retrieval handles exact test names and Thai character bigrams. Optional LightRAG /query/data uses mix graph/vector retrieval; it does not replace BM25. Reciprocal rank fusion combines rankings. Only known file_path IDs beginning resultscope://evidence/ are accepted; content and URLs are resolved locally, never trusted from arbitrary remote chunks.

Export with scripts/export_lightrag.py. Use a pinned LightRAG deployment and embedding model/dimension. The public export contains no patient data or oracle. Rebuild and re-evaluate the external index when sources or embeddings change. Live semantic relevance, latency and ingestion cost remain unmeasured in this package.
