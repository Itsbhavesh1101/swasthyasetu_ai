"""Real PostgreSQL account registration, rollback, and authentication proofs."""

import os
from collections.abc import AsyncIterator
from datetime import UTC, datetime

import pytest
from sqlalchemy import text, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import DatabaseSettings, PatientAccountSettings
from app.modules.identity.domain import ActorType, RoleCode
from app.modules.identity.infrastructure import ActorRecord, PostgresActorRepository
from app.modules.patient_accounts.application import PatientAccountService
from app.modules.patient_accounts.contracts import LoginPatient, RegisterPatient
from app.modules.patient_accounts.domain import (
    DisplayName,
    EmailAddress,
    PatientAccount,
    RawPassword,
)
from app.modules.patient_accounts.infrastructure import (
    PatientAccountRecord,
    PostgresPatientAccountRepository,
)
from app.modules.patient_accounts.passwords import Argon2PasswordHasher
from app.modules.patients.domain import Patient
from app.modules.patients.infrastructure import PatientRecord, PostgresPatientRepository
from app.modules.sessions.domain import SessionType
from app.modules.sessions.infrastructure import PostgresSessionRepository, SessionRecord
from app.shared.errors import ApplicationError, ErrorCode
from app.shared.persistence import DatabaseRuntime
from app.shared.types import OpaqueId

pytestmark = pytest.mark.postgres
NOW = datetime(2026, 11, 3, 10, tzinfo=UTC)
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


def _register(email: str = "Patient@Example.com") -> RegisterPatient:
    return RegisterPatient(
        email=EmailAddress(email),
        display_name=DisplayName("Patient Demo"),
        password=RawPassword("correct horse battery staple"),
        preferred_language="en",
    )


def _service(
    runtime: DatabaseRuntime,
    *,
    accounts: PostgresPatientAccountRepository | None = None,
    actors: PostgresActorRepository | None = None,
    patients: PostgresPatientRepository | None = None,
    sessions: PostgresSessionRepository | None = None,
) -> PatientAccountService:
    return PatientAccountService(
        database=runtime,
        settings=PatientAccountSettings(authenticated_ttl_minutes=720),
        accounts=accounts or PostgresPatientAccountRepository(),
        actors=actors or PostgresActorRepository(),
        patients=patients or PostgresPatientRepository(),
        sessions=sessions or PostgresSessionRepository(),
        passwords=Argon2PasswordHasher(),
        clock=lambda: NOW,
        token_factory=lambda: f"opaque-token-{OpaqueId.new()}",
    )


async def test_registration_login_and_authentication_bind_exact_patient(
    database_runtime: DatabaseRuntime,
) -> None:
    service = _service(database_runtime)

    registered = await service.register(_register())
    context = await service.authenticate(registered.session_token)
    logged_in = await service.login(
        LoginPatient(
            email=EmailAddress("patient@example.COM"),
            password=RawPassword("correct horse battery staple"),
        )
    )

    assert registered.session.session_type is SessionType.AUTHENTICATED
    assert registered.session.actor_id == registered.account.actor_id
    assert registered.session.patient_id == registered.account.patient_id
    assert context.actor_id == registered.account.actor_id
    assert context.subject_id == registered.account.patient_id
    assert context.roles == frozenset({RoleCode.PATIENT.value})
    assert await service.get_current_account(registered.session_token) == registered.account
    assert logged_in.account == registered.account
    assert logged_in.session.session_id != registered.session.session_id
    assert registered.session_token not in repr(registered)

    async with database_runtime.session_factory() as session:
        counts = (
            await session.execute(
                text(
                    "SELECT (SELECT count(*) FROM patient_accounts), "
                    "(SELECT count(*) FROM patients), (SELECT count(*) FROM actors), "
                    "(SELECT count(*) FROM actor_roles), (SELECT count(*) FROM sessions)"
                )
            )
        ).one()
    assert tuple(counts) == (1, 1, 1, 1, 2)

    await service.close_session(registered.session_token)
    with pytest.raises(ApplicationError) as closed:
        await service.authenticate(registered.session_token)
    assert closed.value.code is ErrorCode.AUTHENTICATION_REQUIRED


async def test_duplicate_email_and_bad_credentials_are_generic(
    database_runtime: DatabaseRuntime,
) -> None:
    service = _service(database_runtime)
    await service.register(_register())

    with pytest.raises(ApplicationError) as duplicate:
        await service.register(_register("PATIENT@example.com"))
    assert duplicate.value.code is ErrorCode.RESOURCE_CONFLICT

    errors: list[ApplicationError] = []
    for email in ("patient@example.com", "unknown@example.com"):
        with pytest.raises(ApplicationError) as captured:
            await service.login(
                LoginPatient(
                    email=EmailAddress(email),
                    password=RawPassword("a different secure password"),
                )
            )
        errors.append(captured.value)
    assert {error.code for error in errors} == {ErrorCode.AUTHENTICATION_REQUIRED}
    assert len({error.message for error in errors}) == 1

    async with database_runtime.session_factory() as session:
        counts = (
            await session.execute(
                text(
                    "SELECT (SELECT count(*) FROM patient_accounts), "
                    "(SELECT count(*) FROM patients), (SELECT count(*) FROM actors), "
                    "(SELECT count(*) FROM sessions)"
                )
            )
        ).one()
    assert tuple(counts) == (1, 1, 1, 1)


async def test_disabled_actor_invalidates_existing_session(
    database_runtime: DatabaseRuntime,
) -> None:
    service = _service(database_runtime)
    registered = await service.register(_register())
    async with database_runtime.transaction() as session:
        await session.execute(
            update(ActorRecord)
            .where(ActorRecord.id == registered.account.actor_id.value)
            .values(status="DISABLED", updated_at=NOW)
        )

    with pytest.raises(ApplicationError) as captured:
        await service.authenticate(registered.session_token)
    assert captured.value.code is ErrorCode.AUTHENTICATION_REQUIRED


async def test_disabled_account_invalidates_existing_session(
    database_runtime: DatabaseRuntime,
) -> None:
    service = _service(database_runtime)
    registered = await service.register(_register())
    async with database_runtime.transaction() as session:
        await session.execute(
            update(PatientAccountRecord)
            .where(PatientAccountRecord.id == registered.account.account_id.value)
            .values(status="DISABLED", updated_at=NOW)
        )

    with pytest.raises(ApplicationError) as captured:
        await service.authenticate(registered.session_token)
    assert captured.value.code is ErrorCode.AUTHENTICATION_REQUIRED


class FailingPatientRepository(PostgresPatientRepository):
    async def add(self, session: AsyncSession, patient: Patient) -> PatientRecord:
        await super().add(session, patient)
        raise RuntimeError("injected patient failure")


class FailingActorRepository(PostgresActorRepository):
    async def create(
        self,
        session: AsyncSession,
        *,
        actor_id: OpaqueId,
        actor_type: ActorType,
        roles: frozenset[RoleCode],
        subject_id: OpaqueId | None,
        institution_id: OpaqueId | None,
        created_at: datetime,
    ) -> ActorRecord:
        await super().create(
            session,
            actor_id=actor_id,
            actor_type=actor_type,
            roles=roles,
            subject_id=subject_id,
            institution_id=institution_id,
            created_at=created_at,
        )
        raise RuntimeError("injected actor failure")


class FailingAccountRepository(PostgresPatientAccountRepository):
    async def add(self, session: AsyncSession, account: PatientAccount) -> PatientAccountRecord:
        await super().add(session, account)
        raise RuntimeError("injected account failure")


class FailingSessionRepository(PostgresSessionRepository):
    async def create(
        self,
        session: AsyncSession,
        *,
        session_id: OpaqueId,
        session_type: SessionType,
        language_preference: str | None,
        token_hash: str,
        created_at: datetime,
        expires_at: datetime,
        actor_id: OpaqueId | None = None,
        patient_id: OpaqueId | None = None,
    ) -> SessionRecord:
        await super().create(
            session,
            session_id=session_id,
            session_type=session_type,
            language_preference=language_preference,
            token_hash=token_hash,
            created_at=created_at,
            expires_at=expires_at,
            actor_id=actor_id,
            patient_id=patient_id,
        )
        raise RuntimeError("injected session failure")


@pytest.mark.parametrize("stage", ["patient", "actor", "account", "session"])
async def test_registration_failure_rolls_back_every_record(
    database_runtime: DatabaseRuntime, stage: str
) -> None:
    service = _service(
        database_runtime,
        patients=FailingPatientRepository() if stage == "patient" else None,
        actors=FailingActorRepository() if stage == "actor" else None,
        accounts=FailingAccountRepository() if stage == "account" else None,
        sessions=FailingSessionRepository() if stage == "session" else None,
    )

    with pytest.raises(RuntimeError, match="injected"):
        await service.register(_register())

    async with database_runtime.session_factory() as session:
        counts = (
            await session.execute(
                text(
                    "SELECT (SELECT count(*) FROM patient_accounts), "
                    "(SELECT count(*) FROM patients), (SELECT count(*) FROM actors), "
                    "(SELECT count(*) FROM actor_roles), (SELECT count(*) FROM sessions)"
                )
            )
        ).one()
    assert tuple(counts) == (0, 0, 0, 0, 0)
