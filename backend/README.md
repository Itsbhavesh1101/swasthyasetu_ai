# SwasthyaSetu backend

This directory contains the FastAPI engineering foundation, P2 shared kernel, P3-A PostgreSQL
persistence substrate, P3-B platform event/outbox foundation, and P3-C job/object-storage
contracts and local scaffolds. It intentionally has no clinical logic, domain ORM models, durable
job backend, production object storage, or active external providers.

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) for locked dependency management

## Install

From `backend/`:

```powershell
uv sync --locked --dev
Copy-Item .env.example .env
```

The `.env` file is ignored by Git. The committed example contains no secrets.

The original P1 variables remain supported: `SWASTHYASETU_APP_NAME`,
`SWASTHYASETU_ENVIRONMENT`, `SWASTHYASETU_DEBUG`, `SWASTHYASETU_API_V1_PREFIX`, and
`SWASTHYASETU_LOG_LEVEL`. Minimal future-integration sections can be supplied as JSON environment
values such as `SWASTHYASETU_DATABASE`. Database configuration also supports nested variables such
as `SWASTHYASETU_DATABASE__ENABLED` and `SWASTHYASETU_DATABASE__URL`; it remains disabled by
default. P2-C feature configuration accepts immutable JSON using
synthetic names, for example `SWASTHYASETU_FEATURES={"enabled":["example_feature"]}`. No feature
is enabled by default.

## PostgreSQL and migrations

P3-A uses SQLAlchemy's async engine with the explicit `postgresql+psycopg` driver. Each application
owns its runtime, async session factory, bounded `SELECT 1` readiness probe, and shutdown disposal.
`DatabaseRuntime.transaction()` opens one session per use case, commits on successful exit, rolls
back on exceptions, and always closes the session. Future ORM models remain module-owned; shared
persistence contains only `Base`, deterministic constraint naming, runtime, and session primitives.

Start PostgreSQL from the repository root, then from `backend/` set synthetic host-local values:

```powershell
$env:SWASTHYASETU_DATABASE__ENABLED = "true"
$env:SWASTHYASETU_DATABASE__URL = "postgresql+psycopg://swasthyasetu_dev:local-only-synthetic-password@127.0.0.1:5432/swasthyasetu"
uv run alembic -c alembic.ini upgrade head
uv run uvicorn app.main:app --reload
```

Migrations are an explicit deployment step and never run during API startup. Useful checks are:

```powershell
uv run alembic -c alembic.ini heads
uv run alembic -c alembic.ini current
uv run alembic -c alembic.ini check
```

Real integration tests additionally require the explicit test-only variable:

```powershell
$env:SWASTHYASETU_TEST_DATABASE_URL = $env:SWASTHYASETU_DATABASE__URL
uv run pytest -m postgres
```

These tests use and remove only synthetic `p3a_transaction_probe` / `p3b_atomicity_probe` tables
and P3-B synthetic outbox rows. Do not point this variable at an unapproved or production database.

## Events and transactional outbox

`app.events` owns the immutable versioned envelope, provider-neutral publisher contract, explicit
in-process publisher, `outbox_events` model/repository, and manually invoked `OutboxDispatcher`.
Module-specific payload schemas and handlers stay with future owning modules. Payloads must be
privacy-minimized JSON metadata; they are not transcript archives, document dumps, or substitutes
for canonical domain storage. Event types, correlation IDs, causation IDs, actor references, and
aggregate types use bounded 128-character storage; actor references remain opaque and
non-authoritative.

Callers enqueue through `OutboxRepository` using the same caller-owned `AsyncSession` and
transaction as their state change. Enqueue never commits. The dispatcher selects due `PENDING`
rows in `available_at`, `created_at`, `id` order using `FOR UPDATE SKIP LOCKED`, holds the row lock
through publication, then commits one row outcome per transaction. It is a manual service only and
is never auto-started by FastAPI.

Delivery is at-least-once: a crash after handler side effects but before the status commit can
redeliver an event. Side-effecting consumers must therefore implement idempotency. Failures persist
only the generic `EVENT_DELIVERY_FAILED` code, never exception text or payload data. Retry metadata
changes do not alter the immutable historical envelope.

Migration `p3b_0002` (parent `p3a_0001`) creates only `outbox_events`. Apply it through the same
explicit Alembic deployment commands above; API startup never runs migrations or the dispatcher.

## Jobs and worker scaffold

