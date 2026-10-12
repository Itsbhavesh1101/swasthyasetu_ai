# Codex Phase Prompt — P5-A Patient / Encounter Domain Types & Entities

**Project:** SwasthyaSetu AI
**Prompt ID:** `SSAI-CODEX-P5-A`
**Phase unit:** P5-A — Patient / Encounter Domain Types & Entities
**Base branch:** `main`
**Expected base commit:** `f852ff7ca4cd70528f7e280bad5294ea2ed4a803`
**Implementation branch:** `phase/p5-a-domain-types-entities`
**Commit message:** `feat: establish P5-A patient encounter domain`

---

# 0. Mission

Begin P5 — Patient, Encounter and Longitudinal Clinical Domain.

Merged state:

```text
P4-A — Sessions                         COMPLETE
P4-B — Identity & Authorization         COMPLETE
P4-C — Consent Domain & APIs            COMPLETE
P4 overall                              COMPLETE

P5-A — Domain Types & Entities          NEXT
P5-B — Persistence / Migrations         NOT STARTED
P5-C — Timeline / Provenance APIs       NOT STARTED
```

P5-A is deliberately **domain-only**.

Implement the authoritative framework-independent domain model that later P5-B/P5-C, intake,
document/OCR, FHIR, clinician review, safety, self-care, and risk-model modules will consume.

Implement:

```text
Patient
PatientStatus
PatientIdentifier
PatientDemographics

Encounter
EncounterType
EncounterStatus
explicit encounter lifecycle/state transition rules

ClinicalFact
FactType
VerificationState
FactProvenance
ProvenanceSourceType

Problem
ProblemStatus

MedicationRecord
MedicationStatus

AllergyRecord
ProcedureRecord
Observation
InvestigationRecord

typed IDs / opaque-reference usage
UTC timestamp invariants
confidence invariants
fact correction/supersession rules
clinician-confirmed overwrite protection
public domain exports/contracts
domain unit tests
documentation reconciliation
```

Do NOT implement:

```text
SQLAlchemy models for P5
new tables
new Alembic migration
patient persistence
encounter persistence
clinical_facts persistence
provenance persistence
patient APIs
encounter APIs
timeline API/read model
fact review APIs
patient authorization HTTP flows
patient-subject consent activation
FHIR
ABDM
clinical intake
documents/OCR
AI extraction
summary generation
safety routing
frontend
```

P5-B owns persistence/migrations.

P5-C owns timeline/provenance services and APIs.

---

# 1. Mandatory Preflight

From repository root:

```text
git rev-parse --show-toplevel
git branch --show-current
git status --short
git rev-parse HEAD
git remote -v
git log --oneline --decorate -15
```

Expected:

```text
branch: main
HEAD: f852ff7ca4cd70528f7e280bad5294ea2ed4a803
working tree: clean
```

Verify merged P4 state:

```text
P4 = COMPLETE
AC-P4-001 through AC-P4-010 = PASS
Alembic head = p4c_0005
```

Verify these modules currently remain placeholders:

```text
backend/app/modules/patients/.gitkeep
backend/app/modules/encounters/.gitkeep
backend/app/modules/provenance/.gitkeep
```

If unrelated local changes exist, stop.

---

# 2. Create Branch

```text
git switch -c phase/p5-a-domain-types-entities
```

If already present, inspect history and preserve legitimate work.

Do not work on `main`.
Do not merge.

---

# 3. Required Reading

Read before editing:

```text
docs/00_PROJECT_MASTER_SPEC.md
docs/01_PRODUCT_REQUIREMENTS.md
docs/02_SYSTEM_ARCHITECTURE.md
docs/03_REPOSITORY_STRUCTURE.md
docs/04_DOMAIN_MODEL.md
docs/05_DATABASE_SCHEMA.md
docs/06_API_CONTRACTS.md
docs/29_ENGINEERING_STANDARDS.md
docs/34_MASTER_IMPLEMENTATION_PLAN.md

docs/implementation/35_PHASE_ACCEPTANCE_CRITERIA.md
docs/implementation/36_DEPENDENCY_MAP.md
docs/implementation/37_DECISION_LOG.md
docs/implementation/38_PROGRESS_TRACKER.md

docs/codex/CODEX_INSTRUCTIONS.md
docs/codex/CODEX_WORKFLOW.md
docs/codex/CODEX_CONTEXT_RULES.md

docs/research/r3/R3_FINAL_TECHNOLOGY_STACK.md
docs/research/r3/R3_ARCHITECTURE_RECONCILIATION.md
docs/research/r3/R3_CODEX_DEPENDENCY_POLICY.md

docs/codex/CODEX_PHASE_PROMPTS/P4_A_SESSIONS.md
docs/codex/CODEX_PHASE_PROMPTS/P4_B_IDENTITY_AUTHORIZATION_BASELINE.md
docs/codex/CODEX_PHASE_PROMPTS/P4_C_CONSENT_DOMAIN_APIS.md
```

Inspect current code:

