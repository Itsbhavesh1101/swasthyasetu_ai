# Codex Phase Prompt — P3-B Event Envelope & Transactional Outbox

**Project:** SwasthyaSetu AI
**Prompt ID:** `SSAI-CODEX-P3-B`
**Phase unit:** P3-B — Event Envelope & Transactional Outbox
**Base branch:** `main`
**Expected base commit:** `b33fcd23bff023fd539984d1f7f2862cc3c52fc1`
**Implementation branch:** `phase/p3-b-event-outbox`
**Scope:** Versioned internal event contract, PostgreSQL transactional outbox, explicit in-process event publisher, retry/status dispatcher foundation, atomicity/idempotency verification
**Expected final status:** `COMPLETE`, `PARTIAL`, `BLOCKED`, or `FAILED`

---

# 0. Mission

Continue P3 — Persistence, Migrations, Events, Outbox and Background Jobs.

P3-A already established:

```text
SQLAlchemy 2.x async persistence foundation
Psycopg 3
Alembic
PostgreSQL integration
DatabaseRuntime
async session factory
transaction helper
migration lineage
DB-aware readiness
Persistence integration CI
```

P3-B must now implement only:

```text
versioned generic event envelope
privacy-safe event metadata/value objects
explicit event publisher/handler contracts
minimal explicit in-process event publisher
platform-owned outbox ORM model
Alembic migration for outbox_events
outbox write/repository operations
same-transaction domain-change + outbox atomicity
manual/batch outbox dispatcher service
due-event selection
safe retry scheduling
attempt/status lifecycle
safe failure-code persistence
at-least-once delivery semantics
idempotent-handler test fixture/pattern
PostgreSQL integration verification
migration drift verification
documentation
```

P3-B must NOT implement:

```text
background worker process
JobDispatcher / JobRequest / JobStatus
Procrastinate
Celery
Dramatiq
Taskiq
Redis / Valkey
NATS / Kafka / RabbitMQ
object storage port or adapter
patient/session/consent/encounter/clinical tables
audit module
notification business logic
FHIR/ABDM logic
HTTP product endpoints
clinical logic
AI/ML/QML
```

P3-C owns jobs/workers and object storage.

P4+ own domain/business tables and domain event payload schemas.

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
HEAD: b33fcd23bff023fd539984d1f7f2862cc3c52fc1
working tree: clean
```

Verify merged P3-A exists:

```text
backend/app/shared/persistence/base.py
backend/app/shared/persistence/runtime.py
backend/alembic.ini
backend/migrations/env.py
backend/migrations/versions/0001_persistence_baseline.py
backend/tests/integration/test_postgres_persistence.py

docs/codex/CODEX_PHASE_PROMPTS/P3_A_SQLALCHEMY_ALEMBIC_FOUNDATION.md
```

Verify tracker says:

```text
P3-A = COMPLETE
P3 = PARTIAL
next = P3-B — Event Envelope & Transactional Outbox
```

If `main` differs only through the approved P3-A merge history, inspect the commits and report the actual clean base SHA.

If unrelated changes exist, stop rather than overwrite them.

---

# 2. Create the Phase Branch

Create:

```text
git switch -c phase/p3-b-event-outbox
```

If the branch already exists:

1. inspect its history;
2. compare against `main`;
3. preserve legitimate work;
4. continue only if clearly intended for P3-B.

Do not implement on `main`.

Do not merge at the end.

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

Inspect actual P3-A code before editing:

```text
backend/app/shared/persistence/
backend/app/shared/types/
backend/app/shared/security/
backend/app/shared/observability/
backend/app/events/
backend/app/main.py
backend/tests/
backend/migrations/
backend/alembic.ini
backend/pyproject.toml
backend/uv.lock

.github/workflows/ci.yml
scripts/quality_gate.py
deployments/local/
infra/docker/backend.Dockerfile
```

Do not code from assumptions.

---

# 4. Governing Decisions

P3-B implements accepted architecture.

Important accepted decisions:

```text
ADR-001 — Modular Monolith First
ADR-006 — Typed Domain Events + Transactional Outbox
ADR-008 — PostgreSQL as Transactional Source of Truth
ADR-021 — Internal Contracts Are Typed
ADR-026 — No Arbitrary Runtime Plugin System
ADR-027 — Core Safety Paths Degrade Independently of Optional AI
```

ADR-006 explicitly requires:

```text
versioned events
transactional outbox
idempotent handlers where needed
transport independence
```

Do not create a new ADR merely to restate these decisions.

---

# 5. P3-B Acceptance Targets

P3-B directly targets:

```text
AC-P3-004 — Versioned event envelope exists.
AC-P3-005 — Transactional outbox records events atomically with domain changes.
AC-P3-006 — Outbox dispatcher handles retries/status.
```

P3-A already established:

```text
AC-P3-001
AC-P3-002
AC-P3-003
```

P3-C remains responsible for:

```text
AC-P3-007 — Job-dispatch abstraction
AC-P3-008 — deterministic worker/job smoke
AC-P3-009 — Object-storage port/local adapter
```

`AC-P3-010` remains an architecture invariant throughout P3.

At successful P3-B completion:

```text
P3-B = COMPLETE
P3 = PARTIAL
```

Do not mark P3 complete.

---

# 6. Canonical Event Envelope

Architecture section 37 defines:

```json
{
  "event_id": "...",
  "event_type": "...",
  "event_version": 1,
  "occurred_at": "...",
  "correlation_id": "...",
  "causation_id": "...",
  "actor_ref": "...",
  "payload": {}
}
```

P3-B must implement this as a framework-independent typed contract.

The envelope must be:

```text
immutable
versioned
JSON-serializable
timezone-aware
opaque-ID based
safe for later module-specific typed payload schemas
independent of FastAPI
independent of SQLAlchemy
independent of broker/vendor SDKs
```

---

# 7. Known Specification Drift — Event Envelope vs Outbox Table

There is a material documentation mismatch that MUST NOT be silently ignored.

`docs/02_SYSTEM_ARCHITECTURE.md` defines event envelope metadata:

```text
event_id
event_type
event_version
occurred_at
correlation_id
causation_id
actor_ref
payload
```

`docs/05_DATABASE_SCHEMA.md` currently defines `outbox_events` with:

```text
id
event_type
event_version
aggregate_type
aggregate_id
correlation_id
causation_id
payload
status
attempt_count
available_at
dispatched_at
last_error_code
created_at
```

It omits:

```text
occurred_at
actor_ref
```

A durable outbox must be able to reconstruct the canonical event envelope without inventing or losing metadata.

Before implementation, report:

```text
SPECIFICATION DRIFT DETECTED
```

with:

```text
source A: docs/02_SYSTEM_ARCHITECTURE.md section 37
source B: docs/05_DATABASE_SCHEMA.md section 26
conflict: canonical event fields occurred_at and actor_ref are not represented in outbox persistence
```

Reconcile by updating the logical outbox schema to add:

```text
occurred_at TIMESTAMPTZ NOT NULL
actor_ref VARCHAR NULL
```

Rationale:

```text
occurred_at = semantic event occurrence time
created_at  = outbox persistence-row creation time
actor_ref   = optional opaque actor reference carried by canonical envelope
```

Rules for `actor_ref`:

```text
opaque technical reference only
no display name
no email
no phone
no ABHA
no clinical content
no role/authorization inference
```

Do not implement P4 identity behavior.

This reconciliation follows ADR-006 and does not require a new ADR unless Codex finds a deeper architecture conflict.

---

# 8. Event Package Placement

Use the canonical platform event area:

```text
backend/app/events/
```

A reasonable shape:

```text
backend/app/events/
    __init__.py
    envelope.py
    publisher.py
    outbox.py
    dispatcher.py
