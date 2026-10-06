# Documentation tooling

Current business guidance is in docs/business-v3 and docs/user/USER_GUIDE.md; static/docs/user-guide.html is its English web companion. The business report is provided in DOCX and PDF. Import the DOCX into Google Docs and inspect pagination before course submission. Original course documents and source hashes are included.

Run npm run uat:business for the v3 browser fixture suite. scripts/verify_ui_v2.cjs and scripts/build_guide_v2.cjs are retained /lab-era tools; the latter must not overwrite the current business guide. Historical product-manual and screenshot builders remain archived-scope tools. The current architecture and sequence are in docs/business-v3/03_ARCHITECTURE.md; the exact API schema is api-contract.json in that folder.

Optional report source: scripts/build_business_report.py (python-docx and Pillow required). The delivered DOCX was sanitized and visually checked after PDF conversion. A rebuild must repeat layout review.
