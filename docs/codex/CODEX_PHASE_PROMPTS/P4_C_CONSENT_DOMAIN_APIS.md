# Codex Phase Prompt — P4-C Consent Domain & APIs

**Project:** SwasthyaSetu AI
**Prompt ID:** `SSAI-CODEX-P4-C`
**Phase unit:** P4-C — Consent Domain & APIs
**Base branch:** `main`
**Expected base commit:** `f81bac4d24c6073c7ffcf3c3ec7ceab58cdc150e`
**Implementation branch:** `phase/p4-c-consent-domain-apis`
**Commit message:** `feat: establish P4-C consent domain and APIs`

## 0. Mission

Complete P4 — Identity, Sessions, Authorization Baseline and Consent.

Merged state:

```text
P4-A — Sessions                         COMPLETE
P4-B — Identity & Authorization         COMPLETE
P4-C — Consent Domain & APIs            NEXT
P4 overall                              PARTIAL
```

Implement only P4-C:

```text
canonical ConsentRecord domain
ConsentPurpose
ConsentStatus
ConsentSubjectType
ConsentScope value semantics
versioned notice reference
consent persistence
revocation reason persistence
centralized consent check service
grant/revoke/list/read capabilities
exact-purpose + scope-subset consent checks
time-expiry checks
SESSION-subject authorization through sessions.validate
ACTOR-subject self-authorization through trusted ActorContext
safe PATIENT-subject deferral until P5
POST /api/v1/consents
POST /api/v1/consents/{consent_id}/revoke
GET /api/v1/consents with mandatory subject scope
atomic ConsentGranted / ConsentRevoked outbox events
explicit consent module manifest/capabilities
Alembic migration
real PostgreSQL tests
real HTTP integration tests
cross-subject/IDOR tests
revocation/check tests
referral-purpose separation tests
privacy/security regression
P4 completion audit
documentation
```

Do NOT implement:

```text
full ABDM consent workflow
ABHA linkage
FHIR Consent mapping
patient table/API
referral table/delivery
caregiver delegation
research workflow
external AI provider activation
privacy-notice frontend
consent UI
frontend session/consent flow
audit_events table
general audit module
Keycloak/OIDC/JWT
new login flow
notifications
Redis/Valkey
new broker
new dependency
```

P5 owns patients. P6 owns patient-facing notice/consent UI.

## 1. Mandatory preflight

Run:

```text
git rev-parse --show-toplevel
git branch --show-current
git status --short
git rev-parse HEAD
git remote -v
git log --oneline --decorate -12
```

Expected:

```text
branch: main
HEAD: f81bac4d24c6073c7ffcf3c3ec7ceab58cdc150e
working tree: clean
```

Verify:

```text
P4-A complete
P4-B complete
P4 partial
next = P4-C
Alembic head = p4b_0004
```

If unrelated local changes exist, stop.

## 2. Create branch

```text
git switch -c phase/p4-c-consent-domain-apis
```

Do not work on main. Do not merge.

