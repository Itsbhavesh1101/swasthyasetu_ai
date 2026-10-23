# P18 Readiness Gate Review

> **DRAFT — PROPOSED RESEARCH AND MODEL-GOVERNANCE REVIEW INVENTORY, NOT APPROVED P18 PHASE OR OFFICIAL GATE COUNT**

**Recorded:** 2026-10-24

**Reviewed baseline:** `main` at `0b1eeaf470e129a29f18426ab9a0c4c115fbb4ac`

**Runtime status:** P18 and P19 **NOT STARTED**

**Approval status:** No human approval, dataset, task, benchmark, model, or official P18 gate count exists.

This inventory supports review of [Spec 18](../18_CLASSICAL_ML_SPEC.md). `OPEN` and `BLOCKED` describe missing evidence; they are not approval arithmetic. Roles are accountable functions, not named reviewers or signatures.

## 1. Research use case and clinical/epidemiological authority — BLOCKED

- **As-built evidence:** no clinical indication, task, target, label, positive class, intended population, endpoint, model, or inference API exists.
- **Accountable roles:** clinical/epidemiology owner; research lead; biostatistics/ML-validation owner; model-governance owner; institutional owner.
- **Missing decisions/evidence:** intended research question; target and label-source authority; positive class; population/site/time scope; inclusion/exclusion; clinical relevance; intended and prohibited uses; error-cost assumptions; independent review.
- **Future review artifact:** signed, versioned research protocol and clinical-task statement with limitations and expiry/re-review trigger.
- **Negative tests:** unknown/changed target, label inversion, population mismatch, prohibited inference, post-outcome label leakage, and model statement presented as diagnosis must fail closed.
- **Synthetic possibility:** a separately authorized non-medical fixture may exercise contracts but cannot resolve this domain.
- **STOP:** no dataset selection, real experiment, metric optimization, model card, or inference until the task and clinical authority are approved.

## 2. Dataset source, license, privacy, ethics, and custody — BLOCKED

- **As-built evidence:** no approved/downloaded dataset, manifest, dataset registry, research storage, ethics record, data flow, or custodian is present.
- **Accountable roles:** data custodian; privacy/legal/ethics owner; security owner; clinical owner; research lead; institutional owner.
- **Missing decisions/evidence:** source/publisher, immutable version/checksum, acquisition and redistribution rights, purpose and lawful authority, health/sensitive-data classification, protected populations, subject linkage/de-identification risk, permitted features, retention/deletion/backups, storage region, access, disclosure/egress, incident duties.
- **Future review artifact:** signed dataset admission record, data-flow inventory, license/rights evidence, ethics/privacy assessment, custody and deletion plan.
- **Negative tests:** denied/withdrawn license, unapproved data, re-identification, wrong subject/tenant, unauthorized egress, retention expiry, incomplete deletion, and sensitive tracker/log leakage.
- **Synthetic possibility:** generated non-medical data only under a later narrow prompt; it is not an approved real benchmark dataset.
- **STOP:** no download, access, copying, transformation, or benchmark while any admission evidence is unknown.

## 3. Split and leakage discipline — OPEN

- **As-built evidence:** no split generator, manifest, dataset, preprocessing pipeline, calibration set, or locked test set exists.
- **Accountable roles:** biostatistics/ML-validation owner; research lead; data custodian; clinical/epidemiology owner.
- **Missing decisions/evidence:** subject/group/site/time partition; split ratios and seed; holdout freeze and access; label adjudication; missingness; duplicate policy; training-only transformations; calibration strategy; reproducibility oracle.
- **Future review artifact:** immutable split manifest and signed leakage review bound to dataset and code hashes.
- **Negative tests:** same subject/group across folds, near-duplicate rows, future/post-outcome features, site leakage, fit on test, test-driven tuning/calibration, split mutation, and non-deterministic regeneration.
- **Synthetic possibility:** an offline fixture may prove mechanics only after authorization.
- **STOP:** no performance comparison or candidate registration without a frozen, leakage-reviewed split.

## 4. Classical baselines and evaluation metrics — BLOCKED

