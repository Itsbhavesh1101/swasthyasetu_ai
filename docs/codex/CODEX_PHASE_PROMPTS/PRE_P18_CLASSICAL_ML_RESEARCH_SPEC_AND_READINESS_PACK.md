# SwasthyaSetu AI — Pre-P18 Classical ML Research Specification and Readiness Pack

**Work unit:** `PRE-P18-CLASSICAL-ML-RESEARCH-READINESS` — **DOCUMENTATION AND HUMAN DECISION PREPARATION ONLY.** Do not train a model, access or download datasets, choose a disease/benchmark, activate research infrastructure, import a model, or implement patient-facing inference.

- **Repository:** `Itsbhavesh1101/swasthyasetu_ai`
- **Verified `main` baseline:** `0b1eeaf470e129a29f18426ab9a0c4c115fbb4ac`
- **Previous PR #47:** merged to this SHA; reviewed PR head `c5d241c10843af776860d06437fc1ecb09cabc11` is tree-equivalent to merged `main`.
- **Proposed isolated branch:** `phase/pre-p18-classical-ml-research-spec-readiness`
- **Alembic baseline:** `p7a_0007`; Next.js and root eslint-config-next are pinned to `16.4.2`. Do not modify them.
- **Baseline repository truth:** `docs/18_CLASSICAL_ML_SPEC.md` and `docs/19_QUANTUM_ML_SPEC.md` are absent. Top-level `ml/classical/`, `ml/datasets/`, `ml/evaluation/`, `ml/registry/` and `ml/quantum/` contain only foundation placeholders, as does `backend/app/modules/ml/`. No approved research dataset, target/label/population, real benchmark protocol, training pipeline, experiment tracker, registry service, trained artifact, P18 model baseline or P19 QML comparison is implemented. P18 and P19 are **NOT STARTED**.

> **Authority boundary:** A dataset license, model accuracy, research paper, MLflow registry stage, benchmark comparison, or green CI is **never** permission to use a model for patient care. The accepted R3 architecture, clinical provenance, privacy rules and SwasthyaSetu-owned human governance outrank R2-E research proposals. This work must document evidence gaps, not invent research validity, clinical calibration/thresholds, approvals, model performance, or quantum advantage.

## 0. Mandatory preflight and source hierarchy

1. Fetch remote and independently verify `main` and `origin/main` are **exactly** `0b1eeaf470e129a29f18426ab9a0c4c115fbb4ac`, PR #47 is merged, merge tree matches reviewed head, and canonical Spec 18 does not exist. If the baseline has changed, the canonical file exists, or the primary worktree has unrelated changes, **STOP and report**, never silently rebase, overwrite, force push, reset, or clean. Use a **new clean isolated worktree** and preserve primary checkout and all preexisting files.
2. Read Codex governance first: `docs/codex/{CODEX_INSTRUCTIONS,CODEX_WORKFLOW,CODEX_CONTEXT_RULES}.md`. Then authoritative `docs/{00_PROJECT_MASTER_SPEC,01_PRODUCT_REQUIREMENTS,02_SYSTEM_ARCHITECTURE,03_REPOSITORY_STRUCTURE,04_DOMAIN_MODEL,05_DATABASE_SCHEMA,06_API_CONTRACTS,09_MENTAL_HEALTH_POLICY,10_SELF_CARE_AYURVEDA_POLICY,12_CLINICAL_PROVENANCE_SPEC,13_AI_ORCHESTRATION_SPEC,14_LLM_EXTRACTION_SPEC,17_RAG_KNOWLEDGE_SPEC,23_PATIENT_APP_SPEC,26_PRIVACY_CONSENT_SPEC,29_ENGINEERING_STANDARDS,30_TESTING_STRATEGY,33_ERROR_HANDLING_POLICY,34_MASTER_IMPLEMENTATION_PLAN}.md` and `docs/implementation/{35_PHASE_ACCEPTANCE_CRITERIA,36_DEPENDENCY_MAP,37_DECISION_LOG,38_PROGRESS_TRACKER}.md`. Check existence and actual document status before citing.
3. Review research **as historical/evidence proposals, not self-executing implementation authority**: `docs/research/ai-ml-qml/{AI_ML_QML_TECH_EVALUATION,AI_MODEL_ADAPTER_CONTRACT_DRAFT,MODEL_GOVERNANCE_AND_VALIDATION_PLAN}.md`, `docs/research/r3/{R3_ARCHITECTURE_RECONCILIATION,R3_FINAL_TECHNOLOGY_STACK,R3_CODEX_DEPENDENCY_POLICY}.md`, `docs/adr/ADR-005-research-isolation.md`, and current accepted decision-log ADRs, especially **ADR-005, ADR-013, ADR-017, ADR-018, ADR-022, ADR-032, ADR-033, ADR-038, ADR-039, ADR-040**. If a source/ADR path differs, discover actual path rather than fabricate a link. Respect the R3 research-only dependency profile and its prohibition against importing research dependencies in clinical/safety modules.
4. Inspect actual repo layout and relevant modules without editing: `ml/` and child placeholders, `backend/app/modules/ml/`, `backend/app/adapters/quantum/`, backend identity/consent/provenance types, P7 intake, P9 deterministic safety, model-governance placeholders, configuration and dependency profiles. Confirm the absence of approved research data, real experiments, MLflow deployment and patient inference rather than relying only on roadmap tables. Source-of-truth claims must match code.
5. Map exact canonical `FR-ML-001..017` from `01_PRODUCT_REQUIREMENTS.md` and `AC-P18-001..010` from `35_PHASE_ACCEPTANCE_CRITERIA.md`, plus `FR-QML-*`/`AC-P19-*` strictly as future P19 dependencies. P18-A/B/C/D/E from the master plan are **future separately prompted** units. P19 requires a reproducible P18 classical baseline; none exists yet. Do not create a new approved model lifecycle, official gate count or accepted ADR.

