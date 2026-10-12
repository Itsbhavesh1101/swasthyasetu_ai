# SwasthyaSetu AI
## 03 — Repository Structure Specification

**Document ID:** `SSAI-REPO-003`  
**Filename:** `03_REPOSITORY_STRUCTURE.md`  
**Status:** Foundation / Repository Layout Source of Truth  
**Version:** `1.0.0-draft`  
**Depends on:**
- `00_PROJECT_MASTER_SPEC.md`
- `01_PRODUCT_REQUIREMENTS.md`
- `02_SYSTEM_ARCHITECTURE.md`
- `29_ENGINEERING_STANDARDS.md`
- `34_MASTER_IMPLEMENTATION_PLAN.md`

**Primary implementation agent:** Codex  
**Architecture style:** Feature-oriented monorepo + modular FastAPI backend + independent web apps + isolated research and clinical-governance assets.

---

# 1. Purpose

This document freezes the initial repository organization for SwasthyaSetu AI.

The layout is designed so that:

- Codex always knows where new code belongs;
- new features can be added as modules without rewriting unrelated areas;
- domain logic stays separate from external providers;
- frontend, backend, clinical policy, ML/QML, infrastructure and documentation remain distinct;
- compute-heavy modules can later be extracted into services;
- safety-critical policy and test assets are visible and version-controlled;
- production artifacts and sensitive datasets are not accidentally committed.

This structure is intentionally extensible. New top-level directories should not be added without a clear need and an architecture decision when material.

---

# 2. Canonical Top-Level Structure

```text
swasthyasetu-ai/
|
+-- apps/
|   +-- patient-web/
|   +-- clinician-web/
|   +-- admin-web/
|
+-- backend/
|   +-- app/
|       +-- api/
|       +-- modules/
|       +-- shared/
|       +-- adapters/
|       +-- events/
|       +-- config/
|
+-- workers/
|
+-- packages/
|   +-- contracts/
|   +-- ui/
|
+-- ml/
|   +-- classical/
|   +-- quantum/
|   +-- datasets/
|   +-- evaluation/
|   +-- registry/
|   +-- notebooks/
|
+-- clinical/
|   +-- policies/
|   +-- knowledge/
|   +-- lexicons/
|   +-- test_cases/
|   +-- localization/
|
+-- tests/
|   +-- integration/
|   +-- contracts/
|   +-- e2e/
|   +-- safety/
|   +-- security/
|   +-- performance/
|   +-- fixtures/
|
+-- docs/
|   +-- clinical/
|   +-- ai/
|   +-- interoperability/
|   +-- frontend/
|   +-- security/
|   +-- engineering/
|   +-- implementation/
|   +-- codex/
|   +-- adr/
|
+-- infra/
|   +-- docker/
|   +-- terraform/
|   +-- monitoring/
|   +-- environments/
|
+-- deployments/
|   +-- local/
|   +-- staging/
|   +-- pilot/
|   +-- production/
|
+-- scripts/
+-- data/
|   +-- synthetic/
|   +-- fixtures/
|
+-- models/
+-- artifacts/
+-- .github/
|   +-- workflows/
|
+-- README.md
+-- CONTRIBUTING.md
+-- .gitignore
+-- .editorconfig
```

---

# 3. Core Rules

1. **Top-level directories are stable.** Ordinary feature work should fit an existing top-level concern.
2. **Backend feature logic lives in bounded modules.** A module owns its domain logic, persistence, state transitions, and tests.
3. **No direct cross-module table mutation.** Modules integrate through public services, typed contracts, read models, or events.
4. **External providers live behind adapters.** LLM, OCR, ASR/TTS, FHIR, ABDM, notifications, storage, model inference, and quantum backends must not leak vendor SDKs into domain logic.
5. **Research code and production inference are separate.** Top-level `/ml` contains training/evaluation; backend `modules/ml` contains governed runtime inference access.
6. **Clinical policy/content is version-controlled separately.** Policies, knowledge packs, safety lexicons, clinical localization, and safety fixtures live under `/clinical`.
7. **Real patient data is never committed.** Synthetic fixtures only.
8. **Large model/data artifacts are not stored in Git.** Use artifact/object/model storage.
9. **Feature extensibility uses modules, capabilities, events, and adapters—not a growing central `if/elif` chain.**
10. **Dynamic untrusted runtime plugins are out of scope.** Extensibility is compile-time/module-contract based.

