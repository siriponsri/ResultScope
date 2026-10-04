# Vendor packages

`vendor/resultscope_evidence_v1/` is an owner-supplied, pinned imported evidence
bundle used by the optional public-reference adapter. It is kept intact as one
reproducibility unit, including its source snapshots, rights metadata, package
tests, verifier, disabled Clef module, and original documentation. It is not
project-authored third-party software, and no upstream license is inferred here.

The supported offline verifier is:

```powershell
python vendor/resultscope_evidence_v1/verify.py
```

The application default is `vendor/resultscope_evidence_v1`. An existing owner
configuration containing exactly `addons/resultscope_evidence_v1` is mapped to
the canonical path for compatibility; arbitrary custom, missing, or invalid
roots continue to fail closed. `PUBLIC_REFERENCE_ENABLED` remains opt-in, and
the bundle is never release business data or a patient-specific reference range.

Do not add README files or generated output inside the checksummed bundle. Do not
deduplicate or edit its files, even when a package file is not imported by the
main application.
