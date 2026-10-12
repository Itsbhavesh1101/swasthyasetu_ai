# Codex Phase Prompt — P5-C Timeline / Provenance Services & APIs

**Project:** SwasthyaSetu AI
**Prompt ID:** `SSAI-CODEX-P5-C`
**Phase unit:** P5-C — Timeline / Provenance Services & APIs
**Base branch:** `main`
**Expected base commit:** `ae987f683bee2bbb5759dd9abe8a3f66401bc74c`
**Implementation branch:** `phase/p5-c-timeline-provenance-apis`
**Commit message:** `feat: establish P5-C patient timeline services and APIs`

## 0. Mission

Complete P5 using the merged P5-A domain and P5-B PostgreSQL persistence.

Current state:

```text
P5-A = COMPLETE
P5-B = COMPLETE
P5-C = NEXT
P5 overall = PARTIAL

AC-P5-001..006 = PASS
AC-P5-007 = NOT YET IMPLEMENTED
AC-P5-008 = NOT YET IMPLEMENTED

Alembic head = p5b_0006
```

Implement only P5-C:

```text
patient application service
encounter application service
fact/provenance read services
longitudinal timeline read model
explicit public capability contracts
patients / encounters / provenance runtime module registrations
authorized patient APIs
authorized encounter APIs
patient facts read API
timeline API with bounded deterministic pagination
cross-module patient-context consumption only through public interfaces
P5 completion tests
```

Do NOT implement:

```text
new database tables
new Alembic migration
clinical intake
question packs
OCR/documents
AI extraction
FHIR/ABDM
referrals
safety routing
summary generation
frontend
clinician dashboard
fact-confirm/reject/correct HTTP APIs
patient-subject consent activation
external identity provider
new dependencies
```

P7 owns intake. Later clinician workflow owns governed fact-review HTTP actions.

---

## 1. Preflight

Expected:

```text
branch: main
HEAD: ae987f683bee2bbb5759dd9abe8a3f66401bc74c
working tree: clean
Alembic head: p5b_0006
P5-A: COMPLETE
P5-B: COMPLETE
P5: PARTIAL
```

Create:

```text
git switch -c phase/p5-c-timeline-provenance-apis
```

Do not merge.

---

## 2. Required Reading

Read all canonical project/architecture/database/API/engineering/acceptance/dependency/progress/Codex/R3 documents, plus:

```text
docs/codex/CODEX_PHASE_PROMPTS/P5_A_DOMAIN_TYPES_ENTITIES.md
docs/codex/CODEX_PHASE_PROMPTS/P5_B_PERSISTENCE_MIGRATIONS.md
```

Inspect actual merged implementations:

```text
backend/app/modules/patients/
backend/app/modules/encounters/
backend/app/modules/provenance/
backend/app/modules/sessions/
backend/app/modules/identity/
backend/app/modules/consent/
backend/app/api/security/
backend/app/main.py
backend/tests/
```

Do not code from assumptions.

---

## 3. P5-C Acceptance Target

P5-C must close:

```text
AC-P5-007 — timeline query orders relevant events predictably
AC-P5-008 — other modules consume patient context through public interfaces rather than direct table access
```

Successful final state:

```text
AC-P5-001..008 = PASS
P5-C = COMPLETE
P5 = COMPLETE
next = P6-A — Patient Web Design System / App Shell
```

Do not implement P6.

---

## 4. No Migration

Expected:

```text
NO new migration
NO schema change
Alembic head remains p5b_0006
```

P5-C is application/service/API composition over existing P5-B persistence.

---

## 5. Runtime Modules

Activate the existing bounded contexts through explicit compile-time registrations:

```text
patients
encounters
provenance
```

Default application modules become:

```text
consent
encounters
identity
patients
provenance
sessions
```

Use deterministic registry ordering.

No runtime discovery.

No plugin scanning.

---

## 6. Public Capabilities

