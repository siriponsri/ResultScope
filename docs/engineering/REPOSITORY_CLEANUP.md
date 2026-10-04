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
| docs/coursework-demo/ResultScope_Coursework_Demo_v1 | Keep unchanged | Runtime synthetic knowledge and evaluator dependencies |
| addons/resultscope_evidence_v1 | Keep unchanged | Runtime public references, rights records and checksummed verifier bundle |
| knowledge/snapshots/legacy | Keep original source bytes | Stable provenance for explicitly non-release legacy sources |
| knowledge, evaluation, indexes, tests/fixtures | Keep | Source, benchmark and regression data; Thai is intentional data |
| NOTICE and third-party notices | Keep | Attribution and unresolved rights cannot be deleted by a rebrand |
| Owner .env, .venv, data stores, secrets, ledger, PROMPT.md, .git | Preserve in place | Local state is outside the replacement payload |
| Future evaluation reports | Write under docs/evidence/runs | Avoid rebuilding the obsolete phase-progress directory |

There are 144 explicit removals in scripts/repo_cleanup_manifest.json. Each is
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

## Dry run and apply

Run only after the replacement payload has been verified and editing has stopped:

```powershell
python scripts/apply_repo_cleanup.py
# Inspect every eligible path and any error. A mismatch must be investigated.
python scripts/apply_repo_cleanup.py --apply
```

The first command is read-only. The second verifies the historical archive, all
listed paths and each file's original checksum before deleting anything. UTF-8
files may differ only in CRLF/LF line endings. Symlinks, junctions, traversal paths,
changed content, missing archive or corrupted archive block the operation.

Before deletion, actual current bytes are copied into a unique sibling directory
named ResultScope-pre-refresh-backup-*/removed-files.zip. That backup is verified.
The script rechecks every candidate, removes only named files, leaves directories
and unlisted items intact, and prints the backup path. Run without concurrent edits.
An already absent listed file is skipped, making a second run harmless.

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
addons/resultscope_evidence_v1/data/records-review.csv. Its checked-in LF bytes have
SHA-256 ce566648ade1b2674fdc3f617d66ec9d075fd3ca4fd60f89249d55e30c5f847f.
Restoring only CRLF produces the exact already-pinned package hash
d8cb1f902fc5cf0ce7fea81c0ab4adcbd625cebd99b4964d072d502a14495b19.
The refresh ships those restored bytes. No CSV fields, manifest hashes, source
approvals or rights are changed. Other addon files remain byte-for-byte unchanged.
