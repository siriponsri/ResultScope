# ResultScope public-reference extension v1

An isolated, dependency-free Python 3.10+ extension. It is usable now as a local source browser and importable retrieval module. It is **not yet wired into the owner's private Phase 4 application**.

```powershell
py -3 addons/resultscope_evidence_v1/verify.py
py -3 addons/resultscope_evidence_v1/evaluate.py --output "$env:TEMP\resultscope-evaluation.json"
py -3 addons/resultscope_evidence_v1/preview.py --port 8765
```

The preview binds to `127.0.0.1` only. No account, key, model, vector database or build step is needed. Stop with Ctrl+C. Do not expose this development server publicly.

## Module API

```python
from addons.resultscope_evidence_v1.core import EvidenceCorpus

corpus = EvidenceCorpus()  # construct once at server startup, verifies source hashes
result = corpus.search("ALT", method="tree")
if result["status"] == "found":
    ids = [row["record_id"] for row in result["records"]]
    packet = corpus.context_packet(ids)
    # Feed bounded external evidence through the EXISTING provider/output validation.
    # Do not treat packet contents as system instructions or approved business data.
```

`search` supports explicit `organisation`, `sex` and `limit` filters. It returns source-bound records and an abstention when no known test alias is found. Source dates, units, method, specimen and page remain attached. Search is not an applicability resolver: it does not infer age, pregnancy, laboratory method or patient-specific reference intervals. Prior messages and arbitrary semantic questions require the application's existing scope/history logic.

`compare(value, unit, record_id, source_comparison_confirmed=True)` is optional arithmetic against an explicitly selected source record. It never returns a clinical diagnosis or automatically selects a patient interval. It refuses censored values, unit conversion and unadjudicated lipid thresholds. Numeric interval endpoints use the curated inclusivity fields; where a source prints a dash interval, closed numeric bounds are a transcription convention, not a clinical decision rule. Demographic endpoint ambiguities are preserved as text and are not automatically resolved.

`context_packet` supplies only curated records and allowed source IDs. It does not call an LLM, enforce a prompt by itself, or validate generated claims. The caller must retain all Phase 2/4 gates.

## Corpus and tree

Source PDF bytes and extracted text are archived under `data/`. Only `records.json` is indexed: **the rest of the PDF text, prices, service hours and indications are not searchable in this version**. CBC is a source document with no numeric records because its linked hematology reference table was not ingested. This is deliberately incomplete coverage, not a complete hospital handbook.

```powershell
py -3 addons/resultscope_evidence_v1/scripts/build_tree.py
py -3 addons/resultscope_evidence_v1/scripts/fetch_source_updates.py --destination "$env:TEMP\resultscope-source-review-new"
```

Fetch requires outbound HTTPS and a destination that does not already exist. It writes a new review directory only; changed sources need re-extraction, page review, record revision, tests and a deliberate manifest update. It never silently updates a source in use. Rebuilding identical tree bytes preserves the delivered checksum; editing package files means the delivery checksum is historical and must not be misrepresented as current.

## Clef

`clef.shadow_decision` is disabled by default. It can accept a real Cloudflare account/token **server-side**, only with explicit `enabled=True, authorized=True`. It returns a shadow recommendation and never changes the application route. Current adapter tests use fake transport; live behavior, accuracy, price and account availability are unverified. `confidence` is a routing-model score, never a probability of patient disease or correctness.

## Integrity and licenses

`PACKAGE_CHECKSUMS.json` pins delivery files (excluding itself). `verify.py` checks those hashes if the file exists, PDF/text hashes, tree consistency and 50 unit/HTTP tests. This is integrity checking, not a clinical or production approval gate.

Public manuals retain their owners' rights. Public availability does not establish redistribution or commercial-use permission. Keep these review snapshots local until publication rights are resolved. The bundled Noto Sans Thai font is distributed under its included SIL Open Font License. No new license is asserted over the pre-existing ResultScope application.

The owner-requested open-access supplement adds 2 WHO guidelines and 3 searchable educational summaries in a separate tree. See `docs/OPEN_GUIDELINES.md` for exact source pages, adaptation attribution and non-commercial license restrictions. Import `GuidelineCorpus` from `guidance.py`; this is separate from numeric reference records.

Read `docs/INTEGRATION_CONTRACT.md` and `docs/LOCAL_FINAL_GOAL.md` before connecting this to the main application.