## 3. Required reading

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
docs/codex/CODEX_PHASE_PROMPTS/P4_A_SESSIONS.md
docs/codex/CODEX_PHASE_PROMPTS/P4_B_IDENTITY_AUTHORIZATION_BASELINE.md
```

Inspect:

```text
backend/app/main.py
backend/app/modules/sessions/
backend/app/modules/identity/
backend/app/modules/consent/
backend/app/events/
backend/app/shared/security/
backend/app/shared/modules/
backend/app/shared/capabilities/
backend/app/shared/errors/
backend/app/shared/persistence/
backend/app/api/security/
backend/app/api/v1/
backend/tests/
backend/migrations/
.github/workflows/ci.yml
```

## 4. Governing requirements

Consent requirements:

```text
FR-CONSENT-001 privacy notice
FR-CONSENT-002 versioned consent
FR-CONSENT-003 separate referral consent
FR-CONSENT-004 external AI processing disclosure/consent
FR-CONSENT-005 ABDM consent
FR-CONSENT-006 research consent
FR-CONSENT-007 revocation
FR-CONSENT-008 minimal sharing
FR-CONSENT-009 consent auditability
```

P4-C closes:

```text
AC-P4-007 grant records version/scope/purpose
AC-P4-008 revocation represented and checked
AC-P4-009 referral-specific consent separate from general product consent
```

If successful:

```text
AC-P4-001 through AC-P4-010 = PASS
P4-C = COMPLETE
P4 = COMPLETE
next = P5-A — Patient / Encounter Domain Types & Entities
```

Do not implement P5.

## 5. Consent model

Canonical purposes:

```text
GENERAL_PRODUCT_USE
EXTERNAL_AI_PROCESSING
REFERRAL_SHARING
ABDM_EXCHANGE
RESEARCH_USE
CAREGIVER_ACCESS
```

Canonical statuses:

```text
GRANTED
REVOKED
EXPIRED
SUPERSEDED
```

Consent subject types:

```text
SESSION
ACTOR
PATIENT
```

`PATIENT` is represented structurally but MUST NOT be accepted for live HTTP management until P5.

## 6. Specification drift 01 — subject/actor references

`docs/04_DOMAIN_MODEL.md` uses:

```text
subject_ref
actor_ref
```

while DB/API use:

```text
subject_type
subject_id
actor_id
```

Report:

```text
SPECIFICATION DRIFT DETECTED
```

Reconcile canonical ConsentRecord to:

```text
subject_type
subject_id
actor_id?
```

Update domain documentation narrowly.

## 7. Specification drift 02 — revocation reason

The API requires:

```json
{"reason":"user_requested"}
```

but the DB schema has no dedicated field.

Do not discard it.

Add:

```text
revocation_reason VARCHAR(64) NULL
```

Use a bounded machine-readable code, not free text.

Update DB/domain docs.

## 8. Scope semantics

Create immutable validated scope values.

Requirements:

```text
lowercase machine-readable
bounded
non-empty collection
no duplicates
no wildcard
deterministic ordering
stored as JSONB array
```

Subset rule:

```text
granted {"a","b"} + required {"a"} -> valid
granted {"a","b"} + required {"c"} -> invalid
```

Purpose must match exactly.

General product consent must never satisfy referral consent.

## 9. Notice version

Record a bounded non-empty `notice_version`.

Do NOT invent legal notice text.

`privacy-v1` is an API example, not a claim of final approved legal content.

P6 will present approved notice UI.

## 10. Revocation reason

Validate a machine-readable code, recommended:

```text
^[a-z][a-z0-9_]{0,63}$
```

P4-C tests only need `user_requested`.

No free-text narrative.

## 11. ConsentRecord

Framework-independent immutable entity:

```text
consent_id
subject_type
subject_id
actor_id?
purpose
scope
notice_version
status
granted_at
revoked_at?
revocation_reason?
expires_at?
metadata?
created_at
updated_at
```

Rules:

```text
GRANTED -> no revoked_at/revocation_reason
REVOKED -> revoked_at required
expires_at, if present, > granted_at
timestamps aware UTC
metadata reserved/internal only
```

No tokens/credentials/clinical data.

## 12. Expiry

Public API does not accept `expires_at`.

Foundation grants may use NULL expiry.

Central checks MUST still treat:

```text
now >= expires_at
```

as invalid.

No background expiry sweep required.

## 13. Central consent check

Implement public capability:

```text
has_consent(...)
require_consent(...)
```

Match:

```text
subject type
subject ID
exact purpose
GRANTED status
not time-expired
required scopes subset
```

Missing/invalid consent:

```text
CONSENT_REQUIRED
```

Later modules must consume this capability rather than query the table directly.

## 14. Multiple records

Do NOT add unique constraint on:

```text
(subject_type, subject_id, purpose)
```

Future referral/context-specific grants may coexist.

A consent check succeeds if any valid matching GRANTED record covers required scopes.

Revocation affects one consent record only.

## 15. Grant lifecycle

On grant:

```text
status = GRANTED
granted_at = now
created_at = now
updated_at = now
revoked_at = NULL
revocation_reason = NULL
```

No implicit consent from session, actor, role, login, patient creation, or usage.

## 16. Revoke lifecycle

Use row locking.

Only:

```text
GRANTED -> REVOKED
```

Set:

```text
revoked_at
revocation_reason
updated_at
```

Repeat revoke / expired / superseded revoke:

```text
INVALID_STATE_TRANSITION
409
```

No silent success.

## 17. Time invariants

Service clock:

```text
reject naive
normalize aware non-UTC to UTC
```

No `datetime.utcnow()`.

Test naive rejection and offset normalization.

## 18. Persistence

Create SQLAlchemy model for:

```text
consent_records
```

Columns:

```text
id UUID PK
subject_type VARCHAR NOT NULL
subject_id UUID NOT NULL
actor_id UUID NULL
purpose VARCHAR NOT NULL
scope JSONB NOT NULL
notice_version VARCHAR NOT NULL
status VARCHAR NOT NULL
granted_at TIMESTAMPTZ NOT NULL
revoked_at TIMESTAMPTZ NULL
revocation_reason VARCHAR(64) NULL
expires_at TIMESTAMPTZ NULL
metadata JSONB NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

