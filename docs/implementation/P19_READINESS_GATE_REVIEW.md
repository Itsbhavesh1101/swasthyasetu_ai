# P19 Readiness Gate Review

> **DRAFT — PROPOSED P19 RESEARCH AND MODEL-GOVERNANCE REVIEW INVENTORY, NOT AN OFFICIAL GATE PROGRAM OR HUMAN SIGNOFF**

**Recorded:** 2026-10-24

**Baseline:** `main` at `9ed502ceb4973d6cb95e3a85828699be1cd31ee3`

**Status:** P18 has zero actual baselines; P18 and P19 runtime are **NOT STARTED**. This document creates no official gate count, approval, or signature.

## 1. P18 benchmark admission and owner signoff — BLOCKED

- **Evidence:** Spec 18 and its readiness inventory are drafts; no approved task, real dataset, split, baseline run, metric oracle, tracker, artifact, or model exists.
- **Roles:** P18 research owner, clinical/epidemiology owner, data custodian, privacy/legal/ethics owner, biostatistics/ML-validation owner, model-governance owner.
- **Missing:** admitted source/license/ethics, target/positive class/population, frozen subject/site/time split, replayable classical runs, metrics and signed ownership.
- **Future artifact:** approved P18 protocol, manifest, run package, model card, validation report, and owner decision.
- **Negative tests:** changed target/split, borrowed score, missing license, leakage, unreplayable artifact.
- **Synthetic option:** later non-medical mechanics cannot satisfy a real baseline.
- **STOP:** no P19 experiment; `AC-P19-001` remains NOT VERIFIED.

## 2. QML purpose, clinical authority, and claims — BLOCKED

- **Evidence:** no intended QML task, population, measurement plan, ethics decision, result, or clinical use exists.
- **Roles:** P19 research owner, clinical/model-governance owner, ethics reviewer, independent validator, institutional owner.
- **Missing:** bounded purpose, prohibited uses, population, measurement and claim language, independent review.
- **Future artifact:** signed research protocol and pre-registered claim/analysis plan.
- **Negative tests:** diagnosis wording, unreviewed superiority, universal score, patient-record/FHIR promotion.
- **Synthetic option:** conceptual envelopes may later be scoped but confer no authority.
- **STOP:** no clinical, performance, advantage, publication, pilot, or production claim.

## 3. Quantum port, framework, and simulator lifecycle — OPEN

- **Evidence:** quantum adapter path is empty; PennyLane/Qiskit ML are absent; no `qml-research` runtime or backend exists.
- **Roles:** architecture, research, security, dependency/license, operations owners.
- **Missing:** port contract, exact versions/licenses, isolated environment, simulator type, lifecycle, bounds, secrets/network policy.
- **Future artifact:** reviewed port/adapter contract, dependency proposal, environment manifest, threat model.
- **Negative tests:** patient API import, unpinned dependency, backend mismatch, unauthorized network/hardware.
- **Synthetic option:** a future local-only fake may be separately authorized.
- **STOP:** no package, simulator, service, credential, queue, cloud, or QPU activation.

## 4. Encoding, feature reduction, and model-design review — BLOCKED

- **Evidence:** no feature schema, qubit budget, encoding, circuit, VQC/QNN/QSVM, optimizer, or training exists.
- **Roles:** P18/P19 research owners, biostatistics/ML-validation, architecture, independent reviewer.
- **Missing:** training-only reduction, information-budget disclosure, frozen schema, VQC suitability, optional-model scope, circuit metadata.
- **Future artifact:** pre-registered design with hashes, leakage review, resource budget, and reproducibility plan.
- **Negative tests:** reduction on test, feature reorder, unreported discarded data, circuit mutation, optional candidate treated as mandatory.
- **Synthetic option:** contract-only design may later be authorized; no runnable fixture now.
- **STOP:** no algorithm/value selection or implementation without the approved P18 protocol.

## 5. Comparable evaluation, uncertainty, efficiency, and generalization — BLOCKED

- **Evidence:** no P18 metric oracle, QML run, score, calibration, interval, generalization, or resource result exists.
- **Roles:** biostatistics/ML-validation, clinical/epidemiology, research, fairness/ethics, independent reviewer.
- **Missing:** identical samples/labels/split, primary metrics, seed plan, uncertainty method, compute budget, negative controls, subgroup/shift authority.
- **Future artifact:** pre-registered comparison and statistical plan followed by independently reviewed results.
- **Negative tests:** cherry-picking, unequal budget, insufficient seeds, degenerate classes, hidden queue/cost, simulator/hardware confusion.
- **Synthetic option:** metric math can later be tested but supplies no scientific evidence.
- **STOP:** no comparative or quantum-advantage conclusion.

## 6. Dataset security, privacy, artifacts, and QPU egress — BLOCKED

