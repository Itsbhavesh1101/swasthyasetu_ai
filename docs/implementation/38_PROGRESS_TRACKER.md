# SwasthyaSetu AI
## 38 — Progress Tracker

**Document ID:** `SSAI-PROG-038`  
**Filename:** `38_PROGRESS_TRACKER.md`  
**Status:** Active Project Tracker  
**Version:** `1.0.0`

---

# 1. Status Vocabulary

Use only:

```text
NOT STARTED
IN PROGRESS
PARTIAL
BLOCKED
FAILED
COMPLETE
```

A phase becomes `COMPLETE` only after the applicable criteria in `35_PHASE_ACCEPTANCE_CRITERIA.md` pass.

---

# 2. Project-Level Status

**Current macro stage:** P11-A/B/C/D, P12-A, P13-A/B/C/D/E, P14-A/B/C/D/F, P15-A/B/E, and P16-A have bounded synthetic engineering foundations only; the related live workflows remain unapproved. P11 is partial while P8, P9, P10, P12, P13, P14, P15, and P16 remain partial.
**Current recommended next action:** Review the bounded synthetic foundations and obtain accountable decisions before any verified source, clinical signal/rule, contact, taxonomy, routing, persistence, API, notification delivery, referral sharing, or patient/admin activation. Do not begin live P11 document processing, P12 providers/voice, P13 delivery/UI activation, P14 mental-health processing/routing, or P21 runtime while applicable decisions remain unresolved. P11 stays 0/9 approved (5 OPEN, 4 BLOCKED), P10 live stays 0/9 approved, and all P8-C/P9-C Stage 3 gates remain blocked.

---

# 3. Phase Tracker

| Phase | Name | Status | Notes |
|---|---|---|---|
| P0 | Documentation + Codex Governance | COMPLETE | Foundation, repository structure, Codex governance, acceptance criteria, dependency map, decision log, progress tracker created. |
| P1 | Repository + Tooling Foundation | COMPLETE | P1-A, P1-B, and P1-C complete; all mandatory P1-C feature-branch CI jobs passed. |
| P2 | Shared Platform Kernel | COMPLETE | P2-A, P2-B, and P2-C complete; all mandatory P2-C feature-branch CI jobs passed. |
| P3 | Persistence + Events + Jobs | COMPLETE | P3-A, P3-B, and P3-C complete; all mandatory P3-C feature-branch CI jobs passed. |
| P4 | Identity + Sessions + Consent | COMPLETE | P4-A, P4-B, and P4-C complete; all mandatory P4-C feature-branch CI jobs passed. |
| P5 | Patient + Encounter + Provenance | COMPLETE | P5-A, P5-B, and P5-C complete; AC-P5-001..008 pass. |
| P6 | Patient Web Foundation | COMPLETE | P6-A, P6-B, and P6-C complete; AC-P6-001..008 pass and all mandatory P6-C feature-branch CI jobs passed. |
| P7 | Structured Clinical Intake | COMPLETE | P7-A/P7-B/P7-C complete; PR #21 merged at `926f27a5bda456b616061617dfaf1519e302b9d4`. Production clinical content remains governance-deferred. |
| P8 | AI Gateway + Structured Extraction | PARTIAL | P8-A/P8-B are merged. P8-C Stage 2 synthetic integration evidence is implemented; patient-facing Stage 3 remains blocked by explicit governance gates. |
| P9 | Physical Safety Framework | PARTIAL | P9-A/P9-B and P9-C Stage 2 are merged. P9-C provides detached synthetic presentation and fail-closed degraded-state evidence only; real policy activation, API/persistence and patient routing remain approval-blocked. |
| P10 | Clinician Dashboard + Summary | PARTIAL | P10-A safe engineering domain/test subset merged in PR #30. P10-B, sensitive P10-C and P10-D remain blocked; no live clinician workflow is authorized. |
| P11 | Document AI / OCR | PARTIAL | P11-A/B/C and P11-D are merged through PR #35 at `f71662322b27ec79004745ec6217283887700ac8`; reviewed P11-D head `963f5e11eccec4d1ef7a80386ae49f61833bc28e` is tree-equivalent. Pre-P11-E is documentation-only; its P11-A approval-readiness package is prepared with every human decision pending. No upload, storage, live document workflow, medical extraction, executable processor, OCR provider or P11-E UI is approved. |
| P12 | Multilingual Speech / Translation | PARTIAL | P12-A synthetic contract/port/metadata/mock foundation implemented; no runtime registration, provider/model, audio, API/UI, persistence, clinical use or live approval. P12-B/C/D and all live AC-P12 criteria remain blocked/not verified. |
| P13 | Providers + Resources + Referrals | PARTIAL | P13-A/B/C/D/E provide strict engineering-synthetic directory, symbolic match/abstention, detached referral lifecycle/idempotency, content-free simulated notification failure, and test-only unavailable/degraded/source-warning presentation evidence. No verified source, contact, clinical taxonomy, provider query/ranking, live consent/sharing, delivery, persistence, API, adapter or UI/runtime activation exists; all live AC-P13 criteria remain unverified. |
| P14 | Mental Health / MannSetu | PARTIAL | P14-A/B/C/D/F provide detached content-free signal, safety-backstop, toy policy-routing, test-only presentation, and offline adversarial composition evidence using fixed nonmedical symbols. Protected environments are denied and no presentation is routed. P14-E remains blocked. No conversation, patient data, clinical signal/lexicon/policy/route, production adapter, resource, referral, API, persistence, live UI or runtime activation exists; all live AC-P14 criteria remain unverified. |
| P15 | Self-Care / Ayurveda | PARTIAL | P15-A/B/E provide detached engineering-only knowledge-pack contracts, strict parsing, a fail-closed toy eligibility-state evaluator, and an offline P9-to-P15 safety regression harness using closed nonmedical tokens. No remedy/advice, real source, clinical eligibility/exclusion, approved retrieval, patient context, persistence, API, UI or runtime activation exists; all live AC-P15 criteria remain unverified. |
| P16 | FHIR | PARTIAL | P16-A provides detached engineering-only R4 mapping metadata contracts and symbolic projection/import-candidate mechanics. No clinical field crosswalk, real patient data, profile/schema validation, terminology, authorization, consent evaluation, persistence, API, adapter, transport, HAPI sidecar, ABDM behavior or runtime activation exists; all live AC-P16 criteria remain unverified. |
| P17 | ABDM / ABHA | NOT STARTED | Requires current ABDM integration spec. |
| P18 | Classical ML | NOT STARTED | Dataset/task selection pending. |
| P19 | Hybrid QML | NOT STARTED | Depends on P18 baseline. |
| P20 | Unified Care Orchestration | NOT STARTED | PRE-P20 DRAFT DOCUMENTATION, P20 RUNTIME NOT STARTED AND LIVE AC NOT VERIFIED. |
| P21 | Admin + Governance + Review | NOT STARTED | Spec 25 exists as unapproved Pre-P13/P21 draft; Pre-P21 decision reconciliation prepared; P21-A/B/C/D runtime NOT STARTED and live acceptance NOT VERIFIED; accountable decisions pending. |
| P22 | Security + Privacy + Resilience | PARTIAL | P22-A audit evidence, bounded P22-B controls, and synthetic P22-C/P22-D foundations are delivered. Headers, origin enforcement, process-local abuse controls, provider-neutral purge/restore mechanics, safe-off optional dependency switches, bounded execution and privacy-safe telemetry are implemented; real retention execution, edge/upload controls, distributed resilience and independent live acceptance remain outstanding. AC-P22-001..011 remain LIVE NOT VERIFIED. |
| P23 | E2E + Accessibility + Performance | NOT STARTED | Pre-P23 bounded coverage/gap review and unsigned readiness inventory drafted; P23-A/B/C/D NOT STARTED, AC-P23-001..012 LIVE NOT VERIFIED, upstream/human approvals pending. |
| P24 | Pilot Readiness | NOT STARTED | Pre-P24 unapproved evidence and unsigned owner docket drafted; conditional scope undecided, AC-P24-001..013 LIVE NOT VERIFIED, human pilot prohibited and formal release decision NOT RECORDED. |

---

# 4. P0 Deliverables

| Deliverable | Status |
|---|---|
| `00_PROJECT_MASTER_SPEC.md` | COMPLETE |
| `01_PRODUCT_REQUIREMENTS.md` | COMPLETE |
| `02_SYSTEM_ARCHITECTURE.md` | COMPLETE |
| `03_REPOSITORY_STRUCTURE.md` | COMPLETE |
| `29_ENGINEERING_STANDARDS.md` | COMPLETE |
| `34_MASTER_IMPLEMENTATION_PLAN.md` | COMPLETE |
| `CODEX_INSTRUCTIONS.md` | COMPLETE |
| `CODEX_WORKFLOW.md` | COMPLETE |
| `CODEX_CONTEXT_RULES.md` | COMPLETE |
| `35_PHASE_ACCEPTANCE_CRITERIA.md` | COMPLETE |
| `36_DEPENDENCY_MAP.md` | COMPLETE |
| `37_DECISION_LOG.md` | COMPLETE |
| `38_PROGRESS_TRACKER.md` | COMPLETE |

---

# 5. Pre-P1 Specification Queue

These documents should be created before their dependent coding phases.

## Highest priority before meaningful domain implementation

| Document | Status | Needed before |
|---|---|---|
| `04_DOMAIN_MODEL.md` | COMPLETE | P4/P5 |
| `05_DATABASE_SCHEMA.md` | COMPLETE | P4/P5 |
| `06_API_CONTRACTS.md` | COMPLETE | P4+ |

## Before P7

| Document | Status |
|---|---|
| `07_CLINICAL_INTAKE_SPEC.md` | COMPLETE |
| `22_UX_AND_USER_FLOWS.md` | COMPLETE |
| `23_PATIENT_APP_SPEC.md` | COMPLETE |

## Before P8

| Document | Status |
|---|---|
| `13_AI_ORCHESTRATION_SPEC.md` | COMPLETE — SUBJECT TO USER REVIEW |
| `14_LLM_EXTRACTION_SPEC.md` | COMPLETE — SUBJECT TO USER REVIEW |
| `26_PRIVACY_CONSENT_SPEC.md` | COMPLETE — SUBJECT TO USER REVIEW |
| `30_TESTING_STRATEGY.md` | COMPLETE — SUBJECT TO USER REVIEW |
| `33_ERROR_HANDLING_POLICY.md` | COMPLETE — SUBJECT TO USER REVIEW |

## Before P9

| Document | Status |
|---|---|
| `08_SAFETY_AND_TRIAGE_POLICY.md` | DRAFT — NOT CLINICALLY APPROVED / real clinical rules NOT STARTED |

## Before P10

| Document | Status |
|---|---|
| `12_CLINICAL_PROVENANCE_SPEC.md` | COMPLETE — SPECIFICATION COMPLETED, SUBJECT TO REVIEW; not clinical approval or implementation |
| `24_CLINICIAN_DASHBOARD_SPEC.md` | COMPLETE — SPECIFICATION COMPLETED, SUBJECT TO REVIEW; not production access approval or implementation |

## Before P11

| Document | Status |
|---|---|
| `15_DOCUMENT_AI_OCR_SPEC.md` | COMPLETE — SPECIFICATION WRITTEN, SUBJECT TO INDEPENDENT REVIEW; not clinical, privacy, production, provider, upload, retention or implementation approval |

## Before P12

| Document | Status |
|---|---|
| `16_MULTILINGUAL_SPEECH_SPEC.md` | DRAFT PRE-P12 SPECIFICATION — SUBJECT TO INDEPENDENT/HUMAN REVIEW; NOT IMPLEMENTED OR APPROVED |

## Before P13

| Document | Status |
|---|---|
| `11_PROVIDER_ROUTING_POLICY.md` | DRAFT — HUMAN REVIEW REQUIRED, NO LIVE P13 APPROVAL |
| `25_ADMIN_PORTAL_SPEC.md` | DRAFT — PRE-P13/P21 GOVERNANCE REVIEW PENDING; NO LIVE ADMIN IMPLEMENTATION/APPROVAL |

## Before P14

| Document | Status |
|---|---|
| `09_MENTAL_HEALTH_POLICY.md` | PRE-P14 DRAFT — CLINICAL POLICY/SAFETY/PRIVACY REVIEW PENDING; NO ACTUAL CLINICAL RULES OR RUNTIME APPROVAL |
| `13_AI_ORCHESTRATION_SPEC.md` | COMPLETE — SUBJECT TO USER REVIEW |
| `14_LLM_EXTRACTION_SPEC.md` | COMPLETE — SUBJECT TO USER REVIEW |

## Before P15

| Document | Status |
|---|---|
| `10_SELF_CARE_AYURVEDA_POLICY.md` | DRAFT — ACCOUNTABLE CLINICAL/SOURCE/PRIVACY/ARCHITECTURE REVIEW PENDING; NO P15 RUNTIME APPROVAL |
| `17_RAG_KNOWLEDGE_SPEC.md` | DRAFT — ACCOUNTABLE CLINICAL/SOURCE/PRIVACY/ARCHITECTURE REVIEW PENDING; NO P15 RUNTIME APPROVAL |

## Before P16/P17

| Document | Status |
|---|---|
| `20_FHIR_MAPPING_SPEC.md` | DRAFT — ACCOUNTABLE ARCHITECTURE, CLINICAL, PRIVACY, SECURITY AND INTEROPERABILITY REVIEW PENDING; NO LIVE P16 APPROVAL |
| `21_ABDM_INTEGRATION_SPEC.md` | DRAFT — OFFICIAL ABDM/ABHA, ARCHITECTURE, IDENTITY, CLINICAL, PRIVACY, SECURITY, PARTNER AND LEGAL REVIEW PENDING; NO LIVE P17 APPROVAL |

## Before P18/P19

| Document | Status |
|---|---|
| `18_CLASSICAL_ML_SPEC.md` | DRAFT — RESEARCH DATASET/TASK, PRIVACY, BENCHMARK AND MODEL-GOVERNANCE REVIEW PENDING; NO P18 RUNTIME OR CLINICAL APPROVAL |
| `19_QUANTUM_ML_SPEC.md` | DRAFT — P18 CLASSICAL BASELINE, QML BENCHMARK, PRIVACY, SECURITY AND MODEL-GOVERNANCE REVIEW PENDING; NO P19 RUNTIME OR CLINICAL APPROVAL |

## Before hardening

| Document | Status |
|---|---|
| `26_PRIVACY_CONSENT_SPEC.md` | COMPLETE — SUBJECT TO USER REVIEW |
| `27_SECURITY_ARCHITECTURE.md` | P11-FOCUSED DRAFT — PLATFORM-WIDE COVERAGE AND HUMAN REVIEW PENDING |
| `28_THREAT_MODEL.md` | P11-FOCUSED DRAFT — PLATFORM-WIDE COVERAGE AND HUMAN REVIEW PENDING |
| `30_TESTING_STRATEGY.md` | COMPLETE — SUBJECT TO USER REVIEW |
| `31_OBSERVABILITY_SPEC.md` | NOT STARTED |
| `32_DEVOPS_DEPLOYMENT.md` | NOT STARTED |
| `33_ERROR_HANDLING_POLICY.md` | COMPLETE — SUBJECT TO USER REVIEW |

---

# 6. Current Known External Decisions Still Open

These are not implementation failures; they are intentionally unresolved.

| Decision | Status |
|---|---|
| final cloud provider | OPEN |
| final production auth provider | OPEN |
| final production LLM provider | OPEN |
| final ASR/TTS provider per language | OPEN |
| final provider-directory source | OPEN |
| final approved self-care/Ayurveda knowledge source | OPEN |
| final ML/QML disease benchmark dataset/task | OPEN |
| final production ABDM flows | OPEN |
| final clinical red-flag policy | CLINICAL APPROVAL REQUIRED |
| final mental-health route policy/copy | CLINICAL APPROVAL REQUIRED |
| final multi-tenancy approach | DEFERRED |

---

# 7. Blocker Register

No current blocker prevents P1 repository/tooling work.

Future clinical/product blockers are expected and must not be bypassed by Codex.

---

# 8. Update Template

When a sub-phase runs, add/update:

```text
Phase/Sub-phase:
Status:
Branch:
Commit:
Requirement IDs:
Commands run:
Tests:
Blockers:
Notes:
```

---

# 9. Completion Rule

Do not manually mark a phase `COMPLETE` unless its mandatory criteria in `35_PHASE_ACCEPTANCE_CRITERIA.md` have been evaluated and passed.


---

# R3 Research / Architecture Reconciliation

| Work item | Status |
|---|---|
| R2-A OCR research | COMPLETE |
| R2-B Indian language/speech research | COMPLETE |
| R2-C FHIR/interoperability research | COMPLETE |
| R2-D infrastructure/security research | COMPLETE |
| R2-E AI/ML/QML research | COMPLETE |
| R3 final technology matrix | COMPLETE |
| R3 architecture reconciliation | COMPLETE |
| R3 final dependency map | COMPLETE |
| R3 Codex dependency policy | COMPLETE |
| Provider-specific OCR benchmark | NOT RUN |
| Provider-specific ASR/TTS benchmark | NOT RUN |
| Keycloak identity spike | NOT RUN |
| Procrastinate durable-job spike | NOT RUN |
| SeaweedFS object-storage spike | NOT RUN |
| Embedding multilingual benchmark | NOT RUN |

## R3 implementation consequence

Foundation implementation may proceed using core dependencies and fake/local adapters.

Benchmark-gated or phase-gated infrastructure must not be pulled forward merely because R3 documents it.

---

# 10. P1-A Completion Record

```text
Phase/Sub-phase: P1-A — Repository + Backend Tooling
Status: COMPLETE
Date: 2026-10-10
Branch: unavailable — repository directory has no .git metadata
Commit: none
Requirement IDs: FR-CORE-003, FR-CORE-005, FR-CORE-006, FR-EXT-002, FR-EXT-012, NFR-MAINT-001, NFR-MAINT-003, NFR-MAINT-005, NFR-MAINT-007, NFR-MAINT-008, NFR-TEST-001, NFR-TEST-004, NFR-SEC-005, NFR-SEC-014, PRIV-007
Implemented scope: locked Python 3.12+/FastAPI project; application factory; typed settings; /health/live and /health/ready; /api/v1 router composition; canonical error envelope; opaque request IDs; privacy-safe JSON logging; backend lint, format, type, test and smoke tooling; backend developer documentation.
Verification commands: uv lock --check; uv sync --locked --dev; ruff check; ruff format --check; mypy; pytest; compileall; import smoke; live Uvicorn health probe.
Tests: 17 passed.
Remaining P1 subunits: P1-B frontend workspaces + shared tooling; P1-C Docker/CI + quality-gate scripts.
Blockers: none for P1-A. Git-native diff/status verification is unavailable until .git metadata exists.
Open decisions: none required for P1-A.
```

## P1-A provenance clarification

The historical P1-A execution record above remains unchanged: `.git` metadata was unavailable during
that execution. After P1-A completed, the repository was initialized and pushed with this baseline:

```text
Branch: main
Commit: 1d299b7f4e7f95d634e5e4745b2d020b69a87b01
```

This note clarifies later repository provenance and does not change the P1-A status or original
execution record.

---

# 11. P1-B Completion Record

```text
Phase/Sub-phase: P1-B — Frontend Workspaces + Shared Frontend Tooling
Status: COMPLETE
Date: 2026-10-10
Branch: phase/p1-b-frontend-foundation
Base commit: 1d299b7f4e7f95d634e5e4745b2d020b69a87b01
Implementation commit: 283a40480bfe9d8bd8fc8376543119b0f6decfbf
Requirement IDs: NFR-ACCESS-001, NFR-ACCESS-002, NFR-ACCESS-003, NFR-ACCESS-004, NFR-MAINT-002, NFR-MAINT-007, NFR-MAINT-008, NFR-SEC-005, NFR-TEST-001, NFR-UX-008
Implemented scope: pnpm workspace; patient, clinician, and admin Next.js App Router applications; strict TypeScript; Tailwind CSS; shared UI package with accessible application shell and loading/error/empty states; Vitest/Testing Library unit tests; Playwright smoke-test skeleton; frontend developer documentation.
Verification commands: pnpm install --frozen-lockfile; pnpm frontend:format-check; pnpm frontend:lint; pnpm frontend:typecheck; pnpm frontend:test; pnpm frontend:build; pnpm e2e:list; backend uv lock --check, Ruff lint/format, mypy, and pytest; git diff --check.
Tests/builds: 5 frontend unit tests passed; patient, clinician, and admin production builds passed; 3 Playwright smoke tests discovered; 17 backend regression tests passed.
Remaining P1 criteria: AC-P1-010 local PostgreSQL and AC-P1-011 CI workflow remain assigned to P1-C.
Blockers: none for P1-B. Full Playwright browser execution is deferred to the browser-enabled P1-C/CI environment; configuration and discovery passed.
Open decisions: none required for P1-B.
```

---

# 12. P1-C Completion Record

```text
Phase/Sub-phase: P1-C — Docker / Local PostgreSQL / CI / Quality-Gate Foundation
Status: COMPLETE
Date: 2026-10-10
Branch: phase/p1-c-docker-ci-foundation
Base commit: d79a9a9dd9a82764380c9706801d8a3f59de03ea
Implementation commit: de3bd98ae9e859553efb368fcb8c3e544c5ae8a2
Requirement IDs: AC-P1-001 through AC-P1-012; AC-G-001 through AC-G-014 as applicable.
Implemented scope: pinned non-root backend image; two-service local Compose foundation; PostgreSQL 16.12 health and query verification; Node 24 alignment; cross-platform backend/frontend quality gate; GitHub Actions jobs for backend, frontend, Docker/PostgreSQL, Playwright, Gitleaks, and Trivy.
Local verification: COMPLETE — Compose configuration, PostgreSQL health/pg_isready/SELECT 1, backend build/startup/health, combined quality gate, Chromium smoke tests, Gitleaks, and Trivy filesystem/image gates passed. Generated containers, database volume, scanner cache, and scan tar were removed.
Acceptance evaluation: AC-P1-001 through AC-P1-012 COMPLETE.
Remote CI: VERIFIED — GitHub Actions run 38041815538 on branch commit 9285aaa03165a5c978fe25ea84ea12f4b56414a8 passed Backend quality, Frontend quality, Docker and PostgreSQL, Playwright Chromium, and Security scans.
CI URL: https://github.com/Itsbhavesh1101/swasthyasetu_ai/actions/runs/38041815538
Overall P1 status: COMPLETE
Blockers: none.
Open decisions: none required for P1-C.
```

## Post-review Docker reproducibility remediation

Review fix `SSAI-P1C-REVIEW-FIX-01` removed mutable `apk upgrade` operations from both backend image
stages. The superseding official Python base is
`python:3.12.15-alpine3.23@sha256:1fd55c2f838c4f76262f9eeed899ff9168ea96ac383c61667d6f204325e1f169`;
the corrected image and CI security gate passed without vulnerability ignores. GitHub Actions run
`38043640160` verified all five mandatory jobs on correction commit
`bf03a1a1de34860c64a6f3162e78d13d41371a75`.

---

# 13. P2-A Implementation Record

```text
Phase/Sub-phase: P2-A — Shared Kernel Types, Errors & Configuration
Status: COMPLETE
Date: 2026-10-10
Branch: phase/p2-a-shared-kernel-primitives
Base commit: a531305c4693e2acd7dc92d58bab1b0c3e0178b5
Implementation commit: 2f06be4620e2126196f255829d8fe03f7f2c66aa
Requirement IDs: FR-CORE-004, FR-CORE-005, FR-CORE-006, FR-CORE-009, FR-CORE-010, FR-EXT-003, FR-EXT-004, FR-EXT-005, FR-EXT-011, NFR-OBS-011, PRIV-007
Acceptance criteria: AC-P2-001, AC-P2-002, AC-P2-003, AC-P2-008, and AC-P2-009 pass locally; AC-P2-004 through AC-P2-007 remain assigned to P2-B/P2-C.
Implemented scope: opaque UUID identifiers; timezone-aware UTC helper; safe request-ID primitive; immutable identity-neutral actor context; framework-independent error hierarchy and complete canonical error-code registry; explicit FastAPI status translation and unchanged public error envelope; frozen typed settings sections with P1 environment compatibility and inactive future integrations; privacy-safe logging regression coverage.
Verification: 38 backend tests passed; backend and frontend quality gates passed, including locked dependency checks, Ruff, format, mypy, compile/import smoke, frontend lint/typecheck/tests/builds, and Playwright test discovery.
Remote CI: VERIFIED — GitHub Actions run 38045459008 passed Backend quality, Frontend quality, Docker and PostgreSQL, Playwright Chromium, and Security scans on implementation commit 2f06be4620e2126196f255829d8fe03f7f2c66aa.
CI URL: https://github.com/Itsbhavesh1101/swasthyasetu_ai/actions/runs/38045459008
Specification reconciliation: dependency-map section 2 now aligns P2 Shared Platform Kernel and P3 Persistence/migrations/events/jobs/adapter foundation with the canonical master plan, acceptance criteria, and tracker.
Remaining P2 work: P2-B module manifest/capability registry and P2-C observability/feature flags.
Blockers: none.
Open decisions: none required for P2-A; dependency timeouts map conservatively to HTTP 503.
```

