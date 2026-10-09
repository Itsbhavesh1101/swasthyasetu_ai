# SwasthyaSetu AI
## 02 — System Architecture Specification

**Document ID:** `SSAI-ARCH-002`  
**Filename:** `02_SYSTEM_ARCHITECTURE.md`  
**Status:** Foundation / Architecture Source of Truth  
**Version:** `1.0.0-draft`  
**Depends on:** `00_PROJECT_MASTER_SPEC.md`, `01_PRODUCT_REQUIREMENTS.md`  
**Primary implementation agent:** Codex  
**Architecture style:** Extensible modular monolith with bounded contexts, ports/adapters, typed contracts, domain events, feature flags, and extractable compute services

---

# 1. Purpose

This document defines how SwasthyaSetu AI is technically organized.

It converts the project master specification and PRD into an architecture that is:

- modular;
- extensible;
- safety-first;
- testable;
- observable;
- replaceable at integration boundaries;
- suitable for incremental Codex implementation;
- capable of evolving into distributed services later without starting with premature microservice complexity.

The system is expected to gain new features over time. Architecture must therefore make future change a normal operation rather than an exception.

---

# 2. Architectural Drivers

The architecture is driven by five major constraints.

## 2.1 Healthcare safety

Safety-critical behavior must be deterministic, testable, versioned, auditable, and independent of unconstrained model prose.

## 2.2 Broad domain scope

The platform combines clinical intake, patient history, OCR, mental-health triage, self-care, provider navigation, referrals, FHIR/ABDM, classical ML, QML, multilingual speech, and future healthcare capabilities.

## 2.3 Codex-driven implementation

The structure must make it difficult for an implementation agent to accidentally create god services, cross-module persistence coupling, vendor lock-in, duplicated patient models, or unsafe AI authority.

## 2.4 Rapid product evolution

Future modules such as wearables, telemedicine, medication adherence, nutrition, imaging AI, remote vitals, pharmacy, insurance, chronic-care modules, or new predictive models should integrate through stable capabilities.

## 2.5 Incremental delivery

Core patient workflows must work before optional advanced capabilities such as QML are complete.

---

# 3. Mandatory Architecture Principles

## ARCH-P-001 — Modular monolith first
The initial backend SHALL be a modular monolith rather than many independently deployed microservices.

## ARCH-P-002 — Strong boundaries
Logical modules SHALL have explicit ownership, public contracts, persistence boundaries, and tests.

## ARCH-P-003 — Ports and adapters
External systems SHALL be accessed through explicit interfaces/adapters.

## ARCH-P-004 — Safety before intelligence
Deterministic safety policy SHALL execute independently of generative AI prose.

## ARCH-P-005 — Domain ownership
Each module SHALL own its business rules and persistence responsibilities.

## ARCH-P-006 — No cross-module ORM mutation
A module MUST NOT directly mutate another module's internal ORM/repository state.

## ARCH-P-007 — Contract-first boundaries
Cross-module calls, APIs, and events SHALL use typed contracts.

## ARCH-P-008 — Event-driven where useful
Asynchronous reactions SHOULD use typed domain/integration events.

## ARCH-P-009 — Synchronous where necessary
User-blocking operations requiring immediate consistency SHOULD use synchronous application-service calls.

## ARCH-P-010 — Graceful degradation
Failure of optional features MUST NOT collapse unrelated core workflows.

## ARCH-P-011 — Versioned behavior
Safety policies, prompts, models, schemas, external resources, mappings, and consent text SHALL be versioned.

## ARCH-P-012 — Feature isolation
New features SHALL be addable without widespread unrelated edits.

## ARCH-P-013 — Extractable compute
Compute-heavy capabilities SHALL be written so they can later move to services/workers.

## ARCH-P-014 — Observable without oversharing
Operational telemetry SHALL avoid raw sensitive clinical content.

---

# 4. Initial Deployment Shape

The initial production-quality shape is:

```text
Patient Web / PWA / Kiosk
Clinician Web
Admin Web
        |
        v
FastAPI Modular Backend
        |
        +--> Background Worker
        |
        +--> PostgreSQL
        +--> Object Storage
        +--> Optional Redis
        |
        +--> LLM Adapter(s)
        +--> OCR Adapter(s)
        +--> ASR/TTS Adapter(s)
        +--> FHIR Adapter
        +--> ABDM Adapter
        +--> Notification Adapter(s)
        +--> ML/QML Backends
```

The backend is one deployable application initially, but internally behaves like a collection of bounded systems.

---

# 5. Why Not Microservices Initially

Starting with microservices would introduce:

- distributed transactions;
- service discovery;
- network failure between domains;
- duplicated auth concerns;
- broker complexity;
- multi-service local setup;
- additional CI/CD and monitoring;
- difficult debugging for a small implementation team.

SwasthyaSetu therefore starts with one modular FastAPI backend plus workers. Modules may be extracted later when justified by scaling, security, runtime, team ownership, or deployment cadence.

---

# 6. Backend Layering

Each module SHOULD conceptually contain four layers.

## 6.1 Interface layer
Owns HTTP transport, API validation, auth-context extraction, request/response mapping, and API versioning.

It MUST NOT contain substantive clinical/business rules.

## 6.2 Application layer
Owns use-case orchestration, transaction boundaries, authorization checks, commands, queries, and calls to module public interfaces.

## 6.3 Domain layer
Owns entities, value objects, invariants, policies, domain services, and domain events.

It SHOULD remain minimally dependent on FastAPI, SQLAlchemy, or vendor SDKs.

## 6.4 Infrastructure layer
Owns SQLAlchemy repositories, PostgreSQL, object storage, external APIs, AI SDKs, task queues, telemetry integrations, and adapters.

---

# 7. Initial Bounded Contexts

The initial backend SHALL be divided into the following logical modules:

```text
identity
sessions
consent
patients
encounters
clinical_intake
safety
mental_health
documents
provenance
summaries
self_care
providers
resources
referrals
notifications
interoperability
ml
research
audit
feature_management
```

These names may be refined by the repository-structure document, but ownership boundaries are authoritative.

---

# 8. Identity Module

Responsibilities:

- authenticated identities;
- pseudonymous identity;
- clinician/admin/service actor identity;
- actor context;
- identity-provider adapters.

Exposes capabilities such as:

```text
identity.current_actor
identity.authenticate
identity.resolve_patient_identity
```

Must not own clinical consent or clinical records.

---

# 9. Sessions Module

Responsibilities:

- application session lifecycle;
- kiosk sessions;
- pseudonymous conversation sessions;
- expiry and closure.

Publishes:

```text
SessionCreated
SessionExpired
SessionClosed
```

---

# 10. Consent Module

Responsibilities:

- privacy-notice versions;
- consent scope;
- referral consent;
- external-processing consent;
- ABDM consent linkage where applicable;
- revocation;
- consent evaluation.

Exposes:

```text
consent.grant
consent.revoke
consent.check
```

No module should create a parallel consent subsystem.

---

# 11. Patients Module

Responsibilities:

- patient master profile where applicable;
- longitudinal clinical context;
- active/historical problem list;
- medication list;
- allergy list;
- procedures;
- structured longitudinal read access.

Exposes:

```text
patients.get
patients.get_longitudinal_context
patients.query_timeline
patients.record_confirmed_fact
```

Other modules must not create competing patient-master records.

---

# 12. Encounters Module

Responsibilities:

- encounter/intake episode lifecycle;
- encounter state;
- linkage to patient/session;
- encounter closure/abandonment.

Publishes:

```text
EncounterStarted
EncounterUpdated
EncounterClosed
EncounterAbandoned
```

---

# 13. Clinical Intake Module

Responsibilities:

- presenting complaint;
- HPI;
- medical/surgical history;
- medications/allergies;
- family/personal history;
- review of systems;
- prior investigations;
- AYUSH extensions;
- missing-field detection;
- adaptive question selection;
- pluggable specialty questionnaires.

