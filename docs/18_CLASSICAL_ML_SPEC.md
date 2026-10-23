# 18 — Classical ML Research and Reproducible Benchmark Specification

> **DRAFT — PRE-P18 TECHNICAL/HUMAN-REVIEW PREPARATION ONLY; NO DATASET, CLINICAL TASK, REAL TRAINING, VALIDATED MODEL OR LIVE INFERENCE APPROVED**

| Field                        | Value                                                                                                                                                                                                                                     |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Recorded                     | 2026-10-24                                                                                                                                                                                                                                |
| Reviewed repository baseline | `main` at `0b1eeaf470e129a29f18426ab9a0c4c115fbb4ac`                                                                                                                                                                                      |
| Status                       | Research design and accountable-review preparation only                                                                                                                                                                                   |
| Accountable reviewer roles   | Research lead; clinical/epidemiology owner; data custodian; privacy/legal/ethics owner; security owner; architecture/data owner; model-governance owner; biostatistics/ML validation owner; operations/release owner; institutional owner |
| Current evidence             | Empty research placeholders under `/ml`, `backend/app/modules/ml`, and `backend/app/adapters/quantum`; no approved dataset, task, benchmark, trained artifact, tracker service, registry service, or inference path                       |

This draft is subordinate to the [project master specification](00_PROJECT_MASTER_SPEC.md), [system architecture](02_SYSTEM_ARCHITECTURE.md), [privacy and consent specification](26_PRIVACY_CONSENT_SPEC.md), accepted [decision log](implementation/37_DECISION_LOG.md), and [R3 dependency policy](research/r3/R3_CODEX_DEPENDENCY_POLICY.md). The R2-E research documents are evidence proposals, not implementation or clinical authority. The limitations and OPEN/BLOCKED decisions below cannot be resolved by this document, green CI, a paper, a license, a registry label, or an experiment score.

## A. Research-only scope and as-built separation

P18 is intended to prepare a reproducible classical baseline for a later, fair P19 hybrid-QML comparison. The existing `/ml` tree is an isolated research workspace. Its child directories contain placeholders only. The production backend ML and quantum adapter directories likewise contain no implementation. P18 and P19 are **NOT STARTED**.

Future research may consume only explicitly admitted and purpose-authorized inputs. P5 structured patient context is not automatically research data, and P4 general-product or clinical-intake consent does not authorize research reuse. Any future governed product inference must cross a replaceable `ModelInferencePort`, resolve a separately approved immutable model/version and input schema, and preserve P5 provenance. Research code has no authority to write arbitrary clinical state.

P7 deterministic/manual intake and P9 deterministic safety must remain available when every research system, tracker, model, or QML component is absent or fails. Model output cannot diagnose, prescribe, confirm a FHIR Condition or Observation, override a hard safety result, or become clinician-confirmed truth.

This draft selects no clinical indication, disease, dataset, label, target condition, intended population, positive class, covariate, decision threshold, risk band, triage route, or production claim. A future synthetic/offline engineering fixture would demonstrate mechanics only; it would not be dataset-based benchmark evidence, clinical validation, or satisfaction of a real-benchmark criterion.

## B. Bounded architecture and data authority

A separately authorized P18 implementation may propose these bounded research components:

1. an immutable dataset manifest and admission registry;
2. schema, quality, provenance, license, and custody validation;
3. deterministic group/site/time-aware split generation and a locked test set;
4. fit/transform preprocessing plus feature engineering and selection;
5. an experiment runner, metrics/evaluation package, and reproducibility oracle;
6. a research-only tracker and private artifact store;
7. a candidate registry, model card, and SwasthyaSetu governance handoff.

Those component names and possible interfaces are proposals, not implemented contracts. Canonical `ExperimentRun`, `ModelRegistration`, and `RiskAssessment` meanings remain governed by the [domain model](04_DOMAIN_MODEL.md): experiments belong to research; registrations carry explicit approval status; risk assessments are not diagnoses and cannot override hard safety. PostgreSQL remains authoritative for product governance state, and another module may not bypass ownership to perform clinical writes.

R3 identifies MLflow for research and task-appropriate training libraries such as scikit-learn. This draft adds no service, package, version, database, worker, container, or runtime. MLflow metadata, including a label resembling production, is never a SwasthyaSetu approval. Promotion cannot be hidden, automatic, or triggered by an experiment tracker.

## C. Dataset provenance, licensing, ethics, and admission gate

Before any real benchmark, accountable reviewers must make and record decisions for:

