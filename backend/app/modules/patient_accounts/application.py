"""Atomic patient registration, login, and account-session authentication."""

from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from app.config import PatientAccountSettings
from app.modules.identity.domain import Actor, ActorStatus, ActorType, RoleCode
from app.modules.patient_accounts.contracts import (
    AccountActorRepository,
    AccountAlreadyExistsError,
    AccountPatientRepository,
    AccountSession,
    AccountSessionRepository,
    CurrentAccount,
    LoginPatient,
    PasswordHasher,
    PatientAccountRepository,
    RegisterPatient,
    current_account,
)
from app.modules.patient_accounts.domain import (
    AccountStatus,
    DisplayName,
    PatientAccount,
    RawPassword,
)
from app.modules.patients.domain import Patient, PatientStatus
from app.modules.sessions.application import generate_session_token, hash_session_token
from app.modules.sessions.domain import Session, SessionStatus, SessionType
from app.shared.errors import ApplicationError, DependencyError, ErrorCode
from app.shared.persistence import DatabaseRuntime
from app.shared.security import ActorContext
from app.shared.types import OpaqueId, utc_now

type Clock = Callable[[], datetime]
type TokenFactory = Callable[[], str]


class PatientAccountService:
    """Own all patient account writes inside one database transaction."""

    def __init__(
        self,
        *,
        database: DatabaseRuntime | None,
        settings: PatientAccountSettings,
        accounts: PatientAccountRepository,
        actors: AccountActorRepository,
        patients: AccountPatientRepository,
        sessions: AccountSessionRepository,
        passwords: PasswordHasher,
        clock: Clock = utc_now,
        token_factory: TokenFactory = generate_session_token,
    ) -> None:
        self._database = database
        self._settings = settings
        self._accounts = accounts
        self._actors = actors
        self._patients = patients
        self._sessions = sessions
        self._passwords = passwords
        self._unknown_account_digest = passwords.hash(
            RawPassword("swasthyasetu invalid account credential")
        )
        self._clock = clock
        self._token_factory = token_factory

    async def register(self, command: RegisterPatient) -> AccountSession:
        database = self._require_database()
        now = self._now()
        token = self._new_token()
        patient_id = OpaqueId.new()
        actor_id = OpaqueId.new()
        account = PatientAccount(
            account_id=OpaqueId.new(),
            actor_id=actor_id,
            patient_id=patient_id,
            email=command.email,
            display_name=None,
            password_digest=self._passwords.hash(command.password),
            status=AccountStatus.ACTIVE,
            created_at=now,
            updated_at=now,
        )
        patient = Patient(
            patient_id=patient_id,
            status=PatientStatus.ACTIVE,
            preferred_language=command.preferred_language,
            created_at=now,
            updated_at=now,
        )
        try:
            async with database.transaction() as transaction:
                if await self._accounts.get_by_email(transaction, command.email.normalized):
                    raise self._registration_conflict()
                await self._patients.add(transaction, patient)
                await self._actors.create(
                    transaction,
                    actor_id=actor_id,
                    actor_type=ActorType.PATIENT,
                    roles=frozenset({RoleCode.PATIENT}),
                    subject_id=patient_id,
                    institution_id=None,
                    created_at=now,
                )
                await self._accounts.add(transaction, account)
                session_record = await self._sessions.create(
                    transaction,
                    session_id=OpaqueId.new(),
                    session_type=SessionType.AUTHENTICATED,
                    language_preference=command.preferred_language,
                    token_hash=hash_session_token(token),
                    created_at=now,
                    expires_at=now + timedelta(minutes=self._settings.authenticated_ttl_minutes),
                    actor_id=actor_id,
                    patient_id=patient_id,
                )
                session = self._sessions.to_domain(session_record)
        except AccountAlreadyExistsError as error:
            raise self._registration_conflict(error) from error
        return AccountSession(
            account=current_account(account), session=session, session_token=token
        )

    async def login(self, command: LoginPatient) -> AccountSession:
        database = self._require_database()
        now = self._now()
        token = self._new_token()
        async with database.transaction() as transaction:
            account = await self._accounts.get_by_email(transaction, command.email.normalized)
            digest = (
                account.password_digest if account is not None else self._unknown_account_digest
            )
            password_valid = self._passwords.verify(command.password, digest)
            if account is None or not password_valid or account.status is not AccountStatus.ACTIVE:
                raise self._authentication_required()
            actor_record = await self._actors.get(transaction, account.actor_id)
            if actor_record is None:
                raise self._authentication_required()
            actor = self._actors.to_domain(actor_record)
            if (
                actor.status is not ActorStatus.ACTIVE
                or actor.actor_type is not ActorType.PATIENT
                or RoleCode.PATIENT not in actor.roles
                or actor.subject_id != account.patient_id
            ):
                raise self._authentication_required()
            session_record = await self._sessions.create(
                transaction,
                session_id=OpaqueId.new(),
                session_type=SessionType.AUTHENTICATED,
                language_preference=None,
                token_hash=hash_session_token(token),
                created_at=now,
                expires_at=now + timedelta(minutes=self._settings.authenticated_ttl_minutes),
                actor_id=account.actor_id,
                patient_id=account.patient_id,
            )
            session = self._sessions.to_domain(session_record)
        return AccountSession(
            account=current_account(account), session=session, session_token=token
        )

    async def authenticate(self, token: str) -> ActorContext:
        account, session, actor = await self._resolve_authenticated(token)
        return ActorContext(
            actor_id=actor.actor_id,
            actor_type=actor.actor_type.value,
            roles=frozenset(role.value for role in actor.roles),
            subject_id=account.patient_id,
            session_id=session.session_id,
            is_authenticated=True,
            mfa_verified=False,
        )

    async def get_current_account(self, token: str) -> CurrentAccount:
        account, _, _ = await self._resolve_authenticated(token)
        return await self._current_with_profile_state(account)

    async def update_display_name(self, token: str, display_name: DisplayName) -> CurrentAccount:
        account, _, _ = await self._resolve_authenticated(token)
        database = self._require_database()
        async with database.transaction() as transaction:
            updated = await self._accounts.save_display_name(
                transaction, account.actor_id, display_name, self._now()
            )
        return await self._current_with_profile_state(updated)

    async def _current_with_profile_state(self, account: PatientAccount) -> CurrentAccount:
        database = self._require_database()
        async with database.transaction() as transaction:
            patient = await self._patients.get(transaction, account.patient_id)
        demographics = None if patient is None else patient.demographics
        complete = (
            account.display_name is not None
            and demographics is not None
            and demographics.date_of_birth is not None
            and demographics.administrative_sex is not None
            and demographics.height_cm is not None
            and demographics.weight_kg is not None
        )
        return current_account(account, profile_complete=complete)

    async def close_session(self, token: str) -> None:
        database = self._require_database()
        now = self._now()
        async with database.transaction() as transaction:
            record = await self._sessions.get_by_token_hash(
                transaction, hash_session_token(token), for_update=True
            )
            if record is None:
                raise self._authentication_required()
            session = self._sessions.to_domain(record)
            self._ensure_session(session, now)
            self._sessions.close(record, closed_at=now)

    async def _resolve_authenticated(self, token: str) -> tuple[PatientAccount, Session, Actor]:
        database = self._require_database()
        now = self._now()
        async with database.transaction() as transaction:
            session_record = await self._sessions.get_by_token_hash(
                transaction, hash_session_token(token)
            )
            if session_record is None:
                raise self._authentication_required()
            session = self._sessions.to_domain(session_record)
            self._ensure_session(session, now)
            if session.actor_id is None or session.patient_id is None:
                raise self._authentication_required()
            account = await self._accounts.get_by_actor(transaction, session.actor_id)
            actor_record = await self._actors.get(transaction, session.actor_id)
            if account is None or actor_record is None:
                raise self._authentication_required()
            actor = self._actors.to_domain(actor_record)
            if (
                account.status is not AccountStatus.ACTIVE
                or actor.status is not ActorStatus.ACTIVE
                or account.actor_id != session.actor_id
                or account.patient_id != session.patient_id
                or actor.subject_id != session.patient_id
                or RoleCode.PATIENT not in actor.roles
            ):
                raise self._authentication_required()
            return account, session, actor

    @staticmethod
    def _ensure_session(session: Session, now: datetime) -> None:
        if session.session_type is not SessionType.AUTHENTICATED:
            raise PatientAccountService._authentication_required()
        if session.status is not SessionStatus.ACTIVE:
            raise PatientAccountService._authentication_required()
        if now >= session.expires_at.astimezone(UTC):
            raise ApplicationError(
                code=ErrorCode.SESSION_EXPIRED, message="The session has expired."
            )

    def _require_database(self) -> DatabaseRuntime:
        if self._database is None:
            raise DependencyError(
                code=ErrorCode.DEPENDENCY_UNAVAILABLE,
                message="Patient account persistence is temporarily unavailable.",
            )
        return self._database

    def _now(self) -> datetime:
        value = self._clock()
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("patient account clock must be timezone-aware")
        return value.astimezone(UTC)

    def _new_token(self) -> str:
        token = self._token_factory()
        if not token:
            raise ValueError("session token factory must return a non-empty token")
        return token

    @staticmethod
    def _authentication_required() -> ApplicationError:
        return ApplicationError(
            code=ErrorCode.AUTHENTICATION_REQUIRED,
            message="The credentials are invalid or the account is unavailable.",
        )

    @staticmethod
    def _registration_conflict(cause: Exception | None = None) -> ApplicationError:
        return ApplicationError(
            code=ErrorCode.RESOURCE_CONFLICT,
            message="An account could not be created with those details.",
            cause=cause,
        )
