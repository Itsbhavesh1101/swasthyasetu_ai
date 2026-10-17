"""P7-A PostgreSQL records and caller-transaction-scoped repositories."""

from __future__ import annotations

from dataclasses import replace
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
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.clinical_intake.contracts import (
    ClinicalIntakeAlreadyExistsError,
    ClinicalIntakeIdentityError,
    IntakeAnswer,
    IntakeAnswerSourceType,
    QuestionnaireInstance,
    QuestionnaireInstanceIdentityError,
    QuestionnaireStatus,
    StaleClinicalIntakeWriteError,
)
from app.modules.clinical_intake.domain import (
    ClinicalIntake,
    ClinicalIntakeStatus,
    normalize_utc,
)
from app.modules.clinical_intake.serialization import (
    deserialize_answer,
    deserialize_chief_complaint,
    deserialize_contradictions,
    deserialize_history_sections,
    deserialize_hpi,
    deserialize_missing_information,
    deserialize_questionnaire_responses,
    serialize_answer,
    serialize_chief_complaint,
    serialize_contradictions,
    serialize_history_sections,
    serialize_hpi,
    serialize_missing_information,
    serialize_questionnaire_responses,
)
from app.shared.persistence import Base
from app.shared.types import OpaqueId


class ClinicalIntakeRecord(Base):
    __tablename__ = "clinical_intakes"
    __table_args__ = (
        CheckConstraint(
            "status IN ('IN_PROGRESS','COMPLETED','ABANDONED')", name="status_supported"
        ),
        CheckConstraint("version > 0", name="version_positive"),
        CheckConstraint(
            "(status = 'COMPLETED' AND completed_at IS NOT NULL) OR "
            "(status <> 'COMPLETED' AND completed_at IS NULL)",
            name="completed_at_lifecycle",
        ),
        CheckConstraint(
            "chief_complaint IS NULL OR jsonb_typeof(chief_complaint) = 'object'",
            name="chief_complaint_json_object",
        ),
        CheckConstraint("hpi IS NULL OR jsonb_typeof(hpi) = 'object'", name="hpi_json_object"),
        CheckConstraint(
            "jsonb_typeof(history_sections) = 'object'", name="history_sections_json_object"
        ),
        CheckConstraint(
            "jsonb_typeof(missing_information) = 'array'", name="missing_information_json_array"
        ),
        CheckConstraint("jsonb_typeof(contradictions) = 'array'", name="contradictions_json_array"),
    )
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    encounter_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("encounters.id"), nullable=False, unique=True
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    chief_complaint: Mapped[dict[str, object] | None] = mapped_column(
        JSONB(none_as_null=True), nullable=True
    )
    hpi: Mapped[dict[str, object] | None] = mapped_column(JSONB(none_as_null=True), nullable=True)
    history_sections: Mapped[dict[str, object]] = mapped_column(
        JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb")
    )
    missing_information: Mapped[list[object]] = mapped_column(
        JSONB, nullable=False, default=list, server_default=text("'[]'::jsonb")
    )
    contradictions: Mapped[list[object]] = mapped_column(
        JSONB, nullable=False, default=list, server_default=text("'[]'::jsonb")
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    version: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default=text("1")
    )

    def __repr__(self) -> str:
        return (
            f"ClinicalIntakeRecord(id={self.id!r}, status={self.status!r}, "
            f"version={self.version!r})"
        )


class IntakeAnswerRecord(Base):
    __tablename__ = "intake_answers"
    __table_args__ = (
        CheckConstraint(
            "source_type IN ('PATIENT_TEXT','PATIENT_TOUCH','REUSED_HISTORY')",
            name="source_type_supported",
        ),
        CheckConstraint("jsonb_typeof(answer) = 'object'", name="answer_json_object"),
        Index("ix_intake_answers_intake_id_question_id", "intake_id", "question_id"),
    )
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    intake_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("clinical_intakes.id"), nullable=False
    )
    question_id: Mapped[str] = mapped_column(String(128), nullable=False)
    question_version: Mapped[str] = mapped_column(String(64), nullable=False)
    answer: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    answered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class QuestionnaireInstanceRecord(Base):
    __tablename__ = "questionnaire_instances"
    __table_args__ = (
        CheckConstraint("status IN ('ACTIVE','COMPLETED','ABANDONED')", name="status_supported"),
        CheckConstraint("jsonb_typeof(responses) = 'object'", name="responses_json_object"),
        CheckConstraint(
            "(status = 'COMPLETED' AND completed_at IS NOT NULL) OR "
            "(status <> 'COMPLETED' AND completed_at IS NULL)",
            name="completed_at_lifecycle",
        ),
        Index(
            "ix_questionnaire_instances_encounter_questionnaire",
            "encounter_id",
            "questionnaire_id",
            "questionnaire_version",
        ),
    )
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    encounter_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("encounters.id"), nullable=False
    )
    questionnaire_id: Mapped[str] = mapped_column(String(128), nullable=False)
    questionnaire_version: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    responses: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


