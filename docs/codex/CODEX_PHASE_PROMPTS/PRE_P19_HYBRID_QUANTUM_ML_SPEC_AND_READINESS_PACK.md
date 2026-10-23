# SwasthyaSetu AI — Pre-P19 Hybrid Quantum ML Specification and Readiness Pack

**Work unit:** `PRE-P19-HYBRID-QML-GOVERNANCE-READINESS` — **DOCUMENTATION AND ACCOUNTABLE-REVIEW PREPARATION ONLY**.

**Repository:** `Itsbhavesh1101/swasthyasetu_ai`

**Verified starting `main`:** `9ed502ceb4973d6cb95e3a85828699be1cd31ee3`

**Previous PR #48:** MERGED to that SHA. The reviewed head `32b57631bd37ce6f53db1b8098589c45e6304ee6` has a tree-equivalent merge. The next tracker section is **65**.

**Proposed new branch:** `phase/pre-p19-hybrid-qml-spec-readiness`

**As-built baseline:** `docs/19_QUANTUM_ML_SPEC.md` does not exist. The research `ml/quantum/`, `ml/classical/`, `ml/datasets/`, `ml/evaluation/`, `ml/registry/`, and `backend/app/adapters/quantum/` paths are placeholders. P18 Spec 18 and its readiness inventory are **unapproved drafts**; P18-A/B/C/D/E have NOT STARTED, and there is **no approved P18 task, admitted real dataset, frozen split, classical benchmark result, experiment tracker, artifact or model**. P19-A/B/C/D/E and QML runtime are **NOT STARTED**. Do not mistake the presence of research drafts or placeholders for experimental or clinical approval. Current Alembic head `p7a_0007`; Next.js and root `eslint-config-next` remain pinned to `16.4.2`.

> **STOP boundary:** Preparing a design cannot authorize quantum circuits, simulators, dependencies, datasets, training, model inference, external QPU access or clinical use. Quantum advantage, diagnostic performance and superiority must **never be presumed**. Human clinical and research approval, fair P18 comparison evidence and separate security/privacy/release decisions remain absent. Six green CI jobs do not close those gates.

## 0 — Mandatory preflight and source precedence

1. Fetch origin. Verify local `main` and `origin/main` are exactly `9ed502ceb4973d6cb95e3a85828699be1cd31ee3`, PR #48 is merged, its tree matches the reviewed head, and `docs/19_QUANTUM_ML_SPEC.md` is absent. If this is not true, **STOP, report**; do not silently rebase, merge, reset, clean, force-push, overwrite or change this baseline. Use a clean isolated worktree and new branch. Preserve all existing checkouts and untracked files.
2. Read governance before drafting: `docs/codex/{CODEX_INSTRUCTIONS,CODEX_WORKFLOW,CODEX_CONTEXT_RULES}.md`. Read current canonical `docs/{00_PROJECT_MASTER_SPEC,01_PRODUCT_REQUIREMENTS,02_SYSTEM_ARCHITECTURE,03_REPOSITORY_STRUCTURE,04_DOMAIN_MODEL,05_DATABASE_SCHEMA,06_API_CONTRACTS,12_CLINICAL_PROVENANCE_SPEC,18_CLASSICAL_ML_SPEC,26_PRIVACY_CONSENT_SPEC,29_ENGINEERING_STANDARDS,30_TESTING_STRATEGY,33_ERROR_HANDLING_POLICY,34_MASTER_IMPLEMENTATION_PLAN}.md`; `docs/implementation/{35_PHASE_ACCEPTANCE_CRITERIA,36_DEPENDENCY_MAP,37_DECISION_LOG,38_PROGRESS_TRACKER,P18_READINESS_GATE_REVIEW}.md`, and applicable P8/P9/P10/P11/P15/P16/P17 readiness restrictions. Verify path existence before citing and do not cite non-existent project evidence.
3. Review **R3 as the accepted technology/dependency architecture**: `docs/research/r3/{R3_ARCHITECTURE_RECONCILIATION,R3_FINAL_TECHNOLOGY_STACK,R3_CODEX_DEPENDENCY_POLICY}.md`. Inspect prior **research proposals only**, not implementation authority: `docs/research/ai-ml-qml/{AI_ML_QML_TECH_EVALUATION,AI_MODEL_ADAPTER_CONTRACT_DRAFT,MODEL_GOVERNANCE_AND_VALIDATION_PLAN}.md`, and, if offline available/readable, `docs/source_material/sih/SIH26139_HYBRID_QML.pdf` as historical problem context without assuming technical results or current scientific validity. Preserve accepted ADRs, especially **ADR-005** research isolation, **ADR-013** no universal health score, **ADR-017** classical benchmark before QML, **ADR-018** no quantum advantage by default, **ADR-022** no invented clinical policy, **ADR-032** separate research dependencies, **ADR-033** SwasthyaSetu owns model approvals, **ADR-038** dependency boundaries, **ADR-039** trusted hashed artifacts, and **ADR-040** phase activation. Do not alter accepted ADRs.
4. Inspect actual code and empty research directories. Verify no runnable simulator, quantum/backend port, VQC, classical baseline, model registry, real dataset, artifact, experiment tracker, or research deployment exists. Do not adopt the historical R2-E lifecycle or a library's nomenclature over current canonical domain states without a recorded decision.
5. Trace the **exact** current canonical text of `FR-QML-001..018` and `AC-P19-001..009` to the created documentation. Map `FR-ML-001..017` and `AC-P18-001..010` as **unmet prerequisites**, not proof of P19. The master implementation plan lists future P19-A quantum abstraction, P19-B VQC pipeline, P19-C evaluation comparison, P19-D optional QNN or QSVM, and P19-E visualization; none is authorized in this documentation phase.