Exposes:

```text
intake.start
intake.answer
intake.get_state
intake.next_question
intake.complete
```

It does not own final urgent routing.

---

# 14. Safety Module

The physical-health safety module is high criticality.

Responsibilities:

- deterministic red-flag evaluation;
- hard overrides;
- ambiguity state;
- route calculation;
- self-care exclusion;
- reason codes;
- policy version.

Exposes:

```text
safety.evaluate
safety.evaluate_selfcare_eligibility
safety.get_active_policy
```

A typed decision should resemble:

```json
{
  "route": "PRIORITY_REVIEW",
  "reason_codes": ["..."],
  "policy_version": "...",
  "requires_clarification": false,
  "blocks_self_care": true
}
```

The safety module MUST NOT depend on free-form model prose.

---

# 15. Mental Health Module

Responsibilities:

- mental-health conversation workflow;
- structured signal schema;
- language-aware safety backstop;
- deterministic A/B/C policy;
- focused clarification;
- crisis fallback;
- resource selection;
- referral request preparation.

Internal flow:

```text
Message
  |
  +--> Safety Backstop
  |
  +--> LLM Structured Extractor
  |
  +--> Schema Validation
  |
  +--> Deterministic Mental-Health Policy
  |
  +--> Route / Clarify / Crisis
```

The LLM extractor MUST NOT be authoritative for the final route.

---

# 16. Documents Module

Responsibilities:

- upload metadata;
- object-storage references;
- validation state;
- OCR orchestration;
- document classification;
- medical entity extraction;
- confidence;
- source linking;
- document parser registry.

Processors should be pluggable:

```text
PrescriptionProcessor
LabReportProcessor
DischargeSummaryProcessor
DiagnosticReportProcessor
ImagingReportProcessor
ReferralLetterProcessor
```

Do not create one giant conditional parser.

Publishes events such as:

```text
DocumentUploaded
DocumentProcessingStarted
DocumentProcessed
DocumentProcessingFailed
ClinicalFactsExtractedFromDocument
```

---

# 17. Provenance Capability

Every meaningful AI-derived fact should answer:

```text
Where did it come from?
Which source?
Which model/extractor?
Which version?
What confidence?
Who confirmed/rejected it?
```

Provenance source types may include:

```text
patient_report
caregiver_report
ocr
document_ai
fhir_import
abdm_import
model_inference
clinician
admin
```

AI-derived facts must remain distinguishable from clinician-confirmed facts.

---

# 18. Summaries Module

Responsibilities:

- structured physician-ready draft summaries;
- summary sections;
- versions;
- clinician edits;
- acceptance/rejection;
- source links.

Summary generation MUST summarize structured information rather than create new medical truth.

---

# 19. Self-Care Module

Responsibilities:

- curated supportive-care knowledge;
- Ayurveda / gharelu knowledge packs;
- eligibility;
- contraindication-aware retrieval;
- approved content versions;
- escalation instructions;
- reviewer status.

Flow:

```text
Structured Context
    |
Safety Eligibility
    |
+---+----------------+
|                    |
blocked              eligible
|                    |
care route       knowledge retrieval
                     |
                personalization filters
                     |
                approved guidance
```

No unrestricted LLM-generated treatment.

---

# 20. Providers Module

Responsibilities:

- doctor/provider registry;
- facility affiliation;
- normalized specialty;
- languages;
- contact;
- teleconsultation;
- hours;
- location;
- verification state;
- external provider-directory adapters.

Exposes:

```text
providers.search
providers.get
providers.find_by_specialty
providers.verify
```

Named providers MUST come from verified data, not model generation.

---

# 21. Resources Module

Resources include:

- crisis lines;
- hospitals;
- counselling cells;
- public health services;
- NGOs;
- institution-specific support.

Records support:

```text
source
owner
verified_at
expires_at
status
locale
contact
eligibility
hours
version
```

Critical resources may have bundled fallback copies.

---

# 22. Referrals Module

Responsibilities:

- referral offer;
- consent linkage;
- minimal payload;
- destination adapter;
- send/retry;
- status lifecycle;
- acknowledgement;
- scheduling/completion.

Lifecycle:

```text
OFFERED
  -> CONSENTED
  -> SENT
  -> ACKNOWLEDGED
  -> SCHEDULED
  -> COMPLETED
```

Alternative states:

```text
DECLINED
UNREACHABLE
EXPIRED
FAILED
CANCELLED
```

Full raw conversation is not shared by default.

---

# 23. Notifications Module

Responsibilities:

- notification intent;
- templates;
- delivery preference;
- provider abstraction;
- delivery state;
- retry;
- sensitive-content minimization.

Potential adapters:

```text
EmailNotificationProvider
SMSNotificationProvider
PushNotificationProvider
MockNotificationProvider
```

---

# 24. Interoperability Module

Owns external health-system exchange boundaries:

- FHIR;
- ABDM/ABHA;
- hospital/HIS connectors;
- future clinical integrations.

Exposes:

```text
interop.export_fhir
interop.import_fhir
interop.push_to_abdm
interop.pull_from_abdm
```

Internal domain entities are not forced to mirror FHIR everywhere.

---

# 25. ML Runtime Module

The production-facing ML module provides a governed model-access layer.

Responsibilities:

- approved-model lookup;
- input validation;
- model version;
- calibration version;
- inference;
- normalized risk output;
- explanation reference;
- inference metadata.

Normalized output:

```json
{
  "model_id": "...",
  "model_version": "...",
  "risk_probability": 0.71,
  "risk_band": "elevated",
  "calibration_version": "...",
  "input_quality": "valid",
  "explanation_ref": "..."
}
```

Risk output is not diagnosis and cannot override safety policy.

---

# 26. Research / QML Boundary

Research workloads are logically isolated from normal patient runtime.

Capabilities include:

- approved dataset registry;
- preprocessing;
- feature engineering;
- classical baselines;
- QML experiments;
- evaluation;
- experiment tracking;
- model candidates;
- model promotion.

Research code MUST NOT automatically obtain unrestricted production patient data.

---

# 27. Audit Module

Responsibilities:

- policy changes;
- resource changes;
- consent changes;
- clinician corrections;
- model promotion;
- privileged admin actions;
- referral status changes;
- operational governance actions.

Audit is not a raw transcript archive.

---

# 28. Feature Management

The platform SHALL support feature flags for optional/staged capabilities.

Examples:

```text
voice_intake_enabled
mental_health_enabled
ayurveda_selfcare_enabled
provider_directory_enabled
abdm_enabled
qml_inference_enabled
preventive_care_enabled
```

Risky experimental features default off when flag state cannot be determined.

Feature flags MUST NOT disable mandatory safety while leaving dependent risky features active.

---

# 29. Shared Kernel

Keep shared code small.

Acceptable shared concerns:

- typed IDs;
- timestamps;
- actor context;
- pagination;
- event envelope;
- generic errors;
- observability;
- configuration interfaces;
- feature flag interface.

Do NOT place domain-specific clinical logic into the shared kernel.

---

# 30. Module Public Interface Pattern

Modules should expose narrow public interfaces.

Conceptual shape:

```text
modules/
  providers/
    domain/
    application/
    infrastructure/
    api/
    public.py
```

Other modules import `public.py` or equivalent contracts, not internal repositories.

---

# 31. Feature Module Manifest

Every substantial feature SHOULD declare metadata similar to:

```yaml
id: providers
version: 1

capabilities:
  - providers.search
  - providers.read

requires:
  - consent.check

api_prefix:
  - /api/v1/providers

events_published:
  - ProviderVerified
  - ProviderExpired

events_consumed:
  - ResourceVerificationRequested

permissions:
  - provider:read
  - provider:manage

feature_flags:
  - provider_directory_enabled
```

The runtime representation may be typed Python rather than YAML.

