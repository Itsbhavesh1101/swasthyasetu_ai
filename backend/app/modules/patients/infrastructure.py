"""P5-B PostgreSQL records and narrow transaction-scoped repositories."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    Uuid,
    delete,
    select,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload

from app.modules.patients.persistence import (
    canonical_label,
    deserialize_clinical_value,
    serialize_clinical_value,
)
from app.modules.patients.public import (
    AllergyRecord,
    ClinicalFact,
    FactSupersession,
    FactType,
    MedicationRecord,
    Observation,
    Patient,
    PatientDemographics,
    PatientIdentifier,
    PatientStatus,
)
from app.modules.provenance.public import (
    FactProvenance,
    ProvenanceSourceType,
    VerificationState,
)
from app.shared.persistence import Base
from app.shared.types import OpaqueId


class PatientRecord(Base):
    __tablename__ = "patients"
    __table_args__ = (
        CheckConstraint(
            "status IN ('ACTIVE','INACTIVE','MERGED','DELETED_PENDING')",
            name="status_supported",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    preferred_language: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    demographics_record: Mapped[PatientDemographicsRecord | None] = relationship(
        back_populates="patient", cascade="all, delete-orphan", lazy="selectin", uselist=False
    )
    identifier_records: Mapped[list[PatientIdentifierRecord]] = relationship(
        back_populates="patient", cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"PatientRecord(id={self.id!r}, status={self.status!r})"


class PatientDemographicsRecord(Base):
    __tablename__ = "patient_demographics"
    __table_args__ = (
        CheckConstraint("age_years IS NULL OR age_years >= 0", name="age_years_non_negative"),
    )

    patient_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("patients.id", name="fk_patient_demographics_patient_id_patients"),
        primary_key=True,
    )
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    age_years: Mapped[int | None] = mapped_column(Integer, nullable=True)
    administrative_sex: Mapped[str | None] = mapped_column(String(256), nullable=True)
    gender_identity: Mapped[str | None] = mapped_column(String(256), nullable=True)
    pregnancy_status: Mapped[str | None] = mapped_column(String(256), nullable=True)
    location_context: Mapped[str | None] = mapped_column(String(256), nullable=True)
    demographics_metadata: Mapped[dict[str, object] | None] = mapped_column(JSONB, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    patient: Mapped[PatientRecord] = relationship(back_populates="demographics_record")

    def __repr__(self) -> str:
        return f"PatientDemographicsRecord(patient_id={self.patient_id!r})"


class PatientIdentifierRecord(Base):
    __tablename__ = "patient_identifiers"
    __table_args__ = (Index("ix_patient_identifiers_system_value", "system", "value"),)

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    patient_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("patients.id", name="fk_patient_identifiers_patient_id_patients"),
        nullable=False,
    )
    system: Mapped[str] = mapped_column(String(128), nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    use: Mapped[str | None] = mapped_column(String(64), nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, nullable=False)
    source: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    patient: Mapped[PatientRecord] = relationship(back_populates="identifier_records")

    def __repr__(self) -> str:
        return (
            f"PatientIdentifierRecord(id={self.id!r}, patient_id={self.patient_id!r}, "
            f"system={self.system!r}, verified={self.verified!r})"
        )


class ClinicalFactRecord(Base):
    __tablename__ = "clinical_facts"
    __table_args__ = (
        CheckConstraint(
            "fact_type IN ('SYMPTOM','PROBLEM','MEDICATION','ALLERGY','PROCEDURE',"
            "'OBSERVATION','INVESTIGATION','FAMILY_HISTORY','PERSONAL_HISTORY',"
            "'REVIEW_OF_SYSTEMS')",
            name="fact_type_supported",
        ),
        CheckConstraint(
            "verification_state IN ('EXTRACTED','LOW_CONFIDENCE','NEEDS_CONFIRMATION',"
            "'PATIENT_CONFIRMED','CLINICIAN_CONFIRMED','REJECTED','SUPERSEDED')",
            name="verification_state_supported",
        ),
        CheckConstraint(
            "superseded_by_fact_id IS NULL OR superseded_by_fact_id <> id",
            name="not_self_superseded",
        ),
        Index("ix_clinical_facts_patient_id", "patient_id"),
        Index("ix_clinical_facts_encounter_id", "encounter_id"),
        Index("ix_clinical_facts_patient_id_fact_type", "patient_id", "fact_type"),
        Index("ix_clinical_facts_verification_state", "verification_state"),
        Index("ix_clinical_facts_effective_at", "effective_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    patient_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("patients.id"), nullable=True
    )
    encounter_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("encounters.id"), nullable=True
    )
    fact_type: Mapped[str] = mapped_column(String(32), nullable=False)
    canonical_label: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    coding_system: Mapped[str | None] = mapped_column(Text, nullable=True)
    effective_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verification_state: Mapped[str] = mapped_column(String(32), nullable=False)
    structured_value: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    source_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    superseded_by_fact_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("clinical_facts.id", name="fk_clinical_facts_superseded_by_fact_id"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    provenance_records: Mapped[list[ClinicalFactProvenanceRecord]] = relationship(
        back_populates="fact", cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self) -> str:
        return (
            f"ClinicalFactRecord(id={self.id!r}, fact_type={self.fact_type!r}, "
            f"verification_state={self.verification_state!r})"
        )


class ClinicalFactProvenanceRecord(Base):
    __tablename__ = "clinical_fact_provenance"
    __table_args__ = (
        CheckConstraint(
            "source_type IN ('PATIENT_REPORT','CAREGIVER_REPORT','CLINICIAN','OCR',"
            "'DOCUMENT_AI','FHIR_IMPORT','ABDM_IMPORT','HIS_IMPORT','MODEL_INFERENCE',"
            "'ADMIN','SYSTEM')",
            name="source_type_supported",
        ),
        CheckConstraint(
            "confidence IS NULL OR (confidence >= 0 AND confidence <= 1)",
            name="confidence_range",
        ),
        Index("ix_clinical_fact_provenance_fact_id", "fact_id"),
        Index("ix_clinical_fact_provenance_source_type_source_id", "source_type", "source_id"),
        Index("ix_clinical_fact_provenance_model_id_model_version", "model_id", "model_version"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    fact_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("clinical_facts.id"), nullable=False
    )
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    source_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    source_ref: Mapped[str | None] = mapped_column(Text, nullable=True)
    extractor_type: Mapped[str | None] = mapped_column(String(128), nullable=True)
    provider: Mapped[str | None] = mapped_column(String(128), nullable=True)
    model_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(128), nullable=True)
    prompt_version: Mapped[str | None] = mapped_column(String(128), nullable=True)
    schema_version: Mapped[str | None] = mapped_column(String(128), nullable=True)
    confidence: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    created_by: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("actors.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    metadata_json: Mapped[dict[str, object] | None] = mapped_column(
        "metadata", JSONB, nullable=True
    )
    fact: Mapped[ClinicalFactRecord] = relationship(back_populates="provenance_records")

    def __repr__(self) -> str:
        return (
            f"ClinicalFactProvenanceRecord(id={self.id!r}, fact_id={self.fact_id!r}, "
            f"source_type={self.source_type!r})"
        )


class MedicationRecordProjection(Base):
    __tablename__ = "medications"
    __table_args__ = (
        CheckConstraint(
            "status IN ('ACTIVE','HISTORICAL','STOPPED','UNKNOWN')",
            name="status_supported",
        ),
        CheckConstraint(
            "verification_state IN ('EXTRACTED','LOW_CONFIDENCE','NEEDS_CONFIRMATION',"
            "'PATIENT_CONFIRMED','CLINICIAN_CONFIRMED','REJECTED','SUPERSEDED')",
            name="verification_state_supported",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    patient_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("patients.id"))
    source_fact_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("clinical_facts.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    dose_value: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    dose_unit: Mapped[str | None] = mapped_column(Text, nullable=True)
    route: Mapped[str | None] = mapped_column(Text, nullable=True)
    frequency: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    verification_state: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class AllergyRecordProjection(Base):
    __tablename__ = "allergies"
    __table_args__ = (
        CheckConstraint(
            "verification_state IN ('EXTRACTED','LOW_CONFIDENCE','NEEDS_CONFIRMATION',"
            "'PATIENT_CONFIRMED','CLINICIAN_CONFIRMED','REJECTED','SUPERSEDED')",
            name="verification_state_supported",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    patient_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("patients.id"))
    source_fact_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("clinical_facts.id"), nullable=False
    )
    substance: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    reaction: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(64), nullable=False)
    verification_state: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ObservationRecordProjection(Base):
    __tablename__ = "observations"
    __table_args__ = (
        CheckConstraint(
            "value_numeric IS NOT NULL OR value_text IS NOT NULL",
            name="value_present",
        ),
        CheckConstraint(
            "verification_state IN ('EXTRACTED','LOW_CONFIDENCE','NEEDS_CONFIRMATION',"
            "'PATIENT_CONFIRMED','CLINICIAN_CONFIRMED','REJECTED','SUPERSEDED')",
            name="verification_state_supported",
        ),
        Index(
            "ix_observations_patient_id_observation_type_effective_at",
            "patient_id",
            "observation_type",
            "effective_at",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    patient_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("patients.id"), nullable=True
    )
    encounter_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("encounters.id"), nullable=True
    )
    source_fact_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("clinical_facts.id"), nullable=False
    )
    observation_type: Mapped[str] = mapped_column(Text, nullable=False)
    value_numeric: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    value_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    unit: Mapped[str | None] = mapped_column(Text, nullable=True)
    normalized_value: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    normalized_unit: Mapped[str | None] = mapped_column(Text, nullable=True)
    reference_low: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    reference_high: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    abnormal_flag: Mapped[str | None] = mapped_column(String(128), nullable=True)
    effective_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verification_state: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


def _demographics_record(patient: Patient) -> PatientDemographicsRecord | None:
    value = patient.demographics
    if value is None:
        return None
    return PatientDemographicsRecord(
        patient_id=patient.patient_id.value,
        date_of_birth=value.date_of_birth,
        age_years=value.age_years,
        administrative_sex=value.administrative_sex,
        gender_identity=value.gender_identity,
        pregnancy_status=value.pregnancy_status,
        location_context=value.location_context,
        demographics_metadata=None,
        updated_at=patient.updated_at,
    )


def _identifier_records(patient: Patient) -> list[PatientIdentifierRecord]:
    return [
        PatientIdentifierRecord(
            id=value.identifier_id.value,
            patient_id=patient.patient_id.value,
            system=value.system,
            value=value.value,
            use=value.use,
            verified=value.verified,
            source=value.source,
            created_at=patient.created_at,
            updated_at=patient.updated_at,
        )
        for value in patient.identifiers
    ]


class PostgresPatientRepository:
    """Persist complete patient profile state in the caller's transaction."""

    async def add(self, session: AsyncSession, patient: Patient) -> PatientRecord:
        record = PatientRecord(
            id=patient.patient_id.value,
            status=patient.status.value,
            preferred_language=patient.preferred_language,
            created_at=patient.created_at,
            updated_at=patient.updated_at,
            demographics_record=_demographics_record(patient),
            identifier_records=_identifier_records(patient),
        )
        session.add(record)
        await session.flush()
        return record

    async def get(self, session: AsyncSession, patient_id: OpaqueId) -> Patient | None:
        statement = (
            select(PatientRecord)
            .options(
                selectinload(PatientRecord.demographics_record),
                selectinload(PatientRecord.identifier_records),
            )
            .where(PatientRecord.id == patient_id.value)
        )
        record = (await session.execute(statement)).scalar_one_or_none()
        return None if record is None else self.to_domain(record)

    async def save(self, session: AsyncSession, patient: Patient) -> Patient:
        statement = (
            select(PatientRecord)
            .options(
                selectinload(PatientRecord.demographics_record),
                selectinload(PatientRecord.identifier_records),
            )
            .where(PatientRecord.id == patient.patient_id.value)
            .with_for_update()
        )
        record = (await session.execute(statement)).scalar_one_or_none()
        if record is None:
            raise LookupError("patient record does not exist")
        record.status = patient.status.value
        record.preferred_language = patient.preferred_language
        record.updated_at = patient.updated_at
        record.demographics_record = _demographics_record(patient)
        record.identifier_records = _identifier_records(patient)
        await session.flush()
        return self.to_domain(record)

    def to_domain(self, record: PatientRecord) -> Patient:
        demographics = record.demographics_record
        return Patient(
            patient_id=OpaqueId(record.id),
            status=PatientStatus(record.status),
            created_at=record.created_at,
            updated_at=record.updated_at,
            preferred_language=record.preferred_language,
            demographics=(
                None
                if demographics is None
                else PatientDemographics(
                    date_of_birth=demographics.date_of_birth,
                    age_years=demographics.age_years,
                    administrative_sex=demographics.administrative_sex,
                    gender_identity=demographics.gender_identity,
                    pregnancy_status=demographics.pregnancy_status,
                    location_context=demographics.location_context,
                )
            ),
            identifiers=tuple(
                PatientIdentifier(
                    identifier_id=OpaqueId(identifier.id),
                    patient_id=OpaqueId(identifier.patient_id),
                    system=identifier.system,
                    value=identifier.value,
                    use=identifier.use,
                    verified=identifier.verified,
                    source=identifier.source,
                )
                for identifier in sorted(record.identifier_records, key=lambda item: item.id)
            ),
        )


