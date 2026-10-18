"""Typed P7-C HTTP answer-payload conversion regressions."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.modules.clinical_intake.api import AnswerPayload, _patient_value
from app.modules.clinical_intake.contracts import AnswerType, ResponseDisposition


@pytest.mark.parametrize(
    ("answer_type", "raw_value", "expected"),
    [
        (AnswerType.TEXT, "synthetic", "synthetic"),
        (AnswerType.SINGLE_CHOICE, None, None),
        (AnswerType.MULTI_CHOICE, None, None),
        (AnswerType.BOOLEAN, False, False),
        (AnswerType.NUMBER, 2.5, Decimal("2.5")),
        (AnswerType.DATE, "2026-10-18", date(2026, 10, 18)),
        (AnswerType.DURATION, 3, Decimal("3")),
        (AnswerType.SEVERITY_SCALE, 2, Decimal("2")),
    ],
)
def test_all_eight_http_answer_types_convert_without_truthiness_or_type_loss(
    answer_type: AnswerType,
    raw_value: str | bool | int | float | None,
    expected: str | bool | Decimal | date | None,
) -> None:
    payload = AnswerPayload.model_validate(
        {
            "schema_version": "intake-answer.v1",
            "answer_type": answer_type.value,
            "value": raw_value,
            "selected_option_ids": ["one"]
            if answer_type in {AnswerType.SINGLE_CHOICE, AnswerType.MULTI_CHOICE}
            else None,
            "unit": "unit" if answer_type in {AnswerType.NUMBER, AnswerType.DURATION} else None,
            "response_disposition": "ANSWERED",
            "language_code": "en",
            "original_text": "synthetic" if answer_type is AnswerType.TEXT else None,
        }
    )
    assert _patient_value(payload) == expected


@pytest.mark.parametrize("raw_value", [float("nan"), float("inf"), "not-a-number"])
def test_http_numeric_values_reject_non_finite_or_non_numeric_input(raw_value: object) -> None:
    payload = AnswerPayload.model_validate(
        {
            "schema_version": "intake-answer.v1",
            "answer_type": "NUMBER",
            "value": raw_value,
            "selected_option_ids": None,
            "unit": "unit",
            "response_disposition": "ANSWERED",
            "language_code": "en",
            "original_text": None,
        }
    )
    with pytest.raises(ValueError, match="numeric value is invalid"):
        _patient_value(payload)


def test_http_answer_payload_rejects_extra_authority_fields() -> None:
    with pytest.raises(ValidationError):
        AnswerPayload.model_validate(
            {
                "schema_version": "intake-answer.v1",
                "answer_type": "TEXT",
                "value": "synthetic",
                "selected_option_ids": None,
                "unit": None,
                "response_disposition": ResponseDisposition.ANSWERED.value,
                "language_code": "en",
                "original_text": "synthetic",
                "verification_state": "CLINICIAN_CONFIRMED",
            }
        )