```text
backend/app/shared/types/
backend/app/shared/security/
backend/app/modules/patients/
backend/app/modules/encounters/
backend/app/modules/provenance/
backend/app/modules/sessions/
backend/app/modules/identity/
backend/app/modules/consent/
backend/tests/
backend/migrations/
.github/workflows/ci.yml
```

Do not code from assumptions.

---

# 4. Governing P5 Requirements

P5 is governed by:

```text
FR-PAT-001 through FR-PAT-014
FR-ENC-001 through FR-ENC-006
FR-PROV-001 through FR-PROV-007
```

Relevant patient requirements include:

```text
structured profile
longitudinal record
problems
medications
allergies
procedures
investigations/labs
provenance
confidence/verification
correction history
source links
duplicate management
```

Relevant encounter requirements include:

```text
explicit encounter creation/state
patient/session/consent/language context
closure
incomplete != completed
```

P5-A provides domain foundations only; it does not claim all runtime/persistence requirements complete.

---

# 5. P5 Acceptance Staging

P5 acceptance criteria:

```text
AC-P5-001 — authoritative patient domain
AC-P5-002 — encounter lifecycle explicit/tested
AC-P5-003 — typed medication/allergy/problem/procedure/observation
AC-P5-004 — clinically meaningful facts support provenance
AC-P5-005 — AI-extracted facts support verification state
AC-P5-006 — clinician-confirmed fact cannot be silently overwritten
AC-P5-007 — timeline predictable ordering
AC-P5-008 — other modules consume patient context through public interfaces
```

Expected after successful P5-A:

```text
AC-P5-001 PASS
AC-P5-002 PASS
AC-P5-003 PASS
AC-P5-004 PASS
AC-P5-005 PASS
AC-P5-006 PASS
AC-P5-007 NOT YET IMPLEMENTED
AC-P5-008 NOT YET IMPLEMENTED
```

P5-A may establish public domain boundaries, but concrete patient-context capability implementations
and consumers arrive in P5-B/P5-C, so AC-P5-008 remains open.

Expected:

```text
P5-A = COMPLETE
P5 = PARTIAL
next = P5-B — Patient / Encounter Persistence & Migrations
```

---

# 6. Core Modeling Rules

Preserve:

```text
one authoritative patient domain
shared longitudinal context
no giant patient-history JSON object
provenance first-class
extracted != confirmed
risk assessment != diagnosis
safety route != diagnosis
patient != actor
patient != session
patient != encounter
```

No model inference may silently create a clinician-confirmed Problem.
No OCR/LLM-derived fact becomes trusted only because confidence is high.

---

# 7. Framework Independence

P5-A domain files MUST NOT import:

```text
FastAPI
SQLAlchemy
Psycopg
Alembic
Pydantic transport DTOs
```

Allowed:

```text
standard library
existing shared kernel types
frozen dataclasses
Enum / StrEnum
tuple / frozenset
OpaqueId
datetime / date
Decimal
```

Do not add dependencies.

---

# 8. Module Layout

Replace placeholders with real domain modules.

Recommended:

```text
backend/app/modules/patients/
    __init__.py
    domain.py
    clinical.py
    public.py

backend/app/modules/encounters/
    __init__.py
    domain.py
    public.py

backend/app/modules/provenance/
    __init__.py
    domain.py
    public.py
```

A smaller cohesive layout is acceptable.

Do not create empty infrastructure/application/api folders in P5-A.
Remove `.gitkeep` files when real files exist.

---

# 9. Runtime Registration Boundary

P5-A does NOT yet provide persistence-backed application capabilities.

Therefore:

```text
do not add patients/encounters/provenance to create_app() default registrations
do not add empty ModuleRegistration objects
do not claim provided runtime capabilities without bindings
```

P5-B/P5-C will activate concrete capabilities when services exist.

It is acceptable for `public.py` to expose stable domain contracts only.
Prefer no runtime registry change in P5-A.

---

# 10. Core IDs

Canonical concepts include:

```text
PatientId
EncounterId
ClinicalFactId
```

Reuse existing UUID-backed `OpaqueId` mechanics.
Do NOT duplicate UUID parsing/generation logic.

Lightweight semantic wrappers/aliases are allowed only if they remain immutable UUID-backed and do
not require shared-kernel churn.

---

# 11. Specification Drift 01 — Clinical Fact Supersession Link

There is a material domain/schema gap.

`docs/04_DOMAIN_MODEL.md` defines ClinicalFact without an explicit correction/supersession link.

`docs/05_DATABASE_SCHEMA.md` includes:

```text
superseded_by_fact_id UUID NULL
```

and requirements include:

```text
FR-PAT-012 correction history
AC-P5-006 clinician-confirmed fact cannot be silently overwritten
```

Report:

```text
SPECIFICATION DRIFT DETECTED
```

Reconcile `04_DOMAIN_MODEL.md` by adding:

```text
superseded_by_fact_id?
```

and documenting explicit supersession instead of destructive overwrite.

