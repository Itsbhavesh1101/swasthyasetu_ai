# P18-C Synthetic Classical Baselines

## Status

PARTIAL — bounded offline engineering-only P18-C foundation. P18 remains PARTIAL, every live
`FR-ML-*` and `AC-P18-*` outcome remains unverified, and P19 remains blocked.

## Baseline and isolation

This unit starts from merged `main` at
`255d33000b32e69006caa5548987fd24462f3547`. Executable code remains under `/ml`; the production
backend continues to import no research package and receives no dependency, route, worker, storage,
feature flag, model artifact, or inference behavior.

## Implemented mechanics

- Immutable `TEST_ONLY_UNAPPROVED` majority-class and nearest-centroid synthetic baseline records.
- Exact binding to the P18-B split, reconstructed preprocessing receipt, transformed training
  membership, label fingerprint, feature width, class counts, and explicit tie behavior.
- Train-partition-only fitting with strict duplicate, missing, extra, degenerate-class, split-drift,
  preprocessing-drift, forged-record, and protected-environment rejection.
- Validation/test-only prediction with exact split membership and feature-schema checks.
- Deterministic composition with the P18-B content-free evaluator using non-medical synthetic
  classes only.
- No registration, promotion, activation, save, load, or arbitrary serialization surface.

## Explicit negative scope

No real or sample biomedical dataset, medical task/label/feature, approved estimator, logistic
regression, random forest, SVM, XGBoost, MLP, hyperparameter tuning, probability, threshold,
calibration, clinical metric, fairness or explainability claim, model artifact, candidate registry,
model card, MLflow/tracker, dependency, migration, persistence, API, UI, worker, runtime activation,
P18-D/E, or P19 behavior is introduced.

## Acceptance truth

The end-to-end exercise proves only deterministic synthetic mechanics. It does not establish an
approved task, real dataset, scientifically valid baseline, clinically relevant metric, calibration,
external validity, model registration, or production safety. `AC-P18-005` and every other live
`FR-ML-*`/`AC-P18-*` outcome remain NOT VERIFIED.

## Next action

Review this isolated engineering boundary. A separately bounded P18-D may define synthetic-only
candidate metadata and model-card mechanics without promotion authority or executable artifacts.
Real dataset use, governed benchmark execution, live model registration/inference, P18-E, and all
P19 work remain stopped on `P18_READINESS_GATE_REVIEW.md`.