Recommended patient capabilities:

```text
patients.create
patients.read
patients.fact.read
patients.facts.list
```

Recommended encounter capabilities:

```text
encounters.create
encounters.read
encounters.list
encounters.transition
```

Provenance/longitudinal capabilities:

```text
provenance.read
patients.timeline
```

Use typed Protocol contracts.

No ORM objects in capability contracts.

---

## 7. Cross-Module Rule — Critical

AC-P5-008 requires real enforcement.

Other modules MUST NOT import:

```text
app.modules.patients.infrastructure
app.modules.encounters.infrastructure
```

to obtain patient context.

Required composition pattern:

```text
Encounter service/API
    -> patients.read public capability

Timeline/Provenance service
    -> patients.read
    -> patients.facts.list / patients.fact.read
    -> encounters.list
```

Use injected public Protocol/capability providers.

Do not query another bounded context's tables directly.

Add AST/import-boundary tests.

---

## 8. Patient Service

Create framework-independent application service.

Operations:

```text
create_patient
get_patient
get_fact
list_facts
```

Use P5-B repositories.

Database disabled:

```text
DEPENDENCY_UNAVAILABLE
```

No hidden commits.

No global singleton.

---

## 9. Patient Creation Identity Rule

`POST /api/v1/patients` is authenticated continuity only.

The client MUST NOT provide `patient_id`.

Server derives patient ID from trusted:

```text
ActorContext.subject_id
```

Requirements:

```text
authenticated actor
patient self-write permission
subject_id present
```

Create:

```text
patient_id = ActorContext.subject_id
status = ACTIVE
created_at = now
updated_at = now
```

This avoids writing identity tables from the patients module.

If patient already exists:

```text
409 RESOURCE_CONFLICT
```

Do not mutate Actor records.

---

## 10. Authorization Policy Extension

Add only the permissions required for authenticated patient self-service:

```text
patient:write:self
encounter:read:self
encounter:write:self
```

Patient role receives:

```text
patient:read:self
patient:write:self
encounter:read:self
encounter:write:self
```

Preserve:

```text
actor type does not imply role
no wildcard
caregiver gets no automatic patient access
system admin is not implicit patient
MFA behavior unchanged
```

Update authorization policy version explicitly.

No new role codes.

---

## 11. Patient Create Request

Canonical strict body:

```json
{
  "preferred_language": "en",
  "demographics": {
    "date_of_birth": null,
    "age_years": null,
    "administrative_sex": null,
    "gender_identity": null,
    "pregnancy_status": null,
    "location_context": null
  }
}
```

All fields optional except request object itself.

Rules:

```text
extra=forbid
no identifiers
no patient_id
no status
no timestamps
no actor_id
no inference
```

Do not infer age from DOB.

Do not infer pregnancy from sex.

---

## 12. Patient Read API

Implement:

```text
GET /api/v1/patients/{patient_id}
```

Require:

```text
patient:read:self
ActorContext.subject_id == patient_id
```

Response may include:

```text
patient_id
status
preferred_language
demographics
created_at
updated_at
```

Do NOT expose patient identifiers in the initial HTTP response.

Internal `patients.read` capability may return full typed Patient.

Cross-patient access:

```text
403 AUTHORIZATION_DENIED
```

Anonymous:

```text
401 AUTHENTICATION_REQUIRED
```

---

## 13. Patient Facts Read API

Implement canonical read-only endpoint:

```text
GET /api/v1/patients/{patient_id}/facts
```

Require patient self-read authorization.

Optional filters:

```text
fact_type
verification_state
limit
cursor
```

Use bounded pagination.

Return safe fact summaries containing only what is necessary, such as:

```text
fact_id
fact_type
canonical_label
effective_time
recorded_at
verification_state
superseded_by_fact_id
provenance summary:
  source_type
  confidence
  created_at
```

Do NOT expose by default:

```text
source_text
source_ref
raw document/message
internal metadata
identifier values
arbitrary structured JSON
```

Internal fact capabilities may return full typed ClinicalFact.

---

## 14. Provenance Read Capability

Implement:

```text
provenance.read
```

Input:

```text
fact_id
```

Output:

```text
FactProvenance
```

It must operate through public patient/fact interfaces rather than direct patient table access.

No public `/provenance` oracle endpoint is required.

Authorization belongs to the consuming resource/API boundary.

---

## 15. Encounter Service

Create framework-independent application service.

Operations:

```text
create_encounter
get_encounter
list_for_patient
transition_encounter
```

Use P5-B encounter repository.

Use injected `patients.read` public capability where patient validation is needed.

Do not directly import patient persistence.

---

## 16. Encounter Creation API

Implement:

```text
POST /api/v1/encounters
```

Request:

```json
{
  "session_id": "uuid",
  "patient_id": "uuid-or-null",
  "encounter_type": "GENERAL_INTAKE"
}
```

Always require exact valid session bearer:

```text
Authorization: Bearer <session_token>
sessions.validate(session_id, token)
```

For:

```text
patient_id = null
```

session authorization is sufficient for eligible pseudonymous flow.

For:

```text
patient_id != null
```

also require trusted authenticated actor:

```text
encounter:write:self
ActorContext.subject_id == patient_id
```

and validate patient existence via `patients.read`.

Do not directly query patients table.

---

## 17. Patient-Creatable Encounter Types

Initial HTTP create permits only patient/session-facing encounter types:

```text
GENERAL_INTAKE
MENTAL_HEALTH
KIOSK_INTAKE
```

Do NOT allow patient/session HTTP callers to create:

```text
CLINICIAN_REVIEW
DOCUMENT_REVIEW
RESEARCH_ONLY
```

Also enforce session compatibility:

```text
KIOSK session -> KIOSK_INTAKE
PSEUDONYMOUS session -> GENERAL_INTAKE or MENTAL_HEALTH
```

Do not invent authenticated-session creation in this phase.

---

## 18. Encounter Creation Fields

Server controls:

```text
encounter_id
status = CREATED
started_at = now
completed_at = null
created_by
language_context
```

For authenticated patient-bound encounter:

```text
created_by = trusted ActorContext.actor_id
```

For pseudonymous encounter:

```text
created_by = null
```

Language context may copy the validated session language preference.

No client-created institution or creator field.

---

## 19. Encounter Read API

Implement:

```text
GET /api/v1/encounters/{encounter_id}
```

Authorization:

```text
patient-bound encounter:
  authenticated patient self
  encounter:read:self
  ActorContext.subject_id == encounter.patient_id

pseudonymous encounter:
  exact session bearer validated against encounter.session_id
```

Do not expose another patient's encounter.

No clinician-assignment access is implemented until an authoritative assignment model exists.

---

## 20. Encounter Transition APIs

Implement:

```text
POST /api/v1/encounters/{encounter_id}/complete
POST /api/v1/encounters/{encounter_id}/abandon
```

Authorization follows encounter read ownership but write requires:

```text
encounter:write:self
```

for patient-bound encounters.

Pseudonymous transitions require exact session bearer.

Use canonical P5-A transition matrix.

Invalid transition:

```text
409 INVALID_STATE_TRANSITION
```

Optimistic concurrency conflict:

```text
409 RESOURCE_CONFLICT
```

No public generic transition endpoint.

---

## 21. No Public Start Transition

Do not add:

```text
POST /encounters/{id}/start
```

P7 intake will use internal `encounters.transition` capability to move the encounter into the governed intake lifecycle.

A freshly-created `CREATED` encounter cannot be completed directly because P5-A forbids it.

This is expected.

---

## 22. Timeline Service

Implement an immutable longitudinal read model.

P5-C timeline entry types:

```text
ENCOUNTER
CLINICAL_FACT
```

