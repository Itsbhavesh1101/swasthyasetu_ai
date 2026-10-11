# Codex Phase Prompt — P3-C Jobs, Worker Abstraction & Object Storage

**Project:** SwasthyaSetu AI
**Prompt ID:** `SSAI-CODEX-P3-C`
**Phase unit:** P3-C — Jobs, Worker Abstraction & Object Storage
**Base branch:** `main`
**Expected base commit:** `040888179a43af56328fde57954bf4cd4cdc0b3f`
**Implementation branch:** `phase/p3-c-jobs-object-storage`
**Scope:** Provider-neutral job contracts, deterministic in-process job/worker scaffold, object-storage port, controlled local filesystem adapter, P3 closure
**Expected final status:** `COMPLETE`, `PARTIAL`, `BLOCKED`, or `FAILED`

---

# 0. Mission

Complete P3 — Persistence, Migrations, Events, Outbox and Background Jobs.

P3-A already established PostgreSQL/SQLAlchemy/Alembic/session/transaction/readiness.
P3-B already established the versioned event envelope, PostgreSQL transactional outbox, manual dispatcher, retries/status, at-least-once delivery, and idempotent-consumer pattern.

P3-C must implement only:

```text
provider-neutral JobDispatcher contract
immutable JobRequest / JobHandle / JobStatus contracts
explicit process-local InProcessJobDispatcher
deterministic InProcessWorker
explicit job-handler registration
safe job failure state
deterministic worker/job smoke test
provider-neutral ObjectStoragePort
validated ObjectKey
controlled LocalFilesystemObjectStorage adapter
safe local object put/get/exists/delete behavior
path-traversal and symlink escape protections
tests/documentation
final P3 acceptance audit
```

P3-C must NOT implement:

```text
Procrastinate
Celery
Dramatiq
Taskiq
Redis / Valkey
NATS / Kafka / RabbitMQ
SQS / Pub/Sub
jobs SQL table
persistent job state
job retry framework
worker daemon/process loop
FastAPI BackgroundTasks queue
SeaweedFS
MinIO
S3/Boto3
cloud storage SDK
object metadata table
document upload API
quarantine/malware/MIME workflow
patient/session/consent/clinical tables
domain jobs
clinical logic
AI/ML/QML
```

This is the final P3 unit. If all AC-P3 criteria and CI pass:

```text
P3-C = COMPLETE
P3 = COMPLETE
next = P4-A — Sessions
```

Stop before P4.

---

# 1. Mandatory Preflight

From repository root:

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
HEAD: 040888179a43af56328fde57954bf4cd4cdc0b3f
working tree: clean
```

Verify merged P3-A/P3-B:

```text
backend/app/shared/persistence/
backend/app/events/envelope.py
backend/app/events/publisher.py
backend/app/events/outbox.py
backend/app/events/dispatcher.py
backend/migrations/versions/0001_persistence_baseline.py
backend/migrations/versions/0002_transactional_outbox.py
backend/tests/integration/test_postgres_persistence.py
backend/tests/integration/test_postgres_outbox.py

docs/codex/CODEX_PHASE_PROMPTS/P3_A_SQLALCHEMY_ALEMBIC_FOUNDATION.md
docs/codex/CODEX_PHASE_PROMPTS/P3_B_EVENT_OUTBOX.md
```

Verify tracker says:

```text
P3-A COMPLETE
P3-B COMPLETE
P3 PARTIAL
next P3-C — Jobs, Worker Abstraction & Object Storage
```

If `main` legitimately advanced only through the approved P3-B merge, inspect and report actual base SHA. If unrelated changes exist, stop.

Create:

```text
git switch -c phase/p3-c-jobs-object-storage
```

Do not work on `main`. Do not merge.

---

# 2. Required Reading

Read before editing:

```text
docs/00_PROJECT_MASTER_SPEC.md
docs/01_PRODUCT_REQUIREMENTS.md
docs/02_SYSTEM_ARCHITECTURE.md
docs/03_REPOSITORY_STRUCTURE.md
docs/05_DATABASE_SCHEMA.md
docs/29_ENGINEERING_STANDARDS.md
docs/34_MASTER_IMPLEMENTATION_PLAN.md

docs/implementation/35_PHASE_ACCEPTANCE_CRITERIA.md
docs/implementation/36_DEPENDENCY_MAP.md
docs/implementation/37_DECISION_LOG.md
docs/implementation/38_PROGRESS_TRACKER.md

