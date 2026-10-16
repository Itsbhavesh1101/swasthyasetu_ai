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

**Current macro stage:** P7-A Intake Domain / Schema — PARTIAL; remote CI verification pending
**Current recommended next action:** verify P7-A remote CI, then P7-B — Deterministic Adaptive Engine.

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
| P7 | Structured Clinical Intake | PARTIAL | P7-A implementation is complete locally; remote CI verification is pending. P7-B/P7-C are not started. |
| P8 | AI Gateway + Structured Extraction | NOT STARTED | Depends on P7. |
| P9 | Physical Safety Framework | NOT STARTED | Real policy requires clinical approval. |
| P10 | Clinician Dashboard + Summary | NOT STARTED | Depends on P5/P7. |
| P11 | Document AI / OCR | NOT STARTED | Requires OCR spec. |
| P12 | Multilingual Speech / Translation | NOT STARTED | Requires speech spec. |
| P13 | Providers + Resources + Referrals | NOT STARTED | Real provider source may remain TBD. |
| P14 | Mental Health / MannSetu | NOT STARTED | Real routing/copy requires clinical approval. |
| P15 | Self-Care / Ayurveda | NOT STARTED | Real content requires approved knowledge. |
| P16 | FHIR | NOT STARTED | Depends on stable domain model. |
| P17 | ABDM / ABHA | NOT STARTED | Requires current ABDM integration spec. |
| P18 | Classical ML | NOT STARTED | Dataset/task selection pending. |
| P19 | Hybrid QML | NOT STARTED | Depends on P18 baseline. |
| P20 | Unified Care Orchestration | NOT STARTED | Depends on implemented modules. |
| P21 | Admin + Governance + Review | NOT STARTED | Depends on governed modules. |
| P22 | Security + Privacy + Resilience | NOT STARTED | Continuous work culminates here. |
| P23 | E2E + Accessibility + Performance | NOT STARTED | Depends on integrated system. |
| P24 | Pilot Readiness | NOT STARTED | Requires governance and validation. |

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

## Before P9

| Document | Status |
|---|---|
| `08_SAFETY_AND_TRIAGE_POLICY.md` | NOT STARTED |

## Before P10

| Document | Status |
|---|---|
| `12_CLINICAL_PROVENANCE_SPEC.md` | NOT STARTED |
| `24_CLINICIAN_DASHBOARD_SPEC.md` | NOT STARTED |

## Before P11

| Document | Status |
|---|---|
| `15_DOCUMENT_AI_OCR_SPEC.md` | NOT STARTED |

## Before P12

| Document | Status |
|---|---|
| `16_MULTILINGUAL_SPEECH_SPEC.md` | NOT STARTED |

## Before P13

| Document | Status |
|---|---|
| `11_PROVIDER_ROUTING_POLICY.md` | NOT STARTED |

## Before P14

| Document | Status |
|---|---|
| `09_MENTAL_HEALTH_POLICY.md` | NOT STARTED |
| `13_AI_ORCHESTRATION_SPEC.md` | NOT STARTED |
| `14_LLM_EXTRACTION_SPEC.md` | NOT STARTED |

## Before P15

| Document | Status |
|---|---|
| `10_SELF_CARE_AYURVEDA_POLICY.md` | NOT STARTED |
| `17_RAG_KNOWLEDGE_SPEC.md` | NOT STARTED |

## Before P16/P17

| Document | Status |
|---|---|
| `20_FHIR_MAPPING_SPEC.md` | NOT STARTED |
| `21_ABDM_INTEGRATION_SPEC.md` | NOT STARTED |

## Before P18/P19

| Document | Status |
|---|---|
| `18_CLASSICAL_ML_SPEC.md` | NOT STARTED |
| `19_QUANTUM_ML_SPEC.md` | NOT STARTED |

## Before hardening

| Document | Status |
|---|---|
| `26_PRIVACY_CONSENT_SPEC.md` | NOT STARTED |
| `27_SECURITY_ARCHITECTURE.md` | NOT STARTED |
| `28_THREAT_MODEL.md` | NOT STARTED |
| `30_TESTING_STRATEGY.md` | NOT STARTED |
| `31_OBSERVABILITY_SPEC.md` | NOT STARTED |
| `32_DEVOPS_DEPLOYMENT.md` | NOT STARTED |
| `33_ERROR_HANDLING_POLICY.md` | NOT STARTED |

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
Status: PARTIAL — REMOTE CI VERIFICATION PENDING
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
Local verification: backend unit/regression and real PostgreSQL verification pass; final full gates pending.
P7 status: PARTIAL. P7-B and P7-C are not started.
Remote CI: PENDING.
Next recommended unit after CI completion: P7-B — Deterministic Adaptive Engine.
```
