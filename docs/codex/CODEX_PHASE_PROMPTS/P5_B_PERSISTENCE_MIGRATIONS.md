# Codex Phase Prompt — P5-B Patient / Encounter Persistence & Migrations

**Project:** SwasthyaSetu AI
**Prompt ID:** `SSAI-CODEX-P5-B`
**Phase unit:** P5-B — Patient / Encounter Persistence & Migrations
**Base branch:** `main`
**Expected base commit:** `470aeec643a577e82d035c23e5771bed74149a28`
**Implementation branch:** `phase/p5-b-persistence-migrations`
**Commit message:** `feat: establish P5-B patient persistence`

## 0. Mission

Continue P5 after the merged P5-A domain-only baseline.

Current state:

```text
P4 = COMPLETE
P5-A = COMPLETE
P5-B = NEXT
P5-C = NOT STARTED
P5 overall = PARTIAL
Alembic head = p4c_0005
```

Implement only persistence/migrations for the authoritative P5-A domain.

Implement:

```text
patients persistence
patient_demographics persistence
patient_identifiers persistence
encounters persistence
clinical_facts persistence
clinical_fact_provenance persistence
medications projection
allergies projection
observations projection
typed domain <-> persistence mappers
narrow repositories
sessions.patient_id -> patients.id FK
Alembic migration
real PostgreSQL round-trip/integrity tests
migration downgrade/re-upgrade verification
documentation reconciliation
CI evidence
```

Do NOT implement:

```text
patient HTTP APIs
encounter HTTP APIs
timeline API/read model
timeline query
patient-subject consent activation
clinical-fact review APIs
intake engine
OCR/document ingestion
AI extraction
FHIR/ABDM workflows
frontend
new external services
new dependencies
```

P5-C owns timeline/provenance services and APIs.

---

# 1. Preflight

Run:

```text
git branch --show-current
git status --short
git rev-parse HEAD
git log --oneline --decorate -15
```

Expected:

```text
branch: main
HEAD: 470aeec643a577e82d035c23e5771bed74149a28
working tree: clean
```

Verify:

```text
P5-A = COMPLETE
AC-P5-001..006 = PASS
AC-P5-007..008 = NOT YET IMPLEMENTED
Alembic head = p4c_0005
```

Create:

```text
git switch -c phase/p5-b-persistence-migrations
```

Do not merge.

---

# 2. Required Reading

Read before coding:

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
docs/codex/CODEX_PHASE_PROMPTS/P5_A_DOMAIN_TYPES_ENTITIES.md
```

Inspect actual P5-A domain and current persistence patterns.

---

# 3. P5 Acceptance Boundary

P5-A already closed:

```text
AC-P5-001
AC-P5-002
AC-P5-003
AC-P5-004
AC-P5-005
AC-P5-006
```

P5-B must preserve these.

Do NOT mark:

```text
AC-P5-007
AC-P5-008
```

complete unless their exact acceptance condition is actually implemented.

Expected after P5-B:

```text
AC-P5-001..006 PASS
AC-P5-007 NOT YET IMPLEMENTED
AC-P5-008 NOT YET IMPLEMENTED or PARTIAL groundwork only
P5-B COMPLETE
P5 PARTIAL
next P5-C
```

---

# 4. Tables to Add

Create exactly these P5 persistence tables:

```text
patients
patient_demographics
patient_identifiers
encounters
clinical_facts
clinical_fact_provenance
medications
allergies
observations
```

Do not create:

```text
clinical_intakes
intake_answers
questionnaire_instances
documents
referrals
audit tables
safety tables
FHIR resource tables
```

---

# 5. Migration

Create:

```text
backend/migrations/versions/0006_patient_encounter_persistence.py
```

Revision:

```text
p5b_0006
```

Parent:

```text
p4c_0005
```

Upgrade only P5-B persistence.

Downgrade must restore P4-C schema exactly.

---

# 6. Patients

Table:

```text
patients
id UUID PK
status VARCHAR NOT NULL
preferred_language VARCHAR NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

