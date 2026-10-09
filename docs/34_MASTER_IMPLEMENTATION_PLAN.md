# SwasthyaSetu AI
## 34 — Master Implementation Plan

**Document ID:** `SSAI-IMP-034`  
**Filename:** `34_MASTER_IMPLEMENTATION_PLAN.md`  
**Status:** Foundation / Implementation Roadmap Source of Truth  
**Version:** `1.0.0-draft`  
**Primary implementation agent:** Codex  
**Architecture:** Extensible modular monolith with extractable compute/integration services  
**Implementation style:** Incremental, vertical-slice, test-first-at-boundaries, specification-driven  
**Depends on:**
- `00_PROJECT_MASTER_SPEC.md`
- `01_PRODUCT_REQUIREMENTS.md`
- `02_SYSTEM_ARCHITECTURE.md`
- `29_ENGINEERING_STANDARDS.md`

---

# 1. Purpose

This document defines the order in which SwasthyaSetu AI is built.

It converts the project specification, PRD, system architecture, and engineering standards into a controlled sequence of implementation phases that Codex can execute without losing architectural alignment.

This plan exists to prevent the following failure modes:

- implementing everything in one enormous prompt;
- creating UI before stable contracts;
- implementing AI before deterministic safety boundaries;
- coupling future features into the first version;
- allowing ML/QML experimentation to block core product progress;
- introducing database structures ad hoc;
- letting Codex invent missing clinical policy;
- marking partially tested work as complete.

Every implementation prompt generated for Codex should map to one phase or one clearly defined sub-phase from this plan.

---

# 2. Implementation Philosophy

The project SHALL be built using the following sequence:

```text
SPECIFICATION
    ->
FOUNDATION
    ->
CORE DOMAIN
    ->
PATIENT WORKFLOW
    ->
SAFETY
    ->
CLINICIAN WORKFLOW
    ->
DOCUMENT INTELLIGENCE
    ->
LANGUAGE / SPEECH
    ->
CARE NAVIGATION
    ->
MENTAL HEALTH
    ->
SELF-CARE
    ->
INTEROPERABILITY
    ->
CLASSICAL ML
    ->
QML
    ->
FULL INTEGRATION
    ->
SECURITY / PRIVACY / PERFORMANCE HARDENING
    ->
PILOT VALIDATION
```

The project is not considered complete merely because all modules exist.

It is complete only when the modules work together under the defined safety, privacy, testing, and operational constraints.

---

# 3. Global Implementation Rules

These rules apply to every phase.

## IMP-G-001 — Inspect before editing

Codex MUST inspect the current repository before making changes.

## IMP-G-002 — Read the context pack

Every phase prompt SHALL identify the documents Codex must read.

## IMP-G-003 — Implement only current scope

Codex MUST NOT implement future phases unless explicitly requested.

## IMP-G-004 — Preserve architecture

Module boundaries, data ownership, ports/adapters, and safety precedence must remain intact.

## IMP-G-005 — Tests accompany code

Every meaningful behavior must receive appropriate tests in the same phase.

## IMP-G-006 — No invented medicine

Codex MUST NOT invent clinical thresholds, crisis policy, remedies, treatment, provider data, or validated-screening claims.

## IMP-G-007 — Migrations are explicit

Any DB schema change requires an Alembic migration.

## IMP-G-008 — External systems use adapters

No vendor SDK should leak into domain/application logic.

## IMP-G-009 — Honest status

Each phase ends as one of:

```text
COMPLETE
PARTIAL
BLOCKED
FAILED
```

## IMP-G-010 — Update progress

On completion, update the implementation/progress tracking files once they exist.

---

# 4. Phase Completion Gate

A phase is COMPLETE only if all applicable conditions hold:

```text
[ ] requirements implemented
[ ] architecture respected
[ ] public contracts typed
[ ] database migration present if required
[ ] unit tests pass
[ ] integration tests pass
[ ] contract tests pass where applicable
[ ] frontend typecheck/lint pass where applicable
[ ] backend typecheck/lint pass
[ ] security impact reviewed
[ ] privacy impact reviewed
[ ] safety impact reviewed
[ ] documentation updated
[ ] git diff inspected
[ ] no unrelated changes
[ ] known limitations reported
```

---

# 5. Blocker Policy

A phase SHALL be marked BLOCKED instead of guessing when any of the following is missing:

- required clinician-approved threshold;
- required crisis wording;
- approved self-care guidance;
- required external credentials;
- final dataset selection where the phase depends on it;
- ABDM flow decision not yet specified;
- unresolved architecture conflict;
- missing legal/privacy approval for real deployment.

Codex may still implement infrastructure/scaffolding using clearly labeled synthetic fixtures where appropriate.

---

# 6. Phase Dependency Graph

```text
P0  Documentation Freeze
 |
P1  Repository Foundation
 |
P2  Platform Kernel
 |
P3  Persistence + Outbox + Jobs
 |
+-----------------------+
|                       |
P4 Identity/Consent   P5 Domain Core
|                       |
+-----------+-----------+
            |
P6 Patient Web Foundation
            |
P7 Clinical Intake Core
            |
P8 AI Gateway + Structured Extraction
            |
P9 Physical Safety Framework
            |
P10 Clinician Dashboard
            |
P11 Document Intelligence
            |
P12 Multilingual Speech/Translation
            |
P13 Providers/Resources/Referrals
            |
P14 Mental Health / MannSetu
            |
P15 Self-Care / Ayurveda Framework
            |
P16 FHIR
            |
P17 ABDM
            |
P18 Classical ML Research Platform
            |
P19 QML Research Platform
            |
P20 Integrated Care Orchestration
            |
P21 Admin/Governance Completion
            |
P22 Security/Privacy/Resilience Hardening
            |
P23 E2E / Accessibility / Performance
            |
P24 Pilot Readiness / Release Gates
```

Some phases may proceed partially in parallel after their dependencies are stable, but Codex prompts should remain scoped.

---

# 7. Phase Groups

## Foundation Group

- P0
- P1
- P2
- P3

## Core Clinical Group

- P4
- P5
- P6
- P7
- P8
- P9
- P10

## Intelligence and Navigation Group

- P11
- P12
- P13
- P14
- P15

## Interoperability and Research Group

- P16
- P17
- P18
- P19

## Integration and Hardening Group

- P20
- P21
- P22
- P23
- P24

---

# 8. P0 — Documentation Freeze and Project Control Plane

## Objective

Prepare the specification set Codex will use as the implementation contract.

## Requirements

Cross-cutting; no application requirements implemented.

## Must exist before completion

```text
docs/
  00_PROJECT_MASTER_SPEC.md
  01_PRODUCT_REQUIREMENTS.md
  02_SYSTEM_ARCHITECTURE.md
  29_ENGINEERING_STANDARDS.md
  34_MASTER_IMPLEMENTATION_PLAN.md
```

Then create initial versions of:

```text
03_REPOSITORY_STRUCTURE.md
04_DOMAIN_MODEL.md
05_DATABASE_SCHEMA.md
06_API_CONTRACTS.md
35_PHASE_ACCEPTANCE_CRITERIA.md
36_DEPENDENCY_MAP.md
37_DECISION_LOG.md
38_PROGRESS_TRACKER.md

codex/
  CODEX_INSTRUCTIONS.md
  CODEX_WORKFLOW.md
  CODEX_CONTEXT_RULES.md
```

## In scope

- define document precedence;
- define implementation phase IDs;
- define progress status;
- establish ADR system;
- establish requirement traceability.

## Out of scope

- application code;
- framework setup;
- database;
- UI.

## Deliverables

1. documentation folder;
2. decision log initialized with architecture seeds;
3. progress tracker with P0–P24;
4. acceptance-criteria document template;
5. Codex operating instructions.

## Tests

None beyond document/link checks.

## Exit criteria