`app.jobs` owns immutable `JobType`, `JobRequest`, `JobHandle`, and `JobStatus` contracts plus the
provider-neutral `JobDispatcher` protocol. `InProcessJobDispatcher` and its shared backend are
non-durable, process-local development/test scaffolding: queued state is lost on restart and cannot
be shared across processes. Enqueue only records a job; execution happens separately and only when
`InProcessWorker.run_once()` is explicitly called. Handlers are registered explicitly and frozen
at worker construction.

No daemon, process loop, or FastAPI background worker starts automatically. Failures retain only
generic codes, never payloads, raw exception messages, or stack traces. This scaffold makes no
exactly-once claim. A PostgreSQL-native durable-job spike, with Procrastinate as the preferred
candidate, remains deferred until durability is required.

## Object storage

`app.shared.storage` owns the provider-neutral `ObjectStoragePort`, validated `ObjectKey`, result
metadata, and typed errors. `app.adapters.storage.LocalFilesystemObjectStorage` implements exact
byte put/get/exists/delete behavior under an explicitly injected root, using semantic path
containment, symlink-escape checks, atomic local replacement, and thread-offloaded filesystem I/O.

The local adapter is development/test only. It is not production object storage or an untrusted
medical-upload boundary and makes no encryption, malware scanning, quarantine, medical-grade
durability, or compliance claim. SeaweedFS and S3 adapters remain deferred; MinIO is not selected.

## Run the API

```powershell
uv run uvicorn app.main:app --reload
```

The foundation endpoints are:

- `GET /health/live`
- `GET /health/ready`

With the database disabled, readiness has no required dependencies. With it enabled, readiness
reports `required.database=ok` or returns HTTP 503 with `database=unavailable`; liveness remains
process-only and never exposes connection details.

Normal product APIs will be registered below `/api/v1` in their owning phases.

## Sessions

The default application explicitly registers the `sessions` module through the sealed module and
capability registries. With PostgreSQL enabled and migrated, P4-A exposes:

- `POST /api/v1/sessions`
- `GET /api/v1/sessions/{session_id}`
- `POST /api/v1/sessions/{session_id}/close`

Creation supports only `PSEUDONYMOUS` and `KIOSK`. It returns a high-entropy opaque bearer token
once and stores only its SHA-256 hash. Subsequent read/close calls require
`Authorization: Bearer <session_token>`. Responses use `Cache-Control: no-store`; token/hash values
are excluded from normal views and logs. PostgreSQL remains authoritative for expiry and close
state. Token expiry is not a data-retention or deletion policy, and P4-A implements no purge or
lost-token recovery flow.

Foundation TTL defaults are 60 minutes for pseudonymous sessions and 30 minutes for kiosk
sessions. Override them with `SWASTHYASETU_SESSIONS__PSEUDONYMOUS_TTL_MINUTES` and
`SWASTHYASETU_SESSIONS__KIOSK_TTL_MINUTES`. Production values require security/privacy review.

Migration `p4a_0003` (parent `p3b_0002`) creates only `sessions` and its constraints/indexes.
Migrations remain an explicit deployment step and are never run by API startup.

## Module composition

Future module `public.py` boundaries can supply immutable `ModuleRegistration` values to
`create_app(module_registrations=(...))`. Each registration explicitly declares its manifest,
routers, and typed capability bindings. Application construction validates the complete required
capability set, seals both registries, mounts supplied routers below `/api/v1`, and exposes the
sealed composition metadata as `application.state.module_registry` and
`application.state.capability_registry`.

Registrations are explicit imports assembled at startup. Runtime plugin discovery, package
scanning, global registries, and request-time provider mutation are intentionally unsupported.

## Feature flags and observability

`application.state.feature_flags` exposes the provider-neutral `FeatureFlagService`. Valid but
absent flags evaluate to `False`; configuration is immutable for the process lifetime. Flags do
not provide authorization and must not encode clinical policy. Manifest flag names remain
declaration metadata and do not alter module registration.

`application.state.observability` owns isolated OpenTelemetry tracer and meter providers. Manual
HTTP instrumentation emits `swasthyasetu.http.server.requests` and
`swasthyasetu.http.server.duration` (milliseconds) with bounded method, route-template, and status
attributes. Spans and JSON logs can correlate request, trace, and span identifiers without raw
bodies, query strings, credentials, cookies, or exception details. External export is disabled by
default and enabling it is rejected because P2-C installs no exporter. No Collector or monitoring
service is required.

## Quality checks

```powershell
uv lock --check
uv sync --locked --dev
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
uv run python -m compileall -q app tests
uv run python -c "from app.main import app; assert app.title == 'SwasthyaSetu AI'"
```

To format backend Python files:

```powershell
uv run ruff format .
```