---

# 14. P2-B Implementation Record

```text
Phase/Sub-phase: P2-B — Module Manifest & Capability Registry
Status: COMPLETE
Date: 2026-10-11
Branch: phase/p2-b-module-capability-registry
Base commit: 6c8fe9f54fc16788acc9c478638864a5a69eb988
Implementation commit: 4270d0e97c02ab998fdc9a423acc3b6819e76d54
Requirement IDs: FR-CORE-004, FR-CORE-005, FR-CORE-006, FR-CORE-010, FR-EXT-003, FR-EXT-004, FR-EXT-008, FR-EXT-011; ARCH-P-002, ARCH-P-007, ARCH-P-010, ARCH-P-012
Acceptance criteria: AC-P2-004, AC-P2-005, and AC-P2-009 pass locally; AC-P2-006 and AC-P2-007 remain assigned to P2-C; P2-A acceptance remains green.
Implemented scope: immutable versioned module manifests; typed capability identifiers and keys; explicit provider/module/router bindings; deterministic duplicate, declaration-integrity, missing-capability, and sealed-registry failures; registration-order-independent finalization; sealed per-application composition state; synthetic module router integration below /api/v1.
Verification: 65 backend tests passed; backend and frontend quality gates passed, including locked dependency checks, Ruff, format, mypy, compile/import smoke, frontend lint/typecheck/tests/builds, and Playwright test discovery.
Remote CI: VERIFIED — GitHub Actions run 38086205809 passed Backend quality, Frontend quality, Docker and PostgreSQL, Playwright Chromium, and Security scans on implementation commit 4270d0e97c02ab998fdc9a423acc3b6819e76d54.
CI URL: https://github.com/Itsbhavesh1101/swasthyasetu_ai/actions/runs/38086205809
Remaining P2 work: P2-C observability and feature flags.
Blockers: none.
Open decisions: none required for P2-B.
```

---

# 15. P2-C Completion Record

```text
Phase/Sub-phase: P2-C — Observability & Feature Flags
Status: COMPLETE
Date: 2026-10-11
Branch: phase/p2-c-observability-feature-flags
Base commit: 0533847ebeb8f9d0ae9ee3541130158d38a1c6f4
Implementation commit: a04bffcfab70f71572c11e15e39493e6a01f47fe
Requirement IDs: FR-CORE-004, FR-CORE-005, FR-CORE-009, FR-CORE-010, FR-EXT-005, NFR-OBS-001, NFR-OBS-011, PRIV-007; AC-P2-006, AC-P2-007, AC-P2-008, AC-P2-009
Dependencies: opentelemetry-api>=1.45.1,<2.0 resolved 1.45.1; opentelemetry-sdk>=1.45.1,<2.0 resolved 1.45.1; R3 class CORE_RUNTIME; opentelemetry-semantic-conventions 0.66b1 is an SDK transitive.
Implemented scope: immutable provider-neutral feature flags with safe/off absent behavior; configuration-backed provider and service composition; isolated per-application OTel tracer/meter providers; content-free route-template HTTP spans; bounded request count and duration metrics; safe request/trace/span log correlation; external export disabled and unsupported in P2-C.
Local acceptance: AC-P2-006 PASS; AC-P2-007 PASS; AC-P2-008 PASS; AC-P2-009 PASS. AC-P2-001 through AC-P2-005 remain green in regression tests.
Local verification: 84 backend tests passed; 35 targeted privacy/telemetry/feature-flag/error/request-context tests passed; locked sync, Ruff, format, strict mypy, compile/import smoke, backend quality gate, frontend quality gate, dependency diff, architecture audit, and git diff check passed.
Remote CI: VERIFIED — GitHub Actions run 38087693702 passed Backend quality, Frontend quality, Docker and PostgreSQL, Playwright Chromium, and Security scans on head commit 2eabfc97c0e1d3b8299ab7676430757837601545.
CI URL: https://github.com/Itsbhavesh1101/swasthyasetu_ai/actions/runs/38087693702
P2 final acceptance: AC-P2-001 PASS; AC-P2-002 PASS; AC-P2-003 PASS; AC-P2-004 PASS; AC-P2-005 PASS; AC-P2-006 PASS; AC-P2-007 PASS; AC-P2-008 PASS; AC-P2-009 PASS.
Overall P2 status: COMPLETE
Next recommended unit: P3-A — SQLAlchemy & Alembic Persistence Foundation
Blockers: none.
Open decisions: none required for P2-C.
```

---

# 16. P3-A Implementation Record

```text
Phase/Sub-phase: P3-A — SQLAlchemy & Alembic Persistence Foundation
Status: COMPLETE
Date: 2026-10-11
Branch: phase/p3-a-sqlalchemy-alembic-foundation
Base commit: 2b3dcfed0c90d1bb1d3a7153d3b67cae52080091
Implementation commit: 346035cd91bd9451c465ac4118f4ba72ca390066
Requirement IDs: FR-CORE-005, FR-CORE-009, NFR-MAINT-004, NFR-RES-006; AC-P3-001, AC-P3-002, AC-P3-003, AC-P3-010
Dependencies: SQLAlchemy[asyncio]>=2.1.4,<2.2; Alembic>=1.20,<2.0; psycopg[binary]>=3.3.6,<4.0; all R3 CORE_RUNTIME.
Migration revision: p3a_0001; down_revision=None; empty application-schema baseline.
Local migration evidence: fresh PostgreSQL 16.12 volume upgraded to one head; current/check passed; downgrade base and re-upgrade passed; public schema contained only alembic_version.
PostgreSQL integration evidence: 2 executed, 2 passed, 0 skipped; SELECT 1, commit, rollback, subsequent pool use, cleanup, and disposal verified.
Docker evidence: non-root image built; dependency imports and Alembic CLI passed; explicit container migration passed; live=200; ready=200 with required.database=ok; DB outage kept live=200 and returned ready=503 without connection details.
Acceptance: AC-P3-001 PASS; AC-P3-002 PASS; AC-P3-003 PASS; AC-P3-004 through AC-P3-009 NOT YET IMPLEMENTED; AC-P3-010 PASS by architecture/regression inspection.
Remaining P3 work: P3-B event envelope/transactional outbox; P3-C jobs/object storage.
Remote CI: PASS — run 38092648858; https://github.com/Itsbhavesh1101/swasthyasetu_ai/actions/runs/38092648858; head 346035cd91bd9451c465ac4118f4ba72ca390066; all six mandatory jobs green.
Next recommended unit: P3-B — Event Envelope & Transactional Outbox.
```

---

# 17. P3-B Completion Record

```text
Phase/Sub-phase: P3-B — Event Envelope & Transactional Outbox
Status: COMPLETE
Date: 2026-10-11
Branch: phase/p3-b-event-outbox
Base commit: b33fcd23bff023fd539984d1f7f2862cc3c52fc1
Implementation commit: ed103319016b9e3ab50471b5a92aa9e5b551a096
Requirement IDs: FR-CORE-005, FR-CORE-006, FR-CORE-009; AC-P3-004, AC-P3-005, AC-P3-006, AC-P3-010
Implemented scope: immutable versioned event envelope; explicit deterministic in-process publisher; PostgreSQL transactional outbox; caller-session repository; manual bounded dispatcher; deterministic retry/status lifecycle; handler-side idempotency fixture.
Migration revision: p3b_0002; parent p3a_0001; creates only outbox_events with three required secondary indexes and named invariant checks.
Atomicity evidence: real PostgreSQL synthetic probe + outbox commit and rollback passed in the same caller-owned session/transaction.
Dispatcher evidence: real PostgreSQL due selection with FOR UPDATE SKIP LOCKED, success, retry then success, terminal failure, future scheduling, non-redelivery, and batch continuation passed.
Local PostgreSQL results: 9 executed, 9 passed, 0 skipped (7 new P3-B and 2 P3-A regression tests).
Backend results: 137 collected; 137 passed with the explicit PostgreSQL test URL. Backend quality gate passed; frontend regression quality gate passed.
Local acceptance: AC-P3-004 PASS; AC-P3-005 PASS; AC-P3-006 PASS; AC-P3-010 PASS by architecture/regression inspection.
Delivery semantics: at-least-once; consumer side effects require idempotency; no exactly-once claim.
Remote CI: VERIFIED — GitHub Actions run 38110783677 passed Backend quality, Frontend quality, Persistence integration, Docker and PostgreSQL, Playwright Chromium, and Security scans on implementation commit ed103319016b9e3ab50471b5a92aa9e5b551a096.
CI URL: https://github.com/Itsbhavesh1101/swasthyasetu_ai/actions/runs/38110783677
Acceptance: AC-P3-004 PASS; AC-P3-005 PASS; AC-P3-006 PASS. P3-A acceptance remains green; P3-C criteria remain not implemented.
Overall P3 status: PARTIAL.
Remaining P3 work: P3-C jobs, worker abstraction, and object storage.
Next recommended unit: P3-C — Jobs, Worker Abstraction & Object Storage.
```

---

# 18. P3-C Completion Record

```text
Phase/Sub-phase: P3-C — Jobs, Worker Abstraction & Object Storage
Status: COMPLETE
Date: 2026-10-11
Branch: phase/p3-c-jobs-object-storage
Base commit: 040888179a43af56328fde57954bf4cd4cdc0b3f
Implementation commit: 5db265406fd23ab030ef57c0d83ef5cd8d6067bf
Review fix commit: df4597a48082e816f634052f2bf8fd9a16a0e176
Requirement IDs: AC-P3-007, AC-P3-008, AC-P3-009, AC-P3-010
Job scope: immutable provider-neutral contracts; non-durable process-local dispatcher/backend; explicit deterministic run_once worker; safe failure state; synthetic worker smoke.
Worker timestamp invariant: naive injected clock values are deliberately rejected before state mutation; aware non-UTC values are normalized to UTC; started_at/completed_at remain aware UTC; invalid clocks leave jobs QUEUED.
Storage scope: provider-neutral port/key/errors; root-contained local-filesystem development/test adapter; exact-byte roundtrip; typed missing/duplicate behavior; traversal and symlink-escape protection.
Dependencies: unchanged; dependency diff empty.
Migrations: unchanged; Alembic head remains p3b_0002; no jobs or storage table.
Local repair verification: 23 targeted job tests passed; 172 backend tests collected with 162 passed/10 PostgreSQL-or-host-capability skips; explicit PostgreSQL run 9 passed/0 skipped; frontend quality regression passed.
Local verification: locked sync, Ruff, format, strict mypy, compile/import smoke, backend/frontend quality gates, Docker image/build/health, PostgreSQL migration regression, and required no-change diffs passed.
Local acceptance: AC-P3-007 PASS; AC-P3-008 PASS; AC-P3-009 PASS; AC-P3-010 PASS by architecture inspection.
Remote CI: VERIFIED — GitHub Actions run 38117592284 passed Backend quality, Frontend quality, Persistence integration, Docker and PostgreSQL, Playwright Chromium, and Security scans on review fix commit df4597a48082e816f634052f2bf8fd9a16a0e176.
CI URL: https://github.com/Itsbhavesh1101/swasthyasetu_ai/actions/runs/38117592284
Final P3 acceptance: AC-P3-001 PASS; AC-P3-002 PASS; AC-P3-003 PASS; AC-P3-004 PASS; AC-P3-005 PASS; AC-P3-006 PASS; AC-P3-007 PASS; AC-P3-008 PASS; AC-P3-009 PASS; AC-P3-010 PASS.
Overall P3 status: COMPLETE.
Deferred non-blockers: Procrastinate durable-job spike; production/self-hosted object-storage adapter.
Next recommended unit: P4-A — Sessions.
```

---

# 19. P4-A Sessions Implementation Record

```text
Phase/Sub-phase: P4-A — Sessions
Status: COMPLETE
Date: 2026-10-11
Branch: phase/p4-a-sessions
Base commit: 455436c8c863a6bcd5df286a81974e6811fca02a
Implementation commit: ea7ae29cf1f619afef790c145e4076e5f4864e66
Requirement IDs: FR-IDENT-001, FR-IDENT-003, FR-IDENT-004, FR-IDENT-005, FR-IDENT-006, FR-IDENT-007, NFR-SEC-009, NFR-SEC-014, PRIV-001, PRIV-003, PRIV-006, PRIV-007; AC-P4-001 through AC-P4-004
Implemented scope: PostgreSQL-authoritative pseudonymous/kiosk sessions; one-time opaque bearer token; SHA-256 verifier at rest; typed TTL settings; expiry/close enforcement; strict versioned HTTP API; explicit sessions manifest and capabilities.
Migration revision: p4a_0003; parent p3b_0002; creates only sessions with named constraints and required indexes.
Dependencies: unchanged.
Local acceptance: AC-P4-001 PASS; AC-P4-002 PASS; AC-P4-003 PASS; AC-P4-004 PASS.
Local test evidence: 198 backend tests collected; combined real-PostgreSQL run 197 passed/1 host symlink-capability skip; PostgreSQL-marked regression 14 passed/0 skipped; 20 network-free session tests and 5 real PostgreSQL/session HTTP tests passed.
Local verification: locked dependencies, Ruff, format, strict mypy, compile/import smoke, fresh migration, downgrade/re-upgrade, Alembic drift check, backend/frontend quality gates, Docker build/migration/health, privacy/security audit, and no-change dependency/frontend/infrastructure diffs passed.
Overall P4 status: PARTIAL.
Remote CI: VERIFIED — GitHub Actions run 38131187740 passed Backend quality, Frontend quality, Persistence integration, Docker and PostgreSQL, Playwright Chromium, and Security scans on implementation commit ea7ae29cf1f619afef790c145e4076e5f4864e66.
CI URL: https://github.com/Itsbhavesh1101/swasthyasetu_ai/actions/runs/38131187740
Next recommended unit: P4-B — Identity & Authorization Baseline.
```

---

# 20. P4-B Identity & Authorization Implementation Record

```text
Phase/Sub-phase: P4-B — Identity & Authorization Baseline
Status: COMPLETE
Date: 2026-10-11
Branch: phase/p4-b-identity-authorization
Base commit: bb9a0522f13bbfb496d74d99a1655bc9d5117e58
Implementation commit: 26a9b57f8ccb57db60e14548d8b02ef9652bcdad
Requirement IDs: FR-IDENT-002, FR-IDENT-007, NFR-SEC-003, NFR-SEC-004, NFR-SEC-014; AC-P4-005, AC-P4-006, AC-P4-010
Migration revision: p4b_0004; parent p4a_0003; creates actors/actor_roles and adds only sessions.actor_id -> actors.id.
Actor/policy scope: canonical ActorType; ActorStatus ACTIVE/DISABLED; baseline persisted roles; extensible validated PermissionCode; immutable p4b-v1 explicit role-permission mapping; no wildcard or actor-type inference.
Authentication scope: redacted provider-neutral credential; principal carries only actor_id/provider/MFA proof; external provider unconfigured by default; unknown/disabled actors fail closed.
Authorization evidence: synthetic real-guard 401/403/200 tests; administrative MFA deny/allow tests; system-admin explicit non-wildcard tests; patient self-subject A->A allow and A->B deny tests.
Persistence evidence: 18 PostgreSQL-marked tests passed with zero skips, including actor/role roundtrip, disable/authentication rejection, named constraints, session actor FK, and nullable P4-A session regression.
Dependencies: unchanged. Docker/Compose: unchanged. Frontend authentication: not implemented.
Local acceptance: AC-P4-005 PASS; AC-P4-006 PASS; AC-P4-010 PASS. AC-P4-007 through AC-P4-009 remain not implemented for P4-C.
Overall P4 status: PARTIAL.
Remote CI: VERIFIED — GitHub Actions run 38145524529 passed Backend quality, Frontend quality, Persistence integration, Docker and PostgreSQL, Playwright Chromium, and Security scans on implementation commit 26a9b57f8ccb57db60e14548d8b02ef9652bcdad.
CI URL: https://github.com/Itsbhavesh1101/swasthyasetu_ai/actions/runs/38145524529
Next recommended unit: P4-C — Consent Domain & APIs.
```

---

# 21. P4-C Consent Domain & APIs Implementation Record

```text
Phase/Sub-phase: P4-C — Consent Domain & APIs
Status: COMPLETE
Date: 2026-10-11
Branch: phase/p4-c-consent-domain-apis
Base commit: f81bac4d24c6073c7ffcf3c3ec7ceab58cdc150e
Implementation commit: 4679c14a17250224c53fff007bbc7885fdca4170
CI repair commit: 381a0739be00bcb45408f6adc38224142b925e43
Requirement IDs: FR-IDENT-006, FR-IDENT-007, FR-REF-003, PRIV-003, PRIV-004, PRIV-006, PRIV-007; AC-P4-007, AC-P4-008, AC-P4-009
Specification reconciliation: ConsentRecord now canonically uses subject_type/subject_id/actor_id, matching API and persistence; machine-coded revocation_reason is persisted with revoked_at.
Implemented scope: canonical consent values and immutable record; SESSION authorization through sessions.validate; ACTOR self-authorization through trusted ActorContext; PATIENT deferral; purpose-exact/scope-subset consent checks; grant/revoke/subject-scoped list APIs; atomic minimal ConsentGranted/ConsentRevoked outbox events.
Migration revision: p4c_0005; parent p4b_0004; creates only consent_records with the required foreign key, checks, and indexes.
Dependencies: unchanged.
Local PostgreSQL evidence: fresh upgrade/current/check, downgrade to p4b_0004 and re-upgrade, seven consent integration/API tests, and 25 PostgreSQL-marked regression tests passed with zero skips.
Local test evidence: 261 passed and one unrelated Windows symlink-capability skip with PostgreSQL enabled; network-free regression 236 passed and 26 PostgreSQL skips.
Local acceptance: AC-P4-007 PASS; AC-P4-008 PASS; AC-P4-009 PASS. AC-P4-001 through AC-P4-006 and AC-P4-010 remain green in regression verification.
Remote CI: VERIFIED — GitHub Actions run 38157106550 passed Backend quality, Frontend quality, Persistence integration, Docker and PostgreSQL, Playwright Chromium, and Security scans on head commit 381a0739be00bcb45408f6adc38224142b925e43.
CI URL: https://github.com/Itsbhavesh1101/swasthyasetu_ai/actions/runs/38157106550
P4 final acceptance: AC-P4-001 PASS; AC-P4-002 PASS; AC-P4-003 PASS; AC-P4-004 PASS; AC-P4-005 PASS; AC-P4-006 PASS; AC-P4-007 PASS; AC-P4-008 PASS; AC-P4-009 PASS; AC-P4-010 PASS.
Overall P4 status: COMPLETE.
Next recommended unit: P5-A — Patient / Encounter Domain Types & Entities.
```

---

# 22. P4-C Review Fix 01 — Notice and Revoke Atomicity

```text
Review repair: VERIFIED
Date: 2026-10-11
Branch: phase/p4-c-consent-domain-apis
Reviewed head: 81e19218b4210210d78c0a88b21f6dece2e46139
Repair commit: 2b863b247c0b1d462146148738b435fae408c08d
NoticeVersion: strict ASCII machine-code grammar ^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$; malformed values fail domain and HTTP validation without echo.
Atomicity evidence: real PostgreSQL test flushes the ConsentRevoked outbox row, injects failure, and verifies rollback to GRANTED with null revocation fields, one committed ConsentGranted, and zero ConsentRevoked events.
Schema/migrations/dependencies/APIs/authorization/Docker/Compose/frontend: unchanged.
Remote CI: VERIFIED — GitHub Actions run 38161569705 passed Backend quality, Frontend quality, Persistence integration, Docker and PostgreSQL, Playwright Chromium, and Security scans on repaired code head 2b863b247c0b1d462146148738b435fae408c08d.
CI URL: https://github.com/Itsbhavesh1101/swasthyasetu_ai/actions/runs/38161569705
Local evidence: 26 focused consent tests; 237 network-free backend tests with 27 expected skips; 26 real PostgreSQL tests with zero skips; Alembic p4c_0005 head/check; backend and frontend quality gates.
P4-C status: COMPLETE.
P4 status: COMPLETE.
P4 final acceptance: AC-P4-001 through AC-P4-010 remain PASS.
Next recommended unit remains P5-A — Patient / Encounter Domain Types & Entities.
```

---

# 23. P5-A Patient / Encounter Domain Types & Entities

```text
Phase/Sub-phase: P5-A — Patient / Encounter Domain Types & Entities
Status: COMPLETE
Date: 2026-10-12
Branch: phase/p5-a-domain-types-entities
Base commit: f852ff7ca4cd70528f7e280bad5294ea2ed4a803
Implementation commit: 307237b332d3228f223f9a0504c899976356271e
Domain concepts: immutable Patient, PatientIdentifier, PatientDemographics, Encounter, FactProvenance, ClinicalFact, and typed Problem/Medication/Allergy/Procedure/Observation/Investigation values.
Encounter lifecycle: explicit canonical transition matrix; COMPLETED/ABANDONED/CANCELLED terminal; completed_at only for COMPLETED; pseudonymous session-bound encounters supported.
Provenance evidence: all canonical source and verification values tested; confidence bounds and finite decimal checks; aware timestamps normalized to UTC; raw source content excluded.
Supersession evidence: explicit immutable correction operation preserves the historical fact and provenance; clinician-confirmed facts reject extracted, low-confidence, needs-confirmation, and patient-confirmed replacements; clinician-confirmed correction remains explicit.
Local acceptance: AC-P5-001 PASS; AC-P5-002 PASS; AC-P5-003 PASS; AC-P5-004 PASS; AC-P5-005 PASS; AC-P5-006 PASS; AC-P5-007 NOT YET IMPLEMENTED; AC-P5-008 NOT YET IMPLEMENTED.
Local tests: 329 passed with 27 expected PostgreSQL skips; real PostgreSQL regression 26 passed with zero skips; backend and frontend quality gates passed.
Migration/schema: unchanged; Alembic head p4c_0005; drift check passed; zero P5 tables.
Overall P5 status: PARTIAL.
Remote CI: VERIFIED — GitHub Actions run 38209044264 passed Backend quality, Frontend quality, Persistence integration, Docker and PostgreSQL, Playwright Chromium, and Security scans on head eb11fccfe586c0c83ebff0a78f91c5200774deb9.
CI URL: https://github.com/Itsbhavesh1101/swasthyasetu_ai/actions/runs/38209044264
Final P5-A acceptance: AC-P5-001 PASS; AC-P5-002 PASS; AC-P5-003 PASS; AC-P5-004 PASS; AC-P5-005 PASS; AC-P5-006 PASS; AC-P5-007 NOT YET IMPLEMENTED; AC-P5-008 NOT YET IMPLEMENTED.
Next recommended unit after P5-A completion: P5-B — Patient / Encounter Persistence & Migrations.
```

---

# 24. P5-B Patient / Encounter Persistence & Migrations