docs/research/r3/R3_FINAL_TECHNOLOGY_STACK.md
docs/research/r3/R3_ARCHITECTURE_RECONCILIATION.md
docs/research/r3/R3_CODEX_DEPENDENCY_POLICY.md

docs/codex/CODEX_INSTRUCTIONS.md
docs/codex/CODEX_WORKFLOW.md
docs/codex/CODEX_CONTEXT_RULES.md

docs/codex/CODEX_PHASE_PROMPTS/P3_A_SQLALCHEMY_ALEMBIC_FOUNDATION.md
docs/codex/CODEX_PHASE_PROMPTS/P3_B_EVENT_OUTBOX.md
```

Inspect:

```text
backend/app/events/
backend/app/shared/
backend/app/adapters/
backend/app/config/
backend/tests/
backend/migrations/
backend/pyproject.toml
backend/uv.lock
workers/
data/
.gitignore
.github/workflows/ci.yml
scripts/quality_gate.py
deployments/local/
infra/docker/backend.Dockerfile
```

---

# 3. P3-C Acceptance

Directly target:

```text
AC-P3-007 — Job-dispatch abstraction exists.
AC-P3-008 — At least one deterministic worker/job smoke test passes.
AC-P3-009 — Object-storage port and test/local adapter exist.
AC-P3-010 — No domain module uses Redis/object storage as sole clinical source of truth.
```

Re-verify AC-P3-001 through AC-P3-006 from P3-A/P3-B.

P3 COMPLETE requires:

```text
AC-P3-001 ... AC-P3-010 = PASS
all mandatory remote CI jobs = SUCCESS
```

---

# 4. Durable Job Backend Is Explicitly Deferred

Canonical R3 order:

```text
InProcessJobDispatcher
        |
        | only when durability is required
        v
PostgreSQL-native durable adapter
(Procrastinate preferred spike target)
        |
        | only if requirements outgrow it
        v
Celery / later messaging
```

P3-C acceptance does not require durability.

Therefore:

```text
NO Procrastinate dependency
NO Celery dependency
NO Redis/Valkey
NO jobs table
NO worker service/container
```

If Codex believes a durable dependency is unavoidable:

```text
STATUS: BLOCKED — DEPENDENCY / ARCHITECTURE REVIEW REQUIRED
```

Do not install it silently.

---

# 5. Migration Boundary

`docs/05_DATABASE_SCHEMA.md` makes the `jobs` table conditional on a persistent job backend.

P3-C uses an in-process/local scaffold, so:

```text
DO NOT create jobs table
DO NOT create new Alembic revision
DO NOT modify p3a_0001 or p3b_0002
```

Expected Alembic head remains:

```text
p3b_0002
```

Run migration regression checks, but no schema change is expected.

---

# 6. Job Package Placement

Use:

```text
backend/app/jobs/
```

A reasonable structure:

```text
backend/app/jobs/
    __init__.py
    contracts.py
    in_process.py
    worker.py
```

Exact split may be smaller if cohesive.

`workers/` remains reserved for future standalone process bootstrapping. Do not create a fake standalone worker process backed by process-local memory; it would not share state with the API process.

---

# 7. JobType

Implement immutable validated `JobType`.

Use neutral test values:

```text
synthetic.echo
example.process
```

Requirements:

```text
non-empty
bounded
machine-readable
stable
hashable
```

A lowercase dotted grammar is appropriate.

Do not activate real OCR/referral/FHIR/etc. job types.

---

# 8. JobRequest

Implement immutable `JobRequest`.

Recommended fields:

```text
job_id: OpaqueId
job_type: JobType
payload: JSON-compatible mapping
correlation_id: optional bounded opaque string
created_at: timezone-aware UTC
scheduled_at: timezone-aware UTC
```

Convenience constructor may generate:

```text
job_id
created_at
scheduled_at=created_at
```

Caller-supplied deterministic values must be supported for tests.

Reject naive datetimes.

---

# 9. Job Payload Privacy

Payload must be:

```text
JSON-compatible
copy-protected / recursively immutable where practical
excluded from repr
not pickle
not arbitrary objects
```

Caller mutation after construction/enqueue must not mutate queued content.

Use synthetic payloads only.

Job payload is work input/reference metadata, not canonical clinical truth.

Do not log it.

---

# 10. JobStatus

Define explicit enum aligned with architecture:

```text
QUEUED
RUNNING
SUCCEEDED
FAILED
CANCELLED
NEEDS_REVIEW
```

P3-C worker automatically exercises only:

```text
QUEUED
RUNNING
SUCCEEDED
FAILED
```

Do not invent clinical meaning for other states.

---

# 11. JobHandle

Implement immutable payload-free `JobHandle`.

Preferred minimal field:

```text
job_id
```

Do not include:

```text
payload
handler
exception
stack trace
```

---

# 12. JobDispatcher Port

Framework-independent protocol:

```python
class JobDispatcher(Protocol):
    async def enqueue(self, job: JobRequest) -> JobHandle:
        ...
