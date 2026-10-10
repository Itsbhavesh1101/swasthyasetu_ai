# Codex Phase Prompt — P3-A SQLAlchemy & Alembic Persistence Foundation

**Project:** SwasthyaSetu AI
**Prompt ID:** `SSAI-CODEX-P3-A`
**Phase unit:** P3-A — SQLAlchemy & Alembic Persistence Foundation
**Base branch:** `main`
**Expected base commit:** `2b3dcfed0c90d1bb1d3a7153d3b67cae52080091`
**Implementation branch:** `phase/p3-a-sqlalchemy-alembic-foundation`
**Scope:** PostgreSQL application connectivity, SQLAlchemy foundation, transaction/session helpers, Alembic baseline, DB-aware readiness, integration verification
**Expected final status:** `COMPLETE`, `PARTIAL`, `BLOCKED`, or `FAILED`

---

# 0. Mission

Begin P3 — Persistence, Migrations, Events, Outbox and Background Jobs.

P0–P2 are complete.

P3-A must implement only the relational persistence foundation required before feature modules start owning tables.

Implement:

```text
SQLAlchemy 2.x async engine foundation
Psycopg 3 PostgreSQL driver
per-application database runtime
async session factory
application-owned transaction helper
shared SQLAlchemy metadata/naming conventions
Alembic configuration
initial empty/foundation migration
clean-database -> Alembic head verification
database configuration validation
local Compose database connectivity
database-aware readiness when persistence is enabled
database runtime shutdown/disposal
PostgreSQL integration tests
CI migration/persistence verification
documentation
```

Do NOT implement yet:

```text
patient tables
session/identity tables
consent tables
encounter tables
clinical tables
outbox_events table
event envelope
event dispatcher
jobs table
job dispatcher
worker runtime
object storage port/adapter
pgvector
Redis/Valkey
Procrastinate
Celery
audit tables
business repositories
clinical/product APIs
```

P3-B owns typed events + transactional outbox.

P3-C owns job abstraction + worker smoke + object storage port/local adapter.

P4 and later own domain tables.

---

# 1. Mandatory Preflight

From repository root run:

```text
git rev-parse --show-toplevel
git branch --show-current
git status --short
git rev-parse HEAD
git remote -v
git log --oneline --decorate -10
```

Expected:

```text
branch: main
HEAD: 2b3dcfed0c90d1bb1d3a7153d3b67cae52080091
working tree: clean
```

Verify completed P2 exists:

```text
backend/app/shared/types/
backend/app/shared/errors/
backend/app/shared/modules/
backend/app/shared/capabilities/
backend/app/shared/feature_flags/
backend/app/shared/observability/
backend/app/config/
backend/app/main.py

docs/codex/CODEX_PHASE_PROMPTS/P2_A_SHARED_KERNEL_PRIMITIVES.md
docs/codex/CODEX_PHASE_PROMPTS/P2_B_MODULE_CAPABILITY_REGISTRY.md
docs/codex/CODEX_PHASE_PROMPTS/P2_C_OBSERVABILITY_FEATURE_FLAGS.md
```

Verify tracker says:

```text
P2 = COMPLETE
P3 = NOT STARTED
next = P3-A — SQLAlchemy & Alembic Persistence Foundation
```

If `main` differs from the expected SHA only because of the approved P2-C merge, inspect the intervening commits and use the actual clean `main` head.

If unrelated work exists, stop rather than overwrite it.

---

# 2. Create the Phase Branch

Create:

```text
git switch -c phase/p3-a-sqlalchemy-alembic-foundation
```

If it already exists:

1. inspect the history;
2. compare it to `main`;
3. preserve legitimate work;
4. continue only if clearly intended for P3-A.

Do not work directly on `main`.

Do not merge at completion.

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

docs/codex/CODEX_PHASE_PROMPTS/P3_A_SQLALCHEMY_ALEMBIC_FOUNDATION.md
```

Also inspect the actual current implementation:

```text
backend/app/main.py
backend/app/api/health.py
backend/app/config/settings.py
backend/app/config/sections.py
backend/app/shared/
backend/tests/
backend/pyproject.toml
backend/uv.lock

deployments/local/compose.yaml
deployments/local/.env.example
deployments/local/README.md

infra/docker/backend.Dockerfile
scripts/quality_gate.py
.github/workflows/ci.yml
```

Do not code from remembered assumptions.

---

# 4. Canonical P3 Requirements

P3 objective:

```text
Create platform persistence and asynchronous-work foundation before feature modules write data.
```

Relevant requirements include:

```text
FR-CORE-005 — typed contracts / persistence boundary discipline
FR-CORE-009 — configuration-driven behavior
FR-EXT-006 — extension/event foundation where applicable later in P3
NFR-MAINT-004
NFR-RES-006
database/audit/observability requirements applicable to infrastructure
```

P3-A directly targets:

```text
AC-P3-001 — SQLAlchemy 2.x persistence foundation configured
AC-P3-002 — Alembic upgrades a clean database to head
AC-P3-003 — database session/transaction helpers tested
```

P3-A must preserve:

```text
DB-P-001 PostgreSQL is transactional source of truth
DB-P-002 each table has one owning module
DB-P-003 modules do not directly write another module's tables
DB-P-004 every schema change uses Alembic
DB-P-007 timestamps are timezone-aware UTC
DB-P-008 internal primary keys are opaque UUIDs
DB-P-009 caches/vector stores never sole clinical truth
DB-P-010 binary medical files are not ordinary relational rows
```

No domain tables are created in P3-A.

---

# 5. P3 Phase Boundary

P3 is divided into:

```text
P3-A — SQLAlchemy/Alembic
P3-B — event envelope/outbox
P3-C — worker/job abstraction/object storage
```

P3-A is complete only for criteria:

```text
AC-P3-001
AC-P3-002
AC-P3-003
```

At the end:

```text
P3-A = COMPLETE
P3 = PARTIAL
```

Do not mark P3 complete.

---

# 6. Dependency Authorization

P3-A explicitly activates:

```text
SQLAlchemy 2.x
Alembic
Psycopg 3
```

R3 classification:

```text
SQLAlchemy     CORE_RUNTIME
Alembic        CORE_RUNTIME
Psycopg 3      CORE_RUNTIME
```

Preferred PostgreSQL driver:

```text
psycopg 3
```

Reason:

```text
modern PostgreSQL driver
native sync + async APIs
works with SQLAlchemy create_engine and create_async_engine
one driver can support async app runtime and migration tooling
```

Do not add:

```text
asyncpg
psycopg2
databases
SQLModel
Tortoise ORM
Django ORM
Prisma Python
database DI framework
```

unless the phase is explicitly blocked and dependency review is requested.

---

# 7. Version Selection

Before modifying `pyproject.toml`, verify current stable upstream releases, Python 3.12 support, security posture, and licenses.

At prompt preparation time the upstream stable landscape was approximately:

```text
SQLAlchemy current active series: 2.1.x
Alembic current stable series: 1.20.x
Psycopg current stable series: 3.3.x
```

Do not blindly assume these exact versions.

Re-check at implementation time.

Prefer current stable versions compatible with:

```text
Python 3.12
PostgreSQL 16
Alpine-based production container
existing FastAPI/Pydantic stack
strict mypy
```

Use bounded constraints in `pyproject.toml` and lock exact resolved versions in `uv.lock`.

Do not jump to a future major.

---

# 8. Driver Packaging

Prefer:

```text
psycopg[binary]
```

for the current containerized baseline unless implementation evidence shows a better reproducible option.

Reason:

```text
avoid adding system libpq/compiler packages to the runtime image
preserve small reproducible container
support sync + async psycopg APIs
```

Before adoption verify:

```text
Python 3.12 wheel availability
Alpine/musllinux compatibility
license
Trivy result
runtime import in backend container
```

If binary packaging does not work cleanly on the pinned Alpine image:

```text
do not install mutable OS packages casually
report the issue
choose the smallest reproducible supported alternative
```

Do not use `apk upgrade`.

---

# 9. License Review

Record exact licenses.

Expected upstream families:

```text
SQLAlchemy — MIT
Alembic — MIT
Psycopg — LGPL-3.0-only
```

Verify rather than assume.

The final report must name:

```text
package
resolved version
license
R3 classification
import/runtime location
reason
```

If license metadata materially differs, report it before claiming COMPLETE.

---

# 10. Persistence Placement

Use a generic platform persistence area.

Preferred:

```text
backend/app/shared/persistence/
```

A reasonable shape:

```text
backend/app/shared/persistence/
    __init__.py
    base.py
    runtime.py
    sessions.py
