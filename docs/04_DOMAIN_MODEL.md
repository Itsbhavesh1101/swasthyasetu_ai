# SwasthyaSetu AI
## 04 — Domain Model Specification

**Document ID:** `SSAI-DOM-004`  
**Filename:** `04_DOMAIN_MODEL.md`  
**Status:** Foundation / Canonical Domain Source of Truth  
**Version:** `1.0.0-draft`  
**Depends on:** `00_PROJECT_MASTER_SPEC.md`, `01_PRODUCT_REQUIREMENTS.md`, `02_SYSTEM_ARCHITECTURE.md`, `03_REPOSITORY_STRUCTURE.md`, `29_ENGINEERING_STANDARDS.md`, `34_MASTER_IMPLEMENTATION_PLAN.md`

---

# 1. Purpose

This document defines the canonical business/domain concepts used across SwasthyaSetu AI so that modules do not invent conflicting representations of patients, encounters, clinical facts, medications, allergies, observations, documents, safety decisions, mental-health signals, self-care guidance, providers/resources, referrals, consent, model risk assessments, and provenance.

This document defines meaning and ownership, not ORM tables. Persistence is defined in `05_DATABASE_SCHEMA.md`; HTTP contracts are defined in `06_API_CONTRACTS.md`.

---

# 2. Modeling Principles

- **DOM-P-001 — Shared longitudinal context:** modules consume one canonical patient context.
- **DOM-P-002 — Provenance:** clinically meaningful facts retain source information where known.
- **DOM-P-003 — Extracted is not confirmed:** AI/OCR/model-derived data remains distinguishable from clinician-confirmed data.
- **DOM-P-004 — Decision support is not diagnosis:** safety/risk outputs are separate from confirmed diagnoses.
- **DOM-P-005 — Explicit ownership:** each aggregate has one owning bounded context.
- **DOM-P-006 — Interoperability mapping:** FHIR/ABDM representations do not replace the internal model.
- **DOM-P-007 — Extensibility:** future modules extend through typed entities/capabilities, not a giant patient JSON object.

---

# 3. Core IDs

Opaque UUID-backed identifiers:

```text
PatientId
EncounterId
SessionId
DocumentId
ClinicalFactId
ProviderId
ResourceId
ReferralId
ConsentId
DecisionId
ModelId
ExperimentRunId
```

External identifiers are stored separately with source namespace.

---

# 4. Actor

`Actor` represents the current operating principal.

Fields:

```text
actor_id
actor_type
roles[]
subject_id?
institution_id?
status
created_at
updated_at
```

Actor types may include:

```text
PATIENT
PSEUDONYMOUS_USER
CAREGIVER
CLINICIAN
COUNSELLOR
TRIAGE_STAFF
RESOURCE_ADMIN
CLINICAL_REVIEWER
SYSTEM_ADMIN
RESEARCHER
SERVICE_ACCOUNT
```

Lifecycle status:

```text
ACTIVE
DISABLED
```

Rules:

- actor != patient;
- actor type != role code;
- role code != permission code;
- actor type never grants a role or permission;
- caregiver does not inherit patient permission automatically;
- pseudonymous actor may have no direct identity;
- disabled actors cannot resolve to an authenticated current actor.

Owner: `identity`.

---

# 5. Session Aggregate

`Session`

```text
session_id
session_type
subject_ref?
language_preference?
created_at
expires_at
closed_at?
status
recovery_token_hash?
```

Session types:

```text
PSEUDONYMOUS
AUTHENTICATED
KIOSK
CLINICIAN
ADMIN
RESEARCH
```

Statuses:

```text
ACTIVE
EXPIRED
CLOSED
REVOKED
```

Owner: `sessions`.

---

# 6. Consent Aggregate

`ConsentRecord`

```text
consent_id
subject_ref
actor_ref
purpose
scope[]
notice_version
granted_at
revoked_at?
expires_at?
status
metadata?
```

Possible purposes:

```text
GENERAL_PRODUCT_USE
EXTERNAL_AI_PROCESSING
REFERRAL_SHARING
ABDM_EXCHANGE
RESEARCH_USE
CAREGIVER_ACCESS
```

Statuses:

```text
GRANTED
REVOKED
EXPIRED
SUPERSEDED
```

Rules:

- consent is purpose-specific;
- referral consent is not implied by general product consent;
- revocation must be representable.

Owner: `consent`.

---

# 7. Patient Aggregate

`Patient`

```text
patient_id
status
created_at
updated_at
preferred_language?
demographics?
identifiers[]
```

Patient status:

```text
ACTIVE
INACTIVE
MERGED
DELETED_PENDING
```

The patient aggregate is not a giant container for every future feature.

Owner: `patients`.

---

# 8. Patient Identifier

`PatientIdentifier`

```text
identifier_id
patient_id
system
value
use?
verified
source
```

Examples of `system`:

```text
internal
hospital_mrn
abha
external_his
```

ABHA linkage remains optional and integration-driven.

---

# 9. Demographics

`PatientDemographics`

Possible fields:

```text
date_of_birth?
age_years?
administrative_sex?
gender_identity?
pregnancy_status?
location_context?
```

Rules:

- collect only what the workflow requires;
- missing/unknown values must be explicit;
- pregnancy status must never be inferred automatically from sex.

---

# 10. Encounter Aggregate

`Encounter`

```text
encounter_id
patient_id?
session_id
encounter_type
status
started_at
completed_at?
institution_id?
language_context?
created_by
```

Encounter types:

```text
GENERAL_INTAKE
MENTAL_HEALTH
KIOSK_INTAKE
CLINICIAN_REVIEW
DOCUMENT_REVIEW
RESEARCH_ONLY
```

Statuses:

```text
CREATED
IN_PROGRESS
AWAITING_REVIEW
COMPLETED
ABANDONED
CANCELLED
```

Rules:

- incomplete != completed;
- encounter may exist for pseudonymous session without patient linkage.

Owner: `encounters`.

---

# 11. Clinical Fact

`ClinicalFact` is a normalized clinically meaningful proposition.

```text
fact_id
patient_id?
encounter_id?
fact_type
value
normalized_code?
coding_system?
effective_time?
recorded_at
verification_state
provenance
```

Fact types may include:

```text
SYMPTOM
PROBLEM
MEDICATION
ALLERGY
PROCEDURE
OBSERVATION
INVESTIGATION
FAMILY_HISTORY
PERSONAL_HISTORY
REVIEW_OF_SYSTEMS
```

Rules:

- a risk assessment is not a confirmed problem;
- a safety route is not a diagnosis;
- source wording may be preserved separately.

---

# 12. Verification State

Canonical values:

```text
EXTRACTED
LOW_CONFIDENCE
NEEDS_CONFIRMATION
PATIENT_CONFIRMED
CLINICIAN_CONFIRMED
REJECTED
SUPERSEDED
```

A clinician-confirmed value must not be silently overwritten by a lower-trust extracted value.

---

# 13. Fact Provenance

`FactProvenance`

```text
source_type
source_id?
source_ref?
extractor_type?
provider?
model_id?
model_version?
prompt_version?
schema_version?
confidence?
created_at
created_by?
```

Source types:

```text
PATIENT_REPORT
CAREGIVER_REPORT
CLINICIAN
OCR
DOCUMENT_AI
FHIR_IMPORT
ABDM_IMPORT
HIS_IMPORT
MODEL_INFERENCE
ADMIN
SYSTEM
```

Confidence is not clinical certainty.

---

# 14. Symptom

`Symptom`

```text
name
normalized_code?
onset?
duration?
location?
character?
severity?
progression?
associated_symptoms[]
aggravating_factors[]
relieving_factors[]
source_text?
```

Symptoms remain separate from diagnoses.

---

# 15. Problem

`Problem`

```text
label
normalized_code?
status
onset?
resolution?
verification_state
```

Statuses:

```text
ACTIVE
HISTORICAL
RESOLVED
UNKNOWN
```

Predictive output must not automatically create a clinician-confirmed Problem.

---

# 16. Medication Record

`MedicationRecord`

```text
name
normalized_code?
dose?
dose_unit?
route?
frequency?
start_date?
end_date?
status
indication?
verification_state
```

Status:

```text
ACTIVE
HISTORICAL
STOPPED
UNKNOWN
```

Prescription OCR produces candidate medication information only.

---

# 17. Allergy Record

`AllergyRecord`

```text
substance
normalized_code?
reaction?
severity?
status
verification_state
```

Where source supports it, allergy and side effect should remain distinct.

---

# 18. Procedure Record

`ProcedureRecord`

```text
name
normalized_code?
performed_at?
facility?
notes?
verification_state
```

---

# 19. Observation

`Observation`

```text
observation_type
value
unit?
reference_range?
effective_at?
normalized_value?
normalized_unit?
abnormal_flag?
verification_state
```

Rules:

- numeric interpretation must be unit-aware;
- out-of-range does not equal diagnosis.

---

# 20. Investigation Record

`InvestigationRecord`

```text
investigation_type
performed_at?
result_summary?
document_id?
status
verification_state
```

---

# 21. Family History

`FamilyHistoryItem`

```text
relation?
condition_label
normalized_code?
notes?
verification_state
```

---

# 22. Personal History

`PersonalHistoryItem` may represent:

```text
sleep
diet
substance_use
occupation
activity
other governed categories
```

Use typed category-specific values rather than an unrestricted miscellaneous bucket where practical.

---

# 23. Review of Systems

`ROSItem`

```text
system
finding
status
source_text?
verification_state
```

Possible status:

```text
POSITIVE
NEGATIVE
UNKNOWN
NOT_ASKED
```

---

# 24. Clinical Intake Aggregate

`ClinicalIntake`

```text
intake_id
encounter_id
status
chief_complaint
hpi
history_sections
questionnaire_instances[]
missing_information[]
contradictions[]
started_at
completed_at?
```

Statuses:

```text
DRAFT
IN_PROGRESS
READY_FOR_REVIEW
COMPLETED
ABANDONED
```

Owner: `clinical_intake`.

---

# 25. History of Present Illness

`HistoryOfPresentIllness`

```text
presenting_symptoms[]
onset?
duration?
location?
character?
severity?
progression?
associated_symptoms[]
aggravating_factors[]
relieving_factors[]
narrative_source?
```

---

# 26. Question Definition

`QuestionDefinition`

```text
question_id
version
domain
prompt_key
answer_type
required_when?
visibility_rule?
clinical_owner?
```

Question packs enable future specialty modules.

---

# 27. Questionnaire Instance

`QuestionnaireInstance`

```text
instance_id
questionnaire_id
version
encounter_id
responses[]
status
started_at
completed_at?
```

A questionnaire score does not automatically become final safety routing unless explicitly governed.

---

# 28. AYUSH Intake Extension

`AyushIntakeProfile`

Possible governed fields:

```text
prakriti
vikriti
agni
koshtha
ahara_vihara
nidana
samprapti
dashavidha_pariksha_fields
```

Rules:

- optional;
- workflow-specific;
- definitions/content come from approved spec;
- not mandatory for every patient.

---

# 29. Physical Safety Signals

`PhysicalSafetySignals` is the typed input to the physical safety engine.

Conceptual inputs may include:

```text
symptoms[]
vital_signals?
duration?
severity?
age_context?
pregnancy_context?
known_conditions[]
medications[]
allergies[]
missing_critical_information[]
```

Exact trigger fields belong in the safety policy specification.

---

# 30. Safety Decision

`SafetyDecision`

```text
decision_id
encounter_id
route
reason_codes[]
policy_id
policy_version
requires_clarification
blocks_self_care
created_at
input_snapshot_ref?
```

Routes:

```text
EMERGENCY
PRIORITY_REVIEW
ROUTINE_CARE
SUPPORTED_SELF_CARE
CLARIFICATION_REQUIRED
```

Rules:

- deterministic;
- policy version mandatory;
- no diagnosis field.

Owner: `safety`.

---

# 31. Mental-Health Signals

`MentalHealthSignals`

Conceptual fields:

```text
distress_level?
persistence?
functional_impairment?
self_harm_ideation?
plan?
intent?
means?
recent_attempt?
immediacy?
violence_or_abuse?
psychosis_or_mania?
disorientation?
protective_factors[]
support_factors[]
uncertainties[]
contradictions[]
```