```text
[ ] all foundation specs committed
[ ] every phase has an ID
[ ] document precedence documented
[ ] no implementation ambiguity about coding rules
[ ] progress tracker initialized
```

## Prompt units

- P0-A: supporting specs
- P0-B: Codex governance files
- P0-C: traceability + progress framework

---

# 9. P1 — Repository and Tooling Foundation

## Objective

Create a clean monorepo that enforces the architecture and engineering standards before feature work begins.

## Primary requirements

- `FR-CORE-003`
- `FR-CORE-005`
- `FR-CORE-006`
- `FR-EXT-002`
- `FR-EXT-012`
- `NFR-MAINT-001` through applicable maintainability requirements
- `NFR-TEST-001`

## Context pack

Codex must read:

```text
00_PROJECT_MASTER_SPEC.md
01_PRODUCT_REQUIREMENTS.md
02_SYSTEM_ARCHITECTURE.md
03_REPOSITORY_STRUCTURE.md
29_ENGINEERING_STANDARDS.md
34_MASTER_IMPLEMENTATION_PLAN.md
```

## Target repository skeleton

```text
swasthyasetu-ai/
  apps/
    patient-web/
    clinician-web/
    admin-web/

  backend/
    app/
      modules/
      shared/
      adapters/
      events/
      api/
      config/

  workers/

  packages/
    contracts/

  ml/
    classical/
    quantum/
    evaluation/

  clinical/
    policies/
    knowledge/
    lexicons/
    test_cases/

  tests/
    integration/
    contracts/
    e2e/
    safety/

  docs/
  infra/
  scripts/
```

The exact final structure is frozen by `03_REPOSITORY_STRUCTURE.md`.

## Backend foundation

Create:

- Python project configuration;
- FastAPI application;
- Pydantic settings;
- structured logging;
- request/correlation IDs;
- base error envelope;
- health routes;
- module registration mechanism;
- dependency injection conventions.

## Frontend foundation

Create:

- Next.js patient app;
- Next.js clinician app;
- Next.js admin app;
- TypeScript strict mode;
- Tailwind;
- shared design-system package/area;
- base error/loading components.

## Tooling

Configure:

- Ruff;
- backend type checker;
- pytest;
- frontend lint;
- frontend TypeScript check;
- frontend test runner;
- Playwright skeleton;
- pre-commit optional;
- task runner/Makefile or equivalent.

## Infrastructure

Create local Docker Compose skeleton for:

- PostgreSQL;
- optional Redis placeholder;
- local object store placeholder if selected.

## CI

Create initial workflow:

```text
lint
typecheck
unit tests
frontend checks
build smoke
```

## Out of scope

- patient database entities;
- business modules;
- clinical logic;
- LLM;
- OCR.

## Tests

- API liveness;
- API readiness skeleton;
- each frontend builds;
- CI configuration syntax;
- module registry smoke test.

## Exit criteria

```text
[ ] repository installs reproducibly
[ ] backend starts
[ ] all 3 frontend apps start/build
[ ] PostgreSQL local service available
[ ] lint passes
[ ] typecheck passes
[ ] tests pass
[ ] CI passes
[ ] no domain feature implemented prematurely
```

## Prompt units

- P1-A: repo skeleton + backend tooling
- P1-B: frontend workspaces + shared tooling
- P1-C: Docker/CI + quality-gate scripts

---

# 10. P2 — Shared Platform Kernel

## Objective

Implement the minimum reusable platform services that all future modules need.

## Requirements

- `FR-CORE-004`
- `FR-CORE-005`
- `FR-CORE-006`
- `FR-CORE-009`
- `FR-CORE-010`
- `FR-EXT-003`
- `FR-EXT-004`
- `FR-EXT-005`
- `FR-EXT-011`
- observability/security NFRs applicable to platform.

## Components

### Shared IDs and time

- UUID types/helpers;
- timezone-aware UTC utilities;
- correlation IDs.

### Error model

- domain base error;
- application error;
- dependency errors;
- centralized FastAPI mapping.

### Actor context

Base actor representation for later authorization.

### Feature flags

Implement provider-neutral feature-flag interface.

Initial implementation may be configuration/database-backed.

### Capability registry

Implement architecture-approved capability registration/discovery.

### Module manifest

Define typed module metadata.

### Configuration

Typed sections:

```text
app
database
security
object_storage
llm
ocr
speech
fhir
abdm
observability
features
```

### Observability

- structured logs;
- OpenTelemetry hooks/skeleton;
- request metrics;
- content-free tracing.

## Explicit constraints

Shared kernel must stay generic.

No clinical business rules.

## Tests

- feature flag defaults;
- module registration;
- error serialization;
- correlation ID propagation;
- typed settings validation;
- logs do not dump request bodies by default.

## Exit criteria

```text
[ ] modules can register explicitly
[ ] capabilities can be resolved through a typed interface
[ ] errors use one stable envelope
[ ] feature flags have safe defaults
[ ] correlation IDs propagate
[ ] observability does not require sensitive payloads
```

## Prompt units

- P2-A: shared types/errors/config
- P2-B: module/capability registry
- P2-C: observability + feature flags

---

# 11. P3 — Persistence, Migrations, Events, Outbox and Background Jobs

## Objective

Create the platform persistence and asynchronous-work foundation before feature modules begin writing data.

## Requirements

- `FR-CORE-005`
- `FR-CORE-009`
- `FR-EXT-006`
- `NFR-MAINT-004`
- `NFR-RES-006`
- relevant audit/observability requirements.

## Components

### SQLAlchemy

Configure:

- async engine;
- session factory;
- base metadata;
- naming conventions;
- transaction helpers.

### Alembic

Create initial migration and migration quality checks.

### Outbox

Create:

- event envelope;
- outbox table;
- dispatcher interface;
- processing state;
- retry metadata.

### Internal event bus

Initial event transport can be in-process/worker-driven.

### Job abstraction

Create:

```text
JobDispatcher
JobRequest
JobStatus
```

Initial implementation may use in-process/local worker or selected lightweight queue.

### Object storage port

Define interface and local-development adapter.

## Out of scope

- medical document business behavior;
- patient schema;
- referral jobs.

## Tests

- empty DB -> Alembic head;
- transaction rollback;
- outbox event written atomically;
- duplicate event handler/idempotency fixture;
- job dispatch fake;
- object-storage mock/local adapter.

## Exit criteria

```text
[ ] DB foundation stable
[ ] migrations run from empty DB
[ ] outbox available
[ ] event schemas versioned
[ ] worker can execute a sample job
[ ] no domain-specific table ownership violations
```

## Prompt units

- P3-A: SQLAlchemy/Alembic
- P3-B: event envelope/outbox
- P3-C: worker/job abstraction/object storage

---

# 12. P4 — Identity, Sessions, Authorization Baseline and Consent

## Objective

Implement the minimum identity/session/consent infrastructure required by every patient workflow.

## Requirements

### Identity/session

- `FR-IDENT-001` through `FR-IDENT-007`

### Consent

- `FR-CONSENT-001` through `FR-CONSENT-009`

### Security

Applicable:
- `NFR-SEC-003`
- `NFR-SEC-004`
- `NFR-SEC-009`

## Modules

```text
identity
sessions
consent
```

## Features

### Session

- pseudonymous session;
- authenticated-session abstraction;
- kiosk-session mode;
- expiry;
- close;
- safe token generation.

### Actor/roles baseline

Initial roles:

```text
patient
pseudonymous_user
clinician
resource_admin
clinical_reviewer
system_admin
researcher
```

Full auth provider integration may remain replaceable.

### Consent

Support:

- notice version;
- purpose;
- scope;
- granted_at;
- revoked_at;
- subject/session reference;
- referral-specific consent later;
- consent check service.

## Important implementation rule

Do not implement full ABDM consent here.

Create extensible consent domain first.

## APIs

Initial:

```text
POST /api/v1/sessions
GET  /api/v1/sessions/{id}
POST /api/v1/sessions/{id}/close

POST /api/v1/consents
POST /api/v1/consents/{id}/revoke
GET  /api/v1/consents
```