def _provenance_record(fact: ClinicalFact) -> ClinicalFactProvenanceRecord:
    value = fact.provenance
    return ClinicalFactProvenanceRecord(
        id=OpaqueId.new().value,
        fact_id=fact.fact_id.value,
        source_type=value.source_type.value,
        source_id=None if value.source_id is None else value.source_id.value,
        source_ref=value.source_ref,
        extractor_type=value.extractor_type,
        provider=value.provider,
        model_id=value.model_id,
        model_version=value.model_version,
        prompt_version=value.prompt_version,
        schema_version=value.schema_version,
        confidence=value.confidence,
        created_by=None if value.created_by is None else value.created_by.value,
        created_at=value.created_at,
        metadata_json=None,
    )


def _projection(fact: ClinicalFact) -> Base | None:
    value = fact.value
    if isinstance(value, MedicationRecord):
        if fact.patient_id is None:
            raise ValueError("medication projection requires patient scope")
        return MedicationRecordProjection(
            id=fact.fact_id.value,
            patient_id=fact.patient_id.value,
            source_fact_id=fact.fact_id.value,
            name=value.name,
            normalized_code=value.normalized_code,
            dose_value=value.dose,
            dose_unit=value.dose_unit,
            route=value.route,
            frequency=value.frequency,
            start_date=value.start_date,
            end_date=value.end_date,
            status=value.status.value,
            verification_state=value.verification_state.value,
            created_at=fact.recorded_at,
            updated_at=fact.recorded_at,
        )
    if isinstance(value, AllergyRecord):
        if fact.patient_id is None:
            raise ValueError("allergy projection requires patient scope")
        return AllergyRecordProjection(
            id=fact.fact_id.value,
            patient_id=fact.patient_id.value,
            source_fact_id=fact.fact_id.value,
            substance=value.substance,
            normalized_code=value.normalized_code,
            reaction=value.reaction,
            severity=value.severity,
            status=value.status,
            verification_state=value.verification_state.value,
            created_at=fact.recorded_at,
            updated_at=fact.recorded_at,
        )
    if isinstance(value, Observation):
        reference = value.reference_range
        return ObservationRecordProjection(
            id=fact.fact_id.value,
            patient_id=None if fact.patient_id is None else fact.patient_id.value,
            encounter_id=None if fact.encounter_id is None else fact.encounter_id.value,
            source_fact_id=fact.fact_id.value,
            observation_type=value.observation_type,
            value_numeric=value.value if isinstance(value.value, Decimal) else None,
            value_text=value.value if isinstance(value.value, str) else None,
            unit=value.unit,
            normalized_value=value.normalized_value,
            normalized_unit=value.normalized_unit,
            reference_low=None if reference is None else reference.low,
            reference_high=None if reference is None else reference.high,
            abnormal_flag=value.abnormal_flag,
            effective_at=value.effective_at,
            verification_state=value.verification_state.value,
            created_at=fact.recorded_at,
        )
    return None


