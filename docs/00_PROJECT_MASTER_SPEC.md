# SwasthyaSetu AI
## 00 — Project Master Specification

**Document ID:** `SSAI-MASTER-000`  
**Filename:** `00_PROJECT_MASTER_SPEC.md`  
**Status:** Foundation / Source of Truth  
**Version:** `1.0.0-draft`  
**Primary implementation agent:** Codex  
**Architecture posture:** Extensibility-first, safety-first, modular, replaceable integrations  
**Project type:** India-first multimodal health intake, decision-support, care-navigation, mental-health triage, document intelligence, and research platform

---

# 1. Purpose of This Document

This is the highest-level engineering and product specification for **SwasthyaSetu AI**.

It defines:

- what the project is;
- what it is not;
- permanent architectural and safety invariants;
- the product capabilities that must exist;
- how AI is allowed to participate;
- how clinical and non-clinical decisions are separated;
- the core technical architecture;
- how new features must be added later without destabilizing the platform;
- the rules every future implementation phase and Codex prompt must follow.

This document is intentionally **feature-extensible**. The current feature list is not considered final. New features may be introduced later without rewriting the entire application, provided they comply with the architectural contracts, safety rules, privacy requirements, and module boundaries defined here.

This document should be read together with detailed specifications that will be created later, especially:

- `01_PRODUCT_REQUIREMENTS.md`
- `02_SYSTEM_ARCHITECTURE.md`
- `03_REPOSITORY_STRUCTURE.md`
- `04_DOMAIN_MODEL.md`
- `05_DATABASE_SCHEMA.md`
- `06_API_CONTRACTS.md`
- clinical policy specifications
- AI specifications
- security specifications
- `34_MASTER_IMPLEMENTATION_PLAN.md`
- `CODEX_INSTRUCTIONS.md`

---

# 2. Source Baseline

SwasthyaSetu AI combines requirements from four project sources and additional product extensions.

## 2.1 SIH26047 — Patient Case-Taking Software

The source problem requires an AI-assisted clinical intake system capable of:

- multilingual patient-facing history taking;
- natural voice conversation and guided touch interaction;
- adaptive questioning;
- structured chief complaint and HPI capture;
- past medical/surgical history;
- drug and allergy history;
- family and personal history;
- review of systems;
- AYUSH-specific history where relevant;
- printed and handwritten medical-document OCR;
- medical entity extraction;
- chronological record organization;
- physician-ready summaries;
- red-flag detection;
- privacy and consent controls;
- hospital information-system integration;
- ABDM / ABHA interoperability using FHIR-compatible workflows.

## 2.2 SIH26139 — Hybrid Quantum Machine Learning Platform for Early Disease Detection

The source problem requires a software platform containing:

- biomedical data ingestion;
- data cleaning and normalization;
- missing/noisy data handling;
- dimensionality reduction and feature selection;
- classical machine-learning baselines;
- hybrid quantum-classical architecture;
- quantum-enhanced predictive models such as VQC, QSVM, QNN, or equivalent;
- training and inference workflows;
- early disease-risk prediction;
- explainability;
- sensitivity/specificity-oriented evaluation;
- comparison of hybrid models against classical baselines;
- simulator compatibility;
- optional near-term quantum-hardware compatibility;
- end-to-end evaluation and result visualization.

## 2.3 MannSetu — Mental-Health Digital Front Door

MannSetu contributes a strict safety model:

- conversational intake;
- Hindi/English/Hinglish handling;
- structured mental-health signal extraction;
- deterministic clinician-authored routing;
- low-risk self-help/resource routing;
- professional/counsellor referral;
- crisis/urgent-human-support routing;
- persistent crisis-resource availability;
- verified resource registry;
- referral lifecycle tracking;
- privacy-first operation;
- data minimization;
- explicit referral consent;
- fail-safe behavior on model/parser failure;
- separation between LLM understanding and final route selection.

## 2.4 Additional SwasthyaSetu Features

The unified product additionally includes:

- longitudinal patient history;
- patient-aware symptom handling;
- safe self-care guidance;
- Ayurveda / gharelu supportive-care knowledge;
- contraindication-aware self-care eligibility;
- doctor/specialist discovery;
- verified provider directory;
- appointment/referral handoff;
- clinician dashboard;
- preventive-care and follow-up features;
- research workspace;
- extensible future-feature framework.

---

# 3. Project Vision

> **SwasthyaSetu AI is a multilingual, multimodal digital health front door that transforms patient conversation, previous records, documents and structured health data into an understandable longitudinal health context, detects urgent safety concerns, supports explainable risk screening, provides carefully governed self-care education where appropriate, and connects the patient to the right human care.**

The platform must reduce fragmentation rather than create another isolated healthcare application.

---

# 4. Primary Product Goals

The project SHALL aim to:

1. reduce repetitive history-taking during clinical consultation;
2. improve completeness and organization of patient history;
3. digitize fragmented paper and image-based medical records;
4. preserve longitudinal context across encounters;
5. identify clinically governed urgent warning signals early;
6. provide mental-health first-contact triage without replacing human care;
7. enable safe care-navigation toward an appropriate specialty/provider;
8. support low-risk, governed self-care education;
9. provide research-grade classical and hybrid-QML experimentation;
10. integrate with health-information infrastructure through explicit adapters;
11. support multilingual and accessibility-first patient interaction;
12. provide clinicians with transparent, editable AI-assisted summaries;
13. retain provenance for important facts and decisions;
14. remain extensible so future healthcare modules can be added without architectural rewrites.

---

# 5. Explicit Non-Goals

SwasthyaSetu AI is NOT intended to be:

- an autonomous doctor;
- a substitute for emergency services;
- an autonomous psychiatric or psychological service;
- a system that makes unreviewable clinical decisions;
- an unrestricted prescription generator;
- a source of invented doctor contacts;
- a source of invented helpline details;
- an unrestricted remedy generator;
- an unverified medical knowledge chatbot;
- a system that treats an AI inference as a confirmed diagnosis;
- a claim of quantum advantage without benchmark evidence;
- a replacement for hospital HIS/EMR systems;
- a replacement for ABDM infrastructure;
- a replacement for qualified clinicians.

---

# 6. Safety and Clinical Decision Invariants

The following rules are **non-negotiable platform invariants**. Future features must comply with them.

## 6.1 AI Understanding Is Separate From Decision Authority

The generative AI / LLM layer MAY:

- hold conversation;
- translate or normalize language;
- extract structured information;
- summarize information;
- classify document content;
- identify missing information;
- request clarification;
- retrieve approved knowledge;
- explain already-approved outputs.

The generative AI / LLM layer MUST NOT independently:

- diagnose a patient;
- prescribe medication;
- modify medication dosage;
- determine emergency disposition;
- determine the final mental-health crisis route;
- invent care resources;
- invent doctors;
- invent helpline numbers;
- create unapproved medical remedies;
- override deterministic safety rules;
- silently convert uncertain AI output into confirmed patient history.

## 6.2 Safety Rules Override Other Intelligence

When a configured safety rule is triggered:

`Safety Policy > Predictive Model > LLM > Convenience`

Examples:

- a physical emergency red flag must not wait for a predictive model;
- a high-risk mental-health signal must not be downgraded by a low screening score;
- self-care must be blocked when exclusion criteria are present;
- model unavailability must not remove crisis resources;
- ambiguous high-risk information must fail toward clarification or the safer route.

## 6.3 Human Clinical Authority

A qualified clinician remains responsible for:

- diagnosis;
- prescription;
- clinical examination;
- investigation decisions;
- treatment decisions;
- final interpretation of uncertain cases;
- approval of safety-critical policy where required.

---

# 7. Product Modes

The platform SHALL support multiple workflows without forcing all users through the same experience.

## 7.1 Anonymous / Pseudonymous First-Contact Mode

Designed mainly for mental-health first contact, low-friction screening, and users unwilling to identify themselves initially. This mode should minimize identity collection.

## 7.2 Authenticated Continuity Mode

Designed for longitudinal patient history, hospital interaction, repeat users, ABHA/HIS-connected workflows, and clinician review.

## 7.3 Hospital / Kiosk Mode

Designed for OPD pre-consultation history collection, document scanning, assisted accessibility, and rapid physician handoff.

## 7.4 Clinician Mode

Designed for summary review, source inspection, correction, confirmation, patient timeline, and referral follow-up.

## 7.5 Administrative / Governance Mode

Designed for provider/resource verification, policy management, knowledge approval, audit, clinical-review queues, and feature configuration.

## 7.6 Research Mode

Designed for classical ML, QML, dataset experimentation, model evaluation, model registry, explainability, and benchmark comparison.

Research mode must remain logically isolated from production clinical decision authority.

---

# 8. Core Capability Domains

The initial platform shall contain the following capability domains. These are logical modules, not necessarily independent deployed microservices.

1. Session and identity
2. Consent and privacy
3. Patient profile
4. Encounter management
5. Longitudinal clinical history
6. Conversational intake
7. Multilingual speech/language
8. Physical-health safety
9. Mental-health safety
10. Document ingestion
11. OCR and document intelligence
12. Clinical summarization
13. Provenance
14. Self-care knowledge
15. Ayurveda / gharelu supportive-care guidance
16. Provider directory
17. Specialty routing
18. Referral lifecycle
19. Resource registry
20. FHIR interoperability
21. ABDM adapter
22. Classical ML
23. Quantum ML
24. Model registry
25. Explainability
26. Clinician review
27. Administrative governance
28. Audit
29. Observability
30. Notification/follow-up
31. Feature configuration
32. Future feature modules

---

# 9. Extensibility-First Architecture

## 9.1 Architectural Goal

A new feature should normally be implementable by adding:

- one bounded module;
- its contracts;
- its data ownership;
- optional API routes;
- optional UI components;
- optional domain events;
- configuration/policy;
- tests;
- documentation;

without modifying unrelated domains.

A new feature MUST NOT require rewriting the complete backend, patient history system, safety engine, authentication system, or frontend shell.

---

# 10. Initial Architecture Style

## 10.1 Modular Monolith First

The first production-quality implementation SHALL use a:

> **Modular Monolith with Strong Internal Boundaries**

