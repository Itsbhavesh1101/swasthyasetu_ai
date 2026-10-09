# SwasthyaSetu AI — CODEX_CONTEXT_RULES

**Document ID:** SSAI-CODEX-003  
**Status:** Context and specification precedence  
**Version:** 1.0.0-draft

## 1. Purpose

This document defines what Codex must read for each type of work and how conflicting context is resolved.

The goal is not maximum context. The goal is the smallest authoritative context pack sufficient to implement the task safely.

## 2. Precedence

When documents conflict:

1. approved clinical/safety policy
2. `00_PROJECT_MASTER_SPEC.md`
3. `02_SYSTEM_ARCHITECTURE.md`
4. `01_PRODUCT_REQUIREMENTS.md`
5. security/privacy specifications
6. domain/database/API contracts
7. `29_ENGINEERING_STANDARDS.md`
8. `34_MASTER_IMPLEMENTATION_PLAN.md`
9. phase acceptance criteria
10. current Codex prompt

A current prompt cannot silently override safety or architecture.

## 3. Permanent core context

Before application-code changes read:

- `docs/00_PROJECT_MASTER_SPEC.md`
- `docs/02_SYSTEM_ARCHITECTURE.md`
- `docs/29_ENGINEERING_STANDARDS.md`
- `docs/34_MASTER_IMPLEMENTATION_PLAN.md`
- `docs/codex/CODEX_INSTRUCTIONS.md`
- `docs/codex/CODEX_WORKFLOW.md`

Read relevant sections of `01_PRODUCT_REQUIREMENTS.md` by requirement ID.

## 4. Repository-structure context

Read `docs/03_REPOSITORY_STRUCTURE.md` when:

- adding/moving directories;
- adding modules;
- changing module ownership;
- creating packages;
- extracting services.

## 5. Domain/data/API context

When available, read:

- `04_DOMAIN_MODEL.md` for entity/domain changes;
- `05_DATABASE_SCHEMA.md` for persistence/migrations;
- `06_API_CONTRACTS.md` for API/public-contract changes.

Do not infer API/database shape from frontend code.

## 6. Clinical intake pack

Read:

- `07_CLINICAL_INTAKE_SPEC.md`
- `12_CLINICAL_PROVENANCE_SPEC.md`
- `08_SAFETY_AND_TRIAGE_POLICY.md` when routing/safety is involved.

## 7. Mental-health pack

Read:

- `09_MENTAL_HEALTH_POLICY.md`
- `13_AI_ORCHESTRATION_SPEC.md`
- `14_LLM_EXTRACTION_SPEC.md`
- `26_PRIVACY_CONSENT_SPEC.md`
- `30_TESTING_STRATEGY.md`

## 8. Self-care pack

Read:

- `10_SELF_CARE_AYURVEDA_POLICY.md`
- `08_SAFETY_AND_TRIAGE_POLICY.md`
- `17_RAG_KNOWLEDGE_SPEC.md`
- `26_PRIVACY_CONSENT_SPEC.md`

## 9. AI pack

Read:

- `13_AI_ORCHESTRATION_SPEC.md`
- `14_LLM_EXTRACTION_SPEC.md`
- `30_TESTING_STRATEGY.md`
- `33_ERROR_HANDLING_POLICY.md`

Also read the domain policy owning the task.

## 10. OCR pack

Read:

- `15_DOCUMENT_AI_OCR_SPEC.md`
- `12_CLINICAL_PROVENANCE_SPEC.md`
- `05_DATABASE_SCHEMA.md`
- `06_API_CONTRACTS.md`
- `30_TESTING_STRATEGY.md`

## 11. Speech/language pack

Read:

- `16_MULTILINGUAL_SPEECH_SPEC.md`
- `22_UX_AND_USER_FLOWS.md`
- `30_TESTING_STRATEGY.md`

Add safety policy if language affects a safety-critical flow.

## 12. Provider/referral pack

Read:

- `11_PROVIDER_ROUTING_POLICY.md`
- `26_PRIVACY_CONSENT_SPEC.md`
- `05_DATABASE_SCHEMA.md`
- `06_API_CONTRACTS.md`
- `30_TESTING_STRATEGY.md`

## 13. FHIR pack

Read:

- `20_FHIR_MAPPING_SPEC.md`
- `04_DOMAIN_MODEL.md`
- `05_DATABASE_SCHEMA.md`
- `06_API_CONTRACTS.md`
- `30_TESTING_STRATEGY.md`

## 14. ABDM pack

Read:

- `21_ABDM_INTEGRATION_SPEC.md`
- `20_FHIR_MAPPING_SPEC.md`
- `26_PRIVACY_CONSENT_SPEC.md`
- `27_SECURITY_ARCHITECTURE.md`
- `30_TESTING_STRATEGY.md`

