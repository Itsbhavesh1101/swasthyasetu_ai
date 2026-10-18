"""Real PostgreSQL and HTTP verification for the P7-C structured intake flow."""

from __future__ import annotations

import os
from asyncio import gather
from collections.abc import AsyncIterator
from typing import cast
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import func, select, text

from app.config import DatabaseSettings, Environment, FeaturesSettings, Settings
from app.main import create_app
from app.modules.clinical_intake.application import ClinicalIntakeService
from app.modules.clinical_intake.infrastructure import (
    ClinicalIntakeRecord,
    IntakeAnswerRecord,
    QuestionnaireInstanceRecord,
)
from app.modules.clinical_intake.public import INTAKE_ANSWER
from app.shared.persistence import DatabaseRuntime

pytestmark = pytest.mark.postgres


@pytest.fixture
async def intake_client() -> AsyncIterator[tuple[AsyncClient, DatabaseRuntime, FastAPI]]:
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
        features=FeaturesSettings(enabled=("engineering_clinical_intake",)),
        _env_file=None,
    )
    application = create_app(settings, database=database)
    async with AsyncClient(
        transport=ASGITransport(app=application), base_url="http://test"
    ) as client:
        yield client, database, application
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


async def _start(client: AsyncClient, token: str, encounter_id: str) -> dict[str, object]:
    response = await client.post(
        f"/api/v1/encounters/{encounter_id}/intake",
        headers={"Authorization": f"Bearer {token}"},
        json={"pack_ids": ["core.intake"]},
    )
    assert response.status_code in {200, 201}, response.text
    return cast(dict[str, object], response.json())


def _answer_request(version: int, value: str = "Synthetic test concern") -> dict[str, object]:
    return {
        "question_id": "core.chief_complaint",
        "question_version": "engineering.1",
        "answer": {
            "schema_version": "intake-answer.v1",
            "answer_type": "TEXT",
            "value": value,
            "selected_option_ids": None,
            "unit": None,
            "response_disposition": "ANSWERED",
            "language_code": "en",
            "original_text": value,
        },
        "source_type": "PATIENT_TEXT",
        "expected_version": version,
    }


async def test_real_http_flow_is_atomic_versioned_idempotent_and_session_bound(
    intake_client: tuple[AsyncClient, DatabaseRuntime, FastAPI],
) -> None:
    client, database, _ = intake_client
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
    intake_client: tuple[AsyncClient, DatabaseRuntime, FastAPI],
) -> None:
    client, _, _ = intake_client
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


async def test_competing_start_and_answer_requests_are_atomic(
    intake_client: tuple[AsyncClient, DatabaseRuntime, FastAPI],
) -> None:
    client, database, _ = intake_client
    _, token, encounter_id = await _onboard(client)
    headers = {"Authorization": f"Bearer {token}"}
    starts = await gather(
        client.post(
            f"/api/v1/encounters/{encounter_id}/intake",
            headers=headers,
            json={"pack_ids": ["core.intake"]},
        ),
        client.post(
            f"/api/v1/encounters/{encounter_id}/intake",
            headers=headers,
            json={"pack_ids": ["core.intake"]},
        ),
    )
    assert sorted(response.status_code for response in starts) == [200, 201]
    assert len({response.json()["intake_id"] for response in starts}) == 1
    started = starts[0].json()

    answers = await gather(
        client.post(
            f"/api/v1/intakes/{started['intake_id']}/answers",
            headers=headers,
            json=_answer_request(1, "Synthetic concurrent A"),
        ),
        client.post(
            f"/api/v1/intakes/{started['intake_id']}/answers",
            headers=headers,
            json=_answer_request(1, "Synthetic concurrent B"),
        ),
    )
    assert sorted(response.status_code for response in answers) == [200, 409]
    async with database.session_factory() as session:
        assert await session.scalar(select(func.count()).select_from(ClinicalIntakeRecord)) == 1
        assert (
            await session.scalar(select(func.count()).select_from(QuestionnaireInstanceRecord)) == 1
        )
        assert await session.scalar(select(func.count()).select_from(IntakeAnswerRecord)) == 1
        assert await session.scalar(select(ClinicalIntakeRecord.version)) == 2
        responses = await session.scalar(select(QuestionnaireInstanceRecord.responses))
        assert isinstance(responses, dict)
        answer_refs = responses["answer_refs"]
        assert isinstance(answer_refs, list)
        assert len(answer_refs) == 1