```text
Phase/Sub-phase: P5-B — Patient / Encounter Persistence & Migrations
Status: COMPLETE
Date: 2026-10-12
Branch: phase/p5-b-persistence-migrations
Base commit: 470aeec643a577e82d035c23e5771bed74149a28
Implementation commit: afe499ebbe587999d60e89b69868d31fa205da47
Persistence scope: exactly nine P5-B tables for patients, demographics, identifiers, encounters, canonical clinical facts, provenance, and medication/allergy/observation projections.
Mapping decisions: demographics fields round-trip without inference; identifier global uniqueness remains deferred; canonical labels are derived; domain recorded_at maps to created_at; source_text remains NULL.
Integrity: sessions.patient_id now has a nullable patients FK; pseudonymous encounters remain valid; encounter versions reject stale writes; no ambiguous encounter consent FK exists.
Atomicity evidence: real PostgreSQL injected-failure tests cover patient aggregates, facts/provenance/projections, and supersession replacement/history.
Migration: p5b_0006, parent p4c_0005; downgrade removes all nine P5-B tables and the session-patient FK, then upgrade restores them with Alembic drift clean.
Local tests: 342 network-free tests passed with 41 expected PostgreSQL skips; 41 real PostgreSQL tests passed with zero skips; backend and frontend quality gates passed.
Docker evidence: unchanged Compose and Dockerfile built the non-root backend; explicit migration and live/database-aware readiness passed at p5b_0006.
P5 acceptance: AC-P5-001..006 PASS; AC-P5-007 NOT YET IMPLEMENTED; AC-P5-008 NOT YET IMPLEMENTED.
Overall P5 status: PARTIAL.
Remote CI: VERIFIED — GitHub Actions run 38219959198 passed Backend quality, Frontend quality, Persistence integration, Docker and PostgreSQL, Playwright Chromium, and Security scans on implementation commit afe499ebbe587999d60e89b69868d31fa205da47.
CI URL: https://github.com/Itsbhavesh1101/swasthyasetu_ai/actions/runs/38219959198
Next recommended unit after P5-B completion: P5-C — Timeline / Provenance Services & APIs.
```

---

# 25. P5-C Timeline / Provenance Services & APIs

```text
Phase/Sub-phase: P5-C — Timeline / Provenance Services & APIs
Status: COMPLETE
Date: 2026-10-12
Branch: phase/p5-c-timeline-provenance-apis
Base commit: ae987f683bee2bbb5759dd9abe8a3f66401bc74c
Implementation scope: trusted-subject patient create/read; bounded fact summaries; session-bound and patient-self encounter create/read/complete/abandon; public provenance reads; deterministic encounter/fact timeline with versioned opaque keyset pagination.
Authorization: patient role receives only explicit patient/encounter self permissions; patient-bound resources require trusted subject equality; pseudonymous encounter access validates the exact session bearer; MFA and existing role behavior remain unchanged.
Architecture: default modules are consent, encounters, identity, patients, provenance, sessions. Encounter and timeline services consume patient context through typed public capabilities. AST tests reject foreign P5 infrastructure imports.
Timeline order: occurred_at DESC, entry_type ASC, entry_id ASC. Clinical facts use effective_time or recorded_at; encounters use started_at. Filters execute before bounded source queries and pagination.
Privacy: patient identifiers, raw structured clinical JSON, source text, and source refs are excluded; sensitive success and error responses use Cache-Control: no-store.
Migration/dependencies/frontend/Docker: unchanged. Alembic head remains p5b_0006.
Local tests: 352 network-free tests passed with 50 expected PostgreSQL skips; 50 real PostgreSQL tests passed with zero skips.
Local acceptance: AC-P5-001..008 PASS.
Remote CI: VERIFIED — GitHub Actions run 38228256117 passed Backend quality, Frontend quality, Persistence integration, Docker and PostgreSQL, Playwright Chromium, and Security scans on implementation commit 972374df303558c99078ca3580070bdb7253deef.
P5 final acceptance: AC-P5-001..008 PASS.
Overall P5 status: COMPLETE.
Next recommended unit after CI completion: P6-A — Patient Web Design System / App Shell.
```

---

# 26. P6-A Patient Web Design System / App Shell

```text
Phase/Sub-phase: P6-A — Patient Web Design System / App Shell
Status: COMPLETE
Date: 2026-10-12
Branch: phase/p6-a-patient-web-shell
Base commit: f8634bea8876ea800b06527c4328c0c24873a661
Shell scope: responsive patient header, navigation, skip link, content and footer landmarks, patient-facing tokens/primitives, loading/error/unavailable states, and route titles.
Routes: /, /start, /consent, /language, /encounter, /documents, /results, /urgent-help, and /referrals; future capabilities remain honestly unavailable.
Urgent help: persistently visible and keyboard reachable; generic safe wording only; no invented numbers, providers, contacts, or routing decisions.
Privacy/boundaries: no browser storage, Cache API, service worker, cookies, backend requests, authentication, working language persistence, or PWA activation.
Dependencies/backend/migrations/Docker: unchanged. Alembic head remains p5b_0006.
Local acceptance: AC-P6-001 PASS; AC-P6-004 PASS; AC-P6-006 PASS; AC-P6-007 PASS; AC-P6-008 PASS; AC-P6-005 PARTIAL (shell keyboard path passes; connected onboarding remains P6-B); AC-P6-002 and AC-P6-003 NOT YET IMPLEMENTED.
Overall P6 status: PARTIAL.
Remote CI: PENDING.
Next recommended unit after P6-A completion: P6-B — Patient Onboarding / Session / Consent.
```

---

# 27. P6-B Patient Onboarding / Session / Consent

```text
Phase/Sub-phase: P6-B — Patient Onboarding / Session / Consent
Status: COMPLETE
Date: 2026-10-12
Branch: phase/p6-b-onboarding-session-consent
Base commit: 778459800d1f16dc69d7efaeb57907beac19217f
Flow: /start -> /language -> real pseudonymous session -> /consent -> real GENERAL_PRODUCT_USE grant -> /encounter readiness.
BFF: same-origin Next.js handlers; server-only SWASTHYASETU_BACKEND_URL; bounded fetch timeout; no side-effect retry; minimized safe responses.
Cookie security: opaque ID and bearer only in transient HttpOnly, SameSite=Strict, Path=/ cookies; Secure in production/non-loopback environments; bearer forwarded to FastAPI only through Authorization.
Consent constants: SESSION subject from cookie; GENERAL_PRODUCT_USE; [clinical_intake]; privacy-v1; user_requested withdrawal; duplicate active grants serialized per session and rechecked within the BFF process.
Known boundary: the fixed backend contract has no cross-instance idempotency key or active-grant uniqueness guarantee; changing it is outside P6-B.
Browser boundary: no localStorage, sessionStorage, IndexedDB, Cache API, service worker, health data, raw consent collection, or client-visible bearer.
Scope boundary: no backend/schema/migration/dependency change; Alembic head remains p5b_0006; no clinical intake or backend encounter.
Notice: bounded project notice implemented; final jurisdiction-specific notice governance-deferred.
PWA: deferred to P6-C.
Local acceptance: AC-P6-001..008 PASS.
Overall P6 status: PARTIAL.
Remote CI: PASS — GitHub Actions run 38244030550; all six required jobs passed.
Next after P6-B completion: P6-C — Accessibility + PWA Baseline.
```

---

# 28. P6-C Accessibility + PWA Baseline

```text
Phase/Sub-phase: P6-C — Accessibility + PWA Baseline
Status: COMPLETE
Date: 2026-10-12
Branch: phase/p6-c-accessibility-pwa-baseline
Base commit: b361511cbcf25e6834cc56daeb78bfc32d52e94d
Accessibility: semantic landmarks and headings, skip navigation, deterministic client-route focus, keyboard journeys, visible focus, reduced motion, forced-colors support, WCAG contrast checks, 44px representative touch targets, and 320/390px reflow verification.
Urgent help: remains persistently visible and keyboard reachable with generic safe wording; no invented contacts, emergency numbers, providers, or routing logic.
PWA: installable first-party manifest, same-origin root-scoped service worker, explicit static shell allowlist, generic offline fallback, and cache cleanup limited to obsolete SwasthyaSetu shell versions.
Cache privacy: API requests, mutations, authenticated/session responses, consent responses, health data, runtime pages, and cross-origin resources are never cached; navigations remain network-only and fall back only when offline.
Browser boundary: no localStorage, sessionStorage, IndexedDB, background sync, push, offline submission, replay queue, or bearer exposure; P6-B HttpOnly cookie/session boundary is preserved.
Scope boundary: no backend, schema, migration, dependency, Docker, Compose, deployment, or product/domain changes; Alembic head remains p5b_0006.
Local acceptance: AC-P6-001..008 PASS.
Overall P6 status: COMPLETE.
Remote CI: PASS — GitHub Actions run 38254479579; all six required jobs passed on implementation commit 8e55700c74250757c6a93d3a50a938963cf96675.
Next recommended action: complete and approve the governance-deferred P7 prerequisite specifications before P7-A.
```

---

# 29. Pre-P7 Prerequisite Specification Pack

```text
Work unit: Pre-P7 prerequisite specifications
Status: COMPLETE
Date: 2026-10-12
Branch: phase/pre-p7-specification-pack
Base commit: ed08ab6109995001821d9bd2b6b305666e045c1d
Created: 07_CLINICAL_INTAKE_SPEC.md, 22_UX_AND_USER_FLOWS.md, 23_PATIENT_APP_SPEC.md.
Traceability: FR-INTAKE-001..032 and AC-P7-001..010 are mapped to future P7-A/P7-B/P7-C evidence; no AC-P7 criterion is marked PASS.
Architecture: clinical_intake owns its typed domain and three predeclared tables; PostgreSQL is authoritative; cross-module access is capability-only; question packs register explicitly at compile time.
Safety boundary: no diagnosis, triage, threshold, treatment, medication advice, AYUSH interpretation, specialty routing, or unapproved question content was invented.
Deferrals: /messages and AI to P8; safety policy to P9; speech/translation to P12; production Dashavidha content requires clinical approval.
P6 security continuity: exact session bearer, centralized consent, server-only BFF, no-store, and PWA/browser-storage restrictions remain mandatory.
Code/schema/dependencies/CI: unchanged; Alembic head remains p5b_0006.
P7 status: NOT STARTED.
Remote CI: PASS — GitHub Actions run 38260421591; all six required jobs passed on specification commit c826f2dc1e8852483530958b4ed1f796d6cc412d.
Next recommended unit: P7-A — Intake Domain / Schema.
```

---

# 30. P7-A Intake Domain / Schema

```text
Phase/Sub-phase: P7-A — Intake Domain / Schema
Status: COMPLETE
Date: 2026-10-17
Branch: phase/p7-a-intake-domain-schema
Base commit: 2bfd834c4d1e4a1c0fb5782eeae6e2a6a097cda3
Domain: immutable intake lifecycle and typed chief complaint, HPI, history, ROS, prior investigations, missing-information, contradiction, answer, questionnaire, and pack contracts.
Serialization: strict versioned JSONB shapes reject unknown keys/versions and restore immutable typed values without echoing sensitive payloads in errors.
Persistence: exactly clinical_intakes, intake_answers, and questionnaire_instances; one intake per encounter; append-only answers; caller-owned transactions; optimistic versioning.
Migration: p7a_0007 on p5b_0006; downgrade removes only P7-A tables and re-upgrade is drift-clean.
Composition: unbound clinical_intake manifest and future capability keys; no default registration, service stub, API, or router.
Safety boundary: no diagnosis, triage, treatment, safety policy, AI, production question content, Hindi clinical content, or AYUSH/Dashavidha content.
Dependencies/frontend: unchanged.
Local verification: 379 non-PostgreSQL tests passed with 74 expected skips; all 74 real PostgreSQL tests passed; backend/frontend quality, migration downgrade/re-upgrade/drift, Docker readiness, and scope audits passed.
P7 status: PARTIAL. P7-B and P7-C are not started.
Remote CI: PASS — GitHub Actions run 38963368588; all six required jobs passed on implementation commit ce843754d37a90c2be8ee3ceef3cfb39945273c2.
Next recommended unit after CI completion: P7-B — Deterministic Adaptive Engine.
```

---

# 31. P7-A Review Fix 01 — Lifecycle Persistence Guard

```text
Review repair: VERIFIED
Date: 2026-10-17
Branch: phase/p7-a-intake-domain-schema
Reviewed head: 258c64905fc26ba8729cfc9f6b404cc07f3f199a
Repair commit: 43aa57a27f7a1718bf520ed6991a8a5e6d0e9eb5
Lifecycle guard: PostgresClinicalIntakeRepository.save locks the authoritative row and reuses the canonical domain transition semantics before mutating any persisted field; terminal intakes are immutable through this repository path.
PostgreSQL evidence: all four requested cross-state terminal transitions and same-status structured terminal mutations are rejected with InvalidClinicalIntakeTransitionError; fresh-session assertions prove status, structured content, completed_at, and version remain unchanged; valid IN_PROGRESS edit/complete/abandon saves increment exactly once.
Regression evidence: 379 non-PostgreSQL tests passed with 83 expected skips; all 83 real PostgreSQL tests passed; backend/frontend quality gates, Alembic p7a_0007 head/drift, dependency, migration, frontend, and P7-B scope audits passed.
Schema/migrations/dependencies/APIs/frontend: unchanged. Alembic head remains p7a_0007.
Remote CI: VERIFIED — GitHub Actions run 38969891055 passed Backend quality, Frontend quality, Persistence integration, Docker and PostgreSQL, Playwright Chromium, and Security scans on repair commit 43aa57a27f7a1718bf520ed6991a8a5e6d0e9eb5.
CI URL: https://github.com/Itsbhavesh1101/swasthyasetu_ai/actions/runs/38969891055
P7-A status: COMPLETE. P7 remains PARTIAL; P7-B and P7-C are not started.
Next recommended unit remains P7-B — Deterministic Adaptive Engine.
```

---

# 32. P7-B Deterministic Adaptive Engine

```text
Phase/Sub-phase: P7-B — Deterministic Adaptive Engine
Status: COMPLETE
Date: 2026-10-17
Branch: phase/p7-b-deterministic-adaptive-engine
Base commit: 1e4522c9f13309935faed0557ee2654cea54e093
Engine: pure immutable deterministic-intake.v1 evaluation with NextQuestion, ClarificationRequired, Incomplete, and CompletionReady results.
Rules: closed validated EXISTS/EQUALS/IN/AND/OR/NOT/ANSWER_DISPOSITION/HISTORY_AVAILABLE/CONTRADICTION_STATE grammar; no executable expressions.
Determinism: canonical pack/question ordering, newest-answer tie-breaks, stable UUIDv5 missing IDs, and order-perturbation/repeatability coverage.
Validation: strict pack graphs/metadata/approval boundaries and all registered answer-type constraints fail closed with privacy-safe typed errors.
History/contradictions: terminal facts are excluded, suppression requires explicit fully approved policy, reused history is never promoted to a patient answer, and configured open clarification has priority.
Extensibility: synthetic complaint, specialty, and approval-gated AYUSH packs use the same engine; no production clinical content was added.
Schema/dependencies/frontend/runtime composition: unchanged. Alembic head remains p7a_0007.
Local verification: 465 non-PostgreSQL tests passed with 83 expected skips; all 83 real PostgreSQL tests passed; 113 focused intake/domain tests passed; backend/frontend quality gates, production builds, compileall, migration drift, Docker readiness, and scope audits passed.
Remote CI: PASS — GitHub Actions run 38975516345; all six required jobs passed on implementation commit a8bd924f7ac0f0bb8a1df82be38dd3657d51afe2.
P7-A = COMPLETE. P7-B = COMPLETE. P7-C = NOT STARTED. P7 = PARTIAL.
Next recommended unit: P7-C — APIs + Patient UI.

---

# 34. P7-C Intake APIs and Patient UI

Phase/Sub-phase: P7-C — Clinical Intake Application, APIs, Patient BFF & UI

Implementation: explicit runtime registration; exact-session and SESSION-consent authorization;
PostgreSQL-serialized general-intake encounter start; one intake per encounter; server-pinned packs;
append-only answer correction; atomic questionnaire index/projection/version updates; deterministic
read/review/completion; same-origin no-store BFF; accessible question and review routes.

Clinical content: neutral English `core.intake@engineering.1` fixture, activated only when a
local/test environment also explicitly enables `engineering_clinical_intake`. Missing opt-in,
Hindi, and non-local deployment content fail closed. No AI, safety,
diagnosis, clinical threshold, AYUSH pack, abandon endpoint, dependency, schema, or migration added.

Alembic head: `p7a_0007`.

Acceptance mapping: AC-P7-001/006/008 use deterministic server pack/engine selection;
AC-P7-002 uses the chief-complaint draft projection; AC-P7-003..005 are covered by the closed eight
answer controls and typed section contracts without activating unapproved medical content;
AC-P7-007 preserves the governed history boundary with no fabricated pseudonymous history;
AC-P7-009 keeps AYUSH absent until approved; AC-P7-010 verifies draft-only, non-diagnostic review
and completion copy. All results are engineering acceptance only.

P7-C status: COMPLETE. P7 status: COMPLETE. PR #21 merged to `main` at
`926f27a5bda456b616061617dfaf1519e302b9d4` after the reviewed repair evidence passed.
```

---

# 35. P7-C Review Fix 01 — Intake Authority and Coverage

```text
Review repair: VERIFIED
Branch: phase/p7-c-intake-apis-patient-ui / PR #21
Authority: persisted pre-mutation engine selection gates new answers; eligible corrections are
re-evaluated without their prior answer history, while early, conditional, or dependency-blocked
writes fail before persistence.
Completed drafts: exact-session and consent-protected reads remain available after encounter
termination; all writes still require a writable encounter. Completed reads and retries validate
pinned instance identity, resolvability, uniqueness, and terminal status.
Typed controls/BFF: configured NUMBER units are server-derived hidden values; all eight submission
shapes and allowed non-answer dispositions have request tests; nested response alternatives are
strictly bounded and reject unexpected objects and keys.
Concurrency/rollback: real PostgreSQL tests cover competing starts and answers, stage-injected
rollback, exact-subject IDOR, consent withdrawal, closed sessions, terminal reads, and corrupted
completed-instance rejection.
Feature policy: engineering content requires environment AND explicit opt-in and can never activate
in staging, pilot, or production. Production clinical approval remains unavailable.
Schema/dependencies: unchanged. Alembic head remains p7a_0007.
Repair head: `61d04658fc2a7d1c357b77f3eaf79d75e5f8cc5d`.
Remote CI: PASS — GitHub Actions run `39148572995`; Backend quality, Frontend quality,
Persistence integration, Docker and PostgreSQL, Playwright Chromium, and Security scans passed.
Merge evidence: PR #21 merged at `926f27a5bda456b616061617dfaf1519e302b9d4`.
P7-C status: COMPLETE. P7 status: COMPLETE.
```

---

# 33. P7-B Review Fix 01 — Active Question-Version Ambiguity Guard

```text
Review repair: VERIFIED
Date: 2026-10-17
Branch: phase/p7-b-deterministic-adaptive-engine
Reviewed head: 9280523bb76593ee2ee140294329a1ff7e9a86ee
Repair: active pack validation now requires question_id uniqueness regardless of question_version, matching the engine and rule-language namespace.
Compatibility: registry storage may retain separate packs with different versions of one question; either pack activates independently, while simultaneous activation fails with InvalidQuestionPackError in both caller orders.
Scope: no engine result, rule operator, schema, migration, dependency, API, application, frontend, clinical policy, production content, AI, or P7-C change.
Migration: Alembic head remains p7a_0007.
Local verification: 467 non-PostgreSQL tests passed with 83 expected skips; all 83 real PostgreSQL tests passed; backend/frontend quality gates, compileall, migration drift, and scope audits passed.
Repair commit: d02d60917a4eb6727366397928287497f52c0c7b
Remote CI: VERIFIED — GitHub Actions run 38978341449 passed Backend quality, Frontend quality, Persistence integration, Docker and PostgreSQL, Playwright Chromium, and Security scans.
P7-B repair status: COMPLETE. P7-B remains COMPLETE. P7 remains PARTIAL.
Next recommended unit: P7-C — APIs + Patient UI.
```

---

# 36. Pre-P8 Prerequisite Specification Pack

```text
Work unit: Pre-P8 prerequisite specifications
Status: COMPLETE — SUBJECT TO USER REVIEW
Date: 2026-10-18
Branch: phase/pre-p8-specification-pack
Base commit: 926f27a5bda456b616061617dfaf1519e302b9d4
Created: 13_AI_ORCHESTRATION_SPEC.md, 14_LLM_EXTRACTION_SPEC.md,
26_PRIVACY_CONSENT_SPEC.md, 30_TESTING_STRATEGY.md, and 33_ERROR_HANDLING_POLICY.md.
Architecture: future P8-A is a project-owned in-process orchestration boundary over LLMProvider
with explicit compile-time registration; no production provider, SDK, proxy, or service is selected.
Extraction: future P8-B owns strict task schemas/prompts, evidence, validation, provenance,
uncertainty, injection/hallucination rejection, and candidate-only outputs.
Integration: /api/v1/intakes/{intake_id}/messages remains P8-C design only and is not activated.
Privacy: current exact-session/SESSION-consent/no-store/BFF rules are preserved; general intake
consent does not authorize third-party AI egress, and real-patient external transfer remains blocked
pending explicit privacy/security/institutional/regulatory review.
Traceability: AC-P8-001..010 are mapped to future P8-A/B/C evidence and remain NOT YET VERIFIED.
P7 status: COMPLETE. P8/P8-A/P8-B/P8-C status: NOT STARTED.
Schema/dependencies/code/CI: unchanged. Alembic head remains p7a_0007.
Next recommended unit after review and merge: P8-A — AI gateway + provider ports/mock.
```

---

# 37. P8-A AI Orchestration, Provider Port & Offline Mock

```text
Phase/Sub-phase: P8-A — AI Orchestration, Provider Port & Offline Mock
Status: COMPLETE
Date: 2026-10-18
Branch: phase/p8-a-ai-orchestration-provider-ports
Base commit: b510e502f58fbd964f3011f25616a03425c7c347
Architecture: project-owned in-process orchestration over an async LLMProvider Protocol, registered
explicitly through the sealed module/capability registry; no runtime discovery or service locator.
Contracts: immutable strict bounded generic request/result/source/provenance/usage values; exact
supported versions and correlation; unknown fields, non-finite values, oversize/deep collections,
forbidden provider authority, raw retention, and incompatible results fail closed.
Providers: disabled/unconfigured adapter is the runtime default. The deterministic exact-fixture
offline fake is explicit engineering tooling and is rejected in staging, pilot, and production.
Runtime policy: one 30-second maximum total deadline; retry budget capped at three; bounded backoff;
only explicitly retryable timeout, rate-limit, and provider-unavailable failures may retry. Auth,
refusal, content-policy, schema/version, cancellation, caller validation, and unknown failures do not.
Privacy/telemetry: raw request/result content, source refs, provider request IDs, credentials, and
patient/session/encounter IDs are not logged or emitted. OTel spans/metrics contain only allowlisted
operational/version metadata; request correlation is excluded from metric labels.
Scope: no API, persistence, migration, live provider, external egress, clinical prompt/schema,
fact promotion, P8-C messaging, safety/triage, frontend, service/container, or dependency change.
Local evidence: 71 focused contract/orchestration/registration/privacy/deadline/retry tests pass;
complete network-free backend regression passes 561 tests
with one expected host-capability skip and PostgreSQL-marked tests excluded.
Real integration: all 97 PostgreSQL tests pass; Alembic heads/upgrade/current/check stay clean at
p7a_0007. Non-root backend image build, explicit container migration, live/database-aware readiness,
all frontend quality/build gates, and all 13 Playwright Chromium journeys pass locally.
Acceptance: AC-P8-001 PASS; AC-P8-002 PASS; P8-A evidence for AC-P8-004/005/006 PASS/PARTIAL.
AC-P8-003/007/008/009/010 and all P8-B/P8-C evidence remain NOT YET VERIFIED.
Migration/dependencies: unchanged. Alembic head remains p7a_0007.
Remote CI: VERIFIED — GitHub Actions run 39155451018 passed Backend quality, Frontend quality,
Persistence integration, Docker and PostgreSQL, Playwright Chromium, and Security scans on
implementation commit cb7cc030e69aa74826f71924df7c6e06b1c94009.
P8 status: PARTIAL. P8-B and P8-C: NOT STARTED.
Next recommended unit after independent review and merge: P8-B — task-specific clinical extraction.
```