Do not create persistence/migration changes in P5-A.

---

# 12. Specification Drift 02 — Encounter created_by Optionality

Canonical Encounter currently lists:

```text
created_by
```

without optionality.

But:

```text
pseudonymous sessions may have no actor
encounters may exist for pseudonymous sessions
05_DATABASE_SCHEMA.md has created_by UUID NULL
```

Reconcile domain documentation to:

```text
created_by?
```

Do not fabricate an actor for pseudonymous encounters.

---

# 13. Encounter Consent Context — Defer Persistence Decision

`FR-ENC-003` says applicable consent context is part of encounter context.

Current canonical Encounter/DB schema has no dedicated consent reference.

P5-A MUST NOT invent:

```text
single consent_id
encounter_consents table
JSON consent dump
```

because P4 consent is purpose-specific and multiple consent records may apply.

Record as a P5-B/P5-C open decision:

```text
encounter workflows must retain/validate applicable consent context without collapsing
purpose-specific consent into one ambiguous FK.
```

Do not block P5-A on this.

---

# 14. PatientStatus

Define exactly:

```text
ACTIVE
INACTIVE
MERGED
DELETED_PENDING
```

No extra states.
No hard-delete behavior in P5-A.
No merge service yet.

---

# 15. Patient Entity

Define immutable `Patient`.

Canonical fields:

```text
patient_id
status
created_at
updated_at
preferred_language?
demographics?
identifiers
```

Rules:

```text
timestamps aware UTC
identifiers immutable collection
no actor roles
no session token
no consent flags
no clinical-history giant mapping
```

---

# 16. Patient Time Invariants

All Patient timestamps must be timezone-aware and normalized to UTC.

Require:

```text
updated_at >= created_at
```

Reject naive timestamps.

---

# 17. Preferred Language

Keep lightweight and bounded.

Do not implement translation behavior.
Do not infer language from location/device.
No new dependency.

---

# 18. PatientIdentifier

Define immutable `PatientIdentifier`:

```text
identifier_id
patient_id
system
value
use?
verified
source
```

Rules:

```text
system non-empty/bounded
value non-empty/bounded
source non-empty/bounded
verified explicit boolean
```

Examples:

```text
internal
hospital_mrn
abha
external_his
```

Do NOT:

```text
validate ABHA format in P5-A
connect to ABDM
normalize external identifiers without explicit source rules
log identifier values
```

No persistence/uniqueness behavior yet.

---

# 19. PatientDemographics

Define immutable `PatientDemographics` with canonical optional fields:

```text
date_of_birth?
age_years?
administrative_sex?
gender_identity?
pregnancy_status?
location_context?
```

Rules:

```text
collect only what workflows require
missing stays explicit
pregnancy status never inferred from administrative sex
```

Do not add name/email/phone/address without canonical requirement.
Do not infer DOB from age or age from DOB as authoritative state in P5-A.

---

# 20. Demographics Validation

Keep validation conservative:

```text
date_of_birth is a date when present
age_years non-negative when supplied
categorical strings bounded/non-blank when supplied
```

Do not invent clinical taxonomies for sex/gender/pregnancy/location.

---

# 21. EncounterType

Define exactly:

```text
GENERAL_INTAKE
MENTAL_HEALTH
KIOSK_INTAKE
CLINICIAN_REVIEW
DOCUMENT_REVIEW
RESEARCH_ONLY
```

---

# 22. EncounterStatus

Define exactly:

```text
CREATED
IN_PROGRESS
AWAITING_REVIEW
COMPLETED
ABANDONED
CANCELLED
```

Incomplete is not completed.

---

# 23. Encounter Entity

Define immutable `Encounter`:

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
created_by?
```

Technical lifecycle fields `created_at`, `updated_at`, `version` may be represented only if needed to
align the planned persistence model and are clearly documented.

Do not put intake content inside Encounter.

---

# 24. Encounter Required Session

Every encounter has `session_id`.

`patient_id` may be absent.
`created_by` may be absent.

This supports pseudonymous workflows.

---

# 25. Encounter Lifecycle

Implement deterministic transitions:

```text
CREATED
  -> IN_PROGRESS
  -> ABANDONED
  -> CANCELLED

IN_PROGRESS
  -> AWAITING_REVIEW
  -> COMPLETED
  -> ABANDONED
  -> CANCELLED

AWAITING_REVIEW
  -> IN_PROGRESS
  -> COMPLETED
  -> ABANDONED
  -> CANCELLED

COMPLETED
  -> terminal

ABANDONED
  -> terminal

CANCELLED
  -> terminal
