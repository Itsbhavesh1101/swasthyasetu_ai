# SwasthyaSetu AI
## 01 — Product Requirements Document (PRD)

**Document ID:** `SSAI-PRD-001`  
**Filename:** `01_PRODUCT_REQUIREMENTS.md`  
**Status:** Foundation / Implementation Source of Truth  
**Version:** `1.0.0-draft`  
**Depends on:** `00_PROJECT_MASTER_SPEC.md`  
**Primary implementation agent:** Codex  
**Requirement style:** Traceable IDs with explicit acceptance intent  
**Extensibility posture:** New capabilities are expected and must be addable without architectural rewrites

---

# 1. Purpose

This document defines **what SwasthyaSetu AI must do**.

It translates the project vision and source problem statements into traceable product requirements that can later be mapped to:

- architecture;
- domain models;
- database tables;
- APIs;
- frontend screens;
- policy rules;
- AI contracts;
- tests;
- implementation phases;
- acceptance criteria.

This PRD intentionally separates **product requirements** from detailed implementation decisions.

The system architecture, repository layout, code standards, database design and implementation sequence will be defined in separate documents.

---

# 2. Requirement Language

The keywords **SHALL**, **MUST**, **SHOULD**, **MAY**, and **MUST NOT** are normative.

- **SHALL / MUST** — required for the applicable release scope.
- **SHOULD** — strongly recommended; deviation must be justified.
- **MAY** — optional capability.
- **MUST NOT** — prohibited behavior.

Requirement IDs are stable identifiers.

Changing the wording of a requirement must not silently reuse the same ID if its meaning materially changes.

---

# 3. Requirement Categories

| Prefix | Domain |
|---|---|
| `FR-CORE` | Core platform |
| `FR-EXT` | Extensibility framework |
| `FR-IDENT` | Identity and sessions |
| `FR-CONSENT` | Consent and privacy |
| `FR-PAT` | Patient profile and longitudinal record |
| `FR-ENC` | Encounters |
| `FR-INTAKE` | Clinical intake |
| `FR-LANG` | Multilingual / speech |
| `FR-SAFE` | Physical-health safety and triage |
| `FR-MH` | Mental-health triage |
| `FR-DOC` | Document AI / OCR |
| `FR-SUM` | Clinical summaries |
| `FR-PROV` | Clinical provenance |
| `FR-SELF` | Self-care / Ayurveda support |
| `FR-DIR` | Doctor/resource directory |
| `FR-REF` | Referrals |
| `FR-CLIN` | Clinician dashboard |
| `FR-ADMIN` | Admin / governance |
| `FR-FHIR` | FHIR interoperability |
| `FR-ABDM` | ABDM / ABHA |
| `FR-ML` | Classical ML |
| `FR-QML` | Quantum ML |
| `FR-RAG` | Knowledge retrieval |
| `FR-NOTIF` | Notifications / follow-up |
| `FR-AUDIT` | Audit |
| `NFR-*` | Non-functional requirements |
| `SAFE-*` | Cross-cutting safety invariants |
| `PRIV-*` | Cross-cutting privacy requirements |

---

# 4. Product Scope Summary

SwasthyaSetu AI SHALL provide one unified product experience spanning:

1. patient-facing digital health intake;
2. structured longitudinal patient history;
3. medical-document digitization and intelligence;
4. physical-health safety screening;
5. mental-health triage and care routing;
6. supported self-care education;
7. Ayurveda / gharelu low-risk supportive guidance;
8. doctor/specialist/resource discovery;
9. referral handoff and tracking;
10. clinician review and summary editing;
11. FHIR / ABDM interoperability;
12. classical ML disease-risk research;
13. hybrid QML disease-risk research;
14. explainability and model comparison;
15. extensible future-feature integration.

---

# 5. Source Traceability

The requirements in this document originate from four source groups:

## SRC-A — SIH26047

Primary contributions:

- patient case-taking;
- multilingual voice + touch;
- adaptive questioning;
- clinical-history structure;
- AYUSH history;
- medical-document OCR;
- chronological records;
- physician-ready summaries;
- red flags;
- privacy/consent;
- ABDM/ABHA/FHIR integration;
- accessibility.

## SRC-B — SIH26139

Primary contributions:

- biomedical preprocessing;
- feature engineering;
- hybrid quantum-classical design;
- VQC / QSVM / QNN or equivalent;
- early disease-risk outputs;
- training and inference;
- explainability;
- sensitivity/specificity;
- classical baseline comparison;
- simulator / near-term hardware compatibility;
- software platform and visualization.

## SRC-C — MannSetu

Primary contributions:

- bilingual/Hinglish mental-health intake;
- LLM extraction boundary;
- deterministic routing;
- fail-safe crisis logic;
- verified resources;
- referral lifecycle;
- data minimization;
- pseudonymous mode;
- privacy;
- accessibility;
- observability;
- safety evaluation.

## SRC-D — Unified SwasthyaSetu Extensions

Primary contributions:

- longitudinal unified record;
- doctor discovery;
- provider registry;
- self-care / Ayurveda knowledge;
- contraindication checking;
- preventive follow-up;
- feature extensibility;
- modular future-feature framework.

---

# 6. User Roles

## 6.1 Patient

A person interacting with SwasthyaSetu for health intake, records, navigation, self-care information or follow-up.

## 6.2 Pseudonymous Mental-Health User

A user who begins without providing identifying information.

## 6.3 Caregiver / Assisted User

A person helping another patient use the application where the deployment allows it.

## 6.4 Clinician

A doctor or qualified health professional reviewing intake, records and decision-support information.

## 6.5 Counsellor / Mental-Health Professional

A qualified professional receiving a consented mental-health referral.

## 6.6 Triage / Nursing Staff

Staff monitoring urgent or priority cases.

## 6.7 Resource / Provider Administrator

A person responsible for verifying doctor, hospital, counsellor and resource information.

## 6.8 Clinical Safety Reviewer

A qualified person responsible for safety policy review.

## 6.9 System Administrator

A restricted technical/operational administrator.

## 6.10 Researcher

A user working inside isolated ML/QML research workflows.

---

# 7. Global Safety Requirements

## SAFE-001 — No autonomous diagnosis

The system MUST NOT present an LLM-generated interpretation or predictive score as a confirmed medical diagnosis.

## SAFE-002 — No autonomous prescription

The system MUST NOT prescribe medication or independently alter an existing prescription.

## SAFE-003 — Safety overrides

Deterministic safety rules MUST take priority over self-care suggestions, LLM recommendations and predictive-model output.

## SAFE-004 — Human clinical authority

Clinician-confirmed information and clinical decisions SHALL remain distinct from AI-generated or AI-extracted information.

## SAFE-005 — Uncertainty

When safety-critical information is ambiguous, the system MUST clarify or choose the safer governed action rather than guess.

## SAFE-006 — Model outage

Failure of an LLM, ML model, QML model, OCR service or other optional AI dependency MUST NOT remove emergency/crisis resources.

## SAFE-007 — No invented resources

LLMs MUST NOT invent doctor contacts, hospital contacts, counsellor contacts, helpline numbers or other referral resources.

## SAFE-008 — No invented remedies

LLMs MUST NOT create unrestricted remedies from model memory for patient-facing use.

## SAFE-009 — Self-care gating

Self-care content MUST NOT be shown when a configured exclusion or urgent-red-flag condition is active.

## SAFE-010 — Versioned safety decisions

Safety-sensitive decisions SHALL record sufficient version metadata to make the route reproducible.

---

# 8. Core Platform Requirements

