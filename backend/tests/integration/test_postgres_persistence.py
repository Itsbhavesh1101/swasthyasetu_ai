"""Real PostgreSQL verification for P3-A persistence behavior."""

from __future__ import annotations

import os
from collections.abc import AsyncIterator

import pytest
from sqlalchemy import text

from app.config import DatabaseSettings
from app.shared.persistence import DatabaseRuntime

pytestmark = pytest.mark.postgres
PROBE_TABLE = "p3a_transaction_probe"


@pytest.fixture
async def database_runtime() -> AsyncIterator[DatabaseRuntime]:
    """Use only the explicit test URL and always remove the synthetic probe."""
    test_url = os.getenv("SWASTHYASETU_TEST_DATABASE_URL")
    if test_url is None:
        pytest.skip("SWASTHYASETU_TEST_DATABASE_URL is not configured")
    runtime = DatabaseRuntime(DatabaseSettings(enabled=True, url=test_url))
    async with runtime.engine.begin() as connection:
        await connection.execute(
            text(f"CREATE TABLE IF NOT EXISTS {PROBE_TABLE} (value TEXT PRIMARY KEY)")
        )
        await connection.execute(text(f"TRUNCATE TABLE {PROBE_TABLE}"))
    try:
        yield runtime
    finally:
        async with runtime.engine.begin() as connection:
            await connection.execute(text(f"DROP TABLE IF EXISTS {PROBE_TABLE}"))
        await runtime.dispose()


async def test_postgres_ping_and_successful_transaction_commit(
    database_runtime: DatabaseRuntime,
) -> None:
    await database_runtime.ping()

    async with database_runtime.transaction() as session:
        await session.execute(
            text(f"INSERT INTO {PROBE_TABLE} (value) VALUES (:value)"),
            {"value": "commit"},
        )

    async with database_runtime.engine.connect() as connection:
        value = await connection.scalar(
            text(f"SELECT value FROM {PROBE_TABLE} WHERE value = :value"),
            {"value": "commit"},
        )
    assert value == "commit"


async def test_postgres_transaction_rolls_back_and_pool_remains_usable(
    database_runtime: DatabaseRuntime,
) -> None:
    with pytest.raises(RuntimeError, match="synthetic rollback"):
        async with database_runtime.transaction() as session:
            await session.execute(
                text(f"INSERT INTO {PROBE_TABLE} (value) VALUES (:value)"),
                {"value": "rollback"},
            )
            raise RuntimeError("synthetic rollback")

    async with database_runtime.engine.connect() as connection:
        count = await connection.scalar(
            text(f"SELECT count(*) FROM {PROBE_TABLE} WHERE value = :value"),
            {"value": "rollback"},
        )
        assert await connection.scalar(text("SELECT 1")) == 1
    assert count == 0