Do not invent referral/document/safety events before those modules exist.

Timeline service must consume:

```text
patients.read
patients.facts.list
encounters.list
```

through public contracts/injected capability providers.

No direct cross-module ORM/table imports.

---

## 23. Timeline Timestamp Semantics

Use:

```text
ClinicalFact -> effective_time if present, otherwise recorded_at
Encounter    -> started_at
```

Expose this as:

```text
occurred_at
```

Do not fabricate event time.

---

## 24. Timeline Ordering

Define one deterministic order and document it.

Recommended:

```text
occurred_at DESC
entry_type ASC
entry_id ASC
```

Newest-first is acceptable as the API's documented chronological presentation.

Equal timestamps must have deterministic tie-breaking.

AC-P5-007 must test ties.

---

## 25. Timeline API

Implement:

```text
GET /api/v1/patients/{patient_id}/timeline
```

Query:

```text
limit?
cursor?
entry_type?
from?
to?
```

Requirements:

```text
patient self-read authorization
limit default <= 50
limit maximum <= 100
strict UTC timestamp validation
from <= to
opaque/versioned cursor
stable pagination
no duplicate/skip across page boundary
```

No offset pagination for the authoritative contract.

---

## 26. Timeline Cursor

Use a versioned opaque URL-safe cursor.

Cursor must encode only pagination position, e.g.:

```text
version
occurred_at
entry_type
entry_id
```

No PHI.

No identifier value.

Malformed cursor:

```text
422 VALIDATION_ERROR
```

No new crypto/dependency required; opacity is not secrecy.

---

## 27. Timeline Entry Payload

Encounter entry:

```text
entry_id
entry_type = ENCOUNTER
occurred_at
encounter_id
encounter_type
status
completed_at?
```

Clinical fact entry:

```text
entry_id
entry_type = CLINICAL_FACT
occurred_at
fact_id
fact_type
canonical_label
verification_state
superseded_by_fact_id?
provenance:
  source_type
  confidence
  created_at
```

Do not include raw structured clinical JSON.

Do not include source text/ref.

---

## 28. Timeline Filtering

Support:

```text
entry_type
from
to
```

Filtering must happen before pagination.

Do not load the entire longitudinal history into memory.

Underlying source queries must be bounded.

A bounded merge of independently bounded patient-fact and encounter result sets is acceptable.

---

## 29. Public Interface Requirement

Prove AC-P5-008 with real architecture tests.

At least one real P5-C service must consume patient context via public contracts.

Required examples:

```text
Encounter composition validates patient through patients.read
Timeline composes facts/encounters through public interfaces
```

AST/import tests must fail if non-owning modules import:

```text
patients.infrastructure
encounters.infrastructure
```

No competing patient-history JSON silo.

---

## 30. Fact Review APIs Deferred

Do NOT implement in P5-C:

```text
POST /clinical-facts/{id}/confirm
POST /clinical-facts/{id}/reject
POST /clinical-facts/{id}/correct
```

Reason:

```text
no authoritative clinician assignment/resource-authorization model is active yet
```

P5-A/P5-B already preserve verification and correction history.

Record this as an intentional deferred governed API, not missing persistence.

---

## 31. PATIENT Consent Subject Remains Deferred

Do NOT change P4-C PATIENT consent authorization in P5-C.

Patient persistence alone does not establish a complete consent/onboarding authorization flow.

P6 onboarding or a separately governed authorization step may activate it.

SESSION and ACTOR consent behavior must remain unchanged.

---

## 32. Consent Context on Encounter

Do NOT add a single encounter `consent_id` or consent blob.

No schema change.

Purpose-specific consent remains validated by the consuming workflow when applicable.

Do not invent one universal consent rule for every encounter type.

---

## 33. HTTP Privacy

All new patient/encounter/fact/timeline success and error responses:

```text
Cache-Control: no-store
```

Extend the existing sensitive-response helper cleanly.