`actor_id` may FK to `actors.id`.

Do NOT add polymorphic FK for subject_id.

## 19. Constraints/indexes

Named constraints for:

```text
subject type
purpose
status
scope JSONB array
expiry after grant when non-null
```

Canonical indexes:

```text
(subject_type, subject_id, purpose, status)
actor_id
```

No speculative indexes.

## 20. Migration

Create:

```text
backend/migrations/versions/0005_consent.py
```

Revision:

```text
p4c_0005
```

Parent:

```text
p4b_0004
```

Create only:

```text
consent_records
```

No patient/referral/audit tables.

Downgrade removes only `consent_records`.

## 21. Repository

Narrow module-owned repository only.

Potential operations:

```text
create
get
get_for_update
list_for_subject
find_valid_matching
revoke
```

Repository never commits.

Writes consent_records only.

## 22. Consent service

Explicit per-app `ConsentService`.

Dependencies:

```text
DatabaseRuntime | None
ConsentRepository
OutboxRepository
clock
```

Operations:

```text
grant_consent
get_consent
list_consents
revoke_consent
has_consent
require_consent
```

No FastAPI imports.

## 23. Database-disabled behavior

Persistence-backed consent operations fail with:

```text
DEPENDENCY_UNAVAILABLE
```

Routes still exist.

## 24. Consent events

FR-CONSENT-009 / FR-AUDIT-003 require auditable grant/revocation history.

Enqueue through existing transactional outbox:

```text
ConsentGranted v1
ConsentRevoked v1
```

Same transaction as consent state.

Do not add broker or consumer.

Do not claim outbox is the final regulated audit store.

## 25. Event payload minimization

Allowed minimal fields:

```text
consent_id
subject_type
subject_id
purpose
scope
notice_version
status
revocation_reason? on revoke
```

No clinical content, names, tokens, credentials, arbitrary metadata.

Use:

```text
aggregate_type="consent"
aggregate_id=consent_id
```

`actor_ref` only from trusted opaque actor ID when present.

## 26. Outbox atomicity tests

Real PostgreSQL must prove:

```text
grant + ConsentGranted commit together
grant rollback -> neither persists
revoke + ConsentRevoked commit together
failed revoke -> no revoke event
```

No dispatching.

## 27. Module placement

Use:

```text
backend/app/modules/consent/
```

Suggested:

```text
domain.py
contracts.py
application.py
infrastructure.py
events.py
api.py
public.py
__init__.py
```

Remove `.gitkeep`.

## 28. Capabilities

Define centrally:

```text
consent.grant
consent.read
consent.list
consent.revoke
consent.check
```

Most important future dependency:

```text
consent.check
```

## 29. Manifest

```text
module_id = consent
version = 1
API prefix = /consents
data ownership = consent_records
events = ConsentGranted, ConsentRevoked
required capability = sessions.validate
```

No feature flag.

## 30. Default composition

Default app registers explicitly:

```text
identity
sessions
consent
```

No runtime scanning.

Custom explicit registrations remain deterministic.

## 31. Bearer parser refactor

P4-A currently owns a private bearer parser in `sessions.api`.

Do NOT import that private helper.

Preferred refactor:

```text
backend/app/api/security/bearer.py
```

Generic parser:

```text
exact Bearer <token>
malformed -> AUTHENTICATION_REQUIRED
never log/echo token
```

Update session API to use it.

P4-A tests remain green.

## 32. SESSION subject authorization

For `subject_type=SESSION`:

```text
Authorization: Bearer <session_token>
```

Resolve and call:

```text
sessions.validate(session_id=subject_id, session_token=token)
```

through the public capability.

Cross-session token:

```text
401 AUTHENTICATION_REQUIRED
```

Do not read sessions table directly.

## 33. ACTOR subject authorization