---

# 32. Capability Registry

Internal capabilities may include:

```text
identity.current_actor
consent.check
patients.read
patients.timeline
intake.start
intake.answer
safety.evaluate
mental_health.evaluate
ocr.extract
documents.process
llm.extract
llm.summarize
speech.transcribe
speech.synthesize
translation.translate
selfcare.retrieve
providers.search
resources.search
referrals.create
fhir.export
fhir.import
abdm.exchange
risk.predict
notifications.send
```

Business modules consume capabilities, not vendor SDKs.

---

# 33. Ports and Adapters

Every meaningful external dependency must sit behind an explicit interface.

Examples:

```text
LLMExtractorPort
OCRPort
SpeechToTextPort
TextToSpeechPort
TranslationPort
FHIRGatewayPort
ABDMGatewayPort
ObjectStoragePort
NotificationPort
AppointmentProviderPort
ModelInferencePort
QuantumBackendPort
```

Example OCR interface:

```python
class OCRPort(Protocol):
    async def extract(self, document: DocumentInput) -> OCRResult:
        ...
```

Potential implementations:

```text
PaddleOCRAdapter
MockOCRAdapter
FutureCloudOCRAdapter
```

---

# 34. AI Orchestration Boundary

Generative AI use SHOULD flow through a central **SwasthyaSetu-owned application orchestration boundary** for shared operational concerns:

- provider configuration;
- timeout;
- bounded retry;
- cost/token metadata;
- model metadata;
- structured output enforcement;
- sensitive-data handling;
- provenance;
- approved fallback behavior.

R3 clarification:

> This boundary is **in-process by default**. It does not imply a separately deployed LiteLLM/MLflow/other proxy.

Default architecture:

```text
Domain Module
     |
Task-Specific AI Contract
     |
AI Orchestration Service
     |
LLMProvider
     |
Concrete Provider Adapter
```

A network AI gateway may be introduced later only when multi-provider routing, shared budgets/quotas, virtual credentials, or cross-application AI governance justify it.

Task-specific prompts and schemas remain owned by the calling module.

# 35. LLM Task Separation

Do not create one universal medical prompt.

Separate tasks:

```text
ClinicalIntakeExtractor
MentalHealthSignalExtractor
DocumentEntityExtractor
SummaryGenerator
TranslationAssistant
KnowledgeExplanationGenerator
```

Each task needs its own:

- prompt ID/version;
- schema version;
- allowed output;
- validation;
- timeout;
- fallback;
- evaluation fixtures.

---

# 36. Deterministic Policy Engine

Safety-sensitive policies follow:

```text
Structured Input
    |
Schema Validation
    |
Policy Evaluation
    |
Hard Overrides
    |
Route
    |
Reason Codes
    |
Policy Version
```

Policies may include:

```text
physical_red_flags
mental_health_routing
self_care_eligibility
provider_specialty_routing
resource_selection
model_thresholds
```

A historical decision should be reproducible from structured input + policy/model/resource versions.

---

# 37. Domain Events

Events reduce coupling for asynchronous reactions.

Event envelope:

```json
{
  "event_id": "...",
  "event_type": "...",
  "event_version": 1,
  "occurred_at": "...",
  "correlation_id": "...",
  "causation_id": "...",
  "actor_ref": "...",
  "payload": {}
}
```

Payloads must minimize sensitive content.

Examples:

```text
SessionCreated
ConsentGranted
ConsentRevoked
PatientCreated
EncounterStarted
EncounterClosed
IntakeCompleted
SafetyRouteDecided
DocumentUploaded
DocumentProcessed
ClinicalFactExtracted
ClinicalFactConfirmed
MentalHealthRouteDecided
ProviderVerified
ProviderExpired
ReferralCreated
ReferralStatusChanged
SummaryGenerated
SummaryConfirmed
ModelInferenceCompleted
RetentionPurgeCompleted
```

---

# 38. Transactional Outbox

Important events SHOULD use a transactional outbox.

```text
transaction:
  change domain records
  insert outbox row
COMMIT

dispatcher:
  fetch pending outbox
  deliver event
  mark dispatched
```

Initial delivery may be internal. Later transport can move to Redis Streams, NATS, RabbitMQ, Kafka, or another broker without changing domain logic.

---

# 39. Idempotent Event Handling

Event handlers performing side effects must tolerate duplicate delivery using:

- event IDs;
- idempotency keys;
- unique constraints;
- deduplication records.

This is particularly important for notifications, referrals, and external sync.

---

# 40. Background Jobs

Long-running operations should use workers rather than block normal HTTP requests.

Examples:

- OCR;
- document entity extraction;
- embeddings;
- notification delivery;
- referral delivery/retry;
- FHIR sync;
- purge jobs;
- model training;
- QML experiments;
- report generation.

Job state may include:

```text
QUEUED
RUNNING
SUCCEEDED
FAILED
CANCELLED
NEEDS_REVIEW
```

---

# 41. Background Execution Port

The backend SHOULD use an abstraction:

```python
class JobDispatcher(Protocol):
    async def enqueue(self, job: JobRequest) -> JobHandle:
        ...
```

Potential implementations:

```text
InProcessJobDispatcher
ProcrastinateJobDispatcher
CeleryJobDispatcher
CloudTaskDispatcher
```

R3 preference:

- use the in-process dispatcher for deterministic local/test scaffolding;
- evaluate Procrastinate first when a durable queue is required because PostgreSQL is already a hard dependency;
- retain Celery as a mature fallback;
- do not add Redis/Valkey merely because background work exists.

The exact durable backend is activated only by its implementation phase/spike.

---

# 42. Data Architecture

```text
PostgreSQL
  - transactional truth
  - module-owned tables
  - outbox
  - audit metadata

Object Storage
  - original medical files
  - derived document artifacts
  - model/research artifacts where applicable

pgvector
  - semantic retrieval only where justified

Valkey / Redis-compatible cache (optional)
  - ephemeral cache
  - rate limiting
  - short-lived non-authoritative state

Background jobs SHOULD use the selected `JobDispatcher` implementation; the cache is not the job system by default.
```

Cache/vector search MUST NOT be the sole authoritative store of critical clinical data.

---

# 43. PostgreSQL Ownership

One PostgreSQL cluster is used initially.

Modules own their tables.

Example:

| Module | Primary ownership |
|---|---|
| sessions | session state |
| consent | consent records |
| patients | patient longitudinal records |
| encounters | encounter state |
| intake | structured intake |
| safety | route decisions |
| documents | document metadata/processing |
| self_care | approved guidance metadata |
| providers | provider registry |
| resources | verified care resources |
| referrals | referral lifecycle |
| audit | audit records |
| research | experiment/model metadata |

Exact tables belong in `05_DATABASE_SCHEMA.md`.

---

# 44. Cross-Module Read Patterns

Allowed patterns:

1. public query service;
2. denormalized read model;
3. event-maintained projection;
4. explicitly documented database view.

Example:

```text
clinical_intake -> patients.get_longitudinal_context()
```

rather than importing patient repositories directly.

---

# 45. Cross-Module Write Rule

Direct writes into another module's tables are prohibited.

Incorrect:

```text
documents repository writes medication rows
```

Correct:

```text
documents produces extracted clinical fact
-> provenance/reconciliation workflow
-> patient/clinician confirmation
```

---

# 46. Consistency Model

Use strong consistency for:

- consent;
- authorization-sensitive state;
- safety decisions tied to current input;
- clinician confirmation;
- referral creation + consent linkage.

Eventual consistency is acceptable for:

- analytics;
- search indexes;
- vector indexes;
- timeline projections;
- notifications;
- non-critical summary refresh;
- resource cache.

---

# 47. Object Storage

Binary medical files should live in object storage, not large PostgreSQL blobs.

PostgreSQL stores:

- object key;
- checksum;
- MIME type;
- size;
- owner/subject reference;
- encryption metadata;
- retention metadata;
- processing state.

