# Codex Phase Prompt — P4-A Sessions

**Project:** SwasthyaSetu AI
**Prompt ID:** `SSAI-CODEX-P4-A`
**Phase unit:** P4-A — Sessions
**Base branch:** `main`
**Expected base commit:** `455436c8c863a6bcd5df286a81974e6811fca02a`
**Implementation branch:** `phase/p4-a-sessions`
**Commit message:** `feat: establish P4-A sessions`

---

# 0. Mission

Begin P4 — Identity, Sessions, Authorization Baseline and Consent.

P4 is split into:

```text
P4-A — sessions
P4-B — identity/authz baseline
P4-C — consent domain + APIs
```

Implement only P4-A.

Implement:

```text
Session domain types
pseudonymous-session creation
kiosk-session creation
secure opaque bearer session tokens
token hash at rest
typed expiry configuration
sessions PostgreSQL table
Alembic migration
session application service
session module manifest/public boundary
typed sessions capabilities
POST /api/v1/sessions
GET  /api/v1/sessions/{session_id}
POST /api/v1/sessions/{session_id}/close
server-side expiry enforcement
server-side close/state enforcement
session-token self-access
PostgreSQL/API integration tests
CI/migration regression
documentation
```

Do NOT implement:

```text
actors table
actor_roles table
RBAC
OIDC/OAuth
Keycloak/Authentik/ZITADEL
password login
MFA
consent_records
consent APIs
patient table
encounter table
frontend onboarding
JWT
cookies
Redis/Valkey
rate-limiter infrastructure
session refresh
recovery endpoint
```

P4-B owns identity/authz. P4-C owns consent.

---

# 1. Mandatory preflight

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
HEAD: 455436c8c863a6bcd5df286a81974e6811fca02a
working tree: clean
```

Verify merged P3 assets and prompts exist.

Verify tracker says:

```text
P3 = COMPLETE
P4 = NOT STARTED
next = P4-A — Sessions
```

If unrelated local changes exist, stop.

---

# 2. Create phase branch

```text
git switch -c phase/p4-a-sessions
```

Do not work on `main`.

Do not merge at completion.

---

# 3. Required reading

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
docs/codex/CODEX_PHASE_PROMPTS/P3_A_SQLALCHEMY_ALEMBIC_FOUNDATION.md
docs/codex/CODEX_PHASE_PROMPTS/P3_B_EVENT_OUTBOX.md
docs/codex/CODEX_PHASE_PROMPTS/P3_C_JOBS_OBJECT_STORAGE.md
```

Inspect actual code before editing:

```text
backend/app/main.py
backend/app/config/
backend/app/shared/security/actor.py
backend/app/shared/modules/
backend/app/shared/capabilities/
backend/app/shared/errors/
backend/app/shared/persistence/
backend/app/api/errors/
backend/app/api/v1/
backend/app/modules/sessions/
backend/tests/
backend/migrations/
.github/workflows/ci.yml
```

---

# 4. Governing requirements

Relevant product requirements:

```text
FR-IDENT-001 — pseudonymous session without name
FR-IDENT-002 — authenticated continuity (activation belongs P4-B)
FR-IDENT-003 — hospital/kiosk session
FR-IDENT-004 — explicit lifecycle and expiry
FR-IDENT-005 — no covert fingerprinting
FR-IDENT-006 — privacy-preserving recovery only where supported
FR-IDENT-007 — identifying information separated where practical

NFR-SEC-009 — high-entropy protected session tokens
NFR-SEC-014 — sensitive bodies not logged
PRIV-001 — data minimization
PRIV-003 — explicit transient retention rules
PRIV-006 — pseudonymous mode avoids unnecessary identity
PRIV-007 — sensitive logs exclude raw content
```

Direct P4-A acceptance:

```text
AC-P4-001 — pseudonymous creation requires no patient name
AC-P4-002 — session tokens are non-predictable
AC-P4-003 — expiry is enforced
AC-P4-004 — close/invalid-state behavior is tested
```

P4-B/P4-C own AC-P4-005 through AC-P4-010.

---

# 5. Canonical session model

Define canonical session types:

