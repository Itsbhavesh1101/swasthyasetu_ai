"""P5-B PostgreSQL encounter record and transaction-scoped repository."""

from datetime import datetime
from typing import cast
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Uuid,
    select,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.encounters.public import Encounter, EncounterStatus, EncounterType
from app.shared.persistence import Base
from app.shared.types import OpaqueId


class StaleEncounterWriteError(RuntimeError):
    """Raised when an encounter save does not match its expected version."""


class EncounterRecord(Base):
    __tablename__ = "encounters"
    __table_args__ = (
        CheckConstraint(
            "encounter_type IN ('GENERAL_INTAKE','MENTAL_HEALTH','KIOSK_INTAKE',"
            "'CLINICIAN_REVIEW','DOCUMENT_REVIEW','RESEARCH_ONLY')",
            name="encounter_type_supported",
        ),
        CheckConstraint(
            "status IN ('CREATED','IN_PROGRESS','AWAITING_REVIEW','COMPLETED',"
            "'ABANDONED','CANCELLED')",
            name="status_supported",
        ),
        CheckConstraint("version > 0", name="version_positive"),
        CheckConstraint(
            "(status = 'COMPLETED' AND completed_at IS NOT NULL) OR "
            "(status <> 'COMPLETED' AND completed_at IS NULL)",
            name="completed_at_lifecycle",
        ),
        Index("ix_encounters_patient_id", "patient_id"),
        Index("ix_encounters_session_id", "session_id"),
        Index("ix_encounters_status_started_at", "status", "started_at"),
        Index("ix_encounters_institution_id", "institution_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    patient_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("patients.id"), nullable=True
    )
    session_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("sessions.id"), nullable=False
    )
    encounter_type: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    institution_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    language_context: Mapped[dict[str, object] | None] = mapped_column(JSONB, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("actors.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    version: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default=text("1")
    )

    def __repr__(self) -> str:
        return (
            f"EncounterRecord(id={self.id!r}, encounter_type={self.encounter_type!r}, "
            f"status={self.status!r}, version={self.version!r})"
        )


def _language_context(value: str | None) -> dict[str, object] | None:
    if value is None:
        return None
    return {"schema_version": "p5b-v1", "value": value}


def _language_context_from_record(value: object) -> str | None:
    if value is None:
        return None
    if (
        not isinstance(value, dict)
        or set(value) != {"schema_version", "value"}
        or value.get("schema_version") != "p5b-v1"
        or not isinstance(value.get("value"), str)
    ):
        raise ValueError("encounter language context persistence shape is invalid")
    return cast(str, value["value"])


class PostgresEncounterRepository:
    """Persist encounters without committing the caller-owned transaction."""

    async def add(self, session: AsyncSession, encounter: Encounter) -> EncounterRecord:
        record = EncounterRecord(
            id=encounter.encounter_id.value,
            patient_id=None if encounter.patient_id is None else encounter.patient_id.value,
            session_id=encounter.session_id.value,
            encounter_type=encounter.encounter_type.value,
            status=encounter.status.value,
            institution_id=(
                None if encounter.institution_id is None else encounter.institution_id.value
            ),
            language_context=_language_context(encounter.language_context),
            started_at=encounter.started_at,
            completed_at=encounter.completed_at,
            created_by=None if encounter.created_by is None else encounter.created_by.value,
            created_at=encounter.started_at,
            updated_at=encounter.started_at,
            version=1,
        )
        session.add(record)
        await session.flush()
        return record

    async def get(self, session: AsyncSession, encounter_id: OpaqueId) -> Encounter | None:
        record = await session.get(EncounterRecord, encounter_id.value)
        return None if record is None else self.to_domain(record)

    async def save(
        self,
        session: AsyncSession,
        encounter: Encounter,
        *,
        expected_version: int,
        updated_at: datetime,
    ) -> int:
        statement = (
            select(EncounterRecord)
            .where(
                EncounterRecord.id == encounter.encounter_id.value,
                EncounterRecord.version == expected_version,
            )
            .with_for_update()
        )
        record = (await session.execute(statement)).scalar_one_or_none()
        if record is None:
            raise StaleEncounterWriteError("encounter version is stale")
        record.patient_id = None if encounter.patient_id is None else encounter.patient_id.value
        record.status = encounter.status.value
        record.completed_at = encounter.completed_at
        record.language_context = _language_context(encounter.language_context)
        record.updated_at = updated_at
        record.version += 1
        await session.flush()
        return record.version

    def to_domain(self, record: EncounterRecord) -> Encounter:
        return Encounter(
            encounter_id=OpaqueId(record.id),
            patient_id=None if record.patient_id is None else OpaqueId(record.patient_id),
            session_id=OpaqueId(record.session_id),
            encounter_type=EncounterType(record.encounter_type),
            status=EncounterStatus(record.status),
            started_at=record.started_at,
            completed_at=record.completed_at,
            institution_id=(
                None if record.institution_id is None else OpaqueId(record.institution_id)
            ),
            language_context=_language_context_from_record(record.language_context),
            created_by=None if record.created_by is None else OpaqueId(record.created_by),
        )