---

# 38. P8-A Review Fix 01 — Deadline and Failure Boundaries

```text
Work unit: P8-A review fix 01 — fail-closed provider results and total deadline
Status: COMPLETE — REMOTE CI VERIFIED
Date: 2026-10-19
Branch: phase/p8-a-ai-orchestration-provider-ports
Reviewed commit: 47a6010c5bb48b4528ca822c094f153aecdec7ce
Finding 1: malformed, wrong-type, structurally invalid, mismatched, or unsafe provider return values
are contained and normalized to nonretryable LLM_SCHEMA_INVALID without leaking raw values.
Finding 2: project-owned ContractValidationError raised by an adapter is normalized to nonretryable
LLM_SCHEMA_INVALID with the completed-attempt count and no exception detail exposure.
Finding 3: retry backoff is bounded by the remaining total deadline; timeout and unexpected sleeper
failures are normalized without starting another attempt, while cancellation still propagates.
Focused evidence: 83 AI contract/orchestration/registration/privacy tests pass, including 44
orchestration deadline/retry/failure-boundary tests.
Regression evidence: backend quality passes 573 tests with 97 PostgreSQL-marked tests skipped in
the network-free gate; all 97 real PostgreSQL tests pass; frontend quality passes 88 tests and all
production builds. Alembic head remains p7a_0007.
Scope: no schema, migration, dependency, API, adapter, Docker, Compose, frontend, P8-B, or P8-C
change. No provider/model/network egress was added.
Remote CI: VERIFIED — GitHub Actions run 39158621025 passed Backend quality, Frontend quality,
Persistence integration, Docker and PostgreSQL, Playwright Chromium, and Security scans on repair
commit 94ca6d0d385355a72588ffed04ecd59cb26dcc85.
P8-A remains subject to independent review. P8 remains PARTIAL; P8-B/P8-C remain NOT STARTED.
External-provider, clinical, privacy, consent, retention, and production activation approvals remain
pending.
```

---

# 39. P8-B Clinical Extraction Schema and Prompt Package

```text
Work unit: P8-B — Clinical Intake Extraction Schemas, Prompt Package and Validation
Status: IMPLEMENTATION COMPLETE — REMOTE CI VERIFIED / INDEPENDENT REVIEW REQUIRED
Date: 2026-10-19
Branch: phase/p8-b-clinical-extraction-schema-prompts
Base commit: 9d764d381a3c669baac4374ba67dde33536db211
Package: detached clinical_intake/extraction contracts, compile-time engineering prompt registry,
conservative source/evidence validation, and one-call P8-A capability application service.
Authority: all outputs are immutable AI_EXTRACTED_UNCONFIRMED candidates; literal English
engineering fixtures only; diagnosis, treatment, clinical scores, final triage, confirmation,
provider/referral data, and later-phase policy outputs are outside the closed schema.
Safety/privacy: default off; no runtime registration, API, persistence, event, telemetry content,
provider SDK, network adapter, or external egress. Deterministic P7 intake remains the fallback.
Validation: exact source version/hash and Unicode half-open spans, literal quote/value support,
server-derived proposal IDs, prompt/schema/provider/model/source correlation, whole-output rejection,
and a deliberately small positive allowlist of unambiguous first-person synthetic engineering
fixtures. All other candidate-producing source forms are rejected because authority is unproven.
Schema/migrations/dependencies/frontend: unchanged. Alembic head remains p7a_0007.
Acceptance: AC-P8-003/004/006/007/008/009/010 implementation evidence added; AC-P8-001/002 and
P8-A evidence preserved. P8-B is subject to independent review; P8-C is NOT STARTED; P8 is PARTIAL.
Remote CI: VERIFIED — GitHub Actions run 39170768507 passed Backend quality, Frontend quality,
Persistence integration, Docker and PostgreSQL, Playwright Chromium, and Security scans on
implementation commit 17d40eea8568efc55bd3a6dbab3041d998c8b110.
Open gates: production prompt/schema semantics, clinical evidence sufficiency, real-patient external
egress/consent/security/institutional/regulatory review, retention, and governed confirmation remain
unapproved and unimplemented.
```

---

# 40. P8-B Review Repair 01 — Source Authority and Prompt Boundary

```text
Work unit: P8-B review repair 01
Status: IMPLEMENTATION COMPLETE — REMOTE CI PENDING
Date: 2026-10-19
Branch: phase/p8-b-clinical-extraction-schema-prompts
Reviewed head: 3f1da4678d1e2ecc516b7b2641f5377182b19bb3
Source authority: the prior negative-pattern heuristic is removed. Candidate promotion now requires
an exact, server-owned engineering fixture form and literal, with evidence covering the authorized
claim exactly. The guard applies to every enabled CandidateFieldKey and rejects mixed output wholly.
Unicode boundary: all extraction string fields deliberately reject malformed UTF-8 Unicode with
content-free validation errors; lone high/low surrogates cannot reach provider invocation or output
serialization. Valid NFC Unicode remains supported.
Prompt boundary: the immutable manifest records ADAPTER_ROLE_BINDING_NOT_VERIFIED. A future approved
adapter must resolve prompt ID/version against the server-owned manifest, verify the content hash,
and render the instruction template in a trusted instruction role separate from patient source data.
P8-B does not transport that instruction through P8-A and does not claim adapter-level role
enforcement or production prompt-injection resistance.
AC-P8-009: schema/data separation is regression-tested; adapter role binding is NOT YET VERIFIED,
so full production instruction-boundary acceptance remains deferred.
Scope: no API, persistence, migration, dependency, adapter, provider, Docker, Compose, frontend, or
P8-C changes. Alembic head remains p7a_0007.
Open gates: clinical approval of production semantics/evidence, approved external-provider adapter,
role separation assurance, real-patient egress/consent/security/institutional/regulatory review,
retention, and governed confirmation remain unapproved and unimplemented.
```

---

# 41. P8-C Gated Intake Integration — Safe Engineering Subset

```text
Work unit: P8-C — Gated Intake Integration, API and UI
Status: PARTIAL — SAFE ENGINEERING SUBSET IMPLEMENTED / PATIENT-FACING STAGE 3 BLOCKED
Date: 2026-10-19
Branch: phase/p8-c-guarded-clinical-intake-integration
Base commit: ad3bb6cd709e2f403e6e798d1bac31f9477eaf23
Governance: P8_C_INTEGRATION_GATE_REVIEW.md records the authoritative evidence, owner, decision
state, approved scope, future transaction proposal, and Stage 3 approval checklist. No missing
approval is inferred or invented.
Authorized integration: exact synthetic fixtures exercise ClinicalIntakeExtractor through the
AIOrchestrationService and DeterministicOfflineLLMProvider with correlated contract, prompt, schema,
source provenance, deadline, retry, and provider metadata.
Safety: candidates remain detached AI_EXTRACTED_UNCONFIRMED values. Disabled/unconfigured providers,
all closed P8-A failures, schema/provenance/evidence failures, unsupported injection-like input,
abstention, and refusal produce no fabricated candidate and preserve deterministic P7 availability.
Privacy/egress: the integration is process-local and network-blocked in tests; no patient text,
identifier, source reference, or candidate content is logged. No live adapter or external egress is
added.
P7/API/schema: P7 state and public routes remain unchanged. No /messages route, BFF handler, patient
UI, AI persistence/table, migration, event, automatic activation, or canonical fact/answer mutation
is added.
Dependencies/migrations: unchanged. Alembic head remains p7a_0007.
Local verification: 19 new P8-C integration tests pass; the combined P8-A/B/C focused matrix passes
208 tests; the network-free backend gate passes 698 tests with 97 PostgreSQL-marked tests skipped;
all 97 real PostgreSQL tests pass; frontend quality passes 88 unit tests and all three production
builds; Docker build, non-root image, explicit migration, liveness, and database-aware readiness
pass. Playwright's first 13-test run had one intake-navigation timeout, that journey passed alone,
and a complete retry passed all 13 journeys. Formatting, lint, strict typing, compile/import,
Alembic heads/current/check, privacy, route, egress-import, scope, and diff audits pass.
Remote CI: pending final branch commit.
Acceptance: synthetic evidence advances AC-P8-002/004/005/006/007/008/009/010, but clinical and
privacy production acceptance remains unverified. P8 and P8-C remain PARTIAL.
Open approvals: clinical scope/languages/copy; trusted role binding; specific AI consent and egress;
provider/processor/residency terms; persistence/retention/deletion; withdrawal and in-flight
handling; confirmation/canonical mutation; create-message idempotency/concurrency/replay; threat,
privacy, and clinical safety reviews; explicit production enablement.
```

---

# 42. P9-A Safety Decision Types and Guarded Policy Registry

```text
Work unit: P9-A — Safety Decision Types and Guarded Policy Registry
Status: IMPLEMENTATION COMPLETE — REMOTE CI VERIFIED / INDEPENDENT REVIEW REQUIRED
Date: 2026-10-19
Branch: phase/p9-a-safety-decision-types-policy-registry
Base commit: 9a6f5b1190909ab90aa7c0cc87a160a851d84763
Contracts: exact five-route vocabulary and an immutable, bounded SafetyDecision with deterministic
machine reason codes, exact policy identity/version, strict flags, and UTC timestamp normalization.
Registry: immutable explicit registration/selection, canonical metadata checksum, duplicate/tamper/
unknown/inactive rejection, deterministic ordering, and typed content-free closed failures.
Fixture: metadata-only synthetic engineering identity; explicitly selectable only in LOCAL/TEST;
the actual boundary rejects STAGING/PILOT/PRODUCTION. No clinical-approved state or clinical rules
exist.
Governance: docs/08_SAFETY_AND_TRIAGE_POLICY.md is a DRAFT architecture/approval gate containing no
medical criteria. An approved, source-traceable, versioned policy and recorded clinical review are
still required before P9-B/P9-C or patient use.
Default/runtime: default registry is empty and unavailable. No evaluator, safety API, runtime module
registration, persistence/table/migration, frontend, external provider, network egress, or P7/P8
state mutation was added. Alembic head remains p7a_0007; dependencies and lockfiles are unchanged.
Acceptance: AC-P9-001 and the typed-shape portion of AC-P9-002 have P9-A evidence. The unavailable
policy portion of AC-P9-006 and synthetic distinction/environment guard portion of AC-P9-007 have
evidence. AC-P9-003/004/005/008 and every clinically meaningful outcome remain deferred to an
approved policy, P9-B, and P9-C. P9-B/P9-C are NOT STARTED; P9 remains PARTIAL.
Local verification: 48 focused tests pass; network-free backend passes 746 with 97 PostgreSQL tests
skipped; all 97 real PostgreSQL tests pass; frontend passes 88 tests and all three production
builds; Docker build/migration/non-root/live/readiness checks pass. Playwright passes all 13
journeys under the CI retry contract; the known intake-navigation first-attempt timeout reproduced
and the affected journey also passed independently without retry. Ruff, strict mypy, compile/import,
Alembic current/check, privacy/scope/route/egress/dependency/diff audits pass.
P8-C: every Stage 3 blocker in P8_C_INTEGRATION_GATE_REVIEW.md remains open and unchanged; P8-C and
P8 remain PARTIAL.
Remote CI: VERIFIED — GitHub Actions run 39240064163 passed Backend quality, Frontend quality,
Persistence integration, Docker and PostgreSQL, Playwright Chromium, and Security scans on the
implementation commit. The documentation-only evidence commit must pass the same six jobs on its
exact final SHA before handoff.
```

---

# 43. P9-A Review Repair 01 — Registry Integrity and Error Boundaries

```text
Work unit: P9-A review repair 01
Status: IMPLEMENTATION COMPLETE — REMOTE CI VERIFICATION REQUIRED / INDEPENDENT REVIEW REQUIRED
Date: 2026-10-19
Branch: phase/p9-a-safety-decision-types-policy-registry
Reviewed head: 6dd860d58e2b036d245f32857c4f7a68a199d7ba
Registry integrity: registration now validates and stores immutable scalar snapshots rather than
caller-owned metadata references. all(), require(), and get_active_policy() reconstruct and
revalidate detached metadata, so mutation before or after a returned read cannot alter later reads.
Exact registered-key, selected-identity, policy type, checksum, approval, activation, and protected
environment checks remain fail closed.
Error privacy: require() validates bounded machine identities and uses cause-free lookup. Valid but
unknown identities still raise UnknownPolicyError, while malformed identities raise the typed
InvalidPolicyMetadataError without preserving caller content in exception causes or tracebacks.
Selection bounds: ActivePolicySelection and require() share the metadata limits of 128 characters
for policy IDs and 64 for versions, with exact-limit and limit-plus-one regression coverage.
Tracker correction: the Before P9 row now truthfully marks 08_SAFETY_AND_TRIAGE_POLICY.md as DRAFT
— NOT CLINICALLY APPROVED, while real clinical rules remain NOT STARTED.
Local verification: 61 focused tests pass; network-free backend passes 759 with 97 PostgreSQL tests
skipped; all 97 real PostgreSQL tests pass; frontend passes 88 tests and all three production
builds; Docker build/migration/non-root/live/readiness checks and all 13 Playwright journeys pass.
Ruff, strict mypy, compile/import, Alembic current/check, privacy, architecture, dependency, scope,
and diff audits pass. Alembic remains p7a_0007 and dependencies/lockfiles are unchanged.
Scope: no evaluator, clinical rule, route, API, persistence, migration, frontend, provider, egress,
runtime activation, P9-B/P9-C, or P8-C patient-facing AI change. All clinical and P8-C approval
gates remain open.
Remote CI: pending on the repair commit; the exact final run ID and six conclusions must be reported
in PR #26 and the handoff before this repair is considered verified.
```

---

# 44. P9-B Deterministic Safety Engine — Synthetic Engineering Evidence

```text
Work unit: P9-B — Deterministic Safety Engine and Synthetic Regression Proof
Status: IMPLEMENTATION COMPLETE — REMOTE CI VERIFICATION REQUIRED / INDEPENDENT REVIEW REQUIRED
Date: 2026-10-19
Branch: phase/p9-b-deterministic-safety-engine
Base commit: 5c4cdc604f36aa6683e4daf0c3f975f7f3055511
P9-A: PR #26 is merged at the exact base. Its immutable SafetyDecision and guarded metadata registry
remain unchanged, and all 61 focused P9-A review-repair tests remain present.
Contracts: frozen bounded synthetic input/rule/rule-set types expose only a closed nonmedical token
vocabulary. Rules use fixed symbolic predicates and SYNTHETIC_ reasons; no free text, patient/session/
encounter identity, clinical measurement, dynamic expression, callback, model score, or provider data
is accepted. The rule-set checksum covers canonical fixture bytes only and is not clinical approval.
Engine: the pure evaluator resolves PHYSICAL_SAFETY through the injected registry on every call,
then requires exact metadata and exact compile-time fixture identity/version/checksum. LOCAL/TEST need
explicit synthetic selection; default registry and STAGING/PILOT/PRODUCTION fail closed at the actual
evaluate boundary. Importing the fixture has no registration or activation side effect.
Synthetic mechanics: tests prove hard override over every lower toy route, ambiguity, exclusion, and
LOW_RISK advisory; the advisory has no callable or decision authority. Missing/ambiguous toy input
requires clarification and blocks self-care. Exclusion precedes toy self-care. Deterministic input/
rule ordering, reason ordering, UTC normalization, repeatability, all five symbolic routes, conflicts,
tampering, stale identity, malformed input, invalid clocks, and privacy-safe failures are covered.
Architecture: no safety API, /messages route, runtime module binding, ORM/table/migration, audit/outbox,
provider, network egress, P7/P8 mutation, frontend/BFF route, patient decision, or dependency change.
Alembic head remains p7a_0007; safety_decisions and policy_versions tables are absent.
Acceptance: AC-P9-001 is preserved. AC-P9-002..008 have only the P9-B engineering evidence explicitly
allowed by the phase prompt. Clinical semantics, real precedence, production model policy, patient
decision persistence, P9-C/P15 integration, and production activation are NOT APPROVED/NOT VERIFIED.
Local verification: 127 focused safety tests pass (61 preserved P9-A plus 66 P9-B); network-free
backend passes 825 tests with 97 PostgreSQL tests skipped; all 97 real PostgreSQL tests pass; frontend
passes 88 unit tests and all three production builds; all 13 Playwright journeys pass sequentially,
and the parallel CI retry contract exits successfully. Clean Alembic upgrade/current/check and
downgrade/re-upgrade, Docker build/migration/non-root/live/database-readiness, compile/import, Ruff,
strict mypy, privacy/route/table/egress/scope, and diff audits pass.
P8-C: every Stage 3 approval blocker in P8_C_INTEGRATION_GATE_REVIEW.md remains open and unchanged,
including clinical scope/copy, trusted role binding, AI-specific consent and egress, provider terms/
residency, persistence/retention/deletion, withdrawal/in-flight handling, confirmation/canonical
mutation, message idempotency/concurrency/replay, threat/privacy/clinical-safety review, and explicit
production enablement. P8-C and P8 remain PARTIAL.
Phase status: P9-B engineering mechanics are implemented pending independent review; P9-C is NOT
STARTED; P9 remains PARTIAL. The authoritative docs/08 policy remains DRAFT — NOT CLINICALLY APPROVED
— NO REAL TRIAGE RULES. Real policy activation and patient rollout remain BLOCKED.
Remote CI: VERIFIED — GitHub Actions run 39266042012 passed Backend quality, Frontend quality,
Persistence integration, Docker and PostgreSQL, Playwright Chromium, and Security scans on
implementation commit 00b27be76b849164a0471291da74079ed40e8340. This documentation-only evidence
commit must pass the same six jobs on its final SHA before handoff.
```

---

# 45. P9-C Gated Safety Result Presentation and Degraded-Mode Evidence

```text
Work unit: P9-C — gated safety result presentation and degraded-mode engineering evidence
Status: PARTIAL — SAFE PRESENTATION ENGINEERING SUBSET / PATIENT ROUTING BLOCKED
Date: 2026-10-19
Branch: phase/p9-c-guarded-safety-result-presentation
Base commit: 541fa9033349162c4bf1abb5d6cdfe7a6cd8d6fd
Gate decision: no clinician-approved real policy, route semantics, patient copy, persistence contract,
API authorization design, or pilot/production enablement is recorded. The required gate matrix names
the accountable approval roles and keeps every Stage 3 gate open. No draft, checksum, flag, consent,
synthetic fixture, or test result is treated as clinical authority.
Stage 2 contract: a closed safety-presentation.v1 projection accepts only the exact P9-B synthetic
policy identity, exact bounded keys and route tokens, sorted unique SYNTHETIC_ reasons, consistent
flags, and a fresh UTC timestamp. LOCAL/TEST require explicit selection. Unknown or protected
environments, malformed data, stale/future/invalid clocks, getter failures, and missing decisions
fail closed to an immutable unavailable/degraded state that always blocks hypothetical self-care.
Presentation proof: a disconnected component used only by unit tests prominently identifies
engineering test data as not a medical assessment. It renders machine tokens only and exposes no
advice, CTA, link, form, patient identity, source evidence, provider output, or health data.
Unavailable/degraded states state that no safety assessment has been performed. The production app
does not import or route to this component; /results remains unavailable and /urgent-help remains the
independent generic shell resource.
Architecture: no backend application/service/API/BFF route, capability registration, ORM/table,
migration, outbox/audit record, patient signal parser, persistence, P7/P8 mutation, provider/egress,
runtime synthetic import, dependency, or lockfile change. Alembic remains p7a_0007 and no safety
table exists. P9-A/P9-B deterministic mechanics remain unchanged and have no real safety authority.
Acceptance: AC-P9-001..008 gain only the explicitly bounded Stage 2 schema, isolation, inaccessible
synthetic rendering, and degraded/fail-closed presentation evidence. Clinically valid decisions,
real precedence and uncertainty rules, approved patient actions, persistence, authenticated APIs,
P15 self-care release, and pilot/production activation remain NOT APPROVED/NOT VERIFIED.
Local verification: 127 focused safety tests pass; network-free backend passes 825 tests with 97
PostgreSQL tests skipped; all 97 real PostgreSQL tests pass; frontend passes 128 tests (124 patient,
2 UI, 1 clinician, 1 admin) and all three production builds. All 13 Playwright journeys pass in a
clean sequential run; the CI-style parallel run also exited successfully after two truthful flaky
retries (one route-navigation timeout and one intake-start timing failure). Clean Alembic upgrade/
current/check and downgrade/re-upgrade, Docker build/migration/non-root/live/database-readiness,
compile/import, Ruff, strict mypy, privacy/route/table/egress/scope/diff audits, source secret scan,
filesystem dependency/configuration scan, and backend image vulnerability scan pass.
P7/P8-C: P7 remains non-diagnostic and does not claim urgency assessment. Every P8-C Stage 3 gate
remains open and unchanged, including trusted role binding, AI-specific consent/egress, provider
terms/residency, retention/deletion, confirmation/canonical mutation, idempotency/concurrency/replay,
threat/privacy/clinical-safety review, and explicit production enablement. P8-C and P8 remain PARTIAL.
Remote CI: VERIFIED — GitHub Actions run 39277176339 passed Backend quality, Frontend quality,
Persistence integration, Docker and PostgreSQL, Playwright Chromium, and Security scans on
implementation commit 576acd5fe0b039eb4fb0977be22c0c333f5b3c18. This documentation-only evidence
commit must pass the same six jobs on its exact final SHA before handoff.
```

---

# 46. Pre-P10 Clinician and Provenance Specification Pack

```text
Work unit: Pre-P10 canonical documentation prerequisites
Status: COMPLETE — SPECIFICATIONS WRITTEN, SUBJECT TO INDEPENDENT REVIEW
Baseline: main @ 08219993e96e2023500370bcaf4057c29f289df6
Deliverables: 12_CLINICAL_PROVENANCE_SPEC.md, 24_CLINICIAN_DASHBOARD_SPEC.md, and
P10_READINESS_GATE_REVIEW.md define source authority, fact disposition/correction, source-traceable
summary design, clinician queue/overview/UI boundaries, phased ownership and approval gates.
Repository facts: P5 facts/provenance and P7 deterministic intake are working foundations;
summaries remains a placeholder and clinician-web remains an empty shell. Permission constants do
not prove clinician assignment or production identity.
Gate result: 0/9 gates are approved for live clinician access; 6 are OPEN and 3 are BLOCKED. P10-B,
P10-C sensitive data, and P10-D remain blocked. After independent specification review, only an
explicitly scoped P10-A domain/test-only subset is recommended.
Governance: P8 and P9 remain PARTIAL. Every P8-C and P9-C Stage 3 restriction remains in force;
P7 answers, P8 candidates, P9 synthetic decisions and P5 clinical facts are not interchangeable.
Acceptance: AC-P10-001..009 are mapped but NOT YET IMPLEMENTED. Documentation is not clinical,
privacy, identity, security, data-sharing, migration or production approval.
Architecture: documentation-only; no runtime, API, persistence, migration, dependency, lockfile,
CI, infrastructure, feature-flag or clinical-policy change. Alembic remains p7a_0007.
Next action: independent review of both canonical specifications and the readiness-gate matrix,
then a separate prompt for the bounded P10-A subset if accepted. Do not start P10-B/C/D.
```

---

# 47. P10-A Deterministic Source-Backed Summary Domain