```text
PSEUDONYMOUS
AUTHENTICATED
KIOSK
CLINICIAN
ADMIN
RESEARCH
```

Define canonical statuses:

```text
ACTIVE
EXPIRED
CLOSED
REVOKED
```

P4-A may create only:

```text
PSEUDONYMOUS
KIOSK
```

Do not fake identity-bound sessions before P4-B.

---

# 6. Specification drift — active session token hash

Before implementation report:

```text
SPECIFICATION DRIFT DETECTED
```

Source A:

```text
docs/06_API_CONTRACTS.md section 9
NFR-SEC-009
```

requires creation of an opaque session token and subsequent authorized session access.

Source B:

```text
docs/05_DATABASE_SCHEMA.md section 5.3
```

contains `recovery_token_hash` but no verifier/hash for the active session bearer token.

Do NOT overload `recovery_token_hash`.

Reconcile the logical schema with an active token verifier:

```text
token_hash CHAR/VARCHAR(64) NOT NULL UNIQUE
```

for a SHA-256 hex digest.

Update:

```text
docs/05_DATABASE_SCHEMA.md
docs/06_API_CONTRACTS.md
```

Rules:

```text
raw token never stored
raw token returned only at creation
token_hash never exposed through API/domain DTO
recovery_token_hash remains distinct and NULL in P4-A
```

---

# 7. Token generation and protection

Use stdlib CSPRNG:

```python
secrets.token_urlsafe(32)
```

or an equivalent strategy using at least 32 random bytes / 256 bits.

Never use:

```text
random
timestamp token
sequential token
session UUID alone
```

Hash the high-entropy bearer token using stdlib SHA-256.

This token is not a human password; no password KDF dependency is required.

No new crypto/auth package.

If comparing hashes in memory use:

```python
hmac.compare_digest(...)
```

Do not log raw token or hash.

---

# 8. Token transport

Creation returns the token once.

Subsequent session self-access uses:

```text
Authorization: Bearer <session_token>
```

Do not accept the token in:

```text
query parameters
URL path
cookies
```

No frontend/localStorage work in P4-A.

Prefer:

```text
Cache-Control: no-store
```

on all session responses, mandatory for creation response.

---

# 9. Pseudonymous data minimization

P4-A create body contains only session-specific data such as:

```json
{
  "session_type": "PSEUDONYMOUS",
  "language_preference": "en"
}
```

It must not require or collect:

```text
name
email
phone
address
ABHA
DOB
IP-based identity
User-Agent fingerprint
device fingerprint
```

Use strict Pydantic request DTOs with:

```text
extra=forbid
```

A submitted `name` must not be silently accepted.

---

# 10. No fingerprinting

Do not persist:

```text
IP
User-Agent
canvas/browser fingerprint
device ID
hardware identifier
```

Pseudonymous continuity is provided by the explicit user-held session token.

---

# 11. Recovery boundary

P4-A does NOT implement a separate lost-token recovery flow.

Keep:

```text
recovery_token_hash = NULL
```

The active bearer token provides continuity while retained by the user.

Do not claim recovery after token loss.

---

# 12. Session TTL configuration

Add immutable typed settings, e.g. `SessionsSettings`.

Recommended foundation defaults:

```text
pseudonymous_ttl_minutes = 60
kiosk_ttl_minutes = 30
```

These are engineering foundation defaults, NOT final production policy.

Bound them to positive reasonable values.

Support nested env overrides:

```text
SWASTHYASETU_SESSIONS__PSEUDONYMOUS_TTL_MINUTES
SWASTHYASETU_SESSIONS__KIOSK_TTL_MINUTES
```

Do not add authenticated TTL until P4-B activates authenticated sessions.

---

# 13. Time invariants

All session timestamps are timezone-aware UTC:

```text
created_at
expires_at
closed_at
updated_at
```

Use deterministic clock injection.

Reject naive clocks before persistence/state mutation.

Normalize aware non-UTC values to UTC.

Do not use `datetime.utcnow()`.

---

# 14. Expiry semantics

On creation:

```text
created_at = now
expires_at = now + TTL(session_type)
status = ACTIVE
```

Client cannot choose expiry.