## 1 — Deliverable A: `docs/19_QUANTUM_ML_SPEC.md` (NEW)

Title **19 — Hybrid Quantum Machine Learning Research and Comparative Benchmark Specification**. Prominently label **DRAFT — PRE-P19 ACCOUNTABLE REVIEW ONLY; NO APPROVED P18 BASELINE, QUANTUM EXPERIMENT, MODEL, CLINICAL USE OR QUANTUM ADVANTAGE CLAIM**. State verified main SHA, date, status, accountable **role** categories (never invented names/signatures), and as-built vs prospective designs. Include the following sections. Write an actionable governance and engineering contract while **not** presenting any executable algorithm, protocol, fixture, dataset, measured result or clinically validated inference.

**A. Research scope and source hierarchy.** P19 is future research for the SIH hybrid QML objective. P18 Spec 18 is only a draft; no benchmark exists. QML is optional to care paths and subordinate to deterministic safety, privacy and clinician authority. Distinguish `/ml/quantum` research tooling from `backend/app/adapters/quantum` placeholder and any future governed `ModelInferencePort`. No QML output may diagnose, confirm a clinical fact or FHIR Condition, direct treatment, override emergency policy, or write to patient records. Research status does not imply model promotion. Note historical source PDFs and R2-E reports are proposals, not verified experiment evidence.

**B. P18 prerequisite gate and parity contract.** Specify immutable linkage to an independently approved and reproducible P18 classical run, named target, positive class, admitted dataset version and permissions, subject/site/time split manifest and locked test set, input and label schemas, consent or other approved research authority, preprocessing assumptions, evaluator version, comparable primary and secondary metrics, resource budget and statistical plan. Explicitly require **same samples, labels and held-out split**. If QML must reduce features to match qubits, fit reduction **only on training data**, report information discarded and original/reduced feature counts, and make the information-budget difference visible. No real P18 baseline means **NO P19 experiment or comparator claim**. Never borrow a published classical score as a substitute for a same-protocol baseline.

**C. Quantum port, backends and trust boundary (conceptual only).** Define future `QuantumBackendPort`, typed experiment request/result envelopes and research-only adapters with a simulator-first policy, keeping framework-specific settings honest. R3 designates **PennyLane primary**, **Qiskit Machine Learning secondary**; neither is installed or activated here. Differentiate analytic/statevector, finite-shot, noisy simulation and optional future hardware because results and resource costs are not automatically interchangeable. No simulator or GPU service started, no external credentials, cloud execution, queue or QPU selected. Hardware use requires a separate approved source, cost, regional/data-egress, cryptographic credential, provider and institutional review.

**D. Bounded hybrid designs, not implementation.** Explain candidate VQC (master-plan primary), with QNN, QSVM or quantum kernel **optional**, subject to task suitability and pre-registered comparison. Discuss encoding/feature map, qubits, ansatz, entanglement, depth, parameterization, optimizer, shots, seeds, noise model and backend metadata as **design axes**. Do not choose actual values or claim expressivity, speedup, clinical utility or superiority. Keep classical preprocessing/optimization outside the quantum execution boundary; distinguish training, inference and circuit execution concepts without introducing code.

