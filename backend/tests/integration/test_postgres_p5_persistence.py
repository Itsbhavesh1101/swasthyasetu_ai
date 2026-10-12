"""Real PostgreSQL verification for P5-B persistence and atomicity."""

from __future__ import annotations

import os
from collections.abc import AsyncIterator
from dataclasses import replace
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import cast

import pytest
from sqlalchemy import Table, func, select, text, update
from sqlalchemy.exc import IntegrityError

from app.config import DatabaseSettings
from app.modules.encounters.infrastructure import (
    EncounterRecord,
    PostgresEncounterRepository,
    StaleEncounterWriteError,
)
from app.modules.encounters.public import Encounter, EncounterStatus, EncounterType
from app.modules.patients.infrastructure import (
    AllergyRecordProjection,
    ClinicalFactProvenanceRecord,
    ClinicalFactRecord,
    MedicationRecordProjection,
    ObservationRecordProjection,
    PatientIdentifierRecord,
    PatientRecord,
    PostgresClinicalFactRepository,
    PostgresPatientRepository,
)
from app.modules.patients.public import (
    AllergyRecord,
    ClinicalFact,
    FactType,
    InvestigationRecord,
    MedicationRecord,
    MedicationStatus,
    Observation,
    Patient,
    PatientDemographics,
    PatientIdentifier,
    PatientStatus,
    Problem,
    ProblemStatus,
    ProcedureRecord,
    ReferenceRange,
    supersede_fact,
)
from app.modules.provenance.public import (
    FactProvenance,
    ProvenanceSourceType,
    VerificationState,
)
from app.modules.sessions.infrastructure import SessionRecord
from app.shared.persistence import DatabaseRuntime
from app.shared.types import OpaqueId

pytestmark = pytest.mark.postgres

NOW = datetime(2026, 10, 12, 8, tzinfo=UTC)


@pytest.fixture
async def database_runtime() -> AsyncIterator[DatabaseRuntime]:
    test_url = os.getenv("SWASTHYASETU_TEST_DATABASE_URL")
    if test_url is None:
        pytest.skip("SWASTHYASETU_TEST_DATABASE_URL is not configured")
    runtime = DatabaseRuntime(DatabaseSettings(enabled=True, url=test_url))
    truncate = text(
        "TRUNCATE TABLE observations, allergies, medications, clinical_fact_provenance, "
        "clinical_facts, encounters, patient_identifiers, patient_demographics, patients, "
        "consent_records, sessions, actor_roles, actors, outbox_events CASCADE"
    )
    async with runtime.engine.begin() as connection:
        await connection.execute(truncate)
    try:
        yield runtime
    finally:
        async with runtime.engine.begin() as connection:
            await connection.execute(truncate)
        await runtime.dispose()


def _patient(*, identifier_value: str = "synthetic-identifier") -> Patient:
    patient_id = OpaqueId.new()
    return Patient(
        patient_id=patient_id,
        status=PatientStatus.ACTIVE,
        created_at=NOW,
        updated_at=NOW,
        preferred_language="en-IN",
        demographics=PatientDemographics(
            date_of_birth=date(1990, 1, 1),
            age_years=36,
            administrative_sex="unspecified",
            gender_identity=None,
            pregnancy_status="unknown",
            location_context="synthetic-location",
        ),
        identifiers=(
            PatientIdentifier(
                identifier_id=OpaqueId.new(),
                patient_id=patient_id,
                system="hospital_mrn",
                value=identifier_value,
                use="usual",
                verified=True,
                source="synthetic-test",
            ),
        ),
    )


async def _add_session(runtime: DatabaseRuntime) -> OpaqueId:
    session_id = OpaqueId.new()
    async with runtime.transaction() as session:
        session.add(
            SessionRecord(
                id=session_id.value,
                session_type="PSEUDONYMOUS",
                actor_id=None,
                patient_id=None,
                language_preference=None,
                status="ACTIVE",
                token_hash=str(OpaqueId.new()).replace("-", ""),
                recovery_token_hash=None,
                created_at=NOW,
                expires_at=datetime(2026, 10, 13, 8, tzinfo=UTC),
                closed_at=None,
                updated_at=NOW,
            )
        )
    return session_id


def _provenance() -> FactProvenance:
    return FactProvenance(
        source_type=ProvenanceSourceType.DOCUMENT_AI,
        source_ref="synthetic-source-reference",
        extractor_type="synthetic-extractor",
        provider="synthetic-provider",
        model_id="synthetic-model",
        model_version="v1",
        prompt_version="p1",
        schema_version="s1",
        confidence=Decimal("0.75"),
        created_at=NOW,
    )


