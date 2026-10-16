# Codex Phase Prompt — P7-A Intake Domain / Schema

**Project:** SwasthyaSetu AI
**Prompt ID:** `SSAI-CODEX-P7-A`
**Phase unit:** P7-A — Intake Domain / Schema
**Base branch:** `main`
**Expected base commit:** `2bfd834c4d1e4a1c0fb5782eeae6e2a6a097cda3`
**Implementation branch:** `phase/p7-a-intake-domain-schema`
**Commit message:** `feat: establish P7-A clinical intake domain and persistence`

## Mission

Begin P7 from the merged approved prerequisite specifications.

Current state:

```text
P6 = COMPLETE
Pre-P7 specification pack = COMPLETE
P7 = NOT STARTED
Alembic head = p5b_0006
```

Implement only P7-A:

```text
clinical_intake bounded-context skeleton
immutable intake domain types
closed typed question/answer/pack contracts
strict versioned JSON serialization
three canonical P7 persistence tables
Alembic migration
transaction-scoped PostgreSQL repositories
optimistic intake version persistence
public capability contracts/keys
module manifest
domain + real PostgreSQL tests
```

Do NOT implement the adaptive engine, application services, APIs, frontend/BFF, session/consent enforcement, encounter orchestration, AI, safety/triage, speech/translation, production clinical question content, Hindi clinical content, or AYUSH/Dashavidha clinical content.

P7-B owns deterministic engine/pack validation/history reuse logic.
P7-C owns application/API/BFF/UI/E2E.

Do not merge.

## 1. Preflight

Expected:

```text
branch: main
HEAD: 2bfd834c4d1e4a1c0fb5782eeae6e2a6a097cda3
working tree: clean
P6: COMPLETE
P7: NOT STARTED
Alembic head: p5b_0006
```

Create:

```text
git switch -c phase/p7-a-intake-domain-schema
```

## 2. Required Reading

Read completely:

```text
docs/00_PROJECT_MASTER_SPEC.md
docs/01_PRODUCT_REQUIREMENTS.md
docs/02_SYSTEM_ARCHITECTURE.md
docs/03_REPOSITORY_STRUCTURE.md
docs/04_DOMAIN_MODEL.md
docs/05_DATABASE_SCHEMA.md
docs/06_API_CONTRACTS.md
docs/07_CLINICAL_INTAKE_SPEC.md
docs/22_UX_AND_USER_FLOWS.md
docs/23_PATIENT_APP_SPEC.md
docs/29_ENGINEERING_STANDARDS.md
docs/34_MASTER_IMPLEMENTATION_PLAN.md
docs/implementation/35_PHASE_ACCEPTANCE_CRITERIA.md
docs/implementation/36_DEPENDENCY_MAP.md
docs/implementation/37_DECISION_LOG.md
docs/implementation/38_PROGRESS_TRACKER.md
docs/codex/CODEX_INSTRUCTIONS.md
docs/codex/CODEX_WORKFLOW.md
docs/codex/CODEX_CONTEXT_RULES.md
```

Inspect actual merged patterns:

```text
backend/app/modules/encounters/**
backend/app/modules/patients/**
backend/app/modules/provenance/**
backend/app/modules/consent/**
backend/app/modules/sessions/**
backend/app/shared/**
backend/migrations/env.py
backend/migrations/versions/0006_patient_encounter_persistence.py
backend/tests/integration/test_postgres_p5_persistence.py
backend/app/main.py
```

Code from repository reality, not assumptions.

## 3. P7-A Ownership

Per `07_CLINICAL_INTAKE_SPEC.md`, P7-A owns:

```text
domain types
closed serializers
module skeleton / manifest
three tables
migration
repositories
registry contracts
```

Expected package:

```text
backend/app/modules/clinical_intake/
  __init__.py
  domain.py
  serialization.py
  contracts.py
  infrastructure.py
  public.py
```

Small additional files are allowed when separation improves, but do not create an application/API layer.

## 4. Migration

Create exactly one migration:

```text
backend/migrations/versions/0007_clinical_intake_foundation.py
```

Expected:

```text
revision = p7a_0007
down_revision = p5b_0006
```

After P7-A:

```text
Alembic head = p7a_0007
```

## 5. Exact Table Scope

Create exactly:

```text
clinical_intakes
intake_answers
questionnaire_instances
```

Do not create safety, AI/message, question-pack DB, localization, diagnosis, triage, or other tables.

## 6. `clinical_intakes`