def _constraint_name(error: IntegrityError) -> str | None:
    diagnostic = getattr(getattr(error, "orig", None), "diag", None)
    return cast(str | None, getattr(diagnostic, "constraint_name", None))


class PostgresClinicalIntakeRepository:
    async def add(self, session: AsyncSession, intake: ClinicalIntake) -> ClinicalIntakeRecord:
        if intake.version != 1:
            raise ValueError("new clinical intake version must be 1")
        record = ClinicalIntakeRecord(
            id=intake.intake_id.value,
            encounter_id=intake.encounter_id.value,
            status=intake.status.value,
            chief_complaint=None
            if intake.chief_complaint is None
            else serialize_chief_complaint(intake.chief_complaint),
            hpi=None if intake.hpi is None else serialize_hpi(intake.hpi),
            history_sections=serialize_history_sections(intake.history_sections),
            missing_information=serialize_missing_information(intake.missing_information),
            contradictions=serialize_contradictions(intake.contradictions),
            started_at=intake.started_at,
            completed_at=intake.completed_at,
            created_at=intake.started_at,
            updated_at=intake.started_at,
            version=intake.version,
        )
        try:
            async with session.begin_nested():
                session.add(record)
                await session.flush()
        except IntegrityError as error:
            if _constraint_name(error) == "uq_clinical_intakes_encounter_id":
                raise ClinicalIntakeAlreadyExistsError(
                    "clinical intake already exists for encounter"
                ) from error
            raise
        return record

    async def get(self, session: AsyncSession, intake_id: OpaqueId) -> ClinicalIntake | None:
        record = await session.get(ClinicalIntakeRecord, intake_id.value)
        return None if record is None else self.to_domain(record)

    async def get_by_encounter(
        self, session: AsyncSession, encounter_id: OpaqueId
    ) -> ClinicalIntake | None:
        record = (
            await session.execute(
                select(ClinicalIntakeRecord).where(
                    ClinicalIntakeRecord.encounter_id == encounter_id.value
                )
            )
        ).scalar_one_or_none()
        return None if record is None else self.to_domain(record)

    async def save(
        self,
        session: AsyncSession,
        intake: ClinicalIntake,
        *,
        expected_version: int,
        updated_at: datetime,
    ) -> ClinicalIntake:
        normalized_updated_at = normalize_utc("updated_at", updated_at)
        if intake.version != expected_version:
            raise StaleClinicalIntakeWriteError("clinical intake version is stale")
        record = (
            await session.execute(
                select(ClinicalIntakeRecord)
                .where(
                    ClinicalIntakeRecord.id == intake.intake_id.value,
                    ClinicalIntakeRecord.version == expected_version,
                )
                .with_for_update()
            )
        ).scalar_one_or_none()
        if record is None:
            raise StaleClinicalIntakeWriteError("clinical intake version is stale")
        if record.encounter_id != intake.encounter_id.value:
            raise ClinicalIntakeIdentityError("clinical intake encounter identity cannot change")
        persisted = self.to_domain(record)
        if (
            persisted.status is not ClinicalIntakeStatus.IN_PROGRESS
            or intake.status is not ClinicalIntakeStatus.IN_PROGRESS
        ):
            persisted.transition_to(intake.status, at=intake.completed_at)
        record.status = intake.status.value
        record.chief_complaint = (
            None
            if intake.chief_complaint is None
            else serialize_chief_complaint(intake.chief_complaint)
        )
        record.hpi = None if intake.hpi is None else serialize_hpi(intake.hpi)
        record.history_sections = serialize_history_sections(intake.history_sections)
        record.missing_information = serialize_missing_information(intake.missing_information)
        record.contradictions = serialize_contradictions(intake.contradictions)
        record.completed_at = intake.completed_at
        record.updated_at = normalized_updated_at
        record.version = expected_version + 1
        await session.flush()
        return replace(intake, version=record.version)

    def to_domain(self, record: ClinicalIntakeRecord) -> ClinicalIntake:
        return ClinicalIntake(
            intake_id=OpaqueId(record.id),
            encounter_id=OpaqueId(record.encounter_id),
            status=ClinicalIntakeStatus(record.status),
            chief_complaint=None
            if record.chief_complaint is None
            else deserialize_chief_complaint(record.chief_complaint),
            hpi=None if record.hpi is None else deserialize_hpi(record.hpi),
            history_sections=deserialize_history_sections(record.history_sections),
            missing_information=deserialize_missing_information(record.missing_information),
            contradictions=deserialize_contradictions(record.contradictions),
            started_at=record.started_at,
            completed_at=record.completed_at,
            version=record.version,
        )