```

This allows encounters that do not require review to complete directly from `IN_PROGRESS`, while a
review workflow may move back to active work before completion.

If canonical source docs explicitly contradict this during implementation, report drift instead of
silently changing the matrix.

---

# 26. Encounter Transition API

Provide a framework-independent method/function such as:

```text
can_transition_to(...)
transition_to(...)
```

Invalid transitions raise a typed domain error, e.g.:

```text
InvalidEncounterTransitionError
```

Do not use HTTP errors in domain code.

---

# 27. Encounter Completion Timestamp

Rules:

```text
COMPLETED -> completed_at required
non-COMPLETED -> completed_at remains NULL in P5-A
```

Transition to COMPLETED receives an explicit aware UTC timestamp.

Do not set `completed_at` for ABANDONED/CANCELLED because the canonical model does not define a
separate `closed_at` yet.

Do not invent one in P5-A.

---

# 28. Terminal Encounter Behavior

Terminal states:

```text
COMPLETED
ABANDONED
CANCELLED
```

reject further transitions.

No implicit reopening.

---

# 29. VerificationState

Define exactly:

```text
EXTRACTED
LOW_CONFIDENCE
NEEDS_CONFIRMATION
PATIENT_CONFIRMED
CLINICIAN_CONFIRMED
REJECTED
SUPERSEDED
```

Confidence alone never changes verification state.

---

# 30. ProvenanceSourceType

Define exactly:

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

No vendor-specific source type in core domain.

---

# 31. FactProvenance

Define immutable `FactProvenance`:

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

Rules:

```text
created_at aware UTC
confidence NULL or 0 <= confidence <= 1
source_ref bounded when present
machine metadata bounded when present
```

Confidence is not clinical certainty.

---

# 32. Provenance Privacy

Do not place raw transcript/document content, credentials, session tokens, or chain-of-thought in
FactProvenance.

`source_ref` is a reference, not a raw content dump.

---

# 33. FactType

Define canonical values:

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

P5-A does not implement the P7 intake engine for every FactType.

---

# 34. Typed Clinical Value Structures

P5-A MUST implement typed structures at least for:

```text
Problem
MedicationRecord
AllergyRecord
ProcedureRecord
Observation
InvestigationRecord
```

Do not collapse them into one untyped mapping.

---

# 35. Problem

Canonical fields:

```text
label
normalized_code?
status
onset?
resolution?
verification_state
```

ProblemStatus exactly:

```text
ACTIVE
HISTORICAL
RESOLVED
UNKNOWN
```

Rules:

```text
label non-empty
resolution must not precede onset when comparable
model risk must not auto-create CLINICIAN_CONFIRMED Problem
```

---

# 36. MedicationRecord

Canonical fields:

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

MedicationStatus exactly:

```text
ACTIVE
HISTORICAL
STOPPED
UNKNOWN
```

Rules:

```text
name non-empty
end_date >= start_date when both present
OCR-derived medication may remain EXTRACTED/NEEDS_CONFIRMATION
```

No interaction engine in P5-A.

---

# 37. AllergyRecord

Canonical fields:

```text
substance
normalized_code?
reaction?
severity?
status
verification_state
```

Canonical docs do not define an Allergy status vocabulary.

Do NOT invent a closed AllergyStatus enum.
Use a bounded validated machine code/string for `status` and document that terminology remains
extensible/governed later.

Do not infer allergy from side effect.

---

# 38. ProcedureRecord

Canonical fields:

```text
name
normalized_code?
performed_at?
facility?
notes?
verification_state
```

Keep notes bounded/repr-safe if validation is added.
Do not parse surgical text.

---

# 39. Observation

Canonical fields:

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

Support typed numeric and text values.
Use `Decimal` for precise numeric values where appropriate.

Do not infer diagnosis from out-of-range values.
Do not implement lab interpretation.

---

# 40. ReferenceRange

If useful, introduce:

```text
low?
high?
text?
```

Require:

```text
low <= high when both present
```

Do not require numeric range when only textual reference information exists.

---

# 41. Observation Unit Rule

Retain original units where known.

No unit conversion engine.
No silent normalization.

---

# 42. InvestigationRecord

Canonical fields:

```text
investigation_type
performed_at?
result_summary?
document_id?
status
verification_state
```

Canonical docs do not define a closed investigation-status vocabulary.
Do NOT invent one.
Use a bounded machine code/string.

No OCR/document lookup.

---

# 43. ClinicalFact

Define immutable `ClinicalFact` with canonical domain + correction-history fields:

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
superseded_by_fact_id?
```

Optional fields directly aligned to planned persistence such as `canonical_label` or `source_text`
may be added only if clearly useful and documented.

Do not add model-risk probability as a clinical fact field.

---

# 44. ClinicalFact Value

The authoritative domain value must be typed.

Use a union/protocol of current P5-A typed values rather than:

```text
dict[str, Any]
```

P5-B may map typed domain values to planned `structured_value JSONB` persistence.

---

# 45. ClinicalFact Provenance Rule

Every clinically meaningful ClinicalFact constructed in P5-A carries FactProvenance.

Do not make provenance optional merely because a caller lacks details.

If source details are unknown, use an explicit canonical provenance source rather than silently
omitting provenance.

---

# 46. Verification-State Consistency

ClinicalFact has canonical `verification_state`.
Typed clinical sub-records also contain verification state in the source domain model.

