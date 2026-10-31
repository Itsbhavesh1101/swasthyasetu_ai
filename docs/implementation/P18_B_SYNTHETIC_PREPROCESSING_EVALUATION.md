# P18-B Synthetic Preprocessing and Evaluation

## Status

PARTIAL — bounded offline engineering-only P18-B foundation. P18 remains PARTIAL, every live
`FR-ML-*` and `AC-P18-*` outcome remains unverified, and P19 remains blocked.

## Baseline and isolation

This unit starts from merged `main` at
`67a72fb1be069682e32209e01e2d4370062133dc`. Executable code remains under `/ml` and is covered by
the existing research quality gate. The production backend imports no research package and gains no
dependency, module registration, route, worker, feature flag, storage, or inference behavior.

## Implemented mechanics

- Immutable non-medical feature rows and split configurations with strict direct-constructor
  validation, bounded capacity, exact ratios, seeded group-aware deterministic allocation, and
  canonical manifest fingerprints.
- Explicit train, validation, and locked test membership with duplicate, overlap, incomplete-group,
  assignment-order, dataset-drift, and protected-environment rejection.
- Train-only mean imputation and standard-score fitting with exact row/group membership, explicit
  missing counts, deterministic zero-variance handling, immutable statistics, and canonical receipt
  fingerprints.
- Partition transformation bound to the exact split and preprocessing receipt.
- Exact test-membership evaluation using only closed synthetic classes and content-free correct/error
  counts. Missing, extra, duplicate, degenerate, or drifted inputs fail closed.
- Adversarial tests proving test-value changes cannot affect fitted preprocessing statistics and
  protected environments reject before hostile caller collections are inspected.

## Explicit negative scope

No real or sample biomedical data, dataset download, medical feature, clinical label, approved task,
target, estimator, training, hyperparameter selection, probability, threshold, sensitivity,
specificity, AUROC/AUPRC, calibration, fairness claim, model artifact, candidate, model card,
MLflow/tracker, dependency, persistence, migration, API, UI, worker, runtime activation, P18-C/D/E,
or P19 behavior is introduced.

## Acceptance truth

These synthetic mechanics do not establish a real dataset source/license/version, approved split,
task-specific preprocessing, clinically selected metric, trained baseline, calibration evidence,
model registration, or reproducible medical benchmark. `FR-ML-001..017` and `AC-P18-001..010`
remain LIVE NOT VERIFIED. `TEST_ONLY_UNAPPROVED` receipts cannot authorize research admission,
pilot, production, or patient-facing use.

## Next action

Review this isolated engineering boundary. A separately bounded P18-C may implement a deterministic
synthetic-only baseline model without medical data or a performance claim. Real dataset use,
governed benchmark execution, model registration/inference, P18-E, and all P19 work remain stopped
on the accountable decisions in `P18_READINESS_GATE_REVIEW.md`.