- **Evidence:** no admitted data, storage, artifact, provider, QPU, credential, egress path, or MLflow service exists.
- **Roles:** data custodian, privacy/legal/ethics, security, architecture, operations, institutional owner.
- **Missing:** minimization, consent/lawful authority, access/encryption, retention/deletion, trusted formats/hashes, region/provider/cost/egress decision.
- **Future artifact:** data-flow/privacy assessment, artifact trust policy, provider review, incident/deletion runbook.
- **Negative tests:** identifiers or sensitive vectors in jobs/logs, cross-tenant read, malicious serialization, artifact substitution, unauthorized region/QPU.
- **Synthetic option:** only unmistakably non-medical data after separate authorization.
- **STOP:** no patient data, realistic IDs, unrestricted tracker, external transfer, credential, or artifact execution.

## 7. SwasthyaSetu governance and production isolation — BLOCKED

- **Evidence:** canonical model concepts exist only as specifications; no P18/P19 registry, approval, loader, API, or runtime registration exists.
- **Roles:** model-governance, clinical model reviewer, security/privacy, architecture, release owner.
- **Missing:** research/product lifecycle mapping, identity/signature, scope, calibration/threshold authority, expiry, suspension, rollback, release.
- **Future artifact:** lifecycle decision, immutable model card, candidate record, signed approve/reject decision.
- **Negative tests:** MLflow promotion, state aliasing, patient API import, safety override, stale approval, automatic deployment.
- **Synthetic option:** future fake states may test enforcement but cannot approve a model.
- **STOP:** no patient/clinician inference, threshold, risk band, referral, or deployment.

## 8. Reproducibility, incident, failure isolation, and phased release — OPEN

- **Evidence:** normal CI exists but is not quantum/scientific validation; no P19 manifest, incident exercise, rollback, pilot, or hardware plan exists.
- **Roles:** research, quality, security/privacy, operations/incident, model-governance, release, independent reviewer.
- **Missing:** versioned manifests, replay oracle, privacy-safe failures, P7/P9 regression evidence, rollback/withdrawal, pilot/production paths.
- **Future artifact:** reproducibility bundle, failure/incident exercises, phased-release and rollback records.
- **Negative tests:** environment drift, corrupt run, outage affecting P7/P9, secret leakage, failed rollback, CI treated as approval.
- **Synthetic option:** offline failure tests may later be separately scoped.
- **STOP:** optional hardware only after simulator evidence and separate approval; no pilot or production.

## Unsigned bounded decision/evidence template

| Field               | Required content                                                     |
| ------------------- | -------------------------------------------------------------------- |
| Decision ID/version | Immutable ID and revision                                            |
| Domain/scope        | One domain; task, population, dataset, environment, purpose          |
| Evidence            | Immutable sources, hashes, code/run IDs, assessments and tests       |
| Alternatives        | Options and consequences                                             |
| Decision            | Approve, reject, defer, or request evidence; blank is never approval |
| Conditions          | Limits, prohibited uses, monitoring, re-review triggers              |
| Effective/expiry    | Explicit conditions or timestamps                                    |
| Withdrawal/rollback | Suspension, deletion, invalidation, communication                    |
| Accountable roles   | Required functions and segregation                                   |
| Signatures          | **UNSIGNED — future approved identity/signature process required**   |

## Owner and risk register

| Risk                                 | Accountable roles                          | State   | Required evidence               | STOP impact              |
| ------------------------------------ | ------------------------------------------ | ------- | ------------------------------- | ------------------------ |
| P18 baseline absent                  | P18 owner, clinical, data, validation      | BLOCKED | Approved replayable P18 package | No P19                   |
| QML purpose/claim policy absent      | Research, clinical, ethics                 | BLOCKED | Protocol and claim plan         | No comparison claim      |
| Port/framework environment absent    | Architecture, security, dependency owner   | OPEN    | Isolated reviewed design        | No simulator/package     |
| Feature/circuit design absent        | Research, validation                       | BLOCKED | Pre-registered design           | No implementation        |
| Fair evaluation plan absent          | Validation, clinical, independent reviewer | BLOCKED | Frozen statistical plan         | No result interpretation |
| Privacy/artifact/QPU controls absent | Privacy, security, custodian, operations   | BLOCKED | Assessments and trust policy    | No data/egress/artifact  |
| Lifecycle/release mapping absent     | Model governance, clinical, release        | BLOCKED | Signed mapping and decision     | No promotion/inference   |
| Incident/replay evidence absent      | Quality, operations, security              | OPEN    | Exercises and runbook           | No pilot/hardware        |

## Exact FR-QML and AC-P19 crosswalk