**E. Reproducibility and experiment manifest.** Propose immutable experiment ID, approval and manifest refs, P18 baseline run IDs, target and split/data hashes, feature pipeline and reduced dimensionality, framework and dependency-lock hash, code SHA, experiment model and circuit/config revisions, backend and simulator mode, seed/shot settings, transpilation/optimizer details, run attempts and failures, hardware/runtime context, artifact checksums, execution timings and resource accounting. Every experiment points to provenance and source eligibility; no in-place mutation under a reused version. MLflow is **research-only** metadata tooling and is not clinical approval.

**F. Fair evaluation, uncertainty and evidence claims.** Use the P18 frozen evaluation protocol and metrics (e.g., sensitivity, specificity, AUROC/AUPRC, Brier/calibration where applicable); declare training/tuning budgets, model-selection procedure, primary metric and significance/uncertainty interpretation before viewing test outcomes. Require multiple seeds, meaningful variance/confidence estimates, held-out generalization, class/prevalence context, subgroup and shift analysis where ethical/legal authority permits, and negative/degenerate-class handling. Report resource footprint: qubit count, circuit depth, two-qubit gates, parameters, shots, optimizer evaluations, training and inference time, wall time, queue time and cost where applicable, simulator vs hardware distinction. No fabricated numbers, charts, comparisons, speedup, advantage, disease-risk values or false certainty. **ADR-018:** any future narrow performance claim requires bounded reproducible evidence and independent reviewer approval; never hard-code quantum-superiority wording.

**G. Privacy, artifact and model-governance boundaries.** Dataset admission, consent, lawful processing purpose, patient grouping, minimum data, encryption/access/retention, third-party hardware egress, research logs and MLflow security must be independently reviewed. No patient data, identifier, raw feature vector, encoded sensitive data or credential may enter provider jobs, logs or repository. No arbitrary pickle, dill, cloudpickle, joblib or executable model deserialization; artifacts must be trusted, hashed, immutable, access-controlled, and subject to reviewed loader formats and parity evidence. The research lifecycle vocabulary and canonical product `ModelRegistration` states cannot be silently equated; SwasthyaSetu-owned separate human pilot/production decision remains mandatory. No production API, registry promotions, threshold/risk band, intervention, referral or patient-facing predictions.

**H. Patient-safety independence and degraded modes.** QML resource exhaustion, simulator failure, corrupted circuit, missing model, provider unavailability, unauthorized egress, stale benchmark evidence or retrieval errors cannot delay or weaken P7 manual text/touch intake, generic urgent-help navigation, P9 deterministic physical-safety authority or future separately approved mental-health policy. Patient API must not import PennyLane or Qiskit. Research failures are typed, isolated and non-authoritative; core workflows remain operational without the entire research environment.

**I. Negative/adversarial and regression test plan (future, not executed).** Cases must include changed target/split/positive class, unequal test rows, test leakage through feature reduction or optimizer, patient overlap, temporal/site/duplicate leakage, absent source/license/ethics, metric cherry-picking, insufficient seeds, invalid shot settings, broken backend reproducibility, environment/version drift, corrupted circuit or artifact, cost/compute omissions, misleading simulator-vs-hardware labels, unauthorized QPU request, logging-sensitive-features, training tracker promotion, cross-tenant read, unfair error comparisons, unsafe patient/FHIR diagnosis conversion, quantum advantage without comparable evidence, and optional-QML outage affecting urgent safety. Specify reject, abstain or block behaviors conceptually; no approved clinical test oracle or runnable QML test fixture.

**J. Exact traceability and STOP.** Table each `FR-QML-001..018` and `AC-P19-001..009` with **verbatim canonical wording**, draft section, as-built evidence, unmet human/technical decision and status **LIVE NOT VERIFIED**. Map P18 FR/AC prerequisites; explicitly separate future P19-A/B/C/D/E. Distinguish conditional optional requirements (`SHOULD`, `MAY`) rather than upgrading them to `SHALL`. Include accountable owners and a final STOP until approved P18 task/dataset/benchmark, P19 research design, artifact/security, privacy, governance, metric validity and release decisions are separately recorded. No official gate count is created by this draft.

