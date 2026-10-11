"""Typed application and repository contracts owned by sessions."""

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.sessions.domain import Session, SessionType
from app.shared.types import OpaqueId


@dataclass(frozen=True, slots=True)
class SessionCreationResult:
    """Creation metadata plus the bearer secret returned exactly once."""

    session: Session
    session_token: str

    def __repr__(self) -> str:
        return f"SessionCreationResult(session={self.session!r}, session_token=<redacted>)"


class CreateSessionCapability(Protocol):
    async def create_session(
        self, *, session_type: SessionType, language_preference: str | None
    ) -> SessionCreationResult: ...


class ReadSessionCapability(Protocol):
    async def get_session(self, *, session_id: OpaqueId, session_token: str) -> Session: ...


class ValidateSessionCapability(Protocol):
    async def validate_session(self, *, session_id: OpaqueId, session_token: str) -> Session: ...


class CloseSessionCapability(Protocol):
    async def close_session(self, *, session_id: OpaqueId, session_token: str) -> Session: ...


class SessionRepository(Protocol):
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
    ) -> object: ...

    async def get(self, session: AsyncSession, session_id: OpaqueId) -> object | None: ...

    async def get_for_update(
        self, session: AsyncSession, session_id: OpaqueId
    ) -> object | None: ...

    def to_domain(self, record: object) -> Session: ...

    def token_hash(self, record: object) -> str: ...

    def close(self, record: object, *, closed_at: datetime) -> Session: ...
