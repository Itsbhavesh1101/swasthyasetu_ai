"""P5-B typed persistence mapping and privacy tests."""

from datetime import UTC, date, datetime
from decimal import Decimal

import pytest

from app.modules.patients.persistence import (
    StructuredValueError,
    canonical_label,
    deserialize_clinical_value,
    serialize_clinical_value,
)
from app.modules.patients.public import (
    AllergyRecord,
    FactType,
    InvestigationRecord,
    MedicationRecord,
    MedicationStatus,
    Observation,
    Problem,
    ProblemStatus,
    ProcedureRecord,
    ReferenceRange,
)
from app.modules.provenance.public import VerificationState
from app.shared.types import OpaqueId

NOW = datetime(2026, 10, 12, 8, tzinfo=UTC)
STATE = VerificationState.NEEDS_CONFIRMATION


@pytest.mark.parametrize(
    ("fact_type", "value", "label"),
    [
        (
            FactType.PROBLEM,
            Problem(
                label="Synthetic problem",
                normalized_code="problem-code",
                status=ProblemStatus.ACTIVE,
                onset=date(2026, 1, 1),
                resolution=None,
                verification_state=STATE,
            ),
            "Synthetic problem",
        ),
        (
            FactType.MEDICATION,
            MedicationRecord(
                name="Synthetic medication",
                normalized_code="med-code",
                dose=Decimal("2.50"),
                dose_unit="mg",
                route="oral",
                frequency="daily",
                start_date=date(2026, 1, 1),
                end_date=date(2026, 2, 1),
                status=MedicationStatus.STOPPED,
                indication="Synthetic indication",
                verification_state=STATE,
            ),
            "Synthetic medication",
        ),
        (
            FactType.ALLERGY,
            AllergyRecord(
                substance="Synthetic substance",
                normalized_code="allergy-code",
                reaction="Synthetic reaction",
                severity="unknown",
                status="ACTIVE_LOCAL_CODE",
                verification_state=STATE,
            ),
            "Synthetic substance",
        ),
        (
            FactType.PROCEDURE,
            ProcedureRecord(
                name="Synthetic procedure",
                normalized_code="procedure-code",
                performed_at=NOW,
                facility="Synthetic facility",
                notes="Synthetic private note",
                verification_state=STATE,
            ),
            "Synthetic procedure",
        ),
        (
            FactType.OBSERVATION,
            Observation(
                observation_type="synthetic-observation",
                value=Decimal("4.25"),
                unit="unit",
                reference_range=ReferenceRange(
                    low=Decimal("3.5"), high=Decimal("5.5"), text="synthetic range"
                ),
                effective_at=NOW,
                normalized_value=Decimal("4.25"),
                normalized_unit="unit",
                abnormal_flag="NORMAL",
                verification_state=STATE,
            ),
            "synthetic-observation",
        ),
        (
            FactType.INVESTIGATION,
            InvestigationRecord(
                investigation_type="synthetic-investigation",
                performed_at=NOW,
                result_summary="Synthetic private result",
                document_id=OpaqueId.new(),
                status="FINAL_LOCAL_CODE",
                verification_state=STATE,
            ),
            "synthetic-investigation",
        ),
    ],
)
def test_typed_clinical_values_round_trip_with_versioned_shape(
    fact_type: FactType, value: object, label: str
) -> None:
    payload = serialize_clinical_value(fact_type, value)  # type: ignore[arg-type]

    assert payload["schema_version"] == "p5b-v1"
    assert set(payload) == {"schema_version", "value"}
    assert canonical_label(value) == label  # type: ignore[arg-type]
    assert deserialize_clinical_value(fact_type, payload) == value


@pytest.mark.parametrize(
    "payload",
    [
        {"schema_version": "unknown", "value": {}},
        {"schema_version": "p5b-v1", "value": {}, "extra": True},
        {"schema_version": "p5b-v1", "value": {"unknown": "field"}},
        {"schema_version": "p5b-v1", "value": "not-an-object"},
    ],
)
def test_deserializer_rejects_unsupported_or_malformed_shapes(
    payload: dict[str, object],
) -> None:
    with pytest.raises(StructuredValueError):
        deserialize_clinical_value(FactType.PROBLEM, payload)


def test_future_fact_types_have_no_untyped_persistence_fallback() -> None:
    with pytest.raises(StructuredValueError, match="supported typed value"):
        deserialize_clinical_value(
            FactType.SYMPTOM,
            {"schema_version": "p5b-v1", "value": {"text": "synthetic"}},
        )


def test_clinical_mapping_errors_do_not_echo_sensitive_payload() -> None:
    marker = "synthetic-sensitive-clinical-marker"
    with pytest.raises(StructuredValueError) as raised:
        deserialize_clinical_value(
            FactType.MEDICATION,
            {"schema_version": "p5b-v1", "value": {"name": marker}},
        )

    assert marker not in str(raised.value)