Exact schema belongs in the mental-health and LLM extraction specs.

---

# 32. Mental-Health Decision

`MentalHealthDecision`

```text
decision_id
session_id
encounter_id?
route
reason_codes[]
policy_version
signal_schema_version
created_at
requires_clarification
```

Routes:

```text
ROUTE_A
ROUTE_B
ROUTE_C
CLARIFICATION_REQUIRED
DEGRADED_SAFE_FALLBACK
```

Final route belongs to deterministic policy, not the LLM.

---

# 33. Clinical Document

`ClinicalDocument`

```text
document_id
patient_id?
encounter_id?
document_type
storage_object_ref
original_filename?
mime_type
size_bytes
checksum
status
uploaded_at
captured_at?
document_date?
language?
```

Statuses:

```text
UPLOADED
VALIDATING
ACCEPTED
QUEUED
PROCESSING
NEEDS_REVIEW
SUCCEEDED
FAILED
REJECTED
```

Owner: `documents`.

---

# 34. Document Type

Initial values:

```text
PRESCRIPTION
LAB_REPORT
DISCHARGE_SUMMARY
DIAGNOSTIC_REPORT
IMAGING_REPORT
REFERRAL_LETTER
OTHER
UNKNOWN
```

New types must be registered via processor/plugin architecture.

---

# 35. OCR Result

`OCRResult`

```text
document_id
provider
provider_version?
language?
text_blocks[]
confidence_summary?
created_at
```

OCR result is derived processing output, not confirmed clinical truth.

---

# 36. Document Extraction Result

`DocumentExtractionResult`

```text
document_id
processor_id
processor_version
candidate_facts[]
warnings[]
confidence_summary?
status
```

Candidate facts enter provenance/review workflow.

---

# 37. Clinical Summary

`ClinicalSummary`

```text
summary_id
encounter_id
version
status
sections
generated_from_fact_ids[]
created_at
created_by
confirmed_by?
confirmed_at?
```

Statuses:

```text
DRAFT
CLINICIAN_EDITED
CONFIRMED
REJECTED
SUPERSEDED
```

Sections may include chief complaint, HPI, PMH/PSH, medications/allergies, family history, personal history, ROS, and prior investigations.

Summary generation must not create new diagnosis/truth.

Owner: `summaries`.

---

# 38. Self-Care Guidance Definition

`SelfCareGuidanceDefinition`

```text
guidance_id
version
title
eligible_context
supportive_actions[]
contraindications[]
medication_conflicts[]
age_rules?
pregnancy_rules?
duration_limit?
escalation_conditions[]
source
review_status
verified_at?
expires_at?
translations?
```

Review statuses:

```text
DRAFT
UNDER_REVIEW
APPROVED
REJECTED
RETIRED
EXPIRED
```

Owner: `self_care`.

---

# 39. Self-Care Eligibility Decision

`SelfCareEligibilityDecision`

```text
decision_id
patient_id?
encounter_id
eligible
reason_codes[]
policy_version
matched_guidance_ids[]
created_at
```

Rules:

- hard safety evaluated first;
- approved knowledge only;
- contraindication/exclusion reason codes explicit.

---

# 40. Provider

`Provider`

```text
provider_id
display_name
provider_type
specialties[]
qualifications?
registration_metadata?
facility_id?
location?
languages[]
contact_methods[]
teleconsultation_available?
hours?
source
verified_at
expires_at?
status
```

Statuses:

```text
ACTIVE
STALE
EXPIRED
INACTIVE
UNVERIFIED
```

Owner: `providers`.

---

# 41. Facility

`Facility`

```text
facility_id
name
facility_type
location
contact_methods[]
hours?
source
verified_at?
status
```

---

# 42. Care Resource

`CareResource`

```text
resource_id
resource_type
display_label
contact_methods[]
geography?
languages[]
hours?
eligibility?
institution_id?
source
verified_at
expires_at?
approval_status
version
```

Examples:

```text
CRISIS_LINE
COUNSELLING_CELL
NGO_SUPPORT
PUBLIC_HEALTH_SERVICE
HOSPITAL_RESOURCE
```