- **As-built evidence:** no baseline, training run, metric output, threshold, calibration, subgroup result, confidence interval, or model claim exists.
- **Accountable roles:** clinical/epidemiology owner; biostatistics/ML-validation owner; research lead; fairness/ethics reviewer; model-governance owner.
- **Missing decisions/evidence:** task-suitable simple baseline and candidates; primary/secondary metrics; imbalance strategy; sensitivity/specificity and false-negative analysis; AUROC/AUPRC applicability; calibration/Brier; subgroup dimensions; uncertainty/confidence intervals; external/temporal shift; meaningful comparison and abstention.
- **Future review artifact:** pre-registered evaluation and statistical-analysis plan, followed by reproducible results and independent review.
- **Negative tests:** degenerate classes, mislabeled positive class, metric misuse, threshold chosen on test, missing calibration, subgroup suppression, unstable intervals, and unsupported clinical utility claim.
- **Synthetic possibility:** metric unit fixtures can later validate math but provide no performance or clinical evidence.
- **STOP:** no metric target, threshold, superiority, diagnostic-validity, fairness, or patient-facing claim before qualified review.

## 5. Research isolation, dependencies, tooling, and artifact security — OPEN

- **As-built evidence:** `/ml`, backend ML, and quantum adapter locations are placeholders; no research dependency profile, MLflow service, artifact store, production loader, or sidecar is active.
- **Accountable roles:** architecture owner; security owner; platform/operations owner; research lead; privacy owner.
- **Missing decisions/evidence:** isolated `ml-research` environment; exact task-justified package versions/licenses; network and identity boundary; MLflow/Optuna/SHAP activation need; secrets; tracker data classification; private artifact custody; safe serialization; hashes/signatures; backup/deletion; incident controls.
- **Future review artifact:** reviewed threat model, dependency proposal, deployment/data-flow diagram, artifact trust policy, and operational runbook.
- **Negative tests:** import from patient/safety dependency closure, tracker exposure, raw-data logging, malicious serialization, unsigned/corrupt/substituted artifact, floating download, unauthorized upload, and telemetry egress.
- **Synthetic possibility:** later isolated unit contracts need no live service unless expressly authorized.
- **STOP:** no package/service/loader/sidecar, artifact execution, or patient-runtime dependency before separate authorization and security review.

## 6. Experiment lineage, candidate governance, and clinical non-authority — BLOCKED

- **As-built evidence:** canonical conceptual `ExperimentRun`, `ModelRegistration`, and `RiskAssessment` definitions exist, but no P18 implementation, registration, candidate, card, approval record, or inference exists.
- **Accountable roles:** model-governance owner; clinical model reviewer; research lead; security/privacy owners; release owner; independent validator.
- **Missing decisions/evidence:** run lineage; model owner/version; purpose/dataset/metrics/limitations; product-versus-research lifecycle mapping; identity and signature; segregation; task/population/use scope; calibration/threshold provenance; expiry; suspension/rollback/retirement; historical trial protection.
- **Future review artifact:** immutable run package, model card, candidate record, lifecycle decision, and signed approval or rejection record.
- **Negative tests:** MLflow-triggered deployment, status aliasing, missing approval scope, expired/revoked approval, mutable card/artifact, model output asserted as diagnosis, FHIR confirmation, or safety override.
- **Synthetic possibility:** future fake candidate records may test state enforcement but confer no approval.
- **STOP:** tracker state, training completion, or technical validation cannot activate clinician or patient inference.

## 7. P19 parity and comparative benchmark ownership — BLOCKED

- **As-built evidence:** no P18 baseline, approved task, split, metric package, QML contract, simulator run, or QML dependency exists.
- **Accountable roles:** P18 research owner; P19 research owner; biostatistics/ML-validation owner; architecture owner; model-governance owner; independent reviewer.
- **Missing decisions/evidence:** one approved shared target, label, dataset, split, preprocessing assumptions, metrics, seeds, resource budget, uncertainty method, held-out generalization protocol, simulator scope, and comparison ownership.
- **Future review artifact:** signed parity protocol referencing immutable P18 evidence plus transparent compute/circuit resource reporting.
- **Negative tests:** changed split/target, unequal preprocessing, cherry-picked seeds, incomparable metrics, hidden compute, patient-runtime dependency, safety-path impact, and unsupported quantum-advantage statement.
- **Synthetic possibility:** none authorizes P19; simulator mechanics require a separate prompt after P18 prerequisites.
- **STOP:** P19 remains blocked until a reproducible approved P18 classical baseline exists.

## 8. Security, privacy, quality, incident, and rollout decisions — BLOCKED

