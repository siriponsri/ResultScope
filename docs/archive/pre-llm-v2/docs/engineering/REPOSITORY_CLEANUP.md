# Repository cleanup and preservation

This migration replaces outdated guidance with maintained English product,
engineering, operations and user documentation. It does not rewrite historical
evidence or translate byte-addressed source material into a different corpus.

## Decisions

| Material | Action | Why |
| --- | --- | --- |
| App, provider guards, tests and current scripts | Keep; change only package-listed files | Runtime and regression coverage remain authoritative |
| README, AGENTS, DESIGN, BUSINESS_BRIEF, active guides | Replace with current English guidance | One coherent product identity and startup procedure |
| Old phase plans, task packets, progress evidence | Archive original bytes, then remove listed loose files | Retain evidence without competing setup instructions |
| Old root patch prompts and release checklists | Archive and remove listed files | Superseded by current setup, readiness and closeout guides |
| Legacy scene.js, Hallmark installer and run metadata | Archive and remove listed files | No imports in the new workspace; not required tooling |
| `examples/coursework_demo_v1` | Keep intact at its canonical home | Synthetic knowledge, images, evaluation inputs, and evaluator dependencies |
| `vendor/resultscope_evidence_v1` | Keep intact at its canonical home | Pinned public references, rights records, and checksummed verifier bundle |
| knowledge/snapshots/legacy | Keep original source bytes | Stable provenance for explicitly non-release legacy sources |
| knowledge, evaluation, indexes, tests/fixtures | Keep | Source, benchmark and regression data; Thai is intentional data |
| NOTICE and third-party notices | Keep | Attribution and unresolved rights cannot be deleted by a rebrand |
| Owner .env, .venv, data stores, secrets, ledger, PROMPT.md, .git | Preserve in place | Local state is outside the replacement payload |
| Future evaluation reports | Write under docs/evidence/runs | Avoid rebuilding the obsolete phase-progress directory |

There were 144 explicit removals in the earlier product-refresh cleanup. Each is
preserved inside docs/archive/pre-redesign-c9236f5.zip. The archive also preserves
10 earlier documents/configuration records that have current replacements.
No wildcard removal or recursive repository deletion is authorized.

## Why source snapshots were needed

At the original c9236f5 baseline, the manifest's AGENTS.md and BUSINESS_BRIEF.md
checksums did not match those files. The original API citation test also failed in
an untouched baseline copy. The refresh stores exact c9236f5 versions of those two
files and the legacy Phase 1 plan under knowledge/snapshots/legacy, then binds the
three corresponding manifest rows to those bytes. Their non-release approval and
eligibility classifications are unchanged. This is provenance reconciliation, not
business approval or an exemption from checksum validation.

.gitattributes preserves byte-addressed source and fixture trees on checkout. It
does not change global Git configuration or authorize blanket renormalization.

## Canonical ownership map

| Area | Canonical home | Boundary |
|---|---|---|
| Maintained application | `main.py`, `config.py`, `routers/`, `services/`, `templates/`, `static/` | Runtime code and browser assets |
| Pinned evidence | `vendor/resultscope_evidence_v1/` | One immutable imported bundle; verifier and package tests stay inside |
| Synthetic examples | `examples/coursework_demo_v1/` | One immutable synthetic coursework bundle; never release data |
| Current corpus | `knowledge/` | Application source manifests and release/synthetic contracts |
| Generated local output | `data/` | Regenerable indexes and owner runtime state; private files remain ignored |
| Current checks | `evaluation/`, `tests/`, `scripts/` | Supported application tests and maintenance commands |
| Current guidance | `docs/product/`, `docs/operations/`, `docs/engineering/`, `docs/user/` | Maintained English instructions |
| Historical material | `docs/archive/` | Labelled records, not active commands |

The old `addons/` and `docs/coursework-demo/` prefixes are retired. The exact
legacy public-reference default remains a compatibility alias in
`services/public_reference.py`; arbitrary custom roots still fail closed.
Generated knowledge indexes under `data/indexes/` are ignored and can be rebuilt
from the canonical corpus with `python scripts/build_index.py --mode synthetic`.

## Historical cleanup procedure

The one-time cleanup script and manifests are preserved under
`docs/archive/product-refresh-v2/`. They are historical source records, not
supported commands at their relocated paths. Do not run them from the current
tree. The verified archive and the earlier closeout describe the old removal
cycle; this migration used explicit canonical package moves and direct hash
comparison instead.

## Recovery

Before a local commit, use the verified sibling backup to recover selected removed
files into a separate directory, inspect them, then copy only the desired paths.
The historical archive also preserves baseline bytes. Git history preserves tracked
replacements. Do not run git reset --hard, git clean, broad checkout/restore, or
extract the whole archive over a repository containing owner changes.

If cleanup reports drift, do not delete the changed file or update hashes to silence
the check. Record the path, keep it intact, and resolve its role with the owner if
it cannot be safely reconciled. Clean up this package's empty directories only if
necessary; Git does not track empty directories.

## Pinned CSV line-ending restoration

The untouched Git baseline also fails the addon verifier at
`vendor/resultscope_evidence_v1/data/records-review.csv`. Its checked-in LF bytes have
SHA-256 ce566648ade1b2674fdc3f617d66ec9d075fd3ca4fd60f89249d55e30c5f847f.
Restoring only CRLF produces the exact already-pinned package hash
d8cb1f902fc5cf0ce7fea81c0ab4adcbd625cebd99b4964d072d502a14495b19.
The refresh ships those restored bytes. No CSV fields, manifest hashes, source
approvals or rights are changed. Other addon files remain byte-for-byte unchanged.
