"""Optimistic patient profile update behavior."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, date, datetime, timedelta, timezone
from typing import cast

import pytest
from pydantic import SecretStr, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.patients.api import (
    DemographicsRequest,
    patient_view,
    resolve_demographics,
)
from app.modules.patients.application import PatientService
from app.modules.patients.clinical import ClinicalFact, FactSupersession
from app.modules.patients.domain import BloodGroup, Patient, PatientDemographics, PatientStatus
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
    async def add(self, session: AsyncSession, fact: ClinicalFact) -> object:
        return fact

    async def get(self, session: AsyncSession, fact_id: OpaqueId) -> None:
        return None

    async def persist_supersession(
        self, session: AsyncSession, supersession: FactSupersession
    ) -> FactSupersession:
        return supersession

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
    demographics = PatientDemographics(
        date_of_birth=date(2000, 1, 2),
        location_context="Delhi",
        mobile_number="+919876543210",
        blood_group=BloodGroup.B_POSITIVE,
        aadhaar_last_four="2301",
    )

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


def test_demographics_request_accepts_valid_12_digits_and_redacts_representation() -> None:
    req = DemographicsRequest(aadhaar_number=SecretStr("123456789012"))
    assert req.aadhaar_number is not None
    assert req.aadhaar_number.get_secret_value() == "123456789012"
    # SecretStr must not expose raw digits in repr or str
    assert "123456789012" not in str(req)
    assert "123456789012" not in repr(req)
    assert "**********" in repr(req)


def test_demographics_request_rejects_malformed_aadhaar_inputs() -> None:
    invalid_inputs = [
        "12345678901",  # 11 digits
        "1234567890123",  # 13 digits
        "1234 5678 9012",  # spaces
        "1234-5678-9012",  # hyphens
        "12345678901a",  # alpha
        "১২৩৪৫৬৭৮৯০১২",  # non-ASCII unicode digits
        "",  # empty string
        " ",  # whitespace
    ]
    for invalid in invalid_inputs:
        with pytest.raises(ValidationError):
            DemographicsRequest(aadhaar_number=SecretStr(invalid))


def test_resolve_demographics_extracts_suffix_and_preserves_existing() -> None:
    # 1. New Aadhaar number extracts last 4 digits
    req1 = DemographicsRequest(
        date_of_birth=date(1995, 5, 20),
        aadhaar_number=SecretStr("987654321098"),
    )
    resolved1 = resolve_demographics(req1, current_demographics=None)
    assert resolved1 is not None
    assert resolved1.aadhaar_last_four == "1098"
    assert resolved1.date_of_birth == date(1995, 5, 20)

    # 2. Null Aadhaar replacement preserves existing suffix
    req2 = DemographicsRequest(
        location_context="Bangalore",
        aadhaar_number=None,
    )
    existing_demographics = PatientDemographics(
        aadhaar_last_four="1098",
        location_context="Delhi",
    )
    resolved2 = resolve_demographics(req2, current_demographics=existing_demographics)
    assert resolved2 is not None
    assert resolved2.aadhaar_last_four == "1098"
    assert resolved2.location_context == "Bangalore"

    # 3. Valid replacement overwrites existing suffix
    req3 = DemographicsRequest(
        aadhaar_number=SecretStr("111122223333"),
    )
    resolved3 = resolve_demographics(req3, current_demographics=existing_demographics)
    assert resolved3 is not None
    assert resolved3.aadhaar_last_four == "3333"

    # 4. Null request yields None
    assert resolve_demographics(None) is None


def test_demographics_response_only_exposes_suffix() -> None:
    p = Patient(
        patient_id=OpaqueId.new(),
        status=PatientStatus.ACTIVE,
        created_at=NOW,
        updated_at=NOW,
        demographics=PatientDemographics(
            aadhaar_last_four="4321",
            mobile_number="+919876543210",
        ),
    )
    view = patient_view(p)
    assert view.demographics is not None
    assert view.demographics.aadhaar_last_four == "4321"
    # Neither DemographicsResponse nor serialized view contains aadhaar_number
    # or demo_aadhaar_reference.
    dump = view.demographics.model_dump()
    assert "aadhaar_number" not in dump
    assert "demo_aadhaar_reference" not in dump
    assert dump["aadhaar_last_four"] == "4321"