Avoid contradictory duplicated state.

Preferred:

```text
A. ClinicalFact is authoritative and nested values omit duplicate verification
OR
B. both exist and constructor validates equality
```

Do not allow a fact to be `CLINICIAN_CONFIRMED` while its MedicationRecord says `EXTRACTED`.

---

# 47. Machine-Derived Fact Rule

Sources such as:

```text
OCR
DOCUMENT_AI
MODEL_INFERENCE
```

must support untrusted states:

```text
EXTRACTED
LOW_CONFIDENCE
NEEDS_CONFIRMATION
```

Do not auto-confirm based on confidence.

---

# 48. Clinician-Confirmed Overwrite Protection

AC-P5-006 is mandatory in P5-A.

Implement explicit supersession logic.

Minimum rule:

```text
CLINICIAN_CONFIRMED existing fact cannot be superseded by replacement states:
  EXTRACTED
  LOW_CONFIDENCE
  NEEDS_CONFIRMATION
  PATIENT_CONFIRMED
```

A clinician-confirmed correction may supersede a clinician-confirmed fact only through the explicit
supersession operation.

Do not mutate/erase original fact value in place.

---

# 49. Explicit Supersession

Provide an operation such as:

```text
supersede_fact(existing, replacement)
```

or an entity method.

Requirements:

```text
existing/replacement IDs distinct
same logical patient/encounter scope where applicable
old fact becomes SUPERSEDED and records superseded_by_fact_id
replacement remains its own immutable fact
lower-trust replacement cannot supersede clinician-confirmed existing fact
```

Do not physically delete original fact.

---

# 50. Rejected / Superseded History

`REJECTED` and `SUPERSEDED` preserve history.

Do not delete rejected/superseded facts.
No persistence/query behavior yet.

Reject self-supersession:

```text
superseded_by_fact_id != fact_id
```

P5-A need not solve arbitrary persisted graph-cycle detection.

---

# 51. No Risk-Assessment Confusion

Do not create RiskAssessment as a Problem/ClinicalFact diagnosis.

Risk-model output is a separate future domain.

---

# 52. No Intake Aggregate

Do not implement:

```text
ClinicalIntake
HPI engine
questionnaires
adaptive questioning
```

P7 owns these.

---

# 53. Public Boundaries

Create stable domain exports:

```text
backend/app/modules/provenance/public.py
backend/app/modules/patients/public.py
backend/app/modules/encounters/public.py
```

Other modules should eventually import public contracts, not internals.

Do not expose nonexistent persistence/application services.

---

# 54. Capability Boundary

Architecture reserves concepts such as:

```text
patients.read
patients.timeline
```

P5-A MUST NOT register them as provided without implementations.

Prefer deferring runtime capability keys/providers to P5-B/P5-C.

---

# 55. Cross-Module Imports

Patient clinical types needing provenance should import via:

```text
app.modules.provenance.public
```

rather than future repository/infrastructure internals.

---

# 56. Domain Errors

Small framework-independent errors are allowed, e.g.:

```text
InvalidEncounterTransitionError
InvalidFactSupersessionError
DomainValidationError
```

Do not subclass FastAPI/HTTP exceptions.

---

# 57. Repr Privacy

Avoid exposing sensitive values in default repr where practical.

At minimum consider redacting/hiding:

```text
PatientIdentifier.value
ClinicalFact.source_text if included
ProcedureRecord.notes
InvestigationRecord.result_summary
```

No logging required in P5-A.

---

# 58. Immutability

Use immutable collections:

```text
tuple
frozenset
frozen nested dataclasses
```

No mutable list/dict fields in frozen domain objects.
No shared mutable defaults.

---

# 59. No Arbitrary Metadata Buckets

Avoid:

```text
patient.metadata
fact.extra
encounter.misc
```

unless canonical source explicitly requires it.

The point of P5-A is explicit typed domain structure.

---

# 60. Time Normalization

Reuse existing shared UTC helpers when appropriate.

If a local helper is needed:

```text
reject naive
normalize aware -> UTC
```

Do not import private helpers from unrelated modules.

---

# 61. Date vs DateTime

Use `date` for date-only concepts and aware `datetime` for instants.

Do not invent midnight UTC for date-only medical information.

---

# 62. Numeric Clinical Values

Prefer `Decimal` where exact decimal values matter:

```text
dose
observation numeric value
reference ranges
```

Do not build units/conversion infrastructure.

---

# 63. Confidence

Invariant:

```text
None OR 0 <= confidence <= 1
```

Reject NaN/infinite values if relevant.
Confidence never auto-changes verification state.

---

# 64. Patient Tests

Test exact PatientStatus values and timestamp/entity invariants.

No patient lifecycle transitions need to be invented.

---

# 65. PatientIdentifier Tests

Test:

```text
valid identifier
empty system rejected
empty value rejected
empty source rejected
verified retained
sensitive value excluded/redacted from repr if implemented
```

No live ABHA format tests.

---