```text
Work unit: P10-A — isolated synthetic/offline summary-domain foundation
Status: COMPLETE SAFE ENGINEERING SUBSET — MERGED; live P10 remains PARTIAL/BLOCKED
Baseline: main @ 9498972eceaa1ec6c647fd8e4dcb7f2e84748583
Merge evidence: P10-A PR #30 merged at 7aad4dce8c68d008e98287d769d83d109c3cb46b;
reviewed feature head 400c8f19ccc6a3d1b1e91038665b0a30c3cda432 has the same tree.
Pre-P10 evidence: PR #29 merged at the exact baseline; both canonical specifications remain
technical prerequisites rather than clinical, institutional or production approval.
Implementation: frozen bounded summary/source/section/readiness/freshness values, strict P5 fact
versus P7 patient-reported source contracts, exact-copy deterministic draft projection, explicit
synthetic coverage and unresolved-conflict handling, and pure source-version drift classification.
Safety/privacy: fixtures use nonmedical SYNTHETIC_* labels only; sensitive labels are repr-hidden;
errors are typed and content-free. P8 candidates and P9 synthetic decisions are prohibited inputs.
No claim is generated, rewritten, diagnosed, treated, routed, signed, approved or promoted.
Architecture: summaries remains inert unless directly imported by tests. No runtime registration,
public capability, application service, API/BFF/UI, repository read, ORM/table/migration,
audit/outbox, provider/LLM, network/file I/O, dependency, lockfile, CI or infrastructure change.
Acceptance honesty: the subset provides partial engineering evidence toward AC-P10-004 and domain
provenance mechanics related to AC-P10-007. AC-P10-001..009 remain NOT YET VERIFIED/NOT ACCEPTED
for live clinical workflows. P10-B, sensitive P10-C and P10-D remain BLOCKED by the 0/9 gate matrix.
Governance: P8 and P9 remain PARTIAL; every P8-C/P9-C Stage 3 restriction remains unchanged.
Alembic remains p7a_0007. P10 macro is IN PROGRESS pending independent acceptance, never COMPLETE.
```

---

# 48. Pre-P11 Document AI / OCR Specification and Readiness Pack

```text
Work unit: Pre-P11 canonical documentation prerequisites
Status: COMPLETE — SPECIFICATIONS WRITTEN, SUBJECT TO INDEPENDENT REVIEW; P11 NOT STARTED
Baseline: main @ 7aad4dce8c68d008e98287d769d83d109c3cb46b
Deliverables: 15_DOCUMENT_AI_OCR_SPEC.md and P11_READINESS_GATE_REVIEW.md define document
ownership/lifecycle, secure ingestion/private-object boundaries, separate parser/OCR ports,
benchmark-gated provider status, processing attempts/jobs/registry, detached candidates,
provenance/source permission, future UI privacy/accessibility, and P11-A/B/C/D/E ownership.
Repository truth: documents contains only .gitkeep; conceptual document tables/routes are absent;
the patient /documents route is unavailable. Existing ObjectStoragePort/local adapter,
process-local jobs/explicit worker and PostgreSQL outbox are generic primitives, not a medical
upload pipeline, durable document worker, production object store, or document event integration.
Gate result: 0/9 gates approved, 5 OPEN, 4 BLOCKED. There is no blanket patient-data, clinical,
privacy, scanner, storage, provider, retention, source-access, pilot or production approval.
Safest candidate next subset after independent review is a separately prompted P11-B
engineering-only parser/OCR port, deterministic nonmedical mock, bounded job-contract and benchmark
harness subset with no provider dependency, model, upload API, persistence, egress or activation.
Acceptance truth: FR-DOC-001..023, FR-PROV-001..007 and AC-P11-001..011 are mapped but all remain
NOT YET IMPLEMENTED / NOT VERIFIED. Documentation is not acceptance evidence.
Governance: P8-C/P9-C Stage 3 remain blocked; P10 stays PARTIAL with live clinician/source access
blocked. OCR evidence cannot become clinical truth, P5 overwrite, P9 safety, P10 signed summary or
P15 self-care. P7 deterministic intake remains available.
Architecture: documentation-only; no runtime, API, schema, migration, dependency, lockfile, CI,
Docker, feature flag, policy, model or dataset change. Alembic remains p7a_0007.
Next action: independent review of the canonical specification and readiness matrix, then an
explicit separate phase prompt. Do not start P11-A/B/C/D/E automatically.
```

---

# 49. P11-B Synthetic Parser/OCR Ports and Processing Contracts

```text
Work unit: P11-B — safe engineering subset only
Status: COMPLETE SAFE ENGINEERING SUBSET — MERGED; live P11 remains PARTIAL/BLOCKED
Baseline: main @ 449cd917f8a79baf30b7a90fc04cd32d131fb318
Merge evidence: P11-B PR #32 merged at a8dea0b374017793f119a85daa971b8256881ab4;
reviewed feature head 3c9bed8836ac0a672e9f9054e7c10d9458bf08ab has the same tree.
Contracts: distinct provider-neutral DocumentParserPort and OCRPort protocols; frozen bounded
synthetic requests/results with explicit versions, identity/source/page coverage, geometry,
confidence-unavailable semantics, deterministic ordering, provider provenance and content-free
closed failures. OCR output remains evidence only and cannot express clinical authority.
Test support: deterministic exact-mapping MockOCRAdapter and in-memory benchmark harness exist only
under backend/tests. They use nonmedical SYNTHETIC_* tokens, perform no I/O or egress, select no
provider and make no accuracy or clinical-support claim.
Processing: immutable in-memory attempt transitions reject stale generation, replay, deadline,
duplicate identity and invalid retry state. Generic JobRequest composition carries bounded
content-free metadata only; no runtime handler, daemon, automatic retry or durability claim exists.
Architecture: no upload/file/object-storage access, API/BFF/UI, runtime registration, ORM/table,
migration, outbox write, production adapter/model, dependency, lockfile, Docker or CI change.
Alembic remains p7a_0007.
Acceptance: partial engineering evidence only toward AC-P11-004/005 and offline mechanics of
AC-P11-003/009. No AC-P11 criterion is accepted for a real document workflow. All 0/9 live P11
gates remain unapproved; P8-C/P9-C Stage 3 and P10 live clinician/source gates remain blocked.
P11-A/D/E are not started by this work. P7 deterministic manual intake remains available.
```

---

# 50. P11-C Synthetic Document Classification and Processor Registry

```text
Work unit: P11-C — safe engineering subset only
Status: COMPLETE SAFE ENGINEERING SUBSET — MERGED IN PR #33; live P11 remains PARTIAL/BLOCKED
Baseline: main @ a8dea0b374017793f119a85daa971b8256881ab4
Classification: an exact closed eight-type vocabulary and immutable versioned decision contracts
normalize only caller-declared synthetic labels. Empty/UNKNOWN abstain, OTHER is unsupported, and
mixed labels conflict; none silently selects a processor. No OCR text, filename, MIME, bytes, image,
URL, natural language, confidence, model or heuristic is inspected.
Registry: six future processor names exist solely as frozen ENGINEERING_ONLY/NOOP_ABSTAIN metadata.
Construction uses explicit tuples; lookup and routing require exact IDs, versions, document types
and explicit pins. Duplicate identity, cross-processor ownership, unpinned simultaneous versions,
unknown versions and incompatible categories fail closed. Receipts contain no callable or handler.
Security/privacy: bounded SYNTHETIC_* non-dereferenceable handles are repr-hidden; direct constructors
and entry points validate runtime types before hashing/sorting and return closed content-free errors.
Snapshots are detached, order-independent and deterministic. Tests contain no medical assertions or
patient data.
Architecture: no app/public registration, route/API/BFF/UI, source read, object storage, job binding,
ORM/table/migration, provider/model, egress, dependency, lockfile, Docker, CI or feature-flag change.
Alembic remains p7a_0007. P11-B contracts and test-only mock remain unchanged.
Acceptance honesty: partial synthetic engineering evidence only toward FR-DOC-010, FR-DOC-023 and
AC-P11-006. It is not a medical classifier or working live processor registry. AC-P11-001..011 remain
NOT VERIFIED for live document use. The P11 live matrix remains 0 APPROVED / 5 OPEN / 4 BLOCKED.
Governance: every P8-C/P9-C Stage 3 restriction remains in force; P10 live matrix remains 0/9.
P11-A/D/E, real OCR providers and live patient/clinician workflows remain blocked by this historical
P11-C work unit. P11-C was independently reviewed and merged in PR #33 at
`d3c2125ebdb2c927f254b913a890b411ccc971e5`.
```

---

# 51. P11-A Synthetic Document Lifecycle and Ingestion Guards

```text
Work unit: P11-A — safe engineering subset only
Status: MERGED after independent review in PR #34; live P11 remains PARTIAL/BLOCKED
Baseline: main @ d3c2125ebdb2c927f254b913a890b411ccc971e5
Domain: frozen versioned ENGINEERING_ONLY metadata uses strict OpaqueId, the P11-C DocumentType
vocabulary, non-dereferenceable synthetic source/owner/idempotency handles, declared synthetic
representation and bounded byte/page/checksum claims. The stated 50 MiB/100-page engineering caps
are test-contract bounds only and are not patient upload policy.
Lifecycle: exact Spec 15 states and edges are pure and immutable. State/metadata/generation guards,
UTC chronology, explicit synthetic validation decisions, terminal rejection and distinct new
attempt identities for reprocessing fail closed with content-free errors. Document, P11-B attempt,
OCR-result and generic-job states remain distinct.
Assessment: pure descriptor comparison accepts no bytes, stream, path, URL, filename, MIME or
storage reference. UNKNOWN requires review; OTHER and owner/source/representation mismatches reject.
Owner-scoped idempotency compares only two explicitly supplied descriptors and never performs a
lookup, existence probe, digest-only cross-owner match or authorization decision.
Architecture: no API/BFF/UI, application/public registration, file scanner/parser, object-store
access, job/outbox binding, ORM/table/migration, feature flag, external provider/model, egress,
dependency, lockfile, Docker or CI change. P11-B/C production files remain unchanged and the OCR
mock remains test-only. Alembic remains p7a_0007.
Deferred: real stream/signature/MIME/active-content/malware/quarantine validation; upload Pattern
A/B; checksums over bytes; patient/clinician authority; private storage, encryption, region,
retention/deletion and schema decisions all still require their recorded human approvals.
Acceptance honesty: partial synthetic reasoning evidence only toward FR-DOC-001/003/022 and
AC-P11-001/003/010 boundaries. AC-P11-001..011 remain NOT VERIFIED for live document workflows.
The P11 gate matrix remains 0 APPROVED / 5 OPEN / 4 BLOCKED; P10 live clinician gates remain 0/9;
P8-C/P9-C Stage 3 restrictions remain in force. The independently reviewed P11-A head
`89f304b9ff98e08fb4a45c72177b9fbedbfd5cf8` was merged at main
`87f87e0a454db86bcdf67569fa1e6ab2061ee46c` with no tree differences. Do not infer live approval.
```

---

# 52. P11-D Detached Synthetic Evidence and Unconfirmed Candidate Contracts

```text
Work unit: P11-D — safe engineering subset only
Status: MERGED after independent review in PR #35; live P11 remains PARTIAL/BLOCKED
Baseline: main @ 87f87e0a454db86bcdf67569fa1e6ab2061ee46c
Contracts: frozen, versioned ENGINEERING_ONLY candidate envelopes permit only UNCONFIRMED or
ABSTAINED states. They carry nonmedical synthetic identity tokens, UNKNOWN confidence, bounded
canonical structural evidence references, and content-free typed errors. No source text, normalized
medical value, unit, code, patient narrative, embedding, prompt, or provider payload is represented.
Evidence: the pure verifier revalidates detached candidate, P11-B structural result, P11-C synthetic
classification and NOOP_ABSTAIN processor receipt metadata. It matches exact request/document/attempt/
source/schema/routing/page/block/table/cell/geometry identities without reading TextBlock.text.
Positive output is only STRUCTURALLY_MATCHED_UNCONFIRMED with source access NOT_VERIFIED. Abstained
or incomplete processing never becomes a positive structural outcome.
Architecture: no API/BFF/UI, application/public registration, filesystem/network/source-open,
provider/model, P5 fact write, job/object-storage binding, ORM/table/migration, feature flag,
dependency, lockfile, Docker or CI change. P11-A/B/C production modules remain unchanged and the
patient document UI remains unavailable. Alembic remains p7a_0007.
Deferred: real medical schemas/extraction and values; source existence/access/consent and retention;
patient identity and clinical correctness/verification; clinician review; live OCR/LLM providers;
persistence, runtime activation and every human clinical/privacy/security approval.
Acceptance honesty: partial synthetic design evidence only toward future Spec 15 §7/§8,
FR-DOC-011..018, FR-DOC-020..021 and FR-PROV boundaries. It is not a passing live P11-D acceptance
criterion. AC-P11-001..011 remain NOT VERIFIED for live use.
The P11 gate matrix remains 0 APPROVED / 5 OPEN / 4 BLOCKED; P10 live clinician gates remain 0/9;
P8-C/P9-C Stage 3 restrictions remain in force. The reviewed P11-D head
`963f5e11eccec4d1ef7a80386ae49f61833bc28e` was merged in PR #35 at main
`f71662322b27ec79004745ec6217283887700ac8` with no tree differences. Do not infer live approval.
```

---

# 53. Pre-P11-E Source-Access and UI Readiness Design

```text
Work unit: Pre-P11-E — documentation/readiness design only
Status: DOCUMENTATION COMPLETE — INDEPENDENT REVIEW PENDING; P11-E NOT STARTED
Baseline: main @ f71662322b27ec79004745ec6217283887700ac8
Deliverable: P11_E_SOURCE_ACCESS_AND_UI_READINESS_DESIGN.md records the as-built synthetic
P11-A/B/C/D evidence, all nine unchanged P11 gates and owners, future request-by-request source
authorization/nonenumeration boundaries, conceptual patient/clinician states, preview/accessibility
security prerequisites, requirement traceability, conditional sequencing and a manual evidence
ledger. It grants no approval or runtime capability.
Repository truth: P11-D PR #35 is merged at the baseline; reviewed head
963f5e11eccec4d1ef7a80386ae49f61833bc28e is tree-equivalent. Documents remains absent from
FastAPI composition and has no route, ORM/table/migration, object-store binding, worker/provider,
upload/status/source API or clinical extractor. Patient /documents remains unavailable and
clinician-web remains a foundation shell. Alembic remains p7a_0007.
Gate truth: P11 live remains 0/9 approved (5 OPEN, 4 BLOCKED), P10 live remains 0/9 approved, and
every P8-C/P9-C Stage 3 restriction remains in force. AC-P11-001..011 remain NOT VERIFIED live.
Scope: documentation only. No application/test code, API/OpenAPI, BFF/UI, schema/migration,
dependency/lockfile, Docker/CI, provider/model/storage, identity/consent/assignment, policy or runtime
activation changed. P11-E is not started or implemented.
Next action: independent review with accountable architecture, security, privacy/legal, clinical,
accessibility, data-governance, operations and institutional owners. Unknown consent, source
authority, retention, IdP, assignment or clinical-claim requirements are hard STOP conditions.
```

---

# 54. P11-A Architecture, Privacy and Security Approval-Readiness Package

```text
Work unit: P11-A approval-readiness documentation only
Status: DOCUMENTATION PREPARED — HUMAN DECISIONS PENDING; NO LIVE P11-A APPROVAL
Baseline: main @ fc662ff8c99ad9a314d53a084213d6542f4f9dde
Deliverable: PRE_P11_E_ARCH_PRIVACY_TECH_ASSESSMENT_AND_DECISION_TEMPLATE.md consolidates the
current P11-A evidence, ownership/consent decisions, upload/file-security controls, private-storage
and retention decisions, PostgreSQL/processing architecture review, accountable reviewers,
acceptance evidence, adversarial negative tests and unsigned human decision records.
Repository truth: P11-A/B/C/D remain synthetic engineering-only foundations. No document route,
ORM/table/migration, real upload, file scanner, object-store binding, durable document worker,
provider, source viewer, clinical extractor, or patient/clinician workflow was added. Alembic remains
p7a_0007.
Gate truth: P11 remains 0/9 approved (5 OPEN, 4 BLOCKED); P10 live remains 0/9 approved; P8-C and
P9-C Stage 3 remain blocked. AC-P11-001..011 remain NOT VERIFIED for live use.
Missing governing artifacts: canonical 27_SECURITY_ARCHITECTURE.md and 28_THREAT_MODEL.md are absent;
the package requires P11-specific threat/security/privacy/data-flow and retention decisions before
live implementation.
Scope: documentation only. No approval was granted or inferred, and no runtime, schema, dependency,
infrastructure, clinical, privacy-policy, identity, consent, storage, worker, API or UI change was
made.
Next action: accountable human owners must review and record gate 1-4 and gate 9 decisions, including
population/purpose/consent, upload pattern and limits, quarantine/scanner, storage/encryption/region,
retention/deletion, schema/idempotency/transactions, durable processing, incident and rollback.
```

---

# 55. Pre-P11-A Security, Threat and Privacy Drafts

```text
Work unit: PRE-P11-A-SECURITY-PRIVACY-DRAFTS — documentation/review preparation only
Status: P11-FOCUSED DRAFTS PREPARED — HUMAN REVIEW REQUIRED; NO LIVE P11 APPROVAL
Baseline: main @ 2b2d9036c7fe9941bc90bb55d4130dabb6571263
Deliverables: 27_SECURITY_ARCHITECTURE.md, 28_THREAT_MODEL.md and
P11_PRIVACY_DATA_FLOW_ASSESSMENT_DRAFT.md distinguish as-built technical primitives from future,
unapproved controls; map trust/data flows, actor and authority boundaries, threat/control registers,
adversarial tests, privacy lifecycle, accountable reviewers and unsigned human decisions.
Scope boundary: the platform-numbered security and threat files cover P11 only. Platform-wide
security/threat coverage remains pending. The privacy document is a draft assessment, not legal
advice, a completed DPIA, a DPDP compliance assertion, privacy approval or release authorization.
Repository truth: P11-A/B/C/D remain synthetic engineering-only and unregistered. No document ORM,
migration, route, upload, scanner, production object-store binding, durable document worker, real
OCR/provider, medical extraction, source viewer, clinician workflow or P11-E UI was added. Alembic
remains p7a_0007 and the patient /documents route remains unavailable.
Gate truth: P11 remains 0/9 approved (5 OPEN, 4 BLOCKED); P10 live remains 0/9 approved; P8-C and
P9-C Stage 3 remain blocked. AC-P11-001..011 remain NOT VERIFIED for live use. P7 deterministic
manual intake remains the supported fallback.
Decisions still pending: allowed population/purpose/uploader; document consent/notice/lawful basis;
upload pattern, formats and measured limits; scanner/quarantine/sandbox; storage provider, region,
IAM, encryption and key custody; retention, deletion, legal hold and backup; metadata/idempotency/
transaction/outbox and durable-processing design; provider/egress/benchmark; source preview and
clinician assignment; clinical reviewer authority; incident, pilot, monitoring, rollback and release.
No approval, vendor, region, quota, retention value, lawful basis, population or signature was
invented. Next action is accountable human review and governed decision records for gates 1–4 and 9;
do not begin live P11-A/P11-E or another implementation phase from these drafts.
```

---

# 56. Pre-P12 Multilingual Speech Specification and Readiness Pack

```text
Work unit: Pre-P12 — documentation/governance readiness only
Status: DOCUMENTATION DRAFT COMPLETE — INDEPENDENT/HUMAN REVIEW PENDING; P12 NOT STARTED
Baseline: main @ 3492481a45e7aae068b521eed555ba829559da77
Repository lineage: P11 security/threat/privacy documentation PR #38 merged at baseline main;
reviewed head f2b771761d724c65bcc5140a090e85dff531d9ed is tree-equivalent (files=[]).
Deliverables: 16_MULTILINGUAL_SPEECH_SPEC.md and P12_READINESS_GATE_REVIEW.md record the as-built
P6/P7 evidence, provider-neutral future design, English/Hindi/Hinglish semantics, source lineage,
privacy/egress and accessible fallback requirements, benchmark evidence needs, FR-LANG-001..012 and
AC-P12-001..009 traceability, proposed unapproved human gates, negative tests and STOP conditions.
Repository truth: only English/Hindi session preference, P7 manual text/touch original-text metadata,
disabled speech configuration and empty speech/translation adapter placeholders exist. No language
module, microphone/audio capture, STT/TTS/translation/transliteration/LID adapter, provider/model,
voice API/BFF/UI, locale pack, persistence or migration was added. Alembic remains p7a_0007.
Scope: documentation only. No code/tests, dependency/lockfile, provider/network/benchmark, model,
audio/data, schema/migration, API/OpenAPI/BFF/UI, locale asset, consent policy, Docker/CI/infra,
feature flag, clinical copy, accepted ADR or runtime activation changed.
Governance: all P12 live acceptance remains NOT VERIFIED. P11 security/threat documents remain
P11-FOCUSED DRAFTS; P11 remains 0/9 approved (5 OPEN, 4 BLOCKED), P10 remains 0/9 approved,
P8-C/P9-C Stage 3 remain blocked, P11-E remains unimplemented, and P7 manual intake remains the
supported fallback.
Next action: independent review by accountable privacy/legal, security, architecture, clinical,
language, accessibility/content, operations and product/institution owners. This pack does not
authorize P12-A or any live speech/language work.
```

---

# 57. Pre-P13 Provider Routing Policy and Readiness Pack

```text
Work unit: Pre-P13 — documentation/review preparation only
Status: DRAFT DOCUMENTATION PREPARED — ACCOUNTABLE HUMAN REVIEW REQUIRED; P13 NOT STARTED
Baseline: main @ 568ad42047d6671971a9de3834c47b9de0687641
Repository lineage: Pre-P12 PR #39 merged at the baseline; reviewed head
36baaf4ef3687083b2e389579cfacaab17d10413 is tree-equivalent (files=[]).
Deliverables: 11_PROVIDER_ROUTING_POLICY.md and P13_READINESS_GATE_REVIEW.md distinguish provider,
resource, specialty, facility, contact, referral, notification, clinical-safety and source authority;
propose unapproved source/freshness, specialty-first, consent/minimization, state/idempotency,
failure, security/privacy/accessibility boundaries; and map all P13 requirements and acceptance.
Repository truth: providers, resources and referrals remain placeholder-only and unregistered. No
verified source, provider/resource record, routing policy, table/migration, API/BFF/UI, adapter,
referral/notification side effect, admin workflow, or runtime activation exists. Patient referrals
remain honestly unavailable; generic urgent-help navigation and P7 manual intake remain available.
Alembic remains p7a_0007. The ai_orchestration providers.py file is LLM adapter infrastructure, not
a clinician/provider directory.
Readiness truth: eight proposed P13 gates are an unapproved review inventory, not an official gate
count or approval model. Every FR-DIR-001..017, FR-REF-001..013, applicable FR-NOTIF-001..006,
FR-AUDIT-002..004, PRIV-001..009 and AC-P13-001..011 remains LIVE NOT VERIFIED for P13.
Governance: no clinical taxonomy/rule, real provider/resource truth, consent/sharing basis, source,
contact, external send, notification, pilot or production approval is granted. P12 runtime remains
NOT STARTED; P11 remains 0/9 approved (5 OPEN, 4 BLOCKED); P10 remains 0/9 approved; P8-C/P9-C
Stage 3 remain blocked. P13 remains NOT STARTED.
Missing prerequisite: 25_ADMIN_PORTAL_SPEC.md remains absent and must be created/reviewed separately
before relevant P13-E governance/admin work. This work does not authorize P13-A/B/C/D/E.
Next action: independent review by accountable clinical, source-governance, privacy/legal, security,
identity, architecture, accessibility/content, operations and institutional owners; record explicit
decisions before issuing any separately scoped P13 implementation prompt.
```

---

# 58. Pre-P13 Admin Portal Specification and Readiness Pack