## 1. Deliverable A — `docs/18_CLASSICAL_ML_SPEC.md` (NEW)

Title **18 — Classical ML Research and Reproducible Benchmark Specification**. Header must state **DRAFT — PRE-P18 TECHNICAL/HUMAN-REVIEW PREPARATION ONLY; NO DATASET, CLINICAL TASK, REAL TRAINING, VALIDATED MODEL OR LIVE INFERENCE APPROVED**. Record date, exact baseline SHA, current as-built evidence and status, accountable reviewer *roles* (no names/signatures), and limitations. Provide these minimum sections:

**A. Research-only scope and as-built separation.** Define isolated `/ml` research workspace vs future governed backend `ModelInferencePort`, P5 structured context vs consent-limited research inputs, deterministic P9 safety and P7 availability independent of ML failure. P18 supports preparing reproducible classical baseline research for later P19 hybrid-QML comparison. This document does not select a clinical indication, dataset, label, target condition, population, decision threshold, triage route or production claim. Distinguish generic possible synthetic future engineering from actual dataset-based benchmark evidence.

**B. Bounded architecture and data authority.** Proposed future dataset manifest/registry, ingestion validator, split generator, fit/transform preprocessing, feature engineering/selection, experiment runner, metrics/evaluation, research tracker/artifact store, candidate registry and model cards. Respect `ExperimentRun`, `ModelRegistration`, `RiskAssessment` canonical domain meanings, PostgreSQL ownership, no arbitrary clinical writes, no hidden automatic model promotion, research isolation and no new services. Architecture classes/interfaces are *proposals*, not implemented contracts. R3 selects MLflow for **research**, and scikit-learn/other training libraries as task-appropriate, but **no service/package addition, active model, dataset or exact provider/version in this PR**. MLflow state is not governance approval.

**C. Dataset provenance, licensing, ethics and admission gate.** A real benchmark requires explicit reviewer decision on data source/publisher, version/checksum, license and redistribution, intended research purpose, sensitive-data classification, population/site/time coverage, consent/legal basis, subject-level linkage/de-identification, demographics protected features, missingness, label definition and source adjudication, exclusions, retention/deletion and research storage/egress. An open, published or downloaded dataset is not automatically approved. Unknown dataset or license means **NO REAL BENCHMARK**; no speculative source, actual dataset name or clinical labels invented. Dataset acquisition or downloads are prohibited here. Describe **synthetic/offline fixtures only as a separately authorized future P18-A/B possibility**, not a P18 result.

**D. Split, leakage and reproducibility contracts.** Proposed immutable manifest contains dataset ID/version/hash, split IDs or protected hashes, seed, patient/group/site/time partition, train/validation/calibration/test boundaries and locked test set, label/prevalence definition, missingness, positive class, preprocessing estimator versions, code commit, dependency lockfile hash, run config, environment/hardware and artifact/checksum. Fit imputation, normalization, encoding, feature selection, target encoding, balancing and calibration **using only training/approved calibration partitions**. Test-set features/labels or post-outcome facts must never influence fitting or threshold choice. Duplicates/repeated visits, future data, subject overlap and site effects require tests. No actual split algorithm/medical covariates are selected in this draft.

**E. Baseline, evaluation and fairness design.** Propose an appropriate simple baseline (e.g. logistic regression) and justified candidates from master-plan examples (random forest, SVM, XGBoost, MLP), **without claiming all are mandated, trained or superior**. Future evaluation can record sensitivity, specificity, AUROC/AUPRC, precision, F1, confusion matrix, calibration/Brier where appropriate, uncertainty/confidence intervals, subgroup and external/temporal shift evidence, missing-data effects and abstention. Pre-specify primary/secondary metrics only after task and clinical owner review. Avoid fabricated metrics, clinical utility, disease prevalence, cutoffs, diagnostic validity, protected-class inferences or patient-facing thresholds.

**F. Experiment and artifacts contract.** Future run ID, dataset/source and split manifest, code SHA, random seeds, parameters, hardware and dependency profile, transformations, metric code/version, output checksum, errors/failures, reproducibility command and artifact storage. Define confidentiality/isolation for tracking server, logs, feature values and model cards. Artifacts must be source-verified, content-addressed/hashed and loaded via trusted format policies: ONNX only after parity and telemetry review; skops for supported sklearn objects; no untrusted pickle/joblib/dill/cloudpickle execution and no open model upload API. Do not create storage schemas, servers, large artifacts, containers or jobs now.

**G. SwasthyaSetu model-governance and lifecycle mismatch.** Canonical `04_DOMAIN_MODEL.md` uses a short product-facing approval vocabulary, while `MODEL_GOVERNANCE_AND_VALIDATION_PLAN.md` includes a richer research-to-pilot/prod lifecycle. **Do not silently equate or adopt new state values.** Record a decision-required mapping, explicit per-task/population approvals, identity of qualified reviewers, threshold/calibration provenance and expiry, suspension/rollback, protection of historical trials and signatures pending. `EXPERIMENTAL`/technical `RESEARCH_VALIDATED` does not authorize inference. Model output is not a diagnosis, cannot override hard safety, and cannot auto-create confirmed FHIR Condition/Observation. Human clinical model review and independent P22 security/privacy and release decisions are required for real use.

**H. ML/QML benchmark parity boundary.** P19's prospective simulator experiments must reuse an approved P18 task/label/splits/metrics/preprocessing assumptions and include transparent compute-resource limits, uncertainty and held-out generalization; no QML task or benchmark is approved here. No quantum advantage claims. Do not import PennyLane/Qiskit into P18 or into the normal patient dependency closure. Patient intake and urgent-help remain usable without research/QML runtime.

**I. Threat, privacy and negative-test plan.** Future negative tests must include license denied, sensitive input in logs/metrics/artifacts, wrong-subject dataset, data leak from same patient across folds, duplicate/temporal/site leakage, fit on test, test-based tuning/calibration, mislabeled positive class, incomplete manifest, incompatible schema or feature reorder, source/label drift, metrics with degenerate classes, corrupted/unsigned artifact, malicious serialization, unauthorized model activation, cross-tenant access, unapproved data egress/MLflow exposure, regression across model revisions, missing calibration and model-induced safety downgrade. Tests are **proposals, not evidence**; no sample medical output or clinical risk category. Retention and ethical/legal handling remain undecided.