| ID         | Verbatim canonical source text                                                                       | Review domain / evidence         | Status            |
| ---------- | ---------------------------------------------------------------------------------------------------- | -------------------------------- | ----------------- |
| FR-QML-001 | The research platform SHALL support hybrid quantum-classical workflows.                              | 2–4; design only                 | LIVE NOT VERIFIED |
| FR-QML-002 | The QML pipeline SHALL support one or more documented feature-encoding strategies.                   | 4; none selected                 | LIVE NOT VERIFIED |
| FR-QML-003 | The platform SHOULD support a Variational Quantum Classifier implementation.                         | 4; prospective                   | LIVE NOT VERIFIED |
| FR-QML-004 | The platform MAY support a Quantum Neural Network implementation.                                    | 4; optional                      | LIVE NOT VERIFIED |
| FR-QML-005 | The platform MAY support a Quantum SVM or quantum-kernel approach.                                   | 4; optional                      | LIVE NOT VERIFIED |
| FR-QML-006 | QML experiments SHALL support simulator execution.                                                   | 3; absent                        | LIVE NOT VERIFIED |
| FR-QML-007 | The design SHOULD permit later near-term quantum-hardware execution through an adapter.              | 3, 6, 8; future only             | LIVE NOT VERIFIED |
| FR-QML-008 | The hybrid pipeline SHALL support classical preprocessing/feature reduction before quantum encoding. | 4; design only                   | LIVE NOT VERIFIED |
| FR-QML-009 | The platform SHALL support reproducible hybrid training.                                             | 8; absent                        | LIVE NOT VERIFIED |
| FR-QML-010 | The platform SHALL support reproducible QML inference.                                               | 3, 8; absent                     | LIVE NOT VERIFIED |
| FR-QML-011 | Classical and QML candidates SHALL be compared on the same evaluation split and target definition.   | 1, 5; P18 absent                 | LIVE NOT VERIFIED |
| FR-QML-012 | The platform SHALL compare predictive performance.                                                   | 5; no results                    | LIVE NOT VERIFIED |
| FR-QML-013 | The platform SHOULD record relevant computational/circuit resource metrics.                          | 5, 8; no run                     | LIVE NOT VERIFIED |
| FR-QML-014 | The platform SHALL compare held-out generalization.                                                  | 5; no results                    | LIVE NOT VERIFIED |
| FR-QML-015 | The platform SHALL expose available explanation/model metadata.                                      | 4–5; no model                    | LIVE NOT VERIFIED |
| FR-QML-016 | Quantum backend, shot count, circuit depth and key experiment configuration SHOULD be recorded.      | 3–5, 8; manifest proposal        | LIVE NOT VERIFIED |
| FR-QML-017 | The product MUST NOT claim quantum advantage unless benchmark evidence supports it.                  | 2, 5, 7; governing prohibition   | LIVE NOT VERIFIED |
| FR-QML-018 | QML output MUST NOT override deterministic urgent-safety policy.                                     | 7–8; governing prohibition       | LIVE NOT VERIFIED |
| AC-P19-001 | QML uses the benchmark target/split defined in P18.                                                  | 1; P18 has zero actual baselines | LIVE NOT VERIFIED |
| AC-P19-002 | Quantum backend abstraction exists.                                                                  | 3; placeholder only              | LIVE NOT VERIFIED |
| AC-P19-003 | Simulator execution works.                                                                           | 3; not installed/executed        | LIVE NOT VERIFIED |
| AC-P19-004 | At least one hybrid QML approach runs end to end.                                                    | 4; none implemented              | LIVE NOT VERIFIED |
| AC-P19-005 | Encoding/circuit/backend metadata is recorded.                                                       | 4, 8; design only                | LIVE NOT VERIFIED |
| AC-P19-006 | Classical/QML comparison uses comparable metrics.                                                    | 1, 5; no results                 | LIVE NOT VERIFIED |
| AC-P19-007 | Generalization results are reported.                                                                 | 5; no results                    | LIVE NOT VERIFIED |
| AC-P19-008 | No hard-coded quantum-superiority claim exists.                                                      | 2, 5, 7; no runtime path         | LIVE NOT VERIFIED |
| AC-P19-009 | QML failure cannot affect urgent safety route.                                                       | 7–8; no runtime test             | LIVE NOT VERIFIED |

All `FR-ML-001..017` and `AC-P18-001..010` remain unmet P19 prerequisites. P19-A/B/C/D/E are separately prompted and not authorized.

## Prerequisites before a future P19-A prompt

1. Independently approve and reproduce one P18 task, dataset, split, evaluator, classical run, artifacts, and ownership package.
2. Record a bounded P19 purpose, parity/statistical plan, claim policy, resource budget, and independent reviewer.
3. Approve the isolated port/framework/simulator architecture, exact dependency/license proposal, and safe local execution boundary.
4. Approve privacy, security, artifact, storage, incident, lifecycle, and research-release decisions.
5. Issue a new narrow prompt. PR approval or green CI is not human model-governance signoff.

**STOP:** no P19-A/B/C/D/E, dependency, simulator, circuit, experiment, dataset access, model, QPU, performance claim, pilot, or production activity until these prerequisites are separately recorded.
