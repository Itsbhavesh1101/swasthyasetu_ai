"""P5-A typed clinical values and fact supersession tests."""

from dataclasses import FrozenInstanceError
from datetime import UTC, date, datetime, timedelta, timezone
from decimal import Decimal

import pytest

from app.modules.patients.public import (
    AllergyRecord,
    ClinicalFact,
    FactType,
    InvalidFactSupersessionError,
    InvestigationRecord,
    MedicationRecord,
    MedicationStatus,
    Observation,
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
from app.shared.types import OpaqueId

NOW = datetime(2026, 10, 12, 8, tzinfo=UTC)


def _provenance(
    source: ProvenanceSourceType = ProvenanceSourceType.PATIENT_REPORT,
) -> FactProvenance:
    return FactProvenance(source_type=source, created_at=NOW)


def _problem(state: VerificationState) -> Problem:
    return Problem(
        label="Synthetic condition",
        normalized_code=None,
        status=ProblemStatus.ACTIVE,
        onset=date(2026, 1, 1),
        resolution=None,
        verification_state=state,
    )


def _fact(
    state: VerificationState,
    *,
    fact_id: OpaqueId | None = None,
    patient_id: OpaqueId | None = None,
    encounter_id: OpaqueId | None = None,
) -> ClinicalFact:
    return ClinicalFact(
        fact_id=fact_id or OpaqueId.new(),
        patient_id=patient_id,
        encounter_id=encounter_id,
        fact_type=FactType.PROBLEM,
        value=_problem(state),
        normalized_code=None,
        coding_system=None,
        effective_time=None,
        recorded_at=NOW,
        verification_state=state,
        provenance=_provenance(),
        superseded_by_fact_id=None,
    )


def test_fact_problem_and_medication_enum_values_are_canonical() -> None:
    assert {value.value for value in FactType} == {
        "SYMPTOM",
        "PROBLEM",
        "MEDICATION",
        "ALLERGY",
        "PROCEDURE",
        "OBSERVATION",
        "INVESTIGATION",
        "FAMILY_HISTORY",
        "PERSONAL_HISTORY",
        "REVIEW_OF_SYSTEMS",
    }
    assert {value.value for value in ProblemStatus} == {
        "ACTIVE",
        "HISTORICAL",
        "RESOLVED",
        "UNKNOWN",
    }
    assert {value.value for value in MedicationStatus} == {
        "ACTIVE",
        "HISTORICAL",
        "STOPPED",
        "UNKNOWN",
    }


def test_problem_validates_label_temporal_order_and_utc_instants() -> None:
    with pytest.raises(ValueError, match="label"):
        Problem(
            label=" ",
            status=ProblemStatus.UNKNOWN,
            verification_state=VerificationState.EXTRACTED,
        )
    with pytest.raises(ValueError, match="resolution"):
        Problem(
            label="Synthetic condition",
            status=ProblemStatus.RESOLVED,
            onset=date(2026, 2, 1),
            resolution=date(2026, 1, 1),
            verification_state=VerificationState.PATIENT_CONFIRMED,
        )
    offset = timezone(timedelta(hours=5, minutes=30))
    problem = Problem(
        label="Synthetic condition",
        status=ProblemStatus.ACTIVE,
        onset=datetime(2026, 10, 12, 13, 30, tzinfo=offset),
        verification_state=VerificationState.EXTRACTED,
    )
    assert problem.onset == NOW


def test_medication_validates_name_dates_decimal_and_preserves_untrusted_state() -> None:
    medication = MedicationRecord(
        name="Synthetic medicine",
        normalized_code=None,
        dose=Decimal("2.50"),
        dose_unit="mg",
        route="oral",
        frequency="daily",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 2, 1),
        status=MedicationStatus.STOPPED,
        indication="synthetic indication",
        verification_state=VerificationState.NEEDS_CONFIRMATION,
    )
    assert medication.dose == Decimal("2.50")
    assert medication.verification_state is VerificationState.NEEDS_CONFIRMATION

    with pytest.raises(ValueError, match="end_date"):
        MedicationRecord(
            name="Synthetic medicine",
            start_date=date(2026, 2, 1),
            end_date=date(2026, 1, 1),
            status=MedicationStatus.UNKNOWN,
            verification_state=VerificationState.EXTRACTED,
        )
    with pytest.raises(ValueError, match="dose"):
        MedicationRecord(
            name="Synthetic medicine",
            dose=Decimal("NaN"),
            status=MedicationStatus.UNKNOWN,
            verification_state=VerificationState.EXTRACTED,
        )