```

No imports/references to:

```text
FastAPI
SQLAlchemy
Procrastinate
Celery
Redis
Valkey
broker SDKs
```

---

# 13. Job Handler

Define explicit async handler contract:

```python
JobHandler = Callable[[JobRequest], Awaitable[None]]
```

or equivalent Protocol.

One handler per job type is sufficient.

Registration is explicit and immutable after worker construction.

No package scanning, dynamic imports, entry points, or runtime plugin discovery.

---

# 14. Process-Local Backend

Build a small in-memory backend shared by:

```text
InProcessJobDispatcher
InProcessWorker
```

Allowed standard-library primitives:

```text
deque/list
dict
asyncio.Lock
```

Properties:

```text
non-durable
process-local
lost on restart
not shared across processes
not source of truth
local/test scaffolding only
```

Document prominently.

---

# 15. InProcessJobDispatcher

Behavior:

```text
enqueue JobRequest
store process-locally
set QUEUED
return JobHandle
```

Critical:

```text
enqueue MUST NOT execute handler
enqueue MUST NOT block on long-running work
```

Duplicate `job_id` must fail deterministically.

No persistent state.

---

# 16. InProcessWorker

Implement deterministic worker object:

```python
await worker.run_once()
```

Behavior:

```text
choose first due QUEUED job
mark RUNNING
resolve explicit handler
await handler
mark SUCCEEDED on success
mark FAILED on missing handler / handler exception
```

No loop/daemon/background task.

No auto-start from FastAPI.

---

# 17. Scheduling

If:

```text
scheduled_at > now
```

worker must not run job early.

Inject a deterministic clock:

```python
clock: Callable[[], datetime] = utc_now
```

No sleeping in tests.

FIFO is sufficient among due jobs.

Do not promise distributed ordering.

---

# 18. Worker Failure Safety

Missing handler:

```text
FAILED
safe code such as JOB_HANDLER_NOT_FOUND
```

Handler exception:

```text
FAILED
safe code such as JOB_EXECUTION_FAILED
```

Do not retain:

```text
raw exception message
stack trace
payload
```

in state/repr/logging.

Worker must remain usable for later jobs.

No retry framework in P3-C.

---

# 19. Job State Inspection

In-process adapter may expose an immutable test/local snapshot containing safe fields such as:

```text
job_id
job_type
status
error_code
created_at
scheduled_at
started_at
completed_at
```

Exclude payload.

Unknown handle should fail deterministically.

This inspection API need not be part of the minimal `JobDispatcher` Protocol.

---

# 20. Deterministic Worker Smoke

AC-P3-008 required test:

```text
create backend
create dispatcher
create worker with synthetic handler
enqueue synthetic job
status = QUEUED
run_once
handler receives request
synthetic side effect = 1
status = SUCCEEDED
```

No network, PostgreSQL, filesystem, sleep, or external service required.

Also test:

```text
enqueue itself does not execute handler
```

---

# 21. Additional Job Tests

Cover:

```text
JobType validation
JobRequest immutability
payload mutation isolation
payload not in repr
naive timestamps rejected
UTC normalization
duplicate job ID rejected
future job not executed early
missing handler -> FAILED safe code
handler exception -> FAILED safe code
raw exception marker absent
worker later processes next job
run_once with no work is safe
correlation_id reaches handler unchanged
```

Use synthetic marker:

```text
synthetic-private-worker-detail
```

---

# 22. No Job Persistence / No Exactly-Once Claim

Do not persist queue/status in:

```text
PostgreSQL
files
object storage
Redis
SQLite
outbox
```

Do not claim exactly-once execution.

Local duplicate-ID checks are not a distributed guarantee.

---

# 23. Event/Job Separation

Do not reuse `EventEnvelope` as `JobRequest`.

Remember:

```text
event = fact that occurred
job   = instruction to perform work
```

Do not route outbox dispatch automatically through the job system.

Do not change P3-B dispatcher behavior.

---

# 24. Object Storage Architecture

P3-C implements:

```text
ObjectStoragePort
LocalFilesystemObjectStorage
```

only.

Canonical future architecture:

```text
PostgreSQL = metadata/ownership/checksum/retention truth
Object storage = binary artifacts
```

P3-C creates no document/business metadata table.

---

# 25. Port Placement

Prefer:

```text
backend/app/shared/storage/
    __init__.py
    port.py
    types.py