## FR-CORE-001 — Unified platform

The product SHALL expose patient, clinician, administrative and research capabilities through a coherent SwasthyaSetu platform.

## FR-CORE-002 — Shared longitudinal context

Applicable modules SHALL use one governed longitudinal patient context rather than independently maintaining conflicting patient histories.

## FR-CORE-003 — Modular capabilities

Major functional domains SHALL be independently evolvable modules.

## FR-CORE-004 — Feature independence

Failure or disablement of an optional feature SHALL NOT cause unrelated core workflows to fail.

## FR-CORE-005 — Typed contracts

Cross-module communication SHALL use typed, documented contracts.

## FR-CORE-006 — Versioned public interfaces

Externally consumed APIs and event contracts SHALL be versioned.

## FR-CORE-007 — Patient-facing transparency

The product SHALL clearly distinguish:
- patient-reported information;
- AI-extracted information;
- predictive risk output;
- clinician-confirmed information.

## FR-CORE-008 — No silent data promotion

AI-extracted clinical facts MUST NOT silently become clinician-confirmed facts.

## FR-CORE-009 — Configuration-driven behavior

Safety-sensitive and operational behavior that is expected to change over time SHOULD be configurable and versioned rather than hard-coded across the codebase.

## FR-CORE-010 — Graceful degradation

Each external dependency SHALL define user-visible degraded behavior.

---

# 9. Extensibility Requirements

## FR-EXT-001 — New feature without platform rewrite

A future feature SHALL be addable without rewriting the core patient, identity, consent, intake, safety or authentication systems unless the new feature genuinely changes those domains.

## FR-EXT-002 — Bounded ownership

Every substantial feature SHALL have an explicit owning module/domain.

## FR-EXT-003 — Capability-based integration

Future modules SHOULD consume stable capabilities instead of hard-coding implementation vendors.

Examples:

- `ocr.extract`
- `speech.transcribe`
- `risk.predict`
- `providers.search`
- `notifications.send`

## FR-EXT-004 — Feature registration

A feature SHALL declare its:
- identifier;
- capabilities;
- required permissions;
- required capabilities;
- APIs;
- events;
- configuration;
- feature flags;
- data ownership.

## FR-EXT-005 — Feature flags

New or experimental capabilities SHOULD support controlled activation.

## FR-EXT-006 — Domain events

Modules SHOULD be able to react to versioned domain events without tight coupling where eventual consistency is acceptable.

## FR-EXT-007 — Extractable components

Compute-heavy or independently scalable modules SHOULD be architected so they can later become separate services.

## FR-EXT-008 — No central conditional explosion

New features MUST NOT be implemented by continuously adding global feature-specific `if/else` branches to central orchestration code.

## FR-EXT-009 — New feature safety classification

Every new feature SHALL be classified for product, architectural, data, safety, privacy and operational impact before implementation.

## FR-EXT-010 — New feature acceptance criteria

No future feature SHALL be considered complete without feature-specific acceptance criteria and tests.

## FR-EXT-011 — Architecture decision records

Material changes to system architecture SHALL require an explicit architecture decision record.

## FR-EXT-012 — Replaceable providers

Third-party and open-source integrations SHALL be replaceable through adapters or equivalent isolation.

---

# 10. Identity and Session Requirements

## FR-IDENT-001 — Pseudonymous session

The system SHALL support a session that does not require a name for eligible workflows such as mental-health first contact.

## FR-IDENT-002 — Authenticated patient mode

The system SHALL support authenticated patient continuity for workflows that require stored longitudinal data.

## FR-IDENT-003 — Hospital/kiosk session

The system SHALL support short-lived hospital/kiosk sessions.

## FR-IDENT-004 — Session expiry

Sessions SHALL have explicit lifecycle and expiry rules.

## FR-IDENT-005 — No user fingerprinting

Pseudonymous continuity MUST NOT rely on covert device fingerprinting.

## FR-IDENT-006 — Recovery mechanism

Where anonymous session resumption is supported, it SHOULD use a user-visible recovery token or equivalent privacy-preserving mechanism.

## FR-IDENT-007 — Identity separation

Where practical, directly identifying information SHOULD be separated from clinical/triage content.

---

# 11. Consent and Privacy Requirements

## FR-CONSENT-001 — Privacy notice

The user SHALL receive a clear privacy notice before applicable processing begins.

## FR-CONSENT-002 — Versioned consent

Consent records SHALL capture the consent version.

## FR-CONSENT-003 — Separate referral consent

External referral data sharing SHALL require explicit consent separate from general application use.

## FR-CONSENT-004 — External AI processing disclosure

If patient data is processed by an external AI provider, applicable notice/consent requirements SHALL be represented in the product.

## FR-CONSENT-005 — ABDM consent

ABDM/ABHA data exchange SHALL follow its applicable consent workflow.

## FR-CONSENT-006 — Research consent

Research use of identifiable or linkable patient data SHALL be separately governed.

## FR-CONSENT-007 — Revocation

Where the applicable workflow permits it, the user SHALL be able to revoke previously granted consent.

## FR-CONSENT-008 — Minimal sharing

The system SHALL share only the minimum data required for a referral or integration.

## FR-CONSENT-009 — Consent audit

Consent grant/revocation events SHALL be auditable.

---

# 12. Patient Profile and Longitudinal Record Requirements

## FR-PAT-001 — Patient profile

Authenticated continuity mode SHALL maintain a structured patient profile.

## FR-PAT-002 — Longitudinal timeline

The system SHALL present a chronological timeline of relevant health events.

## FR-PAT-003 — Problems

The system SHALL represent active and historical patient problems.

## FR-PAT-004 — Medications

The system SHALL represent current and historical medications.

## FR-PAT-005 — Allergies

The system SHALL maintain structured allergy/intolerance information.

## FR-PAT-006 — Procedures

The system SHALL support past procedures/surgeries.

## FR-PAT-007 — Investigations

The system SHALL support prior investigations and diagnostic results.

## FR-PAT-008 — Laboratory results

The system SHALL support structured lab results where available.

## FR-PAT-009 — Referral history

The system SHALL retain relevant referral status/history.

## FR-PAT-010 — Data provenance

Each clinically meaningful record SHALL support provenance where the source is known.

## FR-PAT-011 — Confidence state

AI-derived facts SHALL support confidence and verification state.

## FR-PAT-012 — Correction history

Corrections to important clinical data SHOULD remain auditable.

## FR-PAT-013 — Source links

Clinicians SHOULD be able to inspect the source document/message for AI-extracted facts where available.

## FR-PAT-014 — Duplication management

The system SHOULD detect likely duplicate records/documents and prevent silent duplication.

---

# 13. Encounter Requirements

## FR-ENC-001 — Encounter creation

The system SHALL create an encounter or equivalent care episode for applicable clinical-intake workflows.

## FR-ENC-002 — Encounter state

An encounter SHALL have a defined lifecycle.

## FR-ENC-003 — Encounter context

The encounter SHALL reference applicable patient, session, consent and language context.

## FR-ENC-004 — Encounter summary

Each completed intake encounter SHOULD have a structured summary.

## FR-ENC-005 — Encounter closure

The system SHALL support explicit encounter closure.

## FR-ENC-006 — Incomplete encounter

Abandoned or incomplete encounters SHALL remain distinguishable from completed encounters.

---

# 14. Clinical Intake Requirements

## FR-INTAKE-001 — Presenting complaint

The patient SHALL be able to provide a presenting concern in natural language.

## FR-INTAKE-002 — Text input

Clinical intake SHALL support text input.

## FR-INTAKE-003 — Voice input