```

Exact split is implementation judgment.

This shared area may contain only generic persistence primitives.

Do not put:

```text
PatientORM
SessionORM
ConsentORM
EncounterORM
ClinicalFactORM
ProviderORM
ReferralORM
```

there.

Future ORM models live inside owning module infrastructure folders.

---

# 11. No Global Engine

Do not create a process-global mutable database engine imported everywhere.

Prohibited pattern:

```python
engine = create_async_engine(...)
SessionLocal = ...
```

at generic module import time for application-wide consumption.

Preferred:

```text
create_app()
    -> create DatabaseRuntime from Settings
    -> attach explicitly to application.state
    -> inject session factory/runtime later into use cases/dependencies
```

Tests must be able to construct multiple apps/runtimes without global collisions.

---

# 12. Database Runtime

Implement a small project-owned runtime object.

It should own:

```text
AsyncEngine
async_sessionmaker[AsyncSession]
database-enabled state
ping/readiness operation
dispose/shutdown operation
```

Potential conceptual interface:

```python
DatabaseRuntime
    engine
    session_factory
    ping()
    dispose()
```

Keep it small.

Do not turn it into a repository/service locator.

---

# 13. Async Engine

Use:

```text
sqlalchemy.ext.asyncio.create_async_engine
```

with Psycopg async support.

Use an explicit URL form such as:

```text
postgresql+psycopg://...
```

or:

```text
postgresql+psycopg_async://...
```

Choose one consistent supported form and document it.

Prefer one URL that can also be used by synchronous Alembic tooling when possible.

Do not rely on implicit driver selection.

---

# 14. Engine Safety Defaults

Use safe operational defaults.

At minimum consider:

```text
pool_pre_ping=True
SQL echo=False
bounded connection timeout
```

Do not log SQL by default.

Do not log database URLs.

Do not expose passwords.

Do not introduce excessive pool tuning without evidence.

---

# 15. Database Configuration

P2-A currently defines:

```text
DatabaseSettings:
  enabled: bool = False
  url: SecretStr | None = None
```

P3-A should evolve it minimally.

Requirements:

```text
enabled=False remains safe default for generic unit/test construction
enabled=True requires a database URL
URL must target PostgreSQL
Psycopg driver is explicit or normalized safely
URL remains secret-masked
connection timeout is bounded
```

Optional justified settings:

```text
connect_timeout_seconds
pool_timeout_seconds
```

Do not add dozens of knobs.

---

# 16. Nested Environment Variables

Support operationally safe nested environment overrides.

Add/enable:

```text
env_nested_delimiter="__"
```

if compatible with current Pydantic Settings design.

This should allow:

```text
SWASTHYASETU_DATABASE__ENABLED=true
SWASTHYASETU_DATABASE__URL=postgresql+psycopg://...
```

Preserve current JSON nested config support such as:

```text
SWASTHYASETU_FEATURES={...}
SWASTHYASETU_OBSERVABILITY={...}
```

Preserve all P1 flat environment variables.

Add tests.

---

# 17. Secret Handling

Database URL is sensitive.

It may contain:

```text
username
password
hostname
database name
query parameters
```

Rules:

```text
SecretStr or equivalent masking
no URL in normal repr/log output
no URL in exception response
no URL in telemetry attributes
no URL in health response
no URL in migration logs unless Alembic itself requires sanitized context
```

Tests must protect this.

---

# 18. Declarative Base

Create a SQLAlchemy 2.x declarative base.

Expected concept:

```python
class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=...)
```

Do not define application domain entities yet.

Do not create universal table mixins that incorrectly force fields on all future tables.

The database specification contains many table shapes with differing timestamp/version requirements.

---

# 19. Naming Convention

Provide deterministic constraint/index naming for Alembic.

Use a documented convention for:

```text
pk
fk
uq
ix
ck
```

Example intent:

```text
pk_<table>
fk_<table>_<column>_<referred_table>
uq_<table>_<column>
ix_<table>_<column>
ck_<table>_<name>
```

Exact format may vary.

For complex CHECK constraints, prefer explicit names.

Do not rely on database-generated anonymous constraint names.

Test the convention.

---

# 20. UUID and Time Policy

P3-A does not create domain columns, but persistence documentation/helpers must align with:

```text
UUID internal IDs
TIMESTAMPTZ / timezone-aware UTC
```

Do not introduce integer auto-increment as the default platform identity strategy.

Do not introduce naive datetime helpers.

Do not create universal ORM mixins unless justified by actual table needs.

---

# 21. Session Factory

Use SQLAlchemy async sessions.

Preferred concepts:

```text
AsyncSession
async_sessionmaker
expire_on_commit=False
```

Choose `autoflush` behavior deliberately.

Do not expose raw engine usage to every future use case.

The session factory is the basic injected persistence boundary.

---

# 22. Transaction Helper

Implement a small async transaction/session context helper.

Desired behavior:

```text
open session
begin transaction
yield session
commit on successful scope exit
rollback on exception
close session
re-raise original exception
```

Do not catch and suppress application exceptions.

Do not commit inside repository helper methods.

The transaction boundary belongs at application/use-case level.

---

# 23. Transaction Helper Naming

Use a clear name such as:

```text
transaction()
session_scope()
transactional_session()
```

Avoid ambiguous names such as:

```text
get_db()
```

if they obscure commit/rollback semantics.

Document exact behavior.

---

# 24. No Generic CRUD Repository

Do not add:

```text
BaseRepository
GenericRepository[T]
CRUDRepository
```

P3-A is persistence infrastructure only.

Future modules will define domain-specific repositories.

---

# 25. Alembic Location

Preferred layout:

```text
backend/alembic.ini
backend/migrations/
    env.py
    script.py.mako
    versions/