Final contract governed by `06_API_CONTRACTS.md`.

## Tests

- unpredictable session token;
- expired session rejected;
- consent grant;
- consent revoke;
- consent scope;
- unauthorized cross-subject access;
- pseudonymous flow needs no name.

## Exit criteria

```text
[ ] pseudonymous session works
[ ] session lifecycle works
[ ] actor context available
[ ] consent is versioned
[ ] revocation is represented
[ ] consent checks are centralized
[ ] no duplicate module-local consent logic
```

## Prompt units

- P4-A: sessions
- P4-B: identity/authz baseline
- P4-C: consent domain + APIs

---

# 13. P5 — Patient, Encounter and Longitudinal Clinical Domain

## Objective

Create the authoritative patient/encounter domain that later intake, OCR, FHIR, and clinicians will share.

## Requirements

- `FR-PAT-001` through `FR-PAT-014`
- `FR-ENC-001` through `FR-ENC-006`
- `FR-PROV-001` through `FR-PROV-007`

## Modules

```text
patients
encounters
provenance
```

## Domain model

Initial typed concepts:

```text
Patient
PatientIdentifier
Encounter
ClinicalFact
Problem
Medication
Allergy
Procedure
Observation
Investigation
FactProvenance
VerificationState
```

Exact schema governed by `04_DOMAIN_MODEL.md` and `05_DATABASE_SCHEMA.md`.

## Key requirement

Do not make one giant JSON patient-history column.

Use explicit domain structures with extension points.

## Provenance

Every AI-derived fact supports:

```text
source_type
source_id
confidence
verification_state
created_at
superseded_by
```

## Longitudinal timeline

Implement a query/read model capable of returning chronologically ordered events.

Timeline may initially be computed or projected.

## APIs

Representative:

```text
POST /api/v1/patients
GET  /api/v1/patients/{id}
GET  /api/v1/patients/{id}/timeline

POST /api/v1/encounters
GET  /api/v1/encounters/{id}
POST /api/v1/encounters/{id}/complete
```

## Tests

- patient creation;
- encounter lifecycle;
- invalid transition;
- medication/allergy representation;
- fact provenance;
- clinician-confirmed state cannot be silently overwritten by extracted fact;
- timeline ordering.

## Exit criteria

```text
[ ] one authoritative patient domain exists
[ ] encounter lifecycle explicit
[ ] provenance first-class
[ ] confirmation/rejection states supported
[ ] timeline query works
[ ] other modules can consume patient context only through public interfaces
```

## Prompt units

- P5-A: domain types/entities
- P5-B: persistence/migrations
- P5-C: timeline/provenance services + APIs

---

# 14. P6 — Patient Web / PWA Foundation

## Objective

Build the patient-facing shell before implementing complex AI interactions.

## Requirements

- core patient UX;
- `NFR-ACCESS-001` through `NFR-ACCESS-007`
- `NFR-UX-001`, `NFR-UX-004`, `NFR-UX-006`
- identity/consent requirements from P4.

## Screens

Initial:

```text
/
 /start
 /consent
 /language
 /encounter
 /documents
 /results
 /urgent-help
 /referrals
```

Routes may evolve.

## Features

- responsive layout;
- PWA shell;
- language selector;
- consent UI;
- session start;
- urgent-help persistent entry point architecture;
- accessible shared components;
- feature-disabled/degraded states;
- error boundary.

## Important rule

Do not build fake clinical features just to fill UI.

Use real backend contracts or clearly labeled fixtures in development.

## Tests

- accessibility smoke;
- keyboard navigation;
- consent journey;
- session journey;
- mobile viewport;
- urgent-help control always discoverable on relevant screens.

## Exit criteria

```text
[ ] patient shell usable
[ ] session/consent connected
[ ] accessibility primitives established
[ ] feature architecture established
[ ] no sensitive data stored in browser localStorage by default
```

## Prompt units

- P6-A: design system/app shell
- P6-B: onboarding/session/consent
- P6-C: accessibility + PWA baseline

---

# 15. P7 — Clinical Intake Engine Without LLM Dependency

## Objective

Implement the structured clinical intake domain before adding AI.

## Requirements

- `FR-INTAKE-001` through `FR-INTAKE-032`

## Modules

```text
clinical_intake
```

## Initial functions

- start intake;
- record structured answer;
- retrieve current state;
- determine missing required field;
- register questionnaire/complaint-specific question packs;
- complete draft intake.

## Data model

Support:

```text
chief complaint
HPI
past medical history
past surgical history
medications
allergies
family history
personal history
review of systems
prior investigations
```

## Adaptive logic

At this phase, use deterministic/configured question flow.

Do not require LLM.

## Extension framework

Create registries for:

- complaint-specific questions;
- specialty question packs;
- AYUSH intake extension.

## AYUSH

Implement schema/plugin capability only.

Do not invent clinical assessment content not defined by approved specification.

## UI

Patient can:

- type/select complaint;
- answer structured/touch questions;
- resume current intake;
- review draft.

## Tests

- HPI fields;
- missing-field logic;
- known-history reuse;
- contradiction representation;
- questionnaire registration;
- AYUSH extension registration;
- no cross-module direct DB access.

## Exit criteria

```text
[ ] full structured case-taking possible without LLM
[ ] intake state persists
[ ] question packs extensible
[ ] existing history can prefill/contextualize
[ ] draft remains non-diagnostic
```

## Prompt units

- P7-A: intake domain/schema
- P7-B: deterministic adaptive engine
- P7-C: APIs + patient UI

---

# 16. P8 — AI Gateway and Structured Extraction

## Objective

Add LLM-assisted conversational extraction without giving the LLM decision authority.

## Requirements

- `FR-CORE-007`
- `FR-CORE-008`
- applicable `FR-INTAKE`
- `FR-MH-005` architecture only
- `NFR-TEST-009`
- `NFR-SEC-012`
- `NFR-SEC-013`

## Components

### AI gateway

- provider port;
- adapter;
- timeout;
- model metadata;
- structured-output parser;
- bounded retry;
- failure mapping;
- telemetry.

### Clinical intake extractor

Input:

```text
recent patient utterance
minimal structured encounter context
target schema
```

Output:

```text
candidate clinical facts
missing info
contradictions
confidence
```

## Rules

LLM output is candidate data only.

It must pass:

```text
parse
 -> Pydantic validation
 -> domain validation
 -> provenance creation
```

## Prompt assets

Version:

```text
prompt_id
prompt_version
schema_version
```

## Mock adapter

Required for offline tests.

## UI

Enable conversational free-text intake integrated into P7 state.

## Tests

- valid structured extraction;
- malformed JSON;
- timeout;
- missing field;
- prompt injection in patient text;
- hallucinated unsupported field ignored/rejected;
- provenance preserved;
- no AI diagnosis field accepted.

## Exit criteria

```text
[ ] provider replacement possible
[ ] clinical intake works with mock adapter offline
[ ] all LLM outputs schema validated
[ ] failure produces degraded behavior
[ ] no final triage delegated to LLM
```

## Prompt units

- P8-A: AI gateway + port/adapters
- P8-B: clinical extractor schema/prompt package
- P8-C: integration into intake + regression tests

---

# 17. P9 — Physical-Health Safety Framework and Deterministic Routing

## Objective

Implement the safety engine architecture and route framework before enabling self-care or predictive clinical actions.

## Requirements

- `SAFE-001` through `SAFE-010`
- `FR-SAFE-001` through `FR-SAFE-012`

## Module

```text
safety
```

## Route types

```text
EMERGENCY
PRIORITY_REVIEW
ROUTINE_CARE
SUPPORTED_SELF_CARE
CLARIFICATION_REQUIRED
```

## Inputs

Only validated structured signals.

## Output

```text
route
reason_codes
policy_id
policy_version
requires_clarification
blocks_self_care
```

