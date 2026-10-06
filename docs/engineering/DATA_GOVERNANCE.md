# Data governance

Business fixtures, clinical evidence, customer documents and evaluator oracles are separate data classes. Runtime medical retrieval uses only knowledge/evidence/catalog.json. The discovery report, raw downloaded guidelines and synthetic reports are not automatically admitted to RAG. See knowledge/medical_sources/README.md for source age, page, units and limitations.

Customer sessions and entity payloads are encrypted at rest by the application; owners and roles are checked before access. Metadata remains visible to the database operator. Provider calls contain only the needed context; no end-to-end encryption or regulatory certification is claimed. A staff handoff shares the conversation after the customer requests it. Organization contacts cannot read employee reports merely because they pay.

Report deletion clears conversational copies in current and archived threads. Account deletion, automated retention, provider-side erasure and backup expiry are not implemented as self-service workflows. Operators must define these before real health data is used. Never train or index customer reports in shared LightRAG. Preserve key and encrypted database backups together.
