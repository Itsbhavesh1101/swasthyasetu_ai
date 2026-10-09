# SwasthyaSetu backend

This directory contains the P1-A FastAPI engineering foundation. It intentionally has no
clinical logic, persistence, external providers, or deployment infrastructure.

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

