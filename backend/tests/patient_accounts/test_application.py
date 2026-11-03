"""Patient account orchestration tests with transaction-scoped fakes."""

from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta, timezone
from typing import cast

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import PatientAccountSettings
from app.modules.identity.domain import Actor, ActorStatus, ActorType, RoleCode
from app.modules.patient_accounts.application import PatientAccountService
from app.modules.patient_accounts.contracts import LoginPatient, RegisterPatient
from app.modules.patient_accounts.domain import (
    DisplayName,
    EmailAddress,
    PasswordDigest,
    PatientAccount,
    RawPassword,
)
from app.modules.patients.domain import Patient
from app.modules.sessions.domain import Session, SessionStatus, SessionType
from app.shared.errors import ApplicationError, ErrorCode
from app.shared.persistence import DatabaseRuntime
from app.shared.types import OpaqueId

NOW = datetime(2026, 11, 3, 10, tzinfo=UTC)


class FakeDatabase:
    def __init__(self) -> None:
        self.transaction_count = 0
        self.transaction_object = cast(AsyncSession, object())

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[AsyncSession]:
        self.transaction_count += 1
        yield self.transaction_object


class FakePasswords:
    digest = PasswordDigest("$argon2id$v=19$m=65536,t=3,p=4$synthetic$safe")

    def __init__(self) -> None:
        self.hash_calls = 0
        self.verify_calls = 0

    def hash(self, password: RawPassword) -> PasswordDigest:
        self.hash_calls += 1
        return self.digest

    def verify(self, password: RawPassword, digest: PasswordDigest) -> bool:
        self.verify_calls += 1
        return password.value == "correct horse battery staple" and digest == self.digest


class FakeAccounts:
    def __init__(self) -> None:
        self.by_email: dict[str, PatientAccount] = {}
        self.transactions: list[AsyncSession] = []

    async def add(self, session: AsyncSession, account: PatientAccount) -> PatientAccount:
        self.transactions.append(session)
        self.by_email[account.email.normalized] = account
        return account

    async def get_by_email(
        self, session: AsyncSession, email_normalized: str
    ) -> PatientAccount | None:
        self.transactions.append(session)
        return self.by_email.get(email_normalized)

    async def get_by_actor(
        self, session: AsyncSession, actor_id: OpaqueId
    ) -> PatientAccount | None:
        self.transactions.append(session)
        return next(
            (account for account in self.by_email.values() if account.actor_id == actor_id), None
        )


class FakeActors:
    def __init__(self) -> None:
        self.values: dict[OpaqueId, Actor] = {}
        self.transactions: list[AsyncSession] = []

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
    ) -> Actor:
        self.transactions.append(session)
        actor = Actor(
            actor_id=actor_id,
            actor_type=actor_type,
            roles=roles,
            subject_id=subject_id,
            institution_id=institution_id,
            status=ActorStatus.ACTIVE,
            created_at=created_at,
            updated_at=created_at,
        )
        self.values[actor_id] = actor
        return actor

    async def get(self, session: AsyncSession, actor_id: OpaqueId) -> Actor | None:
        self.transactions.append(session)
        return self.values.get(actor_id)

    def to_domain(self, record: object) -> Actor:
        assert isinstance(record, Actor)
        return record


class FakePatients:
    def __init__(self) -> None:
        self.values: dict[OpaqueId, Patient] = {}
        self.transactions: list[AsyncSession] = []

    async def add(self, session: AsyncSession, patient: Patient) -> Patient:
        self.transactions.append(session)
        self.values[patient.patient_id] = patient
        return patient


class FakeSessions:
    def __init__(self) -> None:
        self.values: dict[str, Session] = {}
        self.transactions: list[AsyncSession] = []

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
    ) -> Session:
        self.transactions.append(session)
        value = Session(
            session_id=session_id,
            session_type=session_type,
            language_preference=language_preference,
            status=SessionStatus.ACTIVE,
            created_at=created_at,
            expires_at=expires_at,
            closed_at=None,
            updated_at=created_at,
            actor_id=actor_id,
            patient_id=patient_id,
        )
        self.values[token_hash] = value
        return value

    async def get_by_token_hash(
        self, session: AsyncSession, token_hash: str, *, for_update: bool = False
    ) -> Session | None:
        self.transactions.append(session)
        return self.values.get(token_hash)

    def to_domain(self, record: object) -> Session:
        assert isinstance(record, Session)
        return record

    def close(self, record: object, *, closed_at: datetime) -> Session:
        value = self.to_domain(record)
        closed = Session(
            session_id=value.session_id,
            session_type=value.session_type,
            language_preference=value.language_preference,
            status=SessionStatus.CLOSED,
            created_at=value.created_at,
            expires_at=value.expires_at,
            closed_at=closed_at,
            updated_at=closed_at,
            actor_id=value.actor_id,
            patient_id=value.patient_id,
        )
        for key, item in self.values.items():
            if item.session_id == value.session_id:
                self.values[key] = closed
        return closed