Columns:

```text
id UUID PK
encounter_id UUID UNIQUE NOT NULL
status VARCHAR NOT NULL
chief_complaint JSONB NULL
hpi JSONB NULL
history_sections JSONB NOT NULL DEFAULT '{}'
missing_information JSONB NOT NULL DEFAULT '[]'
contradictions JSONB NOT NULL DEFAULT '[]'
started_at TIMESTAMPTZ NOT NULL
completed_at TIMESTAMPTZ NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
version INTEGER NOT NULL DEFAULT 1
```

FK:

```text
encounter_id -> encounters.id
```

DB constraints:

```text
status IN ('IN_PROGRESS','COMPLETED','ABANDONED')
version > 0
(COMPLETED AND completed_at IS NOT NULL) OR (status <> 'COMPLETED' AND completed_at IS NULL)
chief_complaint IS NULL OR jsonb_typeof(chief_complaint)='object'
hpi IS NULL OR jsonb_typeof(hpi)='object'
jsonb_typeof(history_sections)='object'
jsonb_typeof(missing_information)='array'
jsonb_typeof(contradictions)='array'
```

One intake per encounter is mandatory.

No cascade delete unless already canonical.

## 7. `intake_answers`

Columns:

```text
id UUID PK
intake_id UUID NOT NULL
question_id VARCHAR NOT NULL
question_version VARCHAR NOT NULL
answer JSONB NOT NULL
source_type VARCHAR NOT NULL
answered_at TIMESTAMPTZ NOT NULL
created_at TIMESTAMPTZ NOT NULL
```

FK:

```text
intake_id -> clinical_intakes.id
```

Required:

```text
source_type IN ('PATIENT_TEXT','PATIENT_TOUCH','REUSED_HISTORY')
jsonb_typeof(answer)='object'
index (intake_id, question_id)
```

Answers are append-only. No update/delete repository API.

## 8. `questionnaire_instances`

Columns:

```text
id UUID PK
encounter_id UUID NOT NULL
questionnaire_id VARCHAR NOT NULL
questionnaire_version VARCHAR NOT NULL
status VARCHAR NOT NULL
responses JSONB NOT NULL
started_at TIMESTAMPTZ NOT NULL
completed_at TIMESTAMPTZ NULL
```

FK:

```text
encounter_id -> encounters.id
```

Required:

```text
status IN ('ACTIVE','COMPLETED','ABANDONED')
jsonb_typeof(responses)='object'
(COMPLETED AND completed_at IS NOT NULL) OR (status <> 'COMPLETED' AND completed_at IS NULL)
```

Add a non-unique lookup index for encounter/questionnaire identity.

Do not silently add additional uniqueness. If needed, report it as an open design issue.

## 9. Alembic Metadata

Import P7-A records in:

```text
backend/migrations/env.py
```

only for SQLAlchemy metadata discovery.

`alembic check` must be clean.

## 10. Intake Lifecycle

Closed lifecycle:

```text
IN_PROGRESS -> COMPLETED
IN_PROGRESS -> ABANDONED
```

Terminal:

```text
COMPLETED
ABANDONED
```

Do not add `DRAFT`, `READY_FOR_REVIEW`, diagnosis, safety, or clinician-confirmed persistence states.

## 11. `ClinicalIntake`

Immutable aggregate:

```text
intake_id
encounter_id
status
chief_complaint
hpi
history_sections
missing_information
contradictions
started_at
completed_at
version
```

Requirements:

```text
frozen/immutable
version > 0
timezone-aware datetimes normalized to UTC
COMPLETED requires completed_at
completed_at >= started_at
non-COMPLETED forbids completed_at
immutable tuple collections
no mutable dict clinical domain surface
no diagnosis/treatment/triage/safety/model-score fields
```

Lifecycle helpers may return immutable copies only.

## 12. Version Semantics

Repository mutation contract:

```text
input aggregate version == expected_version
successful save atomically persists state
DB version becomes expected_version + 1
returned domain/version reflects expected_version + 1
stale expected_version -> typed stale-write error
no partial write
```

Do not trust caller-controlled version jumps.

## 13. Chief Complaint

Implement typed `ChiefComplaint`.

Exact persistence shape:

```json
{
  "schema_version": "chief-complaint.v1",
  "patient_wording": "...",
  "display_key": "...",
  "normalized_code": null,
  "coding_system": null,
  "source_answer_id": "uuid"
}
```

