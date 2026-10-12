"""SQLAlchemy consent record and module-owned PostgreSQL repository."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, Uuid, select, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.consent.domain import (
    ConsentPurpose,
    ConsentScope,
    ConsentStatus,
    ConsentSubjectType,
    NoticeVersion,
    RevocationReason,
)
from app.modules.consent.domain import (
    ConsentRecord as DomainConsentRecord,
)
from app.shared.persistence import Base
from app.shared.types import OpaqueId


class ConsentRecord(Base):
    """Authoritative purpose-specific consent lifecycle state."""

    __tablename__ = "consent_records"
    __table_args__ = (
        CheckConstraint(
            "subject_type IN ('SESSION','ACTOR','PATIENT')",
            name="subject_type_supported",
        ),
        CheckConstraint(
            "purpose IN ('GENERAL_PRODUCT_USE','EXTERNAL_AI_PROCESSING',"
            "'REFERRAL_SHARING','ABDM_EXCHANGE','RESEARCH_USE','CAREGIVER_ACCESS')",
            name="purpose_supported",
        ),
        CheckConstraint(
            "status IN ('GRANTED','REVOKED','EXPIRED','SUPERSEDED')",
            name="status_supported",
        ),
        CheckConstraint(
            "jsonb_typeof(scope) = 'array' AND jsonb_array_length(scope) > 0",
            name="scope_json_array",
        ),
        CheckConstraint(
            "expires_at IS NULL OR expires_at > granted_at",
            name="expiry_after_grant",
        ),
        Index(
            "ix_consent_records_subject_type_subject_id_purpose_status",
            "subject_type",
            "subject_id",
            "purpose",
            "status",
        ),
        Index("ix_consent_records_actor_id", "actor_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    subject_type: Mapped[str] = mapped_column(String(16), nullable=False)
    subject_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    actor_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("actors.id", name="fk_consent_records_actor_id_actors"),
        nullable=True,
    )
    purpose: Mapped[str] = mapped_column(String(32), nullable=False)
    scope: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    notice_version: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=ConsentStatus.GRANTED.value,
        server_default=text("'GRANTED'"),
    )
    granted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revocation_reason: Mapped[str | None] = mapped_column(String(64), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    metadata_json: Mapped[dict[str, object] | None] = mapped_column(
        "metadata", JSONB, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    def __repr__(self) -> str:
        return (
            f"ConsentRecord(id={self.id!r}, subject_type={self.subject_type!r}, "
            f"purpose={self.purpose!r}, status={self.status!r})"
        )


class PostgresConsentRepository:
    """Narrow transaction-scoped consent persistence operations."""

    async def create(
        self,
        session: AsyncSession,
        *,
        consent_id: OpaqueId,
        subject_type: ConsentSubjectType,
        subject_id: OpaqueId,
        actor_id: OpaqueId | None,
        purpose: ConsentPurpose,
        scope: ConsentScope,
        notice_version: NoticeVersion,
        granted_at: datetime,
        expires_at: datetime | None,
    ) -> ConsentRecord:
        record = ConsentRecord(
            id=consent_id.value,
            subject_type=subject_type.value,
            subject_id=subject_id.value,
            actor_id=None if actor_id is None else actor_id.value,
            purpose=purpose.value,
            scope=list(scope.values),
            notice_version=str(notice_version),
            status=ConsentStatus.GRANTED.value,
            granted_at=granted_at,
            revoked_at=None,
            revocation_reason=None,
            expires_at=expires_at,
            metadata_json=None,
            created_at=granted_at,
            updated_at=granted_at,
        )
        session.add(record)
        await session.flush()
        return record

    async def get(self, session: AsyncSession, consent_id: OpaqueId) -> ConsentRecord | None:
        return await session.get(ConsentRecord, consent_id.value)

    async def get_for_update(
        self, session: AsyncSession, consent_id: OpaqueId
    ) -> ConsentRecord | None:
        statement = (
            select(ConsentRecord).where(ConsentRecord.id == consent_id.value).with_for_update()
        )
        return (await session.execute(statement)).scalar_one_or_none()

    async def list_for_subject(
        self,
        session: AsyncSession,
        *,
        subject_type: ConsentSubjectType,
        subject_id: OpaqueId,
        purpose: ConsentPurpose | None,
        status: ConsentStatus | None,
    ) -> tuple[ConsentRecord, ...]:
        statement = select(ConsentRecord).where(
            ConsentRecord.subject_type == subject_type.value,
            ConsentRecord.subject_id == subject_id.value,
        )
        if purpose is not None:
            statement = statement.where(ConsentRecord.purpose == purpose.value)
        if status is not None:
            statement = statement.where(ConsentRecord.status == status.value)
        statement = statement.order_by(ConsentRecord.granted_at.desc(), ConsentRecord.id.desc())
        return tuple((await session.execute(statement)).scalars())

    async def find_granted_matching(
        self,
        session: AsyncSession,
        *,
        subject_type: ConsentSubjectType,
        subject_id: OpaqueId,
        purpose: ConsentPurpose,
    ) -> tuple[ConsentRecord, ...]:
        statement = select(ConsentRecord).where(
            ConsentRecord.subject_type == subject_type.value,
            ConsentRecord.subject_id == subject_id.value,
            ConsentRecord.purpose == purpose.value,
            ConsentRecord.status == ConsentStatus.GRANTED.value,
        )
        return tuple((await session.execute(statement)).scalars())

    def revoke(
        self,
        record: object,
        *,
        revoked_at: datetime,
        reason: RevocationReason,
    ) -> DomainConsentRecord:
        if not isinstance(record, ConsentRecord):
            raise TypeError("consent repository received an unexpected record")
        record.status = ConsentStatus.REVOKED.value
        record.revoked_at = revoked_at
        record.revocation_reason = str(reason)
        record.updated_at = revoked_at
        return self.to_domain(record)

    def to_domain(self, record: object) -> DomainConsentRecord:
        if not isinstance(record, ConsentRecord):
            raise TypeError("consent repository received an unexpected record")
        return DomainConsentRecord(
            consent_id=OpaqueId(record.id),
            subject_type=ConsentSubjectType(record.subject_type),
            subject_id=OpaqueId(record.subject_id),
            actor_id=None if record.actor_id is None else OpaqueId(record.actor_id),
            purpose=ConsentPurpose(record.purpose),
            scope=ConsentScope(tuple(record.scope)),
            notice_version=NoticeVersion(record.notice_version),
            status=ConsentStatus(record.status),
            granted_at=record.granted_at,
            revoked_at=record.revoked_at,
            revocation_reason=(
                None
                if record.revocation_reason is None
                else RevocationReason(record.revocation_reason)
            ),
            expires_at=record.expires_at,
            metadata=record.metadata_json,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )
