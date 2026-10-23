# 19 — Hybrid Quantum Machine Learning Research and Comparative Benchmark Specification

> **DRAFT — PRE-P19 ACCOUNTABLE REVIEW ONLY; NO APPROVED P18 BASELINE, QUANTUM EXPERIMENT, MODEL, CLINICAL USE OR QUANTUM ADVANTAGE CLAIM**

| Field             | Value                                                                                                                                                                                                                                                                |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Recorded          | 2026-10-24                                                                                                                                                                                                                                                           |
| Verified baseline | `main` at `9ed502ceb4973d6cb95e3a85828699be1cd31ee3`                                                                                                                                                                                                                 |
| Status            | Prospective research architecture and accountable-review preparation only                                                                                                                                                                                            |
| Accountable roles | P18/P19 research owners; clinical/epidemiology owner; biostatistics/ML-validation owner; data custodian; privacy/legal/ethics owner; security owner; architecture owner; model-governance owner; operations/release owner; institutional owner; independent reviewer |
| As built          | Spec 18 and its readiness inventory are unapproved drafts; P18 has zero actual baselines; ML/QML directories contain placeholders only                                                                                                                               |

This draft is governed by the [master specification](00_PROJECT_MASTER_SPEC.md), [system architecture](02_SYSTEM_ARCHITECTURE.md), [classical ML draft](18_CLASSICAL_ML_SPEC.md), [privacy and consent specification](26_PRIVACY_CONSENT_SPEC.md), [accepted decisions](implementation/37_DECISION_LOG.md), and [R3 dependency policy](research/r3/R3_CODEX_DEPENDENCY_POLICY.md). Historical SIH source material and R2-E reports are problem context and proposals, not verified experiments, current scientific validity, or implementation authority.

## A. Research scope and source hierarchy

P19 is future research toward the SIH hybrid-QML objective. P18-A/B/C/D/E have not started: there is no approved task, dataset, split, classical run, evaluator, tracker, artifact, model, or baseline result. Therefore no P19 comparison can begin.

`/ml/quantum` is the prospective isolated research workspace. `backend/app/adapters/quantum` is an empty placeholder, not a port or runtime. Any later product model inference remains behind a separately governed `ModelInferencePort`; research status never promotes a model.

QML is optional to every care path. It cannot diagnose, prescribe, direct treatment, confirm a clinical fact or FHIR Condition, write patient records, choose referral/triage, or override deterministic urgent-safety policy. P7 manual text/touch intake, generic urgent help, P9 deterministic safety, privacy, provenance, and clinician authority remain superior and independent.

## B. P18 prerequisite gate and parity contract

Every future P19 experiment must immutably reference an independently approved, reproducible P18 run with:

- the named target, positive class, intended population, input and label schemas;
- an admitted dataset version/hash, permissions, custody, consent or other approved research authority;
- subject/group/site/time split manifest, identical sample IDs, labels, and locked held-out test set;
- preprocessing assumptions, evaluator version, primary/secondary metrics, statistical plan, and resource budget;
- replayable classical artifacts, code/dependency hashes, reviewer scope, and limitations.

The QML and classical branches must use the **same samples, labels, target definition, and held-out split**. A published score or differently produced result is not a comparator. If qubit limits require feature reduction, it is fitted on training data only; original and reduced dimensions, discarded information, transformation hash, and information-budget difference must be visible. Without a real approved P18 baseline there is **NO P19 EXPERIMENT OR COMPARATOR CLAIM**.

## C. Quantum port, backends, and trust boundary

A future `QuantumBackendPort` may accept a typed, bounded experiment request and return a typed result/error envelope with immutable provenance. Framework-specific configuration stays in research-only adapters. R3 identifies PennyLane as primary and Qiskit Machine Learning as secondary; neither is installed or activated here.

Simulator-first policy must distinguish analytic/statevector, finite-shot, noisy simulation, and optional hardware. Their results, runtime, uncertainty, and costs are not interchangeable. No simulator, GPU service, queue, external provider, credential, cloud execution, or QPU is selected or started.

Hardware use requires a new authorization covering provider/source, exact purpose, region and data egress, credential and cryptographic controls, cost limits, queue behavior, institutional authority, privacy/security review, incident response, and approved non-sensitive payload.

## D. Bounded hybrid designs, not implementation

The master plan treats VQC as the primary candidate. QNN and QSVM/quantum-kernel approaches remain optional `MAY` candidates, not requirements or implied winners. Suitability and a pre-registered comparison determine whether any is studied.

Encoding/feature map, qubit count, ansatz, entanglement, depth, parameterization, optimizer, shots, seeds, noise model, transpilation, and backend are future design axes. No values are chosen here and no expressivity, speedup, utility, accuracy, or superiority is asserted. Classical preprocessing and optimization stay outside the quantum execution boundary. Training, inference, and individual circuit execution are distinct concepts and require separate contracts.

## E. Reproducibility and experiment manifest

A future immutable manifest must bind experiment ID; approval and source-eligibility references; P18 run IDs; task/target, data and split hashes; feature pipeline and reduced dimensionality; code SHA and dependency-lock hash; framework, experiment-model and circuit revisions; backend and simulator mode; seeds/shots; transpilation and optimizer details; attempts/failures; hardware/runtime environment; timings, queue time, resource/cost accounting; and content-addressed artifact checksums.

No identifier is reused for mutated content. Every output traces to eligible inputs and an authorized purpose. MLflow may later record isolated research metadata, but its lifecycle label is not SwasthyaSetu clinical or release approval.

## F. Fair evaluation, uncertainty, and evidence claims

The future comparison uses the frozen P18 protocol and applicable sensitivity, specificity, precision/recall/F1, AUROC/AUPRC, Brier/calibration, uncertainty, subgroup, missingness, and shift analysis. Before test access, reviewers must pre-register training/tuning budgets, selection procedure, primary metric, secondary metrics, confidence/variance method, and claim language.

Multiple seeds, held-out generalization, class/prevalence context, meaningful uncertainty, negative controls, and degenerate-class behavior are required. Resource reports distinguish simulator/hardware and record qubits, circuit depth, two-qubit gates, parameters, shots, optimizer evaluations, training/inference/wall/queue time, and applicable cost.

No number, chart, speedup, advantage, diagnostic performance, disease-risk value, or false certainty is claimed. Under ADR-018, even a narrow future performance statement requires comparable reproducible evidence and independent approval; quantum-superiority wording must never be hard-coded.

## G. Privacy, artifact, and model-governance boundaries

Dataset admission, purpose and lawful authority, subject grouping, minimization, encryption, access, retention/deletion, tracker security, hardware egress, and provider region must be independently approved. No patient data, identifier, raw/encoded sensitive feature, secret, or credential may enter provider jobs, logs, source control, generic metrics, or MLflow.

Artifacts must be trusted, immutable, hashed, access-controlled, schema-bound, and loaded only through reviewed safe formats with parity evidence. Arbitrary pickle, dill, cloudpickle, joblib, executable uploads, floating downloads, and remote code are prohibited.

Historical research lifecycle terms are not silently equivalent to canonical `ModelRegistration` states. SwasthyaSetu requires a separate human decision for any pilot or production use, including task/population scope, calibration/threshold authority, expiry, suspension, and rollback. This draft creates no registry promotion, API, risk band, threshold, intervention, referral, or patient prediction.

## H. Patient-safety independence and degraded modes

Resource exhaustion, simulator or optimizer failure, corrupt circuits/artifacts, missing models, provider outage, unauthorized egress, stale benchmark evidence, and tracker errors fail within research. They cannot delay, downgrade, or remove P7 manual intake, generic urgent help, P9 deterministic safety, or separately approved future mental-health policy.

Patient APIs must not import PennyLane, Qiskit, or QML research dependencies. Typed research failures are non-authoritative, privacy-safe, and isolated; core workflows operate with the complete research environment removed.

## I. Future negative, adversarial, and regression plan

| Condition                                                                  | Conceptual safe behavior                |
| -------------------------------------------------------------------------- | --------------------------------------- |
| Target, split, positive class, labels, or test rows differ from P18        | Reject comparison and claim             |
| Reduction/optimizer fits on test; subject/site/time/duplicate leakage      | Invalidate run before evaluation        |
| Source, license, consent/legal authority, ethics, or custody absent        | Block data use and experiment           |
| Metric cherry-picking, too few seeds, unfair budget, or degenerate classes | Withhold comparative conclusion         |
| Shot/backend settings invalid or environment/version drifts                | Typed failure; run not reproducible     |
| Circuit/artifact corrupt, substituted, unsigned, or executable             | Reject before execution                 |
| Simulator result mislabeled as hardware or cost/compute omitted            | Reject report                           |
| QPU request, egress, credential, tenant, or region unauthorized            | Block without transmitting data         |
| Sensitive feature enters logs/tracker/provider                             | Fail test; quarantine and incident path |
| Research tracker attempts promotion or model writes patient/FHIR diagnosis | Deny and preserve clinical authority    |
| Quantum advantage lacks same-protocol evidence                             | Block claim                             |
| Optional QML outage affects urgent safety or P7                            | Regression failure; retain core route   |

These are proposals, not executed tests or approved clinical oracles. No runnable QML fixture or medical example is created.

## J. Exact traceability and STOP

### J.1 FR-QML-001..018