class PostgresClinicalFactRepository:
    """Persist canonical typed facts, provenance, and subordinate projections."""

    async def add(self, session: AsyncSession, fact: ClinicalFact) -> ClinicalFactRecord:
        record = ClinicalFactRecord(
            id=fact.fact_id.value,
            patient_id=None if fact.patient_id is None else fact.patient_id.value,
            encounter_id=None if fact.encounter_id is None else fact.encounter_id.value,
            fact_type=fact.fact_type.value,
            canonical_label=canonical_label(fact.value),
            normalized_code=fact.normalized_code,
            coding_system=fact.coding_system,
            effective_at=fact.effective_time,
            verification_state=fact.verification_state.value,
            structured_value=serialize_clinical_value(fact.fact_type, fact.value),
            source_text=None,
            superseded_by_fact_id=(
                None if fact.superseded_by_fact_id is None else fact.superseded_by_fact_id.value
            ),
            created_at=fact.recorded_at,
            updated_at=fact.recorded_at,
            provenance_records=[_provenance_record(fact)],
        )
        session.add(record)
        await session.flush()
        projection = _projection(fact)
        if projection is not None:
            session.add(projection)
        await session.flush()
        return record

    async def get(self, session: AsyncSession, fact_id: OpaqueId) -> ClinicalFact | None:
        statement = (
            select(ClinicalFactRecord)
            .options(selectinload(ClinicalFactRecord.provenance_records))
            .where(ClinicalFactRecord.id == fact_id.value)
        )
        record = (await session.execute(statement)).scalar_one_or_none()
        return None if record is None else self.to_domain(record)

    async def persist_supersession(
        self, session: AsyncSession, supersession: FactSupersession
    ) -> FactSupersession:
        existing = await session.get(
            ClinicalFactRecord, supersession.superseded.fact_id.value, with_for_update=True
        )
        if existing is None:
            raise LookupError("clinical fact record does not exist")
        await self.add(session, supersession.replacement)
        existing.verification_state = supersession.superseded.verification_state.value
        existing.structured_value = serialize_clinical_value(
            supersession.superseded.fact_type, supersession.superseded.value
        )
        existing.superseded_by_fact_id = supersession.replacement.fact_id.value
        existing.updated_at = supersession.replacement.recorded_at
        await self._update_projection(session, supersession.superseded)
        await session.flush()
        return supersession

    async def _update_projection(self, session: AsyncSession, fact: ClinicalFact) -> None:
        if fact.fact_type is FactType.MEDICATION:
            await session.execute(
                delete(MedicationRecordProjection).where(
                    MedicationRecordProjection.source_fact_id == fact.fact_id.value
                )
            )
        elif fact.fact_type is FactType.ALLERGY:
            await session.execute(
                delete(AllergyRecordProjection).where(
                    AllergyRecordProjection.source_fact_id == fact.fact_id.value
                )
            )
        elif fact.fact_type is FactType.OBSERVATION:
            await session.execute(
                delete(ObservationRecordProjection).where(
                    ObservationRecordProjection.source_fact_id == fact.fact_id.value
                )
            )
        else:
            return
        projection = _projection(fact)
        if projection is not None:
            session.add(projection)

    def to_domain(self, record: ClinicalFactRecord) -> ClinicalFact:
        if len(record.provenance_records) != 1:
            raise ValueError("clinical fact must have exactly one canonical provenance record")
        provenance = record.provenance_records[0]
        fact_type = FactType(record.fact_type)
        return ClinicalFact(
            fact_id=OpaqueId(record.id),
            patient_id=None if record.patient_id is None else OpaqueId(record.patient_id),
            encounter_id=None if record.encounter_id is None else OpaqueId(record.encounter_id),
            fact_type=fact_type,
            value=deserialize_clinical_value(fact_type, record.structured_value),
            normalized_code=record.normalized_code,
            coding_system=record.coding_system,
            effective_time=record.effective_at,
            recorded_at=record.created_at,
            verification_state=VerificationState(record.verification_state),
            provenance=FactProvenance(
                source_type=ProvenanceSourceType(provenance.source_type),
                source_id=(
                    None if provenance.source_id is None else OpaqueId(provenance.source_id)
                ),
                source_ref=provenance.source_ref,
                extractor_type=provenance.extractor_type,
                provider=provenance.provider,
                model_id=provenance.model_id,
                model_version=provenance.model_version,
                prompt_version=provenance.prompt_version,
                schema_version=provenance.schema_version,
                confidence=provenance.confidence,
                created_at=provenance.created_at,
                created_by=(
                    None if provenance.created_by is None else OpaqueId(provenance.created_by)
                ),
            ),
            superseded_by_fact_id=(
                None
                if record.superseded_by_fact_id is None
                else OpaqueId(record.superseded_by_fact_id)
            ),
        )
