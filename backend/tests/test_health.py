"""Canonical health endpoint contract tests."""

from unittest.mock import AsyncMock

from httpx import ASGITransport, AsyncClient

from app.config import DatabaseSettings, Settings
from app.main import create_app


async def test_liveness_is_dependency_free(client: AsyncClient) -> None:
    response = await client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_readiness_reports_only_current_dependencies(client: AsyncClient) -> None:
    response = await client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready", "required": {}, "optional": {}}


async def test_database_success_is_required_readiness_dependency() -> None:
    database = AsyncMock()
    settings = Settings(
        database=DatabaseSettings(
            enabled=True,
            url="postgresql+psycopg://synthetic:secret@localhost/synthetic",
        ),
        _env_file=None,
    )
    application = create_app(settings, database=database)

    async with AsyncClient(
        transport=ASGITransport(app=application), base_url="http://test"
    ) as client:
        response = await client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "required": {"database": "ok"},
        "optional": {},
    }
    database.ping.assert_awaited_once_with()


async def test_database_failure_blocks_readiness_without_affecting_liveness() -> None:
    secret = "synthetic-password-that-must-not-leak"
    database = AsyncMock()
    database.ping.side_effect = RuntimeError(
        f"could not connect to postgresql+psycopg://user:{secret}@db/private"
    )
    settings = Settings(
        database=DatabaseSettings(
            enabled=True,
            url=f"postgresql+psycopg://user:{secret}@127.0.0.1:1/synthetic",
            connect_timeout_seconds=1,
        ),
        _env_file=None,
    )
    application = create_app(settings, database=database)

    async with AsyncClient(
        transport=ASGITransport(app=application), base_url="http://test"
    ) as client:
        live = await client.get("/health/live")
        ready = await client.get("/health/ready")

    assert live.status_code == 200
    assert live.json() == {"status": "ok"}
    assert ready.status_code == 503
    assert ready.json() == {
        "status": "not_ready",
        "required": {"database": "unavailable"},
        "optional": {},
    }
    assert secret not in ready.text
    assert "psycopg" not in ready.text


async def test_unreachable_database_failure_is_bounded_and_privacy_safe() -> None:
    secret = "unreachable-secret"
    settings = Settings(
        database=DatabaseSettings(
            enabled=True,
            url=f"postgresql+psycopg://user:{secret}@127.0.0.1:1/synthetic",
            connect_timeout_seconds=1,
            pool_timeout_seconds=1,
        ),
        _env_file=None,
    )
    application = create_app(settings)

    async with (
        application.router.lifespan_context(application),
        AsyncClient(transport=ASGITransport(app=application), base_url="http://test") as client,
    ):
        live = await client.get("/health/live")
        ready = await client.get("/health/ready")

    assert live.status_code == 200
    assert ready.status_code == 503
    assert ready.json()["required"] == {"database": "unavailable"}
    assert secret not in ready.text
    assert "127.0.0.1" not in ready.text
