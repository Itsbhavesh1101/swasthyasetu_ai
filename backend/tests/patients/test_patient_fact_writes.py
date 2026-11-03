"""Patient-entered clinical facts and explicit correction behavior."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import replace
from datetime import UTC, datetime, timedelta, timezone
from decimal import Decimal
from typing import cast

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.patients.application import PatientService
from app.modules.patients.clinical import (
    AllergyRecord,
    ClinicalFact,
    FactSupersession,
    FactType,
    InvestigationRecord,
    MedicationRecord,
    MedicationStatus,
    Observation,
    Problem,
    ProblemStatus,
    ProcedureRecord,
)
from app.modules.patients.contracts import FactCursor
from app.modules.patients.domain import Patient, PatientStatus
from app.modules.provenance.domain import ProvenanceSourceType, VerificationState
from app.shared.errors import ApplicationError, ErrorCode
from app.shared.persistence import DatabaseRuntime
from app.shared.types import OpaqueId

NOW = datetime(2026, 11, 3, 12, tzinfo=UTC)


class FakeDatabase:
    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[AsyncSession]:
        yield cast(AsyncSession, object())


class FakePatients:
    def __init__(self, patient: Patient) -> None:
        self.patient = patient

    async def get(self, session: AsyncSession, patient_id: OpaqueId) -> Patient | None:
        return self.patient if self.patient.patient_id == patient_id else None

    async def add(self, session: AsyncSession, patient: Patient) -> object:
        return patient

    async def save(
        self,
        session: AsyncSession,
        patient: Patient,
        *,
        expected_updated_at: datetime,
    ) -> Patient:
        return patient


class FakeFacts:
    def __init__(self) -> None:
        self.values: dict[OpaqueId, ClinicalFact] = {}

    async def add(self, session: AsyncSession, fact: ClinicalFact) -> object:
        self.values[fact.fact_id] = fact
        return fact

    async def get(self, session: AsyncSession, fact_id: OpaqueId) -> ClinicalFact | None:
        return self.values.get(fact_id)

    async def persist_supersession(
        self, session: AsyncSession, supersession: FactSupersession
    ) -> FactSupersession:
        from app.modules.patients.clinical import supersede_fact

        current = self.values.get(supersession.superseded.fact_id)
        if current is None:
            raise LookupError
        checked = supersede_fact(current, supersession.replacement)
        self.values[checked.superseded.fact_id] = checked.superseded
        self.values[checked.replacement.fact_id] = checked.replacement
        return checked

    async def list_for_patient(
        self,
        session: AsyncSession,
        *,
        patient_id: OpaqueId,
        fact_type: FactType | None,
        verification_state: VerificationState | None,
        from_time: datetime | None,
        to_time: datetime | None,
        cursor: FactCursor | None,
        limit: int,
    ) -> tuple[ClinicalFact, ...]:
        return tuple(self.values.values())[:limit]


def values() -> tuple[tuple[FactType, object], ...]:
    state = VerificationState.PATIENT_CONFIRMED
    return (
        (
            FactType.PROBLEM,
            Problem(
                label="Synthetic asthma", status=ProblemStatus.ACTIVE, verification_state=state
            ),
        ),
        (
            FactType.MEDICATION,
            MedicationRecord(
                name="Synthetic tablet",
                status=MedicationStatus.ACTIVE,
                verification_state=state,
                dose=Decimal("1"),
            ),
        ),
        (
            FactType.ALLERGY,
            AllergyRecord(substance="Synthetic pollen", status="ACTIVE", verification_state=state),
        ),
        (
            FactType.PROCEDURE,
            ProcedureRecord(name="Synthetic procedure", verification_state=state, performed_at=NOW),
        ),
        (
            FactType.OBSERVATION,
            Observation(
                observation_type="Synthetic reading",
                value=Decimal("12.5"),
                verification_state=state,
                effective_at=NOW,
            ),
        ),
        (
            FactType.INVESTIGATION,
            InvestigationRecord(
                investigation_type="Synthetic scan",
                status="COMPLETED",
                verification_state=state,
                performed_at=NOW,
            ),
        ),
    )


@pytest.mark.parametrize(("fact_type", "value"), values())
async def test_adds_every_supported_patient_value_with_patient_provenance(
    fact_type: FactType, value: object
) -> None:
    patient_id = OpaqueId.new()
    actor_id = OpaqueId.new()
    patient = Patient(patient_id, PatientStatus.ACTIVE, NOW, NOW)
    facts = FakeFacts()
    service = PatientService(
        database=cast(DatabaseRuntime, FakeDatabase()),
        patients=FakePatients(patient),
        facts=facts,
        clock=lambda: NOW.astimezone(timezone(timedelta(hours=5, minutes=30))),
    )

    fact = await service.add_patient_fact(
        patient_id=patient_id,
        actor_id=actor_id,
        fact_type=fact_type,
        value=value,  # type: ignore[arg-type]
        effective_time=NOW.astimezone(timezone(timedelta(hours=5, minutes=30))),
    )

    assert fact.patient_id == patient_id
    assert fact.encounter_id is None
    assert fact.verification_state is VerificationState.PATIENT_CONFIRMED
    assert fact.provenance.source_type is ProvenanceSourceType.PATIENT_REPORT
    assert fact.provenance.created_by == actor_id
    assert fact.recorded_at.tzinfo is UTC
    assert fact.effective_time == NOW


async def test_correction_preserves_old_fact_and_rejects_stale_repeat() -> None:
    patient_id = OpaqueId.new()
    actor_id = OpaqueId.new()
    patient = Patient(patient_id, PatientStatus.ACTIVE, NOW, NOW)
    facts = FakeFacts()
    service = PatientService(
        database=cast(DatabaseRuntime, FakeDatabase()),
        patients=FakePatients(patient),
        facts=facts,
        clock=lambda: NOW,
    )
    old = await service.add_patient_fact(
        patient_id=patient_id,
        actor_id=actor_id,
        fact_type=FactType.PROBLEM,
        value=Problem(
            label="Synthetic old",
            status=ProblemStatus.ACTIVE,
            verification_state=VerificationState.PATIENT_CONFIRMED,
        ),
        effective_time=None,
    )
    replacement = Problem(
        label="Synthetic corrected",
        status=ProblemStatus.RESOLVED,
        verification_state=VerificationState.PATIENT_CONFIRMED,
    )

    result = await service.supersede_patient_fact(
        patient_id=patient_id,
        actor_id=actor_id,
        expected_current_id=old.fact_id,
        fact_type=FactType.PROBLEM,
        value=replacement,
        effective_time=None,
    )
    with pytest.raises(ApplicationError) as stale:
        await service.supersede_patient_fact(
            patient_id=patient_id,
            actor_id=actor_id,
            expected_current_id=old.fact_id,
            fact_type=FactType.PROBLEM,
            value=replacement,
            effective_time=None,
        )
    assert result.superseded.fact_id == old.fact_id
    assert result.superseded.verification_state is VerificationState.SUPERSEDED
    assert result.replacement.fact_id != old.fact_id
    assert stale.value.code is ErrorCode.RESOURCE_CONFLICT


async def test_patient_correction_cannot_downgrade_clinician_confirmed_fact() -> None:
    patient_id = OpaqueId.new()
    actor_id = OpaqueId.new()
    patient = Patient(patient_id, PatientStatus.ACTIVE, NOW, NOW)
    facts = FakeFacts()
    service = PatientService(
        database=cast(DatabaseRuntime, FakeDatabase()),
        patients=FakePatients(patient),
        facts=facts,
        clock=lambda: NOW,
    )
    patient_fact = await service.add_patient_fact(
        patient_id=patient_id,
        actor_id=actor_id,
        fact_type=FactType.PROBLEM,
        value=Problem(
            label="Synthetic clinician fact",
            status=ProblemStatus.ACTIVE,
            verification_state=VerificationState.PATIENT_CONFIRMED,
        ),
        effective_time=None,
    )
    clinician_value = replace(
        patient_fact.value, verification_state=VerificationState.CLINICIAN_CONFIRMED
    )
    facts.values[patient_fact.fact_id] = replace(
        patient_fact,
        value=clinician_value,
        verification_state=VerificationState.CLINICIAN_CONFIRMED,
    )

    with pytest.raises(ApplicationError) as captured:
        await service.supersede_patient_fact(
            patient_id=patient_id,
            actor_id=actor_id,
            expected_current_id=patient_fact.fact_id,
            fact_type=FactType.PROBLEM,
            value=Problem(
                label="Synthetic lower trust",
                status=ProblemStatus.ACTIVE,
                verification_state=VerificationState.PATIENT_CONFIRMED,
            ),
            effective_time=None,
        )
    assert captured.value.code is ErrorCode.RESOURCE_CONFLICT
    assert (
        facts.values[patient_fact.fact_id].verification_state
        is VerificationState.CLINICIAN_CONFIRMED
    )
