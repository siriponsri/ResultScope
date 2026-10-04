# Synthetic examples

`examples/coursework_demo_v1/` is the intact owner-supplied synthetic business
and evaluation package used by local development, tests, and the coursework
demo evaluator. It contains the fictional corpus, source and checksum manifests,
five image cases, question cases, and safety cases. Thai corpus and evaluation
content remain in their original language.

The evaluator is run in retrieval-only plus mocked-provider mode:

```powershell
python scripts/evaluate_coursework_demo.py --provider mocked
```

The package is synthetic development data, not approved release content and not
evidence of a real business, live model quality, clinical validation, or image
performance. Keep the package as one checksum-preserved unit; do not add README
files inside it or copy it into `knowledge/`.