Clinical intake SHOULD support voice input in configured languages.

## FR-INTAKE-004 — Touch input

Every safety-critical intake question SHOULD have a touch/click alternative to voice.

## FR-INTAKE-005 — Adaptive questioning

The intake engine SHALL ask follow-up questions based on the presenting complaint and prior answers.

## FR-INTAKE-006 — Existing-history reuse

The intake engine SHOULD avoid unnecessarily repeating questions for known, sufficiently reliable information.

## FR-INTAKE-007 — Chief complaint

The system SHALL structure the chief complaint.

## FR-INTAKE-008 — HPI

The system SHALL support history of present illness.

## FR-INTAKE-009 — Onset

HPI SHALL support onset.

## FR-INTAKE-010 — Duration

HPI SHALL support duration.

## FR-INTAKE-011 — Location

HPI SHALL support symptom location when relevant.

## FR-INTAKE-012 — Character

HPI SHALL support symptom character when relevant.

## FR-INTAKE-013 — Severity

HPI SHALL support severity.

## FR-INTAKE-014 — Progression

HPI SHOULD support progression/course.

## FR-INTAKE-015 — Associated symptoms

HPI SHALL support associated symptoms.

## FR-INTAKE-016 — Aggravating factors

HPI SHOULD support aggravating factors.

## FR-INTAKE-017 — Relieving factors

HPI SHOULD support relieving factors.

## FR-INTAKE-018 — Past medical history

The system SHALL collect/represent past medical history.

## FR-INTAKE-019 — Past surgical history

The system SHALL collect/represent past surgical history.

## FR-INTAKE-020 — Drug history

The system SHALL collect/represent medication history.

## FR-INTAKE-021 — Allergy history

The system SHALL collect/represent allergy history.

## FR-INTAKE-022 — Family history

The system SHALL support family history.

## FR-INTAKE-023 — Personal history

The system SHALL support personal history.

## FR-INTAKE-024 — Review of systems

The system SHALL support review of systems.

## FR-INTAKE-025 — Prior investigations

The system SHALL support prior investigation history.

## FR-INTAKE-026 — Missing information

The intake engine SHALL identify clinically relevant missing information.

## FR-INTAKE-027 — Contradiction handling

The intake engine SHALL identify contradictory answers when detectable and request clarification when necessary.

## FR-INTAKE-028 — One-question mode

Sensitive workflows SHOULD support one-question-at-a-time interaction.

## FR-INTAKE-029 — Draft status

AI-generated structured history SHALL remain a draft until appropriately confirmed.

## FR-INTAKE-030 — AYUSH mode

The system SHALL support an optional AYUSH-specific history workflow.

## FR-INTAKE-031 — Ayurvedic history fields

AYUSH mode SHALL support deployment-approved Dashavidha Pariksha-related fields where required.

## FR-INTAKE-032 — Modular specialty questionnaires

Future specialty-specific intake questionnaires SHALL be addable without changing the core intake engine.

---

# 15. Multilingual and Speech Requirements

## FR-LANG-001 — English

The patient-facing system SHALL support English.

## FR-LANG-002 — Hindi

The patient-facing system SHALL support Hindi.

## FR-LANG-003 — Hinglish

The system SHALL support code-mixed Hindi/English in applicable conversational workflows.

## FR-LANG-004 — Romanized Hindi

The system SHOULD recognize common Romanized Hindi input.

## FR-LANG-005 — Language selection

The user SHALL be able to select a preferred language.

## FR-LANG-006 — Language switching

The system SHOULD handle language switching during an active conversation.

## FR-LANG-007 — Original input preservation

The system SHOULD preserve original patient wording where clinically relevant, alongside normalized representation.

## FR-LANG-008 — ASR confidence

Speech recognition output SHOULD include confidence or equivalent quality information where available.

## FR-LANG-009 — ASR fallback

Failure of voice recognition SHALL allow the patient to continue by text/touch.

## FR-LANG-010 — TTS

The system SHOULD support audio prompts for accessibility.

## FR-LANG-011 — Translation safety

Safety-critical translated content SHALL be reviewed/validated before production use.

## FR-LANG-012 — Regional expansion

Additional languages SHALL require language-specific safety and usability validation before full release.

---

# 16. Physical-Health Safety and Triage Requirements

## FR-SAFE-001 — Pre-self-care safety evaluation

Physical red-flag evaluation MUST run before patient-facing self-care recommendations.

## FR-SAFE-002 — Deterministic rules

Physical red-flag logic SHALL support deterministic clinician-approved rules.

## FR-SAFE-003 — Reason codes

Each safety route SHALL return machine-readable reason codes.

## FR-SAFE-004 — Policy version

Each safety decision SHALL record the policy version.

## FR-SAFE-005 — Emergency route

The system SHALL support an urgent/emergency route.

## FR-SAFE-006 — Priority route

The system SHALL support a priority-clinical-review route.

## FR-SAFE-007 — Routine-care route

The system SHALL support a routine-professional-care route.

## FR-SAFE-008 — Supported self-care route

The system SHALL support a low-risk supported-self-care route.

## FR-SAFE-009 — Clarification route

The system SHALL support an explicit insufficient-information/clarification state.

## FR-SAFE-010 — Predictive model non-blocking

The system MUST NOT delay an urgent route waiting for ML/QML inference.

## FR-SAFE-011 — Safety policy tests

Safety rules SHALL have dedicated regression tests.

## FR-SAFE-012 — Safety override

A lower-risk AI/model output MUST NOT override an active hard safety rule.

---

# 17. Mental-Health Requirements

## FR-MH-001 — Mental-health entry

The product SHALL expose a mental-health first-contact workflow.

## FR-MH-002 — Pseudonymous use

The mental-health first-contact workflow SHALL support pseudonymous use.

## FR-MH-003 — Disclosure

The workflow SHALL explain that it is AI-assisted, not therapy, not diagnosis, and not an emergency service.

## FR-MH-004 — Urgent-help control

An urgent-help action SHALL remain visible before and during applicable mental-health conversations.

## FR-MH-005 — Structured extraction

The LLM SHALL output typed mental-health signals rather than a free-form clinical judgement.

## FR-MH-006 — Deterministic routing

Final mental-health route selection SHALL be determined by policy independent of LLM prose.

## FR-MH-007 — Crisis backstop

The system SHALL use a language-aware safety backstop independent of the LLM.

## FR-MH-008 — Active self-harm override

Explicit current high-risk self-harm/suicide indicators SHALL dominate lower-risk scores and protective factors according to approved policy.

## FR-MH-009 — Ambiguity

Ambiguous safety-relevant language SHALL trigger focused clarification or safer routing.

## FR-MH-010 — Route A

The system SHALL support low-risk self-help/psychoeducation with optional professional support.

## FR-MH-011 — Route B

The system SHALL support professional/counsellor referral for non-imminent but meaningful concern.

## FR-MH-012 — Route C

The system SHALL support urgent/crisis human-support routing.

## FR-MH-013 — LLM outage fallback

A high-risk lexical hit during LLM failure SHALL trigger a configured safe fallback.

## FR-MH-014 — No diagnosis language

The mental-health chatbot MUST NOT tell the user they definitively have a mental-health disorder.

## FR-MH-015 — No medication advice

The mental-health chatbot MUST NOT prescribe or change medication.

## FR-MH-016 — Crisis minimal conversation

When crisis routing is active, the product SHOULD minimize unnecessary prolonged chatbot interaction.

## FR-MH-017 — Verified crisis resources

Crisis resources SHALL come from a verified resource registry or bundled fallback.