---

# 4. Frontend Applications

## `apps/patient-web/`

Patient, caregiver, kiosk, and pseudonymous first-contact experience. Future feature areas should include onboarding, consent, intake, documents, mental health, self-care, providers, and referrals. Clinical policy remains server-authoritative.

P6-A establishes the patient-specific shell in `components/`, with responsive navigation,
patient-facing UI primitives, a persistent urgent-help entry point, and honest App Router shells
for planned patient routes. It contains no backend integration, browser persistence, authentication,
working language flow, or PWA/service-worker behavior.

## `apps/clinician-web/`

Clinician-facing queue, patient overview, timeline, summary, provenance, documents, safety, referrals, and future decision-support panels. New clinical modules should register feature panels rather than expanding one giant page.

## `apps/admin-web/`

Provider/resource governance, self-care approval, policy/model visibility, referral operations, feature flags, audits, and system health. Ordinary admins do not automatically receive clinical-policy authority.

---

# 5. Backend Modular Monolith

The backend starts as one FastAPI deployable unit but is internally divided into bounded contexts.

```text
backend/app/modules/
  identity/
  sessions/
  consent/
  patients/
  encounters/
  clinical_intake/
  safety/
  mental_health/
  documents/
  provenance/
  summaries/
  self_care/
  providers/
  resources/
  referrals/
  notifications/
  interoperability/
    fhir/
    abdm/
  ml/
  audit/
  feature_management/
```

A mature module should eventually resemble:

```text
<module>/
  domain/
  application/
  infrastructure/
  api/
  contracts/
  tests/
  public.py
  README.md
```

Do not create empty ceremony for every subfolder on day one; create them when the implementation phase needs them.

P4-A implements `backend/app/modules/sessions/` with cohesive `domain.py`, `contracts.py`,
`application.py`, `infrastructure.py`, `api.py`, and `public.py` files. The public boundary owns the
manifest, typed capabilities, and explicit registration builder; ORM/repository details remain
module-private.

P4-B implements `backend/app/modules/identity/` with cohesive domain, provider-neutral contracts,
application service, immutable authorization policy, SQLAlchemy persistence, and explicit
`public.py` registration. FastAPI-specific permission and self-subject guards live in
`backend/app/api/security/`; identity exposes no production router.

P4-C implements `backend/app/modules/consent/` with cohesive `domain.py`, `events.py`,
`contracts.py`, `application.py`, `infrastructure.py`, `api.py`, and `public.py` files. The module
owns consent persistence and lifecycle rules, exposes typed internal capabilities, and delegates
SESSION subject authentication to the registered `sessions.validate` capability. Shared bearer
syntax parsing remains transport-only in `backend/app/api/security/bearer.py`.

P5-A implements framework-independent domain boundaries in `patients/`, `encounters/`, and
`provenance/`. Patient and typed clinical values live in cohesive domain files; encounter lifecycle
and provenance values remain independently owned. Each module exposes domain contracts through
`public.py` only.

P5-B adds module-private SQLAlchemy records and caller-session repositories in
`patients/infrastructure.py` and `encounters/infrastructure.py`. The explicit typed clinical-value
codec lives in `patients/persistence.py`; it is not a generic JSON persistence surface. These files
add no application service, API route, runtime registration, or timeline capability. P5-C adds
`contracts.py`, `application.py`, and `api.py` boundaries to these modules and activates their
explicit registrations. Encounter patient validation and timeline composition consume only typed
public patient/encounter capabilities; architecture tests prohibit non-owning infrastructure
imports.

---

# 6. Backend Platform Areas

## `backend/app/api/`

Transport-level HTTP concerns only: router registration, request/response mapping, middleware, auth context extraction, correlation IDs, API versioning, and error translation. No substantive clinical/business rules.

## `backend/app/shared/`

Small shared kernel only: generic IDs, time helpers, error bases, actor context, pagination, observability primitives, security helpers, and genuinely generic types. Domain rules do not belong here.

`backend/app/shared/storage/` contains only provider-neutral object-storage contracts, validated
technical keys, and generic result/error types. It has no filesystem or vendor implementation.

## `backend/app/adapters/`

External implementations by capability:

```text
ai/
ocr/
speech/
translation/
storage/
notifications/
fhir/
abdm/
model_inference/
quantum/
```

`backend/app/adapters/storage/` contains storage implementations. P3-C provides only the
root-contained local-filesystem development/test adapter; production/self-hosted adapters remain
phase-gated.

## `backend/app/events/`

Platform event envelope, dispatcher interfaces, outbox integration, serialization, and version handling. Module-specific event payloads remain with owning modules/contracts.

```text
backend/app/events/
  envelope.py       # immutable versioned transport contract
  publisher.py      # publisher port and explicit in-process handlers
  outbox.py         # platform ORM record and caller-transaction repository
  dispatcher.py     # bounded, manual retry/status dispatcher foundation
```

## `backend/app/config/`

Typed configuration for application, database, security, features, object storage, AI, OCR, speech, FHIR, ABDM, and observability. Secrets are injected externally.

---

# 7. Background Work

## `backend/app/jobs/`

Provider-neutral background-job contracts plus the explicit, non-durable process-local dispatcher
and deterministic `run_once` worker scaffold. It is local/test infrastructure, does not persist or
share queue state, and does not auto-start from FastAPI.

## `workers/`

Reserved for future standalone worker process bootstrapping once a durable/shared job backend is
activated. A standalone process must not be backed by P3-C's process-local queue. Business logic
remains in modules and is called from jobs.

---

# 8. Shared Packages

## `packages/contracts/`

Cross-language generated/shared contracts, event schemas, and API-generated TypeScript types. No backend business implementation.

## `packages/ui/`

Shared frontend design-system primitives.

---

# 9. ML / QML Research

```text
ml/
  classical/
  quantum/
  datasets/
  evaluation/
  registry/
  notebooks/
```

- `classical/`: classical ML pipelines.
- `quantum/`: hybrid QML research.
- `datasets/`: dataset manifests/loaders/validation metadata, not large datasets.
- `evaluation/`: common benchmark metrics.
- `registry/`: model metadata, cards, and promotion tooling.
- `notebooks/`: exploration only; reproducible logic must move to modules/scripts.

---

# 10. Clinical Governance Assets

```text
clinical/
  policies/
    physical_red_flags/
    mental_health/
    self_care_eligibility/
    provider_routing/
    model_thresholds/
  knowledge/
    self_care/
    ayurveda/
    psychoeducation/
  lexicons/
    en/
    hi/
    hinglish/
  test_cases/
    physical_safety/
    mental_health/
    self_care/
    multilingual/
  localization/
```

Production clinical policy/content requires appropriate governance. Codex must not invent missing production rules.

---

# 11. Testing

Cross-module/system tests live under:

```text
tests/
  integration/
  contracts/
  e2e/
  safety/
  security/
  performance/
  fixtures/
```

Module-local unit tests may live inside each backend module.

`tests/safety/` is a first-class directory and must not be treated as ordinary optional test coverage.

---

# 12. Documentation

```text
docs/
  00_PROJECT_MASTER_SPEC.md
  01_PRODUCT_REQUIREMENTS.md
  02_SYSTEM_ARCHITECTURE.md
  03_REPOSITORY_STRUCTURE.md
  29_ENGINEERING_STANDARDS.md
  34_MASTER_IMPLEMENTATION_PLAN.md

  clinical/
  ai/
  interoperability/
  frontend/
  security/
  engineering/
  implementation/
  codex/
  adr/
```

Future specifications should be placed in their designated subfolder while retaining their numeric filename prefixes.

---

# 13. Infrastructure and Deployment

## `infra/`

Infrastructure definitions: Docker, Terraform/OpenTofu, monitoring, and environment templates.

## `deployments/`

Environment-specific deployment manifests for local, staging, pilot, and production.

Do not fork application source code per environment.

---

# 14. Data, Models, and Artifacts

## `data/`

Only synthetic fixtures and permitted small assets. Real patient data is prohibited in Git.

## `models/`

Model manifests/metadata or tiny test artifacts only. Large weights/checkpoints belong in model/artifact storage.

## `artifacts/`

Generated local outputs; mostly Git-ignored.

---

# 15. New Feature Placement

When a new feature is proposed:

### New bounded healthcare capability

```text
backend/app/modules/<feature>/
apps/*/src/features/<feature>/   # only if UI is needed
docs/...                         # specification
tests/...                        # cross-module tests
```

