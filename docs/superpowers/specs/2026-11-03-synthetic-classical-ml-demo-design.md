# Synthetic Classical ML Demo Design

## Intent

Provide a fast, genuinely executable college demonstration of the existing P18-A through P18-D
engineering mechanics without weakening the accepted research isolation boundary or implying that a
medical benchmark, approved model, or patient-facing inference exists.

## Goals

- Replay one fixed, non-medical synthetic fixture through the existing dataset registry, group split,
  train-only preprocessing, deterministic nearest-centroid baseline, locked-test evaluation, model
  card, and unapproved candidate registry.
- Produce a deterministic, content-free receipt that exposes provenance fingerprints and mechanical
  counts while explicitly denying clinical and performance claims.
- Offer one offline command that works with the existing locked Python toolchain.
- Fail closed outside `LOCAL` and `TEST`.

## Non-goals and anti-goals

- No real or sample biomedical data, disease task, medical feature, clinical label, probability,
  threshold, calibration, fairness, explainability, diagnostic claim, or validated metric.
- No backend import of `ml`, patient or clinician UI, API, BFF, database, migration, file artifact,
  serializer, model loader, tracker, worker, network access, or dependency change.
- No approval, promotion, activation, inference authority, P18-E benchmark, or P19 comparison.
- The demo must not be described as satisfying any live `FR-ML-*` or `AC-P18-*` criterion.

## Constraints

- Preserve ADR-005: production application code must not import the research package.
- Preserve the P18 readiness STOP boundaries and the `TEST_ONLY_UNAPPROVED` / `ENGINEERING_ONLY`
  states.
- Use only fixed non-medical identifiers, two anonymous numeric features, and closed symbolic classes.
- Validate the environment before constructing or processing the fixture.
- Keep output deterministic and free of raw feature rows, labels, timestamps, paths, or executable
  artifact references.

## Approaches considered

### 1. Production backend endpoint plus patient page

Rejected. It would make the backend import or duplicate research code, blur clinical authority, and
contradict the repository's enforced research isolation.

### 2. TypeScript reimplementation in the patient application

Rejected. It would demonstrate a second algorithm rather than the reviewed P18 implementation and
create unnecessary maintenance and browser exposure.

### 3. Offline Python research command

Selected. It executes the reviewed P18 contracts directly, stays inside `/ml`, requires no new
dependency or infrastructure, and is easy to verify in CI. The command is a research demonstration,
not a product runtime.

## Design

`ml.research.demo` owns a fixed in-memory fixture and exposes
`run_synthetic_classical_demo(environment)`. It validates `LOCAL` or `TEST` first, then constructs a
strict dataset manifest whose hashes bind the fixed fixture, snapshots it in the dataset registry,
builds a deterministic group split, fits preprocessing on the training partition only, transforms
all partitions, fits the existing nearest-centroid baseline on training labels only, predicts the
locked test partition, evaluates closed symbolic labels, builds the existing model card and
candidate, and resolves the candidate through the immutable registry.

The returned immutable `SyntheticClassicalDemoReceipt` includes only closed states, partition and
exact-match counts, and SHA-256 provenance fingerprints. Its fixed claim state is
`NO_PERFORMANCE_OR_CLINICAL_CLAIM`; its runtime state is `OFFLINE_NO_EGRESS`; and its activation
state is `NOT_ACTIVATED`. Direct construction and reconstruction validation prevent forged claim or
fingerprint fields.

Running `python -m ml.research.demo --environment TEST` prints canonical JSON. A protected
environment prints one stable content-free error object to stderr and exits non-zero.

## Verification

- Unit and subprocess tests prove deterministic replay, exact boundary states, receipt validation,
  protected-environment denial, canonical CLI output, and no backend import.
- The complete backend/research quality gate proves formatting, lint, strict typing, research and
  backend regression tests, migration-head stability, compilation, and import smoke.
- Existing six-job CI remains the final integration and security gate.