def _service(
    database: FakeDatabase,
    *,
    clock: Callable[[], datetime] = lambda: NOW.astimezone(
        timezone(timedelta(hours=5, minutes=30))
    ),
) -> tuple[
    PatientAccountService,
    FakeAccounts,
    FakeActors,
    FakePatients,
    FakeSessions,
    FakePasswords,
]:
    accounts = FakeAccounts()
    actors = FakeActors()
    patients = FakePatients()
    sessions = FakeSessions()
    passwords = FakePasswords()
    service = PatientAccountService(
        database=cast(DatabaseRuntime, database),
        settings=PatientAccountSettings(authenticated_ttl_minutes=720),
        accounts=accounts,
        actors=actors,
        patients=patients,
        sessions=sessions,
        passwords=passwords,
        clock=clock,
        token_factory=lambda: "opaque-account-session-token",
    )
    return service, accounts, actors, patients, sessions, passwords


async def test_registration_uses_one_transaction_and_exact_bindings() -> None:
    database = FakeDatabase()
    service, accounts, actors, patients, sessions, _ = _service(database)

    result = await service.register(
        RegisterPatient(
            email=EmailAddress("Patient@Example.com"),
            display_name=DisplayName("Patient Demo"),
            password=RawPassword("correct horse battery staple"),
            preferred_language="en",
        )
    )

    assert database.transaction_count == 1
    assert result.session_token == "opaque-account-session-token"
    assert result.account.email == "Patient@Example.com"
    assert result.session.session_type is SessionType.AUTHENTICATED
    assert result.session.actor_id == result.account.actor_id
    assert result.session.patient_id == result.account.patient_id
    assert result.session.created_at == NOW
    assert actors.values[result.account.actor_id].roles == frozenset({RoleCode.PATIENT})
    assert actors.values[result.account.actor_id].subject_id == result.account.patient_id
    assert patients.values[result.account.patient_id].preferred_language == "en"
    assert all(
        item is database.transaction_object
        for item in (
            *accounts.transactions,
            *actors.transactions,
            *patients.transactions,
            *sessions.transactions,
        )
    )
    assert "opaque-account-session-token" not in repr(result)


async def test_naive_clock_fails_before_any_transaction() -> None:
    database = FakeDatabase()
    service, *_ = _service(database, clock=lambda: NOW.replace(tzinfo=None))

    with pytest.raises(ValueError, match="timezone-aware"):
        await service.register(
            RegisterPatient(
                email=EmailAddress("patient@example.com"),
                display_name=DisplayName("Patient Demo"),
                password=RawPassword("correct horse battery staple"),
            )
        )

    assert database.transaction_count == 0


async def test_unknown_and_wrong_password_fail_with_the_same_generic_error() -> None:
    database = FakeDatabase()
    service, *_, passwords = _service(database)
    await service.register(
        RegisterPatient(
            email=EmailAddress("patient@example.com"),
            display_name=DisplayName("Patient Demo"),
            password=RawPassword("correct horse battery staple"),
        )
    )
    hash_calls_before_login = passwords.hash_calls

    errors: list[ApplicationError] = []
    for command in (
        LoginPatient(
            email=EmailAddress("unknown@example.com"),
            password=RawPassword("a different secure password"),
        ),
        LoginPatient(
            email=EmailAddress("patient@example.com"),
            password=RawPassword("a different secure password"),
        ),
    ):
        with pytest.raises(ApplicationError) as captured:
            await service.login(command)
        errors.append(captured.value)

    assert {error.code for error in errors} == {ErrorCode.AUTHENTICATION_REQUIRED}
    assert len({error.message for error in errors}) == 1
    assert all("email" not in error.message.casefold() for error in errors)
    assert passwords.hash_calls == hash_calls_before_login
    assert passwords.verify_calls == 2