## FR-MH-018 — Resource expiry

Expired/stale crisis resources SHALL be prevented from normal display where possible and SHOULD trigger operational alerts.

## FR-MH-019 — Referral tracking

Professional-support referrals SHALL be trackable beyond "message sent".

## FR-MH-020 — Clinical evaluation

Release of mental-health routing changes SHALL require safety regression evaluation.

---

# 18. Medical Document Intelligence Requirements

## FR-DOC-001 — Upload

Patients or authorized users SHALL be able to upload supported medical documents.

## FR-DOC-002 — Camera capture

Mobile/kiosk flows SHOULD support camera capture.

## FR-DOC-003 — File validation

Uploads SHALL undergo file-type, size and security validation.

## FR-DOC-004 — Prescription OCR

The system SHALL support OCR for prescriptions.

## FR-DOC-005 — Lab-report OCR

The system SHALL support OCR for lab reports.

## FR-DOC-006 — Discharge-summary OCR

The system SHALL support OCR for discharge summaries.

## FR-DOC-007 — Printed text

The OCR pipeline SHALL support printed documents.

## FR-DOC-008 — Handwriting

The OCR pipeline SHOULD support handwritten medical content where reliable enough for the defined use.

## FR-DOC-009 — Multilingual OCR

The OCR pipeline SHOULD support configured Indian-language documents.

## FR-DOC-010 — Document classification

The system SHALL classify supported document types.

## FR-DOC-011 — Diagnosis extraction

The system SHOULD extract diagnostic terms with provenance/confidence.

## FR-DOC-012 — Medication extraction

The system SHALL extract medication names where possible.

## FR-DOC-013 — Dose extraction

The system SHOULD extract medication dose/frequency where possible.

## FR-DOC-014 — Investigation extraction

The system SHALL extract investigation/lab values where supported.

## FR-DOC-015 — Procedure extraction

The system SHOULD extract prior procedure/surgery information.

## FR-DOC-016 — Date extraction

The system SHALL extract/associate document dates where available.

## FR-DOC-017 — Chronological organization

Processed documents SHALL be organized chronologically.

## FR-DOC-018 — Abnormal-value marking

The system MAY flag out-of-range laboratory values when reference range data is reliably available.

## FR-DOC-019 — Interaction flagging

The system MAY surface potential medication-interaction concerns only through a validated source/process.

## FR-DOC-020 — Low-confidence confirmation

Low-confidence extracted facts SHALL be eligible for human confirmation before trusted use.

## FR-DOC-021 — Original document linkage

Extracted facts SHALL retain a link to their source document.

## FR-DOC-022 — Processing state

Document processing SHALL expose explicit pending/succeeded/failed/needs-review states.

## FR-DOC-023 — New document parsers

New document types SHALL be addable through a registered parser/extractor workflow.

---

# 19. Clinical Summary Requirements

## FR-SUM-001 — Physician-ready summary

The system SHALL generate a concise physician-facing history summary.

## FR-SUM-002 — Standard structure

The summary SHALL support a standard clinical sequence including:
- chief complaint;
- HPI;
- past medical/surgical history;
- medications/allergies;
- family history;
- personal history;
- review of systems;
- prior investigations.

## FR-SUM-003 — Multi-source synthesis

The summary SHALL synthesize conversation and approved structured document data.

## FR-SUM-004 — Draft label

AI-generated summaries SHALL be identified as drafts until confirmed.

## FR-SUM-005 — Clinician edit

The clinician SHALL be able to edit the summary.

## FR-SUM-006 — Clinician accept/reject

The clinician SHALL be able to accept, amend or reject AI-derived content.

## FR-SUM-007 — Patient confirmation

The system MAY provide a simplified patient-facing confirmation step.

## FR-SUM-008 — Summary provenance

Important summary items SHOULD remain traceable to underlying structured facts.

---

# 20. Provenance Requirements

## FR-PROV-001 — Source type

Every AI-extracted clinical fact SHOULD record its source type.

## FR-PROV-002 — Source identifier

Where applicable, the fact SHALL reference the source document/message/resource.

## FR-PROV-003 — Confidence

AI-derived facts SHOULD record confidence/quality metadata where meaningful.

## FR-PROV-004 — Verification state

The system SHALL distinguish extracted, patient-confirmed, clinician-confirmed, rejected and superseded information.

## FR-PROV-005 — Model provenance

Predictive outputs SHALL include model/version metadata.

## FR-PROV-006 — Policy provenance

Routing decisions SHALL include policy version.

## FR-PROV-007 — External-data provenance

FHIR/ABDM imported data SHALL retain origin metadata where available.

---

# 21. Self-Care / Ayurveda Requirements

## FR-SELF-001 — Low-risk scope

The self-care module SHALL operate only on configured low-risk contexts.

## FR-SELF-002 — Supportive framing

Patient-facing content SHALL be framed as supportive self-care/wellness information, not guaranteed disease cure.

## FR-SELF-003 — Curated knowledge

Patient-facing remedies/guidance SHALL come from a curated, versioned knowledge source.

## FR-SELF-004 — Source metadata

Every approved guidance item SHALL record a source/reference category.

## FR-SELF-005 — Review status

Every guidance item SHALL have an approval/review state.

## FR-SELF-006 — Red-flag exclusion

An active safety exclusion SHALL block self-care guidance.

## FR-SELF-007 — Allergy context

Where relevant, self-care eligibility SHALL consider known allergy information.

## FR-SELF-008 — Medication context

Where supported by validated rules/data, self-care eligibility SHOULD consider medication conflicts.

## FR-SELF-009 — Chronic-condition context

Relevant known chronic-condition exclusions SHOULD be considered.

## FR-SELF-010 — Age restrictions

Age restrictions SHALL be enforceable where defined.

## FR-SELF-011 — Pregnancy restrictions

Pregnancy-related restrictions SHALL be enforceable where defined and when the relevant data is explicitly available.

## FR-SELF-012 — Duration guidance

Approved guidance SHOULD state an observation/duration limit where clinically relevant.

## FR-SELF-013 — Escalation criteria

Approved guidance SHALL state when to stop self-care and seek professional/urgent care.

## FR-SELF-014 — No model-memory treatment

An LLM MUST NOT generate patient-facing treatment outside the approved knowledge system.

## FR-SELF-015 — Clinician governance

Safety-relevant self-care rules/content SHALL require appropriate clinical review before production use.

## FR-SELF-016 — Knowledge version

Every delivered guidance item SHALL be traceable to its content version.

## FR-SELF-017 — New guidance packs

New self-care knowledge packs SHALL be addable without changing the core self-care engine.

---

# 22. Provider and Care Directory Requirements

## FR-DIR-001 — Specialty-first routing

The system SHOULD map patient context to a care category/specialty before selecting individual providers.

## FR-DIR-002 — Verified registry

Named provider/resource data SHALL come from a verified registry or validated integration.

## FR-DIR-003 — Provider name

Provider records SHALL support a display name.

## FR-DIR-004 — Specialty

Provider records SHALL include normalized specialty/service type.

## FR-DIR-005 — Facility

Provider records SHOULD include facility affiliation.

## FR-DIR-006 — Contact method

Provider records SHALL support one or more verified contact methods.

## FR-DIR-007 — Booking link

Provider records MAY include a booking URL/integration.

## FR-DIR-008 — Location

Provider records SHOULD support location.

## FR-DIR-009 — Languages

Provider records SHOULD support languages served.

## FR-DIR-010 — Teleconsultation

Provider records SHOULD represent teleconsultation availability.