---

# 48. Upload Security Boundary

```text
Client
  |
Upload
  |
Quarantine / validation
  |
type + size + file signature
  |
malware/content checks as configured
  |
accepted object storage
  |
DocumentUploaded event
```

Unvalidated uploads are untrusted.

---

# 49. pgvector

Allowed uses:

- patient-document retrieval;
- approved knowledge retrieval;
- internal semantic search.

Prohibited use:

- replacing authoritative structured clinical state.

---

# 50. Cache

Cache may store reconstructable values such as:

- provider search;
- feature flags;
- public resources;
- terminology.

Never use cache as sole store of:

- consent;
- confirmed clinical facts;
- safety decisions;
- referrals.

---

# 51. Frontend Architecture

Each web app SHOULD be feature-oriented.

Example:

```text
src/
  app/
  features/
    intake/
    documents/
    mental-health/
    self-care/
    providers/
    referrals/
  shared/
    api/
    auth/
    ui/
    forms/
    i18n/
    observability/
```

New features add modules rather than expanding one giant page.

---

# 52. Shared Design System

Shared UI primitives include:

- buttons;
- inputs;
- accessible alerts;
- cards;
- dialogs;
- tables;
- badges;
- loading/error states;
- confirmation;
- language selector;
- secure upload;
- crisis/urgent-action controls.

---

# 53. Patient UI Extension Model

A future patient feature may register:

- route;
- navigation link;
- dashboard card;
- encounter step;
- result panel.

Compile-time registration is preferred initially.

Arbitrary runtime code plugins are not required.

---

# 54. Clinician UI Extension Slots

The clinician dashboard should expose conceptual slots:

```text
PatientHeader
CriticalAlerts
MedicationAllergyPanel
Timeline
EncounterSummary
DecisionSupport
Documents
Referrals
FeaturePanels
```

Future modules may add panels without rewriting the dashboard shell.

---

# 55. Admin UI Extension Model

Feature modules may contribute admin sections such as:

```text
/providers
/resources
/self-care
/policies
/models
/feature-flags
/audit
```

Visibility is permission-controlled.

---

# 56. Authentication and Authorization

Authentication determines who the actor is.

Authorization determines what the actor may do.

Actors may include:

```text
patient
pseudonymous_user
caregiver
clinician
counsellor
triage_staff
resource_admin
clinical_reviewer
system_admin
researcher
service_account
```

Permissions should be action/capability oriented, for example:

```text
patient:read:self
encounter:read:assigned
summary:confirm
provider:manage
policy:review
research:run
audit:read
```

Backend authorization is mandatory; frontend visibility is not security.

---

# 57. Trust Boundaries

Major boundaries:

1. browser -> API;
2. API -> LLM;
3. API/worker -> OCR/speech;
4. backend -> object storage;
5. backend -> FHIR/ABDM;
6. referral -> external institution;
7. research -> production data;
8. administrator -> governance configuration.

Each boundary receives explicit security and privacy controls.

---

# 58. Conversation Orchestration

Conversation is a workflow, not the authoritative clinical database.

```text
User Input
  |
Validation
  |
Language handling
  |
Local safety/backstop scan
  |
Task-specific structured extraction
  |
Schema validation
  |
Update structured intake
  |
Deterministic safety policy
  |
Question / Route / Resource Action
```

Raw chat text and structured clinical state remain separate concepts.

---

# 59. Explicit State Machines

Complex workflows SHOULD be modeled explicitly.

State machines include:

- encounter;
- document processing;
- mental-health triage;
- referral;
- model experiment;
- external sync.

Transitions are typed and tested.

---

# 60. Mental-Health State Machine

```text
START
  -> DISCLOSURE
  -> OPENING_CONCERN
  -> EXTRACT
  -> HARD_RISK?
       yes -> CRISIS_ROUTE
       no  -> AMBIGUOUS?
                yes -> CLARIFY -> EXTRACT
                no  -> POLICY
                       -> ROUTE_A
                       -> ROUTE_B -> REFERRAL_CONSENT -> REFERRAL

ANY STATE:
urgent-help click -> CRISIS_ROUTE
```

---

# 61. Document State Machine

```text
UPLOADED
 -> VALIDATING
 -> ACCEPTED
 -> QUEUED
 -> PROCESSING
 -> SUCCEEDED
      -> REVIEW_PENDING (if required)
      -> CONFIRMED
 -> FAILED
      -> RETRYABLE / FINAL_FAILED
```

---

# 62. Referral State Machine

```text
OFFERED
 -> CONSENTED
 -> SENT
 -> ACKNOWLEDGED
 -> SCHEDULED
 -> COMPLETED
```

Alternative:

```text
DECLINED
UNREACHABLE
EXPIRED
FAILED
CANCELLED
```

---

# 63. Clinical Fact Lifecycle

```text
EXTRACTED
 -> LOW_CONFIDENCE
 -> NEEDS_CONFIRMATION
 -> PATIENT_CONFIRMED
 -> CLINICIAN_CONFIRMED
 -> REJECTED
 -> SUPERSEDED
```

Not all facts must traverse every state.

---

# 64. Decision Composition

Do not produce one opaque universal health score.

Keep separate evidence channels:

```text
physical_red_flags
mental_health_risk
self_care_eligibility
longitudinal_context
document_findings
predictive_risk
provider_availability
```

A governed orchestration layer composes actions while preserving provenance.

---

# 65. Care Orchestration

A high-level care use case may combine:

```text
safety decision
mental-health decision
self-care eligibility
predictive risk
provider category
user request
```

It remains an orchestrator, not a god service.

---

# 66. Provider Routing

```text
Structured Context
   |
Provider Routing Policy
   |
Care Category
   |
Specialty / Service Type
   |
Verified Registry
   |
Transparent Filters
   |
Results
```

Provider data is never generated from LLM memory.

---

# 67. Self-Care Knowledge Separation

Self-care separates:

- **content** — what approved guidance exists;
- **eligibility policy** — when it may be shown;
- **personalization filters** — which approved variant is suitable;
- **explanation layer** — how content is presented.

A content update must not silently change eligibility.

---

# 68. Knowledge Packs

A knowledge pack may contain:

```text
manifest
guidance entries
eligibility tags
contraindications
escalation conditions
source metadata
review metadata
translations
tests
```

New packs can be added without rewriting the self-care engine.

---

# 69. Model Gateway

The product treats models as registered tools.

```text
ModelRequest
   |
Model Registry
   |
Approved Adapter
   |
Inference
   |
Normalized RiskAssessment
```

Framework-specific output does not leak into the product API.

---

# 70. Model Registry

Model metadata should include:

```text
model_id
model_version
task
framework
artifact_ref
input_schema_version
output_schema_version
training_dataset_ref
metrics
calibration_ref
approval_status
created_at
promoted_at
retired_at
```

---

# 71. Research Architecture

```text
Dataset Registry
   |
Preprocessing
   |
Feature Engineering
   |
+-- Classical Models
|
+-- QML Models
   |
Evaluation
   |
Experiment Store
   |
Model Candidate
   |
Governance Gate
   |
Model Registry
```

Research success does not automatically promote a model.

---

# 72. QML Backend Abstraction

QML uses an explicit backend port.

```python
class QuantumBackendPort(Protocol):
    async def execute(self, circuit, *, shots=None, options=None):
        ...
```

Potential adapters:

```text
PennyLaneSimulatorAdapter
QiskitSimulatorAdapter
FutureHardwareAdapter
```

QML failure cannot break clinical intake.

---

# 73. FHIR Boundary

```text
Internal Domain
   |
FHIR Mapper
   |
FHIR Validation
   |
FHIR Gateway
   |
External FHIR System
```

FHIR is an exchange contract, not the internal data model.

---

# 74. ABDM Boundary