- source, publisher/custodian, immutable version, checksum, acquisition path, license, redistribution, derivative-artifact rights, and withdrawal obligations;
- the bounded research purpose, exact target/label and positive class, intended population, site and time coverage, inclusion/exclusion criteria, and source/adjudication authority;
- sensitivity/health-data classification, subject-level linkage, de-identification or pseudonymization limits, re-identification risk, protected/demographic features, consent or other applicable legal authority, ethics review, and prohibited uses;
- data completeness, missingness and representativeness limits, custody, storage region, access roles, external egress, retention, deletion, backup, and incident response.

“Open,” “published,” or downloadable does not mean admitted. An unknown dataset, license, label authority, legal basis, population, or custodian results in **NO REAL BENCHMARK**. This phase prohibits dataset acquisition and download and names no actual dataset or clinical label.

Synthetic/offline fixtures may be considered only in a future separately authorized P18-A/B work unit. They must be unmistakably non-medical, carry no live data, and cannot satisfy `AC-P18-001` for a real benchmark or support a model-performance claim.

## D. Split, leakage, and reproducibility contracts

A future immutable run manifest must bind dataset ID/version/hash; feature/label schema; positive-class definition; prevalence and missingness summaries; split strategy and protected split IDs or hashes; seed; patient/group/site/time partitions; train, validation, calibration, and locked-test boundaries; code commit; dependency-lock hash; estimator and transformation versions; complete run configuration; environment/hardware; metrics implementation/version; and output artifact checksums.

Imputation, normalization, encoding, feature selection, target encoding, balancing, calibration, hyperparameter selection, and threshold selection may fit only on their pre-authorized training or calibration partitions. Test features, labels, outcomes, post-outcome facts, or aggregates must never influence fitting, model selection, calibration, or threshold choice.

Future tests must detect repeated-subject overlap, duplicated and near-duplicated rows/documents, family/group overlap where relevant, future/temporal leakage, post-outcome leakage, site effects, accidental test fitting, split mutation, and non-deterministic regeneration. This draft selects no actual split algorithm, medical covariates, seed, or partition ratios.

## E. Baseline, evaluation, and fairness design

After the task is approved, a simple interpretable baseline such as logistic regression should normally anchor comparison. Depending on task suitability and accountable review, candidates in the master plan may include random forest, SVM, XGBoost, or MLP. No candidate is mandated, trained, validated, or claimed superior here.

Future evaluation may record sensitivity, specificity, precision, recall, F1, confusion matrices, AUROC/AUPRC, calibration and Brier score where appropriate, confidence intervals/uncertainty, missing-data sensitivity, abstention behavior, subgroup performance, and temporal/site/external-shift evidence. Clinical/epidemiology and biostatistics/ML-validation owners must pre-specify primary and secondary metrics, error costs, comparison methods, clinically meaningful operating assumptions, and interpretation before the locked test set is opened.

No metric, prevalence, cutoff, threshold, utility, diagnostic validity, protected-class inference, fairness result, or patient-facing interpretation is asserted. A high aggregate score cannot substitute for calibration, subgroup/error analysis, external validity, or clinical authority.

## F. Experiment and artifact contract

Each future experiment record must bind a unique run ID; task and intended-use version; dataset/source and split manifest; code SHA; random seeds; dependency profile and lock hash; hardware/environment; parameters and transformations; metric code/version; timestamps and status; errors/failures; reproducibility command; and content-addressed output/artifact references with checksums.

Tracking and artifacts require isolated access control, data classification, encryption, retention/deletion, backup, network exposure, and privacy-safe logging decisions. Raw identifiers, patient narratives, clinical documents, unrestricted features, credentials, and sensitive model inputs must not enter generic logs, traces, metrics, model cards, or tracker metadata.

Artifacts must be source-verified, immutable, hashed, schema-bound, privately stored, and released only through trusted-format policy. ONNX is eligible only after native/ONNX prediction, schema, threshold, and telemetry parity review. `skops` may be considered for supported scikit-learn objects. Untrusted pickle, joblib, dill, cloudpickle, remote code, floating downloads, and open model-upload APIs are prohibited. This phase creates no storage schema, service, artifact, container, job, or loader.

## G. SwasthyaSetu model governance and lifecycle mismatch

The canonical domain model uses `EXPERIMENTAL`, `VALIDATED`, `APPROVED_FOR_PILOT`, `APPROVED_FOR_PRODUCTION`, `DEPRECATED`, and `RETIRED`. The historical research plan describes a richer research-to-pilot/production lifecycle. These vocabularies are not silently equivalent and no new state is adopted here.

A future accountable decision must map lifecycle semantics and define permitted transitions, identity/signature evidence, segregation of duties, per-task/population/use approval scope, threshold and calibration provenance, effective and expiry conditions, suspension, rollback, retirement, and protection of historical trials and signatures. Technical `EXPERIMENTAL`, `VALIDATED`, or a research document’s `RESEARCH_VALIDATED` concept does not authorize inference.