## FR-DIR-011 — Hours

Provider/resource records SHOULD represent known operating hours.

## FR-DIR-012 — Verification time

Every external provider/resource record SHALL have a verification timestamp where managed by the platform.

## FR-DIR-013 — Expiry

Managed provider/resource records SHOULD have verification expiry.

## FR-DIR-014 — Stale state

Stale resources SHALL be identifiable.

## FR-DIR-015 — Transparent filters

User-facing provider filters/ranking factors SHOULD be transparent.

## FR-DIR-016 — No fabricated providers

The application MUST NOT display provider data invented by generative AI.

## FR-DIR-017 — Future directory sources

Additional provider-directory data sources SHALL be addable through adapters.

---

# 23. Referral Requirements

## FR-REF-001 — Offer referral

The system SHALL be able to offer a referral when the route permits it.

## FR-REF-002 — Explicit consent

A referral that shares information externally SHALL require explicit consent.

## FR-REF-003 — Minimal payload

Referral payloads SHALL contain only necessary information.

## FR-REF-004 — No raw transcript by default

Full chat transcripts MUST NOT be transmitted by default.

## FR-REF-005 — Offered status

Referral lifecycle SHALL support `OFFERED`.

## FR-REF-006 — Consented status

Referral lifecycle SHALL support `CONSENTED`.

## FR-REF-007 — Sent status

Referral lifecycle SHALL support `SENT`.

## FR-REF-008 — Acknowledged status

Referral lifecycle SHOULD support `ACKNOWLEDGED`.

## FR-REF-009 — Scheduled status

Referral lifecycle SHOULD support `SCHEDULED`.

## FR-REF-010 — Completed status

Referral lifecycle SHOULD support `COMPLETED`.

## FR-REF-011 — Negative statuses

Referral lifecycle SHOULD support `DECLINED`, `UNREACHABLE` and `EXPIRED` where relevant.

## FR-REF-012 — Status visibility

The user SHOULD be able to see applicable referral status.

## FR-REF-013 — Integration adapters

Appointment/referral destinations SHALL be integration-adapter based.

---

# 24. Clinician Dashboard Requirements

## FR-CLIN-001 — Patient queue

Authorized clinicians SHALL be able to view relevant assigned/available encounters.

## FR-CLIN-002 — Summary view

The clinician SHALL see the structured encounter summary.

## FR-CLIN-003 — Longitudinal timeline

The clinician SHOULD see the longitudinal patient timeline where consent/authorization permits.

## FR-CLIN-004 — Medication/allergy visibility

Medication and allergy information SHALL be prominently accessible.

## FR-CLIN-005 — Safety indicators

Relevant safety flags SHALL be clearly separated from confirmed diagnoses.

## FR-CLIN-006 — Risk outputs

Predictive risk outputs SHALL be visually distinguished from confirmed clinical information.

## FR-CLIN-007 — Provenance

The clinician SHOULD be able to inspect provenance of AI-extracted facts.

## FR-CLIN-008 — Edit

The clinician SHALL be able to correct relevant extracted information.

## FR-CLIN-009 — Confirm

The clinician SHALL be able to confirm relevant data.

## FR-CLIN-010 — Reject

The clinician SHALL be able to reject inaccurate extracted data.

## FR-CLIN-011 — Source document

The clinician SHOULD be able to open a source medical document where permitted.

## FR-CLIN-012 — Referral action

Authorized clinicians MAY create/update referrals.

## FR-CLIN-013 — New feature panels

Future clinical modules SHALL be able to add dashboard panels without rewriting the entire dashboard.

---

# 25. Administrative / Governance Requirements

## FR-ADMIN-001 — Role-based access

Administrative capabilities SHALL be protected by role-based authorization.

## FR-ADMIN-002 — Provider management

Authorized users SHALL manage provider/resource records.

## FR-ADMIN-003 — Resource verification

The admin workflow SHALL support resource verification timestamps/owners.

## FR-ADMIN-004 — Resource expiry

Admins SHALL be able to mark stale/expired resources inactive.

## FR-ADMIN-005 — Self-care content management

Authorized reviewers SHALL be able to manage self-care knowledge approval state.

## FR-ADMIN-006 — Policy version visibility

Admins/reviewers SHALL be able to identify active policy versions.

## FR-ADMIN-007 — Model version visibility

Authorized users SHALL be able to identify active predictive model versions.

## FR-ADMIN-008 — Audit access

Authorized users SHALL have access to relevant audit events.

## FR-ADMIN-009 — Feature flags

Authorized users MAY manage approved feature flags.

## FR-ADMIN-010 — No direct unsafe edits

Safety-critical production policy changes SHOULD require an approval workflow rather than unrestricted direct edits.

---

# 26. FHIR Requirements

## FR-FHIR-001 — FHIR boundary

The platform SHALL support FHIR-compatible interoperability.

## FR-FHIR-002 — Patient mapping

Internal patient data SHALL be mappable to/from an appropriate FHIR Patient representation where applicable.

## FR-FHIR-003 — Encounter mapping

Encounter data SHALL be mappable to FHIR Encounter.

## FR-FHIR-004 — Observation mapping

Supported lab/vital data SHALL be mappable to FHIR Observation.

## FR-FHIR-005 — Allergy mapping

Allergy data SHALL be mappable to FHIR AllergyIntolerance.

## FR-FHIR-006 — Medication mapping

Medication data SHALL support appropriate FHIR medication-related mapping.

## FR-FHIR-007 — Diagnostic report mapping

Supported reports SHALL be mappable to FHIR DiagnosticReport.

## FR-FHIR-008 — Document reference mapping

Uploaded medical documents SHALL be mappable to FHIR DocumentReference where appropriate.

## FR-FHIR-009 — Consent mapping

Consent SHALL support interoperability mapping where required.

## FR-FHIR-010 — Validation

FHIR export/import SHALL undergo schema/profile validation as applicable.

## FR-FHIR-011 — Adapter isolation

FHIR infrastructure/vendor choice SHALL remain isolated from core domain logic.

---

# 27. ABDM / ABHA Requirements

## FR-ABDM-001 — Adapter boundary

ABDM integration SHALL be isolated behind an integration layer.

## FR-ABDM-002 — ABHA-enabled workflows

The product SHALL support ABHA-related flows when enabled and technically available.

## FR-ABDM-003 — Consent-aware exchange

ABDM data exchange SHALL respect applicable consent.

## FR-ABDM-004 — Sandbox environment

Development SHALL support ABDM sandbox/test workflows before production integration.

## FR-ABDM-005 — Error isolation

ABDM failure SHALL not destroy locally valid patient intake data.

## FR-ABDM-006 — Import provenance

Imported records SHALL retain source metadata.

## FR-ABDM-007 — Configuration

ABDM integration SHALL be feature/configuration controlled.

---

# 28. Classical ML Requirements

## FR-ML-001 — Research workspace

The platform SHALL include an isolated research workflow for classical disease-risk modelling.

## FR-ML-002 — Dataset ingestion

Researchers SHALL be able to ingest approved benchmark/open biomedical datasets.

## FR-ML-003 — Data validation

Datasets SHALL undergo schema/data-quality validation.

## FR-ML-004 — Missing data

The pipeline SHALL support explicit missing-data handling.

## FR-ML-005 — Normalization

The pipeline SHALL support feature normalization/scaling where appropriate.

## FR-ML-006 — Feature engineering

The pipeline SHALL support reproducible feature engineering.

## FR-ML-007 — Feature selection

The pipeline SHALL support feature selection/dimensionality reduction.

