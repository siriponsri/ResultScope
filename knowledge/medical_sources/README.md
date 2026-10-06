# Downloaded medical source collection

Verified on 2026-10-05. The attached Deep Research report is a discovery document, not an authority. Its unresolved citation tokens are not citations used by the application.

- 68 explicit source URLs attempted; 64 downloaded HTTP bodies. PDF, HTML, maintenance pages and failed downloads are distinguished in the manifest.
- 23 newly source-checked intervals; 58 total runtime evidence records. This is engineering source verification, not clinician approval.
- Raw primary PDFs/HTML, page-separated extraction, URL, final URL, retrieval time, byte count and SHA-256 are included. Never index raw HTML, whole guidelines, the discovery report, or OCR fixtures automatically.

## Runtime retrieval

`knowledge/evidence/catalog.json` is the only runtime corpus. BM25 retrieves locally. `scripts/export_lightrag.py` exports the same approved record IDs for LightRAG mix (graph/vector) ranking; the app fuses rankings and resolves content back to this catalogue. Private patient reports never enter the shared corpus.

## Value semantics

Reference intervals depend on specimen, method, population, age and source sex categories. Diagnostic decision limits and treatment targets are different concepts and are not automatically created from these intervals. Report-supplied ranges take precedence. Missing ranges stay unknown. These records neither diagnose a patient nor define emergency thresholds. Historical manuals remain visibly dated.

## Corrections to the discovery report

- Iowa handbook downloaded from the suggested link is dated 2013 internally, not a current 2026 manual. It is excluded from runtime RAG.
- WHO download URL returned an HTML shell, not a PDF; no new WHO numeric records were admitted.
- Siriraj immunology index is a maintenance page; individual pages are archived but not admitted without review.
- CLSI download is a public landing page, not the paid M100 standard.
- Four sources failed or exceeded the download cap; see manifest. No values were guessed to fill these gaps.

## New source-checked intervals

| Test | Population | Source sex | Interval | Source and PDF page |
|---|---|---|---|---|
| WBC | Age >18 years | F | 4.4–10.3 10^3 cells/µL | [DR-001](https://www.si.mahidol.ac.th/th/manual/Project/PDF/Reference-Ranges-Hematology-2016.pdf) p.1 |
| WBC | Age >18 years | M | 4.5–11.3 10^3 cells/µL | [DR-001](https://www.si.mahidol.ac.th/th/manual/Project/PDF/Reference-Ranges-Hematology-2016.pdf) p.1 |
| RBC | Age >18 years | F | 4.0–5.5 10^6 cells/µL | [DR-001](https://www.si.mahidol.ac.th/th/manual/Project/PDF/Reference-Ranges-Hematology-2016.pdf) p.1 |
| RBC | Age >18 years | M | 4.2–6.1 10^6 cells/µL | [DR-001](https://www.si.mahidol.ac.th/th/manual/Project/PDF/Reference-Ranges-Hematology-2016.pdf) p.1 |
| HGB | Age >18 years | F | 12.0–14.9 g/dL | [DR-001](https://www.si.mahidol.ac.th/th/manual/Project/PDF/Reference-Ranges-Hematology-2016.pdf) p.1 |
| HGB | Age >18 years | M | 12.7–16.9 g/dL | [DR-001](https://www.si.mahidol.ac.th/th/manual/Project/PDF/Reference-Ranges-Hematology-2016.pdf) p.1 |
| HCT | Age >18 years | F | 37.0–45.7 % | [DR-001](https://www.si.mahidol.ac.th/th/manual/Project/PDF/Reference-Ranges-Hematology-2016.pdf) p.1 |
| HCT | Age >18 years | M | 40.3–51.9 % | [DR-001](https://www.si.mahidol.ac.th/th/manual/Project/PDF/Reference-Ranges-Hematology-2016.pdf) p.1 |
| MCV | Age >18 years | F | 80.4–95.9 fL | [DR-001](https://www.si.mahidol.ac.th/th/manual/Project/PDF/Reference-Ranges-Hematology-2016.pdf) p.1 |
| MCV | Age >18 years | M | 80.6–98.8 fL | [DR-001](https://www.si.mahidol.ac.th/th/manual/Project/PDF/Reference-Ranges-Hematology-2016.pdf) p.1 |
| MCH | Age >18 years | F | 25.0–31.2 pg | [DR-001](https://www.si.mahidol.ac.th/th/manual/Project/PDF/Reference-Ranges-Hematology-2016.pdf) p.1 |
| MCH | Age >18 years | M | 25.8–33.1 pg | [DR-001](https://www.si.mahidol.ac.th/th/manual/Project/PDF/Reference-Ranges-Hematology-2016.pdf) p.1 |
| MCHC | Age >18 years | F | 30.2–34.2 g/dL | [DR-001](https://www.si.mahidol.ac.th/th/manual/Project/PDF/Reference-Ranges-Hematology-2016.pdf) p.1 |
| MCHC | Age >18 years | M | 30.8–34.6 g/dL | [DR-001](https://www.si.mahidol.ac.th/th/manual/Project/PDF/Reference-Ranges-Hematology-2016.pdf) p.1 |
| Calcium | Age 18–60 years | All | 8.6–10.0 mg/dL | [DR-005](https://www.si.mahidol.ac.th/th/manual/Project/PDF/Calcium.pdf) p.1 |
| Ionized calcium | Age not specified in range row | All | 4.6–5.2 mg/dL | [DR-006](https://www.si.mahidol.ac.th/th/manual/Project/pdf/ca-ionized.pdf) p.1 |
| Magnesium | Age 21–59 years | All | 1.6–2.6 mg/dL | [DR-007](https://www.si.mahidol.ac.th/th/manual/Project/pdf/magnesium.pdf) p.1 |
| Phosphate | Adults | All | 2.5–4.5 mg/dL | [DR-008](https://www.si.mahidol.ac.th/th/manual/Project/pdf/phosphate.pdf) p.1 |
| TSH | Age >20 years | All | 0.27–4.2 µIU/mL | [DR-028](https://www.si.mahidol.ac.th/th/manual/Project/pdf/tsh.pdf) p.1 |
| FT4 | Age >20 years | All | 0.92–1.68 ng/dL | [DR-029](https://www.si.mahidol.ac.th/th/manual/Project/pdf/FT4.pdf) p.1 |
| Ferritin | Age not specified in range row | M | 30–400 ng/mL | [DR-032](https://www.si.mahidol.ac.th/th/manual/Project/pdf/ferritin.pdf) p.1 |
| Ferritin | Age not specified in range row | F | 13–150 ng/mL | [DR-032](https://www.si.mahidol.ac.th/th/manual/Project/pdf/ferritin.pdf) p.1 |
| Vitamin B12 | Age not specified in range row | All | 197–771 pg/mL | [DR-034](https://www.si.mahidol.ac.th/th/manual/Project/pdf/Vitamin-B12.pdf) p.1 |