Do not implement ABDM from memory.

## 15. Frontend packs

Patient:

- `22_UX_AND_USER_FLOWS.md`
- `23_PATIENT_APP_SPEC.md`
- `06_API_CONTRACTS.md`

Clinician:

- `24_CLINICIAN_DASHBOARD_SPEC.md`
- `12_CLINICAL_PROVENANCE_SPEC.md`
- `06_API_CONTRACTS.md`

Admin:

- `25_ADMIN_PORTAL_SPEC.md`
- `27_SECURITY_ARCHITECTURE.md`
- `06_API_CONTRACTS.md`

## 16. Security pack

Read:

- `26_PRIVACY_CONSENT_SPEC.md`
- `27_SECURITY_ARCHITECTURE.md`
- `28_THREAT_MODEL.md`
- `30_TESTING_STRATEGY.md`
- `33_ERROR_HANDLING_POLICY.md`

for auth, authorization, uploads, logging, secrets, retention, privacy, and external integrations.

## 17. Classical ML pack

Read:

- `18_CLASSICAL_ML_SPEC.md`
- `30_TESTING_STRATEGY.md`
- selected dataset card/manifest.

## 18. QML pack

Read:

- `19_QUANTUM_ML_SPEC.md`
- `18_CLASSICAL_ML_SPEC.md`
- `30_TESTING_STRATEGY.md`

The classical benchmark definition is mandatory.

## 19. DevOps/observability pack

Read:

- `31_OBSERVABILITY_SPEC.md`
- `32_DEVOPS_DEPLOYMENT.md`
- `27_SECURITY_ARCHITECTURE.md`
- `28_THREAT_MODEL.md`

## 20. Error-handling context

Read `33_ERROR_HANDLING_POLICY.md` when adding public errors, dependency fallbacks, retries, or degraded modes.

## 21. Acceptance context

For every phase/sub-phase read the matching section in `35_PHASE_ACCEPTANCE_CRITERIA.md`. Completion is determined against those criteria, not intuition.

## 22. Dependency context

Read `36_DEPENDENCY_MAP.md` before starting a new phase or adding a feature with significant dependencies.

## 23. Decision context

Read `37_DECISION_LOG.md` and relevant `docs/adr/` records before making architecture decisions. Do not silently reopen accepted decisions.

## 24. Progress context

Read `38_PROGRESS_TRACKER.md` at task start to determine current phase, completed prerequisites, and blockers.

## 25. Context minimization

Do not load irrelevant specifications. A CSS accessibility fix does not need QML context; a QML experiment does not need the provider-referral policy.

## 26. Context expansion

Expand context when:

- the task crosses modules;
- a shared contract changes;
- a safety/privacy implication appears;
- specifications conflict;
- an implementation file explicitly depends on another spec.

## 27. Conflict handling

If same-priority specifications conflict:

1. identify the exact conflict;
2. do not choose silently;
3. report it;
4. propose resolution;
5. block if the impact is material.

## 28. Repository vs specification

Repository = current implementation truth.  
Specification = intended behavior truth.

If they drift, report the drift rather than blindly replacing one with the other.

## 29. Safety authority

Only approved clinical/safety documents may define red flags, mental-health route thresholds, crisis wording, contraindications, medication-conflict policy, and patient-facing self-care content.

General model knowledge is not authoritative.

## 30. Resource/provider authority

Named external resources and providers must come from the verified registry or approved integration, not model memory.

## 31. Research authority

Performance claims must come from actual experiment artifacts and recorded metrics, not expected/theoretical values.

## 32. Missing context

If a referenced document does not yet exist, determine whether safe scaffolding is possible. If real behavior depends on the missing document, return `BLOCKED`.

Missing safety-critical context always blocks real clinical behavior.

## 33. New-feature context

For new features read:

- Master Spec;
- relevant PRD requirements;
- Architecture;
- Repository Structure;
- Engineering Standards;
- Implementation Plan;
- Dependency Map;
- feature proposal/spec;
- applicable safety/privacy/data/API docs.

## 34. Refactor context

For refactors read architecture, module README, public contracts, tests, and relevant ADRs. Do not alter behavior unless explicitly scoped.

## 35. Bug-fix context

For bug fixes inspect the failing behavior, requirement, module spec, existing regression tests, and recent related decisions.

## 36. Final principle

Load exactly the authoritative context needed to make the requested change correctly. Context is a constraint system, not a boilerplate-generation exercise.


---

# R3 Technology Precedence

For dependency and infrastructure selection:

```text
clinical/safety policy
    >
project master specification
    >
system architecture
    >
R3 final technology stack / dependency policy
    >
engineering standards
    >
dependency map
    >
current phase prompt
```

A phase prompt may choose among R3-approved candidates but must not silently override safety or an accepted R3 rejection/defer decision.
