"""Explicit versioned mapping between typed clinical values and JSONB shapes."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import cast
from uuid import UUID

from app.modules.patients.public import (
    AllergyRecord,
    ClinicalTime,
    ClinicalValue,
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

STRUCTURED_VALUE_SCHEMA_VERSION = "p5b-v1"


class StructuredValueError(ValueError):
    """Raised without echoing clinical content when a persistence shape is invalid."""


def _fail(message: str = "clinical structured value is invalid") -> StructuredValueError:
    return StructuredValueError(message)


def _object(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise _fail()
    return cast(dict[str, object], value)


def _strict(value: object, fields: frozenset[str]) -> dict[str, object]:
    mapped = _object(value)
    if set(mapped) != fields:
        raise _fail()
    return mapped


def _optional_string(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise _fail()
    return value


def _required_string(value: object) -> str:
    result = _optional_string(value)
    if result is None:
        raise _fail()
    return result


def _optional_decimal(value: object) -> Decimal | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise _fail()
    try:
        return Decimal(value)
    except InvalidOperation as exc:
        raise _fail() from exc


def _optional_date(value: object) -> date | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise _fail()
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise _fail() from exc


def _optional_datetime(value: object) -> datetime | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise _fail()
    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise _fail() from exc


def _clinical_time_to_json(value: ClinicalTime | None) -> dict[str, str] | None:
    if value is None:
        return None
    if type(value) is date:
        return {"kind": "date", "value": value.isoformat()}
    return {"kind": "datetime", "value": value.isoformat()}


def _clinical_time_from_json(value: object) -> ClinicalTime | None:
    if value is None:
        return None
    mapped = _strict(value, frozenset({"kind", "value"}))
    kind = _required_string(mapped["kind"])
    raw = _required_string(mapped["value"])
    try:
        if kind == "date":
            return date.fromisoformat(raw)
        if kind == "datetime":
            return datetime.fromisoformat(raw)
    except ValueError as exc:
        raise _fail() from exc
    raise _fail()


def _state(value: object) -> VerificationState:
    try:
        return VerificationState(_required_string(value))
    except ValueError as exc:
        raise _fail() from exc


def canonical_label(value: ClinicalValue) -> str:
    """Derive the required database label from authoritative typed data."""
    if isinstance(value, Problem):
        return value.label
    if isinstance(value, MedicationRecord):
        return value.name
    if isinstance(value, AllergyRecord):
        return value.substance
    if isinstance(value, ProcedureRecord):
        return value.name
    if isinstance(value, Observation):
        return value.observation_type
    if isinstance(value, InvestigationRecord):
        return value.investigation_type
    raise _fail("clinical value has no supported canonical label")


def serialize_clinical_value(fact_type: FactType, value: ClinicalValue) -> dict[str, object]:
    """Serialize one supported typed value without accepting arbitrary mappings."""
    expected = {
        Problem: FactType.PROBLEM,
        MedicationRecord: FactType.MEDICATION,
        AllergyRecord: FactType.ALLERGY,
        ProcedureRecord: FactType.PROCEDURE,
        Observation: FactType.OBSERVATION,
        InvestigationRecord: FactType.INVESTIGATION,
    }
    if expected.get(type(value)) is not fact_type:
        raise _fail("fact type has no matching supported typed value")
    if isinstance(value, Problem):
        body: dict[str, object] = {
            "label": value.label,
            "normalized_code": value.normalized_code,
            "status": value.status.value,
            "onset": _clinical_time_to_json(value.onset),
            "resolution": _clinical_time_to_json(value.resolution),
            "verification_state": value.verification_state.value,
        }
    elif isinstance(value, MedicationRecord):
        body = {
            "name": value.name,
            "normalized_code": value.normalized_code,
            "dose": None if value.dose is None else str(value.dose),
            "dose_unit": value.dose_unit,
            "route": value.route,
            "frequency": value.frequency,
            "start_date": None if value.start_date is None else value.start_date.isoformat(),
            "end_date": None if value.end_date is None else value.end_date.isoformat(),
            "status": value.status.value,
            "indication": value.indication,
            "verification_state": value.verification_state.value,
        }
    elif isinstance(value, AllergyRecord):
        body = {
            "substance": value.substance,
            "normalized_code": value.normalized_code,
            "reaction": value.reaction,
            "severity": value.severity,
            "status": value.status,
            "verification_state": value.verification_state.value,
        }
    elif isinstance(value, ProcedureRecord):
        body = {
            "name": value.name,
            "normalized_code": value.normalized_code,
            "performed_at": (
                None if value.performed_at is None else value.performed_at.isoformat()
            ),
            "facility": value.facility,
            "notes": value.notes,
            "verification_state": value.verification_state.value,
        }
    elif isinstance(value, Observation):
        reference = None
        if value.reference_range is not None:
            reference = {
                "low": None
                if value.reference_range.low is None
                else str(value.reference_range.low),
                "high": (
                    None if value.reference_range.high is None else str(value.reference_range.high)
                ),
                "text": value.reference_range.text,
            }
        body = {
            "observation_type": value.observation_type,
            "value_type": "decimal" if isinstance(value.value, Decimal) else "text",
            "value": str(value.value),
            "unit": value.unit,
            "reference_range": reference,
            "effective_at": None if value.effective_at is None else value.effective_at.isoformat(),
            "normalized_value": (
                None if value.normalized_value is None else str(value.normalized_value)
            ),
            "normalized_unit": value.normalized_unit,
            "abnormal_flag": value.abnormal_flag,
            "verification_state": value.verification_state.value,
        }
    elif isinstance(value, InvestigationRecord):
        body = {
            "investigation_type": value.investigation_type,
            "performed_at": None if value.performed_at is None else value.performed_at.isoformat(),
            "result_summary": value.result_summary,
            "document_id": None if value.document_id is None else str(value.document_id),
            "status": value.status,
            "verification_state": value.verification_state.value,
        }
    else:
        raise _fail("fact type has no matching supported typed value")
    return {"schema_version": STRUCTURED_VALUE_SCHEMA_VERSION, "value": body}


def deserialize_clinical_value(fact_type: FactType, payload: object) -> ClinicalValue:
    """Reconstruct a typed value from a strict versioned persistence shape."""
    root = _strict(payload, frozenset({"schema_version", "value"}))
    if root["schema_version"] != STRUCTURED_VALUE_SCHEMA_VERSION:
        raise _fail("clinical structured-value schema version is unsupported")
    value = root["value"]
    try:
        if fact_type is FactType.PROBLEM:
            item = _strict(
                value,
                frozenset(
                    {
                        "label",
                        "normalized_code",
                        "status",
                        "onset",
                        "resolution",
                        "verification_state",
                    }
                ),
            )
            return Problem(
                label=_required_string(item["label"]),
                normalized_code=_optional_string(item["normalized_code"]),
                status=ProblemStatus(_required_string(item["status"])),
                onset=_clinical_time_from_json(item["onset"]),
                resolution=_clinical_time_from_json(item["resolution"]),
                verification_state=_state(item["verification_state"]),
            )
        if fact_type is FactType.MEDICATION:
            item = _strict(
                value,
                frozenset(
                    {
                        "name",
                        "normalized_code",
                        "dose",
                        "dose_unit",
                        "route",
                        "frequency",
                        "start_date",
                        "end_date",
                        "status",
                        "indication",
                        "verification_state",
                    }
                ),
            )
            return MedicationRecord(
                name=_required_string(item["name"]),
                normalized_code=_optional_string(item["normalized_code"]),
                dose=_optional_decimal(item["dose"]),
                dose_unit=_optional_string(item["dose_unit"]),
                route=_optional_string(item["route"]),
                frequency=_optional_string(item["frequency"]),
                start_date=_optional_date(item["start_date"]),
                end_date=_optional_date(item["end_date"]),
                status=MedicationStatus(_required_string(item["status"])),
                indication=_optional_string(item["indication"]),
                verification_state=_state(item["verification_state"]),
            )
        if fact_type is FactType.ALLERGY:
            item = _strict(
                value,
                frozenset(
                    {
                        "substance",
                        "normalized_code",
                        "reaction",
                        "severity",
                        "status",
                        "verification_state",
                    }
                ),
            )
            return AllergyRecord(
                substance=_required_string(item["substance"]),
                normalized_code=_optional_string(item["normalized_code"]),
                reaction=_optional_string(item["reaction"]),
                severity=_optional_string(item["severity"]),
                status=_required_string(item["status"]),
                verification_state=_state(item["verification_state"]),
            )
        if fact_type is FactType.PROCEDURE:
            item = _strict(
                value,
                frozenset(
                    {
                        "name",
                        "normalized_code",
                        "performed_at",
                        "facility",
                        "notes",
                        "verification_state",
                    }
                ),
            )
            return ProcedureRecord(
                name=_required_string(item["name"]),
                normalized_code=_optional_string(item["normalized_code"]),
                performed_at=_optional_datetime(item["performed_at"]),
                facility=_optional_string(item["facility"]),
                notes=_optional_string(item["notes"]),
                verification_state=_state(item["verification_state"]),
            )
        if fact_type is FactType.OBSERVATION:
            item = _strict(
                value,
                frozenset(
                    {
                        "observation_type",
                        "value_type",
                        "value",
                        "unit",
                        "reference_range",
                        "effective_at",
                        "normalized_value",
                        "normalized_unit",
                        "abnormal_flag",
                        "verification_state",
                    }
                ),
            )
            raw_value = _required_string(item["value"])
            value_type = _required_string(item["value_type"])
            if value_type == "decimal":
                observed: Decimal | str = Decimal(raw_value)
            elif value_type == "text":
                observed = raw_value
            else:
                raise _fail()
            raw_reference = item["reference_range"]
            reference = None
            if raw_reference is not None:
                mapped_reference = _strict(raw_reference, frozenset({"low", "high", "text"}))
                reference = ReferenceRange(
                    low=_optional_decimal(mapped_reference["low"]),
                    high=_optional_decimal(mapped_reference["high"]),
                    text=_optional_string(mapped_reference["text"]),
                )
            return Observation(
                observation_type=_required_string(item["observation_type"]),
                value=observed,
                unit=_optional_string(item["unit"]),
                reference_range=reference,
                effective_at=_optional_datetime(item["effective_at"]),
                normalized_value=_optional_decimal(item["normalized_value"]),
                normalized_unit=_optional_string(item["normalized_unit"]),
                abnormal_flag=_optional_string(item["abnormal_flag"]),
                verification_state=_state(item["verification_state"]),
            )
        if fact_type is FactType.INVESTIGATION:
            item = _strict(
                value,
                frozenset(
                    {
                        "investigation_type",
                        "performed_at",
                        "result_summary",
                        "document_id",
                        "status",
                        "verification_state",
                    }
                ),
            )
            raw_document_id = _optional_string(item["document_id"])
            return InvestigationRecord(
                investigation_type=_required_string(item["investigation_type"]),
                performed_at=_optional_datetime(item["performed_at"]),
                result_summary=_optional_string(item["result_summary"]),
                document_id=(None if raw_document_id is None else OpaqueId(UUID(raw_document_id))),
                status=_required_string(item["status"]),
                verification_state=_state(item["verification_state"]),
            )
    except (InvalidOperation, TypeError, ValueError) as exc:
        if isinstance(exc, StructuredValueError):
            raise
        raise _fail() from exc
    raise _fail("fact type has no supported typed value")
