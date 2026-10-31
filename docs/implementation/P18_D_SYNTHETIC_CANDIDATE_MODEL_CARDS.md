# P18-D Synthetic Candidate Metadata and Model Cards

## Status

PARTIAL — bounded offline engineering-only P18-D foundation. P18 remains PARTIAL, every live
`FR-ML-*` and `AC-P18-*` outcome remains unverified, and P19 remains blocked.

## Baseline and isolation

This unit starts from merged `main` at
`de95ecc6c7a9ba8ad6a40042bd31d6540e0b52d5`. Executable code remains under `/ml`; the production
backend continues to import no research package and receives no dependency, route, worker, storage,
feature flag, artifact loader, model inference, or registry service.

## Implemented mechanics

- Immutable closed model cards bind exact P18-C model identity/fingerprint, baseline kind, P18-B
  split and preprocessing fingerprints, locked-test evaluation fingerprint, content-free counts,
  engineering-only purpose, fixed limitations, and canonical UTC chronology.
- Card creation recomputes predictions and evaluation from the exact model and locked-test batch;
  copied, drifted, forged, or differently produced receipts fail closed.
- Immutable candidate records bind exact model and card identities/fingerprints and only permit
  `TEST_ONLY_UNAPPROVED` status with `ENGINEERING_ONLY` authority.
- A bounded immutable in-process metadata registry reconstructs snapshots, resolves exact
  ID/version pairs, and rejects duplicate identities or aliases for the same model/card.
- Adversarial coverage includes direct-constructor drift, forced mutation, model/card/result drift,
  split/preprocessing/partition mismatch, naive clocks, hostile inputs, capacity, aliasing,
  content-free failures, and absent lifecycle/serialization surfaces.

## Explicit negative scope

No real or sample biomedical dataset, medical task/label/feature, governed research admission,
scientifically valid benchmark, clinical metric, calibration, threshold, fairness or explainability
claim, executable artifact, file/URI/blob, loader, signature, serializer, MLflow/tracker, database,
persistence, migration, dependency, API, UI, worker, service, backend runtime, promotion, approval,
activation, inference, P18-E, or P19 behavior is introduced.

## Acceptance truth

These are synthetic metadata-integrity mechanics, not a governed model registration. Registry
presence does not satisfy `AC-P18-009`; the synthetic card does not satisfy `AC-P18-016` or create a
promoted model. `FR-ML-001..017` and `AC-P18-001..010` remain LIVE NOT VERIFIED.

## Next action

Review this isolated engineering boundary. P18-E remains blocked until the accountable task,
dataset, license, privacy/ethics, scientific-validation, artifact-security, model-governance, and
release decisions in `P18_READINESS_GATE_REVIEW.md` are recorded. P19 remains blocked until P18
produces a reproducible approved classical benchmark.