Use named check for canonical PatientStatus.

No actor identity fields.

Patient != Actor.

---

# 7. Patient Demographics Drift Reconciliation

P5-A domain contains:

```text
date_of_birth
age_years
administrative_sex
gender_identity
pregnancy_status
location_context
```

Canonical DB draft does not fully preserve all of these.

Do NOT silently drop domain fields.

Reconcile schema explicitly with typed nullable columns sufficient for lossless P5-A round-trip.

Preferred:

```text
patient_id UUID PK/FK patients(id)
date_of_birth DATE NULL
age_years INTEGER NULL
administrative_sex VARCHAR NULL
gender_identity VARCHAR NULL
pregnancy_status VARCHAR NULL
location_context VARCHAR NULL
demographics_metadata JSONB NULL
updated_at TIMESTAMPTZ NOT NULL
```

Rules:

```text
age_years >= 0 when present
no automatic age derivation
no pregnancy inference
metadata reserved/internal, not arbitrary clinical truth
```

Document the reconciliation.

---

# 8. Patient Identifiers

Table:

```text
patient_identifiers
id UUID PK
patient_id UUID FK patients(id)
system VARCHAR NOT NULL
value TEXT NOT NULL
use VARCHAR NULL
verified BOOLEAN NOT NULL
source VARCHAR NOT NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

Important uniqueness decision:

The schema calls `UNIQUE(system, value)` only a candidate pending final rules.

Do NOT impose global uniqueness unless the canonical namespace semantics now prove it valid.

Reason:

```text
hospital_mrn may not be globally unique across institutions
```

Preferred P5-B baseline:

```text
non-unique index on (system, value)
```

and document scoped uniqueness as deferred.

Identifier values must never be logged or exposed in repr.

---

# 9. Encounters

Table:

```text
encounters
id UUID PK
patient_id UUID NULL
session_id UUID NOT NULL
encounter_type VARCHAR NOT NULL
status VARCHAR NOT NULL
institution_id UUID NULL
language_context JSONB or bounded scalar representation
started_at TIMESTAMPTZ NOT NULL
completed_at TIMESTAMPTZ NULL
created_by UUID NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
version INTEGER NOT NULL DEFAULT 1
```

FKs:

```text
patient_id -> patients.id
session_id -> sessions.id
created_by -> actors.id
```

No FK for institution_id because no authoritative institution table exists yet.

Pseudonymous encounters remain valid:

```text
patient_id NULL
created_by NULL
```

---

# 10. Encounter Consent Context

Do NOT add one ambiguous:

```text
consent_id
consent_status
consent JSON blob
```

to encounters.

Purpose-specific consent context remains deferred to P5-C/later consuming workflows.

Document the decision.

---

# 11. sessions.patient_id FK

P4-A staged:

```text
sessions.patient_id UUID NULL
```

Now add named FK:

```text
sessions.patient_id -> patients.id
```

Keep nullable.

Do not change session ownership or session service behavior.

Patients module must not directly mutate session rows.

---

# 12. Clinical Facts

Table:

```text
clinical_facts
id UUID PK
patient_id UUID NULL
encounter_id UUID NULL
fact_type VARCHAR NOT NULL
canonical_label TEXT NOT NULL
normalized_code TEXT NULL
coding_system TEXT NULL
effective_at TIMESTAMPTZ NULL
verification_state VARCHAR NOT NULL
structured_value JSONB NOT NULL
source_text TEXT NULL
superseded_by_fact_id UUID NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

FKs:

```text
patient_id -> patients.id
encounter_id -> encounters.id
superseded_by_fact_id -> clinical_facts.id
```

No cascade that destroys clinical history.

---

# 13. Clinical Fact Canonical Label Drift

P5-A `ClinicalFact` has no separate `canonical_label`, while DB requires it.

Do NOT add duplicated mutable domain truth casually.

Derive canonical label deterministically from typed value:

```text
Problem.label
MedicationRecord.name
AllergyRecord.substance
ProcedureRecord.name
Observation.observation_type
InvestigationRecord.investigation_type
```