```

Exact split may differ if cohesion improves.

`backend/app/events/` owns generic event infrastructure.

Module-specific event payload schemas will later remain with their owning modules/contracts.

Do not put all future domain events into this platform package.

---

# 9. Event ID

Use the existing opaque UUID policy.

Reuse:

```text
OpaqueId
```

or define a narrow type alias/value object only if it materially improves type safety.

Requirements:

```text
UUID-backed
opaque
immutable
non-sequential
generated application-side
```

Do not introduce database sequences for event IDs.

---

# 10. Event Type

Create a stable typed event-type identifier or equivalent validation.

It should accept current canonical names such as:

```text
SessionCreated
ConsentGranted
PatientCreated
EncounterStarted
DocumentUploaded
ReferralStatusChanged
```

Do not activate these events yet.

Tests should use neutral synthetic types:

```text
SyntheticCreated
ExampleChanged
```

Validation should reject:

```text
empty
whitespace-only
obviously unsafe/unbounded strings
```

Avoid an overly restrictive grammar that prevents future dotted or namespaced event types if architecture evolves.

---

# 11. Event Version

`event_version` must be:

```text
positive integer
explicit
stable
```

Do not infer version from application package version.

Do not use Alembic revision as event version.

Do not use semantic-version parsing dependency.

---

# 12. Occurred At

`occurred_at` must be:

```text
timezone-aware
UTC
```

Default construction may use:

```text
utc_now()
```

but callers must be able to supply a deterministic time in tests.

Reject naive datetime values.

Do not silently localize naive timestamps.

---

# 13. Correlation ID

`correlation_id` is optional transport/workflow metadata.

It may reuse safe request/correlation ID conventions.

Do not require every background event to originate from HTTP.

Do not expose correlation values as metric labels.

Do not put them into payload just to persist them.

---

# 14. Causation ID

`causation_id` is optional.

It identifies the event/command that caused the current event when known.

Keep representation opaque.

Do not interpret causation as authorization.

Do not build a full distributed tracing graph in P3-B.

---

# 15. Actor Reference

`actor_ref` is optional metadata.

It must remain:

```text
identity-neutral
opaque
non-authoritative
```

P3-B must not create:

```text
roles
permissions
actor database tables
OIDC claims
authorization policy
```

P4 will define identity/session semantics.

---

# 16. Event Payload

The platform envelope should accept a JSON-compatible mapping.

Prefer a type such as:

```text
Mapping[str, JsonValue]
```

or a Pydantic equivalent.

Requirements:

```text
JSON-compatible
immutable/copy-protected where practical
not arbitrary Python object graph
no pickle
no executable objects
```

Future modules own typed payload models and serialize them into the generic transport envelope.

Do not define real healthcare payload schemas in P3-B.

---

# 17. Payload Representation Privacy

The event envelope/persistence object must not casually expose payload through logs/repr.

If practical:

```text
payload repr=False
```

or equivalent.

Do not add logging that serializes the full event.

Safe operational metadata may include:

```text
event_id
event_type
event_version
attempt_count
status
```

Do not log payload.

---

# 18. Event Payload Minimization

Architecture explicitly requires:

```text
Payloads must minimize sensitive content.
```

P3-B cannot enforce domain-specific minimum necessary data yet.

It MUST establish the rule in code/docs/tests:

```text
event payload is not a transcript archive
event payload is not a document dump
event payload is not a substitute for canonical domain storage
```

Use only synthetic payloads in tests.

---

# 19. Publisher Contract

Define a provider-neutral async publisher contract.

Conceptual interface:

```python
class EventPublisher(Protocol):
    async def publish(self, event: EventEnvelope) -> None:
        ...
```

It must not mention:

```text
Kafka
NATS
RabbitMQ
Redis
Celery
Procrastinate
```

Domain/business code will depend on contracts, not broker implementations.

---

# 20. Event Handler Contract

Define a minimal async handler contract if needed by the in-process publisher.

Conceptual:

```python
class EventHandler(Protocol):
    async def handle(self, event: EventEnvelope) -> None:
        ...
