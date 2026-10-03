# Phase 4A — real public reference data

## Delivered

17 public PDF snapshots, 17 extracted texts, 26 manually curated reference records covering 17 analytes, deterministic tree and provenance hashes. Sources: Siriraj Hospital and Srinagarind Hospital / Faculty of Medicine, Khon Kaen University. Individual source URLs and fetch timestamps are in `data/source_manifest.json`.

`data_class=public_reference`, `production_approved=false`, `release_eligible=false` are intentional. Do not promote these by changing booleans to make an existing validator green. A dedicated public-reference dataset is separate from synthetic data and from the owner's approved business release dataset.

An additional open-access supplement contains 2 WHO guidelines and 3 educational notes in a separate namespace; see `OPEN_GUIDELINES.md`. These do not change the 26 numeric manual-record count.

## Local integration work

1. Audit actual Phase 4 routes, source and record schemas, policy, namespaces and tests on local main. Record exact HEAD and current status.
2. Add a distinct, clearly named public-reference namespace. Do not merge these hospital documents into the business service catalog or synthetic catalog.
3. Integrate the source manifest and extension through an adapter. Preserve the exact source ID, original URL, snapshot hash, page and corpus version at every evidence boundary.
4. Add real-source citation UI using human-readable organisation/title/page. Keep differing references visible. Do not average ranges, choose a hospital silently, invent dates, translate 'adult' into a numeric age cutoff or assume non-pregnancy.
5. For reports, prefer the reference interval supplied by the report. A missing interval remains unresolved unless a reviewed applicability rule has all required context. This extension only provides evidence lookup; it does not implement that resolver.
6. Reconcile source permission before publishing cached PDFs. Production may need linked originals or separately licensed snapshots; preserve permitted provenance evidence either way.
7. Record source-fetch failures and coverage gaps explicitly. Do not infer complete clinical coverage from the number of PDFs.

## Acceptance

- Real source lookup works offline using pinned bytes and shows its source page.
- Corrupt/missing source fails closed; unknown test abstains.
- Source conflicts and unknown patient context cannot produce a confident patient classification.
- Public-reference ingestion passes its own integrity/structure checks while G1-data remains independently evaluated.
- No original business approvals, contacts, prices or institutions are fabricated.

## Remaining owner data

Actual business identity, owner-approved services/prices/contact/policies and publication rights still need genuine inputs. The current public sources provide real reference material but **do not by themselves meet the course requirement for the selected real business**. Prepare a draft business section with missing fields labeled; do not claim owner approval.