def test_allergy_uses_extensible_bounded_status_without_inference() -> None:
    allergy = AllergyRecord(
        substance="Synthetic substance",
        normalized_code=None,
        reaction="Synthetic reaction",
        severity="unknown",
        status="ACTIVE_LOCAL_CODE",
        verification_state=VerificationState.PATIENT_CONFIRMED,
    )
    assert allergy.status == "ACTIVE_LOCAL_CODE"

    with pytest.raises(ValueError, match="status"):
        AllergyRecord(
            substance="Synthetic substance",
            status=" ",
            verification_state=VerificationState.EXTRACTED,
        )
    assert not hasattr(allergy, "inferred_from_side_effect")


def test_procedure_normalizes_time_and_hides_notes_from_repr() -> None:
    marker = "synthetic private procedure note"
    offset = timezone(timedelta(hours=5, minutes=30))
    procedure = ProcedureRecord(
        name="Synthetic procedure",
        normalized_code=None,
        performed_at=datetime(2026, 10, 12, 13, 30, tzinfo=offset),
        facility="Synthetic facility",
        notes=marker,
        verification_state=VerificationState.CLINICIAN_CONFIRMED,
    )
    assert procedure.performed_at == NOW
    assert marker not in repr(procedure)


def test_reference_range_and_observation_support_precise_numeric_and_text_values() -> None:
    reference_range = ReferenceRange(
        low=Decimal("3.5"), high=Decimal("5.5"), text="synthetic range"
    )
    numeric = Observation(
        observation_type="synthetic_numeric",
        value=Decimal("4.25"),
        unit="unit",
        reference_range=reference_range,
        effective_at=NOW,
        normalized_value=None,
        normalized_unit=None,
        abnormal_flag="NORMAL",
        verification_state=VerificationState.CLINICIAN_CONFIRMED,
    )
    text = Observation(
        observation_type="synthetic_text",
        value="not detected",
        unit=None,
        reference_range=ReferenceRange(text="not detected"),
        effective_at=None,
        normalized_value=None,
        normalized_unit=None,
        abnormal_flag=None,
        verification_state=VerificationState.EXTRACTED,
    )

    assert numeric.value == Decimal("4.25")
    assert text.value == "not detected"
    with pytest.raises(ValueError, match="low"):
        ReferenceRange(low=Decimal("6"), high=Decimal("5"))
    with pytest.raises(ValueError, match="finite"):
        Observation(
            observation_type="synthetic_numeric",
            value=Decimal("Infinity"),
            verification_state=VerificationState.EXTRACTED,
        )


def test_investigation_uses_extensible_status_and_hides_summary() -> None:
    marker = "synthetic private result summary"
    investigation = InvestigationRecord(
        investigation_type="synthetic_investigation",
        performed_at=NOW,
        result_summary=marker,
        document_id=OpaqueId.new(),
        status="FINAL_LOCAL_CODE",
        verification_state=VerificationState.CLINICIAN_CONFIRMED,
    )
    assert investigation.status == "FINAL_LOCAL_CODE"
    assert marker not in repr(investigation)