## FR-ML-008 — Train/validation/test discipline

Evaluation SHALL use explicit split methodology and leakage safeguards.

## FR-ML-009 — Baselines

The system SHALL support multiple classical baseline models.

## FR-ML-010 — Sensitivity

Evaluation SHALL report sensitivity/recall where clinically relevant.

## FR-ML-011 — Specificity

Evaluation SHALL report specificity where clinically relevant.

## FR-ML-012 — Discrimination metrics

Appropriate discrimination metrics such as AUROC/AUPRC SHALL be supported.

## FR-ML-013 — Calibration

Risk models SHOULD be evaluated for calibration.

## FR-ML-014 — Explainability

Approved model types SHALL provide suitable explainability outputs where possible.

## FR-ML-015 — Model registry

Trained models SHALL be versioned/registered.

## FR-ML-016 — Model cards

Promoted models SHALL include documented purpose, dataset, metrics and limitations.

## FR-ML-017 — Production isolation

Research models MUST NOT automatically become production decision models.

---

# 29. Quantum ML Requirements

## FR-QML-001 — Hybrid architecture

The research platform SHALL support hybrid quantum-classical workflows.

## FR-QML-002 — Quantum feature encoding

The QML pipeline SHALL support one or more documented feature-encoding strategies.

## FR-QML-003 — VQC

The platform SHOULD support a Variational Quantum Classifier implementation.

## FR-QML-004 — QNN

The platform MAY support a Quantum Neural Network implementation.

## FR-QML-005 — QSVM

The platform MAY support a Quantum SVM or quantum-kernel approach.

## FR-QML-006 — Simulator

QML experiments SHALL support simulator execution.

## FR-QML-007 — Hardware adapter

The design SHOULD permit later near-term quantum-hardware execution through an adapter.

## FR-QML-008 — Classical preprocessing

The hybrid pipeline SHALL support classical preprocessing/feature reduction before quantum encoding.

## FR-QML-009 — Training workflow

The platform SHALL support reproducible hybrid training.

## FR-QML-010 — Inference workflow

The platform SHALL support reproducible QML inference.

## FR-QML-011 — Benchmark parity

Classical and QML candidates SHALL be compared on the same evaluation split and target definition.

## FR-QML-012 — Performance comparison

The platform SHALL compare predictive performance.

## FR-QML-013 — Efficiency comparison

The platform SHOULD record relevant computational/circuit resource metrics.

## FR-QML-014 — Generalization comparison

The platform SHALL compare held-out generalization.

## FR-QML-015 — Explainability metadata

The platform SHALL expose available explanation/model metadata.

## FR-QML-016 — Quantum configuration provenance

Quantum backend, shot count, circuit depth and key experiment configuration SHOULD be recorded.

## FR-QML-017 — No automatic quantum superiority claim

The product MUST NOT claim quantum advantage unless benchmark evidence supports it.

## FR-QML-018 — No safety override

QML output MUST NOT override deterministic urgent-safety policy.

---

# 30. RAG / Knowledge Requirements

## FR-RAG-001 — Approved use

RAG MAY be used where retrieval from an approved corpus materially improves correctness.

## FR-RAG-002 — Patient-document retrieval

RAG MAY retrieve relevant patient-document/history context within authorization boundaries.

## FR-RAG-003 — Self-care retrieval

Self-care explanations MAY retrieve from approved guidance content.

## FR-RAG-004 — Resource retrieval

Resource discovery MAY query verified structured resources.

## FR-RAG-005 — No crisis routing authority

RAG MUST NOT determine final crisis routing.

## FR-RAG-006 — No rule replacement

RAG MUST NOT replace deterministic contraindication/safety rules.

## FR-RAG-007 — Citation/provenance

Patient-facing or clinician-facing retrieved content SHOULD retain source provenance where appropriate.

---

# 31. Notification and Follow-Up Requirements

## FR-NOTIF-001 — Referral status

The system SHOULD notify users of relevant referral-status changes when consent/identity allow it.

## FR-NOTIF-002 — Follow-up reminders

The system MAY provide follow-up reminders after a referral, investigation or discharge.

## FR-NOTIF-003 — Medication reminders

The system MAY support medication-adherence reminders without changing medication instructions.

## FR-NOTIF-004 — User preference

Notification channel/preferences SHALL be user-configurable where applicable.

## FR-NOTIF-005 — No sensitive leakage

Notifications MUST avoid exposing unnecessary sensitive health information on lock screens or insecure channels.

## FR-NOTIF-006 — Provider abstraction

Notification delivery SHOULD use a replaceable provider abstraction.

---

# 32. Audit Requirements

## FR-AUDIT-001 — Policy changes

Safety/policy changes SHALL be auditable.

## FR-AUDIT-002 — Resource changes

Provider/resource changes SHALL be auditable.

## FR-AUDIT-003 — Consent changes

Consent changes SHALL be auditable.

## FR-AUDIT-004 — Admin actions

Sensitive administrative actions SHALL be auditable.

## FR-AUDIT-005 — Clinician corrections

Clinician corrections to AI-extracted clinical information SHOULD be auditable.

## FR-AUDIT-006 — Model promotion

Model promotion/release SHALL be auditable.

## FR-AUDIT-007 — No raw transcript requirement

Auditability MUST NOT require indiscriminate storage of raw sensitive conversations.

---

# 33. Accessibility Requirements

## NFR-ACCESS-001

Patient-facing web surfaces SHOULD target WCAG 2.2 AA.

## NFR-ACCESS-002

The application SHALL support keyboard navigation for core workflows.

## NFR-ACCESS-003

Core controls SHALL have screen-reader labels.

## NFR-ACCESS-004

The application SHALL provide readable high-contrast presentation.

## NFR-ACCESS-005

Kiosk mode SHOULD support large touch targets.

## NFR-ACCESS-006

Audio-guided interaction SHOULD be available for configured workflows.

## NFR-ACCESS-007

Critical emergency/crisis controls SHALL remain visually prominent.

---

# 34. Performance Requirements

Initial targets are pilot-oriented and may be refined later.

## NFR-PERF-001

Core non-model API endpoints SHOULD target predictable low-latency operation under expected pilot load.

## NFR-PERF-002

Conversational response latency SHOULD target acceptable interactive performance.

## NFR-PERF-003

Safety-critical local/backstop actions SHOULD not wait for normal LLM round trips when avoidable.

## NFR-PERF-004

Large document processing MAY be asynchronous.

## NFR-PERF-005

Predictive research jobs MAY be asynchronous.

## NFR-PERF-006

Performance targets SHALL be measurable through observability.

---

# 35. Availability and Resilience Requirements

## NFR-RES-001

Core intake and safety functions SHOULD remain usable during failure of optional research modules.

## NFR-RES-002

Mental-health crisis fallback SHALL remain available during generative-model outage.

## NFR-RES-003

Text/touch intake SHALL remain available when voice processing fails.

## NFR-RES-004

Manual entry SHALL remain possible when OCR fails.

## NFR-RES-005

The product SHALL expose honest failure/degraded states rather than falsely indicating successful assessment.

## NFR-RES-006

Critical external integrations SHOULD define timeouts and bounded retries.

## NFR-RES-007

Independent kill switches SHOULD exist for sufficiently risky optional integrations/policies.

---

# 36. Security Requirements

## NFR-SEC-001

All production network traffic SHALL use TLS.

## NFR-SEC-002

Sensitive data SHALL be encrypted at rest using appropriate platform controls.

## NFR-SEC-003

Administrative accounts SHALL require MFA.

## NFR-SEC-004

