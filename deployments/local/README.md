# Local container foundation

This environment contains only PostgreSQL and the backend container. P3-A enables backend database
connectivity using the committed synthetic local credentials; migrations remain an explicit command.

## Prerequisites

- Docker Desktop or Docker Engine with Compose support.
- Ports 5432 and 8000 available, or alternate loopback ports configured in the local `.env`.

## Configure local values

From the repository root in PowerShell:

```powershell
Copy-Item deployments/local/.env.example deployments/local/.env
```

The committed password is explicitly synthetic and local-only. Change the ignored `.env` value if
the environment is shared with other local users.

## Start and verify PostgreSQL

```powershell
docker compose --env-file deployments/local/.env -f deployments/local/compose.yaml config
docker compose --env-file deployments/local/.env -f deployments/local/compose.yaml up -d postgres
docker compose --env-file deployments/local/.env -f deployments/local/compose.yaml ps
docker compose --env-file deployments/local/.env -f deployments/local/compose.yaml exec -T postgres pg_isready -U swasthyasetu_dev -d swasthyasetu
docker compose --env-file deployments/local/.env -f deployments/local/compose.yaml exec -T postgres psql -U swasthyasetu_dev -d swasthyasetu -c "SELECT 1;"
```

PostgreSQL uses the official pinned `postgres:16.12-bookworm` image and a named Docker volume. It is
bound to loopback rather than exposed publicly.

## Start the backend container

```powershell
docker compose --env-file deployments/local/.env -f deployments/local/compose.yaml build backend
docker compose --env-file deployments/local/.env -f deployments/local/compose.yaml run --rm backend alembic -c /app/alembic.ini upgrade head
docker compose --env-file deployments/local/.env -f deployments/local/compose.yaml up -d backend
Invoke-RestMethod http://127.0.0.1:8000/health/live
Invoke-RestMethod http://127.0.0.1:8000/health/ready
```

The ready response must contain `required.database = "ok"`. API startup never runs migrations, so
deployments must execute the Alembic command once before starting or updating application replicas.

The backend image runs as non-root user `10001:10001` and exposes port 8000 locally.
It uses the official immutable
`python:3.12.15-alpine3.23@sha256:1fd55c2f838c4f76262f9eeed899ff9168ea96ac383c61667d6f204325e1f169`
base without mutating its operating-system package set during the build.

## Stop or reset

Stop containers while preserving the PostgreSQL volume:

```powershell
docker compose --env-file deployments/local/.env -f deployments/local/compose.yaml down
```

Intentionally delete this environment's synthetic database volume and all local data:

```powershell
docker compose --env-file deployments/local/.env -f deployments/local/compose.yaml down -v
```

The volume command targets only `swasthyasetu-local-postgres-data`. Do not use broad Docker prune
commands.