Boundary is exactly:

```text
now >= expires_at -> expired
```

An expired session must be rejected with:

```text
SESSION_EXPIRED
HTTP 401
```

for normal read/validation and close.

A background expiry sweep is NOT required.

Do not implement a mutation-on-read design that becomes ambiguous because exceptions roll back the transaction.

---

# 15. Close semantics

Only valid close transition:

```text
ACTIVE -> CLOSED
```

Set:

```text
closed_at = now
updated_at = now
```

For already:

```text
CLOSED
REVOKED
```

return:

```text
INVALID_STATE_TRANSITION
HTTP 409
```

For a time-expired session return:

```text
SESSION_EXPIRED
HTTP 401
```

Do not silently treat repeat close as success.

---

# 16. Wrong token and session enumeration

These cases must have the same safe authentication outcome:

```text
unknown session ID
wrong token
token from session A used on session B
```

Return:

```text
AUTHENTICATION_REQUIRED
HTTP 401
```

Do not expose which component was wrong.

---

# 17. Session IDs

Use existing:

```text
OpaqueId
```

Persist UUID primary key.

No sequential IDs.

---

# 18. Language preference

Optional, bounded, trimmed, future-compatible.

Accept examples like:

```text
en
hi
hi-Latn
```

Do not implement language behavior here.

---

# 19. Sessions module structure

Use:

```text
backend/app/modules/sessions/
```

Create only useful structure, e.g.:

```text
domain.py
contracts.py
application.py
infrastructure.py
api.py
public.py
__init__.py
README.md   # optional but useful
```

Do not create empty ceremony.

Remove `.gitkeep` when real files exist.

---

# 20. Domain layer

Framework-independent domain types:

```text
SessionType
SessionStatus
Session
```

No FastAPI or SQLAlchemy imports.

Public Session must not contain:

```text
raw token
token_hash
recovery_token_hash
```

---

# 21. Session ORM model

Create `sessions` only.

Canonical/reconciled columns:

```text
id UUID PK
session_type VARCHAR NOT NULL
actor_id UUID NULL
patient_id UUID NULL
language_preference VARCHAR NULL
status VARCHAR NOT NULL
token_hash VARCHAR/CHAR(64) NOT NULL
recovery_token_hash TEXT NULL
created_at TIMESTAMPTZ NOT NULL
expires_at TIMESTAMPTZ NOT NULL
closed_at TIMESTAMPTZ NULL
updated_at TIMESTAMPTZ NOT NULL
```

No unrelated columns.

---

# 22. Staged actor/patient linkage

P4-A runs before actors and patients exist.

Therefore:

```text
actor_id
patient_id
```

remain nullable UUID columns without foreign keys to nonexistent tables.

Do NOT create placeholder actors or patients.

P4-B/P5 may add valid constraints later.

P4-A-created sessions have both fields NULL.

---

# 23. Constraints and indexes

Use named constraints.

At minimum:

```text
valid canonical session_type
valid canonical status
expires_at > created_at
unique token_hash
```

Canonical indexes:

```text
(status, expires_at)
patient_id
actor_id
```

No duplicate indexes.

---

# 24. Alembic migration

Create:

```text
backend/migrations/versions/0003_sessions.py
```

Revision:

```text
p4a_0003
```

Parent:

```text
p3b_0002
```

Create ONLY:

```text
sessions
its constraints/indexes
```

No actors, roles, consent or patient tables.

Do not edit merged prior migrations.

---

# 25. Alembic metadata

Explicitly import/register the sessions ORM model for Alembic drift checks.

After P4-A metadata includes:

```text
outbox_events
sessions
```

and no other domain tables.

Do not introduce a giant central all-domain model file.

---

# 26. Migration verification

On a fresh PostgreSQL DB:

```text
alembic heads
alembic upgrade head
alembic current
alembic check
```

Expected single head:

```text
p4a_0003
```

Verify:

```text
downgrade p3b_0002
sessions absent
outbox_events remains
upgrade head
sessions restored
alembic check clean
```

End at head.

---

# 27. Repository

Create a narrow module-owned repository.

It may support only operations needed for:

```text
create
read
lock-for-close
```

