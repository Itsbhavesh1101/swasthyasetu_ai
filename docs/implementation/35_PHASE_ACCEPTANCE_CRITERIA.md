# SwasthyaSetu AI
## 35 — Phase Acceptance Criteria

**Document ID:** `SSAI-ACC-035`  
**Filename:** `35_PHASE_ACCEPTANCE_CRITERIA.md`  
**Status:** P0 / Phase Completion Source of Truth  
**Version:** `1.0.0-draft`  
**Depends on:**
- `00_PROJECT_MASTER_SPEC.md`
- `01_PRODUCT_REQUIREMENTS.md`
- `02_SYSTEM_ARCHITECTURE.md`
- `29_ENGINEERING_STANDARDS.md`
- `34_MASTER_IMPLEMENTATION_PLAN.md`

---

# 1. Purpose

This document defines the minimum evidence required before any SwasthyaSetu implementation phase may be marked `COMPLETE`.

A phase is not complete because:

- files were created;
- the UI looks correct;
- Codex says implementation is done;
- one test passes;
- a demo works once.

A phase is complete only when its mandatory acceptance criteria are verified.

Allowed phase statuses:

```text
NOT STARTED
IN PROGRESS
PARTIAL
BLOCKED
FAILED
COMPLETE
```

---

# 2. Acceptance Status Vocabulary

For individual criteria use:

```text
PASS
FAIL
BLOCKED
NOT APPLICABLE
NOT VERIFIED
```

Rules:

- `FAIL` prevents phase completion.
- `BLOCKED` prevents phase completion unless the criterion is explicitly optional.
- `NOT VERIFIED` prevents phase completion for mandatory criteria.
- `NOT APPLICABLE` requires a short reason.

---

# 3. Global Acceptance Criteria

These apply to every implementation phase where relevant.

## AC-G-001 — Scope

Implementation matches the phase's `IN SCOPE` definition and does not intentionally build unrelated future phases.

## AC-G-002 — Requirements

Implemented behavior maps to documented requirement IDs.

## AC-G-003 — Architecture

Module ownership, dependency direction, adapter boundaries, and data ownership follow `02_SYSTEM_ARCHITECTURE.md`.

## AC-G-004 — Engineering standards

Applicable rules from `29_ENGINEERING_STANDARDS.md` are followed.

## AC-G-005 — Tests

Applicable tests exist and pass.

## AC-G-006 — Types

Backend/frontend type checks pass where relevant.

## AC-G-007 — Lint/format

Configured lint/format checks pass.

## AC-G-008 — Database

Schema changes include reviewed migrations.

## AC-G-009 — Security

No new hard-coded secret, obvious authorization bypass, unsafe upload path, or unhandled sensitive logging is introduced.

## AC-G-010 — Safety

No safety-critical behavior is delegated to unrestricted LLM generation.

## AC-G-011 — Provenance

AI-derived clinical information preserves required provenance/verification state.

## AC-G-012 — Diff audit

Changed files were inspected and unrelated modifications removed.

## AC-G-013 — Documentation

Relevant docs/contracts/progress records are updated.

## AC-G-014 — Honest verification

Commands not run are reported as not verified.

---

# 4. P0 — Documentation and Codex Governance

## AC-P0-001

The following foundation docs exist:

```text
00_PROJECT_MASTER_SPEC.md
01_PRODUCT_REQUIREMENTS.md
02_SYSTEM_ARCHITECTURE.md
03_REPOSITORY_STRUCTURE.md
29_ENGINEERING_STANDARDS.md
34_MASTER_IMPLEMENTATION_PLAN.md
```

## AC-P0-002

The following Codex governance docs exist:

```text
CODEX_INSTRUCTIONS.md
CODEX_WORKFLOW.md
CODEX_CONTEXT_RULES.md
```

## AC-P0-003

The following implementation-control docs exist:

```text
35_PHASE_ACCEPTANCE_CRITERIA.md
36_DEPENDENCY_MAP.md
37_DECISION_LOG.md
38_PROGRESS_TRACKER.md
```

## AC-P0-004

Documentation precedence is defined.

## AC-P0-005

Phase IDs P0–P24 are defined.

## AC-P0-006

Repository structure is defined before coding.

## AC-P0-007

Initial architecture decisions are recorded.

## AC-P0-008

Progress tracker is initialized.

## AC-P0-009

No clinical threshold/remedy/provider data has been invented as production truth.

---

# 5. P1 — Repository and Tooling Foundation

## AC-P1-001