# 66. Demographics Tests

Test:

```text
all optional works
negative age rejected if age_years supported
pregnancy remains independent of administrative sex
```

No inference logic.

---

# 67. Encounter Lifecycle Tests

At minimum:

```text
CREATED -> IN_PROGRESS
CREATED -> ABANDONED
IN_PROGRESS -> AWAITING_REVIEW
IN_PROGRESS -> COMPLETED
AWAITING_REVIEW -> IN_PROGRESS
AWAITING_REVIEW -> COMPLETED

COMPLETED -> any denied
ABANDONED -> any denied
CANCELLED -> any denied
```

Invalid transition leaves original immutable entity unchanged.

---

# 68. Encounter Timestamp Tests

Verify:

```text
naive started_at rejected
offset started_at normalized UTC
completed transition timestamp normalized UTC
completed_at not set for abandoned/cancelled
```

---

# 69. Typed Clinical Structure Tests

Test each:

```text
Problem
MedicationRecord
AllergyRecord
ProcedureRecord
Observation
InvestigationRecord
```

Verify relevant state/date/range invariants.

This is AC-P5-003 evidence.

---

# 70. Provenance Tests

Test:

```text
all source types
confidence 0 and 1 valid
<0 rejected
>1 rejected
NaN/infinite rejected if applicable
naive created_at rejected
offset timestamp normalized UTC
```

This is AC-P5-004 evidence.

---

# 71. Verification Tests

Verify all canonical VerificationState values.
Create a machine-derived fact in non-confirmed state.

This is AC-P5-005 evidence.

---

# 72. Supersession Tests

Mandatory:

```text
EXTRACTED -> explicit newer EXTRACTED allowed if chosen policy permits
PATIENT_CONFIRMED -> explicit replacement allowed according to chosen rule
CLINICIAN_CONFIRMED -> EXTRACTED denied
CLINICIAN_CONFIRMED -> NEEDS_CONFIRMATION denied
CLINICIAN_CONFIRMED -> PATIENT_CONFIRMED denied
CLINICIAN_CONFIRMED -> CLINICIAN_CONFIRMED explicit correction allowed
self-supersession denied
old fact preserved as historical/superseded
```

This is AC-P5-006 evidence.

---

# 73. Verification Consistency Test

If verification state exists in both ClinicalFact and nested values, mismatch must be rejected.

---

# 74. No Persistence

Expected unchanged:

```text
backend/migrations/**
backend/migrations/env.py
```

Alembic head remains:

```text
p4c_0005
```

No SQLAlchemy P5 model.

---

# 75. No Default App Registration

Existing default runtime modules remain:

```text
consent
identity
sessions
```

No patients/encounters/provenance runtime registration in P5-A.

---

# 76. No API

OpenAPI must not gain:

```text
/patients
/encounters
/clinical-facts
```

A focused regression assertion is useful if simple.

---

# 77. P4 Regression

All P4 tests remain green.

PATIENT-subject consent remains deferred; P5-A does not activate it because patient persistence and
authorization are not yet implemented.

---

# 78. Documentation

Update narrowly:

```text
docs/04_DOMAIN_MODEL.md
docs/03_REPOSITORY_STRUCTURE.md
docs/implementation/38_PROGRESS_TRACKER.md
README.md / backend/README.md only if phase summaries are maintained there
REPOSITORY_TREE.txt if maintained
docs/codex/CODEX_PHASE_PROMPTS/P5_A_DOMAIN_TYPES_ENTITIES.md
```

Required domain reconciliation:

```text
ClinicalFact.superseded_by_fact_id?
Encounter.created_by?
```

Do not rewrite unrelated clinical content.

---

# 79. Database Schema Doc Boundary

`05_DATABASE_SCHEMA.md` remains the P5-B persistence basis.

Do not rewrite its patient/encounter schema during P5-A except if a true contradiction makes the
domain impossible.

If additional persistence drift is discovered:

```text
report it
record it for P5-B
no migration now
```

---

# 80. Dependencies

Expected:

```text
NO new runtime dependency
NO new dev dependency
```

Expected unchanged:

```text
backend/pyproject.toml
backend/uv.lock
package.json
pnpm-lock.yaml
```

If a dependency appears necessary:

```text
STATUS: BLOCKED — DEPENDENCY REVIEW REQUIRED
```

---

# 81. Frontend

No frontend change.

Expected unchanged:

```text
apps/**
packages/**
package.json
pnpm-lock.yaml
```

---

# 82. Docker / Compose

No changes expected:

```text
deployments/local/compose.yaml
infra/docker/backend.Dockerfile
```

---

# 83. CI

Keep exactly six jobs:

```text
Backend quality
Frontend quality
Persistence integration
Docker and PostgreSQL
Playwright Chromium
Security scans
```

Do NOT update Alembic head assertion.
It must remain:

```text
p4c_0005
```

because P5-A has no migration.

---

# 84. Persistence Integration Regression

Existing P4 persistence integration remains unchanged and green.

