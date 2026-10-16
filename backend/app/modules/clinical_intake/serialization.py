"""Strict versioned serializers for clinical-intake JSONB projections."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import NoReturn, cast

from app.modules.clinical_intake.contracts import (
    AnswerReference,
    AnswerType,
    IntakeAnswer,
    IntakeAnswerSourceType,
    QuestionnaireResponses,
    ResponseDisposition,
    SkippedQuestionReference,
)
from app.modules.clinical_intake.domain import (
    ChiefComplaint,
    ConfirmationState,
    Contradiction,
    ContradictionStatus,
    DurationValue,
    HistoryOfPresentIllness,
    HistoryReference,
    HistorySections,
    HistorySourceKind,
    MissingInformation,
    MissingReason,
    PriorInvestigation,
    ResolutionState,
    ReviewOfSystemsEntry,
    ReviewOfSystemsState,
    SeverityValue,
    SourceReference,
    StructuredValue,
)
from app.shared.types import OpaqueId

JsonObject = dict[str, object]
_ERROR = "clinical intake persistence shape is invalid"


def _invalid() -> NoReturn:
    raise ValueError(_ERROR)


def _object(value: object, keys: set[str]) -> JsonObject:
    if (
        not isinstance(value, dict)
        or set(value) != keys
        or any(not isinstance(key, str) for key in value)
    ):
        _invalid()
    return cast(JsonObject, value)


def _string(value: object) -> str:
    if not isinstance(value, str):
        _invalid()
    return value


def _optional_string(value: object) -> str | None:
    if value is None:
        return None
    return _string(value)


def _id(value: object) -> OpaqueId:
    try:
        return OpaqueId.parse(_string(value))
    except (ValueError, TypeError):
        _invalid()


def _optional_id(value: object) -> OpaqueId | None:
    return None if value is None else _id(value)


def _decimal(value: object) -> Decimal:
    if not isinstance(value, str):
        _invalid()
    try:
        result = Decimal(value)
    except InvalidOperation:
        _invalid()
    if not result.is_finite():
        _invalid()
    return result


def _datetime(value: object) -> datetime:
    try:
        result = datetime.fromisoformat(_string(value))
    except ValueError:
        _invalid()
    if result.tzinfo is None or result.utcoffset() is None:
        _invalid()
    return result


def _list(value: object) -> list[object]:
    if not isinstance(value, list):
        _invalid()
    return value


def _enum(enum_type: type[object], value: object) -> object:
    try:
        return enum_type(_string(value))  # type: ignore[call-arg]
    except ValueError:
        _invalid()


def serialize_chief_complaint(value: ChiefComplaint) -> JsonObject:
    return {
        "schema_version": "chief-complaint.v1",
        "patient_wording": value.patient_wording,
        "display_key": value.display_key,
        "normalized_code": value.normalized_code,
        "coding_system": value.coding_system,
        "source_answer_id": str(value.source_answer_id),
    }


def deserialize_chief_complaint(value: object) -> ChiefComplaint:
    try:
        data = _object(
            value,
            {
                "schema_version",
                "patient_wording",
                "display_key",
                "normalized_code",
                "coding_system",
                "source_answer_id",
            },
        )
        if data["schema_version"] != "chief-complaint.v1":
            _invalid()
        return ChiefComplaint(
            patient_wording=_string(data["patient_wording"]),
            display_key=_string(data["display_key"]),
            normalized_code=_optional_string(data["normalized_code"]),
            coding_system=_optional_string(data["coding_system"]),
            source_answer_id=_id(data["source_answer_id"]),
        )
    except (KeyError, TypeError, ValueError):
        _invalid()


def _structured_to_json(value: StructuredValue | None) -> object:
    if value is None:
        return None
    return {"value": value.value, "source_answer_id": str(value.source_answer_id)}


def _structured_from_json(value: object) -> StructuredValue | None:
    if value is None:
        return None
    data = _object(value, {"value", "source_answer_id"})
    return StructuredValue(
        value=_string(data["value"]), source_answer_id=_id(data["source_answer_id"])
    )


def serialize_hpi(value: HistoryOfPresentIllness) -> JsonObject:
    return {
        "schema_version": "hpi.v1",
        "onset": _structured_to_json(value.onset),
        "duration": None
        if value.duration is None
        else {
            "value": str(value.duration.value),
            "unit": value.duration.unit,
            "source_answer_id": str(value.duration.source_answer_id),
        },
        "location": _structured_to_json(value.location),
        "character": _structured_to_json(value.character),
        "severity": None
        if value.severity is None
        else {
            "scale_id": value.severity.scale_id,
            "scale_version": value.severity.scale_version,
            "value": str(value.severity.value),
            "source_answer_id": str(value.severity.source_answer_id),
        },
        "progression": _structured_to_json(value.progression),
        "associated_symptoms": [_structured_to_json(item) for item in value.associated_symptoms],
        "aggravating_factors": [_structured_to_json(item) for item in value.aggravating_factors],
        "relieving_factors": [_structured_to_json(item) for item in value.relieving_factors],
    }


def deserialize_hpi(value: object) -> HistoryOfPresentIllness:
    try:
        keys = {
            "schema_version",
            "onset",
            "duration",
            "location",
            "character",
            "severity",
            "progression",
            "associated_symptoms",
            "aggravating_factors",
            "relieving_factors",
        }
        data = _object(value, keys)
        if data["schema_version"] != "hpi.v1":
            _invalid()
        duration_data = (
            None
            if data["duration"] is None
            else _object(data["duration"], {"value", "unit", "source_answer_id"})
        )
        severity_data = (
            None
            if data["severity"] is None
            else _object(
                data["severity"], {"scale_id", "scale_version", "value", "source_answer_id"}
            )
        )
        structured_lists = {}
        for name in ("associated_symptoms", "aggravating_factors", "relieving_factors"):
            items = tuple(_structured_from_json(item) for item in _list(data[name]))
            if any(item is None for item in items):
                _invalid()
            structured_lists[name] = cast(tuple[StructuredValue, ...], items)
        return HistoryOfPresentIllness(
            onset=_structured_from_json(data["onset"]),
            duration=None
            if duration_data is None
            else DurationValue(
                value=_decimal(duration_data["value"]),
                unit=_string(duration_data["unit"]),
                source_answer_id=_id(duration_data["source_answer_id"]),
            ),
            location=_structured_from_json(data["location"]),
            character=_structured_from_json(data["character"]),
            severity=None
            if severity_data is None
            else SeverityValue(
                scale_id=_string(severity_data["scale_id"]),
                scale_version=_string(severity_data["scale_version"]),
                value=_decimal(severity_data["value"]),
                source_answer_id=_id(severity_data["source_answer_id"]),
            ),
            progression=_structured_from_json(data["progression"]),
            **structured_lists,
        )
    except (KeyError, TypeError, ValueError):
        _invalid()


def _source_to_json(value: SourceReference) -> JsonObject:
    return {
        "answer_id": None if value.answer_id is None else str(value.answer_id),
        "fact_id": None if value.fact_id is None else str(value.fact_id),
        "verification_state": value.verification_state,
    }


def _source_from_json(value: object) -> SourceReference:
    data = _object(value, {"answer_id", "fact_id", "verification_state"})
    return SourceReference(
        answer_id=_optional_id(data["answer_id"]),
        fact_id=_optional_id(data["fact_id"]),
        verification_state=_optional_string(data["verification_state"]),
    )


def _history_to_json(value: HistoryReference) -> JsonObject:
    return {
        "entry_id": str(value.entry_id),
        "display_value": value.display_value,
        "source_kind": value.source_kind.value,
        "source_answer_id": None if value.source_answer_id is None else str(value.source_answer_id),
        "source_fact_id": None if value.source_fact_id is None else str(value.source_fact_id),
        "verification_state": value.verification_state,
        "confirmation_state": value.confirmation_state.value,
    }


def _history_from_json(value: object) -> HistoryReference:
    data = _object(
        value,
        {
            "entry_id",
            "display_value",
            "source_kind",
            "source_answer_id",
            "source_fact_id",
            "verification_state",
            "confirmation_state",
        },
    )
    return HistoryReference(
        entry_id=_id(data["entry_id"]),
        display_value=_string(data["display_value"]),
        source_kind=cast(HistorySourceKind, _enum(HistorySourceKind, data["source_kind"])),
        source_answer_id=_optional_id(data["source_answer_id"]),
        source_fact_id=_optional_id(data["source_fact_id"]),
        verification_state=_optional_string(data["verification_state"]),
        confirmation_state=cast(
            ConfirmationState, _enum(ConfirmationState, data["confirmation_state"])
        ),
    )


def serialize_history_sections(value: HistorySections) -> JsonObject:
    regular = {
        name: [_history_to_json(item) for item in getattr(value, name)]
        for name in (
            "past_medical",
            "past_surgical",
            "medications",
            "allergies",
            "family",
            "personal",
        )
    }
    return {
        "schema_version": "history-sections.v1",
        **regular,
        "review_of_systems": [
            {
                "entry_id": str(item.entry_id),
                "system_key": item.system_key,
                "finding_key": item.finding_key,
                "patient_wording": item.patient_wording,
                "state": item.state.value,
                "source": _source_to_json(item.source),
            }
            for item in value.review_of_systems
        ],
        "prior_investigations": [
            {
                "entry_id": str(item.entry_id),
                "investigation_type": item.investigation_type,
                "performed_at": None
                if item.performed_at is None
                else item.performed_at.isoformat(),
                "result_summary": item.result_summary,
                "document_reference": item.document_reference,
                "source": _source_to_json(item.source),
                "verification_state": item.verification_state,
            }
            for item in value.prior_investigations
        ],
    }


def deserialize_history_sections(value: object) -> HistorySections:
    try:
        regular_names = (
            "past_medical",
            "past_surgical",
            "medications",
            "allergies",
            "family",
            "personal",
        )
        keys = {"schema_version", *regular_names, "review_of_systems", "prior_investigations"}
        data = _object(value, keys)
        if data["schema_version"] != "history-sections.v1":
            _invalid()
        regular = {
            name: tuple(_history_from_json(item) for item in _list(data[name]))
            for name in regular_names
        }
        ros = []
        for raw in _list(data["review_of_systems"]):
            item = _object(
                raw, {"entry_id", "system_key", "finding_key", "patient_wording", "state", "source"}
            )
            ros.append(
                ReviewOfSystemsEntry(
                    entry_id=_id(item["entry_id"]),
                    system_key=_string(item["system_key"]),
                    finding_key=_optional_string(item["finding_key"]),
                    patient_wording=_optional_string(item["patient_wording"]),
                    state=cast(ReviewOfSystemsState, _enum(ReviewOfSystemsState, item["state"])),
                    source=_source_from_json(item["source"]),
                )
            )
        investigations = []
        for raw in _list(data["prior_investigations"]):
            item = _object(
                raw,
                {
                    "entry_id",
                    "investigation_type",
                    "performed_at",
                    "result_summary",
                    "document_reference",
                    "source",
                    "verification_state",
                },
            )
            investigations.append(
                PriorInvestigation(
                    entry_id=_id(item["entry_id"]),
                    investigation_type=_string(item["investigation_type"]),
                    performed_at=None
                    if item["performed_at"] is None
                    else _datetime(item["performed_at"]),
                    result_summary=_optional_string(item["result_summary"]),
                    document_reference=_optional_string(item["document_reference"]),
                    source=_source_from_json(item["source"]),
                    verification_state=_string(item["verification_state"]),
                )
            )
        return HistorySections(
            **regular, review_of_systems=tuple(ros), prior_investigations=tuple(investigations)
        )
    except (KeyError, TypeError, ValueError):
        _invalid()


def serialize_missing_information(values: tuple[MissingInformation, ...]) -> list[object]:
    return [
        {
            "schema_version": "missing-information.v1",
            "missing_id": str(item.missing_id),
            "field_or_question_key": item.field_or_question_key,
            "reason_code": item.reason_code.value,
            "requiredness": str(item.requiredness),
            "source_pack_id": item.source_pack_id,
            "source_pack_version": item.source_pack_version,
            "source_rule_id": item.source_rule_id,
            "resolution_state": item.resolution_state.value,
            "resolution_answer_id": None
            if item.resolution_answer_id is None
            else str(item.resolution_answer_id),
        }
        for item in values
    ]


def deserialize_missing_information(value: object) -> tuple[MissingInformation, ...]:
    from app.modules.clinical_intake.domain import Requiredness

    try:
        result = []
        for raw in _list(value):
            item = _object(
                raw,
                {
                    "schema_version",
                    "missing_id",
                    "field_or_question_key",
                    "reason_code",
                    "requiredness",
                    "source_pack_id",
                    "source_pack_version",
                    "source_rule_id",
                    "resolution_state",
                    "resolution_answer_id",
                },
            )
            if item["schema_version"] != "missing-information.v1":
                _invalid()
            result.append(
                MissingInformation(
                    missing_id=_id(item["missing_id"]),
                    field_or_question_key=_string(item["field_or_question_key"]),
                    reason_code=cast(MissingReason, _enum(MissingReason, item["reason_code"])),
                    requiredness=cast(Requiredness, _enum(Requiredness, item["requiredness"])),
                    source_pack_id=_string(item["source_pack_id"]),
                    source_pack_version=_string(item["source_pack_version"]),
                    source_rule_id=_string(item["source_rule_id"]),
                    resolution_state=cast(
                        ResolutionState, _enum(ResolutionState, item["resolution_state"])
                    ),
                    resolution_answer_id=_optional_id(item["resolution_answer_id"]),
                )
            )
        return tuple(result)
    except (KeyError, TypeError, ValueError):
        _invalid()


def serialize_contradictions(values: tuple[Contradiction, ...]) -> list[object]:
    return [
        {
            "schema_version": "contradiction.v1",
            "contradiction_id": str(item.contradiction_id),
            "field_key": item.field_key,
            "left_ref": _source_to_json(item.left_ref),
            "right_ref": _source_to_json(item.right_ref),
            "source_pack_id": item.source_pack_id,
            "source_rule_id": item.source_rule_id,
            "status": item.status.value,
            "resolution_ref": None if item.resolution_ref is None else str(item.resolution_ref),
            "created_at": item.created_at.isoformat(),
            "resolved_at": None if item.resolved_at is None else item.resolved_at.isoformat(),
        }
        for item in values
    ]


def deserialize_contradictions(value: object) -> tuple[Contradiction, ...]:
    try:
        result = []
        for raw in _list(value):
            item = _object(
                raw,
                {
                    "schema_version",
                    "contradiction_id",
                    "field_key",
                    "left_ref",
                    "right_ref",
                    "source_pack_id",
                    "source_rule_id",
                    "status",
                    "resolution_ref",
                    "created_at",
                    "resolved_at",
                },
            )
            if item["schema_version"] != "contradiction.v1":
                _invalid()
            result.append(
                Contradiction(
                    contradiction_id=_id(item["contradiction_id"]),
                    field_key=_string(item["field_key"]),
                    left_ref=_source_from_json(item["left_ref"]),
                    right_ref=_source_from_json(item["right_ref"]),
                    source_pack_id=_string(item["source_pack_id"]),
                    source_rule_id=_string(item["source_rule_id"]),
                    status=cast(ContradictionStatus, _enum(ContradictionStatus, item["status"])),
                    resolution_ref=_optional_id(item["resolution_ref"]),
                    created_at=_datetime(item["created_at"]),
                    resolved_at=None
                    if item["resolved_at"] is None
                    else _datetime(item["resolved_at"]),
                )
            )
        return tuple(result)
    except (KeyError, TypeError, ValueError):
        _invalid()


def serialize_answer(value: IntakeAnswer) -> JsonObject:
    if isinstance(value.value, Decimal):
        encoded: object = str(value.value)
    elif isinstance(value.value, date):
        encoded = value.value.isoformat()
    else:
        encoded = value.value
    return {
        "schema_version": "intake-answer.v1",
        "answer_type": value.answer_type.value,
        "value": encoded,
        "selected_option_ids": None
        if value.selected_option_ids is None
        else list(value.selected_option_ids),
        "unit": value.unit,
        "response_disposition": value.response_disposition.value,
        "language_code": value.language_code,
        "original_text": value.original_text,
    }


def deserialize_answer(
    value: object,
    *,
    outer: IntakeAnswer | None = None,
    answer_id: OpaqueId | None = None,
    intake_id: OpaqueId | None = None,
    question_id: str | None = None,
    question_version: str | None = None,
    source_type: IntakeAnswerSourceType | None = None,
    answered_at: datetime | None = None,
    created_at: datetime | None = None,
) -> IntakeAnswer:
    try:
        data = _object(
            value,
            {
                "schema_version",
                "answer_type",
                "value",
                "selected_option_ids",
                "unit",
                "response_disposition",
                "language_code",
                "original_text",
            },
        )
        if data["schema_version"] != "intake-answer.v1":
            _invalid()
        answer_type = cast(AnswerType, _enum(AnswerType, data["answer_type"]))
        raw = data["value"]
        decoded: str | bool | Decimal | date | None
        if raw is None or isinstance(raw, bool):
            decoded = raw
        elif answer_type in {AnswerType.NUMBER, AnswerType.DURATION, AnswerType.SEVERITY_SCALE}:
            decoded = _decimal(raw)
        elif answer_type is AnswerType.DATE:
            try:
                decoded = date.fromisoformat(_string(raw))
            except ValueError:
                _invalid()
        else:
            decoded = _string(raw)
        options = (
            None
            if data["selected_option_ids"] is None
            else tuple(_string(item) for item in _list(data["selected_option_ids"]))
        )
        if outer is not None:
            answer_id, intake_id, question_id, question_version = (
                outer.answer_id,
                outer.intake_id,
                outer.question_id,
                outer.question_version,
            )
            source_type, answered_at, created_at = (
                outer.source_type,
                outer.answered_at,
                outer.created_at,
            )
        if None in (
            answer_id,
            intake_id,
            question_id,
            question_version,
            source_type,
            answered_at,
            created_at,
        ):
            _invalid()
        return IntakeAnswer(
            answer_id=cast(OpaqueId, answer_id),
            intake_id=cast(OpaqueId, intake_id),
            question_id=cast(str, question_id),
            question_version=cast(str, question_version),
            answer_type=answer_type,
            value=decoded,
            response_disposition=cast(
                ResponseDisposition, _enum(ResponseDisposition, data["response_disposition"])
            ),
            language_code=_string(data["language_code"]),
            source_type=cast(IntakeAnswerSourceType, source_type),
            answered_at=cast(datetime, answered_at),
            created_at=cast(datetime, created_at),
            selected_option_ids=options,
            unit=_optional_string(data["unit"]),
            original_text=_optional_string(data["original_text"]),
        )
    except (KeyError, TypeError, ValueError):
        _invalid()


def serialize_questionnaire_responses(value: QuestionnaireResponses) -> JsonObject:
    return {
        "schema_version": "questionnaire-responses.v1",
        "pack_id": value.pack_id,
        "pack_version": value.pack_version,
        "answer_refs": [
            {
                "question_id": item.question_id,
                "question_version": item.question_version,
                "answer_id": str(item.answer_id),
            }
            for item in value.answer_refs
        ],
        "skipped_question_refs": [
            {
                "question_id": item.question_id,
                "question_version": item.question_version,
                "disposition": item.disposition.value,
            }
            for item in value.skipped_question_refs
        ],
        "last_selected_question_id": value.last_selected_question_id,
        "engine_version": value.engine_version,
    }


def deserialize_questionnaire_responses(value: object) -> QuestionnaireResponses:
    try:
        data = _object(
            value,
            {
                "schema_version",
                "pack_id",
                "pack_version",
                "answer_refs",
                "skipped_question_refs",
                "last_selected_question_id",
                "engine_version",
            },
        )
        if data["schema_version"] != "questionnaire-responses.v1":
            _invalid()
        answers = []
        for raw in _list(data["answer_refs"]):
            item = _object(raw, {"question_id", "question_version", "answer_id"})
            answers.append(
                AnswerReference(
                    _string(item["question_id"]),
                    _string(item["question_version"]),
                    _id(item["answer_id"]),
                )
            )
        skipped = []
        for raw in _list(data["skipped_question_refs"]):
            item = _object(raw, {"question_id", "question_version", "disposition"})
            skipped.append(
                SkippedQuestionReference(
                    _string(item["question_id"]),
                    _string(item["question_version"]),
                    cast(ResponseDisposition, _enum(ResponseDisposition, item["disposition"])),
                )
            )
        return QuestionnaireResponses(
            pack_id=_string(data["pack_id"]),
            pack_version=_string(data["pack_version"]),
            answer_refs=tuple(answers),
            skipped_question_refs=tuple(skipped),
            last_selected_question_id=_optional_string(data["last_selected_question_id"]),
            engine_version=_string(data["engine_version"]),
        )
    except (KeyError, TypeError, ValueError):
        _invalid()
