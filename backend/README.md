# SwasthyaSetu backend

This directory contains the FastAPI engineering foundation, P2 shared kernel, and P3-A PostgreSQL
persistence substrate. It intentionally has no clinical logic, domain ORM models, outbox, jobs,
object storage, or active external providers.

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

These tests use and remove only the synthetic `p3a_transaction_probe` table. Do not point this
variable at an unapproved or production database.

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
