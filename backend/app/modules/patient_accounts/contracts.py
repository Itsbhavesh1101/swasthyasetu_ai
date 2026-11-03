"""Patient account commands, results, and provider-neutral contracts."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.identity.domain import Actor, ActorType, RoleCode
from app.modules.patient_accounts.domain import (
    AccountStatus,
    DisplayName,
    EmailAddress,
    PasswordDigest,
    PatientAccount,
    RawPassword,
)
from app.modules.patients.domain import Patient
from app.modules.sessions.domain import Session, SessionType
from app.shared.types import OpaqueId


class AccountAlreadyExistsError(RuntimeError):
    """Private persistence uniqueness conflict."""


@dataclass(frozen=True, slots=True)
class RegisterPatient:
    email: EmailAddress
    password: RawPassword = field(repr=False)
    preferred_language: str | None = None


@dataclass(frozen=True, slots=True)
class LoginPatient:
    email: EmailAddress
    password: RawPassword = field(repr=False)


@dataclass(frozen=True, slots=True)
class CurrentAccount:
    account_id: OpaqueId
    actor_id: OpaqueId
    patient_id: OpaqueId
    email: str
    display_name: str | None
    profile_complete: bool
    status: AccountStatus


@dataclass(frozen=True, slots=True)
class AccountSession:
    account: CurrentAccount
    session: Session
    session_token: str = field(repr=False)

    def __repr__(self) -> str:
        return (
            f"AccountSession(account={self.account!r}, session={self.session!r}, token=<redacted>)"
        )


class PasswordHasher(Protocol):
    def hash(self, password: RawPassword) -> PasswordDigest: ...
    def verify(self, password: RawPassword, digest: PasswordDigest) -> bool: ...


class PatientAccountRepository(Protocol):
    async def add(self, session: AsyncSession, account: PatientAccount) -> object: ...
    async def get_by_email(
        self, session: AsyncSession, email_normalized: str
    ) -> PatientAccount | None: ...
    async def get_by_actor(
        self, session: AsyncSession, actor_id: OpaqueId
    ) -> PatientAccount | None: ...
    async def save_display_name(
        self,
        session: AsyncSession,
        actor_id: OpaqueId,
        display_name: DisplayName,
        updated_at: datetime,
    ) -> PatientAccount: ...


class AccountActorRepository(Protocol):
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
    ) -> object: ...
    async def get(self, session: AsyncSession, actor_id: OpaqueId) -> object | None: ...
    def to_domain(self, record: object) -> Actor: ...


class AccountPatientRepository(Protocol):
    async def add(self, session: AsyncSession, patient: Patient) -> object: ...
    async def get(self, session: AsyncSession, patient_id: OpaqueId) -> Patient | None: ...


class AccountSessionRepository(Protocol):
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
    ) -> object: ...
    async def get_by_token_hash(
        self, session: AsyncSession, token_hash: str, *, for_update: bool = False
    ) -> object | None: ...
    def to_domain(self, record: object) -> Session: ...
    def close(self, record: object, *, closed_at: datetime) -> Session: ...


def current_account(account: PatientAccount, *, profile_complete: bool = False) -> CurrentAccount:
    return CurrentAccount(
        account_id=account.account_id,
        actor_id=account.actor_id,
        patient_id=account.patient_id,
        email=account.email.display,
        display_name=None if account.display_name is None else account.display_name.value,
        profile_complete=profile_complete,
        status=account.status,
    )