class PostgresIntakeAnswerRepository:
    async def add(self, session: AsyncSession, answer: IntakeAnswer) -> IntakeAnswerRecord:
        record = IntakeAnswerRecord(
            id=answer.answer_id.value,
            intake_id=answer.intake_id.value,
            question_id=answer.question_id,
            question_version=answer.question_version,
            answer=serialize_answer(answer),
            source_type=answer.source_type.value,
            answered_at=answer.answered_at,
            created_at=answer.created_at,
        )
        session.add(record)
        await session.flush()
        return record

    async def list_for_intake(
        self, session: AsyncSession, intake_id: OpaqueId
    ) -> tuple[IntakeAnswer, ...]:
        records = (
            (
                await session.execute(
                    select(IntakeAnswerRecord)
                    .where(IntakeAnswerRecord.intake_id == intake_id.value)
                    .order_by(IntakeAnswerRecord.answered_at.asc(), IntakeAnswerRecord.id.asc())
                )
            )
            .scalars()
            .all()
        )
        return tuple(
            deserialize_answer(
                record.answer,
                answer_id=OpaqueId(record.id),
                intake_id=OpaqueId(record.intake_id),
                question_id=record.question_id,
                question_version=record.question_version,
                source_type=IntakeAnswerSourceType(record.source_type),
                answered_at=record.answered_at,
                created_at=record.created_at,
            )
            for record in records
        )


class PostgresQuestionnaireInstanceRepository:
    async def add(
        self, session: AsyncSession, instance: QuestionnaireInstance
    ) -> QuestionnaireInstanceRecord:
        record = QuestionnaireInstanceRecord(
            id=instance.instance_id.value,
            encounter_id=instance.encounter_id.value,
            questionnaire_id=instance.questionnaire_id,
            questionnaire_version=instance.questionnaire_version,
            status=instance.status.value,
            responses=serialize_questionnaire_responses(instance.responses),
            started_at=instance.started_at,
            completed_at=instance.completed_at,
        )
        session.add(record)
        await session.flush()
        return record

    async def get(
        self, session: AsyncSession, instance_id: OpaqueId
    ) -> QuestionnaireInstance | None:
        record = await session.get(QuestionnaireInstanceRecord, instance_id.value)
        return None if record is None else self.to_domain(record)

    async def list_for_encounter(
        self, session: AsyncSession, encounter_id: OpaqueId
    ) -> tuple[QuestionnaireInstance, ...]:
        records = (
            (
                await session.execute(
                    select(QuestionnaireInstanceRecord)
                    .where(QuestionnaireInstanceRecord.encounter_id == encounter_id.value)
                    .order_by(
                        QuestionnaireInstanceRecord.started_at.asc(),
                        QuestionnaireInstanceRecord.id.asc(),
                    )
                )
            )
            .scalars()
            .all()
        )
        return tuple(self.to_domain(record) for record in records)

    async def save(
        self, session: AsyncSession, instance: QuestionnaireInstance
    ) -> QuestionnaireInstance:
        record = (
            await session.execute(
                select(QuestionnaireInstanceRecord)
                .where(QuestionnaireInstanceRecord.id == instance.instance_id.value)
                .with_for_update()
            )
        ).scalar_one_or_none()
        if record is None:
            raise LookupError("questionnaire instance was not found")
        if (
            record.encounter_id != instance.encounter_id.value
            or record.questionnaire_id != instance.questionnaire_id
            or record.questionnaire_version != instance.questionnaire_version
        ):
            raise QuestionnaireInstanceIdentityError(
                "questionnaire instance identity cannot change"
            )
        record.status = instance.status.value
        record.responses = serialize_questionnaire_responses(instance.responses)
        record.completed_at = instance.completed_at
        await session.flush()
        return self.to_domain(record)

    def to_domain(self, record: QuestionnaireInstanceRecord) -> QuestionnaireInstance:
        return QuestionnaireInstance(
            instance_id=OpaqueId(record.id),
            encounter_id=OpaqueId(record.encounter_id),
            questionnaire_id=record.questionnaire_id,
            questionnaire_version=record.questionnaire_version,
            status=QuestionnaireStatus(record.status),
            responses=deserialize_questionnaire_responses(record.responses),
            started_at=record.started_at,
            completed_at=record.completed_at,
        )