Owner: `resources`.

---

# 43. Care Category

`CareCategory` represents the governed category before individual provider selection.

Examples may include:

```text
EMERGENCY_CARE
PRIMARY_CARE
GENERAL_MEDICINE
MENTAL_HEALTH_COUNSELLING
PSYCHIATRY
DERMATOLOGY
GYNECOLOGY
```

Exact taxonomy is deferred to provider-routing policy.

---

# 44. Provider Routing Decision

`ProviderRoutingDecision`

```text
decision_id
encounter_id
care_category
specialty_or_service_type
reason_codes[]
policy_version
created_at
```

It does not contain invented provider contacts.

---

# 45. Referral Aggregate

`Referral`

```text
referral_id
patient_id?
session_id?
encounter_id?
destination_type
destination_id
priority
reason_codes[]
consent_id
status
created_at
updated_at
external_reference?
```

Statuses:

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
CANCELLED
```

Owner: `referrals`.

---

# 46. Referral Payload

`ReferralPayload`

```text
referral_id
priority
reason_codes[]
language_preference?
care_category?
minimal_context?
contact_info?
consent_version
created_at
```

Rules:

- full chat transcript excluded by default;
- narrative summary requires explicit consent and governed template if later introduced.

---

# 47. Notification Intent

`NotificationIntent`

```text
notification_id
subject_ref
channel
template_id
template_version
safe_variables
status
created_at
```

Patient health detail should be minimized.

Owner: `notifications`.

---

# 48. Risk Assessment

`RiskAssessment`

```text
assessment_id
patient_id?
encounter_id?
task
model_id
model_version
input_schema_version
risk_probability?
risk_band?
calibration_version?
input_quality
explanation_ref?
created_at
```

Input quality:

```text
VALID
PARTIAL
INSUFFICIENT_INPUT
INVALID
```

Rules:

- not diagnosis;
- cannot override hard safety;
- model version required.

---

# 49. Model Registration

`ModelRegistration`

```text
model_id
model_version
task
framework
artifact_ref
input_schema_version
output_schema_version
dataset_ref
metrics
calibration_ref?
approval_status
created_at
promoted_at?
retired_at?
```

Approval states:

```text
EXPERIMENTAL
VALIDATED
APPROVED_FOR_PILOT
APPROVED_FOR_PRODUCTION
DEPRECATED
RETIRED
```

---

# 50. Experiment Run

`ExperimentRun`

```text
run_id
task
dataset_version
code_version
parameters
seed?
metrics
artifacts[]
environment
started_at
completed_at?
status
```

Owner: research/ML platform.

---

# 51. FHIR Exchange Record

`FHIRExchangeRecord`

```text
exchange_id
direction
external_system
resource_types[]
bundle_ref?
status
started_at
completed_at?
error_code?
provenance
```

Owner: `interoperability`.

---

# 52. ABDM Exchange Record

`ABDMExchangeRecord`

Generic fields only until approved ABDM spec:

```text
exchange_id
consent_ref
external_transaction_ref?
status
created_at
updated_at
error_code?
```

Do not invent current ABDM API semantics in this document.

---

# 53. Audit Event

`AuditEvent`

```text
audit_id
actor_ref
action
object_type
object_id?
timestamp
outcome
metadata
request_id?
```

Rules:

- append-oriented;
- no raw message body by default;
- distinct from domain events.

Owner: `audit`.

---

# 54. Domain Event

`DomainEvent`

```text
event_id
event_type
event_version
occurred_at
correlation_id
causation_id?
actor_ref?
payload
```

Examples:

```text
PatientCreated
EncounterStarted
ConsentGranted
ConsentRevoked
DocumentUploaded
DocumentProcessed
ClinicalFactExtracted
ClinicalFactConfirmed
SafetyRouteDecided
MentalHealthRouteDecided
ReferralCreated
ReferralStatusChanged
ClinicalSummaryConfirmed
```

---

# 55. Timeline Entry

`TimelineEntry` is a derived read-model concept.

```text
entry_id
patient_id
entry_type
occurred_at
source_ref
display_summary
verification_state?
```

The authoritative source remains the owning module and the projection should be rebuildable where practical.

---

# 56. Institution Reference

`InstitutionRef`

```text
institution_id
name?
type?
```

Full multi-tenancy is intentionally deferred. Core code must not assume one hard-coded institution.

---

# 57. Feature Manifest

`FeatureManifest`

```text
feature_id
version
capabilities[]
requires[]
api_prefixes[]
events_published[]
events_consumed[]
permissions[]
feature_flags[]
```

Used for explicit feature/module discoverability.

---

# 58. Capability IDs

Examples:

```text
patients.read
patients.timeline
consent.check
safety.evaluate
providers.search
resources.search
referrals.create
ocr.extract
speech.transcribe
risk.predict
```

Business modules depend on capabilities rather than vendor implementations.

---

# 59. Relationship Summary

```text
Patient 1 --- * Encounter
Patient 1 --- * ClinicalFact
Patient 1 --- * ClinicalDocument
Patient 1 --- * Referral
Patient 1 --- * RiskAssessment