- **As-built evidence:** normal quality/security CI exists, but it is not model validation; P22 is not complete and there is no research incident or model rollout plan.
- **Accountable roles:** security owner; privacy/legal/ethics owner; quality owner; clinical/model-governance owner; operations/incident owner; release owner; institutional owner.
- **Missing decisions/evidence:** threat/privacy assessments; deletion/withdrawal; breach handling; contamination response; runtime isolation; authorization/audit; monitoring without patient features; regression thresholds; rollback; pilot scope; stakeholder signoffs; production release decision.
- **Future review artifact:** approved assessments, incident exercises, rollback/recovery evidence, independent validation, and separately signed pilot/production release record.
- **Negative tests:** breach/deletion failure, poisoned data, unauthorized activation, stale approval, cross-tenant access, monitoring leakage, rollback failure, optional-model outage affecting P7/P9, and CI interpreted as clinical validation.
- **Synthetic possibility:** adversarial engineering tests may later be authorized without patient data.
- **STOP:** no pilot, production, patient/clinician presentation, or external claim until all applicable human decisions and technical evidence are current.

## Unsigned bounded decision and evidence template

This blank template records no approval. A populated record is effective only through a future authenticated, authorized, auditable process approved by accountable owners.

| Field               | Required content                                                            |
| ------------------- | --------------------------------------------------------------------------- |
| Decision ID/version | Immutable identifier and revision                                           |
| Domain              | One bounded review domain above                                             |
| Scope               | Task, target, dataset, population, site, period, purpose, environment       |
| Evidence refs       | Immutable source IDs, hashes, code SHA, run IDs, assessments, test reports  |
| Alternatives        | Considered options and consequences                                         |
| Decision            | Approve, reject, defer, or request evidence; never inferred from blank text |
| Conditions          | Constraints, prohibited uses, monitoring and re-review triggers             |
| Effective/expiry    | Explicit timestamps or conditions                                           |
| Rollback/withdrawal | Suspension, deletion, downstream invalidation and communication steps       |
| Accountable roles   | Required role functions and segregation                                     |
| Signatures          | **UNSIGNED — pending future approved identity/signature mechanism**         |

## Owner and risk register

| Risk / unresolved decision                   | Accountable roles                                | State   | Required evidence                      | STOP impact                   |
| -------------------------------------------- | ------------------------------------------------ | ------- | -------------------------------------- | ----------------------------- |
| Clinical task/label/population absent        | Clinical/epidemiology, research, institutional   | BLOCKED | Approved research protocol             | No real benchmark             |
| Dataset/license/legal/ethics/custody absent  | Data custodian, privacy/legal/ethics, security   | BLOCKED | Admission and rights package           | No data access/download       |
| Split/leakage/calibration protocol absent    | Biostatistics/ML validation, research            | OPEN    | Frozen manifest and test plan          | No evaluation claim           |
| Metrics and error-cost policy absent         | Clinical, biostatistics/ML validation            | BLOCKED | Pre-registered analysis plan           | No threshold/utility claim    |
| Research runtime/tooling design absent       | Architecture, security, operations               | OPEN    | Isolated dependency/deployment review  | No service/package activation |
| Lifecycle vocabulary mismatch unresolved     | Model governance, clinical, architecture         | BLOCKED | Explicit mapping and transition policy | No candidate promotion        |
| Artifact trust/serialization controls absent | Security, model governance, operations           | BLOCKED | Hash/signature/loader policy           | No artifact execution         |
| P19 parity baseline absent                   | P18/P19 research, independent validation         | BLOCKED | Approved P18 benchmark                 | No P19 implementation/claim   |
| Pilot/production release authority absent    | Clinical, privacy, security, operations, release | BLOCKED | Signed release decision                | No live inference             |

## FR-ML-001..017 traceability