```

or an equivalent existing canonical backend-local layout.

Do not create a new top-level migrations directory.

---

# 26. Alembic Target Metadata

Configure Alembic with:

```text
Base.metadata
```

from the project-owned persistence base.

No domain model imports exist yet.

When future module ORM models are added, they must be explicitly imported/registered for autogeneration in their owning phases.

Do not create fake ORM models merely to make Alembic non-empty.

---

# 27. Initial Migration

Create one baseline migration.

Suggested meaning:

```text
P3-A persistence baseline
```

It should contain:

```text
revision metadata
upgrade()
downgrade()
```

P3-A must NOT create future domain tables.

An empty schema baseline is acceptable and preferred.

The expected clean database after P3-A may contain only Alembic's own version table.

Do not create a fake application table solely to prove migration functionality.

---

# 28. Migration Revision Discipline

Use deterministic, readable revision metadata.

The initial revision should have:

```text
down_revision = None
one migration head
clear message
```

Do not create multiple heads.

Do not edit a migration after it is merged in future phases.

P3-A branch may still correct its own unmerged migration if required.

---

# 29. Alembic URL Source

Do not hard-code credentials in:

```text
alembic.ini
env.py
migration scripts
```

Alembic must obtain the database URL from project settings/environment.

A safe command should work conceptually with:

```text
SWASTHYASETU_DATABASE__ENABLED=true
SWASTHYASETU_DATABASE__URL=...
uv run alembic -c alembic.ini upgrade head
```

Do not print the full URL.

---

# 30. Alembic Online/Offline Mode

Support normal online migration mode.

Offline SQL generation support is preferred if straightforward.

Do not overengineer it.

If offline mode is implemented:

```text
URL must still come from settings
credentials must not be emitted into generated SQL comments/logs
```

---

# 31. Migration Autogeneration

Configure autogenerate correctly.

Required:

```text
target_metadata = Base.metadata
compare_type=True or justified equivalent
deterministic naming convention
```

Do not enable experimental Alembic plugins without need.

Alembic 1.20 CHECK-constraint behavior should be treated conservatively.

Explicitly named CHECK constraints are preferred later.

---

# 32. Migration Quality Commands

P3-A verification should include:

```text
alembic heads
alembic current
alembic upgrade head
alembic check
```

Where safe also verify:

```text
alembic downgrade base
alembic upgrade head
```

The branch must end at `head`.

Do not leave the local/CI DB downgraded.

---

# 33. Clean Database Requirement

AC-P3-002 requires a genuinely clean database path.

Verification must start with a fresh ephemeral PostgreSQL database/volume.

Do not claim success based on a database already migrated by earlier manual runs.

Acceptable approach:

```text
fresh Compose volume
start PostgreSQL
confirm no application schema
run Alembic upgrade head
inspect alembic_version
```

---

# 34. Migration Atomicity

Use PostgreSQL transactional DDL behavior.

Do not configure autocommit globally.

Migration failures should fail the command and leave visible error state.

Do not swallow migration exceptions.

---

# 35. Local Compose Activation

P1-C already provides PostgreSQL.

P3-A should activate backend database connectivity in local Compose.

Add backend environment configuration such as:

```text
SWASTHYASETU_DATABASE__ENABLED=true
SWASTHYASETU_DATABASE__URL=postgresql+psycopg://<local synthetic credentials>@postgres:5432/<db>
```

Use Compose interpolation from:

```text
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
```

Do not hard-code production credentials.

---

# 36. Local Compose Secret Scope

The committed `.env.example` password remains:

```text
synthetic local-only
```

Do not claim it is production-safe.

Do not introduce production secret management in P3-A.

Do not add OpenBao/Secrets Manager.

---

# 37. Backend Docker Image

Update the backend image only as needed for P3-A.

The production image must contain:

```text
SQLAlchemy runtime
Psycopg runtime
Alembic runtime
app code
alembic.ini
migration scripts
```

Do not copy:

```text
tests
source materials
developer caches
.env
real secrets
```

The image remains non-root.

Do not add mutable OS upgrades.

---

# 38. Migration from Container

The same backend image should be capable of running migrations as an explicit deployment command.

Example concept:

```text
docker compose run --rm backend alembic -c /app/alembic.ini upgrade head
```

Exact path may vary.

Do not automatically run Alembic inside every application process startup.

Migration execution must be explicit.

This prevents multiple app replicas from racing schema migration.

---

# 39. No Auto-Migrate on API Startup

Prohibited:

```python
@app.startup
async def auto_upgrade():
    alembic upgrade head
```

or equivalent.

The application may verify connectivity/readiness.

Schema deployment is an explicit operational step.

---

# 40. Database Runtime in Application Composition

Extend `create_app()` narrowly.

Expected behavior:

```text
database disabled:
    no DatabaseRuntime required
    app continues
    readiness required dependencies remains empty

database enabled:
    DatabaseRuntime created/injected
    application.state.database available
    readiness treats database as required