## Policy registry

Implement:

- policy ID;
- version;
- status;
- configuration validation;
- activation interface.

## Critical caveat

If clinician-approved real physical red-flag rules are not yet provided, implement:

- engine;
- policy schema;
- synthetic non-production fixtures;
- hard-override mechanics;
- tests;

but mark real clinical policy content BLOCKED.

## UI

Patient result architecture can render:

- urgent action;
- priority review;
- routine care;
- clarification.

Use synthetic/dev policy only in non-production environment.

## Tests

- hard override precedence;
- model output cannot downgrade emergency;
- self-care blocked;
- ambiguous input;
- policy version persisted;
- missing policy fails safe;
- deterministic repeatability.

## Exit criteria

```text
[ ] engine complete
[ ] policy versions stored
[ ] reason codes deterministic
[ ] hard override tested
[ ] real clinical policy clearly distinguished from synthetic fixtures
```

## Prompt units

- P9-A: decision types/policy registry
- P9-B: deterministic engine + tests
- P9-C: UI/result integration + degraded mode

---

# 18. P10 — Clinician Dashboard and Clinical Confirmation Loop

## Objective

Make the system useful to a clinician before adding more AI features.

## Requirements

- `FR-CLIN-001` through `FR-CLIN-013`
- `FR-SUM-001` through `FR-SUM-008`
- provenance requirements.

## Modules/UI

```text
summaries
clinician-web
```

## Features

### Clinician queue

Display encounters appropriate to authorization.

### Patient overview

- encounter;
- chief complaint;
- HPI;
- medications;
- allergies;
- history;
- timeline.

### Summary

Generate structured draft from existing facts.

LLM summarization may use the AI gateway but cannot create new facts.

### Confirmation workflow

Clinician can:

```text
confirm
correct
reject
```

AI-extracted facts.

## Important rule

Correction creates auditable provenance/state transition.

Do not silently overwrite extraction history.

## UI extension slots

Create locations for future:

- document panel;
- safety panel;
- risk model panel;
- referral panel;
- future feature modules.

## Tests

- clinician authz;
- assigned/authorized data;
- confirm/reject/correct;
- summary never creates new condition not in structured context;
- provenance source link;
- patient cannot access clinician-only endpoints.

## Exit criteria

```text
[ ] clinician can review full intake
[ ] clinician can correct AI facts
[ ] summary is editable draft
[ ] provenance visible
[ ] feature panel architecture established
```

## Prompt units

- P10-A: summary domain/backend
- P10-B: clinician read model/API
- P10-C: clinician-web
- P10-D: correction/provenance E2E

---

# 19. P11 — Document Upload, OCR and Medical Document Intelligence

## Objective

Implement the SIH medical-document workflow end to end.

## Requirements

- `FR-DOC-001` through `FR-DOC-023`
- provenance requirements.

## Components

### Upload

- controlled upload;
- object storage;
- validation;
- checksum;
- processing state.

### OCR port

Implement:

```text
OCRPort
MockOCRAdapter
PaddleOCRAdapter or selected first adapter
```

### Pipeline

```text
upload
 -> validate
 -> queue
 -> preprocess
 -> OCR
 -> classify
 -> extract entities
 -> validate
 -> persist candidate facts
 -> needs review / available
```

## Document processor registry

Processors:

```text
PrescriptionProcessor
LabReportProcessor
DischargeSummaryProcessor
DiagnosticReportProcessor
ImagingReportProcessor
ReferralLetterProcessor
```

Not all processors need advanced extraction in first sub-phase.

## Patient/clinician UI

- upload/camera;
- processing status;
- source preview;
- extracted fields;
- confirm/reject;
- timeline integration.

## Tests

- file validation;
- malicious/unsupported type;
- OCR timeout;
- parser failure;
- low confidence;
- duplicate checksum;
- medication extraction fixture;
- lab extraction fixture;
- no silent overwrite of confirmed fact;
- object cleanup where applicable.

## Exit criteria

```text
[ ] document upload works
[ ] async processing status works
[ ] OCR adapter replaceable
[ ] candidate facts retain source/provenance
[ ] clinician can inspect source
[ ] failure does not break intake
```

## Prompt units

- P11-A: object storage/upload
- P11-B: OCR adapter/job
- P11-C: classification/parser registry
- P11-D: medical entity extraction
- P11-E: UI/review/timeline integration

---

# 20. P12 — Multilingual Speech, Translation and Language Layer

## Objective

Add voice and multilingual input without coupling clinical logic to any one speech provider.

## Requirements

- `FR-LANG-001` through `FR-LANG-012`
- relevant accessibility requirements.

## Module/capabilities

```text
language
speech.transcribe
speech.synthesize
translation.translate
```

## Ports

```text
SpeechToTextPort
TextToSpeechPort
TranslationPort
LanguageDetectionPort
```

## Initial languages

- English;
- Hindi;
- Hinglish / Romanized Hindi support where technically feasible.

## Workflow

```text
audio
 -> STT
 -> original transcript
 -> language metadata
 -> optional normalization/translation
 -> clinical extraction
```

## Rules

- original text preserved where clinically relevant;
- failed ASR is not a clinical fact;
- text/touch fallback always available;
- safety-critical translation copy must be approved separately.

## Tests

- adapter timeout;
- language switching;
- romanized Hindi fixture;
- confidence metadata;
- fallback to text;
- translated structured extraction retains original.

## Exit criteria

```text
[ ] voice intake is optional, not mandatory
[ ] language providers replaceable
[ ] original wording preserved
[ ] supported-language metadata recorded
[ ] failure falls back safely
```

## Prompt units

- P12-A: language abstractions
- P12-B: first ASR/TTS/translation adapters
- P12-C: patient UI voice integration
- P12-D: multilingual regression fixtures

---

# 21. P13 — Provider Directory, Resource Registry and Referral Lifecycle

## Objective

Implement verified care navigation without allowing AI-fabricated providers.

## Requirements

### Directory
- `FR-DIR-001` through `FR-DIR-017`

### Referrals
- `FR-REF-001` through `FR-REF-013`

### Notifications
- applicable `FR-NOTIF-*`

## Modules

```text
providers
resources
referrals
notifications
```

## Provider registry

Support:

```text
name
specialty
facility
contact
booking
location
languages
teleconsultation
hours
source
verified_at
expires_at
status
```

## Resource registry

Support:

- crisis resources;
- counselling resources;
- hospitals;
- public support;
- institution-specific resources.

## Provider routing

At this phase implement:

```text
care category
 -> specialty/service type
 -> registry query
 -> transparent filters
```

Do not implement an opaque LLM ranking.

## Referral state machine

```text
OFFERED
CONSENTED
SENT
ACKNOWLEDGED
SCHEDULED
COMPLETED
DECLINED
UNREACHABLE
EXPIRED
FAILED
```

## Real provider-data caveat

If a verified production source is not yet selected:

- use synthetic development registry;
- clearly label;
- implement verification workflow;
- do not invent real contacts.

## Tests

- stale provider excluded/warned;
- provider source/verification required;
- LLM cannot supply contact data;
- consent required before external send;
- duplicate referral prevented;
- webhook retry/idempotency;
- status transitions.

## Exit criteria

```text
[ ] verified-registry architecture works
[ ] specialty-first routing works
[ ] referrals are consented/minimal
[ ] status lifecycle works
[ ] no raw transcript sent by default
```

## Prompt units

- P13-A: providers/resources domain
- P13-B: search/routing
- P13-C: referral domain/state machine
- P13-D: notification/adapter
- P13-E: patient/admin UI

---

# 22. P14 — MannSetu Mental-Health Module

## Objective

Implement mental-health first-contact using the safety architecture from the MannSetu design.

## Requirements

- `FR-MH-001` through `FR-MH-020`
- global `SAFE-*`
- relevant privacy/accessibility/security NFRs.

## Module