Qualified clinical/model reviewers retain authority. Independent P22 security/privacy and release decisions are required before real pilot or production use. Model output remains decision support, not diagnosis; it cannot downgrade deterministic safety or auto-create confirmed FHIR Condition/Observation records.

## H. ML/QML benchmark parity boundary

P19 is blocked until P18 produces a reproducible, approved classical benchmark. A prospective P19 simulator study must reuse the same approved task/label, frozen splits, preprocessing assumptions, and comparable metrics, and report uncertainty, held-out generalization, runtime/compute/circuit resources, and limitations transparently.

No QML task, encoding, circuit, backend, package, experiment, or hardware access is approved. No quantum-advantage claim is made. PennyLane and Qiskit must not be imported into P18 or the normal patient dependency closure. Patient intake, urgent help, and deterministic safety must remain usable with all research and QML systems removed.

## I. Threat, privacy, and negative-test plan

The following are future test proposals, not evidence or clinical fixtures:

| Negative condition                                                              | Required safe result                                       |
| ------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| Dataset/source or license denied, withdrawn, unknown, or mismatched             | Admission and real benchmark stop                          |
| Wrong subject, tenant, population, purpose, or custody boundary                 | Access rejected without disclosure                         |
| Identifier, narrative, feature, or sensitive data enters logs/metrics/artifacts | Test fails; material quarantined and incident path invoked |
| Same subject/group, duplicate, future, post-outcome, temporal, or site leakage  | Split invalidated before evaluation                        |
| Preprocessor fits on test or test guides tuning/calibration/threshold           | Run invalidated; no registration/promotion                 |
| Positive class or label provenance is missing/mislabeled                        | Evaluation fails closed                                    |
| Manifest incomplete, schema incompatible, or feature order changed              | Fit/load/inference rejected                                |
| Source, label, prevalence, feature, or population drift                         | Candidate suspended from comparison/use pending review     |
| Metric receives degenerate class data or invalid probability                    | Typed evaluation failure; no fabricated score              |
| Artifact corrupt, unsigned, unhashed, substituted, or maliciously serialized    | Load rejected before execution                             |
| Unauthorized activation, registry promotion, or cross-tenant access             | Denied and privacy-safe audit/incident signal emitted      |
| Unapproved egress or exposed MLflow/tracker                                     | Connection/use blocked; no data sent                       |
| Regression across model revisions                                               | Candidate cannot advance                                   |
| Calibration/threshold/version approval missing                                  | No governed inference                                      |
| Model attempts to downgrade hard safety                                         | Hard safety remains authoritative; attempt rejected        |

The suite may not contain real patient data, sample medical output, a real clinical risk category, or invented expected clinical behavior. Ethical/legal handling, retention periods, incident ownership, and fixture approval remain pending.

## J. Phase slices, traceability, and STOP boundary

Future work units are separately prompted and all **NOT STARTED**: P18-A dataset/experiment registry; P18-B preprocessing/evaluation; P18-C classical baselines; P18-D model registry/cards; and P18-E first **approved** benchmark task. A future prompt may permit a bounded synthetic-only engineering subset; this draft does not.

### J.1 Canonical functional requirements