@pytest.mark.parametrize("failure_stage", ["answer", "instance", "aggregate"])
async def test_injected_write_failures_roll_back_every_intake_stage(
    intake_client: tuple[AsyncClient, DatabaseRuntime, FastAPI],
    monkeypatch: pytest.MonkeyPatch,
    failure_stage: str,
) -> None:
    client, database, application = intake_client
    _, token, encounter_id = await _onboard(client)
    started = await _start(client, token, encounter_id)
    async with database.session_factory() as session:
        assert await session.scalar(select(func.count()).select_from(IntakeAnswerRecord)) == 0
        assert await session.scalar(select(ClinicalIntakeRecord.version)) == 1
        assert (
            await session.scalar(select(func.count()).select_from(QuestionnaireInstanceRecord)) == 1
        )
    service = cast(
        ClinicalIntakeService,
        application.state.capability_registry.resolve(INTAKE_ANSWER),
    )
    target, method = {
        "answer": (service._answers, "add"),
        "instance": (service._instances, "save"),
        "aggregate": (service._intakes, "save"),
    }[failure_stage]
    monkeypatch.setattr(
        target,
        method,
        AsyncMock(side_effect=RuntimeError("synthetic injected write failure")),
    )
    failed = await client.post(
        f"/api/v1/intakes/{started['intake_id']}/answers",
        headers={"Authorization": f"Bearer {token}"},
        json=_answer_request(1),
    )
    assert failed.status_code == 500
    assert failed.headers["cache-control"] == "no-store"
    assert "synthetic" not in failed.text.lower()

    async with database.session_factory() as session:
        assert await session.scalar(select(func.count()).select_from(IntakeAnswerRecord)) == 0
        assert await session.scalar(select(ClinicalIntakeRecord.version)) == 1
        responses = await session.scalar(select(QuestionnaireInstanceRecord.responses))
        assert isinstance(responses, dict)
        assert responses["answer_refs"] == []
        assert responses["skipped_question_refs"] == []


async def test_continued_access_rechecks_session_consent_and_exact_subject(
    intake_client: tuple[AsyncClient, DatabaseRuntime, FastAPI],
) -> None:
    client, _, _ = intake_client
    session_id, token, encounter_id = await _onboard(client)
    started = await _start(client, token, encounter_id)
    intake_id = str(started["intake_id"])
    owner_headers = {"Authorization": f"Bearer {token}"}
    _, other_token, _ = await _onboard(client)
    other_headers = {"Authorization": f"Bearer {other_token}"}

    for method, path, payload in (
        ("GET", f"/api/v1/intakes/{intake_id}", None),
        ("POST", f"/api/v1/intakes/{intake_id}/answers", _answer_request(1)),
        ("POST", f"/api/v1/intakes/{intake_id}/complete", {"expected_version": 1}),
    ):
        denied = await client.request(method, path, headers=other_headers, json=payload)
        assert denied.status_code in {401, 403, 404}
        assert denied.headers["cache-control"] == "no-store"

    listed = await client.get(
        "/api/v1/consents",
        params={
            "subject_type": "SESSION",
            "subject_id": session_id,
            "purpose": "GENERAL_PRODUCT_USE",
        },
        headers=owner_headers,
    )
    consent_id = listed.json()[0]["consent_id"]
    revoked = await client.post(
        f"/api/v1/consents/{consent_id}/revoke",
        headers=owner_headers,
        json={"reason": "user_requested"},
    )
    assert revoked.status_code == 200
    for method, path, payload in (
        ("GET", f"/api/v1/intakes/{intake_id}", None),
        ("POST", f"/api/v1/intakes/{intake_id}/answers", _answer_request(1)),
        ("POST", f"/api/v1/intakes/{intake_id}/complete", {"expected_version": 1}),
    ):
        denied = await client.request(method, path, headers=owner_headers, json=payload)
        assert denied.status_code == 403
        assert denied.json()["error"]["code"] == "CONSENT_REQUIRED"

    close_session_id, close_token, close_encounter_id = await _onboard(client)
    closed_started = await _start(client, close_token, close_encounter_id)
    close_headers = {"Authorization": f"Bearer {close_token}"}
    closed = await client.post(
        f"/api/v1/sessions/{close_session_id}/close",
        headers=close_headers,
    )
    assert closed.status_code == 200
    for method, path, payload in (
        ("GET", f"/api/v1/intakes/{closed_started['intake_id']}", None),
        (
            "POST",
            f"/api/v1/intakes/{closed_started['intake_id']}/answers",
            _answer_request(1),
        ),
        (
            "POST",
            f"/api/v1/intakes/{closed_started['intake_id']}/complete",
            {"expected_version": 1},
        ),
    ):
        denied = await client.request(method, path, headers=close_headers, json=payload)
        assert denied.status_code == 409
        assert denied.json()["error"]["code"] == "INVALID_STATE_TRANSITION"