Do not create a generic CRUD abstraction.

Repository receives caller session and never commits.

No cross-module table writes.

---

# 28. Application service

Implement a module-owned service with operations equivalent to:

```text
create_session
get_session
validate_session
close_session
```

Dependencies should be explicit:

```text
DatabaseRuntime | None
SessionsSettings
clock
token factory
repository
```

No global singleton.

If DB is unavailable:

```text
DEPENDENCY_UNAVAILABLE
HTTP 503
```

with a safe message.

---

# 29. Token verification

Bind bearer secret to exact session.

Use:

```text
session_id + token_hash
```

verification.

Never query/store by raw token.

Wrong/nonexistent session/token cases must fail uniformly.

---

# 30. Session service result privacy

If creation result contains raw token internally, ensure repr excludes it.

No token in normal logging.

No token/hash in domain/session view.

---

# 31. Module manifest

Create a real `ModuleManifest`.

Recommended:

```text
module_id = sessions
version = 1
api_prefixes = /sessions
configuration_keys = sessions
data_ownership = sessions
```

No feature flag.

No P4-B role permissions yet.

---

# 32. Session capability keys

Define centrally in sessions public contracts.

Recommended:

```text
sessions.create
sessions.read
sessions.close
sessions.validate
```

Expose narrow typed protocols, not infrastructure classes.

Do not create duplicate capability-key definitions in consumers.

---

# 33. Public boundary

`backend/app/modules/sessions/public.py` is the explicit module composition boundary.

It may expose:

```text
manifest
capability keys
public protocols
registration builder
```

Do not expose ORM/repository internals.

---

# 34. Default module composition

P4-A is the first real product module.

Integrate sessions through existing P2 module registry.

Do NOT bypass it by directly adding the router to central API code.

Do NOT use runtime discovery.

A valid pattern is:

```text
resolve settings/database
build explicit sessions registration
register with ModuleRegistry
finalize/seal
mount module router below /api/v1
```

Preserve testability for custom synthetic registrations.

---

# 35. `create_app()` behavior

Refactor narrowly if needed.

A clear acceptable rule:

```text
module_registrations=None -> explicit built-in modules (sessions)
module_registrations=(...) -> caller controls registrations
```

Avoid silent duplicate registration.

Preserve existing injection hooks:

```text
api_v1_routers
observability
feature_flags
database
```

---

# 36. Database-disabled default app

Even when database settings are disabled, the default product app should expose the session route.

Calling create should fail honestly with:

```text
503 DEPENDENCY_UNAVAILABLE
```

not 404 or 500.

This keeps API surface deterministic.

---

# 37. Session POST API

Endpoint:

```text
POST /api/v1/sessions
```

Allowed P4-A types:

```text
PSEUDONYMOUS
KIOSK
```

Response `201`:

```json
{
  "session_id": "uuid",
  "session_token": "opaque",
  "session_type": "PSEUDONYMOUS",
  "status": "ACTIVE",
  "expires_at": "ISO-8601"
}
```

Set:

```text
Cache-Control: no-store
```

No hash fields.

---

# 38. Session GET API

Endpoint:

```text
GET /api/v1/sessions/{session_id}
Authorization: Bearer <session_token>
```

Return safe metadata only:

```text
session_id
session_type
status
language_preference
created_at
expires_at
closed_at
```

No secrets.

Expired -> `SESSION_EXPIRED`.

Wrong/missing/cross-session token -> `AUTHENTICATION_REQUIRED`.

Closed/revoked must not behave ACTIVE.

---

# 39. Close API

Endpoint:

```text
POST /api/v1/sessions/{session_id}/close
Authorization: Bearer <session_token>
```

On valid active session:

```text
status = CLOSED
closed_at = now
```

Return typed safe metadata or 204.

Prefer typed metadata for client clarity.

Second close -> 409 `INVALID_STATE_TRANSITION`.

Expired -> 401 `SESSION_EXPIRED`.

---

# 40. Authorization header parsing

Accept only:

```text
Bearer <non-empty token>
```

Reject missing/wrong/malformed auth safely.

Do not echo Authorization value.

No raw token in error details.