```text
Work unit: PRE-P13-ADMIN-GOVERNANCE-DESIGN — documentation/review preparation only
Status: UNAPPROVED DRAFTS PREPARED — ACCOUNTABLE HUMAN REVIEW REQUIRED; NO LIVE ADMIN AUTHORIZATION
Baseline: main @ af32d98061b4605d405e954de5cde3d380974d8e
Repository lineage: Pre-P13 provider-routing PR #40 merged at the baseline; reviewed head
212a6765e2e6b6450591a70498b0924ef6281d0b is tree-equivalent (files=[]).
Deliverables: 25_ADMIN_PORTAL_SPEC.md and PRE_P13_ADMIN_PORTAL_READINESS_REVIEW.md distinguish
as-built P4 identity/authorization primitives and the empty admin-web shell from future P13-E and
P21-A/B/C/D ownership. They propose unapproved source governance, scoped authorization,
maker-checker, referral/notification visibility, audit/privacy, accessibility, operations, negative
tests, accountable roles, unsigned decisions and STOP conditions.
Repository truth: production authentication remains unconfigured. No admin API, provider/resource/
referral/notification/audit module or record, moderation workflow, clinical review queue, audit
viewer, source verifier, real provider data, external side effect, or P13-E/P21 runtime was added.
Alembic remains p7a_0007; accepted ADRs and dependencies are unchanged.
Requirement truth: FR-ADMIN-001..010, FR-AUDIT-001..007, AC-P21-001..008 and applicable
AC-P13-001..011 remain LIVE NOT VERIFIED. Drafting Spec 25 addresses only the missing-document
artifact in proposed P13 Gate 7; roles, identity, copy, source warnings, accessibility, privacy,
implementation and accountable review remain blocked. P13's original eight proposed gates remain
4 OPEN and 4 BLOCKED, and P21 has no human-approved gate count.
Governance: P13 and P12 runtime remain NOT STARTED; P21 remains NOT STARTED; P11 remains 0/9
approved (5 OPEN, 4 BLOCKED); P10 live remains 0/9 approved; P8-C/P9-C Stage 3 remain blocked.
No clinical, privacy, security, source-verification, policy/model/content, pilot, production, consent,
referral-sharing, export, retention, break-glass or release approval was granted or inferred.
Scope: documentation only. No application/test code, API/OpenAPI, role/policy/consent behavior,
schema/migration, dependency/lockfile, Docker/CI/infrastructure, feature flag, source ingestion,
provider contact, clinical copy, notification, referral send, UI component or runtime changed.
Next action: accountable identity/security, privacy/legal, source-governance, clinical, audit/data,
accessibility/content, operations, application and institution owners must independently review and
record decisions before any separately scoped P13-E or P21 implementation prompt.
```

---

# 59. Pre-P14 MannSetu Mental-Health Policy Framework and Readiness Pack

```text
Work unit: Pre-P14 — documentation and accountable-review preparation only
Status: PRE-P14 DRAFT — CLINICAL POLICY/SAFETY/PRIVACY REVIEW PENDING; NO ACTUAL CLINICAL RULES OR RUNTIME APPROVAL
Baseline: main @ 8a313aabab31bffbbddfa3d94b79aa045cc7a19c
Repository lineage: Pre-P13 admin-portal PR #41 merged at the baseline; reviewed head
5f81e9440ab0c6b1d965ecf952e194ac56001035 is tree-equivalent (files=[]).
Deliverables: 09_MENTAL_HEALTH_POLICY.md and P14_READINESS_GATE_REVIEW.md separate as-built evidence
from future design, audit the historical MannSetu source PDFs without adopting their clinical
proposals, map FR-MH-001..020 and AC-P14-001..013, preserve global safety/privacy/accessibility and
P8/P9/P10/P11/P12/P13/P21 restrictions, identify accountable reviewers and unsigned decisions, and
define conditional STOP criteria and adversarial evidence requirements.
Repository truth: P14 module, clinical-policy, safety-corpus, provider/resource/referral and
notification directories remain placeholders; no clinically approved route policy, instrument,
signal extractor, independent backstop, crisis protocol/copy/resource registry, referral workflow,
P14 API/BFF/UI, persistence or migration exists. Generic urgent-help navigation and P4 pseudonymous
session/consent primitives are not P14 approval or implementation. Alembic remains p7a_0007.
Governance: P14 remains NOT STARTED. No threshold, lexicon, clinical rule, crisis contact, patient
copy, retention period, instrument use, route eligibility, pilot, production or human approval is
created or inferred. P13 referral sharing still requires explicit active purpose-specific
REFERRAL_SHARING consent plus all additionally applicable lawful/governance requirements. P12/P13/P21
runtime remain NOT STARTED; P11 remains 0/9 approved; P10 live remains 0/9 approved; P8-C/P9-C Stage 3
remain blocked.
Scope: documentation only. No runtime/test code, API/OpenAPI, database/schema/migration, dependency,
lockfile, Docker/CI/infrastructure, feature flag, provider/model, content, clinical data, external
side effect or accepted ADR changed.
Next action: accountable clinical, safety, privacy/legal, security, language, accessibility/content,
operations, referral/resource, architecture/data and institutional owners must independently review
the evidence and record explicit decisions before any separately scoped P14 implementation prompt.
```

---

# 60. October 2026 Next.js Security Remediation

```text
Work unit: SECURITY-NEXTJS-2026-10 — dependency security repair only
Status: SECURITY PATCH PREPARED — INDEPENDENT REVIEW REQUIRED; NO PLATFORM/PRODUCTION APPROVAL
Baseline: main @ 747110bcbecaeb3484fddf68b2eec9038fd43ce1
Change: patient-web, clinician-web and admin-web pin Next.js 16.4.2 instead of 16.4.0; root
eslint-config-next is aligned at 16.4.2. The pnpm 9.15.4 lockfile resolves the matching Next.js,
@next/env, ESLint-plugin and platform SWC family; sharp remains 0.35.5 and React/React DOM remain
19.3.0. No unrelated direct dependency, application behavior, API, schema, migration or CI changed.
Security evidence: GHSA-673q-mjm6-r5xr, GHSA-2464-fhr4-w9xw / CVE-2026-96889 and
GHSA-p3m5-59mp-jv5r no longer appear after the exact stable patch. The unrelated unpatched
braces@3.0.3 development-tooling advisory remains explicitly recorded for separate review.
Verification: frozen install, frontend format/lint/typecheck, 145 frontend tests, all three production
builds, backend quality with 1,238 non-PostgreSQL tests, 97 real-PostgreSQL tests, Alembic checks at
p7a_0007, 13 Playwright journeys, and a cached local Trivy production-dependency scan passed. Two
Playwright journeys required their configured retry after local parallel startup/navigation timeouts;
no test was changed. Exact final commit and six-job CI results are authoritative in the PR/report.
Governance: engineering-only remediation, not P22 completion or privacy/security/clinical/release
approval. P7 manual intake remains the fallback; P8-C/P9-C Stage 3 remain blocked; P10/P11 live
remain 0/9 approved; P12/P13/P14/P21 runtime remain NOT STARTED. Alembic and accepted ADRs are
unchanged. Next action is independent review of the narrowly scoped security patch; do not activate
blocked functionality or begin clinical implementation from this branch.
```

---

# 61. Pre-P15 Self-Care / Ayurveda Policy and RAG Knowledge Readiness Pack

```text
Work unit: PRE-P15-SELFCARE-RAG-SPEC — documentation and accountable-review preparation only
Status: DRAFT — ACCOUNTABLE CLINICAL/SOURCE/PRIVACY/ARCHITECTURE REVIEW PENDING; NO P15 RUNTIME APPROVAL
Baseline: main @ bfba7f5a5993c1572c5ad18b942013a0badc3495
Repository lineage: October 2026 Next.js security-remediation PR #43 merged at the baseline; its
merge tree is identical to reviewed head 18e1480c9699cd0fbecb9162eedc045fe7ef9037.
Deliverables: 10_SELF_CARE_AYURVEDA_POLICY.md defines an unapproved process/architecture framework;
17_RAG_KNOWLEDGE_SPEC.md defines an unapproved platform retrieval design with a bounded P15 scope;
P15_SELF_CARE_RAG_READINESS_GATE_REVIEW.md records descriptive OPEN/BLOCKED review domains,
accountable roles, unsigned decisions, negative evidence, dependencies and STOP conditions without
creating an official gate count or granting approval.
Repository truth: the self-care module and relevant knowledge/policy paths remain placeholders. No
approved remedy, source, knowledge pack, eligibility/contraindication rule, patient-facing copy,
retrieval corpus, embedding model/provider, pgvector schema, RAG service, API, UI, runtime
registration, feature flag or production workflow exists. P15 remains NOT STARTED and all
FR-SELF-001..017 / AC-P15-001..010 live outcomes remain NOT VERIFIED. Any separately authorized
future engineering fixture must remain synthetic, unmistakably non-production and isolated.
Governance: P7 manual text/touch intake remains supported; P8-C/P9-C Stage 3 remain BLOCKED; P10 and
P11 live remain 0/9 APPROVED, with P11 five OPEN/four BLOCKED; P12/P13/P14/P15/P21 runtime remain
NOT STARTED; P13's eight proposed/unapproved gates remain four OPEN/four BLOCKED; P14 and P15 have
no official gate count; P22 is not complete. Accepted ADRs and Alembic p7a_0007 remain unchanged.
Existing general-product/clinical-intake consent does not authorize P15 or retrieval using patient
data. No clinical, source/content-rights, safety, privacy/legal/consent, security, language,
accessibility, provider, model/index, pilot, production or release approval was granted or inferred.
Scope: documentation only. Next.js 16.4.2 and root eslint-config-next 16.4.2 remain pinned. No app,
backend, test, schema/migration, dependency/lockfile, CI, Docker/infrastructure or accepted ADR changed.
STOP/next action: accountable clinical/safety, source/rights, privacy/legal, security, architecture/
data, language/accessibility, operations, P13 navigation, P21 governance and institutional owners
must independently review and sign bounded decisions before any separately prompted P15-A/B/C/D/E
work. Missing or disputed evidence fails closed; do not activate patient-facing guidance or RAG.
```

---

# 62. Pre-P16 FHIR Mapping Specification and Readiness Pack

```text
Work unit: PRE-P16-FHIR-MAPPING-DESIGN — documentation and accountable-review preparation only
Status: DRAFT — ACCOUNTABLE ARCHITECTURE, CLINICAL, PRIVACY, SECURITY AND INTEROPERABILITY REVIEW PENDING; NO LIVE P16 APPROVAL
Baseline: main @ 34b3e17df672c68e9677ca3ae88bf07c7711ea0c
Repository lineage: PR #45 merged at the baseline; its merge tree is identical to reviewed head
a0a1fb9b6eaf34ac31de5c0f70f2d59ee47cb27c. Superseded PR #44 was closed and not merged.
Deliverables: 20_FHIR_MAPPING_SPEC.md records the unapproved FHIR R4 4.0.1 mapping, provenance,
validation, privacy, security and adapter-boundary design. P16_READINESS_GATE_REVIEW.md records eight
proposed review areas, accountable roles, unresolved decisions, negative tests, STOP conditions and
an unsigned decision template without creating an official P16 gate count.
Repository truth: internal PostgreSQL/domain records remain canonical. FHIR is a replaceable
interoperability projection. Empty FHIR module/adapter placeholders remain unchanged; no mapper,
validator, HAPI sidecar, remote client, profile/terminology package, endpoint, credential, API,
import/export route, feature flag, persistence or migration exists. Alembic remains p7a_0007 and
Next.js remains pinned at 16.4.2.
Traceability: FR-FHIR-001..011 and AC-P16-001..010 are mapped to the draft sections, current evidence
and future human/technical artifacts. Every live outcome remains NOT VERIFIED. P16-A DTO/mapping,
P16-B validation/gateway and P16-C export/import APIs/tests are separately scoped, gated and NOT
STARTED. FR-ABDM-001..007 and AC-P17-001..007 remain P17 dependencies, not P16 evidence;
21_ABDM_INTEGRATION_SPEC.md remains absent and P17 remains NOT STARTED.
Governance: FHIR validity does not establish clinical truth, patient authorization or recipient
eligibility. General-product/clinical-intake consent does not authorize FHIR or ABDM exchange;
REFERRAL_SHARING applies independently to actual external referrals. No patient data, clinical
mapping, source identity, profile, vendor, destination, lawful authority or approval was invented.
P7 manual text/touch intake remains unchanged; P8-C/P9-C Stage 3 remain BLOCKED; P10/P11 live remain
0/9 approved; P12/P13/P14/P15/P16/P17/P21 runtime remain NOT STARTED; P15 STOP conditions remain.
Scope: documentation only. No runtime, test fixture, schema/ORM, migration, dependency/lockfile, CI,
Docker/infrastructure, network, accepted ADR, consent/policy or unrelated source file changed.
STOP/next action: architecture/interoperability, clinical/terminology, privacy/legal/consent,
security, identity/authorization, institutional/partner, data-governance, operations and release
roles must independently review and record bounded decisions. Only a new explicit prompt from a
current baseline may authorize a permitted synthetic/offline P16 subset. Do not begin P16-A/B/C,
P17, real patient exchange, HAPI deployment, profile acquisition or production integration.
```

---

# 63. Pre-P17 ABDM / ABHA Integration Specification and Readiness Pack

```text
Work unit: PRE-P17-ABDM-ABHA-GOVERNANCE-READINESS — documentation and accountable-human-review preparation only
Status: DRAFT — OFFICIAL ABDM/ABHA, ARCHITECTURE, IDENTITY, CLINICAL, PRIVACY, SECURITY, PARTNER AND LEGAL REVIEW PENDING; NO LIVE P17 APPROVAL
Baseline: main @ 3c727c6015d7e5c4dd8b3a96b0b64796da00eeed
Repository lineage: PR #46 merged at the baseline; its merge tree is identical to reviewed head
110811c77d94ba7cd5dd49ba400c490eace403c6.
Deliverables: 21_ABDM_INTEGRATION_SPEC.md is an unapproved adapter, identity, consent, FHIR,
environment, transport, provenance, security, accessibility and incident-boundary proposal.
P17_READINESS_GATE_REVIEW.md records eight descriptive OPEN/BLOCKED review areas, accountable roles,
missing official evidence, negative tests, STOP conditions, an owner/risk register and unsigned
decision template without inventing an official P17 gate count or approval.
Repository truth: FHIR Spec 20 remains an unapproved Pre-P16 draft; FHIR and ABDM module/adapter
paths remain placeholders. No current official ABDM/ABHA protocol version, operating role, endpoint,
identity flow, consent-manager contract, profile/package, sandbox, partner, credential, callback,
mapper, validator, HAPI sidecar, API, persistence, feature flag or data exchange is implemented,
verified or approved. Historical R2-C material is not adopted as current official authority.
Traceability: exact FR-ABDM-001..007 and AC-P17-001..007 wording is mapped to draft sections,
baseline evidence and future official/human/technical artifacts. Every live P17 outcome remains NOT
VERIFIED; creating an unapproved Spec 21 does not satisfy AC-P17-001. FR-FHIR-001..011 and
AC-P16-001..010 remain unmet prerequisites. P17-A/B/C/D and P16-A/B/C remain NOT STARTED.
Governance: P4 pseudonymous identity, internal patient identity and external ABHA identity are not
interchangeable. GENERAL_PRODUCT_USE/clinical_intake consent is not ABDM authority; a typed
ABDM_EXCHANGE purpose is vocabulary, not approval; REFERRAL_SHARING remains independently mandatory
for actual referral disclosure and is not universal ABDM consent. No identifier, patient data,
clinical mapping, government role, legal basis, protocol detail, partner commitment or approval was
invented. P7 manual intake and generic urgent help remain independent and unchanged.
Upstream status: P8-C/P9-C Stage 3 remain BLOCKED; P10/P11 live remain 0/9 approved; P12/P13/P14/
P15/P16/P17/P21 runtime remain NOT STARTED; P15 STOP conditions remain. P11 draft security/privacy
materials are not general platform or production approval.
Scope: documentation only. Alembic remains p7a_0007; Next.js and root eslint-config-next remain
16.4.2. No runtime/test code, API, payload/fixture, schema/ORM/migration, dependency/lockfile, CI,
Docker/infrastructure, network, configuration, accepted ADR, consent/policy or unrelated file changed.
STOP/next action: qualified ABDM, architecture/interoperability, identity, clinical/terminology,
privacy/legal/consent, security, institutional/partner, accessibility/language, operations/incident
and release roles must independently verify current official sources and record bounded decisions.
Do not begin P16/P17 implementation, acquire a profile, provision a sandbox/credential, expose a
callback, create patient flows or send data without an approved Spec 21 and separate phase prompt.
```

---

# 64. Pre-P18 Classical ML Research Specification and Readiness Pack

```text
Work unit: PRE-P18-CLASSICAL-ML-RESEARCH-READINESS — documentation and accountable-human-review preparation only
Status: DRAFT — RESEARCH DATASET/TASK, PRIVACY, BENCHMARK AND MODEL-GOVERNANCE REVIEW PENDING; NO P18 RUNTIME OR CLINICAL APPROVAL
Baseline: main @ 0b1eeaf470e129a29f18426ab9a0c4c115fbb4ac
Repository lineage: PR #47 merged at the baseline; its merge tree is identical to reviewed head
c5d241c10843af776860d06437fc1ecb09cabc11.
Deliverables: 18_CLASSICAL_ML_SPEC.md defines a research-only architecture, dataset-admission,
split/leakage, evaluation, reproducibility, artifact-security, model-governance and P19 parity draft.
P18_READINESS_GATE_REVIEW.md records eight descriptive OPEN/BLOCKED review domains, accountable
roles, evidence and decisions, negative tests, STOP conditions, an owner/risk register and unsigned
decision template without inventing an official gate count or approval.
Repository truth: ml/classical, ml/datasets, ml/evaluation, ml/registry, ml/quantum,
backend/app/modules/ml and backend/app/adapters/quantum remain placeholders. No approved dataset,
task, target, label, population, real benchmark, split, experiment, training pipeline, tracking or
registry service, model card, artifact, inference path or P19 comparator was created. P18-A/B/C/D/E,
P18 runtime and P19 runtime remain NOT STARTED. All FR-ML-001..017 and AC-P18-001..010 live outcomes
remain NOT VERIFIED; a future synthetic exercise cannot satisfy AC-P18-001 for a real benchmark.
Human decisions: qualified research, clinical/epidemiology, data-custody, privacy/legal/ethics,
security, architecture/data, biostatistics/ML-validation, model-governance, operations/release and
institutional owners must decide the task, dataset/license/custody, legal authority, split,
preprocessing, metrics, calibration, artifact policy, lifecycle mapping, P19 parity and release.
Governance: P7 deterministic/manual intake and urgent help remain independent. P8-C/P9-C Stage 3
remain BLOCKED; P10/P11 live remain 0/9 approved, with P11 five OPEN/four BLOCKED; P12/P13/P14/P15/
P16/P17/P18/P19/P21 runtime remain NOT STARTED; P15 clinical/source STOP conditions remain; P16
FHIR and P17 ABDM are not authorized; P22 is NOT COMPLETE. Research and model output cannot become
diagnosis, confirmed clinical/FHIR truth, hard-safety override, pilot approval or production authority.
Provenance and safe-off: future inputs, runs, transformations, metrics, artifacts, calibration and
approvals require immutable lineage. Missing/invalid/expired evidence fails closed; P7/P9 remain
available when research, MLflow, model inference or QML is absent or fails. No quantum advantage is
claimed, and a P19 comparison requires the same future approved P18 target, splits and metrics.
Scope: documentation only. Alembic remains p7a_0007; Next.js and root eslint-config-next remain
16.4.2. No runtime/test code, dataset/download, experiment/training, dependency/lockfile, model,
artifact, schema/ORM/migration, API/UI, service, Docker/CI/infrastructure, accepted ADR, clinical
threshold, consent/policy or unrelated file changed.
Future work and STOP: safe synthetic-only mechanics require a new narrow prompt. Do not begin P18-A/
B/C/D/E, select or access data, activate research infrastructure, train/register/load a model, start
P19, pilot or release until all applicable accountable decisions and independent evidence are current.
```

---

# 65. Pre-P19 Hybrid Quantum ML Specification and Readiness Pack

```text
Work unit: PRE-P19-HYBRID-QML-GOVERNANCE-READINESS — documentation and accountable-review preparation only
Status: DRAFT — P18 CLASSICAL BASELINE, QML BENCHMARK, PRIVACY, SECURITY AND MODEL-GOVERNANCE REVIEW PENDING; NO P19 RUNTIME OR CLINICAL APPROVAL
Baseline: main @ 9ed502ceb4973d6cb95e3a85828699be1cd31ee3
Repository lineage: PR #48 merged at the baseline; its merge tree is identical to reviewed head
32b57631bd37ce6f53db1b8098589c45e6304ee6.
Deliverables: 19_QUANTUM_ML_SPEC.md records the prospective parity, quantum-port, simulator/hardware,
hybrid-design, reproducibility, evaluation, artifact, privacy, safety and governance boundaries.
P19_READINESS_GATE_REVIEW.md records eight descriptive OPEN/BLOCKED domains, accountable roles,
negative tests, STOP conditions, an owner/risk register and unsigned decision template without
creating an official gate count or human signoff.
Repository truth: P18 Spec 18 and readiness inventory remain unapproved drafts. P18 has zero actual
baselines: no approved task, dataset, frozen split, classical result, tracker, artifact or model.
ML/QML and quantum-adapter paths remain placeholders. No port, dependency, circuit, simulator, QPU,
experiment, training, inference, model, chart, performance result or quantum-advantage claim was
created. P18-A/B/C/D/E and P19-A/B/C/D/E remain NOT STARTED.
Traceability: exact FR-QML-001..018 and AC-P19-001..009 wording maps to draft sections, as-built
evidence and missing human/technical decisions. Every live P18 and P19 criterion remains NOT
VERIFIED; AC-P19-001 cannot pass without an approved reproducible P18 target and split. SHOULD and
MAY requirements remain conditional and are not upgraded to SHALL.
Human decisions: P18/P19 research, clinical/epidemiology, biostatistics/ML validation, data custody,
privacy/legal/ethics, security, architecture, dependency/license, model governance, operations/
incident/release, institutional and independent-review roles must separately decide task, data,
parity, research design, metrics, uncertainty, resource budget, artifacts, egress and release.
Governance: research is isolated and safe-off. P7 deterministic/manual intake and generic urgent
help remain available; P8-C/P9-C Stage 3 remain BLOCKED; P10/P11 live remain 0/9 approved, with P11
five OPEN/four BLOCKED; P12/P13/P14/P15/P16/P17/P18/P19/P21 runtime remain NOT STARTED; P15
clinical/source STOP conditions remain; P16/P17 runtime is unauthorized; P22 is NOT COMPLETE.
Quantum output cannot become diagnosis, confirmed clinical/FHIR truth, safety override, registry
promotion, pilot approval or production authority. PennyLane/Qiskit remain inactive research
candidates; simulator and hardware evidence are not interchangeable.
Scope: exactly four documentation paths. Alembic remains p7a_0007; Next.js and root
eslint-config-next remain 16.4.2. No application/test code, fixture, dataset/download, notebook,
dependency/lockfile, experiment, model/artifact, schema/ORM/migration, API/UI, feature flag,
Docker/CI/infrastructure, accepted ADR, credential, clinical threshold or unrelated file changed.
STOP/next action: accountable owners must first approve and reproduce a P18 baseline, then record
P19 purpose/parity, isolated research architecture, privacy/security/artifact, claim, incident and
release decisions. Only a new narrow prompt may begin P19-A. Do not start P18 engineering, P19-A/B/
C/D/E, P20, simulator/hardware work, dataset use, training, inference, claims, pilot or production.
```

---

# 66. Pre-P20 Unified Care Orchestration Specification and Readiness Pack