For `subject_type=ACTOR` use trusted:

```text
request.state.actor_context
```

Require:

```text
is_authenticated=True
actor_id present
actor_id == subject_id
```

Anonymous -> 401.

Authenticated cross-actor -> 403.

Do not consume client `X-Actor-ID`, `X-Role`, `X-MFA`.

## 34. PATIENT subject

Reject live P4-C HTTP management before persistence.

Do not guess actor-to-patient mapping.

P5 owns authoritative linkage.

## 35. Actor attribution

Client must not send `actor_id`.

Server derives it from trusted ActorContext when available.

Pseudonymous session consent may have actor_id NULL.

No fake actor creation.

## 36. POST /api/v1/consents

Strict DTO:

```json
{
  "subject_type":"SESSION",
  "subject_id":"uuid",
  "purpose":"GENERAL_PRODUCT_USE",
  "scope":["clinical_intake"],
  "notice_version":"privacy-v1"
}
```

Rules:

```text
extra=forbid
scope non-empty/unique
exact purpose enum
subject authorized first
PATIENT unavailable
```

Return 201 safe metadata.

Set `Cache-Control: no-store`.

## 37. POST /api/v1/consents/{id}/revoke

Strict body:

```json
{"reason":"user_requested"}
```

Flow:

```text
load consent
authorize exact subject
lock row
validate state/time
revoke
enqueue ConsentRevoked atomically
```

Repeat revoke -> 409.

## 38. GET /api/v1/consents

MUST require:

```text
subject_type
subject_id
```

Optional:

```text
purpose
status
```

Never list all records.

Authorize subject first.

Return deterministic ordering.

No public GET-by-id endpoint required.

## 39. Cross-subject tests

Mandatory:

```text
session A token -> A consent allowed
session A token -> B consent denied
actor A context -> actor A allowed
actor A context -> actor B denied
```

Test grant/list/revoke where applicable.

## 40. Referral separation

Mandatory AC-P4-009 proof:

```text
grant GENERAL_PRODUCT_USE
check REFERRAL_SHARING -> CONSENT_REQUIRED
grant REFERRAL_SHARING
check REFERRAL_SHARING -> PASS
```

No referral table.

## 41. Other purpose representation

Prove enums can represent:

```text
EXTERNAL_AI_PROCESSING
ABDM_EXCHANGE
RESEARCH_USE
CAREGIVER_ACCESS
```

Do not implement those workflows.

## 42. Privacy notice boundary

P4-C records notice version.

P6 is responsible for displaying approved notice content.

Do not claim frontend notice UX complete.

## 43. Minimum-sharing boundary

No wildcard consent scope.

Grant does not trigger sharing.

Later modules need:

```text
authorization
AND purpose-specific consent
AND minimum-necessary payload
```

## 44. No implicit consent

Session creation and actor authentication must not create consent rows.

Consent is explicit.

## 45. No direct cross-module table access

Consent must not import:

```text
sessions.infrastructure
identity.infrastructure
```

Use:

```text
sessions.validate
trusted ActorContext
```

## 46. API errors

Use existing codes:

```text
AUTHENTICATION_REQUIRED 401
AUTHORIZATION_DENIED 403
CONSENT_REQUIRED 403
RESOURCE_NOT_FOUND 404
INVALID_STATE_TRANSITION 409
VALIDATION_ERROR 422
DEPENDENCY_UNAVAILABLE 503
```

No new code expected.

## 47. Sensitive response caching

Consent success and errors:

```text
Cache-Control: no-store
```

Generalize the existing sensitive-route error helper to cover:

```text
/sessions
/consents
```

Preserve session behavior.

## 48. API strictness/privacy

Client cannot set:

```text
actor_id
status
granted_at
revoked_at
expires_at
metadata
```

No arbitrary metadata.

No free-text revocation narrative.

No Authorization logging.

## 49. Consent checker behavior

Tests:

```text
GRANTED exact purpose + scope -> valid
wrong purpose -> invalid
missing scope -> invalid
REVOKED -> invalid
time-expired -> invalid
SUPERSEDED -> invalid
```

`require_consent` raises `CONSENT_REQUIRED`.

## 50. Expiry tests

Use internal fixture/repository data.

Test:

```text
now < expires_at valid
now == expires_at invalid
now > expires_at invalid
```

No public expires_at request field.

## 51. JSONB test

