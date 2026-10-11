"""Session lifecycle application service."""

from __future__ import annotations

import hashlib
import hmac
import secrets
from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from app.config import SessionsSettings
from app.modules.sessions.contracts import SessionCreationResult as SessionCreationResult
from app.modules.sessions.contracts import SessionRepository
from app.modules.sessions.domain import Session, SessionStatus, SessionType
from app.shared.errors import ApplicationError, DependencyError, ErrorCode
from app.shared.persistence import DatabaseRuntime
from app.shared.types import OpaqueId, utc_now

type Clock = Callable[[], datetime]
type TokenFactory = Callable[[], str]


def normalize_utc(name: str, value: datetime) -> datetime:
    """Reject naive values and normalize aware values to UTC."""
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value.astimezone(UTC)


def generate_session_token() -> str:
    """Generate an opaque URL-safe token from 32 CSPRNG bytes."""
    return secrets.token_urlsafe(32)


def hash_session_token(token: str) -> str:
    """Return the one-way SHA-256 bearer verifier stored by PostgreSQL."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class SessionService:
    """Coordinate session lifecycle against the authoritative database."""

    _CREATE_TYPES = {SessionType.PSEUDONYMOUS, SessionType.KIOSK}

    def __init__(
        self,
        *,
        database: DatabaseRuntime | None,
        settings: SessionsSettings,
        repository: SessionRepository,
        clock: Clock = utc_now,
        token_factory: TokenFactory = generate_session_token,
    ) -> None:
        self._database = database
        self._settings = settings
        self._repository = repository
        self._clock = clock
        self._token_factory = token_factory

    async def create_session(
        self, *, session_type: SessionType, language_preference: str | None
    ) -> SessionCreationResult:
        database = self._require_database()
        if session_type not in self._CREATE_TYPES:
            raise ApplicationError(
                code=ErrorCode.VALIDATION_ERROR,
                message="The requested session type is not available.",
            )
        now = self._now()
        ttl = self._ttl(session_type)
        token = self._token_factory()
        if not token:
            raise ValueError("session token factory must return a non-empty token")
        async with database.transaction() as transaction:
            record = await self._repository.create(
                transaction,
                session_id=OpaqueId.new(),
                session_type=session_type,
                language_preference=language_preference,
                token_hash=hash_session_token(token),
                created_at=now,
                expires_at=now + ttl,
            )
            result = self._repository.to_domain(record)
        return SessionCreationResult(session=result, session_token=token)

    async def get_session(self, *, session_id: OpaqueId, session_token: str) -> Session:
        database = self._require_database()
        now = self._now()
        async with database.transaction() as transaction:
            record = await self._repository.get(transaction, session_id)
            self._authenticate(record, session_token)
            value = self._repository.to_domain(record)
            self._ensure_current(value, now)
            return value

    async def validate_session(self, *, session_id: OpaqueId, session_token: str) -> Session:
        return await self.get_session(session_id=session_id, session_token=session_token)

    async def close_session(self, *, session_id: OpaqueId, session_token: str) -> Session:
        database = self._require_database()
        now = self._now()
        async with database.transaction() as transaction:
            record = await self._repository.get_for_update(transaction, session_id)
            self._authenticate(record, session_token)
            value = self._repository.to_domain(record)
            self._ensure_current(value, now)
            return self._repository.close(record, closed_at=now)

    def _require_database(self) -> DatabaseRuntime:
        if self._database is None:
            raise DependencyError(
                code=ErrorCode.DEPENDENCY_UNAVAILABLE,
                message="Session persistence is temporarily unavailable.",
            )
        return self._database

    def _now(self) -> datetime:
        return normalize_utc("session clock", self._clock())

    def _ttl(self, session_type: SessionType) -> timedelta:
        minutes = (
            self._settings.pseudonymous_ttl_minutes
            if session_type is SessionType.PSEUDONYMOUS
            else self._settings.kiosk_ttl_minutes
        )
        return timedelta(minutes=minutes)

    def _authenticate(self, record: object | None, token: str) -> None:
        supplied = hash_session_token(token)
        if record is None or not hmac.compare_digest(self._repository.token_hash(record), supplied):
            raise ApplicationError(
                code=ErrorCode.AUTHENTICATION_REQUIRED,
                message="A valid session bearer token is required.",
            )

    @staticmethod
    def _ensure_current(session: Session, now: datetime) -> None:
        expires_at = normalize_utc("expires_at", session.expires_at)
        if now >= expires_at:
            raise ApplicationError(
                code=ErrorCode.SESSION_EXPIRED,
                message="The session has expired.",
            )
        if session.status is not SessionStatus.ACTIVE:
            raise ApplicationError(
                code=ErrorCode.INVALID_STATE_TRANSITION,
                message="The session is not active.",
            )
