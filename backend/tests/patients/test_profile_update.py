"""Optimistic patient profile update behavior."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, date, datetime, timedelta, timezone
from typing import cast

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.patients.application import PatientService
from app.modules.patients.domain import Patient, PatientDemographics, PatientStatus
from app.shared.errors import ApplicationError, ErrorCode
from app.shared.persistence import DatabaseRuntime
from app.shared.types import OpaqueId

NOW = datetime(2026, 11, 3, 10, tzinfo=UTC)


class FakeDatabase:
    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[AsyncSession]:
        yield cast(AsyncSession, object())


class FakePatients:
    def __init__(self, patient: Patient | None) -> None:
        self.patient = patient

    async def get(self, session: AsyncSession, patient_id: OpaqueId) -> Patient | None:
        return (
            self.patient
            if self.patient is not None and self.patient.patient_id == patient_id
            else None
        )

    async def add(self, session: AsyncSession, patient: Patient) -> object:
        self.patient = patient
        return patient

    async def save(
        self,
        session: AsyncSession,
        patient: Patient,
        *,
        expected_updated_at: datetime,
    ) -> Patient:
        if self.patient is None or self.patient.updated_at != expected_updated_at:
            from app.modules.patients.contracts import PatientProfileConflictError

            raise PatientProfileConflictError
        self.patient = patient
        return patient


class FakeFacts:
    async def get(self, session: AsyncSession, fact_id: OpaqueId) -> None:
        return None

    async def list_for_patient(self, session: AsyncSession, **kwargs: object) -> tuple[()]:
        return ()


def patient() -> Patient:
    return Patient(
        patient_id=OpaqueId.new(), status=PatientStatus.ACTIVE, created_at=NOW, updated_at=NOW
    )


async def test_profile_update_is_optimistic_and_normalizes_clock_to_utc() -> None:
    existing = patient()
    repository = FakePatients(existing)
    service = PatientService(
        database=cast(DatabaseRuntime, FakeDatabase()),
        patients=repository,
        facts=FakeFacts(),
        clock=lambda: NOW.astimezone(timezone(timedelta(hours=5, minutes=30))),
    )
    demographics = PatientDemographics(date_of_birth=date(2000, 1, 2), location_context="Delhi")

    updated = await service.update_profile(
        patient_id=existing.patient_id,
        expected_updated_at=NOW,
        preferred_language="hi",
        demographics=demographics,
    )

    assert updated.preferred_language == "hi"
    assert updated.demographics == demographics
    assert updated.updated_at == NOW
    assert updated.updated_at.tzinfo is UTC


async def test_profile_update_rejects_stale_or_missing_patient_identically() -> None:
    existing = patient()
    failures: list[ApplicationError] = []
    for repository, patient_id in (
        (FakePatients(existing), existing.patient_id),
        (FakePatients(None), OpaqueId.new()),
    ):
        service = PatientService(
            database=cast(DatabaseRuntime, FakeDatabase()),
            patients=repository,
            facts=FakeFacts(),
            clock=lambda: NOW + timedelta(minutes=1),
        )
        with pytest.raises(ApplicationError) as captured:
            await service.update_profile(
                patient_id=patient_id,
                expected_updated_at=NOW - timedelta(seconds=1),
                preferred_language=None,
                demographics=None,
            )
        failures.append(captured.value)
    assert {failure.code for failure in failures} == {ErrorCode.RESOURCE_CONFLICT}
    assert len({failure.message for failure in failures}) == 1