Authorization SHALL use least-privilege RBAC or equivalent.

## NFR-SEC-005

Secrets SHALL NOT be committed to source control.

## NFR-SEC-006

Uploaded files SHALL undergo security validation.

## NFR-SEC-007

Patient/user-generated content SHALL be safely rendered to prevent XSS.

## NFR-SEC-008

The application SHALL implement rate limiting for abuse-prone endpoints.

## NFR-SEC-009

Session tokens SHALL be high entropy and appropriately protected.

## NFR-SEC-010

Dependencies SHALL be scanned for known vulnerabilities.

## NFR-SEC-011

Production container images SHOULD be scanned.

## NFR-SEC-012

LLM prompt injection SHALL NOT be able to bypass deterministic policy.

## NFR-SEC-013

External AI providers SHALL receive the minimum context required for the operation.

## NFR-SEC-014

Sensitive request/response bodies SHALL not be logged by default.

---

# 37. Privacy Requirements

## PRIV-001 — Data minimization

Only data required for the active purpose SHOULD be collected.

## PRIV-002 — Purpose limitation

Data SHALL be used according to documented purposes and consent/governance.

## PRIV-003 — Retention

Sensitive transient data SHALL have explicit retention rules.

## PRIV-004 — Deletion

Applicable deletion/withdrawal workflows SHALL be supported.

## PRIV-005 — Minimal referral payload

Referral sharing SHALL use a minimized payload.

## PRIV-006 — Pseudonymous mental-health mode

Anonymous-feeling mental-health first-contact mode SHALL avoid intentional collection of unnecessary identity.

## PRIV-007 — Sensitive logs

Operational logs SHALL exclude raw sensitive content by default.

## PRIV-008 — Research separation

Research datasets/workspaces SHALL be separated from normal production patient data access.

## PRIV-009 — Institutional analytics

Institutional aggregate analytics SHOULD avoid exposing identifiable individual mental-health conversations.

---

# 38. Observability Requirements

## NFR-OBS-001

The platform SHALL emit request/error metrics.

## NFR-OBS-002

LLM failures SHALL be measurable by provider/model/schema.

## NFR-OBS-003

OCR failures SHALL be measurable.

## NFR-OBS-004

Route decisions SHALL be measurable in aggregate.

## NFR-OBS-005

Clarification frequency SHOULD be measurable.

## NFR-OBS-006

Crisis fallback activation SHALL be measurable.

## NFR-OBS-007

Stale provider/resource counts SHALL be measurable.

## NFR-OBS-008

Referral lifecycle counts SHALL be measurable.

## NFR-OBS-009

Data-purge failures SHALL be measurable.

## NFR-OBS-010

Model latency/errors SHALL be measurable.

## NFR-OBS-011

Observability SHALL avoid raw sensitive text whenever possible.

---

# 39. Maintainability Requirements

## NFR-MAINT-001

Python SHALL use static typing for public/domain interfaces.

## NFR-MAINT-002

TypeScript SHALL run in strict mode.

## NFR-MAINT-003

Business logic SHOULD NOT live directly inside transport route handlers.

## NFR-MAINT-004

Database schema changes SHALL use migrations.

## NFR-MAINT-005

External technologies SHALL be isolated behind adapters where reasonable.

## NFR-MAINT-006

Safety-critical deterministic logic SHALL have high branch-test coverage.

## NFR-MAINT-007

Module boundaries SHALL be enforceable through repository structure and tests/linting where practical.

## NFR-MAINT-008

Documentation SHALL be updated when public behavior/contracts change.

---

# 40. Testing Requirements

## NFR-TEST-001

Every implementation phase SHALL add or update tests appropriate to the feature.

## NFR-TEST-002

Core domain logic SHALL have unit tests.

## NFR-TEST-003

Database integrations SHALL have integration tests.

## NFR-TEST-004

Public APIs SHALL have contract tests.

## NFR-TEST-005

Critical patient journeys SHALL have E2E tests.

## NFR-TEST-006

Safety rules SHALL have dedicated regression fixtures.

## NFR-TEST-007

Mental-health safety evaluation SHALL include clinician-authored/adversarial cases before production use.

## NFR-TEST-008

Multilingual safety behavior SHALL be tested by supported language.

## NFR-TEST-009

LLM structured extraction SHALL be tested for invalid/missing output.

## NFR-TEST-010

Prompt injection SHALL be included in safety/security tests.

## NFR-TEST-011

OCR SHALL be tested against representative fixtures.

## NFR-TEST-012

FHIR mappings SHALL have validation/round-trip tests where appropriate.

## NFR-TEST-013

ML/QML evaluation SHALL be reproducible.

## NFR-TEST-014

New safety defects SHALL produce regression cases before closure.

---

# 41. Research Governance Requirements

## NFR-RESRCH-001

Human-participant research/pilots SHALL obtain required institutional/ethics review before execution.

## NFR-RESRCH-002

Pilot evaluation criteria SHOULD be predefined.

## NFR-RESRCH-003

Held-out safety evaluation data MUST NOT be used as training data for the same release-gating evaluation.

## NFR-RESRCH-004

Research claims SHALL reflect measured results and limitations.

## NFR-RESRCH-005

Production release SHALL not be justified solely by chatbot fluency or model demo quality.

---

# 42. Model Governance Requirements

## NFR-MODEL-001

Every promoted model SHALL have a unique version.

## NFR-MODEL-002

Model training data provenance SHALL be documented.

## NFR-MODEL-003

Model metrics SHALL be stored.

## NFR-MODEL-004

Model limitations SHALL be documented.

## NFR-MODEL-005

Production thresholds SHALL be versioned.

## NFR-MODEL-006

A model change that affects patient routing SHALL require clinical/safety review.

## NFR-MODEL-007

The platform SHOULD allow model-provider replacement without rewriting routing logic.

---

# 43. User Experience Requirements

## NFR-UX-001

Patient-facing language SHALL be understandable and avoid unnecessary clinical jargon.

## NFR-UX-002

The product SHOULD not overwhelm patients with large multi-question forms when a conversational flow is more suitable.

## NFR-UX-003

Sensitive questions SHOULD be presented one at a time.

## NFR-UX-004

The system SHALL clearly state when it lacks enough information.

## NFR-UX-005

The system SHALL not present probabilistic model confidence as clinical certainty.

## NFR-UX-006

Urgent actions SHALL be visually distinct from routine actions.

## NFR-UX-007

The clinician interface SHALL prioritize information required during consultation.

## NFR-UX-008

Feature-specific interfaces SHALL reuse shared design-system primitives.

---

# 44. Future Feature Integration Requirements

This section ensures the project can continue growing.

## FR-EXT-100 — Feature proposal

Every substantial new feature SHALL begin with a short feature proposal containing:
- user problem;
- target user;
- intended outcome;
- safety category;
- dependencies;
- likely module owner.

## FR-EXT-101 — Requirement IDs

Approved new features SHALL receive new requirement IDs rather than being implemented only from an ad-hoc prompt.

## FR-EXT-102 — Dependency mapping

A future feature SHALL document which existing capabilities it consumes.

## FR-EXT-103 — Data ownership

A future feature SHALL document which new data it owns.

## FR-EXT-104 — Event contracts

If event-driven behavior is used, the feature SHALL define event schemas.

## FR-EXT-105 — Permission model

A future feature SHALL define required permissions/roles.

## FR-EXT-106 — Failure behavior

A future feature SHALL define degraded/failure behavior.

## FR-EXT-107 — Feature flag

High-risk, experimental or staged features SHOULD be feature-flagged.