rather than immediately deploying dozens of microservices.

Reasons:

- faster implementation;
- simpler local development;
- easier Codex reasoning;
- easier transactional integrity;
- easier testing;
- lower DevOps overhead;
- clearer early-stage debugging.

However, module boundaries SHALL be written so modules can later become independent services.

## 10.2 Extractable Modules

A module may later be separated into a service when justified by:

- scaling profile;
- security isolation;
- independent deployment cadence;
- computational requirements;
- external dependency complexity;
- team ownership;
- latency characteristics.

Likely future extraction candidates include document AI, speech processing, model inference, QML research, notifications, and external interoperability.

---

# 11. Bounded-Context Rule

Every major feature belongs to an explicit bounded context.

Example contexts:

- `identity`
- `consent`
- `patients`
- `encounters`
- `clinical_intake`
- `safety`
- `mental_health`
- `documents`
- `self_care`
- `providers`
- `referrals`
- `interoperability`
- `ml`
- `qml`
- `audit`

Each bounded context SHALL own its service layer, domain types, persistence operations, business rules, and tests.

Modules SHALL NOT directly reach into another module's internal implementation.

---

# 12. Module Contract

Every substantial new feature SHALL provide a module manifest.

Conceptual example:

```yaml
module:
  id: preventive-care
  version: 1.0.0

capabilities:
  - preventive.reminders
  - preventive.followup

requires:
  - patients.read
  - encounters.read
  - notifications.send

publishes_events:
  - PreventiveReminderCreated
  - PreventiveReminderCompleted

subscribes_events:
  - EncounterClosed
  - InvestigationRecorded

api:
  prefix: /api/v1/preventive

permissions:
  - preventive:view
  - preventive:manage

feature_flags:
  - preventive_care_enabled
```

The exact implementation format may change in the detailed architecture specification, but the principle is mandatory.

---

# 13. Capability Registry

The application SHOULD maintain a logical capability registry.

Features should depend on capabilities rather than hard-coded implementations.

Examples:

- `speech.transcribe`
- `speech.synthesize`
- `translation.translate`
- `ocr.extract`
- `llm.extract`
- `safety.evaluate`
- `providers.search`
- `referrals.create`
- `fhir.export`
- `risk.predict`
- `selfcare.retrieve`

This permits replacing implementation providers without changing business workflows.

---

# 14. Ports and Adapters

External systems SHALL be accessed through explicit interfaces/adapters.

Examples:

```text
SpeechToTextProvider
TextToSpeechProvider
TranslationProvider
LLMProvider
OCRProvider
ObjectStorageProvider
FHIRProvider
ABDMProvider
NotificationProvider
QuantumBackend
ModelInferenceProvider
GeocodingProvider
AppointmentProvider
```

Business logic SHALL NOT directly import vendor SDKs where an adapter should exist.

Example:

```python
class OCRProvider(Protocol):
    async def extract(self, document: DocumentInput) -> OCRResult:
        ...
```

Then implementations may include:

```text
PaddleOCRProvider
CloudOCRProvider
MockOCRProvider
```

This rule is central to long-term extensibility.

---

# 15. Domain Events

Modules SHALL be able to communicate through typed domain events where synchronous coupling is unnecessary.

Initial implementation MAY use an in-process event bus. Future implementations MAY move selected events to Redis Streams, Kafka, NATS, RabbitMQ, or equivalent.

Example events:

```text
PatientCreated
EncounterStarted
ConsentGranted
ConsentRevoked
DocumentUploaded
DocumentProcessed
ClinicalFactExtracted
SafetySignalDetected
RouteDecided
ProviderSelected
ReferralCreated
ReferralAcknowledged
ClinicalSummaryConfirmed
ModelInferenceCompleted
EncounterClosed
```

Event schemas SHALL be versioned. Modules SHALL NOT depend on undocumented event payloads.

---

# 16. Synchronous vs Event-Driven Rule

Use synchronous calls when the user is waiting for an immediate answer, strong consistency is required, or a workflow cannot continue without the result.

Use domain events when another module is reacting to an already-completed action, eventual consistency is acceptable, or the caller should not know downstream implementation details.

Example:

```text
Document Upload
    |
    +--> synchronous validation
    |
    +--> asynchronous DocumentUploaded event
                           |
                           +--> OCR
                           +--> entity extraction
                           +--> timeline update
                           +--> summary refresh
```

---

# 17. Feature Flags

New capabilities SHOULD be deployable behind feature flags.

Examples:

```text
mental_health_enabled
ayurveda_selfcare_enabled
qml_inference_enabled
voice_intake_enabled
abdm_enabled
preventive_care_enabled
```

Feature flags SHALL NOT be used to bypass required security or safety controls. A disabled feature must fail cleanly without breaking unrelated features.

---

# 18. Versioned Policies

Safety-sensitive logic SHALL be externalized into versioned policy/configuration where practical.

Examples:

- red-flag policy;
- mental-health route policy;
- self-care eligibility policy;
- provider routing policy;
- crisis-resource configuration;
- language-specific safety lexicons;
- model thresholds.

Every safety-relevant decision SHOULD be reproducible from:

```text
structured inputs
+
policy version
+
model version if applicable
+
resource version if applicable
```

---

# 19. UI Extensibility

The frontend SHALL use composable feature modules.

A new feature should be able to contribute routes, navigation entries, dashboard cards, encounter panels, patient timeline entries, admin configuration pages, and feature-specific forms.

Avoid one giant patient page containing hard-coded conditionals for every future feature.

Conceptual structure:

```text
features/
  intake/
  documents/
  mental-health/
  providers/
  self-care/
  preventive-care/
```

Shared UI primitives SHALL live outside individual feature modules.

---

# 20. Database Extensibility

## 20.1 Single PostgreSQL Cluster Initially

The initial system MAY use one PostgreSQL database for simplicity. However, module ownership SHALL remain explicit.

## 20.2 Ownership Rule

A module owns its tables. Other modules SHOULD NOT directly mutate those tables.

Cross-module access should happen through service contracts, domain events, explicit read models, or stable shared schemas where approved.

## 20.3 Schema Changes

Every database change SHALL use migrations.

No Codex prompt may silently modify the database schema without a migration, rollback consideration, updated schema documentation, and tests.

---

# 21. API Extensibility

APIs SHALL be versioned.

Default route structure:

```text
/api/v1/...
```

New features SHALL use their own namespace where appropriate.

Examples:

```text
/api/v1/intake
/api/v1/documents
/api/v1/mental-health
/api/v1/providers
/api/v1/referrals
/api/v1/self-care
/api/v1/research/qml
```

Breaking API changes require an explicit version change or migration strategy, contract tests, and documentation update.

---

# 22. Contract-First Engineering

Internal and external boundaries SHALL use typed schemas.

Primary technologies:

- Pydantic v2 for Python runtime schemas;
- TypeScript types generated/shared where practical;
- OpenAPI for REST contracts;
- JSON Schema where useful;
- FHIR resources at interoperability boundaries.

Business-critical contracts SHALL be tested.

---

# 23. Data Provenance

Every clinically meaningful fact SHOULD record provenance.

Possible source types:

```text
patient_report
caregiver_report
ocr
document_ai
fhir_import
abdm_import
hospital_import
model_inference
clinician
admin
```

Example conceptual record:

```json
{
  "value": "Metformin 500 mg",
  "source_type": "ocr",
  "source_id": "document-123",
  "confidence": 0.93,
  "verified_by_clinician": false,
  "created_at": "..."
}
```

Clinician-confirmed information MUST remain distinguishable from AI-extracted information.

---

# 24. Clinical Data Confidence

AI-derived clinical facts SHALL support states such as:

```text
extracted
low_confidence
needs_confirmation
patient_confirmed
clinician_confirmed
rejected
superseded
```

Low-confidence facts must not silently become trusted clinical truth.

---

# 25. Longitudinal Patient Context

The longitudinal patient context is a central shared platform capability.

It SHOULD include:

- demographics where available;
- active problems;
- previous problems;
- medications;
- allergies;
- past procedures;
- encounters;
- investigations;
- lab values;
- documents;
- referrals;
- confirmed clinical summaries;
- relevant consent;
- risk-assessment history.

Future modules SHOULD consume this context through stable read interfaces rather than duplicating their own patient-history system.

---

# 26. Clinical Intake Domain

Clinical intake SHALL support:

- chief complaint;
- history of present illness;
- onset;
- duration;
- location;
- character;
- severity;
- progression;
- associated symptoms;
- aggravating factors;
- relieving factors;
- past medical history;
- surgical history;
- medication history;
- allergy history;
- family history;
- personal history;
- review of systems;
- prior investigations.

Adaptive questioning SHALL avoid unnecessarily asking for facts already available and sufficiently reliable.

---

# 27. AYUSH / Ayurveda History

When configured for appropriate workflows, intake may include clinician-defined Ayurvedic fields such as those required by the SIH case-taking source.

These fields SHALL be modular, optional, clearly typed, governed separately from conventional clinical data where necessary, and enabled only for relevant workflows.

---

# 28. Physical Safety Module

The physical-health safety module SHALL:

- run before self-care output;
- support deterministic red flags;
- provide reason codes;
- record policy version;
- support clarification;
- allow urgent escalation;
- operate independently of LLM prose.

The detailed rules will live in `08_SAFETY_AND_TRIAGE_POLICY.md`.

---

# 29. Mental-Health Module

The mental-health module SHALL preserve the MannSetu architecture:

```text
Conversation
    |
LLM structured extraction
    |
Schema validation
    |
Safety lexicon/backstop
    |
Deterministic policy
    |
Route / clarification / crisis fallback
```

The LLM may not independently choose the final crisis route.

Crisis information SHALL remain accessible during LLM outage, parser failure, model timeout, or partial platform degradation.

---

# 30. Document Intelligence

The document pipeline SHALL support:

```text
Upload / Camera Capture
        |
File Validation
        |
Preprocessing
        |
OCR
        |
Layout / Document Classification
        |
Medical Entity Extraction
        |
Confidence Validation
        |
Human Confirmation where required
        |
Timeline / Structured Record
```