Encounter 1 --- 0..1 ClinicalIntake
Encounter 1 --- * ClinicalFact
Encounter 1 --- * SafetyDecision
Encounter 1 --- * ClinicalSummary
Encounter 1 --- * ClinicalDocument

ClinicalDocument 1 --- * candidate ClinicalFact

ConsentRecord 1 --- * governed external actions

Provider/Resource 1 --- * Referral destination references

ModelRegistration 1 --- * RiskAssessment
```

---

# 60. Aggregate Ownership Summary

| Concept | Owning module |
|---|---|
| Actor | identity |
| Session | sessions |
| ConsentRecord | consent |
| Patient | patients |
| Encounter | encounters |
| ClinicalIntake | clinical_intake |
| SafetyDecision | safety |
| MentalHealthDecision | mental_health |
| ClinicalDocument | documents |
| Provenance | provenance |
| ClinicalSummary | summaries |
| SelfCareGuidanceDefinition | self_care |
| Provider | providers |
| CareResource | resources |
| Referral | referrals |
| NotificationIntent | notifications |
| RiskAssessment | ml/model gateway |
| ExperimentRun | research |
| FHIR/ABDM exchange records | interoperability |
| AuditEvent | audit |

---

# 61. Domain Invariants

- **INV-001:** model risk assessment never auto-creates a confirmed diagnosis.
- **INV-002:** AI/OCR-extracted fact cannot become clinician-confirmed without explicit confirmation.
- **INV-003:** safety decisions record policy version.
- **INV-004:** external referral send references required consent.
- **INV-005:** verified provider/resource has registry source and verification state.
- **INV-006:** self-care output references approved guidance version.
- **INV-007:** mental-health final route is deterministic-policy output.
- **INV-008:** provenance survives correction/supersession.
- **INV-009:** failed document processing cannot create accepted candidate facts.
- **INV-010:** research status does not imply production approval.

---

# 62. Extension Rule

For a new feature:

1. decide new aggregate vs extension;
2. avoid adding unrelated fields to Patient;
3. define owner;
4. define public capability;
5. define events if needed;
6. define provenance;
7. define safety/privacy impact;
8. define persistence in DB spec;
9. update this document.

---

# 63. FHIR Mapping Boundary

Examples:

```text
Patient -> FHIR Patient
Encounter -> FHIR Encounter
Observation -> FHIR Observation
AllergyRecord -> FHIR AllergyIntolerance
ClinicalDocument -> FHIR DocumentReference
ConsentRecord -> FHIR Consent
```

Risk assessment is not silently mapped as a confirmed Condition.

---

# 64. Open Domain Decisions

Still open:

- final medical coding system;
- final specialty taxonomy;
- final institution/tenancy model;
- exact named screening instruments;
- final clinical safety signal schemas;
- final ABDM-specific identifier/workflow details.

Codex must not silently finalize them.

---

# 65. Completion Criteria

This domain model is sufficient for foundation work when:

```text
[ ] canonical entities are named
[ ] module ownership is explicit
[ ] provenance model exists
[ ] decision support vs diagnosis separation is explicit
[ ] referral/consent relationship is explicit
[ ] model/research separation is explicit
[ ] future extension rules are explicit
```