**J. Phase-specific implementation slices and exact traceability.** Map all `FR-ML-001..017`, `AC-P18-001..010` verbatim to draft sections, actual as-built evidence, missing owner/evidence/technical artifact, status **LIVE NOT VERIFIED**. Detail P18-A dataset/experiment registry, P18-B preprocessing/evaluation, P18-C classical baselines, P18-D model registry/cards, P18-E first **approved** benchmark task as **NOT STARTED**. Some safe, synthetic-only work may later be separately permitted; it is not permitted by this document. Map P19 dependencies, P4 consent, P5 provenance, P7 fallback, P8/9 safety, P10 clinician boundaries, P11 health data, P15 clinical-content STOP, P20 orchestration and P22 security. Explicit STOP while dataset/task/legal/model-owner/research architecture/benchmark/clinical risk and release decisions are absent.

## 2. Deliverable B — `docs/implementation/P18_READINESS_GATE_REVIEW.md` (NEW)

Create **DRAFT — PROPOSED RESEARCH AND MODEL-GOVERNANCE REVIEW INVENTORY, NOT APPROVED P18 PHASE OR OFFICIAL GATE COUNT**. For each of eight descriptive review domains include: as-built source/repo evidence, accountable roles only, status OPEN or BLOCKED (descriptive, not official approval arithmetic), missing evidence/decisions, future review artifact, safety/privacy failure tests, synthetic/offline possibilities only if later explicitly scoped, and STOP conditions:

1. **Research use case and clinical/epidemiological authority** — exact target/label, intended population, positive class, clinical relevance, disallowed inference and independent review.
2. **Dataset source/license/privacy/ethics and data custody** — acquisition/redistribution/consent or legal authority, PHI classification, protected populations, retention and disclosure/egress; no data download this phase.
3. **Split and leakage discipline** — patient/site/time partition, holdout freeze, missingness, label adjudication, preprocessing/calibration split and reproducibility oracle.
4. **Classical baselines and evaluation metrics** — task-suitable baselines, imbalance, sensitivity/specificity, AUROC/AUPRC, calibration, subgroup analysis, meaningful confidence intervals, false-negative analysis and clinically qualified metric selection.
5. **Research isolation/dependency/tooling and artifact security** — R3 `ml-research`, optional MLflow/Optuna/SHAP within research only, trusted artifact hashes and safe serialization; no production loader or sidecar activation.
6. **Experiment lineage, model candidate governance and clinical non-authority** — version/owner/reviewer scope, product vs research lifecycle mismatch, model card content, safeguards against registry-triggered deployment and unsafe model statements.
7. **P19 parity and comparative benchmark ownership** — same approved target/split/preprocessing/metrics, simulator scope and no quantum advantage assertion; no QML implementation approval.
8. **Security/privacy/quality/incident/rollout decisions** — data breach, data deletion, research logging, model contamination, runtime isolation, regression/rollback, stakeholder signoffs and separately approved pilot/production release.

Add an **unsigned** bounded decision/evidence template, owner/risk register, and mapping of all `FR-ML-001..017` and `AC-P18-001..010` with every live criterion **NOT VERIFIED**. Note explicit conditional status for `AC-P18-001`: a real benchmark cannot satisfy its dataset-source/license/version evidence without an approved real dataset; a synthetic future exercise does not satisfy that criterion as a real medical benchmark. P18/P19 runtime **NOT STARTED** and no official P18 gate count or human approval exists. P19 is blocked by absent classical baseline and task approvals.

## 3. Changed-path allowlist and tracker

Modify **only these four paths**:

```text
docs/18_CLASSICAL_ML_SPEC.md
docs/implementation/P18_READINESS_GATE_REVIEW.md
docs/implementation/38_PROGRESS_TRACKER.md
docs/codex/CODEX_PHASE_PROMPTS/PRE_P18_CLASSICAL_ML_RESEARCH_SPEC_AND_READINESS_PACK.md
```