@pytest.mark.parametrize(
    ("fact_type", "value"),
    [
        (FactType.PROBLEM, _problem(VerificationState.EXTRACTED)),
        (
            FactType.MEDICATION,
            MedicationRecord(
                name="Synthetic medicine",
                status=MedicationStatus.UNKNOWN,
                verification_state=VerificationState.EXTRACTED,
            ),
        ),
        (
            FactType.ALLERGY,
            AllergyRecord(
                substance="Synthetic substance",
                status="UNKNOWN",
                verification_state=VerificationState.EXTRACTED,
            ),
        ),
        (
            FactType.PROCEDURE,
            ProcedureRecord(
                name="Synthetic procedure",
                verification_state=VerificationState.EXTRACTED,
            ),
        ),
        (
            FactType.OBSERVATION,
            Observation(
                observation_type="synthetic",
                value="present",
                verification_state=VerificationState.EXTRACTED,
            ),
        ),
        (
            FactType.INVESTIGATION,
            InvestigationRecord(
                investigation_type="synthetic",
                status="UNKNOWN",
                verification_state=VerificationState.EXTRACTED,
            ),
        ),
    ],
)
def test_clinical_fact_accepts_each_typed_value(fact_type: FactType, value: object) -> None:
    fact = ClinicalFact(
        fact_id=OpaqueId.new(),
        patient_id=OpaqueId.new(),
        encounter_id=None,
        fact_type=fact_type,
        value=value,  # type: ignore[arg-type]
        recorded_at=NOW,
        verification_state=VerificationState.EXTRACTED,
        provenance=_provenance(ProvenanceSourceType.OCR),
    )

    assert fact.fact_type is fact_type
    assert not isinstance(fact.value, dict)


def test_clinical_fact_requires_matching_value_type_and_verification_state() -> None:
    with pytest.raises(ValueError, match="fact_type"):
        ClinicalFact(
            fact_id=OpaqueId.new(),
            patient_id=None,
            encounter_id=OpaqueId.new(),
            fact_type=FactType.MEDICATION,
            value=_problem(VerificationState.EXTRACTED),
            recorded_at=NOW,
            verification_state=VerificationState.EXTRACTED,
            provenance=_provenance(),
        )
    with pytest.raises(ValueError, match="verification_state"):
        ClinicalFact(
            fact_id=OpaqueId.new(),
            patient_id=None,
            encounter_id=OpaqueId.new(),
            fact_type=FactType.PROBLEM,
            value=_problem(VerificationState.EXTRACTED),
            recorded_at=NOW,
            verification_state=VerificationState.CLINICIAN_CONFIRMED,
            provenance=_provenance(),
        )


def test_machine_derived_fact_remains_explicitly_unconfirmed() -> None:
    fact = ClinicalFact(
        fact_id=OpaqueId.new(),
        patient_id=None,
        encounter_id=OpaqueId.new(),
        fact_type=FactType.MEDICATION,
        value=MedicationRecord(
            name="Synthetic medicine",
            status=MedicationStatus.UNKNOWN,
            verification_state=VerificationState.NEEDS_CONFIRMATION,
        ),
        recorded_at=NOW,
        verification_state=VerificationState.NEEDS_CONFIRMATION,
        provenance=FactProvenance(
            source_type=ProvenanceSourceType.DOCUMENT_AI,
            confidence=Decimal("0.999"),
            created_at=NOW,
        ),
    )
    assert fact.verification_state is VerificationState.NEEDS_CONFIRMATION


def test_clinical_fact_normalizes_times_and_rejects_self_supersession() -> None:
    fact_id = OpaqueId.new()
    offset = timezone(timedelta(hours=5, minutes=30))
    with pytest.raises(ValueError, match="itself"):
        ClinicalFact(
            fact_id=fact_id,
            patient_id=None,
            encounter_id=OpaqueId.new(),
            fact_type=FactType.PROBLEM,
            value=_problem(VerificationState.SUPERSEDED),
            effective_time=None,
            recorded_at=datetime(2026, 10, 12, 13, 30, tzinfo=offset),
            verification_state=VerificationState.SUPERSEDED,
            provenance=_provenance(),
            superseded_by_fact_id=fact_id,
        )