| ID        | Canonical requirement                                                                          | Draft/evidence                    | Missing decision or artifact                 | Live status  |
| --------- | ---------------------------------------------------------------------------------------------- | --------------------------------- | -------------------------------------------- | ------------ |
| FR-ML-001 | The platform SHALL include an isolated research workflow for classical disease-risk modelling. | Spec §A–B; placeholders only      | Approved architecture and implementation     | NOT VERIFIED |
| FR-ML-002 | Researchers SHALL be able to ingest approved benchmark/open biomedical datasets.               | Spec §C; none approved            | Admission decision and ingest implementation | NOT VERIFIED |
| FR-ML-003 | Datasets SHALL undergo schema/data-quality validation.                                         | Spec §C–D design                  | Validator and executed evidence              | NOT VERIFIED |
| FR-ML-004 | The pipeline SHALL support explicit missing-data handling.                                     | Spec §D–E design                  | Task policy and implementation               | NOT VERIFIED |
| FR-ML-005 | The pipeline SHALL support feature normalization/scaling where appropriate.                    | Spec §D design                    | Approved preprocessing and test              | NOT VERIFIED |
| FR-ML-006 | The pipeline SHALL support reproducible feature engineering.                                   | Spec §B, §D design                | Approved features and run evidence           | NOT VERIFIED |
| FR-ML-007 | The pipeline SHALL support feature selection/dimensionality reduction.                         | Spec §B, §D design                | Approved method and leakage test             | NOT VERIFIED |
| FR-ML-008 | Evaluation SHALL use explicit split methodology and leakage safeguards.                        | Domain 3 and Spec §D/§I           | Frozen split and executed tests              | NOT VERIFIED |
| FR-ML-009 | The system SHALL support multiple classical baseline models.                                   | Domain 4 and Spec §E              | Implemented approved candidates              | NOT VERIFIED |
| FR-ML-010 | Evaluation SHALL report sensitivity/recall where clinically relevant.                          | Domain 4 design                   | Qualified selection and results              | NOT VERIFIED |
| FR-ML-011 | Evaluation SHALL report specificity where clinically relevant.                                 | Domain 4 design                   | Qualified selection and results              | NOT VERIFIED |
| FR-ML-012 | Appropriate discrimination metrics such as AUROC/AUPRC SHALL be supported.                     | Domain 4 design                   | Metric implementation/results                | NOT VERIFIED |
| FR-ML-013 | Risk models SHOULD be evaluated for calibration.                                               | Domain 3–4 design                 | Applicability and evidence                   | NOT VERIFIED |
| FR-ML-014 | Approved model types SHALL provide suitable explainability outputs where possible.             | Spec §E–F boundary                | Approved model and explanation validation    | NOT VERIFIED |
| FR-ML-015 | Trained models SHALL be versioned/registered.                                                  | Domain 6 design                   | Registry and candidate                       | NOT VERIFIED |
| FR-ML-016 | Promoted models SHALL include documented purpose, dataset, metrics and limitations.            | Domain 6 design                   | Governed promotion/card evidence             | NOT VERIFIED |
| FR-ML-017 | Research models MUST NOT automatically become production decision models.                      | Spec §A/§G; accepted architecture | Runtime enforcement and release evidence     | NOT VERIFIED |

## AC-P18-001..010 review

| ID         | Canonical acceptance criterion                                     | Current result                                                                                                | Live status  |
| ---------- | ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------- | ------------ |
| AC-P18-001 | Dataset source/license/version is documented for real benchmark.   | No approved real dataset. A synthetic future exercise does not satisfy this real medical benchmark criterion. | NOT VERIFIED |
| AC-P18-002 | Data schema/quality validation exists.                             | Design only                                                                                                   | NOT VERIFIED |
| AC-P18-003 | Train/validation/test split is explicit and reproducible.          | Design only                                                                                                   | NOT VERIFIED |
| AC-P18-004 | Preprocessing avoids test leakage.                                 | Proposed tests only                                                                                           | NOT VERIFIED |
| AC-P18-005 | At least one classical baseline trains end to end.                 | No training; prohibited in this phase                                                                         | NOT VERIFIED |
| AC-P18-006 | Relevant metrics are recorded.                                     | No experiment or metric output                                                                                | NOT VERIFIED |
| AC-P18-007 | Calibration is evaluated where appropriate.                        | No applicability decision or evidence                                                                         | NOT VERIFIED |
| AC-P18-008 | Experiment metadata and artifacts are reproducible.                | Contract proposal only                                                                                        | NOT VERIFIED |
| AC-P18-009 | Model candidate is registered with status.                         | No registry or candidate                                                                                      | NOT VERIFIED |
| AC-P18-010 | Training does not automatically activate patient-facing inference. | Required architecture; no live training/inference test                                                        | NOT VERIFIED |

## Readiness conclusion

P18 and P19 runtime remain **NOT STARTED**. No official gate count and no human approval exist. P19 is blocked by the absent approved task and reproducible classical baseline. Every live `FR-ML-001..017` and `AC-P18-001..010` outcome remains **NOT VERIFIED**.

The next action is accountable review of the task, data, privacy/ethics, split/evaluation, research architecture, artifact security, governance-lifecycle, incident, and release decisions. Only after recorded decisions may a new narrowly scoped prompt authorize a safe P18-A engineering subset. This document authorizes no dataset access, training, service, model, inference, P19 work, pilot, or production release.
