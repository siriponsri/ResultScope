# Data governance and source boundaries

This document describes current application behavior and unresolved product controls. It is not a privacy policy, certification, clinical validation, or regulatory approval. Use synthetic or de-identified inputs for controlled evaluation until the intended use and data-handling arrangements are approved.

## Data classes

| Data class | Current treatment | Release boundary |
|---|---|---|
| User-entered text and values | Parsed, bounded, used as context, and stored with the conversation | May still contain identifying or health information; no patient identity system exists |
| Report images | JPEG/PNG validated, normalized, and sent to OCR only when permitted | Image bytes are not persisted by the app; provider handling needs separate review |
| Extracted fields | Session-bound records with review state, revisions, corrections, and confirmation | Confirmation establishes reviewed input, not clinical correctness |
| Public laboratory references | Pinned snapshots, source IDs, checksums, pages, and local retrieval | `public_reference`, `release_eligible=false`; not partner business facts or personal ranges |
| Open guideline notes | Educational summaries with source and license metadata | `open_guideline`, `release_eligible=false`; not numeric diagnostic rules |
| Synthetic corpus | Explicit demonstration namespace and banner | Development/test only; cannot silently replace release content |
| Approved business corpus | Manifest validation and owner-approval conditions | Current lack of approved release data remains a blocker |
| Provider credentials | Server-side configuration; local saved values are encrypted and not returned | Local settings are not an approved cloud secret store |
| Attempt records | Persistent slot/cycle/source/outcome accounting | Retain failed and rejected attempts; not a patient audit trail |

## Input, storage, and deletion behavior

`services/store.py` stores conversation history in local SQLite by default outside Vercel, unless Upstash is selected. SQLite rows contain plaintext JSON; this application does not implement at-rest encryption for conversation data. `services/extraction_store.py` stores extracted fields and their lifecycle state separately. The default conversation and extraction TTLs are 24 hours in `config.py`.

TTL behavior is implemented in the adapters; it is not a comprehensive retention policy or a guarantee of secure erasure at an exact time. Expired rows, backups, logs, provider copies, and system-level recovery require an explicit operating policy. **Start a new analysis** resets application context through the reset route; it does not prove erasure from every external or backup system.

Image validation checks content signatures, decoded dimensions, and size. It re-encodes the image and removes image metadata. It does not redact names or identifiers visible in pixels. The application clears references to original/normalized bytes after the OCR operation and does not write those bytes to its image store. Extracted text can still contain sensitive information.

## External transfer boundaries

When authorized, the LLM receives the bounded context assembled by the application, including the current query, relevant history, deterministic facts, retrieved evidence, and confirmed extraction context as applicable. OCR receives normalized image content. Optional SystemOne shadow observation receives the message and Python intent context.

Provider transport is disabled by default. A successful mock test makes no provider request. Enabling live transport requires explicit opt-in and a pre-existing active attempt cycle; it does not establish consent, lawful processing arrangements, retention guarantees, or commercial rights. Upstash is a separate optional external storage path, not covered by the provider network guard.

## Session and administration boundaries

Signed conversation cookies protect the integrity of a session identifier. They do not authenticate a patient or implement organizational roles. Without a configured signing key, a process-local temporary key is used. Session locking and admin sessions are local to the process; do not describe them as distributed authorization controls.

Local administration uses an HttpOnly session cookie, CSRF protection, rate-limited login/tests, and write-only credential entry. Its default password is permitted only in explicit local-demo mode. Local encrypted secret files and their key must remain outside Git and shared artifacts. Do not claim that local secret encryption also encrypts user health data.

## Sources and rights

Keep the source ID, version, checksum, origin, page/section where available, and rights metadata associated with every evidence record. Generated text cannot create a valid new citation or promote a source's eligibility. The validator constrains citation IDs and source URLs to retrieved evidence; these checks reduce specific risks but are not a proof of complete factual correctness.

The retained Phase 6 record identifies a WHO supplement licensed under `CC BY-NC-SA 3.0 IGO`. That record does not grant unrestricted commercial use. Public availability of hospital reference documents likewise does not make them approved business content. Review actual source terms and intended distribution before release.

The upstream starter's redistribution status is recorded in [NOTICE.md](../../NOTICE.md). Resolve that issue before commercial distribution. Preserve provenance snapshots and approval metadata during repository cleanup; neither translation nor reformatting creates new source rights.

## Controls required before a partner pilot

Name owners for intended-use review, approved content, identity/access, consent, retention/deletion, provider arrangements, incident response, monitoring, backups, and change approval. Define tenant isolation and role permissions if organizations or patient records are introduced. Approve cloud secrets and multi-instance quota coordination before deployment.

HIS and pharmacy proposals require separate data-flow mapping, minimum-necessary context, partner interface contracts, and professional oversight. No patient-record integration, dispensing workflow, prescription feature, or FHIR contract currently exists. See the [roadmap](../product/ROADMAP.md) and [readiness gates](../operations/READINESS.md).

## Pinned CSV line-ending restoration

The untouched Git baseline also fails the addon verifier at
vendor/resultscope_evidence_v1/data/records-review.csv. Its checked-in LF bytes have
SHA-256 ce566648ade1b2674fdc3f617d66ec9d075fd3ca4fd60f89249d55e30c5f847f.
Restoring only CRLF produces the exact already-pinned package hash
d8cb1f902fc5cf0ce7fea81c0ab4adcbd625cebd99b4964d072d502a14495b19.
The refresh ships those restored bytes. No CSV fields, manifest hashes, source
approvals or rights are changed. Other addon files remain byte-for-byte unchanged.