```

Function-callable style is also acceptable.

Keep it typed and small.

Do not add a DI framework.

---

# 21. Minimal In-Process Publisher

Implement a deterministic explicit in-process publisher for:

```text
unit/integration scaffolding
future local internal reactions
transport-independent tests
```

Registration must be explicit.

Do not:

```text
scan packages
discover handlers dynamically
use setuptools entry points
import handlers by strings
hot-load handlers
```

A simple immutable mapping from:

```text
event_type -> tuple[handlers]
```

is sufficient.

---

# 22. In-Process Publisher Semantics

For one published event:

```text
invoke matching handlers
await handlers
propagate a handler failure to dispatcher
```

Do not silently swallow handler failures.

Do not automatically mark an event delivered if a handler failed.

If multiple handlers exist, choose deterministic registration order.

Document/test the behavior.

Do not add parallel fan-out complexity in P3-B.

---

# 23. No Built-In Exactly-Once Claim

The outbox architecture is:

```text
at-least-once
```

A crash can occur after side effect delivery but before outbox status commit.

Therefore handlers with side effects must support idempotency.

Do NOT claim:

```text
exactly once
```

anywhere.

Do not hide duplicates by an in-memory publisher-level dedupe mechanism.

---

# 24. Idempotency Fixture

The P3 master plan requests a duplicate-handler/idempotency fixture.

Implement a synthetic test handler that:

```text
tracks processed event IDs
receives the same event twice
performs its synthetic side effect only once
```

This demonstrates the required consumer pattern.

Do not add a production global in-memory dedupe store.

Do not add a persistent processed-events table unless a real phase requirement later needs it.

---

# 25. Outbox Table Ownership

`outbox_events` is the first platform-owned application table.

Owner:

```text
platform event infrastructure
```

It does NOT belong to:

```text
patients
sessions
consent
referrals
notifications
audit
```

Do not create a central file containing future domain models.

The event package may own its ORM model.

---

# 26. Outbox ORM Model

Implement SQLAlchemy 2.x typed ORM for:

```text
outbox_events
```

Canonical/reconciled fields:

```text
id UUID PK
event_type VARCHAR NOT NULL
event_version INTEGER NOT NULL
aggregate_type VARCHAR NULL
aggregate_id UUID NULL
correlation_id VARCHAR NULL
causation_id VARCHAR NULL
actor_ref VARCHAR NULL
occurred_at TIMESTAMPTZ NOT NULL
payload JSONB NOT NULL
status VARCHAR NOT NULL
attempt_count INTEGER NOT NULL DEFAULT 0
available_at TIMESTAMPTZ NOT NULL
dispatched_at TIMESTAMPTZ NULL
last_error_code VARCHAR NULL
created_at TIMESTAMPTZ NOT NULL
```

Do not add unrelated columns.

---

# 27. Outbox Indexes

Create the canonical indexes:

```text
(status, available_at)
event_type
aggregate_id
```

Use the P3-A naming convention.

No duplicate/redundant indexes.

---

# 28. Outbox Constraints

Use DB constraints where they protect generic invariants.

At minimum:

```text
event_version > 0
attempt_count >= 0
status in supported finite statuses
```

Explicitly name CHECK constraints because P3-A naming convention uses:

```text
ck_%(table_name)s_%(constraint_name)s
```

Do not use anonymous CHECK constraints.

---

# 29. Outbox Status

Implement an explicit finite enum/value object.

Minimum lifecycle:

```text
PENDING
DISPATCHED
FAILED
```

Semantics:

```text
PENDING    -> due now or scheduled for retry
DISPATCHED -> successfully published
FAILED     -> terminal delivery failure after retry policy
```

Do not invent business statuses.

Do not add `PROCESSING` unless a concrete correct lease/recovery design is also implemented.

P3-B should stay simple.

---

# 30. Attempt Count

Define exact semantics:

```text
attempt_count = number of publish attempts already performed
```

Expected:

```text
new row -> 0
first successful delivery -> 1
first failed attempt -> 1
retry then success -> 2
```

Document and test this.

---

# 31. Available At

`available_at` controls delivery eligibility.

On initial enqueue:

```text
available_at <= current time
```

unless caller explicitly schedules later.

On retry:

```text
available_at = failure time + retry delay
```

Do not busy-loop immediately unless retry policy deliberately gives zero delay in tests.

---

# 32. Dispatched At

On successful publish:

```text
status = DISPATCHED
dispatched_at = current UTC time
last_error_code = NULL
```

Do not set `dispatched_at` on failed delivery.

---

# 33. Failure Code

Persist only a safe bounded machine-readable error code.

Do not persist:

```text
raw exception message
stack trace
SQL exception
payload
credentials
provider response body
```

For unexpected publisher/handler exceptions use a generic safe code such as:

```text
EVENT_DELIVERY_FAILED
```

Exact internal name may differ.

Do not add this to the public HTTP `ErrorCode` registry unless an HTTP API actually needs it later.

---

# 34. Retry Policy

Implement a small framework-independent retry policy.

It must provide:

```text
maximum attempts
deterministic delay calculation
```

Do not add random jitter in tests.

Do not add a dependency.

A simple bounded exponential or fixed backoff is acceptable.

Keep defaults clearly operational, not clinical.

Allow tests/future workers to inject a policy.

Do not add configuration fields unless implementation actually needs global runtime values in P3-B.

---

# 35. Retry Lifecycle

For a publish failure before max attempts:

```text
attempt_count += 1
status = PENDING
last_error_code = safe code
available_at = now + delay
dispatched_at = NULL
```

At max attempts:

```text
attempt_count += 1
status = FAILED
last_error_code = safe code
dispatched_at = NULL
```

On later success:

```text
attempt_count += 1
status = DISPATCHED
last_error_code = NULL
dispatched_at = now
```

Test all three paths.

---

# 36. Outbox Repository

Implement a narrow repository/store for platform outbox infrastructure.

It may support:

```text
enqueue
load/lock next due event
mark dispatched
schedule retry
mark terminal failure
read by event ID for tests/operations if useful
```

Do not create a generic CRUD repository.

Do not add cross-module repository logic.

---

# 37. Enqueue Must Not Commit

Critical invariant:

```text
outbox enqueue participates in the caller's existing SQLAlchemy transaction
```

Repository enqueue MUST NOT:

```text
commit
open an unrelated transaction
create a new engine
```

Caller supplies the `AsyncSession`.

This is required for AC-P3-005.

---

# 38. Atomicity Pattern

Future use-case pattern:

```python
async with database.transaction() as session:
    await domain_repository.change_state(session, ...)
    await outbox.enqueue(session, event, ...)
```

One commit persists both.

One rollback removes both.

P3-B integration tests must prove this using a synthetic probe table because no domain tables exist yet.

---

# 39. Synthetic Atomicity Probe

Use an ephemeral test-only table such as:

```text
p3b_atomicity_probe
```

It must NOT appear in Alembic migration.

Test:

```text
create probe
transaction:
    insert probe change
    enqueue event
commit
-> both rows exist
```

Then test:

```text
transaction:
    insert probe change
    enqueue event
    raise synthetic exception