```

Allow explicit runtime injection in tests if useful.

Do not add a generic DI container.

---

# 41. Database Lifecycle

Dispose the async engine cleanly at application shutdown.

Use FastAPI lifespan or a similarly supported lifecycle mechanism.

Requirements:

```text
no engine leak across repeated test app creation
shutdown does not expose credentials
custom injected runtime lifecycle ownership is clear
```

Document whether injected test runtimes are disposed by app or caller.

Prefer one simple ownership rule.

---

# 42. Readiness Semantics

P3-A is the first phase where PostgreSQL becomes a real application dependency when enabled.

Preserve the existing response structure:

```json
{
  "status": "...",
  "required": {},
  "optional": {}
}
```

When database is disabled:

```text
HTTP 200
status = ready
required = {}
```

When database is enabled and ping succeeds:

```text
HTTP 200
status = ready
required.database = ok
```

When database is enabled and ping fails:

```text
HTTP 503
status = not_ready (or equally clear documented value)
required.database = unavailable
```

Do not return database URL/error text.

---

# 43. Liveness Semantics

`/health/live` must remain process-only.

Database outage must NOT make liveness fail.

Expected:

```text
database unavailable
/health/live -> 200 {"status":"ok"}
/health/ready -> 503 ...
```

This prevents restart loops for an external DB outage.

---

# 44. Database Ping

Use a minimal bounded query such as:

```sql
SELECT 1
```

Do not run migrations from readiness.

Do not inspect application domain tables from readiness in P3-A.

Do not perform expensive queries.

---

# 45. Readiness Timeout

Database readiness must not hang indefinitely.

Use a bounded connection timeout from configuration/driver settings.

Do not wrap nested long retries in the HTTP readiness endpoint.

One bounded attempt is sufficient.

Orchestration can retry the endpoint externally.

---

# 46. Readiness Error Privacy

On DB failure:

```text
return required.database=unavailable
```

Do not return:

```text
hostname
port
username
database name
password
driver exception string
SQL
stack trace
```

Operational logs should also avoid the full connection URL.

A safe fixed message/error code is sufficient.

---

# 47. SQL Logging

Keep SQLAlchemy echo disabled.

Do not configure engine loggers at DEBUG by default.

Healthcare data will later flow through SQL parameters.

Never build a default logging posture that records SQL bind values.

---

# 48. Telemetry Boundary

P2-C instrumentation must remain privacy-safe.

Do NOT add:

```text
opentelemetry-instrumentation-sqlalchemy
SQL statement span attributes
DB URL span attributes
query parameter telemetry
```

during P3-A.

Database tracing can be governed later if needed.

P3-A only needs generic operational readiness.

---

# 49. Database Error Boundary

Do not introduce database-specific exceptions into public API contracts.

Infrastructure errors may remain internal or map later through generic dependency errors.

P3-A product endpoints do not use persistence yet.

Readiness is the only new operational HTTP behavior.

---

# 50. Integration Test Location

Use a clear test location.

Either:

```text
backend/tests/integration/
```

or existing root:

```text
tests/integration/
```

Prefer backend-local tests because current backend pytest configuration targets `backend/tests`.

Do not create a new top-level test framework.

---

# 51. PostgreSQL Integration Marker

Register a pytest marker such as:

```text
postgres
```

if useful.

Normal backend unit tests must not unexpectedly require local PostgreSQL.

Integration tests may skip when an explicit test DB URL is absent.

However CI must run them with a real PostgreSQL URL and prove they execute rather than all skip.

---

# 52. Test Database Environment

Use a distinct test-only environment variable where practical:

```text
SWASTHYASETU_TEST_DATABASE_URL
```

or reuse project DB settings in the dedicated integration job.

Do not point tests at an arbitrary developer database by default.

Do not run destructive cleanup against a non-test database.

---

# 53. Transaction Integration Test

AC-P3-003 must prove rollback semantics against PostgreSQL.

Use test-only DDL in an ephemeral CI/local test database if needed.

A valid strategy:

```text
create temporary/test-only probe table
begin transaction through project transaction helper
insert one probe row
raise synthetic exception
verify row is absent after rollback
drop probe table
```

Do not add the probe table to Alembic migrations.

Do not leave the probe table behind.

Use a clearly synthetic name.

---

# 54. Commit Integration Test

Also prove successful transaction scope commits.

Example:

```text
insert synthetic probe row in transaction helper
exit successfully
verify row is present
clean it up
```

This distinguishes commit and rollback behavior.

No patient-like data.

---

# 55. Session Closure Test

Verify sessions/connections are returned/closed after transaction helper use.

Do not rely on implementation-private SQLAlchemy internals excessively.

A subsequent query using the pool should work.

Engine disposal should complete cleanly.

---

# 56. Database Runtime Unit Tests

Add unit tests for:

```text
disabled DB config -> no runtime
enabled without URL -> validation error
invalid/non-Postgres URL -> validation error
URL secret masking
runtime constructed without immediate connection if possible
session factory type/behavior
```

No network required for these tests.

---

# 57. Naming Convention Tests

Test the metadata convention.

At minimum prove names are predictable for synthetic SQLAlchemy table constructs.

Do not create production tables.

Use neutral synthetic names.

---

# 58. Alembic Baseline Tests

Verify:

```text
exactly one head
baseline down_revision = None
upgrade on fresh DB succeeds
current revision == expected head
alembic check reports no pending operations
```

If downgrade verification is used:

```text
downgrade base succeeds
upgrade head succeeds again
```

---

# 59. No SQLite Substitution

Do not use SQLite as the main persistence integration test.

Canonical DB behavior is PostgreSQL.

SQLAlchemy unit tests may construct metadata without a database.

Transaction/migration integration must use PostgreSQL 16.

---

# 60. PostgreSQL Version

Retain the existing pinned PostgreSQL 16.12 image unless a current security/compatibility issue requires an approved update.

Do not switch database major version during P3-A without reason.

If image changes:

```text
document why
pin tag + digest
rerun Trivy
rerun full persistence tests
```

---

# 61. Database URL Driver

Prefer explicit:

```text
postgresql+psycopg://
```

This can support sync and async SQLAlchemy use depending on engine constructor.

Do not rely on `postgresql://` default-driver behavior because SQLAlchemy series may change defaults.

Explicit driver choice improves reproducibility.

---

# 62. Psycopg Pooling

Use SQLAlchemy's normal pool initially.

Do not add:

```text
psycopg_pool
external pooler
PgBouncer
```

in P3-A.

If future deployment needs them, they remain replaceable.

---

# 63. Isolation Level

Use PostgreSQL/SQLAlchemy default transaction isolation unless a canonical domain requirement demands otherwise.

Do not globally switch to SERIALIZABLE.

Future high-risk workflows can select isolation deliberately.

---

# 64. Statement Timeouts

Do not introduce aggressive global PostgreSQL statement timeout policy in P3-A unless already canonical.

Connection timeout is justified.

Query timeout policy can be tuned after real workloads exist.

---

# 65. Application Tables

P3-A migration must NOT create any of these:

```text
actors
actor_roles
sessions
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
clinical_intakes
safety_decisions
documents
providers
referrals
audit_events
outbox_events
jobs
feature_flags
```

These belong to later owning phases.

---

# 66. Outbox Boundary

Do not create:

```text
outbox_events
EventEnvelope
OutboxRepository
OutboxDispatcher
```

P3-B owns these.

P3-A's transaction helper should be capable of supporting same-transaction outbox writes later, but do not implement outbox behavior now.

---

# 67. Job Boundary

Do not add:

```text
JobDispatcher
JobRequest
JobStatus
Procrastinate
Celery
Dramatiq
Taskiq
jobs table
worker process
```

P3-C owns them.

---

# 68. Object Storage Boundary

Do not add:

```text
ObjectStoragePort
local filesystem object adapter
S3 adapter
SeaweedFS
MinIO
```

P3-C owns port/local adapter.

---

# 69. No pgvector

Do not enable:

```text
pgvector extension
vector column types
vector indexes
```

RAG has not started.

PostgreSQL remains plain relational baseline.

---

# 70. No Domain Repositories

Do not implement repositories in:

```text
patients
sessions
consent
providers
referrals
```

P3-A provides infrastructure only.

---

# 71. CI Strategy

P3-A adds a real persistence integration gate.

Keep existing CI jobs:

```text
Backend quality
Frontend quality
Docker and PostgreSQL
Playwright Chromium
Security scans
```

Add one focused job:

```text
Persistence integration
```

This makes migration/database failures visible independently.

Do not turn the normal backend unit job into a hidden DB-dependent job.

---

# 72. Persistence Integration CI Job

Suggested workflow:

```text
checkout
setup Python 3.12
setup uv
start PostgreSQL using the canonical local Compose service
wait healthy
set synthetic test DB URL
uv sync --locked --dev
alembic heads
alembic upgrade head
alembic current
alembic check
run PostgreSQL integration tests
optionally downgrade base + re-upgrade head
cleanup Compose volume
```

Use the same PostgreSQL image as local development.

No production secrets.

---

# 73. Persistence CI Credentials

Use synthetic CI-only values.

Do not add GitHub repository secrets for the local CI database.

Examples:

```text
POSTGRES_DB=swasthyasetu
POSTGRES_USER=swasthyasetu_dev
POSTGRES_PASSWORD=ci-only-synthetic-password
```

The exact existing values may be reused.

---

# 74. Persistence CI URL

When tests run from the GitHub runner host:

```text
host = 127.0.0.1
port = mapped POSTGRES_PORT
```

When running from a Compose backend container:

```text
host = postgres
port = 5432
```

Do not confuse these URLs.

Document both if necessary.

---

# 75. Docker/PostgreSQL CI Job

Update the existing `Docker and PostgreSQL` job so it also proves the containerized backend uses the DB when enabled.

Before starting the API:

```text
build backend image
run explicit Alembic upgrade head using the image
start backend
```

Then verify:

```text
/health/live -> 200
/health/ready -> 200
required.database == ok
```

Do not auto-migrate on backend startup.

---

# 76. DB Failure Readiness CI/Integration Test

Add a deterministic test that proves:

```text
DB configured/enabled
DB unavailable
liveness remains 200
readiness becomes 503
response exposes no credentials/driver exception
```

This can be done with an unreachable synthetic port rather than stopping shared CI infrastructure.

Bound timeout so the test is fast.

---

# 77. Existing Quality Gate

Update backend quality gate only where network-free checks make sense.

Good additions:

```text
alembic heads
migration import/syntax check
```

Do not add:

```text
alembic upgrade head
```

to the ordinary backend quality gate because it would make every unit/lint job require PostgreSQL.

DB-required checks belong in Persistence integration.

---

# 78. Backend Docker Build

The Docker build must remain reproducible.

After dependency changes:

```text
build image from pinned base
verify non-root user
verify psycopg import
verify SQLAlchemy import
verify Alembic CLI availability
run Trivy image scan through existing CI
```

Do not install compiler/libpq packages unless required and reviewed.

---

# 79. Container Migration Smoke

Run:

```text
docker compose ... run --rm backend alembic ... upgrade head
```

and verify:

```text
exit code 0
alembic_version contains head revision
```

This proves deployment image includes migration assets.

---

# 80. Local Developer Flow

Update local docs so a fresh developer can:

```text
copy local env
start PostgreSQL
run migration
start backend
verify live
verify ready
```

PowerShell examples must be valid.

Also document reset:

```text
docker compose down -v
```

only for the project-specific synthetic local volume.

---

# 81. Host Development Flow

Document a host-based backend workflow.

Example concept:

```text
start postgres via Compose
cd backend
set SWASTHYASETU_DATABASE__ENABLED=true
set SWASTHYASETU_DATABASE__URL=postgresql+psycopg://...@127.0.0.1:5432/...
uv run alembic -c alembic.ini upgrade head
uv run uvicorn app.main:app --reload
```

Use synthetic local credentials only.

---

# 82. Backend `.env.example`

Keep generic backend defaults safe.

Do not make a copied generic backend `.env` unexpectedly require PostgreSQL unless that is clearly documented.

It is acceptable to add commented/synthetic examples for nested DB settings.

Do not commit real credentials.

---

# 83. Observability Regression

P2-C behavior must remain.

Database changes must not:

```text
add SQL/query telemetry
add DB URL telemetry
break trace/log correlation
enable external telemetry
```

Existing observability tests remain green.

---

# 84. Feature Flag Regression

P2-C feature flags remain unchanged.

Do not use a feature flag to turn the database on/off.

Database activation is configuration/infrastructure, not product feature rollout.

---

# 85. Module Registry Regression

P2-B registry semantics remain unchanged.

Do not register the persistence foundation as a fake product module.

Persistence is platform infrastructure.

---

# 86. Error Contract Regression

P2-A public error envelope remains unchanged.

No new persistence debug endpoint.

No raw SQL exception response.

---

# 87. Health Contract Tests

Add/adjust tests for:

```text
DB disabled -> readiness 200 + no required dependency
DB enabled healthy -> readiness 200 + database=ok
DB enabled unavailable -> readiness 503 + database=unavailable
liveness unaffected by DB availability
```

Use the same stable response envelope shape.

---

# 88. Lifespan Tests

If app lifespan owns engine disposal, test it.

Verify:

```text
runtime dispose called once
normal shutdown succeeds
no exception leakage
```

Avoid brittle private FastAPI internals.

---

# 89. Database Runtime Tests

Test:

```text
runtime has AsyncEngine
runtime has async_sessionmaker
ping SELECT 1 works against Postgres
dispose works
```

Use a real PostgreSQL integration test for ping.

---

# 90. Transaction Helper Unit/Integration Split

Use unit tests for API semantics where possible.

Use PostgreSQL integration for actual commit/rollback.

Do not mock away AC-P3-003 entirely.

---

# 91. Migration Drift Check

`alembic check` must succeed after upgrade.

Because P3-A metadata intentionally contains no domain tables, it should report no new upgrade operations.

If it detects the Alembic version table itself, configure correctly rather than ignoring broad schema objects.

---

# 92. One Head Rule

CI must fail if multiple migration heads appear unexpectedly.

A simple verification can inspect:

```text
uv run alembic -c alembic.ini heads
```

and assert exactly one head.

Do not silently merge heads automatically.