Do not log:

```text
demographics
clinical labels/values
facts
provenance refs
patient identifiers
Authorization
timeline payload
```

No patient/fact IDs as metric labels.

---

## 34. Strict DTOs

All request DTOs:

```text
extra=forbid
```

Server-owned fields must be rejected.

Validation errors must not echo sensitive submitted payloads.

---

## 35. Error Semantics

Use existing codes:

```text
AUTHENTICATION_REQUIRED        401
AUTHORIZATION_DENIED           403
RESOURCE_NOT_FOUND             404
RESOURCE_CONFLICT              409
INVALID_STATE_TRANSITION       409
VALIDATION_ERROR               422
DEPENDENCY_UNAVAILABLE         503
```

No new public error code expected.

---

## 36. Database Disabled

Routes remain registered.

Persistence-dependent calls return:

```text
503 DEPENDENCY_UNAVAILABLE
```

No 500.

---

## 37. No New Dependency

Expected unchanged:

```text
backend/pyproject.toml
backend/uv.lock
package.json
pnpm-lock.yaml
```

No new runtime/dev package.

---

## 38. No Schema Change

Expected unchanged:

```text
backend/migrations/versions/
```

except no new file.

Alembic:

```text
heads = p5b_0006
check = clean
```

---

## 39. Frontend / Docker

Expected unchanged:

```text
apps/**
packages/ui/**
deployments/local/compose.yaml
infra/docker/backend.Dockerfile
```

No P6 implementation.

---

## 40. Required Unit Tests

Cover:

```text
new authorization permissions
patient create ID derived from ActorContext
no client patient_id
patient cross-subject denial
encounter self/session authorization rules
encounter allowed create types
session-type compatibility
transition mapping
timeline entry timestamp rules
timeline deterministic tie ordering
cursor encode/decode
cursor malformed rejection
provenance summary mapping
module manifests/capabilities
cross-module import boundary
```

---

## 41. Required PostgreSQL Tests

Real PostgreSQL:

```text
patient service create/read
duplicate patient conflict
patient fact bounded list
encounter create/read
pseudonymous encounter
patient-bound encounter
encounter transition persistence
stale-write conflict mapping
timeline across encounters + facts
timeline equal-timestamp deterministic ordering
timeline pagination no duplicate/skip
timeline filters
provenance.read
DB-disabled behavior where applicable
```

No SQLite substitute.

---

## 42. Required HTTP Tests

Test with real app/database:

```text
POST /patients authenticated self -> 201
POST /patients anonymous -> 401
POST /patients missing trusted subject -> 403
GET self patient -> 200
GET other patient -> 403

POST pseudonymous encounter with correct session bearer -> 201
cross-session token -> 401
patient-bound encounter self + session -> 201
patient-bound cross-patient -> 403

GET pseudonymous encounter correct bearer -> 200
GET patient-bound encounter self -> 200

abandon valid -> 200
complete invalid from CREATED -> 409
complete valid from IN_PROGRESS/AWAITING_REVIEW fixture -> 200

GET patient facts self -> 200
GET timeline self -> 200
timeline cross-patient -> 403
timeline pagination/filtering -> correct
no-store headers -> present
```

Use trusted ActorContext injection only in tests.

No client identity headers.

---

## 43. Module Registration Tests

Default modules:

```text
consent
encounters
identity
patients
provenance
sessions
```

Capabilities resolve and registry seals.

Custom explicit `module_registrations=(...)` behavior remains unchanged.

No hidden built-ins for custom composition.

---

## 44. P4 Regression

Preserve:

```text
sessions
identity
authorization
MFA
consent
cross-subject protections
no PATIENT consent activation
```

P4 tests remain green.

---

## 45. P5-A/P5-B Regression

Preserve:

```text
domain immutability
supersession trust guard
typed structured_value mapping
provenance
projections
optimistic encounter versioning
p5b_0006 schema
migration downgrade/re-upgrade
```

