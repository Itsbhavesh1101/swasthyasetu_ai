"""Real PostgreSQL and HTTP verification for the P7-C structured intake flow."""

from __future__ import annotations

import os
from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import func, select, text

from app.config import DatabaseSettings, Environment, Settings
from app.main import create_app
from app.modules.clinical_intake.infrastructure import (
    ClinicalIntakeRecord,
    IntakeAnswerRecord,
    QuestionnaireInstanceRecord,
)
from app.shared.persistence import DatabaseRuntime

pytestmark = pytest.mark.postgres


@pytest.fixture
async def intake_client() -> AsyncIterator[tuple[AsyncClient, DatabaseRuntime]]:
    url = os.getenv("SWASTHYASETU_TEST_DATABASE_URL")
    if url is None:
        pytest.skip("SWASTHYASETU_TEST_DATABASE_URL is not configured")
    database = DatabaseRuntime(DatabaseSettings(enabled=True, url=url))
    truncate = text(
        "TRUNCATE TABLE intake_answers, questionnaire_instances, clinical_intakes, "
        "encounters, consent_records, sessions, outbox_events CASCADE"
    )
    async with database.engine.begin() as connection:
        await connection.execute(truncate)
    settings = Settings(
        environment=Environment.TEST,
        database=DatabaseSettings(enabled=True, url=url),
        _env_file=None,
    )
    application = create_app(settings, database=database)
    async with AsyncClient(
        transport=ASGITransport(app=application), base_url="http://test"
    ) as client:
        yield client, database
    async with database.engine.begin() as connection:
        await connection.execute(truncate)
    await database.dispose()


async def _onboard(client: AsyncClient) -> tuple[str, str, str]:
    session_response = await client.post(
        "/api/v1/sessions",
        json={"session_type": "PSEUDONYMOUS", "language_preference": "en"},
    )
    assert session_response.status_code == 201
    session = session_response.json()
    headers = {"Authorization": f"Bearer {session['session_token']}"}
    consent_response = await client.post(
        "/api/v1/consents",
        headers=headers,
        json={
            "subject_type": "SESSION",
            "subject_id": session["session_id"],
            "purpose": "GENERAL_PRODUCT_USE",
            "scope": ["clinical_intake"],
            "notice_version": "privacy-v1",
        },
    )
    assert consent_response.status_code == 201
    encounter_response = await client.post(
        "/api/v1/encounters/general-intake",
        headers=headers,
        json={"session_id": session["session_id"]},
    )
    assert encounter_response.status_code == 200
    return (
        session["session_id"],
        session["session_token"],
        encounter_response.json()["encounter_id"],
    )