Bound strings, reject blank/invalid where appropriate, exact keys/version, typed source ID, no diagnostic interpretation, no logging patient wording.

## 14. HPI

Typed:

```text
HistoryOfPresentIllness
StructuredValue
DurationValue
SeverityValue
```

Support:

```text
onset
duration
location
character
severity
progression
associated_symptoms
aggravating_factors
relieving_factors
```

Schema:

```text
hpi.v1
```

No clinical threshold interpretation.

Duration is structurally non-negative.
Severity is only configured scale ID/version + selected representational value.
All collections immutable.

## 15. History Sections

Typed:

```text
HistorySections
HistoryReference
```

Sections:

```text
past_medical
past_surgical
medications
allergies
family
personal
review_of_systems
prior_investigations
```

Schema:

```text
history-sections.v1
```

`HistoryReference`:

```text
entry_id
display_value
source_kind: ANSWER | REUSED_HISTORY
source_answer_id?
source_fact_id?
verification_state?
confirmation_state:
  NOT_REQUESTED | PENDING | CONFIRMED | DISAGREED
```

Enforce structural reference invariants. No patient-table dependency and no fact rewriting.

P7-A does not decide reuse eligibility.

## 16. ROS / Prior Investigations

Provide typed representation for review of systems and prior investigations.

ROS supports:

```text
system_key
finding_key or bounded patient wording
POSITIVE | NEGATIVE | UNKNOWN | NOT_ASKED
source references
```

Prior investigations support:

```text
investigation type
optional performed date/time
optional patient-provided result summary
optional document reference
source references
verification state
```

No OCR or interpretation.

## 17. Missing Information

Typed `MissingInformation`:

```text
missing_id
field_or_question_key
reason_code:
  REQUIRED_UNANSWERED
  CONDITIONAL_UNANSWERED
  RECONFIRMATION_REQUIRED
  CLARIFICATION_REQUIRED
requiredness:
  REQUIRED
  CONDITIONAL
source_pack_id
source_pack_version
source_rule_id
resolution_state:
  OPEN
  RESOLVED
  WAIVED
resolution_answer_id?
```

Represent/serialize only. P7-B calculates it.

## 18. Contradictions

Typed:

```text
Contradiction
SourceReference
```

Fields:

```text
contradiction_id
field_key
left_ref
right_ref
source_pack_id
source_rule_id
status:
  OPEN
  CLARIFICATION_REQUIRED
  RESOLVED
resolution_ref?
created_at
resolved_at?
```

Structural invariants only. No contradiction detection or winner selection.

## 19. Question Contracts

Create immutable:

```text
QuestionDefinition
QuestionSection
AnswerType
Requiredness
InputMode
ValidationConstraints
HistoryBinding
```

Closed AnswerType:

```text
TEXT
SINGLE_CHOICE
MULTI_CHOICE
BOOLEAN
NUMBER
DATE
DURATION
SEVERITY_SCALE
```

Sections:

```text
CHIEF_COMPLAINT
HPI
PAST_MEDICAL
PAST_SURGICAL
MEDICATIONS
ALLERGIES
FAMILY
PERSONAL
ROS
PRIOR_INVESTIGATIONS
EXTENSION
```

Input modes may represent TEXT/TOUCH/VOICE, but voice must not be runtime activated in P7.

No engine logic.

## 20. Validation Constraints

No arbitrary `dict[str, Any]`.

Use explicit typed/discriminated constraints for:

```text
text length
allowed option IDs
representational numeric bounds/unit
date bounds
duration units/range
severity scale ID/version + allowed values
```

These are representation constraints, not medical thresholds.

## 21. Intake Answer

Implement immutable `IntakeAnswer`.

JSON schema:

```text
schema_version = intake-answer.v1
answer_type
value
selected_option_ids?
unit?
response_disposition:
  ANSWERED
  UNKNOWN
  PREFER_NOT_TO_ANSWER
  SKIPPED
language_code
original_text?
```

Outer fields:

```text
answer_id
intake_id
question_id
question_version
source_type
answered_at
created_at
```

Reject invalid discriminator combinations, unknown keys/versions, invalid source type, naive datetimes, and unbounded original text.

Whether skip/refusal is allowed is P7-B configuration logic.

## 22. Questionnaire Instance

Implement immutable:

```text
QuestionnaireInstance
QuestionnaireStatus
QuestionnaireResponses
AnswerReference
SkippedQuestionReference
```

Statuses:

```text
ACTIVE
COMPLETED
ABANDONED
```

Responses schema:

```text
schema_version = questionnaire-responses.v1
pack_id
pack_version
answer_refs
skipped_question_refs
last_selected_question_id?
engine_version
```

Answers remain authoritative in `intake_answers`.
No question-selection logic.

## 23. Question-Pack Contracts

Define immutable:

```text
QuestionPack
QuestionPackKind
ApprovalState
RuleDefinition / RuleId contract
```

Kinds:

```text
CORE
COMPLAINT
SPECIALTY
AYUSH_EXTENSION
```

Approval states:

```text
ENGINEERING_APPROVED
CLINICAL_APPROVAL_REQUIRED
APPROVED
```

Fields:

```text
pack_id
version
schema_version = question-pack.v1
kind
approval_state
content_version
supported_languages
applicability_rules
contradiction_rules
questions
order
```

P7-B owns full registry validation, rule resolution, cycle checks, and engine behavior.

## 24. No Production Clinical Pack

P7-A must not ship a production-approved questionnaire.

Tests may use synthetic fixtures:

```text
synthetic.core
synthetic.specialty
synthetic.ayush
```

They must contain non-clinical placeholder content and never enter default runtime composition.

No Dashavidha questions.

## 25. Registry Contract

Provide a framework-independent explicit registration contract/container for future core/specialty/complaint/AYUSH packs.

No filesystem scanning, entry-point discovery, remote plugins, dynamic code execution, or global service locator.

P7-A may prove explicit identity/duplicate safety only.
P7-B owns full validation and activation policy.

No next-question selection.

## 26. Strict Serialization

Create strict serializers/deserializers for every P7-A JSONB shape.

Rules:

```text
schema version mandatory
exact key sets
unknown key rejected
unknown version rejected
enum validated
OpaqueId validated
timezone-aware datetime validation
deterministic Decimal serialization
immutable collections restored
no arbitrary nested mappings
no sensitive value in error text
```

Use safe generic errors such as:

```text
clinical intake persistence shape is invalid
```

Do not echo clinical values.

## 27. Repository Contracts

Protocols:

```text
ClinicalIntakeRepository
  add(session, intake)
  get(session, intake_id)
  get_by_encounter(session, encounter_id)
  save(session, intake, expected_version, updated_at)

IntakeAnswerRepository
  add(session, answer)
  list_for_intake(session, intake_id)

QuestionnaireInstanceRepository
  add(session, instance)
  get/list for encounter
  save state when required
```

Caller supplies `AsyncSession`.

Repositories must not open hidden transactions, commit, rollback caller transaction, depend on FastAPI, or call foreign modules.

Flush is allowed.

## 28. Optimistic Concurrency

`ClinicalIntakeRepository.save` must use authoritative persisted ID + expected_version.

Requirements:

```text
input current version == expected_version
safe lock/update
persist allowed intake fields
increment version exactly once
return updated version/domain copy
stale -> StaleClinicalIntakeWriteError
no lost update
```

## 29. One Intake Per Encounter

Two concurrent/same-encounter inserts must not create two intakes.

Expected domain/repository error:

```text
ClinicalIntakeAlreadyExistsError
```

Do not leak raw SQLAlchemy integrity errors for this expected conflict.

## 30. Append-Only Answers

Answer repository:

```text
insert only
no update
no delete
list ordered by answered_at ASC, answer_id ASC
```

Repeated answers remain preserved.

## 31. Questionnaire Persistence

Round-trip exact:

```text
encounter
questionnaire/pack ID
questionnaire version
status
typed response-reference index
started_at
completed_at
```

No arbitrary JSON and no clinical question text required in DB.

## 32. Public Capability Contracts

Define Protocols/keys for future canonical capabilities:

```text
intake.start
intake.read
intake.answer
intake.complete
intake.next_question
```

Do not provide fake service bindings.

## 33. Module Manifest

Define:

```text
CLINICAL_INTAKE_MANIFEST
module_id = clinical_intake
version = 1
```

Data ownership:

```text
clinical_intakes
intake_answers
questionnaire_instances
```

Required capability declarations should align with:

```text
sessions.validate
consent.check
encounters.read
encounters.transition
patient public read/fact capabilities needed by later P7
```

Provided capabilities may describe intended P7 public surface.

But:

```text
DO NOT register clinical_intake in create_app defaults
DO NOT bind stubs
DO NOT add routers
```

Runtime registration waits for real later-unit services.