Initial document categories may include prescription, lab report, discharge summary, diagnostic report, imaging report, and referral letter.

New document types SHALL be addable using registered parsers/extractors rather than modifying one giant parser.

---

# 31. Self-Care and Ayurveda / Gharelu Guidance

The system SHALL treat this feature as:

> supportive self-care education for selected low-risk contexts

and NOT as:

> autonomous disease diagnosis and cure.

The module must support:

- eligibility rules;
- red-flag exclusions;
- contraindications;
- medication-conflict checks where validated;
- age restrictions where validated;
- pregnancy restrictions where validated;
- chronic-condition exclusions where applicable;
- source provenance;
- clinical review status;
- expiry/review date;
- escalation criteria;
- duration limits.

The LLM SHALL retrieve/explain approved content rather than invent treatment.

---

# 32. Provider and Care Navigation

Provider navigation SHALL follow:

```text
Clinical context
      |
Care category
      |
Specialty/service type
      |
Verified provider/resource query
      |
Transparent filtering
      |
Contact / referral / booking
```

Provider data SHALL come from a registry or validated external source. The LLM SHALL NOT manufacture provider contact information.

Provider records SHOULD support name, specialty, facility, location, languages, contact, booking URL, teleconsultation, working hours, source, verified_at, expires_at, and active/stale status.

---

# 33. Referral Lifecycle

Referrals SHOULD support a lifecycle such as:

```text
OFFERED
  -> CONSENTED
  -> SENT
  -> ACKNOWLEDGED
  -> SCHEDULED
  -> COMPLETED

Alternative:
  -> DECLINED
  -> UNREACHABLE
  -> EXPIRED
```

Full private conversations SHALL NOT be sent to external institutions by default.

---

# 34. Classical Machine Learning

Classical ML is the mandatory baseline for predictive research.

Initial candidate techniques may include logistic regression, random forest, gradient boosting / XGBoost, SVM, MLP, and task-appropriate alternatives.

Every predictive task SHALL define dataset, label, inclusion/exclusion, preprocessing, split strategy, leakage prevention, metrics, calibration, threshold strategy, model card, and limitations.

---

# 35. Hybrid Quantum Machine Learning

QML SHALL be implemented as a research and decision-support module.

Possible implementations include VQC, QNN, QSVM, and other justified hybrid approaches.

QML SHALL NOT automatically replace classical models.

Every QML experiment SHALL compare fairly against classical baselines.

No "quantum advantage" claim may be made unless supported by reproducible benchmark evidence.

---

# 36. Predictive Output Boundary

Predictive systems may return outputs such as:

```json
{
  "model_id": "example-model",
  "model_version": "1.2.0",
  "risk_probability": 0.71,
  "risk_band": "elevated",
  "input_quality": "valid",
  "calibration_version": "cal-v2"
}
```

The model response itself SHALL NOT create a confirmed diagnosis, prescribe treatment, or override hard safety rules.

---

# 37. FHIR and ABDM

FHIR SHALL be treated as an interoperability boundary. The internal domain model does not have to copy FHIR exactly.

Mappings will be defined later for resources such as Patient, Encounter, Observation, Condition, AllergyIntolerance, MedicationStatement / MedicationRequest, DiagnosticReport, DocumentReference, and Consent.

ABDM/ABHA functionality SHALL be isolated behind adapters so sandbox/prod implementations can evolve without rewriting core workflows.

---

# 38. Technology Baseline

## Frontend
- Next.js
- React
- TypeScript
- Tailwind CSS
- PWA

## Backend
- Python 3.12+
- FastAPI
- Pydantic v2
- SQLAlchemy 2.x
- Alembic

## Database
- PostgreSQL
- pgvector where justified
- Redis only for ephemeral state/caching/queues where required

## AI
- provider-agnostic LLM adapter
- structured output / JSON schema
- PyTorch
- scikit-learn
- XGBoost

## OCR
- PaddleOCR initially, behind adapter

## Speech / Indian Languages
- AI4Bharat / Bhashini-compatible integrations
- provider abstraction mandatory

## QML
- PennyLane and/or Qiskit

## Interoperability
- FHIR
- ABDM / ABHA adapters

## Operations
- Docker
- OpenTelemetry
- GitHub Actions or equivalent CI
- Terraform/OpenTofu where infrastructure-as-code becomes necessary

Specific providers may change later without violating this master specification.

---

# 39. Dependency Rule

A dependency SHALL be introduced only when it provides clear value.

Before adding a dependency, Codex SHOULD evaluate purpose, maintenance status, license, security, API stability, compatibility, ability to replace it, and whether an existing project dependency already solves the need.

External library choice must not redefine core domain architecture.

---

# 40. Privacy Principles

The platform SHALL follow:

- purpose limitation;
- data minimization;
- explicit consent where applicable;
- minimal external sharing;
- short retention where possible;
- access control;
- encryption;
- auditability;
- deletion/withdrawal workflows where technically applicable;
- separation between identity and anonymous/pseudonymous workflows where appropriate.

Sensitive data must not be logged by default.

---

# 41. Security Baseline

The platform SHALL support:

- TLS;
- encryption at rest;
- RBAC;
- admin MFA;
- secure secret management;
- audit logging;
- rate limiting;
- secure upload validation;
- content sanitization;
- dependency scanning;
- container scanning;
- least privilege;
- safe session management;
- model/provider timeout handling;
- prompt-injection defenses;
- output schema validation.

---

# 42. Observability

Observability SHALL focus on operational metadata rather than sensitive content.

Examples:

```text
requests_total
request_latency
llm_failures_total
extractor_schema_failures_total
ocr_failures_total
safety_rule_hits_total
route_decisions_total
referral_status_total
resource_stale_count
model_inference_latency
model_errors_total
purge_failures_total
```

Raw medical conversation SHOULD NOT be emitted into normal application logs.

---

# 43. Version Everything That Can Change Behavior

At minimum, version:

- API contracts;
- database migrations;
- prompts;
- extractor schemas;
- language resources;
- safety lexicons;
- red-flag policies;
- mental-health policies;
- self-care knowledge;
- provider/resource records;
- ML models;
- QML models;
- calibration settings;
- thresholds;
- FHIR mappings;
- consent text;
- external-integration schemas.

---

# 44. Failure Isolation

A failure in one optional feature SHALL NOT cause unrelated healthcare workflows to fail.

Examples:

- QML unavailable -> normal clinical intake still works;
- OCR unavailable -> patient can continue manual intake;
- speech unavailable -> text/touch remains available;
- LLM unavailable -> static crisis resources remain accessible;
- provider integration unavailable -> verified cached/manual resources may remain available;
- preventive-care module disabled -> consultation intake still works.

---

# 45. Graceful Degradation

Each external dependency SHALL define timeout, retry, fallback, degraded-mode behavior, user-facing message, observability, and recovery behavior.

No subsystem may pretend success when its required dependency failed.

---

# 46. New Feature Integration Standard

Every future feature MUST answer the following before implementation.

## 46.1 Product

- What user problem does it solve?
- Which users use it?
- Is it clinical, administrative, research, or informational?
- Does it affect patient safety?
- What is explicitly out of scope?

## 46.2 Architecture

- Which bounded context owns it?
- Does it require a new module?
- Which capabilities does it consume?
- Which capabilities does it expose?
- Which domain events does it publish?
- Which events does it consume?
- Does it need synchronous APIs?
- Can it fail independently?

## 46.3 Data

- Which data does it read?
- Which data does it own?
- Does it contain personal or health information?
- What is the retention policy?
- Does it require migrations?
- What provenance is required?

## 46.4 Safety

- Can incorrect output cause harm?
- Does it require deterministic rules?
- Does it need clinical approval?
- What is the fail-safe state?
- Which existing safety policies must run before it?

## 46.5 Security and Privacy

- What permissions are required?
- What new trust boundaries are introduced?
- Is external data sharing required?
- What consent is required?
- What is logged?

## 46.6 UI

- Which user surfaces are affected?
- Can it be added as a feature module?
- What loading/error/disabled states exist?
- Is accessibility covered?

## 46.7 Operations

- What feature flag controls it?
- What metrics are required?
- What alerts are required?
- What rollback mechanism exists?

## 46.8 Verification

- Unit tests?
- Integration tests?
- Contract tests?
- Safety tests?
- E2E tests?
- Acceptance criteria?

A feature should not begin implementation until these questions are sufficiently answered.

---

# 47. Change Classification

Changes SHOULD be classified before implementation.

## Class A — Local Feature Change

No safety or contract implications. Example: non-critical UI enhancement.

## Class B — Domain Feature Change

Adds or changes business capability. Example: preventive reminder module.

Requires module specification, tests, and API/data review.

## Class C — Contract / Data Change

Changes API, events, DB, FHIR, or shared schemas. Requires migration/version strategy.

## Class D — Safety-Critical Change

Changes emergency rules, mental-health routing, self-care eligibility, clinical thresholds, or patient-facing risk interpretation.

Requires clinical review, dedicated regression tests, explicit approval, and version bump.

## Class E — Architecture Change

Changes module ownership, communication pattern, database ownership, deployment topology, or framework.

Requires an Architecture Decision Record (ADR).

---

# 48. Architecture Decision Records

Significant architecture changes SHALL create an ADR.

Suggested structure:

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

Codex SHALL NOT silently introduce major architecture changes.

---

# 49. Feature Lifecycle

New features SHOULD move through:

```text
IDEA
  |
DISCOVERY
  |
SPECIFICATION
  |
ARCHITECTURE REVIEW
  |
IMPLEMENTATION
  |
TEST
  |
SAFETY/SECURITY REVIEW
  |
FEATURE FLAG
  |
STAGING
  |
PILOT
  |
RELEASE
  |
MONITOR
  |
ITERATE / RETIRE
```

---

# 50. Testing Philosophy

Testing is part of implementation, not a later cleanup task.

Required test categories will include:

- unit;
- integration;
- API contract;
- database;
- event contract;
- frontend;
- E2E;
- safety;
- clinical-policy regression;
- LLM structured-output regression;
- OCR fixtures;
- multilingual fixtures;
- security;
- accessibility;
- performance;
- model evaluation.