async def test_real_http_flow_is_atomic_versioned_idempotent_and_session_bound(
    intake_client: tuple[AsyncClient, DatabaseRuntime],
) -> None:
    client, database = intake_client
    _, token, encounter_id = await _onboard(client)
    headers = {"Authorization": f"Bearer {token}"}
    start = await client.post(
        f"/api/v1/encounters/{encounter_id}/intake",
        headers=headers,
        json={"pack_ids": ["core.intake"]},
    )
    assert start.status_code == 201
    assert start.headers["cache-control"] == "no-store"
    started = start.json()
    assert started["version"] == 1
    assert started["current_question"]["question_id"] == "core.chief_complaint"
    replay = await client.post(
        f"/api/v1/encounters/{encounter_id}/intake",
        headers=headers,
        json={"pack_ids": ["core.intake"]},
    )
    assert replay.status_code == 200
    assert replay.json()["intake_id"] == started["intake_id"]

    answer_body = {
        "question_id": "core.chief_complaint",
        "question_version": "engineering.1",
        "answer": {
            "schema_version": "intake-answer.v1",
            "answer_type": "TEXT",
            "value": "Synthetic test concern",
            "selected_option_ids": None,
            "unit": None,
            "response_disposition": "ANSWERED",
            "language_code": "en",
            "original_text": "Synthetic test concern",
        },
        "source_type": "PATIENT_TEXT",
        "expected_version": 1,
    }
    answered_response = await client.post(
        f"/api/v1/intakes/{started['intake_id']}/answers",
        headers=headers,
        json=answer_body,
    )
    assert answered_response.status_code == 200, answered_response.text
    answered = answered_response.json()
    assert answered["version"] == 2
    assert answered["completion_ready"] is True
    stale = await client.post(
        f"/api/v1/intakes/{started['intake_id']}/answers",
        headers=headers,
        json=answer_body,
    )
    assert stale.status_code == 409
    assert stale.headers["cache-control"] == "no-store"

    correction_body = {
        "question_id": "core.chief_complaint",
        "question_version": "engineering.1",
        "answer": {
            "schema_version": "intake-answer.v1",
            "answer_type": "TEXT",
            "value": "Corrected synthetic concern",
            "selected_option_ids": None,
            "unit": None,
            "response_disposition": "ANSWERED",
            "language_code": "en",
            "original_text": "Corrected synthetic concern",
        },
        "source_type": "PATIENT_TEXT",
        "expected_version": 2,
    }
    correction = await client.post(
        f"/api/v1/intakes/{started['intake_id']}/answers",
        headers=headers,
        json=correction_body,
    )
    assert correction.status_code == 200
    assert correction.json()["version"] == 3
    assert correction.json()["answers"][0]["value"] == "Corrected synthetic concern"

    _, other_token, _ = await _onboard(client)
    denied = await client.get(
        f"/api/v1/intakes/{started['intake_id']}",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert denied.status_code in {401, 403, 404}
    assert denied.headers["cache-control"] == "no-store"

    completed_response = await client.post(
        f"/api/v1/intakes/{started['intake_id']}/complete",
        headers=headers,
        json={"expected_version": 3},
    )
    assert completed_response.status_code == 200
    completed = completed_response.json()
    assert completed["status"] == "COMPLETED"
    assert completed["version"] == 4
    repeated = await client.post(
        f"/api/v1/intakes/{started['intake_id']}/complete",
        headers=headers,
        json={"expected_version": 3},
    )
    assert repeated.status_code == 200
    assert repeated.json()["version"] == 4

    async with database.session_factory() as session:
        assert await session.scalar(select(func.count()).select_from(ClinicalIntakeRecord)) == 1
        assert await session.scalar(select(func.count()).select_from(IntakeAnswerRecord)) == 2
        assert (
            await session.scalar(select(func.count()).select_from(QuestionnaireInstanceRecord)) == 1
        )


async def test_hindi_and_production_engineering_content_fail_closed(
    intake_client: tuple[AsyncClient, DatabaseRuntime],
) -> None:
    client, _ = intake_client
    session_response = await client.post(
        "/api/v1/sessions",
        json={"session_type": "PSEUDONYMOUS", "language_preference": "hi"},
    )
    session = session_response.json()
    headers = {"Authorization": f"Bearer {session['session_token']}"}
    await client.post(
        "/api/v1/consents",
        headers=headers,
        json={
            "subject_type": "SESSION",
            "subject_id": session["session_id"],
            "purpose": "GENERAL_PRODUCT_USE",
            "scope": ["clinical_intake"],
            "notice_version": "privacy-v1",
        },
    )
    encounter = (
        await client.post(
            "/api/v1/encounters",
            headers=headers,
            json={
                "session_id": session["session_id"],
                "patient_id": None,
                "encounter_type": "GENERAL_INTAKE",
            },
        )
    ).json()
    unavailable = await client.post(
        f"/api/v1/encounters/{encounter['encounter_id']}/intake",
        headers=headers,
        json={"pack_ids": ["core.intake"]},
    )
    assert unavailable.status_code == 503
    assert unavailable.json()["error"]["code"] == "POLICY_UNAVAILABLE"