@pytest.mark.parametrize(
    "replacement_state",
    [
        VerificationState.EXTRACTED,
        VerificationState.LOW_CONFIDENCE,
        VerificationState.NEEDS_CONFIRMATION,
        VerificationState.PATIENT_CONFIRMED,
    ],
)
def test_clinician_confirmed_fact_rejects_lower_trust_supersession(
    replacement_state: VerificationState,
) -> None:
    patient_id = OpaqueId.new()
    existing = _fact(VerificationState.CLINICIAN_CONFIRMED, patient_id=patient_id)
    replacement = _fact(replacement_state, patient_id=patient_id)

    with pytest.raises(InvalidFactSupersessionError, match="clinician-confirmed"):
        supersede_fact(existing, replacement)

    assert existing.verification_state is VerificationState.CLINICIAN_CONFIRMED
    assert existing.superseded_by_fact_id is None


@pytest.mark.parametrize(
    ("existing_state", "replacement_state"),
    [
        (VerificationState.EXTRACTED, VerificationState.EXTRACTED),
        (VerificationState.PATIENT_CONFIRMED, VerificationState.EXTRACTED),
        (VerificationState.CLINICIAN_CONFIRMED, VerificationState.CLINICIAN_CONFIRMED),
    ],
)
def test_explicit_allowed_supersession_preserves_historical_fact(
    existing_state: VerificationState, replacement_state: VerificationState
) -> None:
    patient_id = OpaqueId.new()
    existing = _fact(existing_state, patient_id=patient_id)
    replacement = _fact(replacement_state, patient_id=patient_id)

    result = supersede_fact(existing, replacement)

    assert result.superseded.fact_id == existing.fact_id
    assert result.superseded.verification_state is VerificationState.SUPERSEDED
    assert result.superseded.superseded_by_fact_id == replacement.fact_id
    assert isinstance(result.superseded.value, Problem)
    assert isinstance(existing.value, Problem)
    assert result.superseded.value.label == existing.value.label
    assert result.superseded.value.verification_state is VerificationState.SUPERSEDED
    assert result.superseded.provenance == existing.provenance
    assert result.replacement is replacement
    assert existing.verification_state is existing_state
    assert existing.superseded_by_fact_id is None
    with pytest.raises(FrozenInstanceError):
        result.superseded.value = replacement.value  # type: ignore[misc]


def test_supersession_rejects_self_scope_and_type_mismatches() -> None:
    patient_id = OpaqueId.new()
    existing = _fact(VerificationState.EXTRACTED, patient_id=patient_id)

    with pytest.raises(InvalidFactSupersessionError, match="distinct"):
        supersede_fact(
            existing,
            _fact(VerificationState.EXTRACTED, fact_id=existing.fact_id, patient_id=patient_id),
        )
    with pytest.raises(InvalidFactSupersessionError, match="scope"):
        supersede_fact(existing, _fact(VerificationState.EXTRACTED, patient_id=OpaqueId.new()))

    medication = ClinicalFact(
        fact_id=OpaqueId.new(),
        patient_id=patient_id,
        encounter_id=None,
        fact_type=FactType.MEDICATION,
        value=MedicationRecord(
            name="Synthetic medicine",
            status=MedicationStatus.UNKNOWN,
            verification_state=VerificationState.EXTRACTED,
        ),
        recorded_at=NOW,
        verification_state=VerificationState.EXTRACTED,
        provenance=_provenance(),
    )
    with pytest.raises(InvalidFactSupersessionError, match="fact type"):
        supersede_fact(existing, medication)


def test_risk_assessment_is_not_a_clinical_fact_type() -> None:
    assert "RISK_ASSESSMENT" not in {value.value for value in FactType}
