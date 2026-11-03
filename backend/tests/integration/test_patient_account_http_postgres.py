"""Real FastAPI/PostgreSQL patient account contract verification."""

import os
from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from app.config import DatabaseSettings, Environment, Settings
from app.main import create_app
from app.shared.persistence import DatabaseRuntime

pytestmark = pytest.mark.postgres
TRUNCATE = text(
    "TRUNCATE TABLE patient_documents, patient_accounts, intake_answers, "
    "questionnaire_instances, clinical_intakes, observations, allergies, medications, "
    "clinical_fact_provenance, clinical_facts, encounters, patient_identifiers, "
    "patient_demographics, patients, consent_records, sessions, actor_roles, actors, "
    "outbox_events CASCADE"
)


@pytest.fixture
async def database_runtime() -> AsyncIterator[DatabaseRuntime]:
    url = os.getenv("SWASTHYASETU_TEST_DATABASE_URL")
    if url is None:
        pytest.skip("SWASTHYASETU_TEST_DATABASE_URL is not configured")
    runtime = DatabaseRuntime(DatabaseSettings(enabled=True, url=url))
    async with runtime.engine.begin() as connection:
        await connection.execute(TRUNCATE)
    try:
        yield runtime
    finally:
        async with runtime.engine.begin() as connection:
            await connection.execute(TRUNCATE)
        await runtime.dispose()


async def test_account_http_lifecycle_and_cross_account_isolation(
    database_runtime: DatabaseRuntime,
) -> None:
    application = create_app(
        Settings(environment=Environment.TEST, _env_file=None), database=database_runtime
    )
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        first = await client.post(
            "/api/v1/accounts/register",
            json={
                "email": "first@example.com",
                "display_name": "First Patient",
                "password": "correct horse battery staple",
                "preferred_language": "en",
            },
        )
        second = await client.post(
            "/api/v1/accounts/register",
            json={
                "email": "second@example.com",
                "display_name": "Second Patient",
                "password": "another correct horse password",
            },
        )
        first_token = first.json()["session_token"]
        second_token = second.json()["session_token"]
        first_me = await client.get(
            "/api/v1/accounts/me", headers={"Authorization": f"Bearer {first_token}"}
        )
        second_me = await client.get(
            "/api/v1/accounts/me", headers={"Authorization": f"Bearer {second_token}"}
        )
        logout = await client.post(
            "/api/v1/accounts/logout", headers={"Authorization": f"Bearer {first_token}"}
        )
        closed = await client.get(
            "/api/v1/accounts/me", headers={"Authorization": f"Bearer {first_token}"}
        )
        login = await client.post(
            "/api/v1/accounts/login",
            json={
                "email": "FIRST@EXAMPLE.COM",
                "password": "correct horse battery staple",
            },
        )

    assert first.status_code == 201
    assert second.status_code == 201
    assert first_me.status_code == 200
    assert second_me.status_code == 200
    assert first_me.json()["email"] == "first@example.com"
    assert second_me.json()["email"] == "second@example.com"
    assert first_me.json()["patient_id"] != second_me.json()["patient_id"]
    assert logout.status_code == 204
    assert closed.status_code == 401
    assert first_token not in closed.text
    assert login.status_code == 200
    assert login.json()["session_token"] not in {first_token, second_token}
    assert all(
        response.headers["cache-control"] == "no-store"
        for response in (first, second, first_me, second_me, logout, closed, login)
    )
