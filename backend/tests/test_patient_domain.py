"""P5-A patient profile and identifier domain tests."""

from dataclasses import FrozenInstanceError
from datetime import UTC, date, datetime, timedelta, timezone

import pytest

from app.modules.patients.public import (
    Patient,
    PatientDemographics,
    PatientIdentifier,
    PatientStatus,
)
from app.shared.types import OpaqueId


def test_patient_status_values_are_canonical() -> None:
    assert {value.value for value in PatientStatus} == {
        "ACTIVE",
        "INACTIVE",
        "MERGED",
        "DELETED_PENDING",
    }


def test_patient_normalizes_timestamps_and_uses_immutable_identifiers() -> None:
    patient_id = OpaqueId.new()
    identifier = PatientIdentifier(
        identifier_id=OpaqueId.new(),
        patient_id=patient_id,
        system="hospital_mrn",
        value="synthetic-identifier",
        use="usual",
        verified=True,
        source="synthetic_his",
    )
    offset = timezone(timedelta(hours=5, minutes=30))
    patient = Patient(
        patient_id=patient_id,
        status=PatientStatus.ACTIVE,
        created_at=datetime(2026, 10, 12, 13, 30, tzinfo=offset),
        updated_at=datetime(2026, 10, 12, 14, 30, tzinfo=offset),
        preferred_language="hi-Latn",
        demographics=None,
        identifiers=(identifier,),
    )

    assert patient.created_at == datetime(2026, 10, 12, 8, tzinfo=UTC)
    assert patient.updated_at == datetime(2026, 10, 12, 9, tzinfo=UTC)
    assert patient.identifiers == (identifier,)
    with pytest.raises(FrozenInstanceError):
        patient.status = PatientStatus.INACTIVE  # type: ignore[misc]


def test_patient_rejects_invalid_timestamps_and_identifier_ownership() -> None:
    patient_id = OpaqueId.new()
    other_identifier = PatientIdentifier(
        identifier_id=OpaqueId.new(),
        patient_id=OpaqueId.new(),
        system="internal",
        value="synthetic-identifier",
        use=None,
        verified=False,
        source="system",
    )
    now = datetime(2026, 10, 12, 8, tzinfo=UTC)

    with pytest.raises(ValueError, match="timezone-aware"):
        Patient(
            patient_id=patient_id,
            status=PatientStatus.ACTIVE,
            created_at=datetime(2026, 10, 12, 8),
            updated_at=now,
        )
    with pytest.raises(ValueError, match="updated_at"):
        Patient(
            patient_id=patient_id,
            status=PatientStatus.ACTIVE,
            created_at=now,
            updated_at=now - timedelta(seconds=1),
        )
    with pytest.raises(ValueError, match="same patient"):
        Patient(
            patient_id=patient_id,
            status=PatientStatus.ACTIVE,
            created_at=now,
            updated_at=now,
            identifiers=(other_identifier,),
        )
    with pytest.raises(TypeError, match="tuple"):
        Patient(
            patient_id=patient_id,
            status=PatientStatus.ACTIVE,
            created_at=now,
            updated_at=now,
            identifiers=[],  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("field", ["system", "value", "source"])
def test_patient_identifier_rejects_empty_required_text(field: str) -> None:
    values = {
        "identifier_id": OpaqueId.new(),
        "patient_id": OpaqueId.new(),
        "system": "internal",
        "value": "synthetic-value",
        "use": None,
        "verified": False,
        "source": "system",
    }
    values[field] = " "

    with pytest.raises(ValueError, match=field):
        PatientIdentifier(**values)  # type: ignore[arg-type]


def test_patient_identifier_retains_verified_and_redacts_value_from_repr() -> None:
    marker = "synthetic-sensitive-identifier"
    identifier = PatientIdentifier(
        identifier_id=OpaqueId.new(),
        patient_id=OpaqueId.new(),
        system="abha",
        value=marker,
        use=None,
        verified=True,
        source="patient_report",
    )

    assert identifier.verified is True
    assert identifier.value == marker
    assert marker not in repr(identifier)


def test_patient_identifier_requires_explicit_verification_and_source() -> None:
    with pytest.raises(TypeError):
        PatientIdentifier(  # type: ignore[call-arg]
            identifier_id=OpaqueId.new(),
            patient_id=OpaqueId.new(),
            system="internal",
            value="synthetic-value",
        )


def test_demographics_all_optional_and_pregnancy_is_independent() -> None:
    empty = PatientDemographics()
    demographics = PatientDemographics(
        date_of_birth=date(1995, 4, 8),
        age_years=31,
        administrative_sex="male",
        gender_identity=None,
        pregnancy_status="pregnant",
        location_context="synthetic-region",
    )

    assert empty.date_of_birth is None
    assert demographics.administrative_sex == "male"
    assert demographics.pregnancy_status == "pregnant"


def test_demographics_rejects_negative_age_datetime_and_bad_optional_text() -> None:
    with pytest.raises(ValueError, match="age_years"):
        PatientDemographics(age_years=-1)
    with pytest.raises(TypeError, match="date_of_birth"):
        PatientDemographics(date_of_birth=datetime(1995, 4, 8, tzinfo=UTC))
    with pytest.raises(ValueError, match="gender_identity"):
        PatientDemographics(gender_identity=" ")