| ID         | Verbatim canonical wording                                                                           | Draft/evidence                   | Missing decision/artifact                             | Status            |
| ---------- | ---------------------------------------------------------------------------------------------------- | -------------------------------- | ----------------------------------------------------- | ----------------- |
| FR-QML-001 | The research platform SHALL support hybrid quantum-classical workflows.                              | §A–D; placeholders only          | Approved design and implementation                    | LIVE NOT VERIFIED |
| FR-QML-002 | The QML pipeline SHALL support one or more documented feature-encoding strategies.                   | §D design axes                   | Approved encoding and evidence                        | LIVE NOT VERIFIED |
| FR-QML-003 | The platform SHOULD support a Variational Quantum Classifier implementation.                         | §D prospective primary candidate | Suitability decision and implementation               | LIVE NOT VERIFIED |
| FR-QML-004 | The platform MAY support a Quantum Neural Network implementation.                                    | §D explicitly optional           | Separate scope/suitability decision                   | LIVE NOT VERIFIED |
| FR-QML-005 | The platform MAY support a Quantum SVM or quantum-kernel approach.                                   | §D explicitly optional           | Separate scope/suitability decision                   | LIVE NOT VERIFIED |
| FR-QML-006 | QML experiments SHALL support simulator execution.                                                   | §C conceptual only               | Approved simulator environment/evidence               | LIVE NOT VERIFIED |
| FR-QML-007 | The design SHOULD permit later near-term quantum-hardware execution through an adapter.              | §C future adapter boundary       | Provider, egress, security and institutional approval | LIVE NOT VERIFIED |
| FR-QML-008 | The hybrid pipeline SHALL support classical preprocessing/feature reduction before quantum encoding. | §B, §D design                    | Approved pipeline and leakage evidence                | LIVE NOT VERIFIED |
| FR-QML-009 | The platform SHALL support reproducible hybrid training.                                             | §E manifest proposal             | Runtime and replay evidence                           | LIVE NOT VERIFIED |
| FR-QML-010 | The platform SHALL support reproducible QML inference.                                               | §D–E conceptual distinction      | Approved model and inference evidence                 | LIVE NOT VERIFIED |
| FR-QML-011 | Classical and QML candidates SHALL be compared on the same evaluation split and target definition.   | §B parity contract               | Approved P18 run and comparison                       | LIVE NOT VERIFIED |
| FR-QML-012 | The platform SHALL compare predictive performance.                                                   | §F design only                   | Valid same-protocol results                           | LIVE NOT VERIFIED |
| FR-QML-013 | The platform SHOULD record relevant computational/circuit resource metrics.                          | §E–F proposed metadata           | Executed resource evidence                            | LIVE NOT VERIFIED |
| FR-QML-014 | The platform SHALL compare held-out generalization.                                                  | §F design only                   | Locked test evidence                                  | LIVE NOT VERIFIED |
| FR-QML-015 | The platform SHALL expose available explanation/model metadata.                                      | §D–F proposed manifest           | Approved model and validated metadata                 | LIVE NOT VERIFIED |
| FR-QML-016 | Quantum backend, shot count, circuit depth and key experiment configuration SHOULD be recorded.      | §E contract proposal             | Executed immutable manifest                           | LIVE NOT VERIFIED |
| FR-QML-017 | The product MUST NOT claim quantum advantage unless benchmark evidence supports it.                  | §F and ADR-018                   | Runtime/report enforcement and independent review     | LIVE NOT VERIFIED |
| FR-QML-018 | QML output MUST NOT override deterministic urgent-safety policy.                                     | §A, §H architecture              | Isolation regression evidence                         | LIVE NOT VERIFIED |

### J.2 AC-P19-001..009

| ID         | Verbatim canonical wording                          | Current evidence                           | Status            |
| ---------- | --------------------------------------------------- | ------------------------------------------ | ----------------- |
| AC-P19-001 | QML uses the benchmark target/split defined in P18. | P18 has zero actual baselines              | LIVE NOT VERIFIED |
| AC-P19-002 | Quantum backend abstraction exists.                 | Placeholder only                           | LIVE NOT VERIFIED |
| AC-P19-003 | Simulator execution works.                          | No simulator installed or executed         | LIVE NOT VERIFIED |
| AC-P19-004 | At least one hybrid QML approach runs end to end.   | No implementation or experiment            | LIVE NOT VERIFIED |
| AC-P19-005 | Encoding/circuit/backend metadata is recorded.      | Design only                                | LIVE NOT VERIFIED |
| AC-P19-006 | Classical/QML comparison uses comparable metrics.   | No classical or QML result                 | LIVE NOT VERIFIED |
| AC-P19-007 | Generalization results are reported.                | No result                                  | LIVE NOT VERIFIED |
| AC-P19-008 | No hard-coded quantum-superiority claim exists.     | Required boundary; no runtime/report path  | LIVE NOT VERIFIED |
| AC-P19-009 | QML failure cannot affect urgent safety route.      | Required architecture; no QML runtime test | LIVE NOT VERIFIED |

All `FR-ML-001..017` and `AC-P18-001..010` remain unmet prerequisites, not P19 evidence. P19-A quantum abstraction, P19-B VQC pipeline, P19-C evaluation comparison, P19-D optional QNN/QSVM, and P19-E visualization are separate future units and **NOT STARTED**.

**STOP** until accountable owners separately record an approved P18 task, dataset, authority, frozen benchmark, P19 research design, artifact/security and privacy controls, valid comparison/statistical plan, lifecycle mapping, and research/pilot/release decisions. This draft creates no official gate count and authorizes no P18/P19 code, dependency, data, experiment, inference, hardware, performance claim, pilot, or production use.
