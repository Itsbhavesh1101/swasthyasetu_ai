"""SQLAlchemy session model and module-owned repository."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, Index, String, Text, Uuid, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.sessions.domain import Session, SessionStatus, SessionType
from app.shared.persistence import Base
from app.shared.types import OpaqueId


class SessionRecord(Base):
    """Authoritative PostgreSQL session lifecycle and protected verifier."""

    __tablename__ = "sessions"
    __table_args__ = (
        CheckConstraint(
            "session_type IN ('PSEUDONYMOUS', 'AUTHENTICATED', 'KIOSK', "
            "'CLINICIAN', 'ADMIN', 'RESEARCH')",
            name="session_type_supported",
        ),
        CheckConstraint(
            "status IN ('ACTIVE', 'EXPIRED', 'CLOSED', 'REVOKED')",
            name="status_supported",
        ),
        CheckConstraint("expires_at > created_at", name="expiry_after_creation"),
        Index("ix_sessions_status_expires_at", "status", "expires_at"),
        Index("ix_sessions_patient_id", "patient_id"),
        Index("ix_sessions_actor_id", "actor_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    session_type: Mapped[str] = mapped_column(String(32), nullable=False)
    actor_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    patient_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    language_preference: Mapped[str | None] = mapped_column(String(35), nullable=True)
    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=SessionStatus.ACTIVE.value,
        server_default=text("'ACTIVE'"),
    )
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    recovery_token_hash: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    def __repr__(self) -> str:
        return (
            f"SessionRecord(id={self.id!r}, session_type={self.session_type!r}, "
            f"status={self.status!r})"
        )


class PostgresSessionRepository:
    """Narrow transaction-scoped operations for session creation/read/close."""

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
    ) -> SessionRecord:
        record = SessionRecord(
            id=session_id.value,
            session_type=session_type.value,
            actor_id=None,
            patient_id=None,
            language_preference=language_preference,
            status=SessionStatus.ACTIVE.value,
            token_hash=token_hash,
            recovery_token_hash=None,
            created_at=created_at,
            expires_at=expires_at,
            closed_at=None,
            updated_at=created_at,
        )
        session.add(record)
        await session.flush()
        return record

    async def get(self, session: AsyncSession, session_id: OpaqueId) -> SessionRecord | None:
        return await session.get(SessionRecord, session_id.value)

    async def get_for_update(
        self, session: AsyncSession, session_id: OpaqueId
    ) -> SessionRecord | None:
        statement = (
            select(SessionRecord).where(SessionRecord.id == session_id.value).with_for_update()
        )
        return (await session.execute(statement)).scalar_one_or_none()

    def to_domain(self, record: object) -> Session:
        if not isinstance(record, SessionRecord):
            raise TypeError("session repository received an unexpected record")
        return Session(
            session_id=OpaqueId(record.id),
            session_type=SessionType(record.session_type),
            language_preference=record.language_preference,
            status=SessionStatus(record.status),
            created_at=record.created_at,
            expires_at=record.expires_at,
            closed_at=record.closed_at,
            updated_at=record.updated_at,
        )

    def token_hash(self, record: object) -> str:
        if not isinstance(record, SessionRecord):
            raise TypeError("session repository received an unexpected record")
        return record.token_hash

    def close(self, record: object, *, closed_at: datetime) -> Session:
        if not isinstance(record, SessionRecord):
            raise TypeError("session repository received an unexpected record")
        record.status = SessionStatus.CLOSED.value
        record.closed_at = closed_at
        record.updated_at = closed_at
        return self.to_domain(record)
