"""P5-A patient profile and identifier domain tests."""

from dataclasses import FrozenInstanceError
from datetime import UTC, date, datetime, timedelta, timezone
from decimal import Decimal

import pytest

from app.modules.patients.public import (
    BloodGroup,
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


def test_demographics_validates_measurements_and_derives_bmi() -> None:
    demographics = PatientDemographics(height_cm=Decimal("165"), weight_kg=Decimal("60"))
    assert demographics.bmi == Decimal("22.0")
    assert PatientDemographics(height_cm=Decimal("165")).bmi is None
    with pytest.raises(ValueError, match="height_cm"):
        PatientDemographics(height_cm=Decimal("29.9"))
    with pytest.raises(ValueError, match="weight_kg"):
        PatientDemographics(weight_kg=Decimal("700.1"))


def test_demographics_accepts_closed_blood_groups_and_synthetic_contact_details() -> None:
    assert {value.value for value in BloodGroup} == {
        "A+",
        "A-",
        "B+",
        "B-",
        "AB+",
        "AB-",
        "O+",
        "O-",
        "UNKNOWN",
    }
    minimum = PatientDemographics(
        mobile_number="+1234567",
        blood_group=BloodGroup.UNKNOWN,
        demo_aadhaar_reference="DEMO-AADHAAR-0001",
    )
    maximum = PatientDemographics(
        mobile_number="+123456789012345",
        blood_group=BloodGroup.AB_POSITIVE,
        demo_aadhaar_reference="DEMO-AADHAAR-9999",
    )

    assert minimum.mobile_number == "+1234567"
    assert minimum.blood_group is BloodGroup.UNKNOWN
    assert maximum.mobile_number == "+123456789012345"
    assert maximum.blood_group is BloodGroup.AB_POSITIVE


@pytest.mark.parametrize(
    "mobile_number",
    [
        "1234567890",
        "+123456",
        "+1234567890123456",
        "+01234567",
        "+12 34567",
        "+12-34567",
        " +1234567",
        "+1234567 ",
        "+१२३४५६७",
    ],
)
def test_demographics_rejects_non_e164_mobile_numbers(mobile_number: str) -> None:
    with pytest.raises(ValueError, match="mobile_number"):
        PatientDemographics(mobile_number=mobile_number)


def test_demographics_rejects_arbitrary_blood_group() -> None:
    with pytest.raises((TypeError, ValueError), match="blood_group"):
        PatientDemographics(blood_group="A positive")  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "reference",
    [
        "123456789012",
        "DEMO-AADHAAR-123",
        "DEMO-AADHAAR-12345",
        "demo-aadhaar-1234",
        "DEMO-AADHAAR-१२३४",
        " DEMO-AADHAAR-1234",
        "DEMO-AADHAAR-1234 ",
    ],
)
def test_demographics_rejects_real_or_malformed_aadhaar_values(reference: str) -> None:
    with pytest.raises(ValueError, match="demo_aadhaar_reference"):
        PatientDemographics(demo_aadhaar_reference=reference)