async def test_completed_draft_remains_readable_after_encounter_is_terminal(
    intake_client: tuple[AsyncClient, DatabaseRuntime, FastAPI],
) -> None:
    client, _, _ = intake_client
    _, token, encounter_id = await _onboard(client)
    headers = {"Authorization": f"Bearer {token}"}
    started = await _start(client, token, encounter_id)
    answered = await client.post(
        f"/api/v1/intakes/{started['intake_id']}/answers",
        headers=headers,
        json=_answer_request(1),
    )
    assert answered.status_code == 200
    completed = await client.post(
        f"/api/v1/intakes/{started['intake_id']}/complete",
        headers=headers,
        json={"expected_version": 2},
    )
    assert completed.status_code == 200
    terminal = await client.post(f"/api/v1/encounters/{encounter_id}/abandon", headers=headers)
    assert terminal.status_code == 200

    readable = await client.get(f"/api/v1/intakes/{started['intake_id']}", headers=headers)
    assert readable.status_code == 200
    assert readable.json()["status"] == "COMPLETED"
    for path, payload in (
        (f"/api/v1/intakes/{started['intake_id']}/answers", _answer_request(2)),
        (f"/api/v1/intakes/{started['intake_id']}/complete", {"expected_version": 2}),
    ):
        rejected = await client.post(path, headers=headers, json=payload)
        assert rejected.status_code == 409
        assert rejected.headers["cache-control"] == "no-store"
    _, other_token, _ = await _onboard(client)
    foreign = await client.get(
        f"/api/v1/intakes/{started['intake_id']}",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert foreign.status_code in {401, 403, 404}


async def test_completed_read_and_replay_reject_corrupt_instance_state(
    intake_client: tuple[AsyncClient, DatabaseRuntime, FastAPI],
) -> None:
    client, database, _ = intake_client
    _, token, encounter_id = await _onboard(client)
    headers = {"Authorization": f"Bearer {token}"}
    started = await _start(client, token, encounter_id)
    answered = await client.post(
        f"/api/v1/intakes/{started['intake_id']}/answers",
        headers=headers,
        json=_answer_request(1),
    )
    completed = await client.post(
        f"/api/v1/intakes/{started['intake_id']}/complete",
        headers=headers,
        json={"expected_version": answered.json()["version"]},
    )
    assert completed.status_code == 200
    async with database.engine.begin() as connection:
        await connection.execute(
            text(
                "UPDATE questionnaire_instances "
                "SET status = 'ACTIVE', completed_at = NULL "
                "WHERE encounter_id = CAST(:encounter_id AS uuid)"
            ),
            {"encounter_id": encounter_id},
        )
    for method, payload in (("GET", None), ("POST", {"expected_version": 2})):
        path = f"/api/v1/intakes/{started['intake_id']}"
        if method == "POST":
            path += "/complete"
        rejected = await client.request(method, path, headers=headers, json=payload)
        assert rejected.status_code == 500
        assert rejected.json()["error"]["code"] == "PROCESSING_FAILED"
        assert rejected.headers["cache-control"] == "no-store"


@pytest.mark.parametrize(
    ("environment", "enabled"),
    [
        (Environment.LOCAL, False),
        (Environment.TEST, False),
        (Environment.STAGING, True),
        (Environment.PILOT, True),
        (Environment.PRODUCTION, True),
    ],
)
async def test_engineering_content_requires_environment_and_explicit_opt_in(
    intake_client: tuple[AsyncClient, DatabaseRuntime, FastAPI],
    environment: Environment,
    enabled: bool,
) -> None:
    _, database, _ = intake_client
    flags = ("engineering_clinical_intake",) if enabled else ()
    url = os.environ["SWASTHYASETU_TEST_DATABASE_URL"]
    settings = Settings(
        environment=environment,
        database=DatabaseSettings(enabled=True, url=url),
        features=FeaturesSettings(enabled=flags),
        _env_file=None,
    )
    application = create_app(settings, database=database)
    async with AsyncClient(
        transport=ASGITransport(app=application), base_url="http://test"
    ) as client:
        _, token, encounter_id = await _onboard(client)
        unavailable = await client.post(
            f"/api/v1/encounters/{encounter_id}/intake",
            headers={"Authorization": f"Bearer {token}"},
            json={"pack_ids": ["core.intake"]},
        )
    assert unavailable.status_code == 503
    assert unavailable.json()["error"]["code"] == "POLICY_UNAVAILABLE"