Safety-critical deterministic routing should target exhaustive branch coverage where practical.

---

# 51. Definition of Done for a Feature

A feature is not complete merely because the UI works.

A feature is complete only when applicable items are satisfied:

- specification updated;
- architecture respected;
- contracts defined;
- migrations created;
- implementation complete;
- unit tests pass;
- integration tests pass;
- relevant E2E tests pass;
- safety tests pass;
- security impact assessed;
- privacy impact assessed;
- accessibility checked;
- error/degraded states implemented;
- observability implemented;
- feature flag implemented if required;
- documentation updated;
- acceptance criteria verified;
- no unrelated regression introduced.

---

# 52. Codex Implementation Rules

Codex SHALL:

1. inspect the repository before editing;
2. read this master specification;
3. read the current phase specification;
4. read the relevant domain specifications;
5. implement only the requested phase/scope;
6. preserve existing public contracts unless explicitly authorized;
7. prefer small cohesive changes;
8. add tests with implementation;
9. run required quality gates;
10. report changed files and test results;
11. identify deviations explicitly;
12. stop rather than invent missing safety-critical policy.

Codex SHALL NOT:

- build future phases accidentally;
- invent clinical rules;
- invent remedies;
- invent provider details;
- bypass adapters;
- create cross-module database coupling casually;
- silently add large dependencies;
- silently change architecture;
- replace deterministic safety rules with LLM reasoning;
- mark work complete without verification.

---

# 53. Documentation Precedence

When documents conflict, use the following precedence unless explicitly revised:

1. approved safety/clinical policy;
2. this Project Master Specification;
3. System Architecture;
4. Product Requirements;
5. Security/Privacy specifications;
6. Domain/Data/API contracts;
7. Master Implementation Plan;
8. current phase specification;
9. individual implementation prompt.

An individual prompt must not silently override a higher-priority safety invariant.

---

# 54. Extensibility Examples

The architecture must support future ideas without a platform rewrite.

## Example A — Wearable Integration

New module:

```text
wearables/
```

Capabilities:

```text
wearables.import
wearables.normalize
```

Event:

```text
WearableObservationImported
```

Consumes:

```text
patients.read
observations.write
```

No change required to clinical-intake internals.

## Example B — Nutrition Module

New module:

```text
nutrition/
```

Consumes patient, condition, and allergy read capabilities. Publishes a versioned result event. Clinical-policy approval may be required depending on outputs.

## Example C — Medication Adherence

New module:

```text
adherence/
```

Consumes medication-read and notification capabilities. No need to modify OCR or QML modules.

## Example D — Remote Vitals

New adapter:

```text
DeviceObservationProvider
```

Publishes:

```text
ObservationRecorded
```

Existing timeline and clinician dashboard can consume the same standard event.

## Example E — New Disease Risk Model

A new disease model is registered through the model registry. The rest of the platform consumes the stable `risk.predict` capability rather than disease-specific infrastructure code.

---

# 55. Repository-Level Extensibility Target

The detailed repository structure will be frozen later, but the intended shape is:

```text
swasthyasetu-ai/
|
+-- apps/
|   +-- patient-web/
|   +-- clinician-web/
|   +-- admin-web/
|
+-- backend/
|   +-- modules/
|   |   +-- identity/
|   |   +-- consent/
|   |   +-- patients/
|   |   +-- encounters/
|   |   +-- intake/
|   |   +-- safety/
|   |   +-- mental_health/
|   |   +-- documents/
|   |   +-- self_care/
|   |   +-- providers/
|   |   +-- referrals/
|   |   +-- interoperability/
|   |   +-- ml/
|   |   +-- audit/
|   |
|   +-- shared/
|   +-- adapters/
|   +-- events/
|
+-- ml/
|   +-- classical/
|   +-- quantum/
|   +-- evaluation/
|
+-- clinical/
|   +-- policies/
|   +-- knowledge/
|   +-- test_cases/
|
+-- infra/
+-- tests/
+-- docs/
```

A feature should usually be added as a module rather than expanding unrelated existing modules.

---

# 56. Architectural Anti-Patterns

The following should be actively avoided.

## 56.1 God Service

Do not create one `HealthcareService` containing all business logic.

## 56.2 God Database Model

Do not create one giant patient JSON object containing every future feature.

## 56.3 LLM-as-Orchestrator for Safety

Do not let the LLM freely decide which clinical path is correct.

## 56.4 Cross-Module Table Mutation

Do not let unrelated modules directly update each other's internal tables.

## 56.5 Vendor Lock-In

Do not scatter provider-specific SDK calls through domain code.

## 56.6 Feature Condition Explosion

Avoid central code such as:

```python
if mental_health:
elif qml:
elif ayurveda:
elif future_feature_1:
elif future_feature_2:
```

Use modules, capabilities, and policies.

## 56.7 Unversioned Behavior

Do not change policy/prompt/model behavior without knowing what version generated a decision.

## 56.8 Silent AI Truth

Do not convert AI-derived text into clinician-confirmed truth automatically.

---

# 57. Non-Functional Goals

Initial engineering targets should include:

- strong typing;
- reproducible local setup;
- migration-based database changes;
- deterministic policy testing;
- structured logging;
- horizontal scalability for stateless API components;
- accessible web interfaces;
- modular provider adapters;
- idempotent external integration where practical;
- graceful degradation;
- clear timeouts;
- explicit retries;
- auditable decisions;
- testable feature flags.

Exact performance targets will be defined in later specifications.

---

# 58. Project Success

SwasthyaSetu AI should be judged by meaningful outcomes rather than the number of AI features.

Examples:

- history completeness;
- physician correction rate;
- clinician time saved;
- OCR entity accuracy;
- red-flag sensitivity;
- mental-health route concordance;
- critical false-negative rate;
- referral completion;
- resource correctness;
- provider freshness;
- patient task completion;
- multilingual performance;
- accessibility;
- privacy compliance;
- model calibration;
- classical-vs-QML benchmark quality;
- system reliability.

---

# 59. Initial Major Implementation Sequence

The detailed implementation plan will be maintained separately.

Current high-level direction:

```text
Foundation
  ->
Identity / Sessions / Consent
  ->
Patient + Encounter Domain
  ->
Longitudinal History
  ->
Patient Frontend
  ->
Clinical Intake
  ->
Safety Engine
  ->
Clinician Dashboard
  ->
Document AI
  ->
Multilingual Speech
  ->
Provider / Referral
  ->
MannSetu Mental Health
  ->
Self-Care / Ayurveda
  ->
FHIR
  ->
ABDM
  ->
Classical ML
  ->
Quantum ML
  ->
Integration
  ->
Hardening / Validation
```

New feature ideas can be inserted when dependencies and safety implications permit. They do not automatically require postponing until the end of the entire project.

---

# 60. Rule for New Ideas During Development

The project explicitly expects new ideas.

When a new idea appears:

1. do NOT immediately ask Codex to implement it;
2. classify the feature;
3. define its module/capabilities;
4. evaluate dependencies;
5. evaluate safety/privacy;
6. decide where it enters the roadmap;
7. update relevant specification;
8. create acceptance criteria;
9. write a phase or sub-phase implementation prompt;
10. implement behind a flag when appropriate.

This is how the architecture remains flexible without becoming chaotic.

---

# 61. Source Traceability

This Master Specification derives core requirements from:

- **SIH26047 — Patient Case-Taking Software**
  - multilingual multimodal intake;
  - structured clinical history;
  - AYUSH history mode;
  - document OCR/intelligence;
  - red flags;
  - physician summary;
  - privacy/consent;
  - ABDM/FHIR direction.

- **SIH26139 — Hybrid Quantum Machine Learning Platform for Early Disease Detection**
  - preprocessing;
  - feature engineering;
  - hybrid QML;
  - classical comparison;
  - prediction;
  - explainability;
  - training/inference;
  - evaluation.

- **MannSetu Complete Implementation Blueprint**
  - non-treatment/non-diagnostic boundary;
  - LLM extraction separated from deterministic routing;
  - fail-safe safety handling;
  - resource verification;
  - referral lifecycle;
  - privacy/data minimization;
  - bilingual handling;
  - validation and release gates.

- **MannSetu Competitive Landscape Research**
  - digital-front-door positioning;
  - India-specific care orchestration;
  - evidence-first validation;
  - routing into existing care rather than replacing human services.

The extensibility mechanisms in Sections 9–25, 44–49, and 54–56 are architectural decisions introduced specifically for the unified SwasthyaSetu implementation.

---

# 62. Master Invariants Summary

Every implementation phase must preserve these invariants:

```text
1. Safety rules outrank AI convenience.
2. LLM understands; governed systems decide.
3. Humans retain clinical authority.
4. AI-derived facts retain provenance.
5. Providers/resources are verified, not invented.
6. Self-care uses approved knowledge, not unrestricted generation.
7. Models produce risk support, not confirmed diagnoses.
8. External technologies sit behind adapters.
9. Features are bounded modules.
10. Cross-module contracts are typed and versioned.
11. Optional feature failure must not collapse the platform.
12. Safety-critical behavior is versioned and testable.
13. Data collection and sharing are minimized and consent-aware.
14. New features are expected and must enter through the extension framework.
15. Architecture changes are explicit, documented and reviewable.
```

---

# 63. Next Required Documents

Before major production implementation begins, create:

1. `01_PRODUCT_REQUIREMENTS.md`
2. `02_SYSTEM_ARCHITECTURE.md`
3. `29_ENGINEERING_STANDARDS.md`
4. `34_MASTER_IMPLEMENTATION_PLAN.md`

Then create:

5. `03_REPOSITORY_STRUCTURE.md`
6. `04_DOMAIN_MODEL.md`
7. `05_DATABASE_SCHEMA.md`
8. `06_API_CONTRACTS.md`

Then create domain-specific clinical, AI, security, and interoperability specifications.

---

# 64. Status

This document establishes the **project constitution**.

It is intentionally designed so that:

> **the feature set can grow without the architecture becoming a collection of tightly coupled hacks.**

Any future implementation that conflicts with these principles must first update this specification or create an approved architecture/safety decision explaining the change.
