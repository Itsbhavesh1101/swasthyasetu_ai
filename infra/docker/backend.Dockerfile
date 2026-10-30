# syntax=docker/dockerfile:1.7

ARG PYTHON_IMAGE=python:3.12.15-alpine3.23@sha256:1fd55c2f838c4f76262f9eeed899ff9168ea96ac383c61667d6f204325e1f169
ARG UV_IMAGE=ghcr.io/astral-sh/uv:0.12.20@sha256:100047e74f30778ab704942321a09750d6158739573ff58bf3924085cc6cd2d8

FROM ${UV_IMAGE} AS uv

FROM ${PYTHON_IMAGE} AS builder

COPY --from=uv /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv

WORKDIR /build/backend

COPY backend/pyproject.toml backend/uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

FROM ${PYTHON_IMAGE} AS runtime

ENV PATH="/opt/venv/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN addgroup -S -g 10001 app \
    && adduser -S -D -u 10001 -G app -h /home/app app

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY --chown=10001:10001 backend/app ./app
COPY --chown=10001:10001 backend/alembic.ini ./alembic.ini
COPY --chown=10001:10001 backend/migrations ./migrations

USER 10001:10001

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health/live', timeout=2).read()"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-proxy-headers"]
