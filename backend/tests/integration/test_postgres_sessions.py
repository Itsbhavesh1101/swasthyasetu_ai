"""Real PostgreSQL and HTTP contract verification for P4-A sessions."""

from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncGenerator, AsyncIterator
from datetime import UTC, datetime, timedelta, timezone

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select, text

from app.config import DatabaseSettings, SessionsSettings, Settings
from app.main import create_app
from app.modules.sessions.application import SessionService
from app.modules.sessions.domain import SessionType
from app.modules.sessions.infrastructure import PostgresSessionRepository, SessionRecord
from app.modules.sessions.public import build_sessions_registration
from app.shared.persistence import DatabaseRuntime

pytestmark = pytest.mark.postgres


@pytest.fixture
async def database_runtime() -> AsyncIterator[DatabaseRuntime]:
    test_url = os.getenv("SWASTHYASETU_TEST_DATABASE_URL")
    if test_url is None:
        pytest.skip("SWASTHYASETU_TEST_DATABASE_URL is not configured")
    runtime = DatabaseRuntime(DatabaseSettings(enabled=True, url=test_url))
    async with runtime.engine.begin() as connection:
        await connection.execute(text("TRUNCATE TABLE sessions CASCADE"))
    try:
        yield runtime
    finally:
        async with runtime.engine.begin() as connection:
            await connection.execute(text("TRUNCATE TABLE sessions CASCADE"))
        await runtime.dispose()


async def _client(
    runtime: DatabaseRuntime,
    *,
    now: datetime,
    token: str = "synthetic-session-token-marker",
) -> AsyncGenerator[AsyncClient, None]:
    settings = Settings(
        database=DatabaseSettings(
            enabled=True, url="postgresql+psycopg://unused:unused@localhost/unused"
        ),
        sessions=SessionsSettings(),
        _env_file=None,
    )
    registration = build_sessions_registration(
        settings=settings.sessions,
        database=runtime,
        clock=lambda: now,
        token_factory=lambda: token,
    )
    application = create_app(
        settings,
        database=runtime,
        module_registrations=(registration,),
    )
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