backend/app/adapters/storage/
    __init__.py
    local.py
```

or another clean separation where:

```text
port/contracts do not depend on local filesystem implementation
```

Do not add repository top-level directories.

---

# 26. ObjectStoragePort

Provider-neutral async interface.

Minimum useful methods:

```text
put_bytes
get_bytes
exists
delete
```

No:

```text
boto3 types
S3 client types
SeaweedFS types
FastAPI UploadFile
SQLAlchemy models
document-domain types
```

Do not add recursive listing/admin bucket APIs.

---

# 27. ObjectKey

Implement immutable validated technical key.

Requirements:

```text
relative
non-empty
bounded
POSIX-style `/`
no absolute path
no `..`
no `.` path segment
no empty segment
no backslash
no NUL
no Windows drive form
```

Valid synthetic example:

```text
synthetic/123/example.bin
```

Keys are not original user filenames.

---

# 28. Local Root Containment

Every filesystem operation must remain under explicit root.

Use semantic path containment:

```text
Path.resolve()
Path.relative_to()
```

or robust equivalent.

Do NOT use string prefix checking.

Reject:

```text
../escape.bin
synthetic/../../escape.bin
/absolute.bin
C:\escape.bin
synthetic\escape.bin
```

---

# 29. Symlink Escape

Local adapter must reject an existing symlink path that resolves outside root.

Test where OS supports symlink creation.

A platform-specific skip is acceptable only when the test environment genuinely cannot create symlinks.

Do not broadly disable traversal protection.

---

# 30. Local Adapter Scope

Document:

```text
development/test only
not production object storage
not medical upload boundary
```

Do NOT claim:

```text
encryption at rest
malware protection
medical-grade durability
ABDM compliance
HIPAA compliance
multi-node consistency
```

---

# 31. No SeaweedFS / MinIO / S3

Do not add:

```text
SeaweedFS service/image
MinIO
boto3
S3 SDK
storage service in Compose
```

R3 keeps SeaweedFS as a later self-hosted candidate. MinIO remains rejected as new default.

No dependency additions expected.

---

# 32. Local Data Root

Repository already ignores:

```text
data/local/
data/private/
```

Tests must use:

```text
tmp_path
```

No stored bytes committed to Git.

Do not create sample medical files.

---

# 33. Storage Write Semantics

Recommended:

```text
put_bytes(key, data, overwrite=False)
```

Requirements:

```text
bytes-like content
no hidden serialization
no pickle
default no overwrite
```

Duplicate write should raise typed provider-neutral error unless `overwrite=True` is explicitly supported.

If metadata result is returned, it may contain:

```text
key
size_bytes
sha256
```

No domain identifiers.

---

# 34. Storage Read/Delete/Exists

`get_bytes`:

```text
exact byte-for-byte content
typed not-found error
no absolute root leakage
```

`exists`:

```text
bool
same key validation/containment
```

`delete`:

```text
one validated object only
no recursive delete
explicit missing-object semantics
```

---

# 35. Filesystem I/O

Because port is async, local adapter may use:

```text
asyncio.to_thread
```

Do not add `aiofiles`.

Avoid module-import filesystem side effects.

Root may be created when adapter is explicitly instantiated/used.

---

# 36. Safe Writes

Prefer temporary-file + final move/replace semantics under the same controlled root.

Do not leave temporary artifacts after normal success.

Do not write final data to a global world-writable temp directory.

No need to overengineer production-grade filesystem concurrency.

---

# 37. Storage Errors

Small framework-independent types are allowed:

```text
ObjectStorageError
InvalidObjectKeyError
ObjectNotFoundError
ObjectAlreadyExistsError
```

Do not subclass HTTPException.

Do not expose raw OS error details/root paths unnecessarily.

---

# 38. Storage Tests

Required:

```text
put -> exists -> get -> delete
byte-for-byte equality
size/checksum if exposed
missing read
duplicate write
explicit overwrite if supported
invalid key
absolute path rejection
parent traversal rejection
backslash rejection
root containment
symlink escape where supported
repr/error privacy
```

Use synthetic bytes only.

---

# 39. No Upload-Security Workflow

Do not implement:

```text
MIME detection
file signature validation
malware scan
quarantine
presigned URL
retention
document metadata
DocumentUploaded event
```

These belong to later document/security phases.

The local adapter is not approved for untrusted medical uploads.

---

# 40. Object Storage Configuration

Prefer no settings change.

Current `ObjectStorageSettings` remains safe/inactive.

Do not auto-compose storage into `create_app()` because no product feature consumes it yet.

If a local-root setting is truly needed:

```text
preserve current fields
keep enabled=False
use safe local path
```

But constructor injection with `tmp_path` is preferred for P3-C tests.

---

# 41. Application / Health Boundary

Prefer no changes to:

```text
backend/app/main.py
backend/app/api/health.py
```

Do not add job/storage readiness.

Do not auto-start worker.

Do not attach fake global services merely to prove the abstractions exist.

---

# 42. No Compose / Docker Expansion

Expected unchanged:

```text
deployments/local/compose.yaml
infra/docker/backend.Dockerfile
```

No worker container.

No storage service/container.

No object-storage volume.

A process-local queue cannot support a separate worker container, so adding one would be incorrect.

---

# 43. No Dependency Changes

Expected unchanged:

```text
backend/pyproject.toml
backend/uv.lock
package.json
pnpm-lock.yaml
```

Do not add:

```text
aiofiles
boto3
fsspec
s3fs
procrastinate
celery
redis
kombu
dramatiq
taskiq
```

If any dependency is unavoidable, stop for review.

---

# 44. No Migration Changes

Expected unchanged:

```text
backend/alembic.ini
backend/migrations/**
```

Expected head:

```text
p3b_0002
```

Run Alembic regression checks.

---

# 45. Repository Structure Documentation

Update `docs/03_REPOSITORY_STRUCTURE.md` to explain:

```text
backend/app/jobs/
  provider-neutral background-job contracts + process-local scaffold

backend/app/adapters/storage/
  storage adapter implementations

workers/
  future standalone worker process bootstrap once a durable/shared backend is activated
```

Do not create empty future module ceremony.

---

# 46. Developer Documentation

Update `backend/README.md` with these invariants:

```text
InProcessJobDispatcher is non-durable/process-local
enqueue and execution are separate
no worker daemon starts
Procrastinate remains deferred
ObjectStoragePort is provider-neutral
LocalFilesystemObjectStorage is dev/test only
SeaweedFS/S3 not activated
MinIO not selected
no medical upload-security workflow exists yet
```

Update root README only as needed for current phase status.

---

# 47. P3-C Unit Verification

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

Run import smoke.

---

# 48. PostgreSQL / Migration Regression

With explicit test DB:

```text
uv run alembic -c alembic.ini heads
uv run alembic -c alembic.ini upgrade head
uv run alembic -c alembic.ini current
uv run alembic -c alembic.ini check
uv run pytest -m postgres
```

Verify:

```text
exactly one head
head = p3b_0002
P3-A/P3-B Postgres tests execute
```

P3-C itself adds no Postgres tests unless a regression requires one.

---

# 49. Root Quality Gates

Run:

```text
python scripts/quality_gate.py backend
python scripts/quality_gate.py frontend
```

No frontend behavior change.

---

# 50. Required Diffs

Inspect:

```text
git diff -- backend/pyproject.toml backend/uv.lock package.json pnpm-lock.yaml
git diff -- backend/alembic.ini backend/migrations/
git diff -- deployments/local/compose.yaml infra/docker/backend.Dockerfile
```

Expected all three groups:

```text
no changes
```

---

# 51. Security / Privacy Audit

Verify:

```text
no patient data
no clinical payloads
no secrets
no job payload logging
no raw worker exception persisted
no object bytes logged
no unsafe path traversal
no storage root leak in routine errors
no committed local object files
```

---

# 52. Architecture Audit

Verify:

```text
no jobs table
no new migration
no durable queue dependency
no worker daemon
no Redis/Valkey
no broker
no SeaweedFS
no MinIO
no S3 SDK
no pgvector
no domain/business module
no product endpoint
no clinical logic
no AI/ML/QML
no P3-B outbox semantic change
```

---

# 53. Tests — Expected Coverage

Add P3-C tests covering at least:

### Jobs
```text
JobType validation
JobRequest immutability
payload copy protection
payload repr privacy
timezone validation
enqueue returns handle
enqueue does not execute
duplicate ID rejection
worker smoke success
scheduled job delayed
missing handler failure
handler exception privacy
worker recovers to process next job
no-work result
correlation propagation
```

### Storage
```text
port/local adapter roundtrip
exact bytes
duplicate write
missing object
exists/delete
checksum/size if exposed
absolute path rejection
parent traversal rejection
backslash rejection
symlink escape
root containment
error/repr privacy
```

Do not delete existing tests.

---

# 54. CI

Use existing six mandatory jobs:

```text
Backend quality
Frontend quality
Persistence integration
Docker and PostgreSQL
Playwright Chromium
Security scans
```

Prefer no workflow change.

Worker/storage tests should run under normal backend pytest.

All six jobs must pass for COMPLETE.

---

# 55. Progress Tracker — Local Stage

Before remote CI evidence:

```text
P3-C = PARTIAL — REMOTE CI VERIFICATION PENDING
P3 = PARTIAL
```

Record:

```text
base SHA
branch
implementation SHA
job abstraction/smoke
storage port/adapter
test counts
dependency diff empty
migration diff empty
head p3b_0002
```

---

# 56. Progress Tracker — Final Closure

Only after all six jobs are green:

```text
P3-C = COMPLETE
P3 = COMPLETE
```

Record:

```text
CI run ID
CI URL
head SHA
AC-P3-001 through AC-P3-010 PASS
next = P4-A — Sessions
```

Deferred but non-blocking:

```text
Procrastinate durable-job spike
production/self-hosted object-storage adapter
```

---

# 57. Commit & Push

After local verification:

```text
git status --short
git diff --stat
git diff
git diff --check
```

Then:

```text
git add <P3-C files only>
git commit -m "feat: establish P3-C jobs and object storage"
git push -u origin phase/p3-c-jobs-object-storage
```

Do not merge. Do not force-push.

After CI closure, a focused docs closure commit is allowed.

---

# 58. Final P3 Acceptance Audit

Report:

```text
AC-P3-001 — SQLAlchemy persistence foundation
AC-P3-002 — clean DB -> Alembic head
AC-P3-003 — transaction helpers
AC-P3-004 — versioned event envelope
AC-P3-005 — atomic transactional outbox
AC-P3-006 — outbox retries/status
AC-P3-007 — job-dispatch abstraction
AC-P3-008 — deterministic worker/job smoke
AC-P3-009 — object-storage port/local adapter
AC-P3-010 — no Redis/object storage sole clinical source of truth
```

For P3 COMPLETE, every item must be PASS.

---

# 59. Final Report Format

Return exactly these sections.

## STATUS

```text
COMPLETE | PARTIAL | BLOCKED | FAILED
```

`COMPLETE` requires all six CI jobs green and AC-P3-001..010 PASS.

## BRANCH / GIT

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

Describe only P3-C.

## JOB CONTRACTS

Report:

```text
JobType
JobRequest
JobStatus
JobHandle
JobDispatcher protocol
JobHandler contract
framework independence
payload immutability/privacy
```

## IN-PROCESS JOB BACKEND

Report:

```text
backend type/location
durability
process scope
enqueue behavior
duplicate ID behavior
status inspection
scheduled-job behavior
```

## WORKER

Report:

```text
worker type/location
handler registration
run_once behavior
no-work behavior
success transition
failure transition
missing-handler behavior
clock behavior
daemon/process status
```

## WORKER SMOKE

Report exact evidence:

```text
synthetic job
initial status
handler calls
side effects
final status
network/database/filesystem usage
```

## JOB SAFETY

Report:

```text
payload logging
raw exception persistence
correlation handling
exactly-once claim
durable queue claim
```

## OBJECT STORAGE PORT

Report:

```text
port location
ObjectKey
methods
metadata/result type if any
provider neutrality
```

## LOCAL FILESYSTEM ADAPTER

Report:

```text
adapter location
root behavior
containment method
traversal rejection
absolute/backslash rejection
symlink behavior
write/overwrite semantics
read
exists
delete
checksum/size
blocking-I/O strategy
```

## OBJECT STORAGE SAFETY

Report:

```text
dev/test only
production durability claim
encryption claim
malware/quarantine claim
medical upload validation claim
SeaweedFS status
MinIO status
S3 SDK status
```

## CONFIGURATION

Report whether these changed:

```text
ObjectStorageSettings
create_app
Compose
Dockerfile
```

## MIGRATION STATUS

```text
new migration created
current head
alembic check
jobs table created
storage table created
```

Expected:

```text
NO
p3b_0002
PASS
NO
NO
```

## FILES CHANGED

Group:

```text
job contracts
in-process backend/worker
storage port/types
local adapter
tests
documentation
```

## DEPENDENCIES

Expected:

```text
No new runtime/dev dependency.
```

Report exact diffs for:

```text
backend/pyproject.toml
backend/uv.lock
package.json
pnpm-lock.yaml
```

## TESTS

Report:

```text
new job tests
new storage tests
total backend tests
worker smoke
schedule test
failure privacy test
storage roundtrip
traversal tests
symlink test
Postgres regression executed/pass/skip
```

## VERIFICATION

```text
uv lock --check
uv sync --locked --dev
Ruff
format
mypy
pytest
compile/import smoke
alembic heads
alembic current
alembic check
backend quality gate
frontend quality gate
git diff --check
dependency diff
migration diff
Compose/Docker diff
```

## CI

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

## P3 FINAL ACCEPTANCE

Report AC-P3-001 through AC-P3-010.

All must be PASS for P3 COMPLETE.

## ARCHITECTURE / GOVERNANCE CHECK

```text
JobDispatcher provider-neutral: YES/NO
In-process backend clearly non-durable: YES/NO
No jobs table: YES/NO
No Procrastinate/Celery/Redis/Valkey/broker: YES/NO
No fake standalone daemon backed by process-local queue: YES/NO
No job payload logging: YES/NO
No raw worker exception persisted: YES/NO
ObjectStoragePort provider-neutral: YES/NO
Local adapter root-contained: YES/NO
Traversal/absolute/backslash escape blocked: YES/NO
Symlink escape protected where supported: YES/NO
No SeaweedFS/MinIO/S3 dependency: YES/NO
No storage metadata/domain table: YES/NO
No medical upload-security claims: YES/NO
No domain/business functionality: YES/NO
P2 contracts preserved: YES/NO
P3-A contracts preserved: YES/NO
P3-B contracts preserved: YES/NO
```

## DEVIATIONS

List every deviation and reason.

## BLOCKERS / OPEN DECISIONS

Only genuine unresolved items.

Expected deferred non-blockers:

```text
durable job backend spike (Procrastinate)
production/self-hosted object-storage adapter
```

## PROGRESS TRACKER

```text
P3-C status
overall P3 status
CI evidence status
next recommended unit
```

## MERGE

```text
MERGE PERFORMED: NO
```

## RECOMMENDED NEXT UNIT

If P3 COMPLETE:

```text
P4-A — Sessions
```

Do not implement it.

---

# 60. Success Definition

P3-C is successful only when:

- immutable typed job contracts exist;
- JobDispatcher is provider-neutral;
- InProcessJobDispatcher is process-local/non-durable;
- enqueue and execution are separated;
- deterministic InProcessWorker executes a synthetic job;
- scheduled jobs do not run early;
- missing handler/handler failure produces safe FAILED state;
- raw job payload/exception content is not exposed;
- no durable queue dependency/jobs table is added;
- no fake standalone worker daemon is created;
- ObjectStoragePort is provider-neutral;
- ObjectKey blocks traversal/absolute/backslash escapes;
- LocalFilesystemObjectStorage stays under explicit root;
- storage roundtrip passes;
- symlink escape is rejected where testable;
- local adapter is documented dev/test only;
- no SeaweedFS/MinIO/S3 SDK is activated;
- no medical upload-security/durability/encryption claim is made;
- no schema migration is added;
- Alembic head remains p3b_0002;
- no dependency files change;
- P3-A/P3-B regressions remain green;
- backend/frontend quality gates pass;
- Persistence integration passes;
- Docker/PostgreSQL passes;
- Playwright passes;
- Security scans pass;
- AC-P3-001 through AC-P3-010 all PASS;
- P3-C is marked COMPLETE;
- overall P3 is marked COMPLETE;
- branch is pushed but not merged.

Stop after P3-C.