def _fact(patient_id: OpaqueId, value: object, fact_type: FactType) -> ClinicalFact:
    return ClinicalFact(
        fact_id=OpaqueId.new(),
        patient_id=patient_id,
        encounter_id=None,
        fact_type=fact_type,
        value=value,  # type: ignore[arg-type]
        normalized_code=None,
        coding_system=None,
        effective_time=NOW,
        recorded_at=NOW,
        verification_state=value.verification_state,  # type: ignore[attr-defined]
        provenance=_provenance(),
    )


async def test_patient_demographics_identifiers_round_trip_and_are_atomic(
    database_runtime: DatabaseRuntime, caplog: pytest.LogCaptureFixture
) -> None:
    repository = PostgresPatientRepository()
    marker = "synthetic-private-identifier-marker"
    patient = _patient(identifier_value=marker)

    async with database_runtime.transaction() as session:
        record = await repository.add(session, patient)
        assert marker not in repr(record.identifier_records[0])
    async with database_runtime.session_factory() as session:
        restored = await repository.get(session, patient.patient_id)
    assert restored == patient
    assert marker not in caplog.text

    rolled_back = _patient(identifier_value=marker)
    with pytest.raises(RuntimeError, match="synthetic patient rollback"):
        async with database_runtime.transaction() as session:
            await repository.add(session, rolled_back)
            raise RuntimeError("synthetic patient rollback")
    async with database_runtime.session_factory() as session:
        assert await repository.get(session, rolled_back.patient_id) is None


async def test_identifier_namespace_is_not_globally_unique(
    database_runtime: DatabaseRuntime,
) -> None:
    repository = PostgresPatientRepository()
    first = _patient(identifier_value="shared-local-mrn")
    second = _patient(identifier_value="shared-local-mrn")
    async with database_runtime.transaction() as session:
        await repository.add(session, first)
        await repository.add(session, second)
    async with database_runtime.session_factory() as session:
        count = await session.scalar(select(func.count()).select_from(PatientIdentifierRecord))
    assert count == 2


async def test_patient_save_round_trips_lifecycle_fields(
    database_runtime: DatabaseRuntime,
) -> None:
    repository = PostgresPatientRepository()
    patient = _patient()
    assert patient.demographics is not None
    changed = replace(
        patient,
        status=PatientStatus.INACTIVE,
        preferred_language="hi-IN",
        demographics=replace(patient.demographics, age_years=37),
        updated_at=datetime(2026, 10, 12, 9, tzinfo=UTC),
    )
    async with database_runtime.transaction() as session:
        await repository.add(session, patient)
    async with database_runtime.transaction() as session:
        assert await repository.save(session, changed) == changed
    async with database_runtime.session_factory() as session:
        assert await repository.get(session, patient.patient_id) == changed


async def test_pseudonymous_encounter_round_trip_transition_and_stale_write(
    database_runtime: DatabaseRuntime,
) -> None:
    repository = PostgresEncounterRepository()
    session_id = await _add_session(database_runtime)
    encounter = Encounter(
        encounter_id=OpaqueId.new(),
        patient_id=None,
        session_id=session_id,
        encounter_type=EncounterType.KIOSK_INTAKE,
        status=EncounterStatus.CREATED,
        started_at=NOW,
        created_by=None,
    )
    async with database_runtime.transaction() as session:
        await repository.add(session, encounter)
    async with database_runtime.session_factory() as session:
        assert await repository.get(session, encounter.encounter_id) == encounter

    transitioned = encounter.transition_to(EncounterStatus.IN_PROGRESS)
    async with database_runtime.transaction() as session:
        version = await repository.save(session, transitioned, expected_version=1, updated_at=NOW)
    assert version == 2
    with pytest.raises(StaleEncounterWriteError):
        async with database_runtime.transaction() as session:
            await repository.save(session, transitioned, expected_version=1, updated_at=NOW)