---

# 41. Existing public error codes

Use existing codes only:

```text
AUTHENTICATION_REQUIRED
SESSION_EXPIRED
INVALID_STATE_TRANSITION
DEPENDENCY_UNAVAILABLE
VALIDATION_ERROR
```

No new public session codes unless unavoidable.

Use the canonical error envelope.

---

# 42. Session token is not identity authorization

A valid pseudonymous token proves only session possession.

It must NOT:

```text
set user roles
grant patient access
grant clinician access
grant consent
mark ActorContext authenticated
```

P4-B owns actor/authz.

---

# 43. No consent implication

Session creation does NOT equal consent.

Do not add:

```text
privacy_accepted
consent_granted
consent_scope
```

to sessions.

P4-C owns consent.

---

# 44. No patient/actor creation

Do not create:

```text
actors
patients
```

from P4-A session creation.

`actor_id` and `patient_id` remain NULL.

---

# 45. No JWT/cookies/Keycloak

Do not add:

```text
JWT libraries
cookie auth
Keycloak
Authentik
ZITADEL
OAuth/OIDC provider
password auth
OTP
magic links
```

Authenticated identity begins P4-B.

---

# 46. PostgreSQL source of truth

Session lifecycle is authoritative in PostgreSQL.

Do not use:

```text
in-memory session store
Redis
token-only stateless lifecycle
```

as canonical state.

Each authorized operation validates current DB state and expiry.

---

# 47. Close concurrency

Close is a guarded state transition.

Use row locking, preferably:

```text
SELECT ... FOR UPDATE
```

or an equivalent safe approach.

Where practical verify concurrent close does not double-succeed.

---

# 48. API DTO/ORM separation

Never return ORM objects through HTTP.

Map:

```text
ORM -> domain/application -> API DTO
```

Keep business rules out of route handlers.

---

# 49. Token privacy tests

Use a known synthetic marker token.

Verify marker absent from:

```text
logs
error responses
repr of internal creation result
database raw fields
```

Authorization header must remain excluded from structured logs.

---

# 50. Token-at-rest test

Real PostgreSQL test:

```text
create session
inspect DB row
raw token != token_hash
raw token absent from all persisted session text fields
token_hash = 64 hex chars if SHA-256 hex is used
```

Do not expose hash via HTTP.

---

# 51. Entropy evidence

Final evidence should state actual primitive:

```text
secrets.token_urlsafe(32)
```

or equivalent.

Tests may verify:

```text
decoded/random input >=32 bytes
generated tokens distinct across a sample
URL-safe/non-empty
```

Do not claim sample uniqueness itself proves cryptographic unpredictability.

---

# 52. Pseudonymous no-name tests

Creation without a name must succeed.

Submitting an extra `name` field should fail strict validation.

Do not silently discard identity fields.

---

# 53. Kiosk tests

KIOSK creation succeeds without identity.

Verify configured kiosk TTL.

No kiosk UI/device identity.

---

# 54. Identity-bound type tests

P4-A request must reject:

```text
AUTHENTICATED
CLINICIAN
ADMIN
RESEARCH
```

Do not create misleading identity-bound sessions before P4-B.

---

# 55. Expiry tests

Use deterministic clock.

Verify:

```text
now < expires_at -> valid
now == expires_at -> SESSION_EXPIRED
now > expires_at -> SESSION_EXPIRED
```

No sleeps.

---

# 56. Close tests

Verify:

```text
ACTIVE -> CLOSED
closed_at populated
updated_at updated
second close -> INVALID_STATE_TRANSITION
expired close -> SESSION_EXPIRED
```

---

# 57. Cross-session token test

Create A and B.

Use A's token on B.

Expected:

```text
401 AUTHENTICATION_REQUIRED
```

No B metadata.

This is only groundwork for AC-P4-010; do not mark full object authorization complete yet.

---

# 58. DB-disabled test

`create_app()` with database disabled:

```text
POST /api/v1/sessions -> 503 DEPENDENCY_UNAVAILABLE
```

Route must exist.

---

# 59. No list/refresh/recovery endpoints

Do not add:

```text
GET /api/v1/sessions
POST /sessions/refresh
POST /sessions/recover
```