---

# 93. Migration File Review

Generated migration files must be manually reviewed.

Do not commit autogenerated surprise tables/indexes.

P3-A baseline should be intentionally minimal.

---

# 94. Schema Ownership Future-Proofing

Document the rule:

```text
future module ORM models live under owning module infrastructure
shared persistence provides Base/runtime/session only
cross-module writes are prohibited
```

Do not create central `models.py` containing all future domains.

---

# 95. API DTO / ORM Separation

Preserve engineering standard:

```text
API DTO
Domain
Persistence
```

are separate concerns where representations differ.

P3-A adds no API DTOs for database entities.

---

# 96. Security Scan

Existing Gitleaks + Trivy must remain green after SQLAlchemy/Alembic/Psycopg additions.

If Trivy reports HIGH/CRITICAL:

```text
investigate package/base cause
use safe compatible version if available
do not broadly ignore
report blocker if unresolved
```

Do not weaken CI security policy.

---

# 97. Dependency Audit

After lock update inspect:

```text
backend/pyproject.toml
backend/uv.lock
```

Verify no unrelated runtime package was added.

Expected direct additions:

```text
SQLAlchemy
Alembic
psycopg with selected packaging extra
```

Expected transitive examples may include:

```text
greenlet
Mako
typing-related dependencies
psycopg-binary
```

Report actual transitives.

---

# 98. No Frontend Dependency Change

P3-A is backend persistence work.

Expected:

```text
package.json unchanged
pnpm-lock.yaml unchanged
```

Frontend quality gate still runs as regression.

---

# 99. Database Package Imports

Keep SQLAlchemy imports localized to:

```text
shared persistence foundation
future module infrastructure
Alembic config
integration tests
```

Do not import SQLAlchemy into:

```text
shared types
shared errors
shared security
feature flags
capability keys
domain contracts
frontend packages
```

---

# 100. Psycopg Imports

Prefer using Psycopg through SQLAlchemy.

Direct psycopg imports should be rare.

Do not create a parallel raw-psycopg persistence layer.

---

# 101. Raw SQL

Raw SQL in P3-A is acceptable only for:

```text
SELECT 1 readiness
synthetic integration-test probes
```

Use SQLAlchemy `text()` with static trusted SQL.

No untrusted string interpolation.

---

# 102. Pool Behavior Tests

Do not write fragile tests that depend on exact internal pool class unless configuration explicitly selects one.

Focus on:

```text
usable session
rollback
commit
dispose
bounded failure
```

---

# 103. Concurrency

Do not create one shared AsyncSession reused across requests.

SQLAlchemy session is not a global concurrent object.

Each transaction/use-case receives its own session.

Document this.

---

# 104. Request Dependency

Do not yet add a generic FastAPI `Depends(get_db)` to every route.

No product route consumes persistence in P3-A.

Future modules may define/inject session use at application boundaries.

---

# 105. Health Router Dependency Access

The health route may inspect:

```text
request.app.state.database
```

because health is an application/transport boundary.

Do not make domain code depend on FastAPI application state.

---

# 106. App State

If persistence is enabled, safe app state may include:

```text
application.state.database
```

Do not store:

```text
database URL
password
raw Settings secret
```

as separately exposed state values.

The runtime may internally own its engine.

---

# 107. Database Disabled Mode

Generic unit tests and foundation app construction must continue to work with:

```text
Settings(_env_file=None)
```

where DB defaults disabled.

This is important for test isolation.

P3-A does not make every Python unit test require Docker.

---

# 108. Local Compose Enabled Mode

The canonical local Compose backend SHOULD run with DB enabled after P3-A.

This makes local behavior representative of the persistence-enabled platform.

Readiness must therefore show DB health.

---

# 109. Schema Version Visibility

Do not expose Alembic revision over a public endpoint in P3-A.

Operational verification can use CLI/database inspection.

No `/version/database` endpoint.

---

# 110. Migration Locking

Do not invent a custom distributed migration lock.

Deployment discipline ensures one explicit migration command.

PostgreSQL/Alembic behavior is sufficient for this foundation.

---

# 111. Multi-Tenancy

Do not implement database-per-tenant/schema-per-tenant.

ADR-025 defers full multi-tenancy.

Use one PostgreSQL database baseline.

---

# 112. Separate PostgreSQL Schemas

Do not create per-module PostgreSQL schemas in P3-A.

Database specification currently recommends:

```text
one PostgreSQL database
application-enforced module ownership
clear table naming
```

Separate schemas may be reconsidered only with concrete value.

---

# 113. Timezone

Do not set a hidden application-local timezone.

Database/application timestamp policy is UTC.

Future TIMESTAMPTZ columns remain timezone-aware.

P3-A itself creates no timestamp columns.

---

# 114. Database Extension Management

Do not enable extensions.

No:

```text
pgcrypto
uuid-ossp
pgvector
citext
```

in P3-A.

Python/application UUID generation is already available.

Extensions require explicit future need.

---

# 115. Initial Migration Contents

Expected upgrade body may legitimately be:

```python
def upgrade() -> None:
    pass
```

and downgrade similarly.

If Alembic generated unnecessary content, remove it after review.

The purpose is to establish migration lineage and deployment verification, not fake schema.

---

# 116. Migration Filename

Use a readable filename.

Example:

```text
0001_persistence_baseline.py
```

Alembic revision identifier itself can be a stable short identifier.

Avoid random unreadable filename if project conventions can make it clearer.

Do not manually violate Alembic revision semantics.

---

# 117. Alembic Configuration Logging

Keep Alembic logs useful but avoid connection URL leakage.

Do not set SQLAlchemy engine echo.

Do not include secrets in migration print statements.

---

# 118. Local Cleanup

After integration verification clean only resources created by P3-A.

Safe:

```text
docker compose down -v
```

for the dedicated synthetic project environment when intentionally resetting it.

Never run:

```text
docker system prune
docker volume prune
```

globally.

---

# 119. Integration Test Safety Guard

If integration tests create/drop a synthetic probe table, guard them so they run only against explicitly configured test/local databases.

At minimum:

```text
require explicit test URL env
use clearly synthetic table name
cleanup in finally
```

Do not perform destructive operations against a URL implicitly loaded from production-like settings.

---

# 120. Integration Test Probe Naming

Use a neutral name such as:

```text
p3a_transaction_probe
```

Do not use:

```text
patients
sessions
clinical_facts
```

for test probes.

---

# 121. Persistence Test Data

Use only synthetic scalar values:

```text
1
"commit"
"rollback"
```

No health/person-like fixture data.

---

# 122. Quality Gate Commands

Run:

```text
cd backend
uv lock --check
uv sync --locked --dev
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
uv run python -m compileall -q app tests
uv run python -c "from app.main import app; assert app.title == 'SwasthyaSetu AI'"
```