Verify scope persists as JSONB array and round-trips canonically.

DB constraint rejects non-array JSONB.

## 52. DB constraints/FK tests

Verify invalid:

```text
subject_type
purpose
status
role FK actor_id
```

fails at DB level.

`actor_id=NULL` works for pseudonymous session consent.

## 53. Revocation concurrency

Use `SELECT ... FOR UPDATE`.

Where practical concurrent double revoke yields:

```text
one success
one INVALID_STATE_TRANSITION
```

## 54. No uniqueness by purpose

Do not add uniqueness on subject/purpose.

Multiple historical/context-specific records may coexist.

## 55. No public check endpoint

Do not add `/consents/check`.

`consent.check` is an internal capability.

## 56. No delete/update endpoint

No DELETE.

No generic PUT/PATCH.

Grant is new record; revoke is lifecycle operation.

## 57. No full ABDM/referral/research/caregiver implementation

Representation only.

No external service calls.

No patient/referral/audit tables.

## 58. Metadata/Audit boundary

Keep DB metadata internal/reserved.

No audit table.

Consent lifecycle + transactional outbox events support future audit integration.

OTel logs are not audit.

## 59. Framework independence

No FastAPI imports in:

```text
domain
contracts
application
events
```

Persistence may use SQLAlchemy.

## 60. Dependencies

Expected:

```text
NO new runtime dependency
NO new dev dependency
```

If one seems needed:

```text
BLOCKED — DEPENDENCY REVIEW REQUIRED
```

Do not add silently.

## 61. Frontend

No frontend code changes.

P6 owns consent UI.

## 62. Docker/Compose

No changes expected.

No new services.

## 63. CI

Keep six jobs:

```text
Backend quality
Frontend quality
Persistence integration
Docker and PostgreSQL
Playwright Chromium
Security scans
```

Update exact migration head:

```text
p4b_0004 -> p4c_0005
```

where needed.

## 64. Persistence integration

Verify fresh DB:

```text
single head p4c_0005
upgrade
alembic check
all Postgres regressions
P4-C tests
downgrade p4b_0004
consent_records absent
actors/actor_roles/sessions/outbox remain
re-upgrade
```

Zero relevant P4-C skips.

## 65. Schema inspection

Verify:

```text
consent_records exists
scope is JSONB
actor FK exists
indexes/checks exist
version = p4c_0005
```

Verify no patient/referral/audit table.

## 66. Unit tests

Add tests for:

```text
purposes/statuses/subject types
scope validation/immutability
notice version
revocation reason
domain invariants
UTC clock
checker subset semantics
wrong-purpose behavior
event payload minimization
manifest/capabilities
shared bearer parser regression
```

## 67. Real PostgreSQL tests

Add:

```text
grant persistence
scope JSONB
actor FK
constraints
revoke state/reason
valid check
revoked check
expired check
outbox atomicity
rollback atomicity
```

## 68. HTTP tests

Add:

```text
session grant/list/revoke
cross-session denial
actor self grant/list/revoke with trusted test context
cross-actor denial
PATIENT deferral
unscoped list validation
repeat revoke
no-store
DB-disabled behavior
secret filtering
```

## 69. Regression

P4-A session behavior must remain green.

P4-B identity/authz behavior must remain green.

P2/P3 contracts remain green.

## 70. Local verification

From backend:

```text
uv lock --check
uv sync --locked --dev
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
uv run python -m compileall -q app tests
```

Run import smoke.

## 71. PostgreSQL verification

```text
uv run alembic -c alembic.ini heads
uv run alembic -c alembic.ini upgrade head
uv run alembic -c alembic.ini current
uv run alembic -c alembic.ini check
uv run pytest -m postgres
```

## 72. Downgrade/re-upgrade

```text
head p4c_0005
downgrade p4b_0004
consent_records absent
actors/actor_roles/sessions/outbox remain
upgrade head
consent_records restored
alembic check clean
```

## 73. Root quality gates

```text
python scripts/quality_gate.py backend
python scripts/quality_gate.py frontend
```

## 74. Diff audits

Expected dependency diff empty:

```text
git diff -- backend/pyproject.toml backend/uv.lock package.json pnpm-lock.yaml
```

Expected Docker/Compose diff empty:

```text
git diff -- deployments/local/compose.yaml infra/docker/backend.Dockerfile
```

Inspect migration manually.

Run:

```text
git diff --check
```

## 75. Privacy/security audit

Verify:

```text
no bearer token in consent persistence/events/logs
no client actor_id
no arbitrary metadata
no free-text revocation
no unscoped listing
no cross-subject access
no wildcard scope
no implicit consent
no clinical content in events
```

## 76. Architecture audit

Verify:

```text
consent owns consent_records
session auth via sessions.validate
actor self auth via trusted ActorContext
central consent.check
no direct sessions/actors table access
no P5 patient work
no full ABDM
no referral implementation
no external AI invocation
no audit table
explicit module registration
no runtime discovery
```

## 77. Documentation updates

Expected:

```text
README.md
backend/README.md
REPOSITORY_TREE.txt
docs/03_REPOSITORY_STRUCTURE.md
docs/04_DOMAIN_MODEL.md
docs/05_DATABASE_SCHEMA.md
docs/06_API_CONTRACTS.md
docs/implementation/38_PROGRESS_TRACKER.md
docs/codex/CODEX_PHASE_PROMPTS/P4_C_CONSENT_DOMAIN_APIS.md
```

Optional concise module README.

Do not modify source-material PDFs.

## 78. Progress tracker before CI

```text
P4-C = PARTIAL — REMOTE CI VERIFICATION PENDING
P4 = PARTIAL
```

Record local evidence.

## 79. Progress tracker after CI

After all six jobs green:

```text
P4-C = COMPLETE
P4 = COMPLETE
```

Record:

```text
run ID
URL
head SHA
AC-P4-001 through AC-P4-010 PASS
next = P5-A — Patient / Encounter Domain Types & Entities
```

## 80. Commit/push

```text
git add <P4-C files only>
git commit -m "feat: establish P4-C consent domain and APIs"
git push -u origin phase/p4-c-consent-domain-apis
```

Do not merge. Do not force-push.

## 81. Remote CI

Verify all six mandatory jobs on final SHA.

Do not claim green without observed evidence.

## 82. Final report

Return exactly these sections:

### STATUS
### SPECIFICATION DRIFT
### BRANCH / GIT
### SCOPE IMPLEMENTED
### CONSENT DOMAIN
### CONSENT SUBJECT AUTHORIZATION
### CONSENT CHECK
### CONSENT LIFECYCLE
### CONSENT EVENTS
### PERSISTENCE
### MODULE REGISTRATION / CAPABILITIES
### HTTP API
### REFERRAL CONSENT SEPARATION
### PRIVACY / SECURITY
### ALEMBIC / MIGRATION
### MIGRATION VERIFICATION
### FILES CHANGED
### DEPENDENCIES
### TESTS
### VERIFICATION
### CI
### P4 FINAL ACCEPTANCE
### ARCHITECTURE / GOVERNANCE CHECK
### DEVIATIONS
### BLOCKERS / OPEN DECISIONS
### PROGRESS TRACKER
### MERGE
### RECOMMENDED NEXT UNIT

`MERGE` must state:

```text
MERGE PERFORMED: NO
```

Recommended next unit after success:

```text
P5-A — Patient / Encounter Domain Types & Entities
```

Do not implement it.

## 83. Success definition

P4-C is successful only when:

- canonical consent domain exists;
- subject/reference drift is reconciled;
- revocation reason is persisted;
- scope is typed/non-empty/non-wildcard;
- notice version is recorded;
- exact purpose and subset scope checks work;
- general consent never implies referral consent;
- revocation invalidates checks;
- time-expiry invalidates checks;
- SESSION subject auth uses sessions.validate;
- ACTOR subject auth uses trusted ActorContext;
- PATIENT subject is deferred to P5;
- list API is always subject-scoped;
- no client actor attribution exists;
- grant/revoke are PostgreSQL-authoritative;
- ConsentGranted/ConsentRevoked are atomically enqueued;
- only consent_records is added;
- no audit/patient/referral table is added;
- Alembic head becomes p4c_0005;
- downgrade/re-upgrade/check pass;
- real PostgreSQL and HTTP consent tests execute;
- no new dependency is added;
- all six CI jobs pass;
- AC-P4-007, AC-P4-008, AC-P4-009 pass;
- all AC-P4-001 through AC-P4-010 pass;
- P4-C is COMPLETE;
- P4 is COMPLETE;
- branch is pushed but not merged.

Stop after P4-C.