```text
mental_health
```

## Architecture

```text
user message
   |
local language-aware safety backstop
   |
LLM structured signal extractor
   |
schema validation
   |
deterministic mental-health policy
   |
A / B / C / clarify / degraded
```

## Routes

```text
A = self-help / psychoeducation + optional professional support
B = professional/counsellor referral
C = urgent/crisis human support
```

## Critical rule

No model score can override an explicit high-risk condition in the approved policy.

## Crisis fallback

Must work if:

- LLM times out;
- JSON invalid;
- model unavailable;
- normal conversation service degraded.

## Crisis resources

Read only from:

- verified resource registry;
- bundled approved fallback.

## Policy caveat

If final clinician-approved policy and wording are unavailable:

Implement:

- signal schema;
- policy engine;
- synthetic fixtures;
- backstop interface;
- fallback mechanics;
- UI;
- regression framework;

but production mental-health policy remains BLOCKED.

## Safety dataset

Create a synthetic/clinician-ready evaluation structure covering:

- explicit current intent;
- historical mention;
- negation;
- quotes about others;
- ambiguity;
- Hindi/Hinglish variants;
- prompt injection;
- parser failure;
- resource expiry.

## Tests

This phase requires strong safety tests.

## Exit criteria

```text
[ ] pseudonymous entry works
[ ] structured signal extraction works
[ ] LLM cannot choose route directly
[ ] deterministic policy works
[ ] crisis fallback independent
[ ] verified resource lookup
[ ] referral handoff integrates with P13
[ ] safety tests pass for configured test policy
```

## Prompt units

- P14-A: signal schema/extractor
- P14-B: safety backstop
- P14-C: deterministic route engine
- P14-D: crisis UI/fallback
- P14-E: referral integration
- P14-F: adversarial safety suite

---

# 23. P15 — Self-Care and Ayurveda / Gharelu Guidance Framework

## Objective

Implement the safe self-care architecture without allowing unrestricted generated medical advice.

## Requirements

- `FR-SELF-001` through `FR-SELF-017`
- `SAFE-008`
- `SAFE-009`

## Module

```text
self_care
```

## Components

### Knowledge pack format

Fields:

```text
guidance_id
version
eligible_context
content
contraindications
medication_conflicts
age_rules
pregnancy_rules
duration_limit
escalation_conditions
source
review_status
verified_at
translations
```

### Eligibility

Order:

```text
physical safety
 -> context completeness
 -> exclusions
 -> contraindications
 -> approved knowledge retrieval
```

### Personalization

May use:

- allergy;
- medication;
- chronic conditions;
- age;
- other explicitly available governed context.

## Critical caveat

If clinically approved guidance content is not available:

- implement engine/schema/admin/review;
- use synthetic non-medical content fixtures;
- do not invent patient-facing remedies.

## UI

Display:

- supportive framing;
- source/category;
- warning/contraindication;
- duration;
- stop/escalate conditions;
- doctor navigation option.

## Tests

- red flag blocks;
- contraindication blocks;
- unapproved guidance hidden;
- expired version hidden;
- LLM cannot introduce unseen remedy;
- patient history changes eligibility.

## Exit criteria

```text
[ ] self-care is retrieval-based
[ ] safety gate precedes content
[ ] knowledge versioned
[ ] approval state enforced
[ ] patient context can safely filter
[ ] no unrestricted generation
```

## Prompt units

- P15-A: knowledge schema/pack loader
- P15-B: eligibility engine
- P15-C: admin review workflow
- P15-D: patient UI + provider escalation
- P15-E: safety regression suite

---

# 24. P16 — FHIR Interoperability Layer

## Objective

Map SwasthyaSetu internal data to/from FHIR without contaminating the internal domain model.

## Requirements

- `FR-FHIR-001` through `FR-FHIR-011`

## Module

```text
interoperability.fhir
```

## Mappings

Initial:

```text
Patient
Encounter
Observation
AllergyIntolerance
MedicationStatement / MedicationRequest
DiagnosticReport
DocumentReference
Consent
```

## Architecture

```text
internal DTO
 -> mapper
 -> FHIR resource
 -> validator
 -> gateway adapter
```

## Tools

Select FHIR library/server/client only behind adapter.

## Tests

- mapping unit tests;
- validation;
- representative bundle export;
- import provenance;
- unknown field handling;
- no risk assessment accidentally mapped as confirmed condition.

## Exit criteria

```text
[ ] internal model remains independent
[ ] FHIR resources validate
[ ] imports retain provenance
[ ] adapter replaceable
```

## Prompt units

- P16-A: FHIR DTO/mapping layer
- P16-B: validation/gateway
- P16-C: export/import APIs + tests

---

# 25. P17 — ABDM / ABHA Integration

## Objective

Implement ABDM-specific workflows only after the generic FHIR boundary is stable.

## Requirements

- `FR-ABDM-001` through `FR-ABDM-007`

## Module

```text
interoperability.abdm
```

## Precondition

A detailed `21_ABDM_INTEGRATION_SPEC.md` must exist.

Codex must not infer current ABDM API flows from memory.

## Scope

Depending on approved spec:

- ABHA-enabled identity linkage;
- consent-aware exchange;
- sandbox integration;
- FHIR bundle exchange;
- error handling;
- provenance;
- audit.

## Design rule

ABDM is an adapter.

Core patient history must continue if ABDM is unavailable.

## Tests

- mock adapter;
- sandbox tests if credentials exist;
- consent required;
- failure isolation;
- FHIR validation;
- retry/idempotency.

## Exit criteria

```text
[ ] sandbox flow verified where possible
[ ] ABDM failures isolated
[ ] consent enforced
[ ] no core-domain vendor coupling
```

## Prompt units

- P17-A: approved flow interfaces
- P17-B: sandbox adapter
- P17-C: sync/use-case integration
- P17-D: failure/security/audit tests

---

# 26. P18 — Classical ML Research Platform

## Objective

Implement the baseline research environment required before QML.

## Requirements

- `FR-ML-001` through `FR-ML-017`

## Components

```text
dataset registry
preprocessing
feature engineering
feature selection
training
evaluation
experiment tracking
model registry
model cards
```

## Candidate baselines

Depending on selected task:

```text
logistic regression
random forest
XGBoost
SVM
MLP
```

Not every model is mandatory for every task.

## Dataset gate

Before real experiment implementation, select and document:

- dataset;
- license;
- target;
- features;
- split;
- inclusion/exclusion.

If not selected, build generic framework with synthetic dataset.

## Reproducibility

Record:

- dataset version;
- code commit;
- seed;
- parameters;
- metrics;
- artifacts.

## Metrics

Support:

- sensitivity;
- specificity;
- precision/recall/F1;
- AUROC/AUPRC;
- calibration where appropriate.

## Production separation

Models stay EXPERIMENTAL unless explicitly promoted.

## Tests

- preprocessing does not fit on test;
- deterministic split;
- metric calculations;
- artifact registration;
- no research model auto-activation.

## Exit criteria

```text
[ ] one end-to-end classical experiment runs reproducibly
[ ] experiment metadata stored
[ ] model candidate registered
[ ] evaluation report generated
```

## Prompt units

- P18-A: dataset/experiment registry
- P18-B: preprocessing/evaluation
- P18-C: classical model baselines
- P18-D: model registry/model cards
- P18-E: first approved benchmark task

---

# 27. P19 — Hybrid Quantum Machine Learning Platform

## Objective

Implement the SIH hybrid QML research requirement using the same benchmark discipline as classical ML.

## Requirements

- `FR-QML-001` through `FR-QML-018`

## Precondition

P18 baseline exists.

## Components

### Quantum backend port

Adapters:

```text
simulator
optional future hardware
```

### Encoding

Implement documented encoding strategy appropriate to selected feature dimension.

### Candidate models

At least one required:

```text
VQC
```

Additional candidates:

```text
QNN
QSVM / quantum kernel
```

