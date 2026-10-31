# P18-B Synthetic Preprocessing and Evaluation Design

## Intent

Extend the isolated P18 research workspace with deterministic, offline engineering mechanics for
group-aware splitting, train-only preprocessing, and exact-label evaluation. This unit uses only
closed non-medical synthetic identities and values. It produces no medical benchmark, trained
model, validated metric, clinical threshold, artifact, or inference path.

## Selected approach

Use the existing standard-library-only `ml.research` package and its stable content-free errors.
The pipeline operates only in `LOCAL` or `TEST`, reconstructs immutable inputs at trust boundaries,
and binds each derived receipt through canonical SHA-256 fingerprints. The production backend
continues to be prohibited from importing `/ml`.

## Split contract

- Input rows carry closed synthetic row/group identities and at most four finite numeric fixture
  values; `None` is the only missing-value representation.
- An immutable configuration binds the dataset fingerprint, seed, version, and positive basis-point
  ratios summing to 10,000.
- Groups are deterministically ranked by a seeded hash and allocated with deterministic
  largest-remainder apportionment. At least three groups and all train/validation/test partitions are
  required.
- A manifest binds ratios and assignments. Duplicate rows, group overlap, unsorted assignments,
  incomplete partitions, mutation, and protected-environment use fail closed.

## Preprocessing contract

- A plan binds the exact split fingerprint, ordered closed feature names, train-mean imputation,
  standard-score scaling, and `TRAIN` as the only legal fitting partition.
- Fitting verifies exact row/group membership and feature width, then derives statistics only from
  train members. Changing validation or test values cannot alter the receipt.
- Missing training values are counted explicitly. A feature with no observed training value fails;
  a zero-variance feature uses unit scale deterministically.
- Transformation applies the frozen receipt to an explicitly selected partition and returns an
  immutable, fingerprint-bound batch.

## Evaluation contract

- Evaluation accepts only closed `CLASS_ALPHA`/`CLASS_BETA` engineering labels and requires exact
  test-partition membership for both expected and predicted tuples.
- It records only content-free counts and fingerprints. Missing, extra, duplicate, wrong-partition,
  degenerate-class, or drifted preprocessing inputs fail closed.
- Counts are synthetic engineering evidence only. They are not sensitivity, specificity, AUROC,
  calibration, clinical validity, a model result, or an acceptance claim.

## Rejected alternatives

1. Adding scikit-learn or MLflow: unnecessary for deterministic mechanics and would activate a new
   dependency/runtime profile before an approved task exists.
2. Training even a toy estimator: belongs to separately bounded P18-C and could blur the no-model
   boundary.
3. Using patient-like fixtures or medical labels: provides no engineering benefit and conflicts
   with the unresolved privacy, ethics, data-custody, and clinical-task gates.
4. Placing the code in the backend: conflicts with accepted research/runtime isolation.

## Governance result

This is a bounded P18-B engineering subset only. It does not satisfy a live `FR-ML-*` or
`AC-P18-*` outcome, approve a dataset/task/split/metric, or unblock P18-C/D/E or P19. Real data,
training, model registration, inference, and external claims remain stopped by
`P18_READINESS_GATE_REVIEW.md`.