P4-A contract only includes create/get/close.

---

# 60. Base metadata regression

After sessions ORM registration:

```text
Base.metadata.tables
```

must intentionally include:

```text
outbox_events
sessions
```

and no accidental domain tables.

Update P3 tests deliberately rather than deleting them.

---

# 61. Module registry regression

Add tests proving:

```text
sessions module registered in default composition
sessions capability keys resolve
registry remains sealed
router mounted below /api/v1
```

Preserve synthetic/custom module testability.

---

# 62. OpenAPI/API versioning

Endpoints must appear only under:

```text
/api/v1
```

No unversioned session route.

OpenAPI must not expose token hashes/recovery hashes/ORM fields.

---

# 63. Outbox events

Do NOT add session events unless a concrete P4-A requirement needs them.

No current consumer requires them.

Prefer no event work in this phase.

---

# 64. Jobs/object storage

Do not use P3-C jobs or object storage for sessions.

Regression only.

---

# 65. Retention distinction

Document:

```text
session token expiry != data deletion/retention
```

P4-A does not implement purge.

Do not invent production retention days.

---

# 66. Configuration tests

Test:

```text
default TTLs
nested env overrides
settings immutability
zero/negative rejected
upper bound enforced
```

Preserve all previous Settings behavior.

---

# 67. `.env.example`

If useful add:

```text
SWASTHYASETU_SESSIONS__PSEUDONYMOUS_TTL_MINUTES=60
SWASTHYASETU_SESSIONS__KIOSK_TTL_MINUTES=30
```

No secrets.

---

# 68. Documentation updates

Expected:

```text
README.md
backend/README.md
REPOSITORY_TREE.txt
docs/03_REPOSITORY_STRUCTURE.md
docs/05_DATABASE_SCHEMA.md
docs/06_API_CONTRACTS.md
docs/implementation/38_PROGRESS_TRACKER.md
docs/codex/CODEX_PHASE_PROMPTS/P4_A_SESSIONS.md
```

Possibly:

```text
backend/app/modules/sessions/README.md
docs/04_DOMAIN_MODEL.md
```

only for narrow clarification.

Do not modify source-material PDFs.

---

# 69. Dependencies

Expected:

```text
NO new runtime dependency
NO new dev dependency
```

Use stdlib:

```text
secrets
hashlib
hmac
```

and existing stack.

If a new auth/crypto package seems necessary, stop with:

```text
BLOCKED — DEPENDENCY REVIEW REQUIRED
```

---

# 70. Frontend

No frontend implementation change.

Expected:

```text
apps/**
packages/ui/**
package.json
pnpm-lock.yaml
```

unchanged.

Frontend quality still runs.

---

# 71. Docker/Compose

No new service.

No Keycloak/Redis.

Prefer no changes to:

```text
deployments/local/compose.yaml
infra/docker/backend.Dockerfile
```

unless factual packaging requires a minimal correction.

---

# 72. CI

Keep six mandatory jobs:

```text
Backend quality
Frontend quality
Persistence integration
Docker and PostgreSQL
Playwright Chromium
Security scans
```

No seventh job.

Update exact migration-head assertions from:

```text
p3b_0002
```

to:

```text
p4a_0003
```

where needed.

Persistence integration must execute new Postgres tests with zero relevant skips.

---

# 73. PostgreSQL test coverage

Add real DB tests for:

```text
insert/read
raw-token absence
hash storage
expiry
close
cross-session token
unique constraints
migration
```

Use only explicit test DB env.

No SQLite substitution.

---

# 74. HTTP integration coverage

Against real DB test:

```text
POST create 201
GET valid 200
GET missing token 401
GET wrong token 401
GET cross-session token 401
GET expired 401 SESSION_EXPIRED
close success
repeat close 409
pseudonymous no-name
extra name validation failure
secret fields absent
```

Use canonical error envelope.

---

# 75. Migration verification

Run:

```text
uv run alembic -c alembic.ini heads
uv run alembic -c alembic.ini upgrade head
uv run alembic -c alembic.ini current
uv run alembic -c alembic.ini check
```