## FR-EXT-108 — Rollback

A future feature SHALL define how it can be disabled or rolled back.

## FR-EXT-109 — Observability

A future feature SHALL define at least basic health/error metrics.

## FR-EXT-110 — Tests

A future feature SHALL define required unit/integration/E2E/safety tests.

## FR-EXT-111 — Documentation

A future feature SHALL update applicable architecture/product/API/domain documentation.

## FR-EXT-112 — No accidental platform coupling

A new feature MUST NOT force unrelated modules to import its internal implementation.

---

# 45. Example Future Capabilities

The architecture SHOULD permit adding capabilities such as:

- wearable health data;
- remote vitals;
- nutrition;
- medication adherence;
- teleconsultation;
- pharmacy integration;
- insurance workflow;
- maternal-health modules;
- child-health modules;
- elder-care modules;
- chronic disease management;
- image-based diagnostic decision support;
- rehabilitation;
- physiotherapy;
- lab booking;
- ambulance/emergency resource discovery;
- caregiver collaboration;
- regional-language expansion;
- federated/privacy-preserving analytics;
- additional ML/QML disease tasks.

These are examples, not committed scope.

---

# 46. Release Scope Model

Each requirement will later be tagged as one of:

- `FOUNDATION`
- `MVP`
- `PILOT`
- `POST-PILOT`
- `RESEARCH`
- `FUTURE`

The Master Implementation Plan will assign these tags and phases.

Until that document exists, inclusion in this PRD does not imply that all requirements are implemented in the first build phase.

---

# 47. Requirement Acceptance Format

Detailed acceptance criteria will live in phase/module specifications.

The standard format will be:

```text
Requirement:
FR-XXXX-000

Given:
<precondition>

When:
<user/system action>

Then:
<observable result>

And:
<safety/security/error conditions>
```

---

# 48. Initial Product-Level Acceptance Outcomes

A coherent end-to-end SwasthyaSetu implementation is expected to eventually demonstrate the following.

## AC-PROD-001 — Clinical intake journey

A patient can begin an encounter, provide symptoms, answer adaptive follow-up questions and generate a structured draft history.

## AC-PROD-002 — Document journey

A patient can upload a supported medical document, receive structured extracted data with provenance, and see it incorporated into a timeline after appropriate confirmation.

## AC-PROD-003 — Safety journey

A configured physical-health red flag prevents self-care and produces the governed urgent route.

## AC-PROD-004 — Mental-health journey

A pseudonymous Hindi/English/Hinglish mental-health conversation produces structured signals, while deterministic policy determines the route.

## AC-PROD-005 — Crisis fallback

A crisis-resource path remains available even when the normal LLM path is unavailable.

## AC-PROD-006 — Self-care journey

A low-risk eligible context retrieves approved self-care guidance and displays escalation conditions.

## AC-PROD-007 — Self-care block

A contraindication or red flag blocks self-care output.

## AC-PROD-008 — Provider journey

The patient receives appropriate verified provider/service options without LLM-fabricated contact details.

## AC-PROD-009 — Referral journey

The user can explicitly consent to a minimal referral and track its status.

## AC-PROD-010 — Clinician journey

A clinician can review the summary, see source/provenance, and correct/confirm extracted data.

## AC-PROD-011 — Interoperability journey

Selected structured data can be transformed into validated FHIR-compatible resources.

## AC-PROD-012 — Classical ML journey

A benchmark dataset can be preprocessed, trained on classical baselines and evaluated reproducibly.

## AC-PROD-013 — QML journey

The same task can be evaluated using at least one hybrid QML approach and compared fairly against classical baselines.

## AC-PROD-014 — Extensibility journey

A sample new feature module can be added using documented extension contracts without modifying unrelated core modules.

---

# 49. Requirement Change Control

Requirement changes SHALL follow these rules:

1. do not silently delete requirement IDs;
2. mark deprecated requirements explicitly;
3. create a new ID when semantic meaning materially changes;
4. update source traceability;
5. update impacted architecture/API/domain documentation;
6. identify migration implications;
7. identify test implications;
8. identify safety/privacy implications.

---

# 50. Open Product Questions

The following decisions are intentionally deferred to later specifications and should not be guessed by Codex:

1. exact authenticated identity mechanism;
2. exact ABHA onboarding/integration flows;
3. final medical terminology coding strategy;
4. final provider-directory source(s);
5. final initial self-care dataset(s);
6. final approved Ayurveda knowledge source(s);
7. final disease task(s) used for ML/QML demo;
8. exact production LLM provider;
9. exact ASR/TTS implementation per supported language;
10. exact hosting/cloud provider;
11. exact object-storage implementation;
12. final retention policy by deployment;
13. final clinical red-flag content;
14. final mental-health route thresholds;
15. exact named screening instruments, if any;
16. final legal/compliance interpretation at production launch.

Codex MUST NOT invent these as authoritative product decisions.

---

# 51. Requirements That Need Clinical Sign-Off Before Real Deployment

At minimum:

- physical red-flag policy;
- mental-health safety/route policy;
- crisis wording;
- self-care eligibility;
- Ayurveda/gharelu guidance;
- contraindications;
- medication conflict rules;
- specialty routing rules where clinically consequential;
- predictive-model thresholds that affect care actions;
- patient-facing interpretation of disease risk;
- named clinical-screening questionnaires.

---

# 52. Requirements That Need Privacy/Security Review

At minimum:

- identity design;
- anonymous/pseudonymous mode;
- LLM data flow;
- document storage;
- patient history retention;
- ABDM integration;
- referral payloads;
- provider integrations;
- notification content;
- admin access;
- research dataset use;
- analytics;
- logs/observability;
- backups and deletion.

---

# 53. Requirements That Need Research Validation

At minimum:

- ML predictive performance;
- QML performance;
- QML/classical comparison;
- multilingual extractor performance;
- mental-health route concordance;
- crisis sensitivity;
- OCR medical-entity extraction quality;
- clinician time-saved claims;
- usability/adoption claims.

---

# 54. Codex Usage Rule

Implementation prompts SHALL cite relevant requirement IDs.

Example:

```text
Implement FR-IDENT-001 through FR-IDENT-007.

Do not implement clinical intake or mental-health policy yet.

Preserve SAFE-001 through SAFE-010.

Validate against NFR-SEC-001 through NFR-SEC-014 where applicable.
```

This prevents implementation prompts from becoming vague or scope-creeping.

---

# 55. PRD Completion Status

This PRD defines the broad product requirements.

It intentionally does **not** yet freeze:

- exact service boundaries;
- repository folders;
- database schema;
- API payloads;
- event payloads;
- framework-specific design patterns;
- implementation phases.

Those decisions will be defined next.

---

# 56. Next Required Foundation Documents

The next documents to create are:

1. `02_SYSTEM_ARCHITECTURE.md`
2. `29_ENGINEERING_STANDARDS.md`
3. `34_MASTER_IMPLEMENTATION_PLAN.md`

Then:

4. `03_REPOSITORY_STRUCTURE.md`
5. `04_DOMAIN_MODEL.md`
6. `05_DATABASE_SCHEMA.md`
7. `06_API_CONTRACTS.md`

---

# 57. Product Principle Summary

SwasthyaSetu AI should remain:

```text
Patient-centered
Safety-first
Multilingual
Modular
Extensible
Explainable
Human-governed
Interoperable
Privacy-aware
Evidence-driven
Replaceable at integration boundaries
Testable at every decision boundary
```

The product requirements are intentionally written so the platform can gain new features over time without turning the codebase into one tightly coupled healthcare application.