Do not add P5 PostgreSQL tests in a domain-only phase.

---

# 85. Local Verification

From `backend/`:

```text
uv lock --check
uv sync --locked --dev
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
uv run python -m compileall -q app tests
uv run alembic -c alembic.ini heads
uv run alembic -c alembic.ini check
```

Expected head:

```text
p4c_0005
```

Run import smoke.

---

# 86. Root Quality Gates

From repository root:

```text
python scripts/quality_gate.py backend
python scripts/quality_gate.py frontend
```

Both pass.

---

# 87. Diff Audits

Expected dependency diff empty:

```text
git diff -- backend/pyproject.toml backend/uv.lock package.json pnpm-lock.yaml
```

Expected migration diff empty:

```text
git diff -- backend/alembic.ini backend/migrations/
```

Expected Docker/Compose diff empty:

```text
git diff -- deployments/local/compose.yaml infra/docker/backend.Dockerfile
```

Run:

```text
git diff --check
```

---

# 88. Architecture Audit

Verify:

```text
authoritative patient domain is typed
no giant history JSON
no SQLAlchemy in P5 domain
no migration
no new table
no API
no default runtime module registration
provenance first-class
verification explicit
clinician-confirmed overwrite guard
encounter lifecycle explicit
pseudonymous encounter without patient/actor allowed
no patient-subject consent activation
no FHIR/ABDM/intake/OCR/AI work
```

---

# 89. Privacy Audit

Verify:

```text
no patient identifier value logged
no raw source document/message in provenance
no credentials/tokens in domain entities
no inferred pregnancy
no invented PII fields
no clinical free-text logging
```

P5-A should add no logging.

---

# 90. Git Audit

Run:

```text
git status --short
git diff --stat
git diff
git diff --check
```

Do not commit:

```text
.env
DB dumps
test artifacts
logs
tokens
real patient data
```

Use synthetic fixtures only.

---

# 91. Commit & Push

After local verification:

```text
git add <P5-A files only>
git commit -m "feat: establish P5-A patient encounter domain"
git push -u origin phase/p5-a-domain-types-entities
```

Do not merge.
Do not force-push.

---

# 92. Progress Tracker Before CI

After local verification but before remote green:

```text
P5-A = PARTIAL — REMOTE CI VERIFICATION PENDING
P5 = PARTIAL
```

Record:

```text
base SHA
branch
implementation SHA
domain concepts
encounter lifecycle
provenance evidence
supersession evidence
AC-P5-001..006 local status
Alembic unchanged p4c_0005
```

---

# 93. Remote CI

Verify final branch SHA passes:

```text
Backend quality
Frontend quality
Persistence integration
Docker and PostgreSQL
Playwright Chromium
Security scans
```

All six must pass.

Do not claim completion before actual green CI.

---

# 94. Progress Tracker After CI

After all six jobs green:

```text
P5-A = COMPLETE
P5 = PARTIAL
```

Record:

```text
CI run ID
CI URL
head SHA
AC-P5-001 PASS
AC-P5-002 PASS
AC-P5-003 PASS
AC-P5-004 PASS
AC-P5-005 PASS
AC-P5-006 PASS
AC-P5-007 NOT YET IMPLEMENTED
AC-P5-008 NOT YET IMPLEMENTED
next = P5-B — Patient / Encounter Persistence & Migrations
```

Do not mark P5 complete.

---

# 95. Final Report Format

Return exactly these sections.

## STATUS

```text
COMPLETE / PARTIAL / BLOCKED / FAILED
```

`COMPLETE` requires all six remote CI jobs green.

## SPECIFICATION DRIFT

Report:

```text
ClinicalFact supersession-link drift
Encounter created_by optionality drift
Any additional real drift
Deferred encounter-consent-context decision
Files reconciled
```

## BRANCH / GIT

Report:

```text
base branch
base SHA
implementation branch
implementation SHA
closure SHA if any
remote SHA
main SHA
working-tree state
```

## SCOPE IMPLEMENTED

Only P5-A.

## PATIENT DOMAIN

Report:

```text
Patient
PatientStatus
PatientIdentifier
PatientDemographics
timestamp rules
identifier privacy
demographics inference rules
```

## ENCOUNTER DOMAIN

Report:

```text
Encounter
EncounterType
EncounterStatus
transition matrix
terminal states
pseudonymous behavior
completed_at behavior
created_by optionality
```

## PROVENANCE DOMAIN

Report:

```text
FactProvenance
ProvenanceSourceType
VerificationState
confidence validation
timestamp validation
source-reference privacy
```

## CLINICAL FACT DOMAIN

Report:

```text
ClinicalFact
FactType
typed value strategy
provenance requirement
verification-state strategy
superseded_by_fact_id
risk/diagnosis separation
```

## TYPED CLINICAL STRUCTURES

Report:

```text
Problem
MedicationRecord
AllergyRecord
ProcedureRecord
Observation
InvestigationRecord
status vocab decisions
date/range invariants
```

