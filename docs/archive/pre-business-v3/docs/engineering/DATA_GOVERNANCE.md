# Data governance

| Data | Purpose | Model use |
|---|---|---|
| MedlinePlus short paraphrases | Real public educational reference | Retrieved explanatory evidence |
| Pinned Thai lab manual records/PDFs | Real published reference with source-specific intervals | Retrieved explanatory evidence; no automatic substitution of ranges |
| Six supplied Thai demo reports | Synthetic user context and OCR evaluation | Actual pixels after explicit read; confirmed rows after review |
| `expected_results.json` | Evaluator gold labels only | Never read by runtime code or indexed |
| Legacy synthetic business KB | Historical local v1 tests | Not on v2 retrieval path |
| User-selected report | Optional user context | Provider receives pixels after consent; confirmed fields enter chat |

The supplied ZIP was copied unchanged to `examples/thai_lab_reference_v3`. Verify original
assets against its `MANIFEST.json`. All six filenames, PDFs, PNGs, previews, Thai README
and expected-results file remain in the source package. The manifest itself is the
owner's supplied artifact. Vercel excludes the answer key; the API only whitelists demo
PNG/PDF IDs. Uploading a byte-identical fixture also retains its synthetic classification.

V2 conversation state is encrypted with AES-GCM and carried in tab memory, bound to an
HttpOnly signed cookie and purpose. Default lifetime is one hour. Images and chat bodies
are not persisted by the application. Upstream providers receive relevant content and
may retain it under their own terms. A shared Redis counter stores cycle/call counts,
not patient data. Exported chats are user-managed files.

Public does not mean universally licensed or clinically approved. Original lab PDFs keep
their publisher rights and existing bundle notices. MedlinePlus entries are original brief
paraphrases with links. Recheck upstream editions, specimen/method/population differences,
rights and clinical suitability before release. Do not add real identifiable patient data
to this repository or a shared retrieval index.