as scope allows.

## Fair comparison

Use same:

```text
target
split
preprocessing assumptions
metrics
```

as classical benchmark.

## Record

- qubits;
- encoding;
- circuit depth;
- shots;
- optimizer;
- backend;
- runtime;
- seed;
- framework version.

## Explainability

Expose available task/model metadata without overstating interpretability.

## Tests

- circuit builds;
- simulator inference;
- reproducibility;
- metric parity pipeline;
- production isolation;
- no safety override.

## Exit criteria

```text
[ ] at least one hybrid QML task runs
[ ] results comparable with classical baseline
[ ] experiment metadata complete
[ ] no quantum advantage claim hard-coded
```

## Prompt units

- P19-A: quantum backend abstraction
- P19-B: VQC pipeline
- P19-C: evaluation comparison
- P19-D: optional QNN/QSVM
- P19-E: research dashboard/result visualization

---

# 28. P20 — Integrated Care Orchestration and Unified Patient Journey

## Objective

Connect all implemented modules into one coherent product rather than a collection of demos.

## Requirements

Cross-cutting core product acceptance outcomes:

- `AC-PROD-001` through `AC-PROD-014`

## Components

### Care decision orchestrator

Combines structured module outputs without becoming a god service.

Inputs may include:

```text
physical safety decision
mental-health decision
self-care eligibility
provider category
risk assessment
patient intent
```

## Output

A typed set of recommended next actions.

Example:

```text
URGENT_HELP
PRIORITY_CLINICIAN
ROUTINE_CLINICIAN
SELF_CARE
MENTAL_HEALTH_REFERRAL
DOCUMENT_REVIEW
CLARIFICATION
```

## Rules

- safety routes dominate;
- risk model does not override hard safety;
- self-care blocked when required;
- provider results only from registry;
- actions retain provenance.

## End-to-end patient flow

```text
Start
 -> consent/language
 -> load patient context
 -> presenting concern
 -> intake
 -> safety
 -> optional documents
 -> applicable mental-health/risk/self-care modules
 -> next actions
 -> provider/referral
 -> clinician handoff
 -> continuity
```

## RAG

Introduce RAG only for approved contexts that demonstrably need it, such as:

- patient document retrieval;
- approved knowledge retrieval.

Do not create generic "medical RAG brain".

## Tests

Full integration/E2E:

- low-risk flow;
- physical urgent flow;
- document-enhanced flow;
- history changes self-care eligibility;
- mental-health referral;
- LLM outage;
- OCR outage;
- provider outage;
- QML unavailable.

## Exit criteria

```text
[ ] product feels unified
[ ] no module bypasses safety
[ ] longitudinal context reused
[ ] module failures isolated
[ ] actions explainable
```

## Prompt units

- P20-A: care action contracts/orchestrator
- P20-B: patient journey integration
- P20-C: longitudinal/RAG retrieval where justified
- P20-D: cross-module E2E suite

---

# 29. P21 — Admin, Governance and Clinical Review Completion

## Objective

Complete the governance surfaces needed to operate the system safely.

## Requirements

- `FR-ADMIN-001` through `FR-ADMIN-010`
- `FR-AUDIT-001` through `FR-AUDIT-007`

## Admin capabilities

- provider/resource management;
- verification/expiry;
- self-care knowledge version/status;
- active policy/version visibility;
- model version/approval visibility;
- referral dashboard;
- feature flags;
- audit viewer;
- operational health.

## Clinical review

Support controlled review queues for:

- low-confidence extracted facts;
- document extraction;
- mental-health pilot review;
- route disagreements.

## Maker-checker

Implement for high-impact content where specified or scaffold workflow for later.

## Tests

- admin authz;
- clinical reviewer restrictions;
- audit entry creation;
- ordinary admin cannot directly bypass policy governance;
- no transcript search by default.

## Exit criteria

```text
[ ] governance can manage resources/content safely
[ ] audit events available
[ ] privileged access role-separated
[ ] clinical review workflow exists
```

## Prompt units

- P21-A: admin backend
- P21-B: admin-web
- P21-C: clinical review queue
- P21-D: audit/maker-checker

---

# 30. P22 — Security, Privacy, Retention and Resilience Hardening

## Objective

Turn the integrated application into a defensible pilot-ready system.

## Requirements

All relevant:

- `NFR-SEC-*`
- `PRIV-*`
- `NFR-RES-*`
- audit/retention requirements.

## Workstreams

### Threat model

Complete `28_THREAT_MODEL.md`.

### Access control

- RBAC;
- object-level authorization;
- admin MFA integration or enforceable interface;
- service-account permissions.

### Web security

- CSP;
- CSRF if cookie auth;
- CORS;
- security headers;
- rate limits;
- upload security.

### Data protection

- encryption;
- secret manager abstraction;
- sensitive-log review;
- PII redaction where applicable.

### Retention

Implement:

- retention policy metadata;
- purge jobs;
- object-store deletion;
- vector/search deletion if used;
- purge telemetry.

### Kill switches

Test independent disabling of:

- LLM;
- referral delivery;
- self-care;
- QML inference;
- stale resource;
- specific language/model if needed.

### Dependency failure

Test:

- DB;
- LLM;
- OCR;
- speech;
- FHIR;
- ABDM;
- provider integration.

## Tests

- authz matrix;
- IDOR;
- XSS;
- SQL injection guard;
- upload abuse;
- prompt injection;
- rate limit;
- purge;
- rollback/kill-switch smoke.

## Exit criteria

```text
[ ] high-risk security findings addressed
[ ] retention executes
[ ] secrets absent from repo
[ ] sensitive logs reviewed
[ ] kill switches verified
[ ] degraded modes honest
```

## Prompt units

- P22-A: threat model/authz audit
- P22-B: security controls
- P22-C: retention/deletion
- P22-D: kill switches/resilience
- P22-E: security regression suite

---

# 31. P23 — Full E2E, Accessibility, Reliability and Performance Validation

## Objective

Validate the system as a whole before pilot-readiness review.

## Requirements

- `NFR-TEST-*`
- `NFR-ACCESS-*`
- `NFR-PERF-*`
- `NFR-OBS-*`

## E2E journeys

At minimum:

1. structured clinical intake;
2. conversational intake;
3. document upload/extraction;
4. red-flag urgent route;
5. self-care eligible;
6. self-care blocked;
7. doctor search;
8. referral lifecycle;
9. clinician confirmation;
10. mental-health route A;
11. route B referral;
12. route C/crisis fallback;
13. LLM outage;
14. OCR outage;
15. speech fallback;
16. FHIR export;
17. classical model research run;
18. QML research run.

## Accessibility

Test:

- keyboard;
- screen-reader semantics;
- high contrast;
- focus;
- crisis-button discoverability;
- large touch targets;
- language switch.

## Performance

Measure:

- API latency;
- LLM latency;
- document queue;
- provider search;
- DB query hotspots.

## Reliability

- worker restart;
- duplicate event;
- retry;
- outbox recovery;
- projection rebuild if applicable.

## Exit criteria

```text
[ ] critical E2E journeys pass
[ ] accessibility blockers fixed
[ ] performance baseline documented
[ ] resilience tests pass
[ ] observability dashboards/queries exist
```

## Prompt units

- P23-A: E2E suite
- P23-B: accessibility audit
- P23-C: performance/load
- P23-D: resilience/recovery

---

# 32. P24 — Pilot Readiness, Release Gates and Operational Readiness

## Objective

Prepare a controlled pilot, not merely a software demo.

## Requirements

- relevant research governance;
- safety evaluation;
- operational readiness.

## Pre-pilot documents

Must exist:

```text
clinical policy sign-off
mental-health policy sign-off
self-care content approval
verified resource registry
privacy notice
consent text
threat model
incident runbook
data retention policy
release checklist
pilot protocol
model cards
dataset cards
```

## Safety evaluation

Run:

- clinician-authored safety set;
- multilingual safety set;
- route concordance;
- critical false negatives;
- resource correctness;
- clarification utility.

## Operational rehearsal

Test:

- rollback;
- policy rollback;
- model rollback;
- resource disable;
- incident escalation;
- backup/restore;
- purge failure;
- provider outage.

## Release decision

Final status:

```text
GO
CONDITIONAL GO
NO-GO
```

based on pre-registered criteria.

## Exit criteria

A live human pilot must NOT begin solely because software tests pass.

Required governance/clinical/ethical prerequisites must be satisfied.

---

# 33. Requirement-to-Phase Mapping Summary

| Requirement family | Primary phase |
|---|---|
| `FR-CORE-*` | P1–P3, P20 |
| `FR-EXT-*` | P1–P3 + all feature phases |
| `FR-IDENT-*` | P4 |
| `FR-CONSENT-*` | P4 |
| `FR-PAT-*` | P5 |
| `FR-ENC-*` | P5 |
| `FR-PROV-*` | P5 |
| `FR-INTAKE-*` | P7–P8 |
| `FR-LANG-*` | P12 |
| `FR-SAFE-*` | P9 |
| `FR-CLIN-*` | P10 |
| `FR-SUM-*` | P10 |
| `FR-DOC-*` | P11 |
| `FR-DIR-*` | P13 |
| `FR-REF-*` | P13 |
| `FR-NOTIF-*` | P13 / later expansion |
| `FR-MH-*` | P14 |
| `FR-SELF-*` | P15 |
| `FR-FHIR-*` | P16 |
| `FR-ABDM-*` | P17 |
| `FR-ML-*` | P18 |
| `FR-QML-*` | P19 |
| `FR-RAG-*` | P20 where justified |
| `FR-ADMIN-*` | P21 |
| `FR-AUDIT-*` | P3/P4/P21 |
| `NFR-SEC-*` | continuous + P22 |
| `PRIV-*` | continuous + P22 |
| `NFR-TEST-*` | continuous + P23 |
| `NFR-ACCESS-*` | P6 + P23 |
| `NFR-PERF-*` | P23 |
| `NFR-OBS-*` | P2 onward |

---

# 34. Parallelization Guidance

Codex should not create uncontrolled parallel branches.

However, after stable contracts exist:

## Safe partial parallelism

After P5:

- P6 patient frontend can proceed;
- some P10 clinician read-model planning can begin.

After P8/P9:

- P11 OCR;
- P12 language;
- P13 providers;

can be developed in separate branches if integration contracts are stable.

P18 classical ML may begin earlier as an isolated research branch once P1/P2 foundations and dataset spec exist, because it does not need to block clinical modules.

P19 must still depend on P18 benchmark discipline.

---

# 35. New Feature Insertion Protocol

New ideas are expected.

A new feature does **not** automatically go to the end of the roadmap.

Use the following process.

## Step 1 — Feature proposal

Create:

```text
FEATURE_<name>_PROPOSAL.md
```

containing:

- problem;
- users;
- value;
- safety level;
- data;
- dependencies;
- rough UX.

## Step 2 — Assign requirement IDs

Add new `FR-*` identifiers.

## Step 3 — Architectural classification

Determine:

- new module?
- existing module extension?
- external adapter?
- new data?
- new events?
- new permissions?

## Step 4 — Dependency placement

Identify earliest safe insertion point.

## Step 5 — Decide phase strategy

Options:

```text
insert new phase
add sub-phase
defer post-pilot
research spike
```

## Step 6 — Update documents

At minimum:

- PRD;
- architecture if needed;
- implementation plan;
- dependency map;
- acceptance criteria;
- progress tracker.

## Step 7 — Codex prompt

Only then implement.

---

# 36. Feature Insertion Examples

## Example — Wearables

Dependencies:

```text
P4 consent
P5 patient/observation model
```

Can be inserted after P5 as:

```text
P5W — Wearable Integration Foundation
```

without waiting for QML.

## Example — Teleconsultation

Dependencies:

```text
P13 provider/referral
```

Insert after P13.

## Example — Medical Image AI

Dependencies:

```text
P3 jobs/object storage
P5 patient/encounter
P10 clinician dashboard
P18 model registry concepts
```

Can be introduced as separate module once those contracts exist.

## Example — Nutrition

Depends on:

```text
P5 patient context
P9 safety framework
```

Potentially after P15 because it may reuse knowledge/self-care governance.

---

# 37. Prompt Design Standard

Every Codex implementation prompt SHALL include:

```text
ROLE
PHASE
OBJECTIVE
CONTEXT DOCUMENTS
REQUIREMENT IDs
CURRENT REPOSITORY AUDIT
IN SCOPE
OUT OF SCOPE
ARCHITECTURE RULES
IMPLEMENTATION TASKS
DATABASE CHANGES
API CHANGES
FRONTEND CHANGES
TESTS
COMMANDS TO RUN
ACCEPTANCE CRITERIA
FINAL REPORT FORMAT
```

---

# 38. Codex Context Pack Standard

Do not attach every document to every prompt.

## Always read

```text
00_PROJECT_MASTER_SPEC.md
02_SYSTEM_ARCHITECTURE.md
29_ENGINEERING_STANDARDS.md
34_MASTER_IMPLEMENTATION_PLAN.md
CODEX_INSTRUCTIONS.md
```

## Then add

- relevant PRD section;
- current module spec;
- DB/API/domain spec;
- current phase acceptance criteria.

---

# 39. First Codex Coding Prompt Must Not Be P7+

The first coding prompt must be P1.

Do not ask Codex to implement clinical intake into an empty repository.

The sequence exists to prevent architecture collapse.

---

# 40. Recommended Prompt Granularity

A phase larger than approximately one coherent PR should be split into sub-prompts.

For example:

```text
P11-A Upload/storage
P11-B OCR adapter
P11-C Parser registry
P11-D Entity extraction
P11-E UI integration
```

Each sub-prompt ends with tests and a diff audit.

---

# 41. Merge / Continuation Rule

Before starting the next sub-phase:

```text
[ ] previous changes committed or cleanly present
[ ] tests pass
[ ] migrations at head
[ ] progress tracker updated
[ ] no unresolved blocker hidden
```

---

# 42. Architecture Audit Milestones

Perform explicit architecture audits after:

- P3;
- P5;
- P10;
- P15;
- P20;
- P23.

Audit for:

- cross-module coupling;
- shared-kernel growth;
- unused abstractions;
- duplicate types;
- vendor leakage;
- migration debt;
- feature-flag debt;
- test gaps.

---

# 43. Security Audit Milestones

Perform security review after:

- P4 identity/consent;
- P11 document uploads;
- P13 external referrals;
- P17 ABDM;
- P20 integration;
- P22 hardening.

---

# 44. Safety Audit Milestones

Perform safety review after:

- P9 physical safety;
- P14 mental health;
- P15 self-care;
- P20 unified routing;
- P24 pilot gate.

---

# 45. Database Audit Milestones

After each phase with persistence:

```text
alembic current
alembic heads
upgrade from empty
migration diff check
constraints/index review
```

Avoid multiple unexpected heads.

---

# 46. Model Governance Milestones

After P18/P19:

- model cards;
- dataset cards;
- experiment reproducibility;
- artifact hashes;
- approval state;
- production isolation.

---

# 47. Documentation Creation Schedule

The remaining detailed docs should be created before their dependent phase.

## Before P1

```text
03_REPOSITORY_STRUCTURE.md
CODEX_INSTRUCTIONS.md
CODEX_WORKFLOW.md
CODEX_CONTEXT_RULES.md
```

## Before P4/P5

```text
04_DOMAIN_MODEL.md
05_DATABASE_SCHEMA.md
06_API_CONTRACTS.md
26_PRIVACY_CONSENT_SPEC.md
27_SECURITY_ARCHITECTURE.md
```

## Before P7