## 2 — Deliverable B: `docs/implementation/P19_READINESS_GATE_REVIEW.md` (NEW)

Create **DRAFT — PROPOSED P19 RESEARCH AND MODEL-GOVERNANCE REVIEW INVENTORY, NOT AN OFFICIAL GATE PROGRAM OR HUMAN SIGNOFF**. Structure **eight descriptive OPEN/BLOCKED review domains**, each naming actual code/repo evidence, accountable **roles** (not names), missing approval and evidence, possible future independently approved artifact, negative tests, fail-closed STOP and whether purely synthetic design could be separately authorized later. The domains:

1. **P18 benchmark admission and owner signoff:** real approved task, dataset/license/ethics, frozen splits, baseline runs, metric oracle and replayable artifacts; P18 remains NOT STARTED and P19 blocked.
2. **QML research purpose, clinical model authority and comparison claims:** intended-use limits, populations, measurement plan, ethics, no diagnosis, no unreviewed superiority statements.
3. **Quantum port, framework and simulator lifecycle:** R3 PennyLane primary / Qiskit ML secondary, `qml-research` isolation, exact versions/licenses, approved local-only execution environment; no backend installed yet.
4. **Encoding, feature reduction and QML model-design review:** qubit/resource budget, training-only reduction, frozen feature schema, VQC primary, optional QNN/QSVM, circuit/reproducibility metadata and test-leakage threats.
5. **Comparable evaluation, uncertainty, efficiency and generalization:** same target/split/metrics as P18; repeated seeds, legitimate claims, comparable compute budget, temporal/subgroup limitations, negative controls.
6. **Dataset security, privacy, artifacts and QPU egress:** no patient data or realistic IDs, secrets, trusted hashed model artifacts, approved storage/retention, third-party region/cost/data-transfer decisions, no unrestricted MLflow.
7. **SwasthyaSetu-owned governance and production isolation:** separate research vs product lifecycle, explicit clinical model approval, calibration/threshold authority, no patient API import, no safety override, no research-driven deployment.
8. **Reproducibility, incident, failure isolation and phased release:** versioned manifests, offline/degraded test evidence, P7/P9 independence, optional hardware only later, incident/rollback and pilot/production approval paths.

Include an **unsigned bounded decision/evidence template**, owner/risk register, FR-QML and AC-P19 exact source crosswalk, P18 dependency and `AC-P19-001` not verified, STOP conditions, and a concise list of prerequisites before a future P19-A prompt. **Do not create any official P19 gate count** or reuse P10/P11 gate arithmetic. Confirm P18 0 actual baselines. Independent human signoff, model governance and research release remain required; a PR approval is not a substitute.

## 3 — Tracker update and strict allowlist

Modify **ONLY** the following **four** documentation files:

```text
docs/19_QUANTUM_ML_SPEC.md
docs/implementation/P19_READINESS_GATE_REVIEW.md
docs/implementation/38_PROGRESS_TRACKER.md
docs/codex/CODEX_PHASE_PROMPTS/PRE_P19_HYBRID_QUANTUM_ML_SPEC_AND_READINESS_PACK.md
```

- In `38_PROGRESS_TRACKER.md`, update ONLY the `Before P18/P19` row for `19_QUANTUM_ML_SPEC.md` from `NOT STARTED` to **DRAFT — P18 CLASSICAL BASELINE, QML BENCHMARK, PRIVACY, SECURITY AND MODEL-GOVERNANCE REVIEW PENDING; NO P19 RUNTIME OR CLINICAL APPROVAL**. Do not change Spec 18 status.
- Append **exactly `# 65. Pre-P19 Hybrid Quantum ML Specification and Readiness Pack`** with baseline and PR #48 tree equivalence, four-file scope, no activated QML, canonical FR/AC mapping, missing P18 benchmark, future phase units and separate human decisions, preserved controls, STOP/next action. Preserve historical section 64 and earlier text, statuses and accepted ADRs unaltered.
- Keep P7 deterministic/manual intake and generic urgent help; P8-C/P9-C Stage 3 **BLOCKED**; P10/P11 live **0/9 approved** (P11 five OPEN/four BLOCKED); P12/P13/P14/P15/P16/P17/P18/P19/P21 runtime **NOT STARTED**; P15 clinical/source STOP; P16/P17 runtime unauthorized; P22 **NOT COMPLETE**. P18 source and dataset decisions remain pending; all P18 and P19 live acceptance criteria remain NOT VERIFIED.
- Maintain Alembic `p7a_0007`, Next.js and root eslint-config-next `16.4.2`, dependency manifests/lockfiles, and existing CI unchanged. The Codex prompt tracked in repo must be an **exact byte-for-byte copy** of this provided file.