```text
Internal Use Case
   |
ABDM Application Port
   |
Consent + Mapping Validation
   |
ABDM Adapter
   |
Sandbox / Production Endpoint
```

ABDM failure must not destroy locally valid data.

---

# 75. REST API Architecture

Initial external API style is REST.

Rules:

- `/api/v1/...`;
- typed request/response;
- OpenAPI;
- server-side authorization;
- standardized errors;
- pagination;
- request/correlation IDs;
- idempotency where side effects may duplicate;
- no raw internal stack traces.

Possible namespaces:

```text
/api/v1/sessions
/api/v1/consents
/api/v1/patients
/api/v1/encounters
/api/v1/intake
/api/v1/documents
/api/v1/mental-health
/api/v1/self-care
/api/v1/providers
/api/v1/resources
/api/v1/referrals
/api/v1/clinician
/api/v1/admin
/api/v1/interoperability
/api/v1/research
```

Exact contracts belong in `06_API_CONTRACTS.md`.

---

# 76. Error Architecture

Common typed errors:

```text
ValidationError
AuthenticationError
AuthorizationError
ConflictError
NotFoundError
RateLimitError
DependencyUnavailableError
DependencyTimeoutError
SafetyPolicyError
ConsentRequiredError
FeatureDisabledError
```

Conceptual response:

```json
{
  "error": {
    "code": "CONSENT_REQUIRED",
    "message": "Consent is required for this action.",
    "request_id": "...",
    "details": {}
  }
}
```

---

# 77. Resilience Patterns

Adapters should use as appropriate:

- timeouts;
- bounded retries;
- exponential backoff;
- circuit breaking;
- health checks;
- idempotency;
- fallback;
- isolation.

Do not retry unsafe/non-idempotent operations blindly.

---

# 78. LLM Failure

If LLM extraction fails:

- no fake result is created;
- schema state is failure/unknown;
- safety backstop remains active;
- crisis resources remain available;
- structured/touch fallback may be offered;
- user receives honest degraded-mode messaging.

---

# 79. OCR Failure

If OCR fails:

- patient can continue intake;
- document can remain available for manual review if permitted;
- processing state is explicit;
- manual entry remains possible;
- no extracted fact is invented.

---

# 80. Speech Failure

If ASR fails:

- text/touch remains available;
- failed transcription is not accepted as clinical fact;
- retry is possible;
- audio retention follows policy.

---

# 81. Provider Directory Failure

If provider lookup fails:

- do not generate fake providers;
- use verified cached/static resources where permitted;
- show care category even if named provider lookup is unavailable;
- urgent resources remain available.

---

# 82. ML/QML Failure

If inference fails:

- safety still executes;
- no false low-risk result;
- no risk probability is fabricated;
- normal professional-care routing remains possible.

---

# 83. Feature Flag Failure

If flag configuration is unavailable:

- risky/experimental feature defaults off;
- mandatory safety defaults on;
- safe cached/default configuration may be used.

---

# 84. Security Architecture

Defense in depth:

```text
Client Controls
  |
Transport Security
  |
Authentication
  |
Authorization
  |
Validation
  |
Domain Invariants
  |
Adapter Boundaries
  |
Data Protection
  |
Audit
  |
Monitoring
```

Detailed threat analysis belongs in `28_THREAT_MODEL.md`.

---

# 85. Sensitive Data Classification

Future security/privacy specs should classify data as:

```text
PUBLIC
INTERNAL
SENSITIVE
HEALTH_SENSITIVE
IDENTITY_SENSITIVE
SECURITY_SECRET
```

Classification influences logging, retention, storage, and sharing.

---

# 86. Logging

Structured logs may include:

- timestamp;
- severity;
- module;
- operation;
- request ID;
- correlation ID;
- error code;
- duration.

Avoid:

- raw chat;
- raw medical documents;
- full prompts containing patient text;
- secrets;
- authentication tokens;
- unnecessary identifiers;
- full FHIR/ABDM payloads.

---

# 87. Tracing

Trace useful operations such as:

```text
HTTP request
intake extraction
safety evaluation
document queue
OCR adapter
provider search
referral send
FHIR export
```

Sensitive payloads should not be trace attributes.

---

# 88. Metrics

Architecture-level metrics include:

```text
requests_total
request_duration
errors_total
llm_requests_total
llm_failures_total
llm_schema_failures_total
ocr_jobs_total
ocr_failures_total
safety_decisions_total
safety_hard_overrides_total
mental_health_routes_total
crisis_fallback_total
provider_queries_total
stale_resources_total
referrals_total
referral_status_total
jobs_total
job_failures_total
model_inferences_total
model_inference_failures_total
outbox_pending
outbox_delivery_failures
retention_purge_failures
```

---

# 89. Configuration

Separate:

## Environment configuration
Database URLs, provider endpoints, secrets references.

## Runtime configuration
Enabled languages, features, integration toggles.

## Versioned governance configuration
Safety policy, crisis resources, self-care packs, model thresholds, provider-routing rules.

Governance changes should be auditable.

---

# 90. Secrets

Local development may use ignored `.env` files.

Production should use a secret manager.

Secrets must not be stored in source, database configuration tables, logs, or frontend bundles.

---

# 91. Feature Registration

Initial extensibility is compile-time feature registration.

Pseudo-example:

```python
FEATURE_MODULES = [
    IdentityModule(),
    ConsentModule(),
    PatientModule(),
    IntakeModule(),
    SafetyModule(),
    DocumentModule(),
]
```

Dynamic untrusted runtime plugins are not required.

The project needs modular extensibility, not arbitrary code execution.

---

# 92. New Feature Integration Process

Every new feature follows:

```text
IDEA
 -> feature proposal
 -> requirement IDs
 -> safety/privacy classification
 -> bounded-context decision
 -> capabilities/contracts
 -> data ownership
 -> APIs/events
 -> feature flag
 -> implementation
 -> tests
 -> observability
 -> staging
 -> release
```

---

# 93. New Feature Architecture Checklist

Before coding:

```text
[ ] owning module identified
[ ] user problem documented
[ ] dependencies explicit
[ ] capabilities exposed/consumed
[ ] data ownership defined
[ ] APIs defined
[ ] events defined
[ ] permissions defined
[ ] feature flag considered
[ ] safety class assigned
[ ] privacy impact assessed
[ ] failure/degraded state defined
[ ] telemetry defined
[ ] tests defined
[ ] rollback/disable path defined
```

---

# 94. Example — Wearables

New module:

```text
wearables
```

Port:

```text
WearableProviderPort
```

Events:

```text
WearableObservationImported
WearableSyncFailed
```

Consumes:

```text
patients.read
consent.check
```

Does not require changes to OCR, QML, or mental-health internals.

---

# 95. Example — Medical Image AI

New module:

```text
imaging_ai
```

Consumes:

```text
patients.read
encounters.read
risk.predict
```

Publishes:

```text
ImagingAssessmentCreated
```

Clinician UI adds an imaging panel through a feature slot.

No rewrite of core intake.

---

# 96. Example — Nutrition

New module:

```text
nutrition
```

Consumes:

```text
patients.read
allergies.read
medications.read
```

Owns nutrition preferences/plans/content.

It does not modify the patient master schema into a nutrition-specific model.

---

# 97. Example — New Disease Model

Do not spread:

```text
if disease == ...
```

through the codebase.

Instead:

1. define model task;
2. define input schema;
3. define normalized output;
4. implement/register artifact;
5. add evaluation;
6. promote version;
7. optionally add UI;
8. update policy only if the model influences care action.

---

# 98. Dependency Direction

Preferred direction:

```text
interface
  |
application
  |
domain
  |
ports
  ^
  |
infrastructure adapters
```

Domain code should not import FastAPI, concrete SQLAlchemy session handling, React concepts, or vendor SDKs.

---

# 99. Forbidden Coupling

Forbidden:

```text
self_care imports patient ORM models
mental_health imports LLM vendor SDK directly
documents writes medication rows directly
provider routing asks LLM to invent doctor information
QML route handler writes patient diagnosis
```

Correct patterns use public services, events, adapters, and governed policy.

---

# 100. Synchronous Intake Workflow

```text
POST answer
  |
Interface validation
  |
Intake application service
  |
load patient longitudinal context
  |
local safety scan
  |
task-specific structured extraction
  |
schema validation
  |
update intake
  |
safety.evaluate
  |
next question / route
  |
response
```

---

# 101. Asynchronous Document Workflow

```text
Upload
  |
document transaction + outbox
  |
COMMIT
  |
worker
  |
OCR
  |
classification
  |
medical entity extraction
  |
store extraction + provenance
  |
ClinicalFactsExtracted event
  |
review / timeline projection
```

---

# 102. Referral Workflow

```text
care route recommends referral
  |
show verified destinations
  |
user selects
  |
show exact shared fields
  |
explicit consent
  |
create referral
  |
ReferralCreated event
  |
destination adapter
  |
status updates
```

---

# 103. FHIR Export Workflow

```text
authorized export request
  |
authorization + consent
  |
load structured data
  |
FHIR mapping
  |
validation
  |
FHIR gateway
  |
external system
  |
exchange metadata
```

---

# 104. Feature Rollout States

Features may have:

```text
DISABLED
INTERNAL
STAGING
PILOT
ENABLED
```

High-risk activation may additionally require clinical approval and safety test gates.

---

# 105. Kill Switches

Independent kill switches SHOULD exist for:

- generative replies;
- specific model/provider;
- external referrals;
- stale critical resources;
- self-care;
- QML patient-facing inference;
- ABDM sync;
- unsafe language pathway;
- specific policy version rollback.

Core urgent resources remain available.

---

# 106. Versioning

Behaviorally important versioned artifacts include:

```text
API
event
extractor schema
prompt
language pack
physical safety policy
mental-health policy
self-care knowledge pack
provider-routing policy
resource registry snapshot
ML model
QML model
calibration
FHIR mapping
consent document
```

---

# 107. API Versioning

Start with:

```text
/api/v1
```

Breaking public contract changes require explicit migration or a new version.

Internal refactoring does not require API version changes if the contract remains stable.

---

# 108. Event Versioning

Event type and schema version are separate.

```text
ClinicalFactExtracted v1
ClinicalFactExtracted v2
```

Consumers explicitly support known versions.

---

# 109. Database Migration Strategy

All database changes use Alembic.

Rules:

- migration required;
- destructive changes separated and justified;
- expensive backfills separated;
- rollback/irreversibility documented;
- compatible phased migrations preferred.

Preferred breaking-change sequence:

```text
add new
deploy compatibility
backfill
switch reads/writes
remove old later
```

---

# 110. Testing Architecture

Required layers:

- unit;
- module integration;
- API contract;
- event contract;
- adapter;
- database;
- frontend component;
- E2E;
- safety;
- AI structured-output regression;
- OCR fixtures;
- multilingual fixtures;
- security;
- accessibility;
- performance;
- ML/QML evaluation.

---

# 111. Architecture Fitness Tests

Where practical, CI should enforce:

- forbidden imports;
- module dependency direction;
- vendor SDK only in adapters;
- no cross-module repository import;
- generated OpenAPI consistency;
- event schema validation.

This is especially valuable when Codex performs broad changes.

---

# 112. CI Architecture

Every pull request should run applicable:

```text
format
lint
typecheck
unit tests
module integration
contract tests
migration checks
frontend tests
dependency/security scans
```

Conditional suites:

```text
policy safety tests
OCR fixtures
FHIR validation
ML evaluation
```

---

# 113. Environments

At minimum:

```text
local
test
staging
pilot
production
```

Research may use separate environments.

Production secrets/data should not be reused in lower environments.

---

# 114. Local Development

Core local stack should be runnable with Docker Compose or equivalent:

```text
patient-web
clinician-web
admin-web
api
worker
postgres
object-store
redis (if selected)
```

Mocks allow development without real external integrations.

---

# 115. Mock and Sandbox Strategy

Important ports should have deterministic mocks:

```text
MockLLMExtractor
MockOCR
MockSpeech
MockFHIRGateway
MockABDMGateway
MockNotificationProvider
MockReferralDestination
MockModelInference
```

External systems may additionally have sandbox adapters.

Levels:

```text
mock
sandbox
production
```

---

# 116. Evolution to Services

Possible later extraction candidates:

```text
document-processing
speech-processing
model-inference
qml-research
notification-delivery
interoperability-gateway
```

Core transactional domains such as consent/patient/safety should remain together until real evidence justifies separation.

---

# 117. Service Extraction Criteria

A module becomes a service only when justified by one or more:

- independent scaling;
- security isolation;
- separate deployment cadence;
- separate runtime/language;
- long-running compute;
- organizational ownership;
- infrastructure requirement.

Every extraction needs an ADR.

---

# 118. Future Agentic AI

If AI agents are later added, they operate through capability tools, not unrestricted database access.

Example:

```text
Agent
  +--> patients.read
  +--> documents.search
  +--> providers.search
  +--> referrals.prepare
```

High-consequence actions require authorization, validation, consent, policy checks, and human confirmation where applicable.

---

# 119. Agent Safety Boundary

An agent cannot bypass:

- safety policy;
- consent;
- authorization;
- provider registry;
- resource registry;
- referral minimization;
- clinician approval requirements.

Agent actions must be auditable.

---

# 120. Clinical Configuration

Safety-sensitive configuration should live in governed/versioned locations such as:

```text
clinical/policies/
clinical/knowledge/
clinical/lexicons/
clinical/test_cases/
```

A later admin workflow may manage approved database-backed versions.

---

# 121. Localization

Separate:

- normal UI localization;
- clinical content;
- crisis content;
- self-care content;
- generated conversational text.

Safety-critical translations require review.

No critical message should exist only as hard-coded English inside a component.

---

# 122. Search Modes

Do not unify all search into vector search.

Use:

- structured provider search;
- structured patient/timeline queries;
- document metadata search;
- optional semantic document retrieval;
- approved knowledge retrieval.

Structured clinical truth remains structured.

---

# 123. Explainability Layers

## Policy decisions
Reason codes + policy version.

## AI extraction
Source + confidence + extractor version.

## ML/QML
Model version + risk output + explanation metadata.

## Provider routing
Care category + filters + resource verification.

## Self-care
Eligibility reason + source + exclusions + escalation rules.

---

# 124. High-Impact Decision Record

Important decisions should support:

```text
decision_id
decision_type
subject/encounter
input references
result
reason codes
policy version
model versions
resource versions
timestamp
actor/system
```

Do not store hidden model chain-of-thought.

---

# 125. Retention

Retention is policy-driven per category.

Examples:

- pseudonymous transcripts;
- documents;
- structured history;
- referrals;
- audit;
- research artifacts.

Purge failures must be observable.

---

# 126. Deletion

Deletion may span:

- PostgreSQL;
- object storage;
- vector/search indexes;
- caches;
- backups under policy.

Deleting one row is not automatically full deletion.

Detailed rules belong in privacy specifications.

---

# 127. Incident Controls

Architecture should allow:

- feature disable;
- policy rollback;
- model rollback;
- resource disable;
- referral integration disable;
- provider adapter disable;
- unsafe language-path disable.

Fixes for safety defects should add regression tests.

---

# 128. Resource Freshness

Resources/providers should support:

```text
verified_at
expires_at
owner
source
status
version
```

Expired resources are visibly stale and handled according to policy.

---

# 129. Multi-Institution Readiness

Avoid hard-coding a single university or hospital.

Architecture should leave room for:

- institution-specific resources;
- institution-specific referral endpoints;
- feature configuration;
- branding;
- policy approvals.

