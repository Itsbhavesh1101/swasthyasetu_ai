# P18-A Synthetic Dataset and Experiment Registry

## Status

PARTIAL — bounded offline engineering-only P18-A foundation. P18 remains PARTIAL, every live
`FR-ML-*` and `AC-P18-*` outcome remains unverified, and P19 remains blocked.

## Baseline and placement

This unit starts from merged `main` at
`9c3cd1e50092d1385217cdc0e0a5b4bb6f07b76b`. Its executable code lives only under `/ml`, the
accepted isolated research boundary. An architecture test prevents `backend/app` from importing the
research package. The existing backend development toolchain now lints, formats, type-checks, tests,
and compiles `/ml`; the backend runtime and dependency closure remain unchanged.

## Implemented engineering mechanics

- Immutable, slot-based synthetic dataset manifests with closed non-medical source,
  classification, license, admission, and authority tokens.
- Immutable synthetic experiment records that remain `NOT_EXECUTED` and
  `TEST_ONLY_UNAPPROVED`, binding an exact dataset fingerprint, code commit, dependency-lock hash,
  configuration hash, seed, version, and canonical UTC creation time.
- Stable content-free errors, direct-constructor validation, reconstruction at trust boundaries,
  deterministic fingerprints, and deliberate rejection of forged or forced-mutated records.
- Immutable in-memory registries with exact ID/version resolution, bounded snapshots, duplicate
  rejection, no `latest` lookup, no mutation or promotion API, and exact experiment-to-dataset
  fingerprint enforcement.
- Environment-first denial in staging, pilot, and production before caller-provided fixture
  collections are inspected.

## Explicit negative scope

No real or sample biomedical dataset, dataset download, filesystem/network/database I/O, clinical
task, target, label, feature, split, preprocessing, training, estimator, metric, threshold,
calibration, explanation, model artifact, model candidate, model card, tracker, MLflow, API, worker,
event, migration, persistence, dependency, feature flag, backend module registration, inference,
patient/clinician display, approval, P18-B/C/D/E, or P19 behavior is introduced.

## Acceptance truth

These content-free mechanics do not document a real dataset source/license/version and therefore do
not satisfy `AC-P18-001`. They do not provide schema/quality validation for real data, a split,
leakage-safe preprocessing, training, evaluation, calibration, reproducible artifacts, or a governed
model candidate. `FR-ML-001..017` and `AC-P18-001..010` remain LIVE NOT VERIFIED. A technical
`TEST_ONLY_UNAPPROVED` record cannot be interpreted as research admission, validation, pilot, or
production approval.

## Next action

Review this isolated engineering boundary. A separately bounded P18-B may implement synthetic-only
split and preprocessing mechanics without a medical task or performance claim. Real dataset use,
training, model registration, inference, P18-E, and all P19 work remain stopped on the accountable
decisions recorded in `P18_READINESS_GATE_REVIEW.md`.