Verify downgrade/re-upgrade across P4-A.

---

# 76. Local quality verification

From `backend/`:

```text
uv lock --check
uv sync --locked --dev
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
uv run python -m compileall -q app tests
```

From root:

```text
python scripts/quality_gate.py backend
python scripts/quality_gate.py frontend
```

Run PostgreSQL-marked suite explicitly.

---

# 77. Diff audits

Run:

```text
git diff -- backend/pyproject.toml backend/uv.lock package.json pnpm-lock.yaml
```

Expected empty.

Run:

```text
git diff -- deployments/local/compose.yaml infra/docker/backend.Dockerfile
```

Expected empty unless justified.

Inspect the migration manually: only `sessions`.

Run:

```text
git diff --check
```

---

# 78. Privacy/security audit

Verify:

```text
raw token never persisted
raw token never logged
Authorization never logged
token hash not returned
recovery hash not returned
no name required
no IP/User-Agent fingerprint persistence
no implicit consent
no identity roles
```

---

# 79. Architecture audit

Verify:

```text
sessions owns sessions table
no actors table
no actor_roles table
no consent table
no patient table
no JWT
no Keycloak
no Redis
no cookie auth
no frontend token storage
explicit module registry used
no runtime plugin discovery
P2/P3 contracts preserved
```

---

# 80. Progress tracker before CI

Before remote CI green:

```text
P4-A = PARTIAL — REMOTE CI VERIFICATION PENDING
P4 = PARTIAL
```

Record local acceptance evidence.

---

# 81. Progress tracker after CI

After all six jobs green:

```text
P4-A = COMPLETE
P4 = PARTIAL
```

Record:

```text
run ID
URL
head SHA
AC-P4-001 PASS
AC-P4-002 PASS
AC-P4-003 PASS
AC-P4-004 PASS
next = P4-B — Identity & Authorization Baseline
```

Do not mark P4 complete.

---

# 82. Expected P4 acceptance status

After successful P4-A:

```text
AC-P4-001 PASS
AC-P4-002 PASS
AC-P4-003 PASS
AC-P4-004 PASS
AC-P4-005 NOT YET IMPLEMENTED
AC-P4-006 NOT YET IMPLEMENTED
AC-P4-007 NOT YET IMPLEMENTED
AC-P4-008 NOT YET IMPLEMENTED
AC-P4-009 NOT YET IMPLEMENTED
AC-P4-010 NOT YET IMPLEMENTED
```

Cross-session token binding is groundwork, not full actor/object authorization.

---

# 83. Commit and push

After local verification:

```text
git add <P4-A files only>
git commit -m "feat: establish P4-A sessions"
git push -u origin phase/p4-a-sessions
```

Do not merge.

Do not force-push.

---

# 84. Remote CI

Verify the final branch SHA passes all six jobs.

Do not claim success without observed evidence.

If implementation is committed before CI closure:

```text
implementation commit
then focused tracker closure commit after green CI
```

is acceptable.

---

# 85. Final report format

Return exactly these sections.

## STATUS

```text
COMPLETE / PARTIAL / BLOCKED / FAILED
```

## SPECIFICATION DRIFT

Report:

```text
Detected
Source A
Source B
Conflict
Resolution
Files reconciled
```

## BRANCH / GIT

Report:

```text
base branch
base SHA
implementation branch
implementation SHA
closure SHA
remote SHA
main SHA
working-tree state
```

## SCOPE IMPLEMENTED

Only P4-A.

## SESSION DOMAIN

Report:

```text
Session location
SessionType values
SessionStatus values
supported create types
language behavior
timestamp invariants
```

## SESSION TOKEN

Report:

```text
CSPRNG primitive
entropy/random-byte count
transport
hash algorithm
storage column
raw-token persistence
raw-token logging
token return behavior
verification strategy
```

## SESSION CONFIGURATION

Report:

```text
settings type
pseudonymous TTL
kiosk TTL
env override behavior
production-policy disclaimer
```

## PERSISTENCE

Report:

```text
ORM
table
columns
constraints
indexes
actor_id/patient_id FK status
recovery hash behavior
```

## SESSION SERVICE

Report:

```text
create
read
validate
close
clock
database-disabled behavior
expiry/state behavior
```

## MODULE REGISTRATION / CAPABILITIES

Report:

```text
manifest
module id
provided capabilities
API prefix
data ownership
default composition
registry sealing
```

## HTTP API

Report:

```text
POST /api/v1/sessions
GET /api/v1/sessions/{id}
POST /api/v1/sessions/{id}/close
bearer behavior
cache headers
secret filtering
```

## EXPIRY / STATE

Report:

```text
now >= expires_at
ACTIVE -> CLOSED
repeat close
expired close
closed read behavior
```

## PRIVACY / SECURITY

Report:

```text
name requirement
identity extra-field behavior
fingerprinting
raw token storage
Authorization logging
token hash exposure
recovery
consent implication
```

## ALEMBIC / MIGRATION

Report:

```text
revision
parent
file
created tables
constraints/indexes
downgrade
metadata registration
```

## MIGRATION VERIFICATION

Report all fresh DB / downgrade / re-upgrade evidence.

## FILES CHANGED

Group by concern.

## DEPENDENCIES

Expected no changes.

## TESTS

Report:

```text
new unit
new Postgres
new HTTP integration
total backend
Postgres pass/skip
token privacy
expiry
close
cross-session token
pseudonymous no-name
DB-disabled behavior
```

## VERIFICATION

Report all local checks.

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
overall result
```

## P4 ACCEPTANCE STATUS

Report AC-P4-001 through AC-P4-010.

## ARCHITECTURE / GOVERNANCE CHECK

Explicitly report:

```text
Pseudonymous session requires no identity: YES/NO
Session token uses CSPRNG: YES/NO
Raw token never stored: YES/NO
Raw token absent from logs: YES/NO
PostgreSQL is session source of truth: YES/NO
Expiry enforced server-side: YES/NO
Close enforced server-side: YES/NO
Cross-session token fails closed: YES/NO
No fingerprinting: YES/NO
No actor/RBAC pulled forward: YES/NO
No consent pulled forward: YES/NO
No patient table pulled forward: YES/NO
No JWT/Keycloak/Redis added: YES/NO
Sessions uses module registry: YES/NO
No dynamic plugin discovery: YES/NO
P2 contracts preserved: YES/NO
P3 contracts preserved: YES/NO
```

## DEVIATIONS

All deviations.

## BLOCKERS / OPEN DECISIONS

Only genuine unresolved items.

Expected deferred non-blockers:

```text
authenticated identity provider -> P4-B
production TTL values -> security/privacy review
lost-token recovery -> future UX/privacy design if required
```

## PROGRESS TRACKER

```text
P4-A status
overall P4 status
CI evidence
next unit
```

## MERGE

```text
MERGE PERFORMED: NO
```

## RECOMMENDED NEXT UNIT

```text
P4-B — Identity & Authorization Baseline
```

Stop after P4-A.

---

# 86. Success definition

P4-A is successful only when:

- the sessions bounded context exists;
- canonical session types/statuses exist;
- pseudonymous creation requires no name;
- kiosk mode exists;
- identity-bound modes are not faked;
- token generation uses >=256-bit CSPRNG input;
- raw token is returned only on creation;
- raw token is never stored;
- active token hash is distinct from recovery hash;
- token hash is unique;
- bearer self-access is implemented;
- wrong/unknown/cross-session token fails closed;
- expiry uses `now >= expires_at`;
- close is a guarded transition;
- timestamps are aware UTC;
- TTL settings are typed/configurable;
- no device fingerprinting exists;
- PostgreSQL is source of truth;
- only `sessions` is added;
- no invalid actor/patient foreign keys are introduced;
- Alembic head is `p4a_0003`;
- downgrade/re-upgrade works;
- Alembic check is clean;
- Postgres and HTTP session tests execute;
- no P4-B/P4-C/P5/frontend work is pulled forward;
- no dependency is added;
- all six remote CI jobs pass;
- AC-P4-001 through AC-P4-004 pass;
- P4-A is COMPLETE;
- P4 remains PARTIAL;
- branch is pushed but not merged.

Stop after P4-A.
