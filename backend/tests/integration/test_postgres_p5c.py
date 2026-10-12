"""Real PostgreSQL and HTTP acceptance coverage for P5-C."""

import os
from collections.abc import AsyncIterator
from datetime import UTC, datetime

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text, update

from app.config import DatabaseSettings, Settings
from app.main import create_app
from app.modules.encounters.infrastructure import EncounterRecord
from app.modules.identity.domain import RoleCode
from app.modules.identity.infrastructure import ActorRecord, ActorRoleRecord
from app.modules.patients.infrastructure import PostgresClinicalFactRepository
from app.modules.patients.public import ClinicalFact, FactType, Problem, ProblemStatus
from app.modules.provenance.public import (
    FactProvenance,
    ProvenanceSourceType,
    VerificationState,
)
from app.shared.persistence import DatabaseRuntime
from app.shared.security import ActorContext
from app.shared.types import OpaqueId

pytestmark = pytest.mark.postgres
NOW = datetime(2026, 10, 12, 8, tzinfo=UTC)


@pytest.fixture
async def database_runtime() -> AsyncIterator[DatabaseRuntime]:
    test_url = os.getenv("SWASTHYASETU_TEST_DATABASE_URL")
    if test_url is None:
        pytest.skip("SWASTHYASETU_TEST_DATABASE_URL is not configured")
    runtime = DatabaseRuntime(DatabaseSettings(enabled=True, url=test_url))
    truncate = text(
        "TRUNCATE TABLE observations, allergies, medications, clinical_fact_provenance, "
        "clinical_facts, encounters, patient_identifiers, patient_demographics, patients, "
        "consent_records, sessions, actor_roles, actors, outbox_events CASCADE"
    )
    async with runtime.engine.begin() as connection:
        await connection.execute(truncate)
    try:
        yield runtime
    finally:
        async with runtime.engine.begin() as connection:
            await connection.execute(truncate)
        await runtime.dispose()