No weakening.

---

## 46. CI

Keep exactly six jobs:

```text
Backend quality
Frontend quality
Persistence integration
Docker and PostgreSQL
Playwright Chromium
Security scans
```

All must pass on final branch SHA.

---

## 47. Local Verification

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

Expected:

```text
p5b_0006
```

From root:

```text
python scripts/quality_gate.py backend
python scripts/quality_gate.py frontend
```

Run dependency/schema/frontend/Docker diff audits and `git diff --check`.

---

## 48. Documentation

Update relevant:

```text
README.md
backend/README.md
REPOSITORY_TREE.txt
docs/03_REPOSITORY_STRUCTURE.md
docs/06_API_CONTRACTS.md if behavior needs clarification
docs/implementation/38_PROGRESS_TRACKER.md
docs/codex/CODEX_PHASE_PROMPTS/P5_C_TIMELINE_PROVENANCE_APIS.md
```

Do not rewrite unrelated canonical docs.

---

## 49. Progress Tracker

Before remote CI:

```text
P5-C = PARTIAL — REMOTE CI VERIFICATION PENDING
P5 = PARTIAL
```

After all six jobs green and acceptance verified:

```text
P5-C = COMPLETE
P5 = COMPLETE
AC-P5-001..008 = PASS
next = P6-A — Patient Web Design System / App Shell
```

---

## 50. Commit / Push

```text
git add <P5-C files only>
git commit -m "feat: establish P5-C patient timeline services and APIs"
git push -u origin phase/p5-c-timeline-provenance-apis
```

Do not merge.

---

## 51. Final Report

Return concise sections:

```text
STATUS
BRANCH / GIT
SCOPE IMPLEMENTED
AUTHORIZATION
PATIENT SERVICE / API
ENCOUNTER SERVICE / API
FACT / PROVENANCE READ
TIMELINE
PUBLIC CAPABILITIES / MODULES
AC-P5-008 BOUNDARY EVIDENCE
FILES CHANGED
DEPENDENCIES
MIGRATION STATUS
TESTS
VERIFICATION
CI
P5 FINAL ACCEPTANCE
DEVIATIONS
BLOCKERS / OPEN DECISIONS
PROGRESS TRACKER
MERGE
RECOMMENDED NEXT UNIT
```

`MERGE`:

```text
MERGE PERFORMED: NO
```

---

## 52. Success Definition

P5-C is complete only when:

- patient service/API exists with trusted self-subject authorization;
- patient ID is never client-selected;
- patient profile reads are self-authorized;
- identifiers are not exposed in initial patient HTTP response;
- patient facts have a bounded authorized read API;
- provenance is available through a public capability;
- encounter create/read/transition services exist;
- pseudonymous encounter authorization uses exact session bearer;
- patient-bound encounter authorization is self-subject and fail-closed;
- encounter service validates patient through public patients interface;
- timeline contains encounter + clinical fact entries;
- timeline timestamps are explicitly defined;
- timeline ordering is deterministic including equal-time ties;
- cursor pagination is bounded, stable and opaque;
- timeline service composes public interfaces rather than foreign repositories/tables;
- AC-P5-007 passes;
- AC-P5-008 passes;
- no fact review write API is prematurely exposed;
- PATIENT consent authorization remains deferred;
- no schema/migration/dependency/frontend change occurs;
- Alembic head remains `p5b_0006`;
- P4 and P5-A/B regressions remain green;
- all six CI jobs pass;
- P5-C = COMPLETE;
- P5 = COMPLETE;
- branch is pushed but not merged.

Stop after P5-C.

---

## Execution Record

```text
Implementation: COMPLETE LOCALLY
Remote CI: PENDING
Alembic head: p5b_0006
Schema/dependencies/frontend/Docker: UNCHANGED
AC-P5-001..008: PASS LOCALLY
```
