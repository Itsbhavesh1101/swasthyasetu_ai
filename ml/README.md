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

The bounded P19 demonstration consumes that exact synthetic candidate/card evidence, validates it
through the deterministic no-quantum backend, and produces a non-executable experiment plan:

```powershell
backend\.venv\Scripts\python.exe -m ml.quantum.demo --environment LOCAL
```

Every encoding, circuit, optimizer, shot, framework, and executable-backend choice remains
unselected. The command installs or invokes no quantum framework, simulator, provider, network, or
hardware and makes no comparative or quantum-advantage claim.

`ml.quantum` currently contains only detached, metadata-only P19-A contracts, a deterministic
no-quantum test fake, and non-executable P19-B experiment-plan metadata. Encoding, circuit,
optimizer, shots, backend, and framework remain explicitly unselected. The package does not contain
a circuit, simulator, quantum framework, training, inference, benchmark result, hardware adapter,
or production integration.
