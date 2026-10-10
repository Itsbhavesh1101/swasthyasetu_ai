# SwasthyaSetu backend

This directory contains the FastAPI engineering foundation and P2-A shared-kernel primitives. It
intentionally has no clinical logic, application persistence, or active external providers.

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
values such as `SWASTHYASETU_DATABASE`, but all integrations default disabled or unconfigured and
P2-A performs no connectivity checks.

## Run the API

```powershell
uv run uvicorn app.main:app --reload
```

The foundation endpoints are:

- `GET /health/live`
- `GET /health/ready`

Normal product APIs will be registered below `/api/v1` in their owning phases.

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
