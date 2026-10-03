# Source audit — 3 October 2026

## Retrieval and scope

The 17 hospital PDFs were downloaded from the original institutional hosts, checked for PDF bytes, extracted with PyMuPDF and hashed with SHA-256. Selected numeric reference tables were inspected visually and compared with extracted text. This is an engineering transcription check by the implementation agent, **not independent clinical review**. No claim is made that all content on all pages was reviewed.

`source_manifest.json` preserves exact URL, resolved URL, retrieval timestamp, snapshot hash, extracted-text hash and document-date basis. Raw texts have explicit PDF page markers. Hashes establish which bytes were used, not medical accuracy or current clinical approval.

| Source ID | Institution | Indexed PDF pages | Records | Document date |
|---|---|---|---:|---|
| [siriraj-alt](https://www.si.mahidol.ac.th/th/manual/Project/pdf/alt.pdf) | Siriraj Hospital | 1 | 2 | Not confirmed |
| [siriraj-ast](https://www.si.mahidol.ac.th/th/manual/Project/pdf/ast.pdf) | Siriraj Hospital | 1 | 2 | Not confirmed |
| [siriraj-albumin](https://www.si.mahidol.ac.th/th/manual/Project/pdf/albumin.pdf) | Siriraj Hospital | 1 | 1 | Not confirmed |
| [siriraj-glucose](https://www.si.mahidol.ac.th/th/manual/Project/pdf/glucose.pdf) | Siriraj Hospital | 2 | 1 | Not confirmed |
| [siriraj-bun](https://www.si.mahidol.ac.th/th/manual/Project/pdf/bun.pdf) | Siriraj Hospital | 2 | 2 | Not confirmed |
| [siriraj-creatinine](https://www.si.mahidol.ac.th/th/manual/Project/pdf/creatinine.pdf) | Siriraj Hospital | 1 | 2 | Not confirmed |
| [siriraj-electrolytes](https://www.si.mahidol.ac.th/th/manual/Project/pdf/electrolytes.pdf) | Siriraj Hospital | 2 | 3 | Not confirmed |
| [siriraj-alp](https://www.si.mahidol.ac.th/th/manual/Project/pdf/alp.pdf) | Siriraj Hospital | 1 | 2 | Not confirmed |
| [siriraj-bilirubin](https://www.si.mahidol.ac.th/th/manual/Project/pdf/bilirubin.pdf) | Siriraj Hospital | 1 | 2 | Not confirmed |
| [siriraj-total-protein](https://www.si.mahidol.ac.th/th/manual/Project/pdf/total-protein.pdf) | Siriraj Hospital | 1 | 1 | Not confirmed |
| [siriraj-cholesterol](https://www.si.mahidol.ac.th/th/manual/Project/pdf/cholesterol.pdf) | Siriraj Hospital | 1 | 1 | Not confirmed |
| [siriraj-hdl-c](https://www.si.mahidol.ac.th/th/manual/Project/pdf/hdl-c.pdf) | Siriraj Hospital | 1 | 2 | Not confirmed |
| [siriraj-ldl-c](https://www.si.mahidol.ac.th/th/manual/Project/pdf/ldl-c.pdf) | Siriraj Hospital | 2 | 1 | Not confirmed |
| [siriraj-triglycerides](https://www.si.mahidol.ac.th/th/manual/Project/pdf/Triglycerides.pdf) | Siriraj Hospital | 1 | 1 | Not confirmed |
| [siriraj-cbc](https://www.si.mahidol.ac.th/th/manual/Project/pdf/cbc.pdf) | Siriraj Hospital | None | 0 | Not confirmed |
| [kku-alt](https://lab.md.kku.ac.th/public/files/uploads/SD-CL-00-001-04%20ALT.pdf) | Srinagarind Hospital, KKU | 2 | 2 | 2024-11-01 |
| [kku-glucose](https://lab.md.kku.ac.th/public/files/uploads/SD-CL-00-001-04%20Glucose.pdf) | Srinagarind Hospital, KKU | 2 | 1 | 2024-11-01 |

## Interpretation boundaries

- 26 numeric records / 17 distinct analytes / 17 hospital PDFs; these counts are different concepts.
- Siriraj individual PDFs did not provide a confirmed revision date during this review. A parent manual's date was not copied into them. KKU's selected PDFs show review date 1 November 2024; that is retained, not confused with the 2026 fetch date.
- `original_reference_text` is a normalized display transcription and may translate labels; it is not a verbatim quote. `transcription_note` points back to the PDF. The snapshot/page remains authoritative for checking transcription.
- Adult-only wording without a numeric age definition remains text. Unknown sex/age/method/specimen/pregnancy remain unknown where unconfirmed. No demographic applicability engine is implemented.
- BUN age brackets retain the document wording; shared endpoint ambiguity is not silently resolved. Numeric dash ranges are stored as closed for source-only arithmetic, not as a clinical protocol.
- Lipid entries are marked `source_threshold_unadjudicated`. They display source thresholds but cannot be used by `compare` as reference intervals.
- Different sources intentionally remain separate. No averaged ranges, invented harmonized consensus or automatic best-source selection.
- CBC snapshot refers to another hematology reference table that was not ingested. It has zero numeric records and search must not pretend otherwise.
- Full extracted PDF text is for audit. Only selected reference rows are indexed. Prices, opening hours, clinical indications and remaining pages are not a business corpus or searchable in this version.
- Hospital documents are publicly accessible; permission to redistribute or commercially reuse them was not established. Source owners retain their rights. Do not publish cached manuals automatically.

## Open-access guideline supplement

See [OPEN_GUIDELINES.md](OPEN_GUIDELINES.md). Two additional WHO PDFs and extracted texts have a separate manifest, tree and three educational notes. They do not alter the hospital numeric record count. Licensing is CC BY-NC-SA 3.0 IGO, including the Thai note adaptations, with attribution and non-endorsement/translation notice. These are not unrestricted commercial data.

| Source | Edition | Indexed location | Notes |
|---|---|---|---:|
| [Guideline on haemoglobin cutoffs to define anaemia in individuals and populations](https://www.who.int/publications/i/item/9789240088542) | 2024-03-05 | PDF 30; printed 9 | 1 |
| [WHO guideline on use of ferritin concentrations to assess iron status in individuals and populations](https://www.who.int/publications/i/item/9789240000124) | 2020-04-21 | PDF 37; printed 19 | 2 |

Original WHO license pages and indexed pages were read; those indexed pages were also visually inspected. This is not a complete systematic review of all guidelines or a claim that these editions supersede every local protocol. No patient records or personal identifiers were downloaded.

## Update workflow

Run `scripts/fetch_source_updates.py --destination NEW_DIRECTORY` to fetch allowlisted sources without changing the active corpus. Compare hashes, re-extract changed pages, inspect tables, update notes/records only after review, rebuild trees, test and issue a new corpus version. Never update an in-use snapshot while preserving an old hash or reuse an old approval for changed text.