**Forbidden this phase:** training, circuits, code, scripts, fixtures, notebooks, datasets or downloads, task selection, experiments, simulator/QPU calls, remote provider credentials, model versions/artifacts, data plots implying measured results, MLflow service, package or dependency changes, lockfiles, backend/front-end modules, Python research implementation, ORM/schema/migrations, API/UI/BFF, feature flags, Docker/CI/infrastructure or security scanner changes, patient data, quantum-hardware requests, clinical/risk thresholds, legal/model approvals, unrelated documentation, or changes to accepted ADRs. **No hidden implementation** and no token/secret in source or documentation. If extra work is needed, STOP and request a separately scoped prompt rather than broadening this PR.

## 4 — Checks, PR and handoff

1. Audit exact `FR-QML-001..018` and `AC-P19-001..009` text against canonical docs and preserve `SHALL`, `SHOULD`, `MAY` semantics. Check each source and link, tracker section 65 uniqueness, exactly four authorized paths, unchanged prior history, `git diff --check`, Prettier Markdown, no medical outcomes/metrics/scores/approval or real dataset, and no edited manifests/lockfiles/Alembic. Verify prompt **byte equivalence**. Run Gitleaks locally against current branch commit range and source files. Do not weaken/suppress scanners; avoid a repetition of the Pre-P15 scanner false positive.
2. Run applicable backend and frontend quality checks and, as feasible, real PostgreSQL and Playwright checks; report actual passes/retries/warnings. Require all **six GitHub CI jobs SUCCESS** on the **exact PR final head SHA**: Backend quality, Frontend quality, Persistence integration, Docker and PostgreSQL, Playwright Chromium, Security scans. CI success is not scientific, privacy, clinical, or quantum superiority validation.
3. One clean isolated worktree, one branch, one clean commit from verified starting main, one PR. Verify final local SHA equals remote branch, PR head and exact CI run SHA. **DO NOT MERGE**. Do not begin P19-A/B/C/D/E, P18 engineering, research environment setup or downstream P20. Return completion report for independent review.

### Required completion report

```text
STATUS: COMPLETE PRE-P19 DOCUMENTATION ONLY / PARTIAL / BLOCKED
BRANCH: phase/pre-p19-hybrid-qml-spec-readiness
BASE MAIN SHA: 9ed502ceb4973d6cb95e3a85828699be1cd31ee3
FINAL LOCAL SHA:
FINAL REMOTE SHA:
PR URL / NUMBER:
SPEC 19 — AS-BUILT, QML RESEARCH ISOLATION, NO PERFORMANCE CLAIMS:
P19 READINESS — EIGHT REVIEW DOMAINS, OWNERS, UNSIGNED DECISIONS:
FR-QML-001..018 / AC-P19-001..009 EXACT TRACEABILITY:
P18 CLASSICAL BENCHMARK, TASK, DATA, SPLIT, AND METRICS MISSING:
PENNYLANE/QISKIT CANDIDATES / BACKEND PORT / SIMULATOR-HARDWARE SEPARATION:
REPRODUCIBILITY, FEATURE REDUCTION, UNCERTAINTY, CLAIMS AND RESOURCE METADATA:
PRIVACY / ARTIFACT TRUST / GOVERNANCE / P7-P9 INDEPENDENCE:
UPSTREAM PHASES AND LIVE ACCEPTANCE NOT VERIFIED:
CHANGED FILES / ALEMBIC / DEPENDENCIES / UNRELATED CHANGES:
LOCAL QUALITY / GITLEAKS / WARNINGS AND RETRIES:
CI RUN ID / EXACT FINAL SHA / SIX JOB CONCLUSIONS:
MERGED: NO
```

**STOP after opening the PR.** The pack provides unapproved architectural and scientific-governance drafts only. No patient-facing QML, clinical prediction, quantum inference, simulator/hardware experiment, model promotion, published performance comparison, pilot or production use is authorized.