Monorepo structure matches `03_REPOSITORY_STRUCTURE.md`.

## AC-P1-002

Backend Python project installs reproducibly.

## AC-P1-003

FastAPI application starts successfully.

## AC-P1-004

Patient, clinician, and admin frontend projects build successfully.

## AC-P1-005

Strict TypeScript is enabled.

## AC-P1-006

Backend linting is configured and passes.

## AC-P1-007

Backend type checking is configured and passes.

## AC-P1-008

Pytest is configured and passes initial smoke tests.

## AC-P1-009

Frontend lint/type checks pass.

## AC-P1-010

PostgreSQL starts locally through the documented development environment.

## AC-P1-011

CI workflow executes baseline quality gates.

## AC-P1-012

No business/clinical feature is implemented prematurely.

---

# 6. P2 — Shared Platform Kernel

## AC-P2-001

Typed application settings exist.

## AC-P2-002

Stable error envelope exists.

## AC-P2-003

Correlation/request IDs propagate through HTTP flow.

## AC-P2-004

Module registration mechanism exists.

## AC-P2-005

Capability registry or equivalent public capability resolution exists.

## AC-P2-006

Feature-flag abstraction exists.

## AC-P2-007

Risky optional feature defaults are safe/off unless enabled.

## AC-P2-008

Structured logging is enabled without raw request-body logging by default.

## AC-P2-009

Shared kernel contains no feature-specific clinical logic.

---

# 7. P3 — Persistence, Events, Outbox and Jobs

## AC-P3-001

SQLAlchemy 2.x persistence foundation is configured.

## AC-P3-002

Alembic upgrades a clean database to head.

## AC-P3-003

Database session/transaction helpers are tested.

## AC-P3-004

Versioned event envelope exists.

## AC-P3-005

Transactional outbox records events atomically with domain changes.

## AC-P3-006

Outbox dispatcher handles retries/status.

## AC-P3-007

Job-dispatch abstraction exists.

## AC-P3-008

At least one deterministic worker/job smoke test passes.

## AC-P3-009

Object-storage port and test/local adapter exist.

## AC-P3-010

No domain module uses Redis/object storage as sole clinical source of truth.

---

# 8. P4 — Identity, Sessions, Authorization and Consent

## AC-P4-001

Pseudonymous session creation requires no patient name.

## AC-P4-002

Session tokens are non-predictable.

## AC-P4-003

Session expiry is enforced.

## AC-P4-004

Session close/invalid-state behavior is tested.

## AC-P4-005

Base actor context and role model exist.

## AC-P4-006

Backend authorization is enforced for privileged routes.

## AC-P4-007

Consent grant records version/scope/purpose.

## AC-P4-008

Consent revocation is represented and checked.

## AC-P4-009

Referral-specific consent can be represented separately from general product consent.

## AC-P4-010

Cross-subject access tests prevent basic IDOR.

---

# 9. P5 — Patient, Encounter and Provenance Domain

## AC-P5-001

One authoritative patient domain exists.

## AC-P5-002

Encounter lifecycle is explicit and tested.

## AC-P5-003

Medication/allergy/problem/procedure/observation representations exist as typed structures.

## AC-P5-004

Clinically meaningful facts support provenance.

## AC-P5-005

AI-extracted facts support verification state.

## AC-P5-006

Clinician-confirmed fact cannot be silently overwritten by an extracted fact.

## AC-P5-007

Timeline query orders relevant events predictably.

## AC-P5-008

Other modules consume patient context through public interfaces rather than direct table access.

---

# 10. P6 — Patient Web / PWA Foundation

## AC-P6-001

Patient app starts and builds.

## AC-P6-002

Session/consent journey is connected to backend.

## AC-P6-003

Language selection UI exists.

## AC-P6-004

Urgent-help entry point architecture exists on applicable screens.

## AC-P6-005

Keyboard navigation works for core onboarding.

## AC-P6-006

Accessible labels/focus states exist for primary controls.

## AC-P6-007

Sensitive health data is not stored in localStorage by default.

## AC-P6-008

Loading/error/disabled states are implemented.

---

# 11. P7 — Structured Clinical Intake

## AC-P7-001

A patient can start a structured intake without LLM dependency.

## AC-P7-002

Chief complaint is represented.

## AC-P7-003

HPI supports required fields from PRD.

## AC-P7-004

Past medical/surgical/medication/allergy/family/personal history can be represented.

## AC-P7-005

Review of systems and prior investigations can be represented.

## AC-P7-006

Adaptive question selection is deterministic/config-driven.