Implement one explicit mapper/helper.

Document this persistence mapping.

Do not accept an unrelated free-text label.

---

# 14. Clinical Fact Timestamp Mapping

P5-A domain uses:

```text
recorded_at
```

DB draft uses:

```text
created_at
updated_at
```

Persistence rule:

```text
created_at = original recorded_at
updated_at = persistence lifecycle update timestamp
```

On initial insert:

```text
updated_at = recorded_at
```

Do not lose recorded-at semantics.

Document this mapping.

---

# 15. structured_value JSONB

P5-A deliberately uses typed domain structures.

Persist `structured_value` using explicit type-specific serialization.

Supported P5-A typed values:

```text
Problem
MedicationRecord
AllergyRecord
ProcedureRecord
Observation
InvestigationRecord
```

Do NOT persist arbitrary:

```text
dict[str, Any]
```

from callers.

Use a versioned canonical JSON shape, e.g.:

```json
{
  "schema_version": "p5b-v1",
  "value": { ...typed fields... }
}
```

or equivalent.

Deserializer must:

```text
validate schema version
dispatch by fact_type
reconstruct typed P5-A value
reject malformed/unsupported shapes
```

Do not silently accept unknown fields.

---

# 16. FactType Boundary

P5-A declares additional future fact categories:

```text
SYMPTOM
FAMILY_HISTORY
PERSONAL_HISTORY
REVIEW_OF_SYSTEMS
```

but P5-A does not yet define concrete typed ClinicalValue structures for them.

P5-B MUST NOT invent untyped JSON schemas for them.

Persistence operations should support only currently constructible P5-A ClinicalFact values.

Future P7 domain work may add typed values.

---

# 17. Provenance

Table:

```text
clinical_fact_provenance
id UUID PK
fact_id UUID FK clinical_facts(id)
source_type VARCHAR NOT NULL
source_id UUID NULL
source_ref TEXT NULL
extractor_type VARCHAR NULL
provider VARCHAR NULL
model_id VARCHAR NULL
model_version VARCHAR NULL
prompt_version VARCHAR NULL
schema_version VARCHAR NULL
confidence NUMERIC NULL
created_by UUID NULL
created_at TIMESTAMPTZ NOT NULL
metadata JSONB NULL
```

FK:

```text
created_by -> actors.id
```

Confidence named check:

```text
confidence IS NULL OR confidence BETWEEN 0 AND 1
```

Metadata remains reserved/internal.

No chain-of-thought.

---

# 18. Provenance Cardinality

P5-A `ClinicalFact` requires one `FactProvenance`.

P5-B may persist one canonical provenance row per fact initially.

Do NOT prevent future multiple provenance records unless the canonical schema requires one-to-one.

Preferred:

```text
index fact_id
no unique fact_id constraint
```

Repository maps the primary/current provenance for P5-A round-trip deterministically.

If multiple provenance rows are encountered unexpectedly, fail explicitly or use a documented deterministic rule rather than silently choosing arbitrary order.

---

# 19. Supersession

Persist:

```text
superseded_by_fact_id
```

as self-FK.

Rules:

```text
fact cannot supersede itself
replacement fact must exist
historical fact row/value/provenance remain preserved
```

No hard overwrite of clinician-confirmed facts.

Repository must not bypass P5-A `supersede_fact` trust rules.

P5-B persistence layer does not invent alternate supersession policy.

---

# 20. Frequently Queried Projections

Implement canonical relational projections:

```text
medications
allergies
observations
```

These are projections of canonical ClinicalFact data, not independent authoritative truth.

Each projection must link to:

```text
source_fact_id
```

Medication/allergy projections require patient_id as canonical schema states.

Observation may be patient- or encounter-scoped.

---

# 21. Medication Projection

Use canonical fields from `05_DATABASE_SCHEMA.md`.

Add FKs:

```text
patient_id -> patients.id
source_fact_id -> clinical_facts.id
```

Do not duplicate provenance.

Projection status/verification must match source fact/value.

---