```text
Work unit: PRE-P20-UNIFIED-CARE-ORCHESTRATION-READINESS — documentation and accountable-review preparation only
Status: DRAFT — REVIEW ONLY; NO ACTIVATED CARE ORCHESTRATOR, PATIENT JOURNEY, CLINICAL POLICY OR P20 AUTHORIZATION
Baseline: main @ ec141d4e6c4d843a6d1868e77751bdd30aa01ce0
Repository lineage: PR #49 merged at the baseline; its merge tree is identical to reviewed head
77a88a433ec4620e86aa8e3242fdfee8c5c7db2c.
Deliverables: P20_UNIFIED_CARE_ORCHESTRATION_SPEC.md records current P7 truth, blocked upstream
modules, non-executable typed composition vocabulary, independent safety channels, provenance/time/
consent constraints, source authority, safe degradation, a future journey inventory and test matrix.
P20_READINESS_GATE_REVIEW.md records eight descriptive, unsigned OPEN/BLOCKED review areas,
accountable roles, missing decisions, evidence, negative tests and human STOP conditions. These are
not an official gate count and do not record approval.
Traceability: AC-P20-001..010 are live P20 acceptance criteria and remain LIVE NOT VERIFIED.
AC-PROD-001..014 are distinct eventual product-level outcomes and remain PRODUCT-LEVEL NOT VERIFIED.
FR-CORE-001..010 and SAFE-001..010 are mapped verbatim; impacted domain families and accepted ADRs
remain controlling. Existing P7 evidence does not prove P20 or any blocked product outcome.
Repository truth: there is no care composer, P20 module, new route, API, BFF, patient/clinician UI,
policy, registry, source approval or runtime activation. P20-A/B/C/D and P20 runtime remain NOT
STARTED. P7 deterministic/manual text/touch intake remains the functioning patient path.
Governance: P8-C/P9-C Stage 3 remain BLOCKED; P10/P11 live remain 0/9 approved, with P11 five OPEN/
four BLOCKED; P12–P19 and P20/P21 runtime remain NOT STARTED; P15 clinical/source STOP conditions
remain; P16/P17 exchange is unauthorized; P18 has no approved benchmark and P19 no comparator; P22
is NOT COMPLETE. No clinical/safety/privacy/product/architecture/release approval was invented.
Scope: exactly four documentation paths. Alembic remains p7a_0007; Next.js and root
eslint-config-next remain 16.4.2. No runtime, test, fixture, schema/ORM/migration, API/UI, dependency/
lockfile, accepted ADR, Docker/CI/infrastructure, feature flag, clinical content or unrelated file
changed.
STOP/next action: accountable reviewers must resolve the applicable upstream policies, purposes,
source authority, independent safety behavior, privacy/security and bounded-release decisions. Only
a new narrow prompt may authorize a minimal P20-A preflight. Do not begin P20-A/B/C/D or P21.
```

---

# 67. Pre-P21 Admin Governance Gate Reconciliation and Owner Decision Docket

```text
Status: COMPLETE — PRE-P21 DECISION RECONCILIATION DOCUMENTATION ONLY; P21 runtime remains NOT STARTED.
Baseline: main @ 06d51e5f29a486c9bc13b6d1d65d5ec82239f2ac, the verified merge commit for PR #50;
reviewed head 8755fcdc48232e9571978aa3b3560bb685c89be3 and the baseline share tree
4f16d8efe306cdc000721e014e4271e30c4a5039.
Existing source of truth: docs/25_ADMIN_PORTAL_SPEC.md and
docs/implementation/PRE_P13_ADMIN_PORTAL_READINESS_REVIEW.md remain the unapproved design/readiness
artifacts. They were reused, not duplicated or overwritten. The new Pre-P21 reconciliation supplies
an accountable decision docket and current repository evidence; it is not a new admin specification.
Review structure: eight descriptive decision domains are recorded for identity/MFA/authorization;
provider/resource source governance; maker-checker/domain authority; P10/P11 clinical/document
source review; referral/notification consent; audit/privacy/retention/export/threat controls; admin
API/BFF/UI/accessibility; and environment/credentials/incidents/P22/P24. Eight is descriptive only,
not an official gate count, approval state, acceptance result or authorization.
Traceability: FR-ADMIN-001..010, FR-AUDIT-001..007 and AC-P21-001..008 are reproduced verbatim and
remain LIVE NOT VERIFIED. AC-P13-001..011 are separately traced. Historical P13 Gate 7's missing-
document artifact is addressed by the existing unapproved Spec 25 draft, but the gate remains
BLOCKED and not human-approved. AC-P20-001..010 and AC-PROD-001..014 are upstream unverified
dependencies only and do not become P21 acceptance evidence.
Governance: P21-A/B/C/D runtime remains NOT STARTED; P13-E remains unimplemented; P7 remains the
functioning deterministic/manual patient path; P8-C/P9-C Stage 3 remain BLOCKED; P10/P11 live remain
0/9 approved, with P11 five OPEN/four BLOCKED; P12–P21 runtime remains NOT STARTED where applicable;
P15 remains blocked; P16/P17 are unauthorized; P18 has no approved baseline; P19 has no approved
comparator; P20 is NOT STARTED; and P22 is NOT COMPLETE. No human, clinical, privacy, security,
consent, source, audit, pilot, production or release approval is invented or granted.
Scope: exactly three documentation paths changed: the new Pre-P21 reconciliation, this minimal
tracker update and the byte-equivalent recorded Codex prompt. No runtime source, test, schema/ORM,
migration, dependency/lockfile, CI, Docker/infrastructure, environment, accepted ADR or existing
Admin Portal Specification changed. Alembic remains p7a_0007 and dependencies remain unchanged.
Human next steps: named accountable identity/security, privacy/legal, source-governance, clinical,
audit/data, accessibility/content, operations, application and institutional owners must review
current evidence and sign narrowly bounded decisions. Missing, stale, disputed or unsigned evidence
fails closed. Only a new narrow prompt may authorize a synthetic nonclinical P21-A preflight; do not
begin P21-A/B/C/D, live admin/clinical review, pilot or production work from this documentation.
```

---

# 68. Pre-P22 Platform Security, Privacy, Retention and Resilience Readiness Pack

```text
Status: COMPLETE — PRE-P22 DOCUMENTATION ONLY; P22 AND P22-A/B/C/D/E REMAIN NOT STARTED.
Baseline: main @ 09200acdf5f824a335781249f6a8e56e47b68fcb, the verified PR #51 merge commit;
reviewed feature head aeaef276de5fa6c8e4b5dc2b0d8fc528b220a473 and baseline share tree
dbfc48e7aa61225823ce8a455a77fc132772e72e.
Existing source hierarchy: Spec 26 remains the P4–P7 privacy baseline; Specs 27/28 remain
P11-FOCUSED DRAFTS and are not a completed platform architecture/threat model; Specs 30/33 retain
their recorded scope; Specs 31/32 remain absent/NOT STARTED. None was overwritten or reclassified.
Deliverables: P22_PLATFORM_SECURITY_PRIVACY_GAP_ASSESSMENT.md records platform trust zones, data
classes, as-built versus proposed evidence, a threat/control delta matrix and a NOT STARTED P22-A–E
backlog. P22_READINESS_GATE_REVIEW.md records eight descriptive OPEN/BLOCKED review domains,
accountable role classes, adversarial evidence, safe-off behavior, an unsigned decision template
and STOP conditions. Eight is descriptive only, not an official gate count or approval arithmetic.
Traceability: AC-P22-001..011, NFR-SEC-001..014, PRIV-001..009, NFR-RES-001..007 and
FR-AUDIT-001..007 are reproduced verbatim and mapped to current evidence and missing decisions.
All AC-P22 criteria remain LIVE NOT VERIFIED. Bounded controls, synthetic tests, CI and scanners do
not establish platform/pilot acceptance. The prior Trivy CVE-2026-107891 metadata warning is
recorded for accountable evidence/DB-freshness review without declaring vulnerability or resolution.
Governance: P7 deterministic manual text/touch intake and generic urgent help remain available;
P8-C/P9-C Stage 3 remain BLOCKED; P10/P11 live remain 0/9 approved, with P11 five OPEN/four BLOCKED;
P12–P21 runtime remains NOT STARTED where applicable; P13 real registry/referral and P14 clinical
routing remain unapproved; P15 STOP remains; P16/P17 live exchange is unauthorized; P18 has no
approved baseline and P19 no comparator; P20/P21 runtime and P23/P24 pilot/release remain NOT STARTED.
Scope: exactly four documentation paths changed: two new P22 review documents, this minimal P22
tracker note/section 68 and the byte-identical recorded prompt. No runtime, tests, API/UI, policy,
schema/ORM/migration, dependency/lockfile, accepted ADR, CI/scanner, Docker/infrastructure,
credential, retention job, kill switch or approval changed. Alembic remains p7a_0007; Next.js and
root eslint-config-next remain 16.4.2.
STOP/next action: qualified identity/institution, security/AppSec, privacy/legal/records, data,
clinical/safety, accessibility/product, platform/SRE/incident, research/interop/vendor and release
owners must review current evidence and sign exact bounded decisions. Only a new separately
authorized P22-A prompt may perform a safe non-invasive threat/authorization audit. Do not begin
P22-B/C/D/E, P23/P24, real patient integration, privileged action, retention execution or release.
```

---

# 69. Pre-P23 E2E Accessibility Reliability Performance Readiness Pack

```text
Status: COMPLETE — PRE-P23 DOCUMENTATION ONLY; P23 AND P23-A/B/C/D REMAIN NOT STARTED.
Baseline: main @ 4f422146962141c7f427ed083fa2b013e6cddf7f, the verified PR #52 merge commit;
reviewed feature head ec9c633f9e330cdd8439d84ec718e54e087752c7 and baseline share tree
1c2d852502797f28fc00402f1a491a36756acf29.
Deliverables: P23_VALIDATION_COVERAGE_AND_EVIDENCE_GAP_ASSESSMENT.md records the current evidence
topology, all 13 browser checks, the canonical 18-journey matrix, accessibility gaps, an unexecuted
performance/recovery design, privacy-safe observability gaps and exact requirement traceability.
P23_READINESS_GATE_REVIEW.md records eight descriptive unsigned OPEN/BLOCKED review domains,
accountable roles, missing decisions, adversarial evidence, safer fallbacks, decision template,
owner/risk register and STOP conditions. Eight is descriptive only, not official approval arithmetic.
Evidence boundary: the 13 Playwright checks are 11 patient checks, one clinician-foundation check
and one admin-foundation check. The real synthetic-data FastAPI/PostgreSQL P7 intake journey is
bounded technical evidence, not 13 medical journeys, full clinical validation or live P23 acceptance.
Human-reviewed accessibility remains incomplete; there is no WCAG certification, approved
multilingual clinical/speech matrix or kiosk deployment review. tests/performance contains only
.gitkeep, so there is no load run, approved workload, threshold or baseline. OTel/request logging,
transactional outbox and process-local jobs are bounded primitives, not production dashboards,
durable worker recovery, exactly-once effects or P23 reliability acceptance.
Traceability: AC-P23-001..012, NFR-TEST-001..014, NFR-ACCESS-001..007, NFR-PERF-001..006 and
NFR-OBS-001..011 are reproduced verbatim and mapped to evidence, missing proof and owners. All
AC-P23 outcomes remain LIVE NOT VERIFIED. AC-PROD-001..014 are separately reproduced and remain
PRODUCT-LEVEL NOT VERIFIED; existing P7 completion is not rewritten. NFR-RES-001..007 are a
separate related-resilience crosswalk.
Governance: Specs 31/32 remain absent/NOT STARTED; Specs 27/28 remain P11-focused drafts. P7 manual
text/touch and generic urgent help remain the bounded patient path; P8-C/P9-C Stage 3 remain BLOCKED;
P10/P11 live remain 0/9 approved, with P11 five OPEN/four BLOCKED; P12–P22 runtime or subphases
remain NOT STARTED where applicable; P13 has no verified registry/referral, P14/P15 policies/content
remain unapproved, P16/P17 exchange is unauthorized, P18 has no approved baseline, P19 has no
comparator, P20/P21 are not started and P22-A/B/C/D/E are not started. P24 remains NOT STARTED.
Scope: exactly four documentation paths changed: the two new P23 review documents, this P23-only
tracker note/section 69 and the byte-identical recorded prompt. No runtime, tests, fixtures, patient
data, load run, telemetry export, API/UI, schema/ORM/migration, dependency/lockfile, accepted ADR,
CI/scanner, Docker/infrastructure, clinical/security/privacy policy, approval, pilot or release changed.
Alembic remains p7a_0007; Next.js and root eslint-config-next remain 16.4.2.
STOP/next action: qualified clinical/safety, accessibility/language, privacy/legal, identity/security,
SRE/incident/performance/observability, product/institution, domain, research/interop, independent QA
and release owners must review exact evidence and sign narrowly bounded decisions. Do not transition
directly to P23 engineering. Only a new separate prompt after applicable gates may authorize a
future P23-A, P23-B, P23-C or P23-D unit; no P24 pilot/release follows from this documentation.
```

---

# 70. Pre-P24 Pilot Release and Operational Readiness Evidence Pack

```text
Status: COMPLETE — PRE-P24 DOCUMENTATION ONLY; P24 AND ALL PILOT, RELEASE AND DEPLOYMENT ACTIVITY
REMAIN NOT STARTED.
Baseline: main @ 4f4a128566635231dd498ae84c79664cbb53a95a, the verified PR #53 merge commit;
reviewed feature head 20a538502701f7aa95255022e89269e42430feae and baseline share tree
eb9f9d11546e91871da41a031076b161a2db76c3.
Deliverables: P24_PILOT_EVIDENCE_AND_RELEASE_SCOPE_ASSESSMENT.md records conditional candidate
scope labels, exact acceptance/research/product traceability, the 13-item pre-pilot document
register, an empty evaluation pre-registration template and unexecuted operational rehearsal
matrix. P24_READINESS_GATE_REVIEW.md records eight descriptive unsigned BLOCKED review domains,
accountable role classes, adversarial evidence, safer fallbacks, an unsigned owner docket,
decision template and STOP conditions. Eight is descriptive only, not an official gate count,
approval arithmetic, risk acceptance, release board decision or pilot authorization.
Evidence boundary: capability inclusion, exclusion and not-applicable labels are undecided until
accountable humans sign an exact environment and population scope. AC-P24-001..013,
NFR-RESRCH-001..005 and AC-PROD-001..014 are reproduced verbatim and remain LIVE NOT VERIFIED or
PRODUCT-LEVEL NOT VERIFIED. P22 and P23 acceptance remains unverified. Existing bounded engineering,
synthetic tests, CI, scanners, 13 browser checks and local infrastructure checks are not clinical,
accessibility, performance, security, privacy, resilience, operational or release acceptance.
Missing evidence: no approved physical/mental clinical policy, multilingual safety oracle, verified
resource registry, self-care source package, pilot notice/consent, ethics/institution decision,
platform threat acceptance, retention/purge proof, incident exercise, production observability,
accessibility certification, approved workload/performance baseline, backup/restore proof, provider
outage drill, rollback drill, signed owner docket or independent release decision exists. Safety,
language and resource evaluation has only an empty pre-registration template; it has no results.
Governance: P7 manual text/touch intake remains the bounded functioning path; P8-C/P9-C Stage 3
remain BLOCKED; P10/P11 live remain 0/9 approved, with P11 five OPEN/four BLOCKED; P12–P23 runtime
or subphases remain NOT STARTED where applicable. P13 real provider/referral, P14 clinical routing,
P15 knowledge/RAG, P16/P17 exchange, P18/P19 research, P20 orchestration, P21 admin governance,
P22 platform readiness and P23 validation do not acquire approval through this pack.
Scope: exactly four documentation paths changed: two new P24 review documents, this P24-only tracker
note/section 70 and the byte-identical recorded prompt. No runtime, tests, fixture, API/UI,
schema/ORM/migration, dependency/lockfile, accepted ADR, CI/scanner, Docker/infrastructure,
credential, policy, approval, participant activity, pilot or release changed. Alembic remains
p7a_0007; Next.js and root eslint-config-next remain 16.4.2.
STOP/next action: named accountable institution/product, clinical/safety, mental-health, language,
resource, content/source, ethics/legal/privacy/records, security/identity/vendor, accessibility,
research/statistical, SRE/incident/recovery, independent QA and release-board roles must review
actual exact-SHA evidence and sign narrowly bounded decisions. Missing, stale, disputed, expired,
scope-incompatible or unsigned evidence fails closed. No human participant may be recruited or
enrolled; no real patient or clinician workflow, data collection, production deployment or pilot is
authorized; and no formal GO, CONDITIONAL GO or NO-GO decision is recorded.
```

---

# 71. P22-A Non-Invasive Platform Threat and Authorization Audit — Bounded Technical Evidence

```text
Status: COMPLETE — BOUNDED P22-A TECHNICAL AUDIT/TEST EVIDENCE ONLY; P22 remains PARTIAL and all
live P22 acceptance and accountable approval remain unverified.
Baseline: exact verified origin/main @ 55cbcc9c0ea4680366302919dbacd0240f6a5c5f. Work was performed
on phase/p22-a-noninvasive-threat-authz-audit in a clean isolated worktree; the primary worktree and
its pre-existing files were not modified, reset or stashed.
Deliverables: P22_A_PLATFORM_THREAT_AND_AUTHORIZATION_AUDIT.md records the current P4–P7 asset,
data-flow, trust-zone, route-authority, threat/control-gap, evidence, acceptance and unsigned owner
decision inventory. It distinguishes as-built evidence, proposed/unapproved controls, absent
features, unknown deployment facts and pending human decisions. It does not promote the Pre-P22
prose or P11-focused Specs 27/28 into a signed platform threat model or acceptance decision.
Authorization evidence: a new real-PostgreSQL HTTP regression creates two independent synthetic
pseudonymous session/consent/encounter subjects. It proves session B cannot start, read or abandon
session A's valid pre-intake encounter; missing/invalid bearer and inert forged actor/role/MFA
headers do not authorize the operation; denial is non-cacheable and privacy-safe; the encounter
state/version and intake/questionnaire/answer rows do not change; and session A remains usable.
Existing cross-intake, revoked-consent, closed-session, identity/MFA, self-subject IDOR, BFF storage
and logging tests are referenced rather than duplicated.
Verification: the focused regression passed against a dedicated disposable local PostgreSQL
database. Full backend, PostgreSQL, frontend, Playwright, Docker, security/Gitleaks and exact-feature-
SHA six-job CI evidence is recorded in the associated pull request and execution report; those
technical results do not constitute live AC-P22 acceptance.
Scope: exactly four tracked paths changed: the existing P7 PostgreSQL integration test file, the new
P22-A audit, this minimal tracker update and the byte-identical recorded Codex prompt. No runtime
application/BFF/UI, route, contract, migration/schema, dependency/lockfile, Docker/CI, production
configuration, feature flag, rate limit, retention/purge, kill switch, external integration,
clinical content, finding disposition, accepted ADR, approval, pilot or release changed.
Governance: AC-P22-001..011 LIVE NOT VERIFIED. No official severity, risk acceptance, signer or
institutional/AppSec/privacy/legal/clinical/production approval is recorded. P22-B/C/D/E NOT STARTED;
P23 and P24 remain NOT STARTED. P7 deterministic/manual behavior is unchanged; P8-C/P9-C Stage 3
and P10/P11 live restrictions remain in force.
STOP/next action: independent reviewers and the accountable identity/institution, AppSec, privacy/
consent, data-governance, clinical, platform/SRE and release roles must review exact-SHA evidence and
sign separately bounded decisions. Only a new prompt may authorize P22-B/C/D/E. Do not deploy,
activate optional/clinical functionality, process real data, begin P23/P24 or issue a pilot/release
decision from this bounded evidence.
```

---

# 72. P22-B Security Controls — Bounded Engineering Increment

```text
Status: PARTIAL — BOUNDED P22-B ENGINEERING INCREMENT ONLY; P22 remains PARTIAL and AC-P22-001..011
remain LIVE NOT VERIFIED.
Baseline: exact origin/main @ d9ce291ebe878834fa3f19cd966975936be933bf. Work was performed on
phase/p22-b-security-controls in an isolated worktree without modifying or resetting the primary
worktree.
Controls: FastAPI responses now apply a centralized API security-header policy, with HSTS only in
production and no permissive cross-origin response policy. Patient, clinician and admin Next.js
responses share a production-aware CSP and security-header baseline. Cookie-authenticated patient
BFF mutations require an exact Origin match; production requires an explicit canonical HTTPS
SWASTHYASETU_PUBLIC_ORIGIN and fails closed when it is missing or unsafe.
Evidence: backend unit tests cover API headers, production HSTS, absent CORS grants and sanitized
unexpected errors. Frontend unit tests cover production/development policy differences. Patient BFF
tests cover missing, exact, lookalike and unsafe configured origins. Playwright checks the actual
Patient, Clinician and Admin HTTP responses.
Scope: no dependency, lockfile, schema, migration, API contract, clinical feature, external service,
upload path, retention workflow, kill switch, production credential, CI definition or deployment
infrastructure changed. P7 manual text/touch intake remains available and all P8-C/P9-C/P10/P11
governance restrictions remain in force.
Continuation: from merged origin/main @ 8e6c9a24b84fc09ccbc57bb5eb19a785b854c3d5,
phase/p22-b-abuse-controls adds a provider-neutral limiter contract and a bounded process-local
sliding-window adapter. All `/api/v1` requests consume process and direct-transport-peer budgets;
syntactically valid bearer values use only process-secret HMAC fingerprints. Mutations and anonymous session
creation receive tighter layers. Multi-layer accounting is atomic, storage is bounded, forwarding
headers are ignored, and the container entrypoint disables Uvicorn proxy-header rewriting before
the application boundary. Raw bearer values are not retained, denials are canonical and limiter
failure is fail-closed through the sanitized error boundary.
Ruling: this is application defense in depth, not distributed or topology-aware enforcement. The
bounded key store preserves the global bucket but may evict per-subject history during
high-cardinality churn. Edge/fleet coordination, representative production budgets, proxy
configuration, monitoring and operational ownership remain unverified. AC-P22-006 therefore remains
LIVE NOT VERIFIED. Upload security is not applicable to the current runtime because no upload
endpoint exists, but AC-P22-005 also remains LIVE NOT VERIFIED rather than passing by absence.
Outstanding: approve and implement topology-aware edge/fleet enforcement; complete the route/object access
matrix; review production proxy/header stripping, logging sinks and secrets; implement P22-C
retention and P22-D resilience only in their separately bounded units; then execute P22-E independent
regression and closure. No pilot, production release or human clinical workflow is authorized.
```

---

# 73. P22-C Retention/Purge — Synthetic Engineering Foundation

```text
Status: PARTIAL — SYNTHETIC P22-C ENGINEERING FOUNDATION ONLY; P22 remains PARTIAL and all live
AC-P22 acceptance remains unverified.
Baseline: exact merged origin/main @ 2b473606c34775851d5a51aebe9d548bec5a3e1b. Work was performed
on phase/p22-c-retention-controls in an isolated worktree.
Decision boundary: canonical documents leave durations, lawful/governance authority, legal-hold
precedence, audit preservation, backup/provider deletion and operational ownership unresolved. No
such decision or approval is inferred.
Implementation: immutable policy-reference, external authorization, versioned target, purge-plan,
receipt/result, tombstone and restore-decision contracts; explicit idempotent adapter protocol;
manually invoked coordinator; bounded identifier-free failure telemetry; deterministic restored-
generation reblocking. Blocked plans never call adapters, missing/failed/malformed adapters produce
generic honest failed or partial results, and retry may return already-absent without an exactly-once
claim.
Scope: synthetic tests only. No real adapter, patient-data deletion, duration, schema, migration,
API, UI, job, worker, scheduler, outbox event, provider, dependency, lockfile or startup activation.
Acceptance: PRIV-003/004 and AC-P22-007/008 remain LIVE NOT VERIFIED. Production work requires an
authoritative schedule/hold matrix, durable execution state, real store and backup/provider
integration, alert/runbook ownership, restore drills and independent review. P22-D/P22-E, P23,
P24, pilot and release remain outside this unit.
```

---

# 74. P22-D Kill-Switch/Resilience — Synthetic Engineering Foundation

```text
Status: PARTIAL — SYNTHETIC P22-D ENGINEERING FOUNDATION ONLY; P22 remains PARTIAL and all live
AC-P22 acceptance remains unverified.
Baseline: exact merged origin/main @ 7dc45bf11285e7c061211436f804d4e5f8f5c2dd. Work was performed
on phase/p22-d-resilience-controls in an isolated worktree.
Decision boundary: canonical documents leave the production capability/owner matrix, activation
authority, distributed control topology, reset ceremony, monitoring, recovery objectives and drills
unresolved. No such decision or approval is inferred.
Implementation: closed optional-capability and failure vocabulary; immutable switch, deadline/retry
and outcome contracts; fail-safe process-local switchboard; idempotent one-way trips; bounded
dependency executor; post-call trip recheck; idempotent transient retry only; identifier-free
telemetry; synthetic direct-constructor, outage, concurrency, timeout and privacy tests.
Scope: every capability is disabled by default and the package is absent from runtime registration.
No production enablement, provider request, clinical behavior, API/UI, schema/migration, job/worker,
scheduler, event/outbox, deployment controller, dependency or lockfile change.
Limitation: the process-local post-call check discards late results but cannot reverse an already-
started external side effect; no side-effecting integration is wired in this unit.
Acceptance: AC-P22-009/010 and live NFR-RES-001..007 remain LIVE NOT VERIFIED. Production work
requires authoritative distributed controls, authenticated/audited operations, approved owners and
re-enable rules, monitoring/alerts, real outage and partial-deploy/rollback drills, recovery targets
and independent review. P22-E/P23/P24, pilot and release remain outside this unit.
```

