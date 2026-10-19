"""Policy-neutral safety decision contract tests."""

from dataclasses import FrozenInstanceError, fields
from datetime import UTC, datetime, timedelta, timezone
from typing import Any

import pytest

from app.modules.safety.domain import (
    MAX_REASON_CODES,
    InvalidSafetyDecisionError,
    SafetyDecision,
    SafetyRoute,
)


def decision(**overrides: Any) -> SafetyDecision:
    values: dict[str, Any] = {
        "route": SafetyRoute.ROUTINE_CARE,
        "reason_codes": ("SYNTHETIC_ROUTE",),
        "policy_id": "synthetic-policy",
        "policy_version": "engineering.1",
        "requires_clarification": False,
        "blocks_self_care": True,
        "created_at": datetime(2026, 1, 2, 3, 4, tzinfo=UTC),
    }
    values.update(overrides)
    return SafetyDecision(**values)


def test_route_vocabulary_is_exact() -> None:
    assert tuple(route.value for route in SafetyRoute) == (
        "EMERGENCY",
        "PRIORITY_REVIEW",
        "ROUTINE_CARE",
        "SUPPORTED_SELF_CARE",
        "CLARIFICATION_REQUIRED",
    )
    with pytest.raises(ValueError):
        SafetyRoute("LOW_RISK")


def test_decision_shape_contains_no_diagnosis_or_treatment_authority() -> None:
    assert tuple(item.name for item in fields(SafetyDecision)) == (
        "route",
        "reason_codes",
        "policy_id",
        "policy_version",
        "requires_clarification",
        "blocks_self_care",
        "created_at",
    )


def test_decision_is_frozen_and_normalizes_aware_timestamp_to_utc() -> None:
    value = decision(
        created_at=datetime(2026, 1, 2, 8, 34, tzinfo=timezone(timedelta(hours=5, minutes=30)))
    )
    assert value.created_at == datetime(2026, 1, 2, 3, 4, tzinfo=UTC)
    assert value.created_at.tzinfo is UTC
    with pytest.raises(FrozenInstanceError):
        value.policy_version = "changed"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("override", "message"),
    [
        ({"route": "ROUTINE_CARE"}, "invalid safety route"),
        ({"reason_codes": []}, "invalid reason codes"),
        ({"reason_codes": ()}, "invalid reason codes"),
        ({"reason_codes": ("DUPLICATE", "DUPLICATE")}, "duplicate reason codes"),
        (
            {"reason_codes": ("SECOND", "FIRST")},
            "reason codes must use deterministic ordering",
        ),
        ({"reason_codes": ("patient text",)}, "invalid reason code"),
        ({"reason_codes": tuple(f"CODE_{index:02}" for index in range(17))}, "invalid"),
        ({"policy_id": " Synthetic "}, "invalid policy ID"),
        ({"policy_version": ""}, "invalid policy version"),
        ({"requires_clarification": 1}, "invalid clarification flag"),
        ({"blocks_self_care": 0}, "invalid self-care flag"),
        ({"created_at": datetime(2026, 1, 2)}, "timezone-aware"),
        ({"created_at": "2026-01-02T00:00:00Z"}, "invalid decision timestamp"),
    ],
)
def test_malformed_decision_metadata_fails_with_content_free_error(
    override: dict[str, Any], message: str
) -> None:
    with pytest.raises(InvalidSafetyDecisionError, match=message) as caught:
        decision(**override)
    assert "patient text" not in str(caught.value)


def test_reason_code_bound_is_inclusive() -> None:
    codes = tuple(f"CODE_{index:02}" for index in range(MAX_REASON_CODES))
    assert decision(reason_codes=codes).reason_codes == codes


@pytest.mark.parametrize(
    "overrides",
    [
        {"route": SafetyRoute.CLARIFICATION_REQUIRED, "requires_clarification": False},
        {"route": SafetyRoute.ROUTINE_CARE, "requires_clarification": True},
        {
            "route": SafetyRoute.CLARIFICATION_REQUIRED,
            "requires_clarification": True,
            "blocks_self_care": False,
        },
    ],
)
def test_clarification_is_explicit_and_always_blocks_self_care(
    overrides: dict[str, Any],
) -> None:
    with pytest.raises(InvalidSafetyDecisionError):
        decision(**overrides)


def test_repr_contains_only_bounded_machine_metadata() -> None:
    rendered = repr(decision())
    assert "synthetic-policy" in rendered
    assert "diagnosis" not in rendered.lower()
    assert "patient" not in rendered.lower()