Also run the root gates:

```text
python scripts/quality_gate.py backend
python scripts/quality_gate.py frontend
```

---

# 123. Migration Verification Commands

Against a fresh local test PostgreSQL:

```text
uv run alembic -c alembic.ini heads
uv run alembic -c alembic.ini upgrade head
uv run alembic -c alembic.ini current
uv run alembic -c alembic.ini check
```

If downgrade verification is implemented:

```text
uv run alembic -c alembic.ini downgrade base
uv run alembic -c alembic.ini upgrade head
```

Record exact results.

---

# 124. PostgreSQL Integration Tests

Run the explicit Postgres-marked tests with the test DB URL.

Example:

```text
uv run pytest -m postgres
```

or the actual project command.

Report:

```text
executed count
passed count
skipped count
```

A CI persistence run in which all Postgres tests skip is NOT a pass.

---

# 125. Docker Verification

Run:

```text
docker compose ... config
docker compose ... up -d postgres
docker compose ... build backend
docker compose ... run --rm backend alembic ... upgrade head
docker compose ... up -d backend
```

Verify:

```text
Postgres healthy
migration reaches head
backend non-root
/health/live 200
/health/ready 200
required.database == ok
```

Then clean up.

---

# 126. Failure Verification

Test unavailable DB behavior with a bounded unreachable endpoint.

Verify:

```text
/health/live = 200
/health/ready = 503
response has database=unavailable
no password/URL/exception message
```

Do not wait tens of seconds.

---

# 127. CI Jobs After P3-A

Expected mandatory branch jobs after this phase:

```text
Backend quality
Frontend quality
Persistence integration
Docker and PostgreSQL
Playwright Chromium
Security scans
```

All six must pass for P3-A COMPLETE.

---

# 128. CI Permissions

Preserve least privilege:

```text
contents: read
```

No package publish/deployment permission.

No DB secrets.

---

# 129. CI Concurrency

Preserve existing concurrency behavior.

Do not create excessive duplicated persistence jobs.

One dedicated integration job is enough.

---

# 130. CI Cleanup

Persistence/Docker jobs must clean Compose resources even after failure where practical.

Use:

```text
if: always()
```

for cleanup.

Do not leak project volumes across runner jobs.

---

# 131. CI Timeouts

Set bounded timeout for persistence integration.

A reasonable range:

```text
15–20 minutes
```

Do not create unbounded health loops.

---

# 132. Migration Command Location

Make commands work consistently from:

```text
backend/
```

Document repository-root alternatives if useful.

Avoid hidden dependence on one developer's cwd.

---

# 133. Windows Developer Compatibility

PowerShell examples should avoid Bash-only syntax.

Scripts added for migration checks should be cross-platform if expected for local use.

CI YAML may use Bash on Linux where appropriate.

---

# 134. No New Task Runner

Do not add Make, Task, Invoke, Poetry, Hatch, Nox, or another task runner solely for P3-A.

Use:

```text
uv
Python scripts
Alembic CLI
existing quality_gate.py
Docker Compose
```

---

# 135. Documentation Updates

Expected updates:

```text
README.md
backend/README.md
REPOSITORY_TREE.txt
deployments/local/README.md
backend/.env.example if useful
docs/implementation/38_PROGRESS_TRACKER.md
```

Add:

```text
backend/alembic.ini
backend/migrations/**
```

Do not change clinical/source-material documents.

---

# 136. Dependency/Research Register

If repository governance expects newly activated core components to be recorded in the third-party register, add a concise P3-A activation note for:

```text
SQLAlchemy
Alembic
Psycopg 3
```

Do not rewrite unrelated research evaluations.

If no existing convention requires it, the final dependency report is sufficient.

---

# 137. Decision Log

Do not create a new ADR just to restate:

```text
PostgreSQL source of truth
SQLAlchemy 2.x
Alembic
async engine
module-owned tables
```

These are already canonical.

Create an ADR only if a real new architecture decision is needed.

---

# 138. Progress Tracker Before CI

After implementation/local verification but before remote CI:

```text
P3-A = PARTIAL — REMOTE CI VERIFICATION PENDING
P3 = PARTIAL
```

Record:

```text
base SHA
branch
implementation SHA
direct dependencies
migration revision
local migration evidence
Postgres integration test evidence
remaining P3-B/P3-C
```

---

# 139. Progress Tracker After CI

Only after all six mandatory branch jobs are green:

```text
P3-A = COMPLETE
P3 = PARTIAL
```

Record:

```text
CI run ID
CI URL
head SHA
AC-P3-001 PASS
AC-P3-002 PASS
AC-P3-003 PASS
next = P3-B — Event Envelope & Transactional Outbox
```

Do not mark P3 complete.

---

# 140. P3 Acceptance Evaluation

Report all:

```text
AC-P3-001
AC-P3-002
AC-P3-003
AC-P3-004
AC-P3-005
AC-P3-006
AC-P3-007
AC-P3-008
AC-P3-009
AC-P3-010
```

Expected after successful P3-A:

```text
AC-P3-001 PASS
AC-P3-002 PASS
AC-P3-003 PASS
AC-P3-004 NOT YET IMPLEMENTED
AC-P3-005 NOT YET IMPLEMENTED
AC-P3-006 NOT YET IMPLEMENTED
AC-P3-007 NOT YET IMPLEMENTED
AC-P3-008 NOT YET IMPLEMENTED
AC-P3-009 NOT YET IMPLEMENTED
AC-P3-010 PASS by architecture/regression inspection if no violation exists
```

Use actual evidence rather than forcing the expected result.

---

# 141. Architecture Audit

Explicitly verify:

```text
PostgreSQL remains source of truth
no domain tables introduced
no central all-domain ORM model file
no cross-module table ownership
no global mutable engine/session
no SQLite substitution
no Redis/Valkey
no pgvector
no event/outbox implementation
no jobs/workers
no object storage
no auto-migrate on API startup
no SQL statement/body telemetry
no auth/clinical/AI work
P2 module/capability registry unchanged
P2 feature flag behavior unchanged
P2 observability privacy unchanged
```

---

# 142. Git Diff Audit

Run:

```text
git status --short
git diff --stat
git diff
git diff --check
```

Inspect every changed file.

Explicitly verify no committed:

```text
.env
database file
postgres volume data
credentials
migration test artifacts
SQL logs
pytest cache
Alembic temporary output
```

---

# 143. Commit Policy

After local checks pass:

```text
git add <P3-A files only>
git commit -m "feat: establish P3-A persistence foundation"
git push -u origin phase/p3-a-sqlalchemy-alembic-foundation
```

Do not merge.

Do not force-push.

---

# 144. Remote CI Verification