### New vendor/provider

```text
backend/app/adapters/<capability>/<provider>.py
```

Do not create a new domain module merely because a vendor changed.

### New clinical knowledge pack

```text
clinical/knowledge/<pack>/
```

### New disease model

Use the research `/ml` area and governed backend model gateway. Do not spread disease-specific conditionals across the platform.

---

# 16. Import and Dependency Rules

Other modules may consume another module's documented public contracts/interfaces. They should not import its internal infrastructure/repositories.

Circular module dependencies are prohibited. Resolve them through orchestration, events, or clearer ownership.

---

# 17. Repository Root Policy

The root is for workspace/tooling files only: README, contribution guide, lockfiles, task runner, Compose if selected, environment template, and license when decided. Feature-specific source code does not belong at root.

---

# 18. Initial Detailed Tree

```text
swasthyasetu-ai/
|
+-- .github/
|   +-- workflows/
|
+-- apps/
|   +-- patient-web/
|   +-- clinician-web/
|   +-- admin-web/
|
+-- backend/
|   +-- app/
|       +-- api/
|       |   +-- v1/
|       |   +-- dependencies/
|       |   +-- middleware/
|       |   +-- errors/
|       +-- modules/
|       |   +-- identity/
|       |   +-- sessions/
|       |   +-- consent/
|       |   +-- patients/
|       |   +-- encounters/
|       |   +-- clinical_intake/
|       |   +-- safety/
|       |   +-- mental_health/
|       |   +-- documents/
|       |   +-- provenance/
|       |   +-- summaries/
|       |   +-- self_care/
|       |   +-- providers/
|       |   +-- resources/
|       |   +-- referrals/
|       |   +-- notifications/
|       |   +-- interoperability/
|       |   |   +-- fhir/
|       |   |   +-- abdm/
|       |   +-- ml/
|       |   +-- audit/
|       |   +-- feature_management/
|       +-- shared/
|       |   +-- domain/
|       |   +-- errors/
|       |   +-- observability/
|       |   +-- security/
|       |   +-- types/
|       |   +-- utils/
|       +-- adapters/
|       |   +-- ai/
|       |   +-- ocr/
|       |   +-- speech/
|       |   +-- translation/
|       |   +-- storage/
|       |   +-- notifications/
|       |   +-- fhir/
|       |   +-- abdm/
|       |   +-- model_inference/
|       |   +-- quantum/
|       +-- events/
|       +-- config/
|
+-- workers/
+-- packages/
|   +-- contracts/
|   +-- ui/
|
+-- ml/
|   +-- classical/
|   +-- quantum/
|   +-- datasets/
|   +-- evaluation/
|   +-- registry/
|   +-- notebooks/
|
+-- clinical/
|   +-- policies/
|   +-- knowledge/
|   +-- lexicons/
|   +-- test_cases/
|   +-- localization/
|
+-- tests/
|   +-- integration/
|   +-- contracts/
|   +-- e2e/
|   +-- safety/
|   +-- security/
|   +-- performance/
|   +-- fixtures/
|
+-- docs/
|   +-- clinical/
|   +-- ai/
|   +-- interoperability/
|   +-- frontend/
|   +-- security/
|   +-- engineering/
|   +-- implementation/
|   +-- codex/
|   |   +-- CODEX_PHASE_PROMPTS/
|   +-- adr/
|
+-- infra/
|   +-- docker/
|   +-- terraform/
|   +-- monitoring/
|   +-- environments/
|
+-- deployments/
|   +-- local/
|   +-- staging/
|   +-- pilot/
|   +-- production/
|
+-- scripts/
+-- data/
|   +-- synthetic/
|   +-- fixtures/
|
+-- models/
+-- artifacts/
|
+-- README.md
+-- CONTRIBUTING.md
+-- .gitignore
+-- .editorconfig
```

---

# 19. Status

This repository structure is the baseline layout for SwasthyaSetu AI.

The provided ZIP is a **structure skeleton**, not the P1 implementation. It intentionally contains no FastAPI/Next.js application code, clinical thresholds, real provider data, patient-facing remedies, credentials, or models.

The next repository change should be the remaining P0 Codex-control documents, followed by **P1-A — repository skeleton + backend tooling**.