# 22. Allergy Projection

Use canonical fields.

FKs:

```text
patient_id -> patients.id
source_fact_id -> clinical_facts.id
```

No independent truth updates.

---

# 23. Observation Projection

Use canonical fields.

FKs where present:

```text
patient_id -> patients.id
encounter_id -> encounters.id
source_fact_id -> clinical_facts.id
```

At least one numeric/text value must be present.

Do not treat units as optional semantics during interpretation; persistence must round-trip unit fields exactly.

---

# 24. Procedures / Investigations / Problems

Do NOT create new projection tables unless canonical DB schema explicitly requires them.

They persist canonically through:

```text
clinical_facts.structured_value
```

P5-B must round-trip them correctly.

---

# 25. Repository Boundaries

Create narrow persistence repositories/adapters, not giant generic CRUD.

Recommended boundaries:

```text
PatientRepository
EncounterRepository
ClinicalFactRepository
```

Provenance persistence may be owned internally by ClinicalFactRepository or a narrow provenance repository.

Repositories:

```text
receive caller AsyncSession
never commit
do not open hidden transactions
return P5-A domain objects
```

No FastAPI imports.

---

# 26. Patient Repository

Support only persistence needs required for P5-B verification:

```text
add/create
get
save/update lifecycle-safe fields
```

Round-trip:

```text
status
preferred_language
demographics
identifiers
timestamps
```

Do not add patient APIs.

---

# 27. Encounter Repository

Support:

```text
add
get
save transitioned encounter
```

Use DB `version` for optimistic concurrency groundwork if implemented.

Do not invent HTTP/service workflow.

If optimistic locking is introduced:

```text
stale write must fail deterministically
```

No hidden last-write-wins for encounter lifecycle.

---

# 28. ClinicalFact Repository

Support:

```text
add fact + provenance
get fact
persist explicit supersession result
```

Projection rows for medication/allergy/observation should be written atomically with canonical fact.

Canonical fact remains source of truth.

No independent projection write API.

---

# 29. Transaction Atomicity

Real PostgreSQL tests must prove:

```text
patient + demographics + identifiers atomic
clinical fact + provenance + applicable projection atomic
supersession update + replacement insert atomic
```

Injected failure should roll back the whole transaction.

Do not mock database transaction behavior.

---

# 30. Domain Round-Trip

Real PostgreSQL round-trip tests for:

```text
Patient
PatientDemographics
PatientIdentifier
Encounter
Problem fact
Medication fact
Allergy fact
Procedure fact
Observation fact
Investigation fact
FactProvenance
superseded fact linkage
```

Domain object reconstructed after fresh DB session must preserve canonical values.

---

# 31. Privacy

Never log:

```text
identifier values
clinical structured_value
source_text
demographics
medication names/doses
allergy substances/reactions
provenance source_ref
```

Repr safety from P5-A must remain intact.

No raw clinical payload in generic exceptions.

---

# 32. source_text

Canonical schema includes:

```text
source_text TEXT NULL
```

P5-A domain intentionally does not store raw extraction text in ClinicalFact.

Do NOT invent a public/domain source_text field.

Keep it NULL in P5-B unless a governed future ingestion service provides it.

Document this.

---

# 33. Patient Identifier Privacy Test

Use a synthetic marker identifier.

Verify marker absent from:

```text
repr
logs
generic errors
```

Persistence may contain the identifier because that is the purpose of the table.

Do not print it in CI output.

---

# 34. Consent PATIENT Subject

Do NOT activate PATIENT-subject consent management in P5-B.

Persistence existence of patients is not sufficient to define self-subject authorization.

Leave P4-C behavior unchanged.

P5-C/governed authorization step will bind patient ownership safely.

---

# 35. Runtime Module Registration

P5-B is persistence-only.

Do not expose patient/encounter HTTP routes.

Do not claim timeline capability.

You may add internal/public persistence contracts if needed, but do not register empty/fake runtime capabilities.

Prefer leaving default app modules unchanged unless an actual P5-B service capability is required.

