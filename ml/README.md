# ML / QML Research

Training, benchmarking, classical ML, and hybrid quantum-classical research live here. Research
models do not become production models automatically.

## Offline classical-ML demonstration

The bounded college demonstration replays fixed, non-medical synthetic mechanics through the
existing P18 registry, split, train-only preprocessing, nearest-centroid baseline, locked-test
exact-match evaluation, model-card, and unapproved-candidate contracts:

```powershell
backend\.venv\Scripts\python.exe -m ml.research.demo --environment LOCAL
```

The command performs no network, database, filesystem-artifact, backend, or patient-runtime work.
Its canonical JSON receipt is `ENGINEERING_ONLY`, `TEST_ONLY_UNAPPROVED`, `NOT_ACTIVATED`, and
`NO_PERFORMANCE_OR_CLINICAL_CLAIM`. `STAGING`, `PILOT`, and `PRODUCTION` fail closed. The output is
not a medical benchmark, validated model, diagnostic result, or live P18 acceptance evidence.

`ml.quantum` currently contains only detached, metadata-only P19-A contracts, a deterministic
no-quantum test fake, and non-executable P19-B experiment-plan metadata. Encoding, circuit,
optimizer, shots, backend, and framework remain explicitly unselected. The package does not contain
a circuit, simulator, quantum framework, training, inference, benchmark result, hardware adapter,
or production integration.
