"""SQLAlchemy metadata record for the patient document vault."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    Uuid,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.patient_documents.domain import PatientDocument
from app.shared.persistence import Base
from app.shared.storage import ObjectKey
from app.shared.types import OpaqueId


class PatientDocumentRecord(Base):
    """Patient-owned metadata; document bytes remain in object storage."""

    __tablename__ = "patient_documents"
    __table_args__ = (
        CheckConstraint("byte_size > 0", name="byte_size_positive"),
        CheckConstraint("sha256_digest ~ '^[0-9a-f]{64}$'", name="sha256_digest_valid"),
        CheckConstraint(
            "length(btrim(display_name)) > 0 AND length(btrim(mime_type)) > 0",
            name="display_fields_nonempty",
        ),
        Index("ix_patient_documents_patient_id_created_at", "patient_id", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    patient_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("patients.id", name="fk_patient_documents_patient_id_patients"),
        nullable=False,
    )
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    byte_size: Mapped[int] = mapped_column(BigInteger(), nullable=False)
    object_key: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)
    sha256_digest: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return (
            f"PatientDocumentRecord(id={self.id!r}, patient_id={self.patient_id!r}, "
            f"mime_type={self.mime_type!r}, byte_size={self.byte_size!r}, "
            f"deleted_at={self.deleted_at!r})"
        )


class PostgresPatientDocumentRepository:
    async def add(self, session: AsyncSession, document: PatientDocument) -> PatientDocumentRecord:
        record = PatientDocumentRecord(
            id=document.document_id.value,
            patient_id=document.patient_id.value,
            display_name=document.display_name,
            mime_type=document.mime_type,
            byte_size=document.byte_size,
            object_key=str(document.object_key),
            sha256_digest=document.sha256_digest,
            created_at=document.created_at,
            deleted_at=document.deleted_at,
        )
        session.add(record)
        await session.flush()
        return record

    async def get_owned(
        self,
        session: AsyncSession,
        *,
        patient_id: OpaqueId,
        document_id: OpaqueId,
        for_update: bool = False,
    ) -> PatientDocument | None:
        statement = select(PatientDocumentRecord).where(
            PatientDocumentRecord.id == document_id.value,
            PatientDocumentRecord.patient_id == patient_id.value,
        )
        if for_update:
            statement = statement.with_for_update()
        record = (await session.execute(statement)).scalar_one_or_none()
        return None if record is None else self.to_domain(record)

    async def list_active(
        self, session: AsyncSession, *, patient_id: OpaqueId
    ) -> tuple[PatientDocument, ...]:
        statement = (
            select(PatientDocumentRecord)
            .where(
                PatientDocumentRecord.patient_id == patient_id.value,
                PatientDocumentRecord.deleted_at.is_(None),
            )
            .order_by(PatientDocumentRecord.created_at.desc(), PatientDocumentRecord.id.asc())
        )
        records = (await session.execute(statement)).scalars().all()
        return tuple(self.to_domain(record) for record in records)

    async def mark_deleted(
        self,
        session: AsyncSession,
        *,
        patient_id: OpaqueId,
        document_id: OpaqueId,
        deleted_at: datetime,
    ) -> PatientDocument | None:
        statement = (
            select(PatientDocumentRecord)
            .where(
                PatientDocumentRecord.id == document_id.value,
                PatientDocumentRecord.patient_id == patient_id.value,
            )
            .with_for_update()
        )
        record = (await session.execute(statement)).scalar_one_or_none()
        if record is None:
            return None
        if record.deleted_at is None:
            record.deleted_at = deleted_at
            await session.flush()
        return self.to_domain(record)

    @staticmethod
    def to_domain(record: PatientDocumentRecord) -> PatientDocument:
        return PatientDocument(
            document_id=OpaqueId(record.id),
            patient_id=OpaqueId(record.patient_id),
            display_name=record.display_name,
            mime_type=record.mime_type,
            byte_size=record.byte_size,
            object_key=ObjectKey(record.object_key),
            sha256_digest=record.sha256_digest,
            created_at=record.created_at,
            deleted_at=record.deleted_at,
        )