## AC-P7-007

Known reliable patient history may reduce repeated questioning.

## AC-P7-008

Question-pack registration supports future specialty modules.

## AC-P7-009

AYUSH extension mechanism exists without invented production clinical content.

## AC-P7-010

Completed intake remains a draft, not a diagnosis.

---

# 12. P8 — AI Gateway and Structured Extraction

## AC-P8-001

A provider-neutral AI gateway/port exists.

## AC-P8-002

A deterministic mock adapter supports offline tests.

## AC-P8-003

Task-specific extraction schema exists.

## AC-P8-004

Malformed model output is rejected or safely retried.

## AC-P8-005

Timeout/dependency failure produces typed degraded behavior.

## AC-P8-006

Prompt/model/schema versions are traceable.

## AC-P8-007

Extracted facts preserve provenance.

## AC-P8-008

Unsupported/hallucinated fields do not become trusted clinical facts.

## AC-P8-009

Prompt injection in patient text cannot override system safety authority.

## AC-P8-010

LLM cannot directly return authoritative final triage route.

---

# 13. P9 — Physical Safety Framework

## AC-P9-001

Deterministic safety decision types exist.

## AC-P9-002

Decision returns route, reason codes, policy ID/version, and self-care-block state.

## AC-P9-003

Hard-override precedence is tested.

## AC-P9-004

Predictive/LLM low-risk output cannot downgrade a hard safety route.

## AC-P9-005

Ambiguity/insufficient information can return clarification state.

## AC-P9-006

Missing/invalid policy fails safely.

## AC-P9-007

Synthetic test policy is clearly marked non-production if no approved clinical policy exists.

## AC-P9-008

Self-care cannot bypass safety evaluation.

---

# 14. P10 — Clinician Dashboard and Summary

## AC-P10-001

Authorized clinician can access permitted encounter queue.

## AC-P10-002

Clinician can view structured intake.

## AC-P10-003

Medication/allergy information is prominently accessible.

## AC-P10-004

Draft summary is generated only from structured/source-backed information.

## AC-P10-005

Clinician can confirm, correct, or reject extracted facts.

## AC-P10-006

Corrections preserve history/provenance.

## AC-P10-007

Clinician can inspect source provenance where available.

## AC-P10-008

Patient cannot access clinician-only endpoints.

## AC-P10-009

Dashboard supports future feature panels.

---

# 15. P11 — Document AI / OCR

## AC-P11-001

Supported files can be uploaded securely.

## AC-P11-002

Object-storage metadata is persisted separately from file bytes.

## AC-P11-003

Document state exposes queued/processing/succeeded/failed/review status.

## AC-P11-004

OCR integration uses a port/adapter.

## AC-P11-005

A mock OCR adapter exists for tests.

## AC-P11-006

At least initial document-classification/parser registry exists.

## AC-P11-007

Extracted medical facts retain source-document provenance.

## AC-P11-008

Low-confidence extraction is not clinician-confirmed automatically.

## AC-P11-009

OCR failure does not block manual intake.

## AC-P11-010

Duplicate/identical document handling is addressed.

## AC-P11-011

Source document can be reviewed by authorized clinician.

---

# 16. P12 — Multilingual Speech and Translation

## AC-P12-001

Speech-to-text uses provider abstraction.

## AC-P12-002

Text-to-speech uses provider abstraction if implemented in this phase.

## AC-P12-003

Translation uses provider abstraction if implemented.

## AC-P12-004

English/Hindi configuration exists.

## AC-P12-005

Romanized Hindi/Hinglish fixtures exist where supported.

## AC-P12-006

Original patient wording can be retained alongside normalized text.

## AC-P12-007

ASR failure falls back to text/touch.

## AC-P12-008

Failed transcription is never stored as confirmed clinical fact.

## AC-P12-009

Safety-critical translated copy is not silently generated as authoritative production copy.

---

# 17. P13 — Providers, Resources and Referrals

## AC-P13-001

Provider registry stores source and verification metadata.

## AC-P13-002

Resource registry stores source and verification metadata.

## AC-P13-003

Stale/expired resources are identifiable.

## AC-P13-004

Specialty/service-type routing occurs before individual-provider selection.

## AC-P13-005

LLM-generated provider contact details are impossible through normal registry flow.

## AC-P13-006

Referral requires appropriate explicit consent before external sharing.

## AC-P13-007

Full raw transcript is not included by default.

## AC-P13-008

Referral state machine supports required states.

## AC-P13-009

Duplicate referral side effects are idempotently controlled.

## AC-P13-010

External referral adapter failures produce visible status/fallback.

## AC-P13-011

Synthetic provider records are clearly marked if real verified data is unavailable.

---

# 18. P14 — Mental Health / MannSetu

## AC-P14-001

Pseudonymous mental-health first-contact path works.

## AC-P14-002

AI-assisted/non-therapy/non-diagnostic disclosure is present.

## AC-P14-003

Urgent-help action remains accessible.

## AC-P14-004

Mental-health extractor emits typed signals, not authoritative route.

## AC-P14-005

Independent language-aware safety backstop exists.

## AC-P14-006

Deterministic policy owns A/B/C route.

## AC-P14-007

Explicit high-risk rule cannot be overridden by lower model/questionnaire score.

## AC-P14-008

Ambiguous high-risk language triggers clarification or safer governed behavior.

## AC-P14-009

LLM timeout/invalid JSON still leaves crisis fallback available.

## AC-P14-010

Crisis resources come only from verified registry/bundled fallback.

## AC-P14-011

Route-B referral uses P13 consent/referral flow.

## AC-P14-012

Safety regression corpus includes negation, historical mention, quotes, Hinglish, ambiguity, and prompt-injection cases.

## AC-P14-013

If final approved policy is unavailable, real production triage remains explicitly blocked.

---

# 19. P15 — Self-Care / Ayurveda Framework

## AC-P15-001

Self-care runs only after safety gating.

## AC-P15-002

Knowledge is retrieved from approved/versioned content store.

## AC-P15-003

Unapproved/expired content is not displayed normally.

## AC-P15-004

Contraindication engine exists.

## AC-P15-005

Relevant known allergies can affect eligibility.

## AC-P15-006

Configured medication/chronic-condition exclusions can affect eligibility.

## AC-P15-007

Age/pregnancy constraints are enforceable when defined.

## AC-P15-008

Displayed guidance includes escalation/stop conditions.

## AC-P15-009

LLM cannot introduce a remedy absent from approved knowledge.

## AC-P15-010

Synthetic placeholder knowledge is clearly non-production when approved content is unavailable.

---

# 20. P16 — FHIR

## AC-P16-001

FHIR mapping layer is separate from core domain entities.

## AC-P16-002

Patient mapping exists.

## AC-P16-003

Encounter mapping exists.

## AC-P16-004

Observation mapping exists.

## AC-P16-005

Allergy mapping exists.

## AC-P16-006

Medication-related mapping exists.

## AC-P16-007

DocumentReference/DiagnosticReport mapping exists where applicable.

## AC-P16-008

FHIR validation tests pass.

## AC-P16-009

Imported data retains origin provenance.

## AC-P16-010

Predictive risk output is not silently mapped as confirmed Condition.

---

# 21. P17 — ABDM / ABHA

## AC-P17-001

Approved ABDM integration specification exists before real implementation.

## AC-P17-002

ABDM access occurs through adapter.

## AC-P17-003

Consent-aware exchange is enforced.

## AC-P17-004

Sandbox/mock path exists.

## AC-P17-005

ABDM failure does not destroy valid local clinical data.

## AC-P17-006

Import/export provenance is retained.

## AC-P17-007

Retries/idempotency are tested for supported operations.

---

# 22. P18 — Classical ML

## AC-P18-001

Dataset source/license/version is documented for real benchmark.

## AC-P18-002

Data schema/quality validation exists.

## AC-P18-003

Train/validation/test split is explicit and reproducible.

## AC-P18-004

Preprocessing avoids test leakage.

## AC-P18-005

At least one classical baseline trains end to end.

## AC-P18-006

Relevant metrics are recorded.

## AC-P18-007

Calibration is evaluated where appropriate.

## AC-P18-008

Experiment metadata and artifacts are reproducible.

## AC-P18-009

Model candidate is registered with status.

## AC-P18-010

Training does not automatically activate patient-facing inference.

---

# 23. P19 — Hybrid QML

## AC-P19-001

QML uses the benchmark target/split defined in P18.

## AC-P19-002

Quantum backend abstraction exists.

## AC-P19-003

Simulator execution works.

## AC-P19-004

At least one hybrid QML approach runs end to end.

## AC-P19-005

Encoding/circuit/backend metadata is recorded.

## AC-P19-006

Classical/QML comparison uses comparable metrics.

## AC-P19-007

Generalization results are reported.

## AC-P19-008

No hard-coded quantum-superiority claim exists.

## AC-P19-009

QML failure cannot affect urgent safety route.