rollback
-> neither row exists
```

Cleanup in `finally`.

No patient-like data.

---

# 40. Due Event Selection

Dispatcher/repository must only select:

```text
status = PENDING
available_at <= now
```

Order deterministically, for example:

```text
available_at
created_at
id
```

Limit batch size.

Do not scan all historic dispatched events each cycle.

---

# 41. Concurrent Dispatcher Safety

Use PostgreSQL row locking appropriate for outbox consumption:

```text
SELECT ... FOR UPDATE SKIP LOCKED
```

or a demonstrably equivalent safe approach.

This avoids two dispatcher instances selecting the same pending row simultaneously under normal operation.

Do not add a distributed lock service.

---

# 42. Transaction Scope During Delivery

A simple P3-B implementation may:

```text
open one DB transaction
lock one due row
publish via current in-process publisher
update retry/dispatched state
commit
```

Then repeat until batch limit.

This deliberately keeps the baseline simple.

Document the consequence:

```text
crash after publish but before commit can cause duplicate redelivery
```

Hence at-least-once + idempotent consumer requirement.

Do not claim this design is exact-once.

---

# 43. Dispatcher Service

Implement a manual service such as:

```text
OutboxDispatcher
```

It should be callable explicitly:

```python
await dispatcher.dispatch_batch(...)
```

It is NOT a worker loop.

It is NOT started automatically by FastAPI.

It is NOT a background task.

P3-C will decide worker/job execution.

---

# 44. Dispatcher Dependencies

Inject:

```text
DatabaseRuntime or session factory
Outbox repository
EventPublisher
RetryPolicy
clock/time provider if needed
```

Keep dependencies explicit.

Do not use globals.

Do not pull FastAPI app state into event/domain code.

---

# 45. Dispatch Batch Result

Return a small typed summary if useful:

```text
selected
dispatched
retried
failed
```

No payload data.

This is operational metadata only.

Do not create an HTTP endpoint for it.

---

# 46. No Automatic Dispatcher Startup

Prohibited:

```text
FastAPI startup task that loops forever
asyncio.create_task(outbox_loop())
BackgroundTasks-based outbox worker
```

P3-B establishes the dispatcher logic only.

P3-C owns actual worker execution.

---

# 47. Event Reconstruction

Outbox row must reconstruct the canonical envelope without loss:

```text
id -> event_id
event_type
event_version
occurred_at
correlation_id
causation_id
actor_ref
payload
```

Aggregate fields are delivery/index metadata and may be kept separately.

Test round-trip fidelity.

---

# 48. Aggregate Metadata

`aggregate_type` and `aggregate_id` remain optional outbox metadata.

They are useful for:

```text
diagnostics
indexing
future ordering/partitioning
```

P3-B must not invent a universal aggregate domain model.

Use synthetic aggregate metadata in tests only.

---

# 49. JSONB

Use PostgreSQL JSONB for payload.

Do not store pickled data.

Do not store arbitrary Python serialization.

Do not add pgvector.

---

# 50. Event Serialization

Provide one project-owned serializer/builder path.

Requirements:

```text
UUID -> JSON-safe representation
datetime -> ISO-8601/DB timestamp as appropriate
payload copied/validated
event_version preserved exactly
```

Do not depend on broker serializers.

---

# 51. ORM / Envelope Separation

Keep:

```text
EventEnvelope     = framework-independent contract
OutboxEventRecord = SQLAlchemy persistence model
```

Do not make `EventEnvelope` an ORM model.

Do not leak `Mapped[...]` into module event contracts.

---

# 52. Migration

Create the next migration:

```text
backend/migrations/versions/0002_transactional_outbox.py
```

Suggested revision:

```text
p3b_0002
```

Required:

```text
down_revision = "p3a_0001"
exactly one head
```

Migration creates only:

```text
outbox_events
its constraints
its indexes
```

No other application table.

---

# 53. Migration Model Registration

Alembic `target_metadata` must see the platform outbox ORM model.

Do this explicitly.

Acceptable:

```text
explicit import in migrations/env.py
explicit event metadata-registration module
```

Do not create a giant central `models.py` for all future module models.

Future module phases must explicitly register/import their own ORM models for Alembic.

---

# 54. Migration Autogenerate Drift

After upgrade:

```text
uv run alembic -c alembic.ini check
```

must report no pending upgrade operations.

If it does:

```text
fix model/migration mismatch
```

Do not suppress broad tables/indexes from autogenerate merely to force green.

---

# 55. Migration Downgrade

For P3-B, downgrade is safe because this branch contains only synthetic/test data.

Implement real downgrade:

```text
drop indexes/table
```

or allow `op.drop_table` to remove contained indexes as appropriate.

Verify:

```text
head -> p3a_0001 -> head
```

Do not write fake downgrade.

---

# 56. Migration Verification

Against a fresh PostgreSQL volume:

```text
p3a baseline
upgrade head -> p3b_0002
alembic current
alembic check
```

Inspect:

```text
outbox_events exists
expected columns exist
expected indexes exist
expected constraints exist
no domain tables exist
```

---

# 57. PostgreSQL Integration Tests

P3-B integration tests MUST execute against real PostgreSQL.

Add/update `@pytest.mark.postgres` tests.

CI must prove they do not all skip.

Test at least:

```text
enqueue persistence
event round trip
atomic commit
atomic rollback
due-event selection
successful dispatch
retry scheduling
terminal failure
```

A subset may be unit tests where appropriate, but atomicity/locking/persistence must be real PostgreSQL.

---

# 58. Dispatcher Success Integration

Arrange:

```text
one PENDING due event
fake/in-process publisher succeeds
dispatch one
```

Assert:

```text
publisher received reconstructed envelope
attempt_count = 1
status = DISPATCHED
dispatched_at non-null
last_error_code null
```

---

# 59. Dispatcher Retry Integration

Arrange publisher to fail once.

Assert after first attempt:

```text
attempt_count = 1
status = PENDING
available_at moved forward
last_error_code = safe code
dispatched_at null
```

Then dispatch at/after due time with publisher success.

Assert:

```text
attempt_count = 2
status = DISPATCHED
last_error_code null
```

Do not sleep in tests.

Inject time/retry policy or explicitly move test clock.

---

# 60. Terminal Failure Integration

Use a small synthetic retry policy, for example:

```text
max_attempts = 2
```

Fail twice.

Assert:

```text
status = FAILED
attempt_count = 2
dispatched_at null
last_error_code safe
```

Subsequent dispatch batch must not select the FAILED event.

---

# 61. Future-Dated Event Test

Enqueue event with:

```text
available_at > now
```

Dispatcher must not publish it early.

No sleep.

Use deterministic clock/input time.

---

# 62. Duplicate Delivery / Idempotency Test

Deliver the same envelope twice directly through the in-process publisher to the synthetic idempotent handler.

Assert:

```text
handler received duplicate
synthetic side effect performed once
```

Document:

```text
idempotency is handler responsibility
transport remains at-least-once
```

Do not silently dedupe in the publisher.

---

# 63. Publisher Failure Privacy Test

Raise a synthetic exception containing:

```text
synthetic-sensitive-delivery-detail
```

After dispatch failure verify the marker is absent from:

```text
outbox last_error_code
logs if captured
serialized event status metadata
```

Do not store raw exception text.

---

# 64. Event Repr Privacy Test

If envelope repr is used/defaulted, test a synthetic payload marker is not casually included.

If implementation intentionally keeps normal dataclass repr including payload, then do not log/repr envelopes anywhere and explicitly justify it.

Preferred:

```text
payload excluded from repr
```

---

# 65. Event Time Test

Verify:

```text
occurred_at timezone aware
UTC
naive datetime rejected
```

Reuse project `utc_now()`.

---

# 66. Event Version Test

Verify:

```text
version 1 accepted
zero rejected
negative rejected
```

No floating/string version.

---

# 67. Event Payload Test

Verify non-JSON-compatible payload fails deterministically before persistence if validation is implemented.

Do not allow:

```text
open file handles
bytes without explicit encoding
custom arbitrary objects
```

through the generic event payload.

---

# 68. No Real Domain Events

Do not define production payload classes for:

```text
ConsentGranted
PatientCreated
DocumentUploaded
ReferralCreated
MentalHealthRouteDecided
```

Those belong to their module phases.

Tests use synthetic event types.

---

# 69. No Product Event Handlers

Do not create:

```text
notification handlers
FHIR sync handlers
referral handlers
audit handlers
OCR handlers
```

P3-B is platform infrastructure only.

---

# 70. No Audit Table

Do not create `audit_events`.

Audit persistence is a separate module/phase.

Outbox is not a substitute for the audit trail.

---

# 71. No Jobs Table

Do not create:

```text
jobs
worker_jobs
task_queue
```

P3-C handles jobs.

---

# 72. No Persistent Idempotency Table

Do not create:

```text
processed_events
handler_deduplication
consumer_offsets
```

in P3-B unless a canonical requirement explicitly forces it.

The current requirement is a handler idempotency fixture/pattern.

---

# 73. No Broker

Do not add:

```text
Redis
Valkey
NATS
RabbitMQ
Kafka
SQS
Pub/Sub
```

The outbox publisher is in-process/test scaffolding.

Future transport remains behind `EventPublisher`.

---

# 74. No New Runtime Dependency Expected

P3-B should use the existing stack:

```text
Python stdlib
Pydantic
SQLAlchemy
PostgreSQL/Psycopg
```

Expected:

```text
backend/pyproject.toml unchanged
backend/uv.lock unchanged
```

If a new dependency appears necessary:

```text
STATUS: BLOCKED — DEPENDENCY REVIEW REQUIRED
```

Do not add it silently.

---

# 75. PostgreSQL Source of Truth

Outbox state lives in PostgreSQL.

Do not mirror canonical outbox state into an in-memory map.

The in-process publisher is transport behavior, not outbox persistence authority.

---

# 76. Transaction Ownership

Repositories never commit independently.

Dispatcher may own its dedicated dispatch transaction because dispatch itself is an application operation.

Enqueue repository must use caller-provided session.

This distinction must be documented.

---

# 77. Session Concurrency

Do not share one `AsyncSession` across concurrent operations.

Every transaction scope gets its own session.

P3-A runtime contract remains unchanged.

---

# 78. SQL Construction

Use SQLAlchemy expressions.

If using PostgreSQL-specific row locking:

```text
with_for_update(skip_locked=True)
```

is appropriate.

Do not build dynamic raw SQL from event values.

---

# 79. Batch Size

Dispatcher must accept a bounded positive batch limit.

Reject:

```text
0
negative
unbounded huge values
```

A conservative default is acceptable.

Do not put thousands of events in memory without a bound.

---

# 80. Retry Policy Validation

Validate:

```text
max_attempts >= 1
retry delays non-negative
maximum delay >= base delay if applicable
```

Use immutable dataclass/value object.

No Pydantic network/database validators.

---

# 81. Retry Backoff

If exponential:

```text
base * 2^(attempt-1)
```

cap it.

Avoid integer overflow/unbounded timedelta.

If fixed:

```text
document it
```

Either is acceptable for P3-B.

No jitter dependency.

---

# 82. Dispatcher Exception Handling

Catch publisher/handler delivery errors at the dispatcher boundary only to:

```text
update retry/failure state
store safe error code
continue according to batch semantics
```

Do not:

```text
except Exception: pass
```

An unexpected DB error should still fail/rollback the dispatch transaction.

A publisher exception can be converted into a safe delivery failure state.

---

# 83. Batch Continuation

A delivery failure for one event should not permanently prevent later due events in the same requested batch from being attempted, unless a DB-level failure makes the transaction/runtime unsafe.

Prefer one row/one transaction per delivery iteration so status changes are isolated.

Document behavior.

---

# 84. Lock Duration

The baseline may hold the selected row lock while calling the current publisher.

This is acceptable for the initial in-process publisher.

Do not claim it is optimal for slow external brokers.

Future transport activation may introduce explicit claim/lease semantics if measurements justify it.

No extra lease columns in P3-B.

---

# 85. Event Ordering

Do not promise total global event ordering.

Only deterministic due-row selection is required.

Do not create Kafka-style partition semantics.

Later domain handlers must not rely on global exact ordering unless specified.

---

# 86. Event Actor Privacy

Do not log `actor_ref` by default.

Do not add it to metrics.

Do not add it to trace attributes.

It may be persisted in the outbox because it is canonical envelope metadata, but remains an opaque reference.

---

# 87. Correlation Privacy

Correlation ID may be logged only under current structured logging allowlist/governance.

Do not make correlation ID a metric label.

Do not store request payloads as correlation metadata.

---

# 88. Observability

P2-C observability remains content-free.

P3-B MUST NOT add:

```text
event payload trace attributes
SQL statement spans
outbox payload logs
handler exception stack events
actor refs as metric labels
```

Operational counters for outbox are not required yet.

Do not add Prometheus/Collector.

---

# 89. Feature Flags

Do not gate the outbox foundation behind a feature flag.

Persistence/event infrastructure is platform behavior.

Do not activate real product features.

---

# 90. Module Registry

Do not register event infrastructure as a fake product module.

`backend/app/events` is platform infrastructure.

P2-B module/capability contracts remain unchanged.

---

# 91. App Composition

Do not start the dispatcher in `create_app()`.

P3-B should not require changes to `app.main` unless a narrow shared service composition test genuinely needs them.

Prefer zero app-factory change.

The API can run with outbox table available but no background dispatch loop.

---

# 92. Readiness

Do not add outbox-dispatcher readiness.

The required infrastructure dependency remains PostgreSQL.

If PostgreSQL is healthy:

```text
database=ok
```

is sufficient.

Dispatcher execution is not an API startup dependency in P3-B.

---

# 93. Alembic Baseline Preservation

Do not edit the merged migration:

```text
0001_persistence_baseline.py
```

Create only a new revision.

Never rewrite merged migration history.

---

# 94. Migration Head

After P3-B:

```text
p3b_0002 = head
p3a_0001 = parent
```

Exactly one head.

Update CI revision assertion from:

```text
p3a_0001
```

to:

```text
p3b_0002
```

---

# 95. Clean Migration Verification

The Persistence integration job must still start from a fresh DB.

Verify:

```text
upgrade base -> p3a -> p3b
alembic check
downgrade to p3a
re-upgrade p3b
```

A fully fresh downgrade to base may also be tested if safe.

Do not rely only on an already-migrated developer DB.

---

# 96. Schema Inspection

CI/integration should assert the outbox table exists.

At minimum inspect:

```text
table
head revision
key indexes
```

Prefer SQLAlchemy inspector or PostgreSQL catalog query.

Do not create brittle ordering assumptions on catalog rows.

---

# 97. P3-A Integration Tests

Preserve:

```text
P3-A transaction commit test
P3-A rollback test
DB ping
readiness behavior
migration baseline assumptions updated only where head naturally changed
```

Do not delete valid tests to make P3-B pass.

---

# 98. Test Cleanup

Integration tests must clean:

```text
synthetic probe rows/tables
outbox synthetic rows
```

Do not drop the actual outbox table except through migration downgrade tests.

Do not delete unrelated developer DB data.

---

# 99. Test DB Guard

Continue requiring explicit:

```text
SWASTHYASETU_TEST_DATABASE_URL
```

for destructive integration fixtures.

Do not implicitly use production settings.

---

# 100. No SQLite

Do not substitute SQLite for:

```text
JSONB
SKIP LOCKED
transactional outbox atomicity
PostgreSQL migration tests
```

Unit tests may be DB-free.

Real persistence tests use PostgreSQL 16.

---

# 101. In-Process Handler Registration

Handler registration should be immutable after publisher construction if practical.

Do not expose request-time mutation.

No runtime plugin marketplace.

Use explicit constructor input/builder.

---

# 102. No Handler Side-Effect Transaction Coupling Claim

The event transport transaction and handler side-effect transaction are not automatically one atomic unit.

Document:

```text
outbox guarantees event persistence with originating DB change
consumer side effects require idempotency
```

Do not imply distributed transaction.

---

# 103. Event Envelope Construction Helper

A small helper such as:

```text
EventEnvelope.new(...)
```

may generate:

```text
event_id
occurred_at
```

while requiring:

```text
event_type
event_version
payload
```

Optional metadata remains explicit.

Do not derive event type from Python class name automatically.

Event type is a versioned contract.

---

# 104. Serialization Stability

Persist event type/version explicitly, not only a serialized model class.

Future code refactors must not silently rename historical events.

Do not store Python import paths as event type.

---

# 105. Payload Versioning

`event_version` versions the event contract/payload schema.

Do not add a separate generic schema version unless canonical docs require it.

Future modules may version their payload schema through event version.

---

# 106. Event Mutation

Envelope is immutable after creation.

If a new version/content is needed, create a new event ID.

Do not mutate a dispatched historical event.

Retry metadata changes belong to outbox record, not envelope.

---

# 107. ORM Record Mutation

Outbox ORM record may mutate operational fields:

```text
status
attempt_count
available_at
dispatched_at
last_error_code
```

Do not mutate immutable event content fields after enqueue:

```text
id
event_type
event_version
occurred_at
payload
correlation_id
causation_id
actor_ref
aggregate metadata
```

Application/repository API should discourage such mutation.

---

# 108. Outbox Insert Time

Use project UTC time helper or DB/app equivalent.

`created_at` must be timezone-aware.

Do not use naive `datetime.utcnow()`.

---

# 109. Event Occurrence vs Persistence Time

Test/document:

```text
occurred_at may be <= created_at
```

They are not aliases.

Do not overwrite `occurred_at` at enqueue.

---

# 110. Future Scheduling

`available_at` may be later than `created_at`.

This is delivery scheduling metadata, not event occurrence time.

Do not change event `occurred_at` when retrying.

---

# 111. Index / Constraint Naming

Follow P3-A conventions.

Expected names should be deterministic.

Do not create duplicate manually named indexes that conflict with metadata naming.

`alembic check` must stay clean.

---

# 112. SQLAlchemy Types

Use PostgreSQL-native types where required:

```text
JSONB
timezone-aware DateTime
UUID-compatible type
```

Do not use TEXT to store JSON.

Do not use integer IDs.

---

# 113. Status Storage

String storage with a named CHECK constraint is preferred over PostgreSQL native ENUM for this baseline because:

```text
migration evolution is simpler
status values remain explicit
```

If SQLAlchemy enum is chosen, justify and test downgrade/type cleanup.

Do not create orphan enum types.

---

# 114. Payload Default

Payload is required.

If an event has no domain fields use:

```json
{}
```

Do not allow SQL NULL payload.

Do not use a mutable Python dict default on ORM/dataclass definitions.

---

# 115. Actor Ref Length

If using VARCHAR length, keep it bounded and sufficient for opaque future references.

Do not encode personal display data.

Exact length should be documented.

---

# 116. Correlation/Causation Length

Use bounded storage.

Keep compatibility with current request ID maximum:

```text
128 chars
```

A larger conservative bound may be used if justified.

Do not use unrestricted TEXT without reason.

---

# 117. Event Type Length

Use bounded string storage.

A practical value such as:

```text
128 or 255
```

is acceptable.

Do not truncate silently.

Validate before persistence.

---

# 118. Aggregate Type Length

Use bounded string storage.

No healthcare semantics in validation.

Synthetic tests only.

---

# 119. Payload Size

Do not invent a hard database payload-size threshold in P3-B unless canonical docs define one.

Document minimization requirement.

Large documents/binaries never belong in event payload.

---

# 120. No Object Storage References Requirement Yet

Payload may later contain safe object references from owning modules.

P3-B does not implement object storage.

Do not add object storage dependencies.

---

# 121. In-Process Publisher Test

Test:

```text
no handler -> successful no-op delivery OR explicit documented behavior
one handler -> invoked once
multiple handlers -> deterministic order
handler failure -> propagated
```

Choose and document no-handler semantics.

Preferred:

```text
no registered handler = successful publish
```

because an integration event may legitimately have zero local consumers at a point in deployment.

Do not treat absence as a delivery failure unless canonical requirements say otherwise.

---

# 122. Publisher Handler Key

Route handlers by:

```text
event_type
```

Event version should be visible to handler.

Do not route only by Python payload class.

A handler must be able to reject/branch on unsupported event version in its module phase.

P3-B does not implement domain version adapters.

---

# 123. Dispatcher No-Handler Semantics

If the in-process publisher defines no-handler as successful:

```text
dispatcher marks event DISPATCHED
```

This is acceptable for internal baseline.

Document that future external broker transport may deliver to remote consumers independently.

---

# 124. Delivery Error Type

If defining a typed internal delivery exception, keep it generic.

Potential:

```text
EventDeliveryError(error_code: str)
```

Do not create:

```text
NotificationDeliveryError
FHIRSyncError
```

in platform events.

Unexpected exceptions must still be converted to safe failure metadata.

---

# 125. Dispatcher Return

A batch result should not contain event payloads.

Safe:

```text
selected
dispatched
retried
failed
```

Maybe event IDs if needed for tests, but avoid exposing large/raw data.

No HTTP serialization required.

---

# 126. Batch Zero Case

No due events:

```text
dispatch_batch -> successful zero counts
```

Do not raise.

Test it.

---

# 127. Batch Limit Validation

Reject invalid batch sizes deterministically.

If using dataclass/Pydantic, test:

```text
0 rejected
negative rejected
reasonable positive accepted
```

No arbitrary giant global config needed.

---

# 128. Clock Injection

Prefer deterministic clock injection for retry tests.

Possible:

```python
clock: Callable[[], datetime] = utc_now
```

Do not monkeypatch standard-library time globally.

Validate returned datetime is timezone aware where used.

---

# 129. Retry Delay Test

Prove:

```text
failure at T
delay D
next available_at = T + D
```

No sleeping.

---

# 130. Max Attempts Test

Prove there is no off-by-one.

If:

```text
max_attempts = 2
```

then:

```text
first failure -> PENDING attempt_count=1
second failure -> FAILED attempt_count=2
```

No third publish.

---

# 131. Retry Error Reset

After a prior failure followed by success:

```text
last_error_code = NULL
```

Do not retain stale failure code on DISPATCHED rows.

---

# 132. Failed Event Immutability

Dispatcher should not automatically resurrect:

```text
FAILED
```

rows.

A future operator/requeue command can be a separate governed capability if needed.

P3-B has no admin requeue API.

---

# 133. Dispatched Event Immutability

Dispatcher never republishes:

```text
DISPATCHED
```

rows.

Test selection filter.

---

# 134. Event Repository Read Methods

Do not add broad search/query APIs now.

Only methods needed for:

```text
enqueue
dispatch
tests
```

Keep surface small.

---

# 135. No HTTP Event API

Do not create:

```text
POST /events
GET /outbox
POST /outbox/retry
```

P3-B has no public/admin event APIs.

---

# 136. No Frontend Changes

P3-B requires no frontend behavior change.

Expected:

```text
package.json unchanged
pnpm-lock.yaml unchanged
apps/* unchanged
packages/ui unchanged
```

Frontend quality gate remains regression coverage.

---

# 137. No Runtime Dependency Change

Expected:

```text
backend/pyproject.toml unchanged
backend/uv.lock unchanged
```

If SQLAlchemy/Psycopg constraint changes due a real security issue, report as deviation and justify.

Do not opportunistically upgrade unrelated packages.

---

# 138. Migration CI

Update Persistence integration job.

It must:

```text
start fresh PostgreSQL
sync locked backend
assert exactly one Alembic head
upgrade to p3b_0002
current
alembic check
run Postgres integration tests
verify p3b_0002 in alembic_version
```

Also verify downgrade/re-upgrade across P3-B migration.

---

# 139. Integration Test Execution Count

Final report must state:

```text
Postgres tests executed
passed
skipped
```

Remote Persistence integration must have:

```text
0 relevant skips
```

Do not count an all-skipped suite as success.

---

# 140. Existing Six CI Jobs

Do not create a seventh job unless materially necessary.

Expected mandatory jobs remain:

```text
Backend quality
Frontend quality
Persistence integration
Docker and PostgreSQL
Playwright Chromium
Security scans
```

P3-B DB/outbox tests belong in Persistence integration.

---

# 141. Docker Job

Existing Docker/PostgreSQL job should still:

```text
migrate to head
start backend
verify database readiness
```

Update only revision-specific assertions if needed.

Do not start a dispatcher worker.

---

# 142. Docker Image

No Dockerfile change should be necessary unless event/migration files are not already copied.

Current image already copies:

```text
backend/app
backend/alembic.ini
backend/migrations
```

Prefer no Dockerfile churn.

Do not add OS packages.

---

# 143. Security Scans

Gitleaks + Trivy remain mandatory.

No broad ignore.

No payload/test secrets that look real.

Synthetic credentials remain current CI/local pattern.

---

# 144. Logging Privacy Regression

Run existing logging/observability privacy tests.

Add targeted event privacy tests.

No event payload in:

```text
structured logs
trace attributes
metric labels
error responses
```

P3-B need not emit event metrics.

---

# 145. Database URL Privacy

P3-A DB secret protections remain unchanged.

Dispatcher errors must not accidentally include database URL or SQL errors in `last_error_code`.

---

# 146. P3-A Readiness Regression

Verify:

```text
DB disabled -> ready
DB healthy -> ready/database=ok
DB unavailable -> 503
liveness independent
```

P3-B must not affect health semantics.

---

# 147. P2 Regression

Preserve:

```text
stable error envelope
request IDs
module registry
capability registry
feature flags safe-off
OpenTelemetry privacy
```

No event changes should require frontend API changes.

---

# 148. Alembic Environment

Explicitly import/register the outbox ORM model so `Base.metadata` contains the table for migration drift checks.

Do not import future domain modules.

Comment why the import exists if needed.

---

# 149. Base Metadata Test Evolution

P3-A test asserted:

```text
Base.metadata.tables == ()
```

That is no longer valid after P3-B.

Update it deliberately.

New expectation:

```text
platform Base metadata contains exactly the platform-owned outbox table
no domain tables
```

Do not simply delete the test.

---

# 150. Domain Model Count

Final report should distinguish:

```text
platform persistence models: 1 (outbox_events)
domain/business models: 0
```

P3-B is still before domain modules.

---

# 151. Outbox Model Import Side Effects

Importing event persistence model should only register SQLAlchemy metadata.

It must not:

```text
open DB connection
start dispatcher
register handlers
perform network I/O
```

---

# 152. No App Startup DB Writes

FastAPI startup must not enqueue or mutate outbox events.

No sample event insertion.

No seed event.

---

# 153. Synthetic Fixtures Only

Use:

```text
SyntheticCreated
ExampleChanged
aggregate_type="synthetic"
payload={"value":"example"}
```

No names, symptoms, documents, diagnoses, provider contacts, or other health-like data.

---

# 154. Repository Ownership Documentation

Update backend developer docs with:

```text
outbox owned by platform events
module business tables remain module-owned
module code enqueues within existing transaction
dispatcher is manual service in P3-B
worker activation deferred P3-C
```

---

# 155. At-Least-Once Documentation

Explicitly document:

```text
outbox insertion is atomic with DB change
delivery is at-least-once
consumer side effects must be idempotent
```

Do not use "exactly-once".

---

# 156. Retry Documentation

Document:

```text
PENDING
DISPATCHED
FAILED
attempt_count
available_at
last_error_code
```

No raw failure text.

---

# 157. Source Material

Do not modify:

```text
docs/source_material/**
```

No clinical source review is required for this generic infrastructure phase.

---

# 158. Documentation Updates

Expected:

```text
README.md
backend/README.md
REPOSITORY_TREE.txt
docs/05_DATABASE_SCHEMA.md
docs/implementation/38_PROGRESS_TRACKER.md
docs/codex/CODEX_PHASE_PROMPTS/P3_B_EVENT_OUTBOX.md
```

The `05_DATABASE_SCHEMA.md` change is only the explicit envelope/outbox drift reconciliation described above.

`docs/research/THIRD_PARTY_COMPONENT_REGISTER.md` should not need change because no new third-party component is introduced.

Do not create a new ADR unless a genuinely new architecture decision is required.

---

# 159. Migration Documentation

Record:

```text
revision p3b_0002
parent p3a_0001
table outbox_events
```

Do not list synthetic test probe tables as schema.

---

# 160. Progress Tracker — Local Stage

After local implementation passes but before remote CI:

```text
P3-B = PARTIAL — REMOTE CI VERIFICATION PENDING
P3 = PARTIAL
```

Record:

```text
base SHA
branch
implementation SHA
migration revision
atomicity tests
dispatcher tests
local Postgres results
AC-P3-004/005/006 local status
remaining P3-C
```

---

# 161. Progress Tracker — CI Closure

Only after all six mandatory branch jobs are green:

```text
P3-B = COMPLETE
P3 = PARTIAL
```

Record:

```text
CI run ID
CI URL
head SHA
AC-P3-004 PASS
AC-P3-005 PASS
AC-P3-006 PASS
next = P3-C — Jobs, Worker Abstraction & Object Storage
```

Do not mark P3 complete.

---

# 162. Unit Verification

Run from `backend/`:

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

All must pass.

---

# 163. Postgres Verification

Against a fresh local PostgreSQL:

```text
uv run alembic -c alembic.ini heads
uv run alembic -c alembic.ini upgrade head
uv run alembic -c alembic.ini current
uv run alembic -c alembic.ini check
uv run pytest -m postgres
```

Verify relevant Postgres tests execute, not skip.

---

# 164. Migration Downgrade Verification

Verify:

```text
upgrade p3b_0002
downgrade p3a_0001
outbox_events absent
upgrade head
outbox_events present
alembic check clean
```

If also testing downgrade to base, re-upgrade to head before finishing.

---

# 165. Root Quality Gates

Run:

```text
python scripts/quality_gate.py backend
python scripts/quality_gate.py frontend
```

Frontend remains regression-only.

---

# 166. Dependency Diff

Run:

```text
git diff -- backend/pyproject.toml backend/uv.lock package.json pnpm-lock.yaml
```

Expected:

```text
no dependency change
```

Any change requires investigation.

---

# 167. Database Schema Diff

Inspect migration manually.

Confirm it contains ONLY:

```text
outbox_events
constraints/indexes for outbox_events
```

No surprise domain table.

No extension.

No audit/jobs table.

---

# 168. Privacy Audit

Before commit verify:

```text
no raw event payload logging
no exception message persistence
no actor_ref metrics
no correlation IDs in metric labels
no credentials
no patient-like fixtures
```

---

# 169. Architecture Audit

Before commit verify:

```text
no worker loop
no job abstraction
no object storage
no broker
no Redis/Valkey
no pgvector
no product module
no domain ORM models
no HTTP event API
no audit persistence
no dynamic handler discovery
no exactly-once claim
```

---

# 170. Git Audit

Run:

```text
git status --short
git diff --stat
git diff
git diff --check
```

Inspect all changed files.

Do not commit:

```text
.env
Postgres volume data
SQL dumps
event payload dumps
pytest caches
temporary Alembic output
```

---

# 171. Commit & Push

After local verification:

```text
git add <P3-B files only>
git commit -m "feat: establish P3-B transactional outbox"
git push -u origin phase/p3-b-event-outbox
```

Do not merge.

Do not force-push.

---

# 172. Remote CI

Verify all mandatory jobs:

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
gh run list --branch phase/p3-b-event-outbox
gh run watch <run-id> --exit-status
```

Do not claim green without evidence.

---

# 173. Closure Commit

If implementation is pushed before CI finishes:

1. keep P3-B partial;
2. wait for CI;
3. fix real failures;
4. after green CI update tracker;
5. set P3-B complete;
6. keep P3 partial;
7. record CI evidence;
8. set next P3-C;
9. create focused docs closure commit;
10. push same branch.

Do not merge.

---

# 174. CI Failure Rules

Do not:

```text
skip Postgres outbox tests
disable alembic check
remove retry test
mark Persistence integration continue-on-error
weaken Trivy/Gitleaks
remove SKIP LOCKED merely to avoid concurrency issue without investigation
```

Fix the implementation.

If a real architectural blocker is discovered, report BLOCKED.

---

# 175. P3 Acceptance Evaluation

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

Expected after successful P3-B:

```text
AC-P3-001 PASS
AC-P3-002 PASS
AC-P3-003 PASS
AC-P3-004 PASS
AC-P3-005 PASS
AC-P3-006 PASS
AC-P3-007 NOT YET IMPLEMENTED
AC-P3-008 NOT YET IMPLEMENTED
AC-P3-009 NOT YET IMPLEMENTED
AC-P3-010 PASS
```

Use actual evidence rather than forcing the expected statuses.

---

# 176. Final Report Format

Return exactly these sections.

## STATUS

One of:

```text
COMPLETE
PARTIAL
BLOCKED
FAILED
```

`COMPLETE` requires all six remote CI jobs green.

## SPECIFICATION DRIFT

Report:

```text
Detected: YES/NO
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
closure SHA if any
remote SHA
main SHA
working-tree state
```

## SCOPE IMPLEMENTED

Describe only P3-B.

## EVENT ENVELOPE

Report:

```text
type/location
event ID representation
event type representation/validation
event version
occurred_at behavior
correlation ID
causation ID
actor_ref
payload representation
immutability
repr/log privacy behavior
```

## EVENT PUBLISHER

Report:

```text
publisher protocol
handler protocol
in-process implementation
registration behavior
no-handler behavior
handler-failure behavior
idempotency semantics
```

## OUTBOX MODEL

Report:

```text
ORM type/location
table name
fields
status enum
constraints
indexes
platform ownership
domain model count
```

Expected:

```text
platform persistence models: 1
domain/business models: 0
```

## OUTBOX REPOSITORY

Report:

```text
enqueue semantics
caller session requirement
commit behavior
due selection
row locking
status mutation methods
```

## ATOMICITY

Report real PostgreSQL evidence for:

```text
synthetic domain/probe change + outbox commit
synthetic domain/probe change + outbox rollback
same session
same transaction
```

## DISPATCHER

Report:

```text
dispatcher type/location
manual invocation
batch bound
selection order
publisher integration
transaction scope
at-least-once semantics
```

## RETRY / STATUS

Report exact behavior for:

```text
new event
successful first attempt
retryable failure
later success
terminal failure
future-dated event
DISPATCHED non-redelivery
FAILED non-redelivery
safe last_error_code
```

## IDEMPOTENCY

Report:

```text
synthetic duplicate-delivery test
handler-side dedupe mechanism
side effect count
exactly-once claim = NO
```

## ALEMBIC / MIGRATION

Report:

```text
revision
parent revision
migration file
created tables
indexes
constraints
downgrade
target metadata registration
```

## MIGRATION VERIFICATION

Report:

```text
fresh DB
heads
upgrade
current
alembic check
downgrade to p3a
re-upgrade
schema inspection
alembic_version
```

## FILES CHANGED

Group:

```text
event contracts
outbox persistence
dispatcher/publisher
migration
tests
CI
documentation
```

## DEPENDENCIES

Expected:

```text
No new runtime/dev dependency.
```

Report whether:

```text
backend/pyproject.toml changed
backend/uv.lock changed
package.json changed
pnpm-lock.yaml changed
```

## TESTS

Report:

```text
new unit test count
new PostgreSQL integration test count
total backend test count
Postgres executed/pass/skip
atomicity tests
dispatcher/retry tests
idempotency fixture
privacy tests
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
dependency diff
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

Use canonical status vocabulary.

## ARCHITECTURE / GOVERNANCE CHECK

Explicitly report:

```text
Transactional outbox uses PostgreSQL source of truth: YES/NO
Event envelope independent of SQLAlchemy/FastAPI: YES/NO
Outbox enqueue never commits caller transaction: YES/NO
Atomic domain-change + event write verified: YES/NO
At-least-once semantics documented: YES/NO
No exactly-once claim: YES/NO
No raw payload logging: YES/NO
No raw exception text persisted: YES/NO
No domain/business ORM models introduced: YES/NO
No worker/job abstraction pulled forward: YES/NO
No object storage pulled forward: YES/NO
No Redis/Valkey/broker/pgvector added: YES/NO
No HTTP event/outbox API introduced: YES/NO
No dynamic handler/plugin discovery: YES/NO
P2 contracts preserved: YES/NO
P3-A persistence/readiness contracts preserved: YES/NO
```

## DEVIATIONS

List every deviation and reason.

## BLOCKERS / OPEN DECISIONS

Only genuine unresolved items.

## PROGRESS TRACKER

State:

```text
P3-B status
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

If P3-B is complete:

```text
P3-C — Jobs, Worker Abstraction & Object Storage
```

Do not implement it.

---

# 177. Success Definition

P3-B is successful only when:

- the canonical versioned event envelope exists;
- event envelope is framework/persistence independent;
- event IDs are opaque UUIDs;
- event timestamps are timezone-aware UTC;
- payload is JSON-compatible and privacy-minimized by contract;
- envelope/outbox specification drift is explicitly reconciled;
- `outbox_events` is the only new persistent application table;
- the outbox table preserves the full canonical envelope;
- deterministic indexes/constraints exist;
- status lifecycle is explicit;
- enqueue uses caller-provided session and never commits;
- a real PostgreSQL integration test proves domain/probe + outbox atomic commit;
- a real PostgreSQL integration test proves atomic rollback;
- dispatcher selects only due PENDING events;
- dispatcher uses concurrency-safe row locking;
- successful dispatch updates attempt/status/timestamp correctly;
- transient failure schedules retry safely;
- terminal retry exhaustion becomes FAILED;
- raw exception text is not persisted;
- DISPATCHED/FAILED rows are not automatically redelivered;
- delivery semantics are documented as at-least-once;
- synthetic idempotent-handler fixture tolerates duplicate delivery;
- no exactly-once claim is made;
- minimal in-process publisher is explicit and transport-independent;
- no worker/background loop is activated;
- no broker/Redis/Valkey is added;
- no P3-C/P4/domain/clinical/AI work is pulled forward;
- migration `p3b_0002` upgrades cleanly from P3-A;
- downgrade/re-upgrade works;
- Alembic check is clean;
- PostgreSQL integration tests execute with zero relevant skips in CI;
- P3-A tests/readiness remain green;
- all backend/frontend quality gates pass;
- Gitleaks/Trivy pass;
- all six mandatory CI jobs pass;
- AC-P3-004, AC-P3-005, and AC-P3-006 pass;
- P3-B is marked COMPLETE;
- overall P3 remains PARTIAL;
- branch is pushed but not merged.

Stop after P3-B.