Do not mark AC-P5-008 complete merely because repositories exist.

---

# 36. Alembic Metadata

Register P5-B ORM models explicitly.

Expected tables after migration:

```text
outbox_events
sessions
actors
actor_roles
consent_records
patients
patient_demographics
patient_identifiers
encounters
clinical_facts
clinical_fact_provenance
medications
allergies
observations
```

No later-phase tables.

---

# 37. Named Constraints

Use deterministic named constraints for:

```text
PatientStatus
EncounterType
EncounterStatus
FactType
VerificationState
ProvenanceSourceType
confidence range
age_years >= 0
encounter version > 0
completed_at lifecycle where safe
observation numeric/text presence
```

Do not duplicate application policy in brittle SQL if it would block future valid states.

---

# 38. Indexes

Implement canonical indexes from DB spec.

At minimum:

```text
patient_identifiers(system, value)       # non-unique baseline
encounters(patient_id)
encounters(session_id)
encounters(status, started_at)
encounters(institution_id)

clinical_facts(patient_id)
clinical_facts(encounter_id)
clinical_facts(patient_id, fact_type)
clinical_facts(verification_state)
clinical_facts(effective_at)

clinical_fact_provenance(fact_id)
clinical_fact_provenance(source_type, source_id)
clinical_fact_provenance(model_id, model_version)

observations(patient_id, observation_type, effective_at)
```

Avoid speculative indexes.

---

# 39. Deletion / Cascades

Clinical history must not disappear accidentally.

Avoid broad cascading deletes from patient -> encounters/facts.

Use restrictive/default FK behavior for clinical history.

Child technical rows such as demographics/identifiers may use carefully justified cascade from patient only if canonical privacy/lifecycle policy supports it; otherwise prefer restrictive behavior.

Do not implement deletion workflows in P5-B.

---

# 40. Migration Verification

Fresh PostgreSQL:

```text
alembic heads
alembic upgrade head
alembic current
alembic check
```

Expected head:

```text
p5b_0006
```

Then:

```text
downgrade p4c_0005
all P5-B tables absent
sessions/actors/actor_roles/consent/outbox remain
sessions.patient_id FK removed
upgrade head
P5-B tables restored
sessions.patient_id FK restored
alembic check clean
```

End at head.

---

# 41. PostgreSQL Tests

Mark real DB tests with:

```text
@pytest.mark.postgres
```

Zero relevant skips in CI.

Verify:

```text
FK integrity
check constraints
JSONB structured_value
JSONB metadata behavior
projection consistency
round-trip
atomic rollback
supersession persistence
pseudonymous encounter persistence
```

No SQLite.

---

# 42. No APIs

OpenAPI regression must prove no new:

```text
/api/v1/patients
/api/v1/encounters
/api/v1/clinical-facts
```

routes.

P5-C owns APIs.

---

# 43. No Timeline

Do NOT implement timeline query in P5-B.

AC-P5-007 remains open.

No chronological read model yet.

---

# 44. No Direct Consumer Integration

Do not wire intake/OCR/AI/FHIR modules directly to repositories.

P5-C will expose public patient-context interfaces.

AC-P5-008 remains open unless a real public service boundary is implemented.

---

# 45. Dependencies

Expected:

```text
NO new runtime dependency
NO new dev dependency
```

Use existing SQLAlchemy/Alembic/PostgreSQL stack.

Dependency files should remain unchanged.

---

# 46. Docker / Compose / Frontend

Expected unchanged:

```text
deployments/local/compose.yaml
infra/docker/backend.Dockerfile
apps/**
packages/ui/**
package.json
pnpm-lock.yaml
```

Regression gates still run.

---

# 47. CI

Keep six mandatory jobs:

```text
Backend quality
Frontend quality
Persistence integration
Docker and PostgreSQL
Playwright Chromium
Security scans
```

Update exact migration-head assertions to:

```text
p5b_0006
```

Persistence integration must execute P5-B PostgreSQL tests.

---

# 48. Documentation

Update only relevant:

```text
README.md
backend/README.md
REPOSITORY_TREE.txt
docs/03_REPOSITORY_STRUCTURE.md
docs/04_DOMAIN_MODEL.md if persistence reconciliation requires it
docs/05_DATABASE_SCHEMA.md
docs/implementation/38_PROGRESS_TRACKER.md
docs/codex/CODEX_PHASE_PROMPTS/P5_B_PERSISTENCE_MIGRATIONS.md
```

Record explicit decisions:

```text
demographics round-trip reconciliation
identifier uniqueness deferred
canonical_label derived mapping
recorded_at -> created_at mapping
no encounter single-consent FK
PATIENT consent activation deferred
```

---

# 49. Local Verification

From backend:

```text
uv lock --check
uv sync --locked --dev
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
uv run python -m compileall -q app tests
uv run pytest -m postgres
uv run alembic -c alembic.ini heads
uv run alembic -c alembic.ini current
uv run alembic -c alembic.ini check
```

From root:

```text
python scripts/quality_gate.py backend
python scripts/quality_gate.py frontend
```

Run migration downgrade/re-upgrade.

---

# 50. Diff Audit

Verify no dependency/frontend/Docker scope drift:

```text
git diff -- backend/pyproject.toml backend/uv.lock package.json pnpm-lock.yaml
git diff -- deployments/local/compose.yaml infra/docker/backend.Dockerfile
git diff --check
```

Inspect migration manually.

---

# 51. Progress Tracker

Before remote CI:

```text
P5-B = PARTIAL — REMOTE CI VERIFICATION PENDING
P5 = PARTIAL
```

After all six jobs green:

```text
P5-B = COMPLETE
P5 = PARTIAL
next = P5-C — Timeline / Provenance Services & APIs
```

Do NOT mark P5 complete.

---

# 52. Commit & Push

```text
git add <P5-B files only>
git commit -m "feat: establish P5-B patient persistence"
git push -u origin phase/p5-b-persistence-migrations
```

Do not merge.

---

# 53. Final Report

Return concise but complete sections:

```text
STATUS
SPECIFICATION DRIFT
BRANCH / GIT
SCOPE IMPLEMENTED
PERSISTENCE MODEL
DOMAIN/PERSISTENCE MAPPING
PATIENT PERSISTENCE
ENCOUNTER PERSISTENCE
CLINICAL FACT PERSISTENCE
PROVENANCE
PROJECTIONS
FK / CONSTRAINT MODEL
ATOMICITY
MIGRATION
MIGRATION VERIFICATION
FILES CHANGED
DEPENDENCIES
TESTS
VERIFICATION
CI
P5 ACCEPTANCE STATUS
ARCHITECTURE / GOVERNANCE CHECK
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

Recommended next:

```text
P5-C — Timeline / Provenance Services & APIs
```

---

# 54. Success Definition

P5-B is complete only when:

- all P5-A domain structures remain unchanged except explicitly reconciled persistence-required fields;
- patient, demographics, identifier, encounter, clinical fact, provenance, medication, allergy and observation tables exist;
- only those P5-B tables are added;
- sessions.patient_id gets its valid patients FK;
- pseudonymous encounter persistence still works;
- typed ClinicalFact JSONB serialization is explicit/versioned;
- unsupported future FactTypes are not persisted as arbitrary dicts;
- canonical label is deterministically derived;
- provenance round-trips;
- clinician-confirmed/supersession history remains preserved;
- projections are subordinate to canonical facts;
- patient identifier global uniqueness is not invented without namespace proof;
- demographics round-trip without silent loss;
- no single ambiguous encounter consent FK is introduced;
- PATIENT consent activation remains deferred;
- no patient/encounter/timeline API is added;
- no timeline query is implemented;
- Alembic head is `p5b_0006`;
- downgrade/re-upgrade/check pass;
- real PostgreSQL tests execute with zero relevant skips;
- no new dependency is added;
- all six CI jobs pass;
- P5-B is COMPLETE;
- P5 remains PARTIAL;
- branch is pushed but not merged.

Stop after P5-B.