---

# 24. P20 — Unified Care Orchestration

## AC-P20-001

One coherent patient journey uses shared longitudinal context.

## AC-P20-002

Care orchestrator combines typed module outputs without becoming a god service.

## AC-P20-003

Physical safety route dominates lower-priority actions.

## AC-P20-004

Mental-health crisis route remains independent of LLM prose.

## AC-P20-005

Self-care is blocked when safety/eligibility requires it.

## AC-P20-006

Provider recommendations come only from verified registry.

## AC-P20-007

ML/QML failure does not block routine intake/navigation.

## AC-P20-008

OCR failure does not block manual intake.

## AC-P20-009

LLM failure produces safe degraded behavior.

## AC-P20-010

RAG, if introduced, is limited to approved retrieval use cases.

---

# 25. P21 — Admin, Governance and Clinical Review

## AC-P21-001

Admin access is role-restricted.

## AC-P21-002

Provider/resource verification workflow exists.

## AC-P21-003

Self-care content approval/version state can be governed.

## AC-P21-004

Active policy/model versions are visible to authorized users.

## AC-P21-005

Audit viewer exists for authorized users.

## AC-P21-006

Clinical review queue exists where required.

## AC-P21-007

Ordinary admins cannot bypass clinical-policy governance.

## AC-P21-008

Raw transcript search is not enabled by default.

---

# 26. P22 — Security, Privacy and Resilience

## AC-P22-001

Threat model exists and reflects current architecture.

## AC-P22-002

Backend authorization/object-level access tests pass.

## AC-P22-003

Secrets are absent from repository.

## AC-P22-004

Sensitive logging review completed.

## AC-P22-005

Upload security controls tested.

## AC-P22-006

Rate limits exist for abuse-prone endpoints.

## AC-P22-007

Retention/purge workflow executes successfully.

## AC-P22-008

Purge failure is observable.

## AC-P22-009

LLM/OCR/provider/integration failure modes are tested.

## AC-P22-010

Kill switches work for defined high-risk optional features.

## AC-P22-011

High/critical security findings are resolved or formally accepted before pilot.

---

# 27. P23 — E2E, Accessibility, Reliability and Performance

## AC-P23-001

Critical patient intake journey passes E2E.

## AC-P23-002

Urgent physical safety journey passes E2E.

## AC-P23-003

Document journey passes E2E.

## AC-P23-004

Provider/referral journey passes E2E.

## AC-P23-005

Mental-health A/B/C configured test journeys pass.

## AC-P23-006

Crisis fallback passes during LLM outage.

## AC-P23-007

Speech failure falls back to text/touch.

## AC-P23-008

Keyboard accessibility audit passes critical flows.

## AC-P23-009

Screen-reader semantics are reviewed for critical flows.

## AC-P23-010

Performance baseline is documented.

## AC-P23-011

Outbox/worker retry/recovery behavior is tested.

## AC-P23-012

No critical observability blind spot remains for core workflows.

---

# 28. P24 — Pilot Readiness

## AC-P24-001

Required clinical policy approvals exist.

## AC-P24-002

Mental-health policy/copy/resource approvals exist where the module will be used.

## AC-P24-003

Self-care knowledge approval exists where the module will be used.

## AC-P24-004

Provider/resource registry is verified and current.

## AC-P24-005

Privacy notice and consent text are approved for pilot context.

## AC-P24-006

Threat model and incident runbook are complete.

## AC-P24-007

Retention/deletion procedures are documented/tested.

## AC-P24-008

Safety evaluation has predefined metrics and results.

## AC-P24-009

Multilingual safety evaluation is complete for enabled languages.

## AC-P24-010

Rollback, policy rollback, model rollback, and resource-disable drills are completed.

## AC-P24-011

Backup/restore process is tested where pilot environment requires it.

## AC-P24-012

Ethics/legal/privacy prerequisites required for human pilot are complete.

## AC-P24-013

Final release decision is recorded as `GO`, `CONDITIONAL GO`, or `NO-GO`.

---

# 29. Phase Completion Record Template

Use this format in progress/release reviews:

```text
Phase:
Status:

Mandatory criteria:
- AC-...: PASS
- AC-...: PASS
- AC-...: BLOCKED — reason

Commands/evidence:
- ...

Known limitations:
- ...

Decision:
COMPLETE | PARTIAL | BLOCKED | FAILED
```

---

# 30. Final Rule

Codex does not decide that a phase is complete by intuition.

Completion is determined against this document and the current approved phase specification.