@pytest.mark.parametrize(
    ("fact_type", "value"),
    [
        (
            FactType.PROBLEM,
            Problem(
                label="Synthetic problem",
                status=ProblemStatus.ACTIVE,
                verification_state=VerificationState.NEEDS_CONFIRMATION,
            ),
        ),
        (
            FactType.MEDICATION,
            MedicationRecord(
                name="Synthetic medication",
                dose=Decimal("2.5"),
                dose_unit="mg",
                status=MedicationStatus.ACTIVE,
                verification_state=VerificationState.NEEDS_CONFIRMATION,
            ),
        ),
        (
            FactType.ALLERGY,
            AllergyRecord(
                substance="Synthetic substance",
                reaction="Synthetic reaction",
                status="ACTIVE_LOCAL_CODE",
                verification_state=VerificationState.NEEDS_CONFIRMATION,
            ),
        ),
        (
            FactType.PROCEDURE,
            ProcedureRecord(
                name="Synthetic procedure",
                performed_at=NOW,
                notes="Synthetic private note",
                verification_state=VerificationState.NEEDS_CONFIRMATION,
            ),
        ),
        (
            FactType.OBSERVATION,
            Observation(
                observation_type="synthetic-observation",
                value=Decimal("4.25"),
                unit="unit",
                reference_range=ReferenceRange(low=Decimal("3"), high=Decimal("5")),
                effective_at=NOW,
                verification_state=VerificationState.NEEDS_CONFIRMATION,
            ),
        ),
        (
            FactType.INVESTIGATION,
            InvestigationRecord(
                investigation_type="synthetic-investigation",
                result_summary="Synthetic private result",
                status="FINAL_LOCAL_CODE",
                verification_state=VerificationState.NEEDS_CONFIRMATION,
            ),
        ),
    ],
)
async def test_all_typed_facts_and_provenance_round_trip(
    database_runtime: DatabaseRuntime, fact_type: FactType, value: object
) -> None:
    patient = _patient()
    patient_repository = PostgresPatientRepository()
    fact_repository = PostgresClinicalFactRepository()
    fact = _fact(patient.patient_id, value, fact_type)
    async with database_runtime.transaction() as session:
        await patient_repository.add(session, patient)
        record = await fact_repository.add(session, fact)
        assert record.canonical_label
        assert record.source_text is None
        assert record.created_at == fact.recorded_at
        assert record.updated_at == fact.recorded_at
    async with database_runtime.session_factory() as session:
        restored = await fact_repository.get(session, fact.fact_id)
    assert restored == fact


async def test_fact_provenance_projection_and_rollback_are_atomic(
    database_runtime: DatabaseRuntime,
) -> None:
    patient = _patient()
    patient_repository = PostgresPatientRepository()
    fact_repository = PostgresClinicalFactRepository()
    medication = _fact(
        patient.patient_id,
        MedicationRecord(
            name="Synthetic medication",
            status=MedicationStatus.ACTIVE,
            verification_state=VerificationState.EXTRACTED,
        ),
        FactType.MEDICATION,
    )
    async with database_runtime.transaction() as session:
        await patient_repository.add(session, patient)
    with pytest.raises(RuntimeError, match="synthetic fact rollback"):
        async with database_runtime.transaction() as session:
            await fact_repository.add(session, medication)
            raise RuntimeError("synthetic fact rollback")
    async with database_runtime.session_factory() as session:
        assert await session.get(ClinicalFactRecord, medication.fact_id.value) is None
        assert (
            await session.scalar(select(func.count()).select_from(ClinicalFactProvenanceRecord))
            == 0
        )
        assert (
            await session.scalar(select(func.count()).select_from(MedicationRecordProjection)) == 0
        )


async def test_database_enforces_fk_checks_and_reserved_jsonb_metadata(
    database_runtime: DatabaseRuntime,
) -> None:
    invalid_patient = _patient()
    with pytest.raises(IntegrityError):
        async with database_runtime.transaction() as session:
            session.add(
                PatientRecord(
                    id=invalid_patient.patient_id.value,
                    status="NOT_A_PATIENT_STATUS",
                    preferred_language=None,
                    created_at=NOW,
                    updated_at=NOW,
                )
            )

    with pytest.raises(IntegrityError):
        async with database_runtime.transaction() as session:
            session.add(
                SessionRecord(
                    id=OpaqueId.new().value,
                    session_type="PSEUDONYMOUS",
                    actor_id=None,
                    patient_id=OpaqueId.new().value,
                    language_preference=None,
                    status="ACTIVE",
                    token_hash=str(OpaqueId.new()).replace("-", ""),
                    recovery_token_hash=None,
                    created_at=NOW,
                    expires_at=datetime(2026, 10, 13, 8, tzinfo=UTC),
                    closed_at=None,
                    updated_at=NOW,
                )
            )

    patient = _patient()
    fact = _fact(
        patient.patient_id,
        Problem(
            label="Synthetic metadata check",
            status=ProblemStatus.ACTIVE,
            verification_state=VerificationState.NEEDS_CONFIRMATION,
        ),
        FactType.PROBLEM,
    )
    async with database_runtime.transaction() as session:
        await PostgresPatientRepository().add(session, patient)
        await PostgresClinicalFactRepository().add(session, fact)
        provenance_id = await session.scalar(
            select(ClinicalFactProvenanceRecord.id).where(
                ClinicalFactProvenanceRecord.fact_id == fact.fact_id.value
            )
        )
        assert provenance_id is not None
        await session.execute(
            update(ClinicalFactProvenanceRecord)
            .where(ClinicalFactProvenanceRecord.id == provenance_id)
            .values(metadata_json={"schema_version": "internal-test-v1"})
        )
    async with database_runtime.session_factory() as session:
        metadata = await session.scalar(
            select(ClinicalFactProvenanceRecord.metadata_json).where(
                ClinicalFactProvenanceRecord.id == provenance_id
            )
        )
    assert metadata == {"schema_version": "internal-test-v1"}