Verify the branch CI.

Required jobs:

```text
Backend quality
Frontend quality
Persistence integration
Docker and PostgreSQL
Playwright Chromium
Security scans
```

If GitHub CLI is available:

```text
gh run list --branch phase/p3-a-sqlalchemy-alembic-foundation
gh run watch <run-id> --exit-status
```

Do not claim success without observing it.

---

# 145. Closure Commit

If implementation commit is pushed before CI completes:

1. leave P3-A partial;
2. wait for CI;
3. fix real failures without weakening gates;
4. after green CI update tracker;
5. mark P3-A complete;
6. keep P3 partial;
7. record CI;
8. create a focused docs closure commit;
9. push same branch.

Do not merge.

---

# 146. If CI Fails

Do not:

```text
skip integration test
remove rollback test
disable Alembic check
mark persistence job continue-on-error
ignore DB health
weaken Trivy
```

Fix the actual issue.

If upstream dependency/security issues cannot be resolved, report BLOCKED.

---

# 147. Final Report Format

Return exactly the following sections.

## STATUS

One of:

```text
COMPLETE
PARTIAL
BLOCKED
FAILED
```

`COMPLETE` requires local persistence verification + all six mandatory CI jobs green.

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

Describe only P3-A.

## DEPENDENCIES

For each direct addition:

```text
package
constraint
resolved version
R3 classification
license
reason
import/runtime location
```

Also list relevant transitive additions.

## DATABASE CONFIGURATION

Report:

```text
DatabaseSettings fields
enabled default
URL validation
nested env support
secret masking
connection timeout
local Compose activation
```

## PERSISTENCE RUNTIME

Report:

```text
runtime type/location
AsyncEngine strategy
driver URL
session factory
pool behavior
ping behavior
dispose/lifecycle
app-state exposure
```

## SQLALCHEMY METADATA

Report:

```text
Base location
naming convention
UUID/time policy
domain model count
```

Expected:

```text
domain model count = 0
```

## TRANSACTION HELPER

Report:

```text
helper location
commit behavior
rollback behavior
session close behavior
integration evidence
```

## ALEMBIC

Report:

```text
alembic.ini location
migration directory
head revision
down_revision
target metadata
initial migration contents
autogenerate settings
```

## MIGRATION VERIFICATION

Report exact results:

```text
fresh database
alembic heads
upgrade head
current
alembic check
downgrade/upgrade if run
alembic_version inspection
```

## READINESS

Report:

```text
DB disabled behavior
DB healthy behavior
DB unavailable behavior
liveness behavior
credential/error privacy
```

## LOCAL POSTGRESQL INTEGRATION

Report:

```text
Postgres image
container health
driver connectivity
SELECT 1
transaction commit test
transaction rollback test
cleanup
```

## DOCKER VERIFICATION

Report:

```text
backend image build
non-root user
SQLAlchemy import
Psycopg import
Alembic CLI
container migration
live endpoint
ready endpoint
required.database status
cleanup
```

## FILES CHANGED

Group:

```text
persistence foundation
configuration
health/application composition
migrations
Docker/local deployment
tests
CI
dependencies
documentation
```

## TESTS

Report:

```text
new unit test count
new Postgres integration test count
total backend tests
integration executed/pass/skip counts
```

## VERIFICATION

Report:

```text
uv lock --check
uv sync --locked --dev
Ruff
format check
mypy
pytest
compile/import smoke
backend quality gate
frontend quality gate
git diff --check
frontend dependency diff
```

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

## P3 ACCEPTANCE STATUS

Report:

```text
AC-P3-001
AC-P3-002
AC-P3-003
AC-P3-004
AC-P3-005
AC-P3-006
AC-P3-007
AC-P3-008
AC-P3-009
AC-P3-010
```

Use:

```text
PASS
FAIL
BLOCKED
NOT APPLICABLE
NOT YET IMPLEMENTED
```

## ARCHITECTURE / GOVERNANCE CHECK

Explicitly report:

```text
PostgreSQL remains transactional source of truth: YES/NO
No domain tables introduced: YES/NO
No patient/session/consent/etc. ORM models introduced: YES/NO
No global mutable engine/session: YES/NO
No SQLite substitution: YES/NO
No auto-migration on API startup: YES/NO
No event/outbox implementation pulled forward: YES/NO
No jobs/workers pulled forward: YES/NO
No object storage pulled forward: YES/NO
No Redis/Valkey/pgvector added: YES/NO
No SQL/credential telemetry added: YES/NO
No auth/clinical/AI work introduced: YES/NO
P2-A contracts preserved: YES/NO
P2-B registry contracts preserved: YES/NO
P2-C feature/observability contracts preserved: YES/NO
```

## DEVIATIONS

List every deviation and reason.

## BLOCKERS / OPEN DECISIONS

Only genuine unresolved items.

## PROGRESS TRACKER

State:

```text
P3-A status
overall P3 status
CI evidence status
next recommended unit
```

## MERGE

State:

```text
MERGE PERFORMED: NO
```

## RECOMMENDED NEXT UNIT

If P3-A is complete:

```text
P3-B — Event Envelope & Transactional Outbox
```

Do not implement it.

---

# 148. Success Definition

P3-A is successful only when:

- SQLAlchemy 2.x is an approved locked core runtime dependency;
- Psycopg 3 provides PostgreSQL sync/async driver support;
- Alembic is an approved locked core runtime dependency;
- database config is typed, secret-masked, and validates enabled state;
- nested env configuration works without breaking P1/P2 variables;
- a per-application async database runtime exists;
- no global mutable engine/session exists;
- async session factory exists;
- transaction helper commits on success;
- transaction helper rolls back on exception;
- PostgreSQL integration proves commit and rollback;
- deterministic SQLAlchemy naming convention exists;
- Base metadata exists with zero domain tables;
- exactly one initial baseline Alembic revision exists;
- a fresh PostgreSQL database upgrades to head;
- Alembic reports no unexpected migration drift;
- migration execution is explicit, never automatic at API startup;
- backend image contains migration assets and can run Alembic;
- local Compose backend uses PostgreSQL when enabled;
- readiness reports database as required when enabled;
- DB outage makes readiness fail but not liveness;
- no credential/SQL content leaks into responses/logs/traces;
- P2 feature flags/module registry/observability remain compatible;
- no domain tables/outbox/jobs/object storage/Redis/pgvector are pulled forward;
- unit quality gates pass;
- PostgreSQL integration gate passes;
- Docker/local migration smoke passes;
- Trivy/Gitleaks pass;
- all six remote CI jobs pass;
- AC-P3-001 through AC-P3-003 pass;
- P3-A is marked COMPLETE;
- P3 remains PARTIAL;
- branch is pushed but not merged.

Stop after P3-A.