## SUPERSESSION / OVERWRITE PROTECTION

Report exact rules/tests:

```text
clinician-confirmed -> extracted
clinician-confirmed -> patient-confirmed
clinician-confirmed -> clinician-confirmed correction
self-supersession
historical fact preservation
```

## PUBLIC BOUNDARIES

Report:

```text
patients exports
encounters exports
provenance exports
runtime capabilities registered?
default app registrations changed?
```

Expected runtime registration change:

```text
NO
```

## FILES CHANGED

Group by domain/tests/docs.

## DEPENDENCIES

Expected no changes.

## MIGRATION / DATABASE STATUS

Report:

```text
new migration = NO
schema changes = NO
Alembic head = p4c_0005
alembic check
```

## TESTS

Report:

```text
new P5-A unit tests
total backend tests
patient tests
encounter transition tests
typed structure tests
provenance tests
verification tests
supersession tests
P4 regression
Postgres regression
```

## VERIFICATION

Report all local gates.

## CI

Report:

```text
run ID
URL
head SHA
Backend quality
Frontend quality
Persistence integration
Docker and PostgreSQL
Playwright Chromium
Security scans
overall
```

## P5 ACCEPTANCE STATUS

Expected P5-A result:

```text
AC-P5-001 PASS
AC-P5-002 PASS
AC-P5-003 PASS
AC-P5-004 PASS
AC-P5-005 PASS
AC-P5-006 PASS
AC-P5-007 NOT YET IMPLEMENTED
AC-P5-008 NOT YET IMPLEMENTED
```

## ARCHITECTURE / GOVERNANCE CHECK

Explicitly report:

```text
One authoritative patient domain: YES/NO
No giant patient-history JSON: YES/NO
Patient != Actor: YES/NO
Encounter may be pseudonymous: YES/NO
Encounter lifecycle explicit: YES/NO
Provenance mandatory for ClinicalFact: YES/NO
Verification state explicit: YES/NO
Clinician-confirmed overwrite fails closed: YES/NO
Original/superseded fact history preserved: YES/NO
No risk output treated as diagnosis: YES/NO
No SQLAlchemy in P5-A domain: YES/NO
No migration/schema change: YES/NO
No patient API pulled forward: YES/NO
No timeline pulled forward: YES/NO
No patient-subject consent activation: YES/NO
No intake/OCR/AI/FHIR work pulled forward: YES/NO
No new dependency: YES/NO
P4 contracts preserved: YES/NO
P2/P3 contracts preserved: YES/NO
```

## DEVIATIONS

List all deviations.

## BLOCKERS / OPEN DECISIONS

Expected deferred non-blockers:

```text
P5 persistence mapping / structured_value JSONB -> P5-B
patient_identifier uniqueness rules -> P5-B
demographics persistence reconciliation -> P5-B
encounter purpose-specific consent-context persistence -> P5-B/P5-C
patient-subject consent activation -> P5-C or governed authorization step
timeline read model -> P5-C
duplicate-record detection -> later P5/service work
```

## PROGRESS TRACKER

```text
P5-A status
overall P5 status
CI evidence
next recommended unit
```

## MERGE

```text
MERGE PERFORMED: NO
```

## RECOMMENDED NEXT UNIT

If P5-A complete:

```text
P5-B — Patient / Encounter Persistence & Migrations
```

Do not implement it.

---

# 96. Success Definition

P5-A is successful only when:

- Patient is an authoritative framework-independent domain entity;
- PatientStatus uses exactly ACTIVE/INACTIVE/MERGED/DELETED_PENDING;
- PatientIdentifier and PatientDemographics exist as structured types;
- Encounter is an authoritative domain entity;
- EncounterType and EncounterStatus use canonical values;
- encounter lifecycle is explicit and unit tested;
- terminal encounter states reject further transitions;
- pseudonymous encounters do not require a patient or actor;
- VerificationState exists with canonical values;
- ProvenanceSourceType exists with canonical values;
- FactProvenance validates confidence and UTC timestamps;
- ClinicalFact requires provenance;
- ClinicalFact supports explicit supersession linkage;
- typed Problem/Medication/Allergy/Procedure/Observation/Investigation structures exist;
- clinical values are not collapsed into one arbitrary mapping;
- clinician-confirmed facts cannot be silently overwritten by lower-trust extracted/patient facts;
- correction/supersession preserves historical fact identity;
- risk/model output is not treated as diagnosis;
- no P5 SQLAlchemy model exists;
- no migration is added;
- Alembic head remains p4c_0005;
- no P5 API is added;
- no timeline service is pulled forward;
- no patient-subject consent activation is pulled forward;
- no frontend/intake/OCR/AI/FHIR work is pulled forward;
- no dependency is added;
- all six remote CI jobs pass;
- AC-P5-001 through AC-P5-006 PASS;
- AC-P5-007/008 remain not yet implemented;
- P5-A is COMPLETE;
- P5 remains PARTIAL;
- branch is pushed but not merged.

Stop after P5-A.