Full multi-tenancy implementation is deferred.

---

# 130. Multi-Tenancy Deferred

Do not build full multi-tenancy until requirements are clear.

However:

- allow institution/context IDs where appropriate;
- avoid global singleton assumptions;
- avoid hard-coded institution IDs.

Future ADR will select row-level, schema-level, or deployment-level isolation if needed.

---

# 131. Medical Terminology Flexibility

Clinical concepts should be able to carry:

- source text;
- normalized label;
- optional code;
- coding-system namespace.

Do not hard-code one terminology system everywhere until the terminology strategy is defined.

---

# 132. Units

Observations should preserve:

- value;
- unit;
- source;
- reference range;
- normalized value if conversion occurs.

Never compare medical numeric values without unit awareness.

---

# 133. Provider Search Location

Precise geolocation should be optional.

Provider search should also support manual:

- city;
- area;
- institution.

Precise location is not a required platform dependency.

---

# 134. Provider Ranking

Ranking should be transparent/configurable based on factors such as:

- specialty;
- service type;
- language;
- location;
- teleconsultation;
- freshness;
- availability.

Commercial ranking must remain separate from clinical relevance.

---

# 135. Concurrency

Concurrency-sensitive operations include:

- clinician confirmation;
- referral status;
- consent revocation;
- policy activation;
- resource verification.

Use optimistic versioning or transactions/locking as appropriate.

---

# 136. Idempotency

Protect against duplicate creation of:

- referrals;
- document jobs;
- external syncs;
- notifications;
- encounter-start requests where applicable.

---

# 137. Document-to-Record Reconciliation

Document extraction must not overwrite confirmed clinical facts directly.

Extracted fact comparison can yield:

```text
duplicate
new
conflicting
superseding_candidate
needs_review
```

Human confirmation can promote appropriate facts.

---

# 138. Timeline Projection

Patient timeline should be a read model composed from authoritative domains.

Modules do not all write into one giant timeline table.

Projection may consume events and should be rebuildable where practical.

---

# 139. Audit vs Events

Domain event:

```text
what happened?
```

Audit record:

```text
who performed what sensitive action?
```

They may be related but are not interchangeable.

---

# 140. Notification Privacy

Notifications should avoid sensitive content on insecure surfaces.

Prefer:

```text
You have an update in SwasthyaSetu.
```

rather than exposing diagnoses or mental-health details.

---

# 141. Human Review Queues

Possible queues:

- low-confidence OCR;
- low-confidence clinical extraction;
- resource expiry;
- policy disagreement;
- research review.

Queue entries should reference entities rather than copy sensitive content unnecessarily.

---

# 142. Human Corrections

Corrections should:

- create a verified current state;
- preserve prior provenance/audit;
- not silently erase extraction history;
- optionally contribute to governed evaluation datasets.

Production models are not automatically retrained on corrections.

---

# 143. Model Improvement Loop

```text
Human Corrections
   |
Governed / de-identified dataset
   |
Research training
   |
Evaluation
   |
Clinical/model governance
   |
Model promotion
```

Production data must not become training data by default.

---

# 144. Synthetic Data

Synthetic data is encouraged for:

- development;
- E2E tests;
- multilingual tests;
- safety fixtures;
- QML development.

Synthetic results must not be misrepresented as real clinical evidence.

---

# 145. Webhooks

Inbound webhooks require:

- signature verification;
- replay protection;
- schema validation;
- idempotency;
- audit.

Outbound webhooks require:

- signed payload;
- retry;
- backoff;
- idempotency;
- failure/dead-letter state;
- observability.

---

# 146. Scheduled Jobs

Examples:

- resource-expiry scan;
- provider-freshness scan;
- retention purge;
- referral timeout;
- metrics rollup;
- model-health check.

Scheduling implementation remains replaceable.

---

# 147. Cost Controls

AI-heavy operations may enforce:

- input/page limits;
- token budgets;
- per-session budgets;
- asynchronous processing;
- approved fallback model.

Cost controls cannot silently weaken safety.

---

# 148. Model Fallback

Fallback must be task-specific and approved.

```text
primary extractor unavailable
 -> approved compatible fallback
```

If none exists:

```text
degraded mode
```

Do not choose arbitrary models dynamically.

---

# 149. AI Output Validation

All structured external AI output must pass schema validation.

Invalid output:

- bounded retry/repair if safe;
- otherwise degraded mode.

Never silently accept malformed partial data.

---

# 150. Prompt Versioning

Each task-specific prompt package should record:

```text
prompt_id
prompt_version
schema_version
compatible models
evaluation fixtures
```

Safety-related prompt changes require regression evaluation.

---

# 151. RAG Versioning

Where RAG is used, outputs should be traceable to:

- corpus/source;
- corpus version;
- relevant retrieval configuration.

RAG is not the source of emergency policy.

---

# 152. Self-Care Translation

Safety-critical self-care translations should be pre-reviewed where feasible.

Do not rely on unconstrained real-time translation for contraindication/escalation instructions without validation.

---

# 153. Caregiver Access

A future caregiver feature requires explicit authorization/scope.

Caregiver identity is distinct from patient identity.

---

# 154. Minors

Adult mental-health policy must not be generalized to minors.

Minor workflows require separate safeguarding, consent, content, and clinical policy.

---

# 155. Real-Time Updates

Real-time transport is optional.

Potential uses:

- document progress;
- referral status;
- clinician queue.

Polling is acceptable initially.

SSE/WebSocket should be introduced only when product value justifies complexity.

---

# 156. Offline / Low Connectivity

PWA may cache:

- application shell;
- localization;
- public help;
- static crisis fallback.

Sensitive clinical submissions should not be stored offline by default until an encrypted/offline threat model is approved.

---

# 157. Feature Retirement

A feature should be removable through:

1. flag disable;
2. stop new writes;
3. preserve/migrate legacy reads;
4. remove UI;
5. remove integration;
6. later remove code/data through migration.

Good extensibility includes safe removal.

---

# 158. Clinical Approval Workflow Readiness

Future maker-checker/governance workflows may apply to:

- safety policies;
- crisis resources;
- self-care knowledge;
- provider/resource updates;
- model promotion.

Initial implementation may use version-controlled/manual sign-off, but architecture must not prevent automated governance later.

---

# 159. Architecture Decision Records

Material architecture change requires an ADR:

```text
ADR-XXX
Title
Status
Context
Decision
Alternatives
Consequences
Migration
Rollback
```

Codex must not silently make architecture changes.

---

# 160. Initial ADR Decisions

## ADR-001
Use modular monolith initially.

## ADR-002
Use ports/adapters for external AI and healthcare integrations.

## ADR-003
Deterministic policy owns safety-critical routing.

## ADR-004
FHIR is an interoperability boundary, not internal domain model.

## ADR-005
Research/QML is isolated from runtime clinical authority.

## ADR-006
Use typed events + transactional outbox for asynchronous reactions.

## ADR-007
Use compile-time feature registration rather than arbitrary runtime plugins.

## ADR-008
PostgreSQL is transactional source of truth.

## ADR-009
Object storage owns binary medical documents.

## ADR-010
AI-derived facts require provenance and verification state.

---

# 161. Non-Functional Architecture Priorities

Priority order:

1. safety;
2. correctness;
3. maintainability;
4. extensibility;
5. testability;
6. privacy;
7. reliability;
8. explainability;
9. accessibility;
10. performance;
11. cost optimization.

Performance does not justify weakening safety boundaries.

---

# 162. Scalability Model

Initial scaling approach:

- stateless API instances where possible;
- horizontal API scaling;
- independently scalable workers;
- PostgreSQL pooling;
- external object storage;
- optional cache;
- extract inference/document processing later if needed.

---

# 163. Architecture Quality Gates

A feature is architecture-compliant when:

```text
[ ] owner module defined
[ ] dependencies explicit
[ ] public contracts typed
[ ] external integrations behind adapters
[ ] data ownership explicit
[ ] no cross-module direct writes
[ ] events versioned where used
[ ] API versioning respected
[ ] feature flag/failure mode considered
[ ] permissions defined
[ ] provenance handled
[ ] safety interaction defined
[ ] privacy impact identified
[ ] observability added
[ ] tests cover boundaries
[ ] rollback/disable path exists
```

---

# 164. Codex Architecture Rules

Codex MUST:

1. identify the owning module before adding business logic;
2. use public module interfaces;
3. avoid direct cross-module repository/ORM access;
4. isolate external providers behind adapters;
5. preserve typed schemas;
6. add tests with boundary changes;
7. create migrations for schema changes;
8. preserve safety precedence;
9. preserve provenance;
10. use feature flags when the phase requires them;
11. report architecture deviations;
12. stop rather than invent missing safety-critical policy.

Codex MUST NOT:

1. create a god service;
2. call vendor SDKs from domain/application code;
3. allow LLM prose to choose crisis/emergency route;
4. bypass consent;
5. write into another module's tables directly;
6. make Redis/vector storage authoritative clinical truth;
7. hard-code a single hospital/university through the domain;
8. introduce a microservice without an ADR;
9. add dependencies without justification;
10. silently change the architectural pattern.

---

# 165. Architecture Roadmap

## Foundation
- modular backend shell;
- shared kernel;
- configuration;
- PostgreSQL;
- migrations;
- event envelope;
- outbox;
- logging/metrics;
- adapter conventions.

## Core clinical platform
- identity;
- sessions;
- consent;
- patients;
- encounters;
- intake;
- safety;
- clinician read models.

## Intelligence
- AI gateway;
- documents;
- OCR;
- speech;
- mental health;
- self-care.

## Care navigation
- providers;
- resources;
- referrals;
- notifications.

## Interoperability
- FHIR;
- ABDM.

## Research
- classical ML;
- QML;
- model registry.

## Hardening
- security;
- privacy;
- accessibility;
- performance;
- incident controls.

Detailed sequencing belongs in `34_MASTER_IMPLEMENTATION_PLAN.md`.

---

# 166. Architecture Success Criteria

The architecture succeeds if:

1. new features can be added without widespread unrelated edits;
2. an AI provider can be replaced through an adapter;
3. QML failure does not break patient intake;
4. OCR failure does not invent clinical facts;
5. crisis routing remains available during model failure;
6. clinician-confirmed data remains separate from AI extraction;
7. provider data cannot be fabricated by LLM output;
8. safety decisions are reproducible by version;
9. modules can be tested independently;
10. compute-heavy modules can later be extracted;
11. Codex can navigate the codebase predictably;
12. schema/API evolution is explicit and migration-driven.

---

# 167. Source Alignment

This architecture preserves the project-source requirements:

- SIH26047: multimodal clinical history-taking, document digitization, structured summaries, red flags, privacy/consent, and ABDM/FHIR direction;
- SIH26139: hybrid quantum-classical data pipeline, predictive models, explainability, benchmarking, and software platform;
- MannSetu: LLM structured extraction separated from deterministic policy, crisis fallback, verified resources, referrals, accessibility, privacy, observability, and clinical review.

The capability registry, module manifest, outbox, feature extension process, modular-monolith boundaries, and future-agent/tool architecture are explicit SwasthyaSetu design additions introduced to make the unified system maintainable and extensible.

---

# 168. Deferred Decisions

This document intentionally does not yet freeze:

- cloud provider;
- auth provider;
- LLM provider;
- OCR provider beyond adapter compatibility;
- initial job queue library;
- object-storage provider;
- provider-directory data source;
- exact ABDM flow implementation;
- exact database tables;
- exact API payloads;
- exact clinical safety rules;
- self-care dataset;
- initial disease datasets/models;
- full multi-tenancy strategy.

Codex MUST NOT invent these as permanent architectural decisions before the corresponding specifications are approved.

---

# 169. Next Foundation Documents

Create next:

1. `29_ENGINEERING_STANDARDS.md`
2. `34_MASTER_IMPLEMENTATION_PLAN.md`

Then:

3. `03_REPOSITORY_STRUCTURE.md`
4. `04_DOMAIN_MODEL.md`
5. `05_DATABASE_SCHEMA.md`
6. `06_API_CONTRACTS.md`

Substantial implementation should begin only after the four primary foundation documents are complete.

---

# 170. Final Architecture Statement

SwasthyaSetu AI is designed as:

```text
Feature-oriented web applications
        |
Versioned REST contracts
        |
FastAPI modular monolith
        |
Bounded contexts
        |
Application use cases
        |
Domain rules and deterministic safety policies
        |
Ports
        |
Replaceable adapters
        |
PostgreSQL + object storage
        |
Outbox + workers + optional Redis
```

Its safety path is:

```text
User Input
   |
Structured Extraction
   |
Validation
   |
Deterministic Policy
   |
Governed Action
```

Its feature-extension path is:

```text
New Idea
   |
Requirement IDs
   |
Bounded Module
   |
Capabilities + Contracts
   |
Optional Events + Adapters
   |
Feature Flag
   |
Tests + Observability
   |
Release
```

This is the architecture Codex must preserve throughout implementation.


---

# R3 Architecture Reconciliation Addendum — 2026-10-10

This canonical architecture incorporates the R2-A–R2-E research reconciliation.

## R3-A — Concrete technology activation rule

A technology may be:

```text
researched
candidate
adapter implemented
benchmark winner
pilot approved
production approved
```

These states are not equivalent.

Codex must not convert a research recommendation into a runtime dependency unless the active phase authorizes it.

## R3-B — Default local runtime

The expected minimal local runtime remains:

```text
Next.js app(s) as needed
FastAPI
PostgreSQL
local/test adapters
```

Do not require the full pilot/research ecosystem to run the product locally.

## R3-C — Object storage

`ObjectStoragePort` is mandatory before concrete storage.

Local filesystem is acceptable for controlled development.

SeaweedFS is the preferred self-hosted candidate for later object-storage activation; cloud S3-compatible services may implement the same port.

## R3-D — Identity

Pseudonymous sessions are project-native.

Keycloak is a preferred authenticated-identity target, not a foundation dependency.

## R3-E — OCR

PaddleOCR is the preferred baseline candidate but remains benchmark-gated.

Docling may implement document parsing/normalization.

Document-domain code remains provider-neutral.

## R3-F — Speech/language

Adapters are selected per capability rather than as one monolithic language platform.

Current candidates include:

```text
faster-whisper
IndicConformer
IndicTrans2
IndicLID
IndicXlit
BHASHINI
```

Final ASR/TTS selection remains benchmark-dependent.

## R3-G — FHIR

HAPI FHIR is the preferred conformance/sidecar implementation behind `FHIRProvider`.

Internal domain/PostgreSQL remains canonical.

## R3-H — RAG

Default RAG is:

```text
RetrievalService
 + EmbeddingProvider
 + PostgreSQL/pgvector
 + optional RerankerProvider
```

No core dependency on LangChain or LlamaIndex.

## R3-I — ML

MLflow is research infrastructure.

SwasthyaSetu owns clinical model approval.

ONNX Runtime is preferred when conversion parity passes.

## R3-J — QML

PennyLane is primary research framework; Qiskit Machine Learning is secondary comparison framework.

Both are research-profile dependencies and remain outside the core safety path.

## R3-K — Observability

OpenTelemetry is the contract.

Prometheus/Grafana are deployment backends, not application dependencies.

## R3-L — Infrastructure minimalism

The following are not default local Compose requirements:

```text
Keycloak
SeaweedFS
Valkey
OpenBao
HAPI FHIR
MLflow
Prometheus
Grafana
PaddleOCR
Qiskit/PennyLane
LiteLLM Proxy
```

They activate only in their approved profiles/phases.
