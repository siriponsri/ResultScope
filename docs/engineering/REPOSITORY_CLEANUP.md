# Repository boundaries

Original source documents, synthetic fixtures, licenses, historical reports and retained v1/local code are preserved. The v3 business route and retained v2 lab route use the same approved medical evidence catalog. Uploaded private records and evaluator oracles never enter shared RAG.

scripts/package_v3.py creates the full replacement ZIP with per-file hashes. It excludes private environment files, data, ledgers, virtual environments, caches, Git and installed dependencies. Both empty example environment files are included. .vercelignore additionally excludes documentation and discovery-only raw files; approved source PDFs needed for runtime hashes stay included. Preserve existing .env, data and encryption keys when replacing code.