## 34. Cross-Module Boundary

The new module must not import foreign infrastructure modules for domain behavior:

```text
patients.infrastructure
encounters.infrastructure
sessions.infrastructure
consent.infrastructure
```

Foreign FK table names are allowed.

Add/update AST/import-boundary tests.

## 35. Events

Do not publish runtime intake events in P7-A.

If future event dataclasses are defined, keep payloads to IDs/status/version/timestamps and exclude raw clinical content.

Do not wire outbox emission yet.

## 36. No API / Application Service

P7-A should not add:

```text
clinical_intake/api.py
clinical_intake/application.py
FastAPI intake routes
main.py default clinical_intake registration
```

A tiny domain factory is fine if framework-independent.

## 37. No Runtime Session/Consent Integration Yet

P7-A defines future dependency contracts only.

Do not call sessions.validate, consent.check, encounters.transition, or patients.read in runtime orchestration yet.

## 38. No Engine Yet

Do not implement:

```text
next-question algorithm
rule evaluator
missing-information recomputation
contradiction detection
history eligibility/suppression
pack applicability
completion-readiness calculation
```

P7-B owns these.

## 39. No AI / Safety

No runtime dependency on LLMs, AI gateways, prompt/model systems, safety policy, triage, diagnosis, self-care, speech, or translation.

## 40. No Frontend

Expected unchanged:

```text
apps/**
packages/**
tests/e2e/**
package.json
pnpm-lock.yaml
```

## 41. No New Dependency

Expected unchanged:

```text
backend/pyproject.toml
backend/uv.lock
package.json
pnpm-lock.yaml
```

## 42. Unit Tests — Domain

Cover:

```text
IN_PROGRESS construction
COMPLETED invariant
ABANDONED invariant
invalid/terminal transitions
naive datetime rejection
UTC normalization
positive version
chief complaint strict round-trip
unknown chief complaint version/key
all HPI fields
duration structural validation
severity structural validation without clinical thresholds
all history sections
history source/reference invariants
ROS
prior investigation
missing-information states
contradiction states
closed answer contracts
invalid discriminated answer combinations
question definition invariants
question-pack structural contracts
questionnaire response round-trip
unknown serializer versions
safe serializer error text
```

Use only synthetic test data.

## 43. Registry Contract Tests

Prove with synthetic fixtures:

```text
explicit pack identity/version
specialty pack representable
AYUSH_EXTENSION representable without clinical content
duplicate identity rejected if minimal registry exists
no runtime discovery
no default production pack
```

Do not claim AC-P7-008/009 fully complete before P7-B.

## 44. Real PostgreSQL Tests

Required:

```text
migration creates exactly three new tables
clinical intake round-trip
one intake per encounter uniqueness
pseudonymous encounter FK
missing encounter FK rejected
status constraints
completed_at lifecycle constraint
version > 0
JSONB object/array constraints
answer source_type constraint
questionnaire status constraint
strict typed JSON round-trip
append-only repeated answers
deterministic answer ordering
questionnaire response round-trip
stale save rejected
version increments exactly once
caller rollback removes all writes
repository does not commit hidden transaction
malformed/unsupported stored JSON fails safely
```

Real PostgreSQL only.

## 45. Atomic Rollback

Within one caller-owned transaction:

```text
add intake
add questionnaire instance
add answer
raise synthetic failure
```

After rollback none may persist.

## 46. Migration Verification

Real PostgreSQL:

```text
upgrade p5b_0006 -> p7a_0007
verify P7 tables/constraints/FKs/indexes
downgrade p7a_0007 -> p5b_0006
verify only P7-A tables removed
upgrade again -> p7a_0007
alembic check -> clean
```

Downgrade must not affect P5/P6 structures.

## 47. Regression

Preserve P1-P6 tests, P5 persistence, P6 PWA/BFF/frontend, and all six CI jobs.

## 48. CI

Keep exactly six jobs:

```text
Backend quality
Frontend quality
Persistence integration
Docker and PostgreSQL
Playwright Chromium
Security scans
```

All must pass on final SHA.

## 49. Acceptance After P7-A

Expected:

```text
P7-A = COMPLETE
P7 = PARTIAL

AC-P7-001 = PARTIAL / NOT YET COMPLETE
AC-P7-002 = PASS
AC-P7-003 = PASS
AC-P7-004 = PASS
AC-P7-005 = PASS
AC-P7-006 = NOT YET IMPLEMENTED — P7-B
AC-P7-007 = NOT YET IMPLEMENTED — P7-B
AC-P7-008 = PARTIAL
AC-P7-009 = PARTIAL
AC-P7-010 = PARTIAL
```