| ID        | Canonical requirement                                                                          | Draft section / current evidence    | Missing evidence or owner decision                           | Status            |
| --------- | ---------------------------------------------------------------------------------------------- | ----------------------------------- | ------------------------------------------------------------ | ----------------- |
| FR-ML-001 | The platform SHALL include an isolated research workflow for classical disease-risk modelling. | §A–B; placeholder `/ml` only        | Architecture/security approval and implementation            | LIVE NOT VERIFIED |
| FR-ML-002 | Researchers SHALL be able to ingest approved benchmark/open biomedical datasets.               | §C; no dataset or ingest path       | Dataset, license, ethics/privacy approval and implementation | LIVE NOT VERIFIED |
| FR-ML-003 | Datasets SHALL undergo schema/data-quality validation.                                         | §C–D proposal only                  | Approved schema, validator, fixtures and evidence            | LIVE NOT VERIFIED |
| FR-ML-004 | The pipeline SHALL support explicit missing-data handling.                                     | §D–E proposal only                  | Task-specific policy, implementation and evidence            | LIVE NOT VERIFIED |
| FR-ML-005 | The pipeline SHALL support feature normalization/scaling where appropriate.                    | §D proposal only                    | Task-specific preprocessing and leakage evidence             | LIVE NOT VERIFIED |
| FR-ML-006 | The pipeline SHALL support reproducible feature engineering.                                   | §B, §D proposal only                | Approved features and reproducibility evidence               | LIVE NOT VERIFIED |
| FR-ML-007 | The pipeline SHALL support feature selection/dimensionality reduction.                         | §B, §D proposal only                | Approved method and leakage evidence                         | LIVE NOT VERIFIED |
| FR-ML-008 | Evaluation SHALL use explicit split methodology and leakage safeguards.                        | §D, §I proposed contract/tests      | Approved split plus executed tests                           | LIVE NOT VERIFIED |
| FR-ML-009 | The system SHALL support multiple classical baseline models.                                   | §E candidates only                  | Approved task, implementations and comparative evidence      | LIVE NOT VERIFIED |
| FR-ML-010 | Evaluation SHALL report sensitivity/recall where clinically relevant.                          | §E proposal only                    | Qualified metric selection and results                       | LIVE NOT VERIFIED |
| FR-ML-011 | Evaluation SHALL report specificity where clinically relevant.                                 | §E proposal only                    | Qualified metric selection and results                       | LIVE NOT VERIFIED |
| FR-ML-012 | Appropriate discrimination metrics such as AUROC/AUPRC SHALL be supported.                     | §E proposal only                    | Metric implementation and results                            | LIVE NOT VERIFIED |
| FR-ML-013 | Risk models SHOULD be evaluated for calibration.                                               | §D–E proposal only                  | Applicability decision, calibration split and results        | LIVE NOT VERIFIED |
| FR-ML-014 | Approved model types SHALL provide suitable explainability outputs where possible.             | §E–F boundary only                  | Approved model/task and validated explanation evidence       | LIVE NOT VERIFIED |
| FR-ML-015 | Trained models SHALL be versioned/registered.                                                  | §F–G proposal; no model             | Registry implementation and immutable candidate              | LIVE NOT VERIFIED |
| FR-ML-016 | Promoted models SHALL include documented purpose, dataset, metrics and limitations.            | §F–G model-card proposal            | Approved promotion workflow and evidence                     | LIVE NOT VERIFIED |
| FR-ML-017 | Research models MUST NOT automatically become production decision models.                      | §A, §B, §G architecture requirement | Enforced runtime/governance evidence                         | LIVE NOT VERIFIED |

### J.2 P18 acceptance criteria

| ID         | Canonical criterion                                                | Current evidence / missing artifact                                                 | Status            |
| ---------- | ------------------------------------------------------------------ | ----------------------------------------------------------------------------------- | ----------------- |
| AC-P18-001 | Dataset source/license/version is documented for real benchmark.   | No approved real dataset; a future synthetic exercise cannot satisfy this criterion | LIVE NOT VERIFIED |
| AC-P18-002 | Data schema/quality validation exists.                             | Design only; no validator or approved schema                                        | LIVE NOT VERIFIED |
| AC-P18-003 | Train/validation/test split is explicit and reproducible.          | Design only; no dataset or split manifest                                           | LIVE NOT VERIFIED |
| AC-P18-004 | Preprocessing avoids test leakage.                                 | Proposed controls only; no executed pipeline/test                                   | LIVE NOT VERIFIED |
| AC-P18-005 | At least one classical baseline trains end to end.                 | Training prohibited and no task selected                                            | LIVE NOT VERIFIED |
| AC-P18-006 | Relevant metrics are recorded.                                     | No approved metric plan or experiment                                               | LIVE NOT VERIFIED |
| AC-P18-007 | Calibration is evaluated where appropriate.                        | Applicability and evidence absent                                                   | LIVE NOT VERIFIED |
| AC-P18-008 | Experiment metadata and artifacts are reproducible.                | Contract proposal only; no run/artifact                                             | LIVE NOT VERIFIED |
| AC-P18-009 | Model candidate is registered with status.                         | No registry or candidate                                                            | LIVE NOT VERIFIED |
| AC-P18-010 | Training does not automatically activate patient-facing inference. | Architecture prohibits auto-activation; no live training/inference evidence exists  | LIVE NOT VERIFIED |

### J.3 Dependencies and STOP

P19’s `FR-QML-*` and `AC-P19-*` remain future dependencies only. P4 consent, P5 provenance, P7 fallback, P8/P9 safety restrictions, P10 clinician authority, P11 health-data controls, P15 clinical-content STOP conditions, P20 orchestration, and P22 security/release governance remain in force.

**STOP** before dataset use, training, experiment infrastructure, model registration, inference, pilot, release, or P19 work while any required dataset/task/label/legal/privacy/ethics/custody, accountable model owner, research architecture, split/benchmark, clinical-risk, artifact-security, or release decision is absent. Unknown, unsigned, expired, or disputed evidence is absence, not approval.