---

# 75. P12-A Synthetic Language and Speech Contract Foundation

```text
Status: COMPLETE SAFE ENGINEERING SUBSET — LIVE P12 REMAINS PARTIAL/UNAPPROVED.
Baseline: exact merged origin/main @ 7dc45bf11285e7c061211436f804d4e5f8f5c2dd. Work was performed
on phase/p12-a-synthetic-language-contracts in an isolated linked worktree; the primary worktree and
its pre-existing untracked files were not modified, reset or stashed.
Implementation: strict immutable versioned contracts for batch speech-to-text, language detection,
transliteration, translation and text-to-speech; distinct original/derived artifact references;
explicit language/script uncertainty, partial/final states, protected spans, optional labeled
provider quality, UTC provenance and exact request/result lineage checks. Five independent async
ports prevent a LanguageAIProvider god interface. Explicit version-pinned provider metadata accepts
only ENGINEERING_ONLY / MOCK_ONLY descriptors and stores no executable adapter.
Testing: deterministic exact-mapping mocks live only under backend/tests/language_support. Focused
tests cover direct construction, immutability, strict types/versions, naive/non-UTC timestamps,
malformed/oversize data, fabricated confidence, status/finality contradictions, stale generations,
wrong operation/language/script/voice identity, registry duplicates/ambiguity, mutated frozen shells,
unknown/injected/malformed mock outcomes and zero file/network I/O.
Scope: no dependency/lockfile, model/provider SDK, audio bytes or real fixture, model download,
network call, endpoint/credential, runtime adapter, FastAPI/module/capability registration, feature
flag, API/BFF/UI/microphone, locale pack, schema/ORM/migration, persistence, job/worker/event/outbox,
Docker/CI/infrastructure, consent policy, medical glossary, clinical copy, safety route or fact
promotion was added. Alembic remains p7a_0007 and SpeechSettings remains disabled.
Governance: P7 manual text/touch remains the supported fallback. P8-C/P9-C Stage 3 stay BLOCKED;
P10/P11 live gates remain unchanged; no P11-E source access is enabled. P12-A engineering evidence
does not approve a language, provider, model, voice, format, threshold, region, retention value,
population, patient-data operation, benchmark result, pilot or production use. AC-P12-001..009 remain
LIVE NOT VERIFIED; P12-B/C/D require separately authorized evidence and decisions.
Next action: review this bounded P12-A feature branch. Do not begin real adapters (P12-B), voice UI
(P12-C), governed multilingual regression/clinical-language evaluation (P12-D), or live activation
until every applicable canonical readiness STOP condition has authoritative evidence.
```

---

# 76. P13-A Synthetic Provider/Resource Domain Foundation

```text
Status: PARTIAL — ENGINEERING-SYNTHETIC DOMAIN FOUNDATION ONLY; P13 remains PARTIAL and every live
AC-P13 criterion remains unverified.
Baseline: exact merged origin/main @ 7dc45bf11285e7c061211436f804d4e5f8f5c2dd. Work was performed
on phase/p13-a-synthetic-provider-resource-domain in an isolated worktree.
Implementation: frozen/slotted SyntheticSourceEvidence, SyntheticProviderRecord and
SyntheticCareResourceRecord contracts with strict synthetic prefixes, bounded labels/codes,
SHA-256 artifact metadata, positive versions, aware-UTC normalization, temporal ordering, closed
ENGINEERING_ONLY / ENGINEERING_SYNTHETIC / UNVERIFIED states and nested-object revalidation.
Scope: no real or realistic provider/resource data; no contacts, URLs, facilities, geography,
languages, hours, availability, eligibility, specialty taxonomy, ranking, clinical suitability,
crisis authority, registry query, adapter, persistence, migration, API, referral, event, job,
feature flag, UI, dependency or runtime registration.
Acceptance truth: FR-DIR-001..017, FR-REF-001..013 and AC-P13-001..011 remain LIVE NOT VERIFIED.
P7 manual intake and generic urgent-help navigation remain independent. P8-C/P9-C Stage 3 and
P10/P11/P12 live restrictions remain unchanged.
Next action: independent review of this bounded branch. P13-B routing, P13-C referral state,
P13-D notifications and P13-E UI remain blocked until their source, clinical, privacy, identity,
security, accessibility and operational decisions are explicitly recorded.
```

---

# 77. P13-B Synthetic Symbolic Routing and Abstention Foundation

```text
Status: PARTIAL - BOUNDED ENGINEERING-SYNTHETIC P13-B SUBSET ONLY; P13 remains PARTIAL and all live
AC-P13 acceptance remains unverified.
Baseline: stacked on P13-A exact SHA fd1226505a7d0c96c46ab0068bbb120c5594c999. Work was performed
on phase/p13-b-synthetic-routing-abstention in an isolated worktree.
Implementation: immutable request, rule, versioned policy and decision contracts plus a pure exact
symbol evaluator. Only reserved synthetic signal/service identifiers are accepted. Exactly one
match returns a synthetic match; zero or multiple matches abstain with no selected service/rule.
Nested values are revalidated, policy artifact identity is retained, timestamps are aware UTC, and
direct-constructor invariants prevent inconsistent decisions.
Scope: no free text, symptom, patient, clinical fact/category, threshold, model output, P9 input,
urgency, geography, eligibility, availability, provider/resource lookup, contact, ranking, real
taxonomy/policy, registry, source adapter, persistence, migration, API, UI, referral, notification,
event, job, dependency, feature flag or runtime registration.
Acceptance truth: this is only the readiness Gate 2 nonmedical symbolic matching/abstention
allowance. FR-DIR-001..017, FR-REF-001..013 and AC-P13-001..011 remain LIVE NOT VERIFIED. P7 and
generic urgent-help navigation remain independent; all P8-C/P9-C/P10/P11/P12 restrictions remain.
Next action: independent review of the stacked bounded branch. Real directory query, specialty
mapping, provider selection/ranking, referrals, notifications, and P13 UI remain blocked on their
recorded source, clinical, privacy, identity, security, accessibility, and operational decisions.
```

---

# 78. P13-C Synthetic Referral Lifecycle and Idempotency Foundation

```text
Status: PARTIAL - BOUNDED ENGINEERING-SYNTHETIC P13-C SUBSET ONLY; P13 remains PARTIAL and all live
AC-P13 acceptance remains unverified.
Baseline: stacked on P13-B exact SHA 56c921c2896bb90f91ea928bea0f0452dff27979. Work was performed
on phase/p13-c-synthetic-referral-lifecycle in an isolated worktree.
Implementation: immutable referral status/aggregate, transition-pair, versioned policy, command,
receipt and result contracts plus a pure optimistic transition function. Production code bundles
no transition graph. Exact receipt-backed replay is a no-op; key conflict, stale version,
cross-referral history, invalid chronology and forced mutation fail closed without rolling back a
later state or claiming exactly-once delivery.
Scope: no real transition/terminal/correction/expiry policy; patient/session/encounter, actor,
institution, destination, provider/resource, consent, payload, reason, priority, contact,
transcript, external reference, delivery evidence, adapter, webhook, notification, persistence,
migration, API, outbox/event, job/worker, dependency, feature flag or runtime registration.
Acceptance truth: status names and synthetic mechanics do not prove or authorize offer, consent,
sharing, dispatch, acknowledgement, scheduling, completion or failure. FR-REF-001..013 and
AC-P13-006..010 remain LIVE NOT VERIFIED, as do all other live P13 criteria. P7 and generic
urgent-help navigation remain independent; all P8-C/P9-C/P10/P11/P12 restrictions remain active.
Next action: independent review of the stacked bounded branch. Live referral work remains blocked
on consent/identity, recipient/destination, payload minimization, approved transitions and races,
durable transaction/outbox/idempotency, adapter/reconciliation, privacy/security and operations.
```

---

# 79. P13-D Synthetic Notification Failure Contracts

```text
Status: PARTIAL - BOUNDED ENGINEERING-SYNTHETIC P13-D SUBSET ONLY; P13 remains PARTIAL and all live
AC-P13 acceptance remains unverified.
Baseline: exact merged origin/main @ 86eaccba6010dbe64c612f7fe66bb97b33f8df70. Work was performed
on phase/p13-d-synthetic-notification-contracts in an isolated worktree.
Implementation: immutable template metadata, safe symbolic variable, content-free notification
intent, simulated failure and failure-receipt contracts plus a pure recorder. Constructors enforce
reserved synthetic identifiers, bounded exact variable sets, version/hash binding, aware UTC
normalization, chronology, nested revalidation and fixed engineering-only authority. The receipt
retains a deterministic fingerprint and simulated failure metadata only.
Scope: no message copy/body, recipient, contact, channel, provider, delivery port, success state,
retry/deadline policy, signature/webhook, preference/consent, referral mutation, persistence,
migration, API, outbox/event, job/worker, dependency, feature flag, network or runtime registration.
Acceptance truth: failure evidence does not prove or authorize notification delivery or referral
sharing. FR-NOTIF-001..006, FR-REF-001..013 and AC-P13-006..011 remain LIVE NOT VERIFIED, as do all
other live P13 criteria. P7 and generic urgent-help navigation remain independent; all
P8-C/P9-C/P10/P11/P12 restrictions remain active.
Next action: independent review of this bounded branch. Live notification work remains blocked on
recipient/channel/provider selection, approved copy/locales, preferences/consent, retry/deadline,
security/webhook, retention, delivery semantics and incident/correction decisions.
```

---

# 80. P13-E Synthetic Referral Presentation Test Foundation

```text
Status: PARTIAL - BOUNDED TEST-ONLY P13-E SUBSET; P13 remains PARTIAL and all live AC-P13
acceptance remains unverified.
Baseline: exact merged origin/main @ ced4839c220cd598f1f3c65052828d7fdb4bd36e. Work was performed
on phase/p13-e-synthetic-referral-presentation in an isolated worktree.
Implementation: Vitest-only patient unavailable/unknown/failed referral preview and admin
unavailable/unverified/stale/revoked source-warning preview. Closed vocabularies fail closed for
hostile runtime values; accessible status semantics, explicit engineering labels, no-action states,
and production-import isolation are regression tested.
Scope: no production component or route change; no provider/resource/contact/source evidence,
referral identifier/status authority, consent, moderation, API/BFF, network, browser storage,
persistence, migration, dependency, feature flag or runtime activation.
Acceptance truth: synthetic presentation fixtures do not approve copy, roles, source warnings,
identity, accessibility, referral status or live UI. AC-P13-001..011 and all live P13 requirements
remain LIVE NOT VERIFIED. All P8-C/P9-C/P10/P11/P12 restrictions remain active.
Next action: live P13 remains blocked on accountable source, clinical, identity/consent, privacy,
security, copy/localization, accessibility, operational and release decisions.
```

---

# 81. P14-A Synthetic Mental-Health Signal Schema Foundation

```text
Status: PARTIAL - BOUNDED ENGINEERING-SYNTHETIC P14-A SUBSET ONLY; P14 remains PARTIAL and all live
AC-P14 acceptance remains unverified.
Baseline: exact merged origin/main @ 3451b85b2e95500993e6d36f4f43cc35f5a7a5f8. Work was performed
on phase/p14-a-synthetic-signal-schema in an isolated worktree.
Implementation: immutable engineering-only artifact, extraction request, fixed toy signal,
parsed/abstained result and content-free failure contracts; strict exact-field parser; exact
request/input/schema/deadline binding; and a detached provider-neutral extractor protocol. Direct
construction, forced mutation, identity, chronology, canonical UTC and adversarial payloads fail
closed with stable non-echoing errors.
Scope: fixed ALPHA/BETA/GAMMA/DELTA tokens only; no narrative, patient/session/encounter, clinical
signal name or meaning, score/confidence, screening instrument, prompt, model/provider adapter,
language backstop, route, policy, crisis resource/copy, consent, referral, API, persistence,
migration, job/event, dependency, UI, feature flag or runtime registration.
Acceptance truth: engineering parser/schema evidence does not satisfy live signal extraction or
grant mental-health authority. FR-MH-001..020 and AC-P14-001..013 remain LIVE NOT VERIFIED. P7 and
generic urgent-help navigation remain independent; all P8-C/P9-C/P10/P11/P12/P13 restrictions stay
active.
Next action: independent review of this bounded subset. P14-B backstop, P14-C policy/routing,
P14-D patient fallback UI, P14-E referrals and P14-F clinical/adversarial evidence remain blocked on
their recorded clinical, language, privacy, identity, resource, accessibility and release decisions.
```

---

# 82. P14-B Synthetic Safety-Backstop Foundation

```text
Status: PARTIAL - BOUNDED ENGINEERING-SYNTHETIC P14-B SUBSET ONLY; P14 remains PARTIAL and all live
AC-P14 acceptance remains unverified.
Baseline: exact merged origin/main @ 4d586381d67b5870c8eae4115adaa4c43e45f04c. Work was performed
on phase/p14-b-synthetic-backstop-foundation in an isolated worktree.
Implementation: immutable engineering-only artifact, request, matched/no-match result and
content-free simulated-failure contracts; exact identity/deadline binding; canonical UTC,
chronology, ordering and forced-mutation validation; detached provider-neutral port; and a
deterministic mock isolated under test support that snapshots the request and checks deadlines
before toy evidence.
Scope: fixed ALPHA/BETA/GAMMA/DELTA tokens only. No narrative, OCR or patient data processing,
clinical/language lexicon, patient/session identity, clinical signal or meaning, score/confidence,
prompt, production adapter, route, policy, crisis resource/copy, referral, API, persistence,
migration, job/event, dependency, UI, feature flag, network access or runtime registration.
Acceptance truth: engineering contract/mock evidence does not implement an independent clinical
backstop or grant mental-health authority. FR-MH-001..020 and AC-P14-001..013 remain LIVE NOT
VERIFIED. All P7/P8-C/P9-C/P10/P11/P12/P13 restrictions stay active.
Next action: independent review of this bounded subset. P14-C and all live P14 work remain blocked
on recorded clinical, language, privacy, identity, resource, accessibility and release decisions.
```

---

# 83. P14-C Synthetic Policy-Routing Mechanics

```text
Status: PARTIAL - BOUNDED ENGINEERING-SYNTHETIC P14-C SUBSET ONLY; P14 remains PARTIAL and all live
AC-P14 acceptance remains unverified.
Baseline: exact merged origin/main @ 9244864dc79be72fd8d0db53b0d381af1bf47a88. Work was performed
on phase/p14-c-synthetic-policy-routing in an isolated worktree.
Implementation: immutable engineering-only rule, policy, evaluation, reference, and decision
contracts; exact policy-content and evidence/decision fingerprints; fixed toy override,
clarification, and standard precedence; explicit degraded outcomes; and hard denial before reading
input in staging, pilot, or production. The only executable rule mapping is test-only.
Scope: closed SYNTHETIC symbols only. No ROUTE_A/B/C meaning, clinical signal/rule/threshold,
questionnaire, narrative/patient/session data, model score/route authority, crisis disposition,
resource, referral, consent behavior, API, persistence, migration, event/job, dependency, UI,
feature flag, module registration, or runtime activation.
Acceptance truth: engineering mechanics are not a clinically approved deterministic mental-health
policy and do not satisfy live routing acceptance. FR-MH-001..020 and AC-P14-001..013 remain LIVE
NOT VERIFIED. All P7/P8-C/P9-C/P10/P11/P12/P13 restrictions stay active.
Next action: independent review of this bounded subset. P14-D patient fallback UI and every live P14
capability remain blocked on the recorded clinical, language, privacy, resource, accessibility,
operations, and release decisions.
```

---

# 84. P14-D Synthetic Degraded Presentation

```text
Status: PARTIAL - BOUNDED ENGINEERING-SYNTHETIC P14-D SUBSET ONLY; P14 remains PARTIAL and all live
AC-P14 acceptance remains unverified.
Baseline: exact merged origin/main @ dc2a2c1bada32eb9b184b008a826dcd5fdb1161f. Work was performed
on phase/p14-d-synthetic-degraded-presentation in an isolated worktree.
Implementation: a strict fresh-UTC projection accepts only an exactly shaped P14-C engineering
decision in LOCAL/TEST. Unknown/protected environments return unavailable before untrusted data is read;
malformed or stale data degrades. A disconnected Vitest-only harness presents machine tokens with no
actions and never has a production import or route.
Scope: no crisis guidance/copy/contact, patient-facing P14 UI, route meaning, clinical decision,
patient/session data, API/BFF, persistence, migration, feature flag, service worker/cache change,
dependency, or runtime activation.
Acceptance truth: static test-only presentation evidence does not implement P14 crisis UI/fallback
or satisfy live routing/resource accessibility acceptance. FR-MH-001..020 and AC-P14-001..013 remain
LIVE NOT VERIFIED. All P7/P8-C/P9-C/P10/P11/P12/P13 restrictions stay active.
```

---

# 85. P14-F Synthetic Adversarial Harness

```text
Status: PARTIAL - BOUNDED OFFLINE ENGINEERING-SYNTHETIC P14-F SUBSET ONLY; P14 remains PARTIAL and
all live AC-P14 acceptance remains unverified.
Baseline: exact merged origin/main @ f01cb624325ace6bf26836421fd6ef6564f350bd. Work was performed
on phase/p14-f-synthetic-adversarial-harness in an isolated worktree.
Implementation: an offline pytest harness composes the existing P14-A/B/C contracts, test-only
backstop, and test-only policy fixture. Fixed toy cases cover deterministic standard,
override/non-downgrade, clarification, no-match, missing-policy, cross-source disagreement,
malformed authority/prose fields, and protected-environment short-circuiting.
Scope: tests and documentation only; no production module change, patient/clinical text, score,
threshold, language lexicon, resource, recipient, referral, consent, API/BFF, persistence, migration,
dependency, UI, feature flag, network, or runtime activation. P14-E is deliberately not implemented.
Acceptance truth: this is engineering regression structure, not a clinically reviewed corpus,
clinical validation, release evidence, or live P14 acceptance. FR-MH-001..020 and AC-P14-001..013
remain LIVE NOT VERIFIED; all P7/P8-C/P9-C/P10/P11/P12/P13 restrictions stay active.
```

---

# 86. P15-A Synthetic Knowledge Schema and Pack Loader

```text
Status: PARTIAL - BOUNDED ENGINEERING-SYNTHETIC P15-A SUBSET ONLY; P15 remains PARTIAL and all live
AC-P15 acceptance remains unverified.
Baseline: exact merged origin/main @ 1f71e60036c886f20351fdb6f0923e79d3ab1ce9. Work was performed
on phase/p15-a-synthetic-knowledge-schema in an isolated worktree.
Implementation: immutable pack/item contracts use closed nonmedical identity, placeholder, source,
and tag tokens. Only TEST_ONLY_UNAPPROVED is representable. Exact pack identity, schema/version,
canonical UTC creation time, ordered items, nested metadata, authority labels, and content hash are
strictly validated. The in-memory mapping loader rejects unknown/missing fields, noncanonical or
future timestamps, forged hashes/states, hostile mappings, duplicates, mutation, and oversize input
with content-free errors.
Scope: no remedy/advice or readable content, real source/rights claim, APPROVED state, eligibility,
clinical exclusion, safety integration, patient context, RAG/vector/model/provider, file/network I/O,
database/migration, API/BFF, admin workflow, UI, dependency, feature flag, event/job, or runtime
registration/activation.
Acceptance truth: schema mechanics and synthetic placeholders are not an approved content store,
clinical validation, publication workflow, patient display, or live P15 acceptance. FR-SELF-001..017
and AC-P15-001..010 remain LIVE NOT VERIFIED; all upstream governance restrictions stay active.
```

---

# 87. P15-B Synthetic Eligibility Engine

```text
Status: PARTIAL - BOUNDED ENGINEERING-SYNTHETIC P15-B SUBSET ONLY; P15 remains PARTIAL and all live
AC-P15 acceptance remains unverified.
Baseline: exact merged origin/main @ 0ba2f85b353fcd3884b71a79f4f8ba8fb59146aa. Work was performed
on phase/p15-b-synthetic-eligibility-engine in an isolated worktree.
Implementation: immutable evaluation, toy policy, rule, candidate-reference, and result contracts
bind exact P9 synthetic safety provenance, P15-A pack identity/hash, context snapshot, policy hash,
and UTC decision time. A pure evaluator denies staging/pilot/production, preserves every safety
block, fails closed on incomplete/conflicting context or invalid policy, applies closed exclusions
before includes, and returns only content-free engineering placeholder references.
Scope: no clinical eligibility or contraindication rule, allergy/medication/condition/age/pregnancy
interpretation, remedy/advice/content, real patient/context, approved source/retrieval, RAG/vector/LLM,
database/migration, API/BFF, admin workflow, UI, dependency, feature flag, event/job, or runtime
registration/activation.
Acceptance truth: SYNTHETIC_ENGINEERING_CANDIDATE proves only toy deterministic mechanics. It is not
a low-risk classification, clinical validation, content approval, retrieval result, display authority,
or live P15 acceptance. FR-SELF-001..017 and AC-P15-001..010 remain LIVE NOT VERIFIED; all upstream
governance restrictions stay active.
```

---

# 88. P15-E Synthetic Safety Regression Suite

```text
Status: PARTIAL - BOUNDED OFFLINE ENGINEERING-SYNTHETIC P15-E SUBSET ONLY; P15 remains PARTIAL and
all live AC-P15 acceptance remains unverified.
Baseline: exact merged origin/main @ c50dee59ca507b8d4efcca16425d85224643a9bb. Work was performed
on phase/p15-e-synthetic-safety-regression in an isolated worktree.
Implementation: a pytest-only composition harness runs the existing P9 synthetic safety engine into
the existing P15-A knowledge-pack and P15-B eligibility boundaries. Closed symbolic cases verify
safety-first precedence across downstream context states, clarification, exclusion, missing policy,
future-pack rejection, exact-pack allowlisting, deterministic output and protected-environment
denial before hostile inputs are inspected.
Scope: no production module, patient/clinical fixture, remedy/advice/content, real source, clinical
rule or validation, retrieval/RAG/vector/LLM, persistence/migration, API/BFF, admin workflow, UI,
dependency, network, feature flag, event/job or runtime registration/activation.
Acceptance truth: the suite proves only offline composition mechanics. It is not clinical validation,
an approved held-out corpus, operational/release evidence, display authority or live P15 acceptance.
FR-SELF-001..017 and AC-P15-001..010 remain LIVE NOT VERIFIED; all upstream governance restrictions
stay active.
```

---

# 89. P16-A Synthetic FHIR Mapping Contracts

```text
Status: PARTIAL - BOUNDED DETACHED ENGINEERING-SYNTHETIC P16-A SUBSET ONLY; P16 remains PARTIAL and
all live AC-P16 acceptance remains unverified.
Baseline: exact merged origin/main @ bf095fc3f045145e6843d8abd3b5eb8ff907714e. Work was performed
on phase/p16-a-synthetic-fhir-contracts in an isolated worktree.
Implementation: immutable R4 4.0.1 mapping-context, source-reference and result contracts bind exact
synthetic source identity/version/hash, mapping revision, UTC transformation time and context
fingerprint. A pure detached mapper returns only content-free export projections or non-authoritative
import candidates for a closed symbolic resource vocabulary. Model-risk and unconfirmed-extraction
sources are rejected, Condition is unrepresentable, and protected environments deny before input.
Scope: no patient/clinical values, field crosswalk, terminology/profile/package, FHIR JSON,
validation/conformance claim, authorization/consent processing, document access, persistence,
migration, API/BFF, adapter, transport/network, HAPI sidecar, dependency, feature flag, ABDM behavior
or runtime registration/activation.
Acceptance truth: symbolic metadata mechanics are not a real FHIR mapper, approved clinical mapping,
validator evidence, exchange authority or live P16 acceptance. FR-FHIR-001..011 and AC-P16-001..010
remain LIVE NOT VERIFIED; all upstream governance restrictions stay active.
```
