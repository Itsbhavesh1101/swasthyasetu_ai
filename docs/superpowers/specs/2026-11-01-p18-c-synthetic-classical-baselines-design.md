# P18-C Synthetic Classical Baselines Design

## Intent

Add the smallest transparent classical-baseline mechanics needed to exercise the isolated P18
research pipeline without selecting a medical task, accessing real data, or making a performance or
clinical claim. The unit consumes only P18-B synthetic transformed batches and closed engineering
labels.

## Selected approach

Implement two dependency-free baselines under `ml.research`:

1. `MAJORITY_CLASS` records the majority closed synthetic class in the training partition.
2. `NEAREST_CENTROID` records one deterministic centroid per closed synthetic class and predicts by
   squared Euclidean distance.

An explicit closed tie-break class resolves equal class counts and equal centroid distances. This is
engineering determinism, not a clinical threshold or policy decision.

## Fit boundary

- Fitting is permitted only in `LOCAL` and `TEST`.
- The exact split, reconstructed preprocessing receipt, transformed training batch, and training
  labels must agree by canonical fingerprints and exact row membership.
- Both synthetic classes must be present. Missing, extra, duplicate, degenerate, drifted, or
  non-training inputs fail closed.
- The immutable model binds identity/version, baseline kind, split/preprocessing fingerprints,
  feature count, training membership and label fingerprints, class counts, tie behavior, and
  baseline parameters.

## Prediction boundary

- Prediction accepts only validation or locked-test batches from the exact bound split and
  preprocessing fingerprint.
- Exact partition membership and feature width are revalidated. Training-batch prediction is
  deliberately rejected to prevent accidental in-sample evidence from being presented as
  evaluation.
- Output uses only closed `CLASS_ALPHA`/`CLASS_BETA` engineering labels and can feed the P18-B
  content-free evaluator.

## Governance and security

- Models are always `TEST_ONLY_UNAPPROVED` and expose no register, promote, activate, save, or load
  API.
- There is no serialization, executable artifact, tracker, database, network, API, worker, backend
  import, model registry, or runtime inference path.
- Standard-library implementation avoids activating a research dependency profile before an
  approved task and dataset exist.
- Errors remain stable and content-free; records are frozen and reconstructed at trust boundaries.

## Non-goals

No logistic regression, random forest, SVM, XGBoost, MLP, hyperparameter search, probability,
calibration, clinical metric, explainability claim, feature selection, model card, candidate
registration, real benchmark, P18-D/E, P19 comparison, or patient/clinician use is implemented.

## Acceptance truth

The deterministic end-to-end synthetic exercise is not a real classical benchmark and does not
satisfy `AC-P18-005` or any other live `FR-ML-*`/`AC-P18-*` outcome. P18 remains PARTIAL and P19
remains blocked by the unresolved decisions in `P18_READINESS_GATE_REVIEW.md`.