async def test_p5c_http_patient_encounter_fact_timeline_and_authorization(
    database_runtime: DatabaseRuntime,
) -> None:
    patient_id = OpaqueId.new()
    actor_id = OpaqueId.new()
    async with database_runtime.transaction() as transaction:
        transaction.add(
            ActorRecord(
                id=actor_id.value,
                actor_type="PATIENT",
                subject_ref=patient_id.value,
                institution_id=None,
                status="ACTIVE",
                created_at=NOW,
                updated_at=NOW,
                role_records=[ActorRoleRecord(role_code="patient", created_at=NOW)],
            )
        )

    settings = Settings(
        database=DatabaseSettings(
            enabled=True, url="postgresql+psycopg://unused:unused@localhost/unused"
        ),
        _env_file=None,
    )
    application = create_app(settings, database=database_runtime)

    @application.middleware("http")
    async def trusted_actor(request, call_next):  # type: ignore[no-untyped-def]
        request.state.actor_context = ActorContext(
            actor_id=actor_id,
            actor_type="PATIENT",
            roles=frozenset({RoleCode.PATIENT.value}),
            subject_id=patient_id,
            is_authenticated=True,
        )
        return await call_next(request)

    async with AsyncClient(
        transport=ASGITransport(app=application), base_url="http://test"
    ) as client:
        created_patient = await client.post(
            "/api/v1/patients",
            json={
                "preferred_language": "en",
                "demographics": {"age_years": 30, "location_context": "synthetic"},
            },
        )
        assert created_patient.status_code == 201
        assert created_patient.json()["patient_id"] == str(patient_id)
        assert "identifiers" not in created_patient.json()
        assert created_patient.headers["cache-control"] == "no-store"

        duplicate = await client.post("/api/v1/patients", json={})
        assert duplicate.status_code == 409
        cross_subject = await client.get(f"/api/v1/patients/{OpaqueId.new()}")
        assert cross_subject.status_code == 403

        session_response = await client.post(
            "/api/v1/sessions",
            json={"session_type": "PSEUDONYMOUS", "language_preference": "en"},
        )
        assert session_response.status_code == 201
        session = session_response.json()
        bearer = {"Authorization": f"Bearer {session['session_token']}"}

        pseudonymous = await client.post(
            "/api/v1/encounters",
            headers=bearer,
            json={
                "session_id": session["session_id"],
                "patient_id": None,
                "encounter_type": "GENERAL_INTAKE",
            },
        )
        assert pseudonymous.status_code == 201
        pseudo_id = pseudonymous.json()["encounter_id"]
        assert (
            await client.get(f"/api/v1/encounters/{pseudo_id}", headers=bearer)
        ).status_code == 200
        assert (
            await client.get(
                f"/api/v1/encounters/{pseudo_id}",
                headers={"Authorization": "Bearer incorrect-token"},
            )
        ).status_code == 401
        assert (
            await client.post(f"/api/v1/encounters/{pseudo_id}/abandon", headers=bearer)
        ).status_code == 200

        bound = await client.post(
            "/api/v1/encounters",
            headers=bearer,
            json={
                "session_id": session["session_id"],
                "patient_id": str(patient_id),
                "encounter_type": "MENTAL_HEALTH",
            },
        )
        assert bound.status_code == 201
        bound_id = bound.json()["encounter_id"]
        cross_patient = await client.post(
            "/api/v1/encounters",
            headers=bearer,
            json={
                "session_id": session["session_id"],
                "patient_id": str(OpaqueId.new()),
                "encounter_type": "GENERAL_INTAKE",
            },
        )
        assert cross_patient.status_code == 403
        invalid_complete = await client.post(f"/api/v1/encounters/{bound_id}/complete")
        assert invalid_complete.status_code == 409

        fact = ClinicalFact(
            fact_id=OpaqueId.new(),
            patient_id=patient_id,
            encounter_id=OpaqueId.parse(bound_id),
            fact_type=FactType.PROBLEM,
            value=Problem(
                label="synthetic condition",
                status=ProblemStatus.ACTIVE,
                verification_state=VerificationState.PATIENT_CONFIRMED,
            ),
            recorded_at=NOW,
            verification_state=VerificationState.PATIENT_CONFIRMED,
            provenance=FactProvenance(
                source_type=ProvenanceSourceType.PATIENT_REPORT,
                confidence=None,
                created_at=NOW,
            ),
        )
        async with database_runtime.transaction() as transaction:
            await PostgresClinicalFactRepository().add(transaction, fact)
            await transaction.execute(
                update(EncounterRecord)
                .where(EncounterRecord.id == OpaqueId.parse(bound_id).value)
                .values(
                    status="IN_PROGRESS",
                    started_at=NOW,
                    created_at=NOW,
                    updated_at=NOW,
                )
            )

        facts = await client.get(f"/api/v1/patients/{patient_id}/facts?limit=1")
        assert facts.status_code == 200
        assert facts.json()["items"][0]["canonical_label"] == "synthetic condition"
        assert "source_ref" not in facts.text
        timeline = await client.get(f"/api/v1/patients/{patient_id}/timeline?limit=1")
        assert timeline.status_code == 200
        assert len(timeline.json()["items"]) == 1
        assert timeline.json()["items"][0]["entry_type"] == "CLINICAL_FACT"
        assert timeline.json()["next_cursor"] is not None
        page_two = await client.get(
            f"/api/v1/patients/{patient_id}/timeline",
            params={"limit": 1, "cursor": timeline.json()["next_cursor"]},
        )
        assert page_two.status_code == 200
        assert page_two.json()["items"][0]["entry_id"] != timeline.json()["items"][0]["entry_id"]
        fact_timeline = await client.get(
            f"/api/v1/patients/{patient_id}/timeline",
            params={
                "entry_type": "CLINICAL_FACT",
                "from": "2026-10-12T00:00:00Z",
                "to": "2026-10-12T23:59:59Z",
            },
        )
        assert fact_timeline.status_code == 200
        assert [item["entry_type"] for item in fact_timeline.json()["items"]] == ["CLINICAL_FACT"]
        invalid_timestamp = await client.get(
            f"/api/v1/patients/{patient_id}/timeline",
            params={"from": "2026-10-12T08:00:00+05:30"},
        )
        assert invalid_timestamp.status_code == 422
        assert (await client.post(f"/api/v1/encounters/{bound_id}/complete")).status_code == 200


async def test_p5c_http_anonymous_patient_create_is_401(
    database_runtime: DatabaseRuntime,
) -> None:
    application = create_app(Settings(_env_file=None), database=database_runtime)
    async with AsyncClient(
        transport=ASGITransport(app=application), base_url="http://test"
    ) as client:
        response = await client.post("/api/v1/patients", json={})
    assert response.status_code == 401
    assert response.headers["cache-control"] == "no-store"
