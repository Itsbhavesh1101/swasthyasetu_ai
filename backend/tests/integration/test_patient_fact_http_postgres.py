"""Real PostgreSQL and HTTP proofs for patient-entered medical history."""

import os
from collections.abc import AsyncIterator
from datetime import UTC, datetime

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import DatabaseSettings, PatientAccountSettings, Settings
from app.main import create_app
from app.modules.identity.infrastructure import PostgresActorRepository
from app.modules.patient_accounts.application import PatientAccountService
from app.modules.patient_accounts.contracts import RegisterPatient
from app.modules.patient_accounts.domain import EmailAddress, RawPassword
from app.modules.patient_accounts.infrastructure import PostgresPatientAccountRepository
from app.modules.patient_accounts.passwords import Argon2PasswordHasher
from app.modules.patients.application import PatientService
from app.modules.patients.clinical import (
    ClinicalFact,
    FactSupersession,
    FactType,
    Problem,
    ProblemStatus,
)
from app.modules.patients.infrastructure import (
    ClinicalFactRecord,
    PostgresClinicalFactRepository,
    PostgresPatientRepository,
)
from app.modules.provenance.domain import VerificationState
from app.modules.sessions.infrastructure import PostgresSessionRepository
from app.shared.persistence import DatabaseRuntime
from app.shared.types import OpaqueId

pytestmark = pytest.mark.postgres
NOW = datetime(2026, 11, 3, 13, tzinfo=UTC)
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


async def test_patient_history_http_is_strict_self_scoped_and_correctable(
    database_runtime: DatabaseRuntime,
) -> None:
    application = create_app(Settings(_env_file=None), database=database_runtime)
    async with AsyncClient(
        transport=ASGITransport(app=application), base_url="http://test"
    ) as client:
        account = await client.post(
            "/api/v1/accounts/register",
            json={
                "email": "history@example.com",
                "password": "correct horse battery staple",
            },
        )
        assert account.status_code == 201
        bearer = {"Authorization": f"Bearer {account.json()['session_token']}"}
        current = await client.get("/api/v1/accounts/me", headers=bearer)
        patient_id = current.json()["patient_id"]
        path = f"/api/v1/patients/{patient_id}/facts"
        payload = {
            "fact_type": "PROBLEM",
            "label": "Synthetic migraine",
            "status": "ACTIVE",
            "onset": "2025-01-02",
            "effective_time": "2026-11-03T18:30:00+05:30",
        }

        created = await client.post(path, headers=bearer, json=payload)
        assert created.status_code == 201
        assert created.json()["verification_state"] == "PATIENT_CONFIRMED"
        assert created.json()["provenance"]["source_type"] == "PATIENT_REPORT"
        assert created.json()["effective_time"] == "2026-11-03T13:00:00Z"
        fact_id = created.json()["fact_id"]

        unknown = await client.post(path, headers=bearer, json={**payload, "raw": {}})
        cross = await client.post(
            f"/api/v1/patients/{OpaqueId.new()}/facts", headers=bearer, json=payload
        )
        anonymous = await client.post(path, json=payload)
        assert unknown.status_code == 422
        assert cross.status_code == 403
        assert anonymous.status_code == 401

        correction = {
            "expected_current_id": fact_id,
            "replacement": {
                "fact_type": "PROBLEM",
                "label": "Synthetic migraine corrected",
                "status": "RESOLVED",
                "resolution": "2026-01-02",
            },
        }
        corrected = await client.post(
            f"{path}/{fact_id}/supersede", headers=bearer, json=correction
        )
        stale = await client.post(f"{path}/{fact_id}/supersede", headers=bearer, json=correction)
        assert corrected.status_code == 200
        assert corrected.json()["superseded"]["fact_id"] == fact_id
        assert corrected.json()["superseded"]["verification_state"] == "SUPERSEDED"
        assert corrected.json()["replacement"]["status"] == "RESOLVED"
        assert stale.status_code == 409

        listed = await client.get(path, headers=bearer)
        listed_again = await client.get(path, headers=bearer)
        assert listed.status_code == 200
        labels = [item["canonical_label"] for item in listed.json()["items"]]
        assert labels == [item["canonical_label"] for item in listed_again.json()["items"]]
        assert set(labels) == {
            "Synthetic migraine",
            "Synthetic migraine corrected",
        }


class FailingSupersessionRepository(PostgresClinicalFactRepository):
    async def persist_supersession(
        self, session: AsyncSession, supersession: FactSupersession
    ) -> FactSupersession:
        await super().persist_supersession(session, supersession)
        raise RuntimeError("injected replacement failure")


async def test_injected_correction_failure_rolls_back_old_and_replacement_atomically(
    database_runtime: DatabaseRuntime,
) -> None:
    accounts = PatientAccountService(
        database=database_runtime,
        settings=PatientAccountSettings(),
        accounts=PostgresPatientAccountRepository(),
        actors=PostgresActorRepository(),
        patients=PostgresPatientRepository(),
        sessions=PostgresSessionRepository(),
        passwords=Argon2PasswordHasher(),
        clock=lambda: NOW,
        token_factory=lambda: "synthetic-atomicity-token",
    )
    registered = await accounts.register(
        RegisterPatient(
            email=EmailAddress("atomicity@example.com"),
            password=RawPassword("correct horse battery staple"),
            preferred_language="en",
        )
    )
    facts = PostgresClinicalFactRepository()
    writer = PatientService(
        database=database_runtime,
        patients=PostgresPatientRepository(),
        facts=facts,
        clock=lambda: NOW,
    )
    old = await writer.add_patient_fact(
        patient_id=registered.account.patient_id,
        actor_id=registered.account.actor_id,
        fact_type=FactType.PROBLEM,
        value=Problem(
            label="Synthetic atomic old",
            status=ProblemStatus.ACTIVE,
            verification_state=VerificationState.PATIENT_CONFIRMED,
        ),
        effective_time=None,
    )
    failing = PatientService(
        database=database_runtime,
        patients=PostgresPatientRepository(),
        facts=FailingSupersessionRepository(),
        clock=lambda: NOW,
    )

    with pytest.raises(RuntimeError, match="injected replacement failure"):
        await failing.supersede_patient_fact(
            patient_id=registered.account.patient_id,
            actor_id=registered.account.actor_id,
            expected_current_id=old.fact_id,
            fact_type=FactType.PROBLEM,
            value=Problem(
                label="Synthetic atomic replacement",
                status=ProblemStatus.RESOLVED,
                verification_state=VerificationState.PATIENT_CONFIRMED,
            ),
            effective_time=None,
        )

    async with database_runtime.transaction() as transaction:
        persisted = await facts.get(transaction, old.fact_id)
        count = await transaction.scalar(select(func.count()).select_from(ClinicalFactRecord))
    assert isinstance(persisted, ClinicalFact)
    assert persisted.verification_state is VerificationState.PATIENT_CONFIRMED
    assert persisted.superseded_by_fact_id is None
    assert count == 1