If evidence differs, report precisely. Do not mark P7 complete.

## 50. Progress Tracker

Before CI:

```text
P7-A = PARTIAL — REMOTE CI VERIFICATION PENDING
P7 = PARTIAL
```

After six jobs pass:

```text
P7-A = COMPLETE
P7 = PARTIAL
next = P7-B — Deterministic Adaptive Engine
```

## 51. Documentation

Update relevant:

```text
README.md
backend/README.md
REPOSITORY_TREE.txt
docs/03_REPOSITORY_STRUCTURE.md
docs/05_DATABASE_SCHEMA.md only for implemented migration annotation
docs/implementation/38_PROGRESS_TRACKER.md
docs/codex/CODEX_PHASE_PROMPTS/P7_A_INTAKE_DOMAIN_SCHEMA.md
```

Do not rewrite approved P7 specs unless a real contradiction is found. If found, stop/report rather than silently redefining the spec.

## 52. Verification

Run:

```text
uv lock --check
uv sync --locked --dev
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
uv run pytest -m postgres
uv run python -m compileall -q app tests
uv run alembic -c alembic.ini heads
uv run alembic -c alembic.ini check
```

Expected Alembic head:

```text
p7a_0007
```

Also:

```text
python scripts/quality_gate.py backend
python scripts/quality_gate.py frontend
git diff --check
```

Audit:

```text
no frontend changes
no dependency drift
no CI workflow change
no AI dependency
no P7 API
no main.py clinical_intake registration
no production clinical pack
no foreign direct ORM import
```

## 53. Commit / Push

```text
git add <P7-A files only>
git commit -m "feat: establish P7-A clinical intake domain and persistence"
git push -u origin phase/p7-a-intake-domain-schema
```

Do not merge.

## 54. Final Report

Return only:

```text
STATUS
BRANCH / GIT
DOMAIN MODEL
STRUCTURED SERIALIZATION
QUESTION / ANSWER CONTRACTS
QUESTION-PACK / REGISTRY CONTRACTS
PERSISTENCE
MIGRATION
REPOSITORIES / CONCURRENCY
ATOMICITY
MODULE MANIFEST / CAPABILITIES
BOUNDARY ENFORCEMENT
FILES CHANGED
DEPENDENCIES
TESTS
POSTGRESQL
VERIFICATION
CI
P7 ACCEPTANCE STATUS
DEVIATIONS
BLOCKERS / OPEN DECISIONS
PROGRESS TRACKER
MERGE
RECOMMENDED NEXT UNIT
```

`MERGE PERFORMED: NO`

Recommended next:

```text
P7-B — Deterministic Adaptive Engine
```

## Success Definition

P7-A is complete only when:
- immutable clinical-intake domain types exist;
- lifecycle is exactly IN_PROGRESS / COMPLETED / ABANDONED;
- no diagnosis/triage/treatment authority exists;
- chief complaint, all HPI fields, all history sections, ROS, prior investigations, missing info, and contradictions are typed;
- question/answer/pack/questionnaire contracts are closed;
- strict versioned JSON serializers reject arbitrary/unknown shapes;
- exactly three P7 tables exist;
- migration is `p7a_0007` on `p5b_0006`;
- one intake per encounter is DB enforced;
- answers are append-only;
- questionnaire state is typed;
- repositories use caller-owned AsyncSession and never commit;
- optimistic concurrency and atomic rollback are proven;
- manifest/capability contracts exist without fake bindings;
- clinical_intake is not yet registered in default app runtime;
- no adaptive engine/API/UI exists;
- no production clinical/AYUSH content is invented;
- no dependency drift occurs;
- real PostgreSQL migration/repository tests pass;
- Alembic head is `p7a_0007`;
- all six CI jobs pass;
- P7-A = COMPLETE;
- P7 = PARTIAL;
- branch is pushed and not merged.

Stop after P7-A.

---

## Implementation Record

```text
Status: PARTIAL — REMOTE CI VERIFICATION PENDING
Branch: phase/p7-a-intake-domain-schema
Base: 2bfd834c4d1e4a1c0fb5782eeae6e2a6a097cda3
Migration: p7a_0007 on p5b_0006
Scope: P7-A only; P7-B/P7-C not implemented
Remote CI: PENDING
```