async def test_postgres_http_lifecycle_hash_privacy_and_cross_session_binding(
    database_runtime: DatabaseRuntime,
    caplog: pytest.LogCaptureFixture,
) -> None:
    now = datetime(2026, 10, 11, 8, tzinfo=UTC)
    clients = _client(database_runtime, now=now)
    client = await anext(clients)
    try:
        created = await client.post(
            "/api/v1/sessions",
            json={"session_type": "PSEUDONYMOUS", "language_preference": " hi-Latn "},
        )
        assert created.status_code == 201
        body = created.json()
        session_id = body["session_id"]
        token = body["session_token"]
        assert token == "synthetic-session-token-marker"
        assert body["status"] == "ACTIVE"
        assert created.headers["cache-control"] == "no-store"
        assert "hash" not in created.text.lower()

        async with database_runtime.session_factory() as session:
            record = (await session.execute(select(SessionRecord))).scalar_one()
        persisted = " ".join(str(value) for value in vars(record).values())
        assert token not in persisted
        assert len(record.token_hash) == 64
        assert record.recovery_token_hash is None
        assert record.actor_id is None
        assert record.patient_id is None

        authorized = await client.get(
            f"/api/v1/sessions/{session_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert authorized.status_code == 200
        assert authorized.json()["language_preference"] == "hi-Latn"
        assert "token" not in authorized.text.lower()
        assert authorized.headers["cache-control"] == "no-store"

        missing = await client.get(f"/api/v1/sessions/{session_id}")
        wrong = await client.get(
            f"/api/v1/sessions/{session_id}",
            headers={"Authorization": "Bearer wrong-token"},
        )
        assert missing.status_code == wrong.status_code == 401
        assert missing.json()["error"]["code"] == "AUTHENTICATION_REQUIRED"
        assert wrong.json()["error"]["code"] == "AUTHENTICATION_REQUIRED"
        assert token not in caplog.text

        unknown = await client.get(
            "/api/v1/sessions/00000000-0000-4000-8000-000000000001",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert unknown.status_code == 401
        assert unknown.json()["error"]["code"] == "AUTHENTICATION_REQUIRED"

        second_clients = _client(database_runtime, now=now, token="second-session-token-marker")
        second_client = await anext(second_clients)
        try:
            second = await second_client.post("/api/v1/sessions", json={"session_type": "KIOSK"})
        finally:
            await second_clients.aclose()
        cross = await client.get(
            f"/api/v1/sessions/{second.json()['session_id']}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert cross.status_code == 401
        assert cross.json()["error"]["code"] == "AUTHENTICATION_REQUIRED"

        closed = await client.post(
            f"/api/v1/sessions/{session_id}/close",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert closed.status_code == 200
        assert closed.json()["status"] == "CLOSED"
        assert closed.json()["closed_at"] == now.isoformat().replace("+00:00", "Z")
        repeated = await client.post(
            f"/api/v1/sessions/{session_id}/close",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert repeated.status_code == 409
        assert repeated.json()["error"]["code"] == "INVALID_STATE_TRANSITION"
        closed_read = await client.get(
            f"/api/v1/sessions/{session_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert closed_read.status_code == 409
        assert closed_read.json()["error"]["code"] == "INVALID_STATE_TRANSITION"
    finally:
        await clients.aclose()


async def test_expiry_boundary_and_kiosk_ttl(database_runtime: DatabaseRuntime) -> None:
    created_at = datetime(2026, 10, 11, 8, tzinfo=UTC)
    creator_stream = _client(database_runtime, now=created_at, token="expiry-marker")
    creator = await anext(creator_stream)
    try:
        created = await creator.post("/api/v1/sessions", json={"session_type": "KIOSK"})
    finally:
        await creator_stream.aclose()
    assert created.status_code == 201
    assert created.json()["expires_at"] == (created_at + timedelta(minutes=30)).isoformat().replace(
        "+00:00", "Z"
    )

    boundary_stream = _client(
        database_runtime, now=created_at + timedelta(minutes=30), token="unused"
    )
    boundary = await anext(boundary_stream)
    try:
        response = await boundary.get(
            f"/api/v1/sessions/{created.json()['session_id']}",
            headers={"Authorization": "Bearer expiry-marker"},
        )
        close = await boundary.post(
            f"/api/v1/sessions/{created.json()['session_id']}/close",
            headers={"Authorization": "Bearer expiry-marker"},
        )
    finally:
        await boundary_stream.aclose()
    assert response.status_code == close.status_code == 401
    assert response.json()["error"]["code"] == "SESSION_EXPIRED"
    assert close.json()["error"]["code"] == "SESSION_EXPIRED"


async def test_concurrent_close_allows_only_one_success(
    database_runtime: DatabaseRuntime,
) -> None:
    now = datetime(2026, 10, 11, 8, tzinfo=UTC)
    stream = _client(database_runtime, now=now, token="concurrent-close-marker")
    client = await anext(stream)
    try:
        created = await client.post("/api/v1/sessions", json={"session_type": "PSEUDONYMOUS"})
        session_id = created.json()["session_id"]
        headers = {"Authorization": "Bearer concurrent-close-marker"}
        first, second = await asyncio.gather(
            client.post(f"/api/v1/sessions/{session_id}/close", headers=headers),
            client.post(f"/api/v1/sessions/{session_id}/close", headers=headers),
        )
    finally:
        await stream.aclose()

    assert sorted((first.status_code, second.status_code)) == [200, 409]
    conflict = first if first.status_code == 409 else second
    assert conflict.json()["error"]["code"] == "INVALID_STATE_TRANSITION"


async def test_sessions_database_constraints_are_named_and_complete(
    database_runtime: DatabaseRuntime,
) -> None:
    async with database_runtime.engine.connect() as connection:
        constraints: set[str] = set(
            (
                await connection.execute(
                    text("SELECT conname FROM pg_constraint WHERE conrelid = 'sessions'::regclass")
                )
            ).scalars()
        )
        indexes: set[str] = set(
            (
                await connection.execute(
                    text(
                        "SELECT indexname FROM pg_indexes "
                        "WHERE schemaname = 'public' AND tablename = 'sessions'"
                    )
                )
            ).scalars()
        )

    assert {
        "pk_sessions",
        "uq_sessions_token_hash",
        "ck_sessions_session_type_supported",
        "ck_sessions_status_supported",
        "ck_sessions_expiry_after_creation",
    } <= constraints
    assert {
        "ix_sessions_status_expires_at",
        "ix_sessions_patient_id",
        "ix_sessions_actor_id",
    } <= indexes


async def test_clock_invariant_rejects_naive_before_insert_and_normalizes_offsets(
    database_runtime: DatabaseRuntime,
) -> None:
    naive = SessionService(
        database=database_runtime,
        settings=SessionsSettings(),
        repository=PostgresSessionRepository(),
        clock=lambda: datetime(2026, 10, 11, 8),
        token_factory=lambda: "naive-clock-marker",
    )

    with pytest.raises(ValueError, match="timezone-aware"):
        await naive.create_session(
            session_type=SessionType.PSEUDONYMOUS,
            language_preference=None,
        )

    async with database_runtime.engine.connect() as connection:
        assert await connection.scalar(text("SELECT count(*) FROM sessions")) == 0

    offset_time = datetime(
        2026,
        10,
        11,
        13,
        30,
        tzinfo=timezone(timedelta(hours=5, minutes=30)),
    )
    offset = SessionService(
        database=database_runtime,
        settings=SessionsSettings(),
        repository=PostgresSessionRepository(),
        clock=lambda: offset_time,
        token_factory=lambda: "offset-clock-marker",
    )
    created = await offset.create_session(
        session_type=SessionType.PSEUDONYMOUS,
        language_preference=None,
    )

    assert created.session.created_at == datetime(2026, 10, 11, 8, tzinfo=UTC)
    assert created.session.expires_at == datetime(2026, 10, 11, 9, tzinfo=UTC)