async def test_medication_allergy_observation_projections_match_source_fact(
    database_runtime: DatabaseRuntime,
) -> None:
    patient = _patient()
    patient_repository = PostgresPatientRepository()
    fact_repository = PostgresClinicalFactRepository()
    facts = (
        _fact(
            patient.patient_id,
            MedicationRecord(
                name="Synthetic medication",
                status=MedicationStatus.ACTIVE,
                verification_state=VerificationState.PATIENT_CONFIRMED,
            ),
            FactType.MEDICATION,
        ),
        _fact(
            patient.patient_id,
            AllergyRecord(
                substance="Synthetic substance",
                status="ACTIVE_LOCAL_CODE",
                verification_state=VerificationState.PATIENT_CONFIRMED,
            ),
            FactType.ALLERGY,
        ),
        _fact(
            patient.patient_id,
            Observation(
                observation_type="synthetic-observation",
                value="present",
                unit="original-unit",
                verification_state=VerificationState.PATIENT_CONFIRMED,
            ),
            FactType.OBSERVATION,
        ),
    )
    async with database_runtime.transaction() as session:
        await patient_repository.add(session, patient)
        for fact in facts:
            await fact_repository.add(session, fact)
    async with database_runtime.session_factory() as session:
        medication = await session.get(MedicationRecordProjection, facts[0].fact_id.value)
        allergy = await session.get(AllergyRecordProjection, facts[1].fact_id.value)
        observation = await session.get(ObservationRecordProjection, facts[2].fact_id.value)
    assert medication is not None and medication.source_fact_id == facts[0].fact_id.value
    assert allergy is not None and allergy.source_fact_id == facts[1].fact_id.value
    assert observation is not None and observation.unit == "original-unit"


async def test_supersession_update_and_replacement_insert_are_atomic(
    database_runtime: DatabaseRuntime,
) -> None:
    patient = _patient()
    patient_repository = PostgresPatientRepository()
    fact_repository = PostgresClinicalFactRepository()
    existing = _fact(
        patient.patient_id,
        Problem(
            label="Synthetic original",
            status=ProblemStatus.ACTIVE,
            verification_state=VerificationState.CLINICIAN_CONFIRMED,
        ),
        FactType.PROBLEM,
    )
    replacement = _fact(
        patient.patient_id,
        Problem(
            label="Synthetic correction",
            status=ProblemStatus.ACTIVE,
            verification_state=VerificationState.CLINICIAN_CONFIRMED,
        ),
        FactType.PROBLEM,
    )
    supersession = supersede_fact(existing, replacement)
    async with database_runtime.transaction() as session:
        await patient_repository.add(session, patient)
        await fact_repository.add(session, existing)

    with pytest.raises(RuntimeError, match="synthetic supersession rollback"):
        async with database_runtime.transaction() as session:
            await fact_repository.persist_supersession(session, supersession)
            raise RuntimeError("synthetic supersession rollback")
    async with database_runtime.session_factory() as session:
        original_after_rollback = await fact_repository.get(session, existing.fact_id)
        replacement_after_rollback = await fact_repository.get(session, replacement.fact_id)
    assert original_after_rollback == existing
    assert replacement_after_rollback is None

    async with database_runtime.transaction() as session:
        await fact_repository.persist_supersession(session, supersession)
    async with database_runtime.session_factory() as session:
        historical = await fact_repository.get(session, existing.fact_id)
        persisted_replacement = await fact_repository.get(session, replacement.fact_id)
    assert historical == supersession.superseded
    assert persisted_replacement == replacement


async def test_p5_tables_and_sessions_patient_fk_are_registered() -> None:
    expected = {
        "patients",
        "patient_demographics",
        "patient_identifiers",
        "encounters",
        "clinical_facts",
        "clinical_fact_provenance",
        "medications",
        "allergies",
        "observations",
    }
    assert expected == {
        PatientRecord.__tablename__,
        "patient_demographics",
        "patient_identifiers",
        EncounterRecord.__tablename__,
        ClinicalFactRecord.__tablename__,
        ClinicalFactProvenanceRecord.__tablename__,
        MedicationRecordProjection.__tablename__,
        AllergyRecordProjection.__tablename__,
        ObservationRecordProjection.__tablename__,
    }
    session_table = cast(Table, SessionRecord.__table__)
    patient_fk = next(
        constraint
        for constraint in session_table.foreign_key_constraints
        if tuple(constraint.column_keys) == ("patient_id",)
    )
    assert patient_fk.name == "fk_sessions_patient_id_patients"