```text
07_CLINICAL_INTAKE_SPEC.md
22_UX_AND_USER_FLOWS.md
23_PATIENT_APP_SPEC.md
```

## Before P9

```text
08_SAFETY_AND_TRIAGE_POLICY.md
```

Real policy values may remain pending clinical approval.

## Before P10

```text
24_CLINICIAN_DASHBOARD_SPEC.md
12_CLINICAL_PROVENANCE_SPEC.md
```

## Before P11

```text
15_DOCUMENT_AI_OCR_SPEC.md
```

## Before P12

```text
16_MULTILINGUAL_SPEECH_SPEC.md
```

## Before P13

```text
11_PROVIDER_ROUTING_POLICY.md
25_ADMIN_PORTAL_SPEC.md (relevant sections)
```

## Before P14

```text
09_MENTAL_HEALTH_POLICY.md
13_AI_ORCHESTRATION_SPEC.md
14_LLM_EXTRACTION_SPEC.md
```

## Before P15

```text
10_SELF_CARE_AYURVEDA_POLICY.md
17_RAG_KNOWLEDGE_SPEC.md
```

## Before P16

```text
20_FHIR_MAPPING_SPEC.md
```

## Before P17

```text
21_ABDM_INTEGRATION_SPEC.md
```

## Before P18

```text
18_CLASSICAL_ML_SPEC.md
```

## Before P19

```text
19_QUANTUM_ML_SPEC.md
```

## Before P22/P23

```text
28_THREAT_MODEL.md
30_TESTING_STRATEGY.md
31_OBSERVABILITY_SPEC.md
32_DEVOPS_DEPLOYMENT.md
33_ERROR_HANDLING_POLICY.md
```

---

# 48. MVP Definition

The product can be considered a strong technical MVP when the following phases are functionally complete:

```text
P1–P15
+
basic P16 FHIR export
```

with the caveat that real clinical policy/content may still require sign-off.

This MVP demonstrates:

- patient intake;
- structured history;
- clinical summary;
- OCR;
- multilingual support;
- deterministic safety framework;
- mental-health architecture;
- provider/referral;
- self-care safety framework;
- clinician dashboard.

Classical/QML research remains a separate requirement for the complete unified SIH project.

---

# 49. Complete SIH Demonstration Definition

For the combined project demo, include:

```text
P1–P20
```

with at least:

- one FHIR-compatible exchange demo;
- one ABDM sandbox/mock flow if approved;
- one classical ML benchmark;
- one hybrid QML benchmark;
- integrated patient workflow.

---

# 50. Production/Pilot Definition

Do NOT call the system pilot-ready until:

```text
P21
P22
P23
P24
```

are complete and required clinical/privacy/ethics approvals exist.

---

# 51. Demo vs Real Deployment Labels

UI/config must distinguish:

```text
DEVELOPMENT
DEMO
RESEARCH
PILOT
PRODUCTION
```

Synthetic policies/provider records/remedies must never appear as real verified production data.

---

# 52. Acceptance-Criteria Strategy

`35_PHASE_ACCEPTANCE_CRITERIA.md` will mirror P0–P24.

Each criterion should use:

```text
AC-P<phase>-<number>
```

Example:

```text
AC-P11-003

Given a supported lab report
When document processing completes successfully
Then extracted lab facts include source-document provenance
And low-confidence values are not clinician-confirmed automatically
```

---

# 53. Dependency Map Strategy

`36_DEPENDENCY_MAP.md` should contain:

- phase dependencies;
- module dependencies;
- capability dependencies;
- external dependencies;
- safety/policy prerequisites.

The implementation plan remains the sequence authority.

---

# 54. Progress Tracker Strategy

`38_PROGRESS_TRACKER.md` should track:

```text
phase
sub-phase
status
branch/commit
requirements
tests
blockers
date
notes
```

Codex updates it only when instructed by the phase prompt.

---

# 55. Decision Log Strategy

`37_DECISION_LOG.md` should begin with:

```text
ADR-001 modular monolith
ADR-002 ports/adapters
ADR-003 deterministic safety authority
ADR-004 FHIR boundary
ADR-005 research isolation
ADR-006 domain events/outbox
ADR-007 compile-time feature registration
ADR-008 PostgreSQL source of truth
ADR-009 object storage for documents
ADR-010 clinical provenance
```

---

# 56. Risk-Controlled Ordering Rationale

The implementation order deliberately places:

### Safety before self-care

P9 exists before P15.

### Classical ML before QML

P18 exists before P19.

### Patient domain before OCR

P5 exists before P11.

### Consent before referrals

P4 exists before P13.

### Provider registry before mental-health referral completion

P13 exists before P14.

### FHIR before ABDM

P16 exists before P17.

### Integration before hardening

P20 precedes P22–P24.

This ordering is intentional and should not be rearranged casually.

---

# 57. What Must Not Block Early Product Progress

The following must remain optional to the core patient workflow:

- QML;
- real quantum hardware;
- full ABDM production integration;
- advanced RAG;
- speech;
- external provider booking;
- sophisticated handwritten OCR.

The architecture supports them, but the core intake/safety/clinician workflow should not depend on them.

---

# 58. What Must Block Unsafe Features

The following MUST block corresponding user-facing functionality if absent:

### No approved safety policy
Block real emergency/clinical triage claims.

### No approved self-care knowledge
Block real patient-facing remedy recommendations.

### No verified provider data
Block named real provider recommendations.

### No approved mental-health crisis policy
Block claims of validated mental-health triage.

### No valid model
Block patient-facing disease-risk score.

---

# 59. Definition of "From Scratch"

For this project, "from scratch" means:

SwasthyaSetu owns:

- architecture;
- domain model;
- workflows;
- UI;
- orchestration;
- safety framework;
- policy engine;
- clinical data model;
- care navigation;
- referral lifecycle;
- self-care governance;
- research evaluation framework.

It does NOT mean reimplementing foundational technologies such as:

- PostgreSQL;
- FastAPI;
- OCR algorithms;
- speech models;
- FHIR libraries;
- Qiskit/PennyLane;
- cryptography primitives.

Libraries are dependencies behind controlled boundaries.

---

# 60. Final Master Sequence

```text
P0  Documentation + Codex governance
P1  Repository/tooling
P2  Shared platform kernel
P3  Persistence/events/jobs
P4  Identity/sessions/consent
P5  Patient/encounter/provenance
P6  Patient web foundation
P7  Structured clinical intake
P8  AI gateway + extraction
P9  Physical safety framework
P10 Clinician dashboard + summary
P11 Document AI/OCR
P12 Multilingual speech/translation
P13 Providers/resources/referrals
P14 Mental-health/MannSetu
P15 Self-care/Ayurveda framework
P16 FHIR
P17 ABDM
P18 Classical ML
P19 Hybrid QML
P20 Unified orchestration
P21 Admin/governance/review
P22 Security/privacy/resilience
P23 E2E/accessibility/performance
P24 Pilot/readiness gates
```

---

# 61. Immediate Next Action

Do not start P1 yet.

First complete P0 supporting implementation documents:

```text
03_REPOSITORY_STRUCTURE.md
CODEX_INSTRUCTIONS.md
CODEX_WORKFLOW.md
CODEX_CONTEXT_RULES.md
35_PHASE_ACCEPTANCE_CRITERIA.md
36_DEPENDENCY_MAP.md
37_DECISION_LOG.md
38_PROGRESS_TRACKER.md
```

The detailed domain/database/API specs should then be created before P4/P5 as defined in Section 47.

Once those P0 control documents are complete, the first actual Codex coding prompt should implement **P1-A: repository skeleton + backend tooling**, not the healthcare features.

---

# 62. Master Rule

> **The roadmap is fixed enough to keep Codex disciplined, but modular enough that new features can be inserted deliberately without breaking the rest of SwasthyaSetu.**

This plan is the implementation sequence authority unless superseded by an approved architecture decision and corresponding documentation update.
