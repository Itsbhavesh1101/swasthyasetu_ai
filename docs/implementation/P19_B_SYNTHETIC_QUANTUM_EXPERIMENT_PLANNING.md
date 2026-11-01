# P19-B Synthetic Quantum Experiment Planning

**Status:** BOUNDED ENGINEERING-SYNTHETIC NO-RUN FOUNDATION ONLY

**Baseline:** `origin/main @ cda5e5c3a79bdce7dee2900684e4cdd258ab1ded`

**Recorded:** 2026-11-02

## Outcome

The isolated `ml.quantum` package now contains an immutable, non-executable experiment-plan
contract. Each plan binds an exact P19-A request and its P18 synthetic candidate, model-card,
dataset, split, and preprocessing fingerprints to a code commit, dependency-lock hash,
configuration hash, LOCAL/TEST environment, and UTC chronology.

The plan records the absence of scientific and runtime choices explicitly:

- encoding `NOT_SELECTED`;
- circuit `NOT_DESIGNED`;
- optimizer `NOT_SELECTED`;
- shots `NOT_SELECTED`;
- backend `NO_BACKEND_SELECTED`;
- framework `NOT_SELECTED`;
- execution `NOT_EXECUTED`;
- approval `TEST_ONLY_UNAPPROVED`;
- claim `NO_COMPARATIVE_CLAIM`.

Protected environments are rejected before request inspection. Exact environment binding prevents
LOCAL/TEST replay, chronology prevents a plan predating its request, reconstruction detects forced
mutation, and fingerprints cover every field.

## Deliberate exclusions

No encoding value, feature vector, label, qubit count, gate, ansatz, depth, circuit payload,
parameter, optimizer configuration, shot count, noise model, transpilation, backend, framework,
simulator, statevector, QPU, provider, credential, network, queue, training, inference, prediction,
metric, score, runtime, cost, comparison, result, claim, artifact, persistence, API, UI, worker,
dependency, runtime registration, pilot, or production behavior was added.

## Verification boundary

Adversarial tests cover exact upstream binding, deterministic fingerprints, immutable state,
direct-constructor drift, forced mutation, UTC normalization, chronology, environment replay,
protected-environment short circuiting, hostile values, caller mutation, forbidden payload fields,
and absence of execution, promotion, approval, comparison, or claim methods.

## Acceptance truth

This is reproducibility-planning structure relevant to `FR-QML-009`, `FR-QML-013`, and
`FR-QML-016`; it is not executed evidence. It does not implement a VQC or satisfy
`AC-P19-003..007`. `AC-P19-001..009` and `FR-QML-001..018` remain **LIVE NOT VERIFIED**. The
approved-real-P18-benchmark prerequisite and every scientific, privacy, security, dependency,
model-governance, and release decision remain outstanding.

## Next safe action

Independently review the P19-A/P19-B metadata boundaries. Do not select an encoding, circuit,
framework, simulator, metric, or comparative claim until the genuine P18 benchmark and all
requirements in `P19_READINESS_GATE_REVIEW.md` are satisfied.