- Update `docs/implementation/38_PROGRESS_TRACKER.md` **Before P18/P19** row `18_CLASSICAL_ML_SPEC.md` to **DRAFT — RESEARCH DATASET/TASK, PRIVACY, BENCHMARK AND MODEL-GOVERNANCE REVIEW PENDING; NO P18 RUNTIME OR CLINICAL APPROVAL**. Keep `19_QUANTUM_ML_SPEC.md` NOT STARTED.
- Append exactly **`# 64. Pre-P18 Classical ML Research Specification and Readiness Pack`** with reviewed baseline main SHA, PR #47 merge/tree equivalence, exact deliverables, human decisions, no model/dataset/experiment/training, P18/P19 not started, upstream restrictions, provenance and safe-off, no dependencies or migrations, future separately authorized phases and STOP. Preserve all historic tracker entries; no top-level product stage or accepted-ADR revision.
- Preserve: P7 deterministic/manual intake; P8-C/P9-C Stage 3 **BLOCKED**; P10/P11 live 0/9 approved (P11 5 OPEN/4 BLOCKED); P12/P13/P14/P15/P16/P17/P18/P19/P21 runtime NOT STARTED; P15 clinical/source STOP; P16 FHIR and P17 ABDM not authorized; P22 NOT COMPLETE; Alembic `p7a_0007`; Next.js and eslint-config-next `16.4.2`.

**Prohibited:** model training/fit/inference/metrics outputs, actual patient data/dataset acquisition or dataset downloads, candidate disease/clinical task selection, licensed corpus import, DVC/data artifacts, research package/dependency/lockfile additions, MLflow startup or service, experiment/model store migrations, API/schema/ORM/backend/UI changes, scripts/tests/fixtures, ONNX export, serialization, QML circuits/backends, dashboards, feature flags, clinical thresholds, deployment, logs/artifact with identifiers, arbitrary file/model uploads, proprietary models, new approved role/ADR, unrelated docs, CI/security scanner alterations, Docker/infrastructure, live personal data or clinical approvals. If requirements for later phase turn out to need these, **STOP and request a new narrowly scoped prompt**, never widen this PR.

## 4. Quality, CI, pull request, and handoff

1. Validate all exact FR/AC wording against canonical sources; reconcile draft research proposals vs accepted R3 and current code without inventing facts. Check correct Markdown links/heading 64, exactly FOUR changed paths as listed, byte-identical prompt copy, `git diff --check`, no clinical claims/dataset/model versions/signatures/sensitive examples, no duplicate tracker heading, and no unrelated changes. Confirm Alembic and manifest/lockfile unchanged. Run local Gitleaks against the branch's new clean commit history; avoid scanner false positives without weakening Gitleaks.
2. Run applicable current backend/frontend/local quality checks and report actual test results, retry context and warnings. Require all six CI jobs **SUCCESS on exact final PR head SHA**: Backend quality, Frontend quality, Persistence integration, Docker and PostgreSQL, Playwright Chromium, Security scans. Do not confuse CI success with model/scientific/clinical validation.
3. Commit one clean branch from verified `main`, push and open one PR. Confirm local SHA = remote SHA = PR head SHA = CI SHA. **DO NOT MERGE**. Do not begin P18-A/B/C/D/E or P19 code; return completion report for independent review.

### Required completion report

```text
STATUS: COMPLETE PRE-P18 DOCUMENTATION ONLY / PARTIAL / BLOCKED
BRANCH: phase/pre-p18-classical-ml-research-spec-readiness
BASE MAIN SHA: 0b1eeaf470e129a29f18426ab9a0c4c115fbb4ac
FINAL LOCAL SHA:
FINAL REMOTE SHA:
PR URL / NUMBER:
SPEC 18 — AS-BUILT / RESEARCH VS CLINICAL AUTHORITY:
P18 READINESS — REVIEW DOMAINS, OWNERS, DECISIONS AND STOP:
FR-ML-001..017 / AC-P18-001..010 TRACEABILITY:
DATASET / LICENSE / CLINICAL TASK AND METRICS PENDING:
SPLIT / LEAKAGE / CALIBRATION / EVALUATION DESIGN:
MODEL REGISTRY STATES / APPROVAL / ARTIFACT SECURITY:
R3 ML RESEARCH DEPS / P19 QML COMPARATOR BOUNDARIES:
UPSTREAM GATES / P18 AND P19 NOT STARTED:
CHANGED PATHS / ALEMBIC / DEPENDENCIES / UNRELATED CHANGES:
LOCAL QUALITY / GITLEAKS / WARNINGS AND RETRIES:
CI RUN ID / FINAL SHA / SIX JOB CONCLUSIONS:
MERGED: NO
```

**STOP after opening the PR.** This authorizes research-architecture documents only, not clinical predictions, dataset usage, experiment runs, model artifacts, validation conclusions, P19 QML, research infrastructure, pilot or production model activation.
