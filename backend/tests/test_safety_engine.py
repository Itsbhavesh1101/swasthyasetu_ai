"""Deterministic P9-B mechanics over artificial engineering-only tokens."""

from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime, timedelta, timezone, tzinfo
from traceback import format_exception
from typing import Any

import pytest

from app.config.settings import Environment
from app.modules.safety import contracts as safety_contracts
from app.modules.safety.contracts import (
    InvalidSafetyClockError,
    InvalidSyntheticRuleSetError,
    InvalidSyntheticSafetyInputError,
    SafetyEvaluationUnavailableError,
    SyntheticAdvisory,
    SyntheticRuleKind,
    SyntheticRuleSet,
    SyntheticSafetyInput,
    SyntheticSignal,
)
from app.modules.safety.domain import SafetyRoute
from app.modules.safety.engine import SyntheticSafetyEngine
from app.modules.safety.policies import (
    PolicyEnvironmentRejectedError,
    PolicyUnavailableError,
    SafetyPolicyType,
    build_default_policy_registry,
    build_synthetic_policy_registry,
)
from app.modules.safety.synthetic import SYNTHETIC_RULE_SET

NOW = datetime(2026, 2, 3, 4, 5, tzinfo=UTC)


def toy_input(
    *signals: SyntheticSignal, advisory: SyntheticAdvisory | None = None
) -> SyntheticSafetyInput:
    return SyntheticSafetyInput(signals=signals, advisory=advisory)


def engine(
    *,
    registry: object | None = None,
    rule_set: object = SYNTHETIC_RULE_SET,
    clock: Any = lambda: NOW,
) -> SyntheticSafetyEngine:
    return SyntheticSafetyEngine(
        registry=registry or build_synthetic_policy_registry(),  # type: ignore[arg-type]
        rule_set=rule_set,  # type: ignore[arg-type]
        clock=clock,
    )


@pytest.mark.parametrize(
    ("signal", "expected_route", "blocks_self_care"),
    [
        (SyntheticSignal.SYNTHETIC_OVERRIDE_A, SafetyRoute.EMERGENCY, True),
        (SyntheticSignal.SYNTHETIC_PRIORITY_A, SafetyRoute.PRIORITY_REVIEW, True),
        (SyntheticSignal.SYNTHETIC_ROUTINE_A, SafetyRoute.ROUTINE_CARE, True),
        (SyntheticSignal.SYNTHETIC_SELF_CARE_A, SafetyRoute.SUPPORTED_SELF_CARE, False),
    ],
)
def test_exact_fixture_can_mechanically_represent_nonclinical_route_branches(
    signal: SyntheticSignal, expected_route: SafetyRoute, blocks_self_care: bool
) -> None:
    result = engine().evaluate(
        synthetic_input=toy_input(SyntheticSignal.SYNTHETIC_COMPLETE_A, signal),
        environment=Environment.TEST,
    )
    assert result.route is expected_route
    assert result.blocks_self_care is blocks_self_care
    assert result.requires_clarification is False
    assert result.policy_id == "synthetic-physical-safety-metadata"
    assert result.policy_version == "engineering.1"
    assert result.created_at == NOW


@pytest.mark.parametrize(
    "signal",
    [SyntheticSignal.SYNTHETIC_MISSING_A, SyntheticSignal.SYNTHETIC_AMBIGUOUS_A],
)
def test_missing_or_ambiguous_toy_signal_requires_clarification_and_blocks_self_care(
    signal: SyntheticSignal,
) -> None:
    result = engine().evaluate(synthetic_input=toy_input(signal), environment=Environment.LOCAL)
    assert result.route is SafetyRoute.CLARIFICATION_REQUIRED
    assert result.requires_clarification is True
    assert result.blocks_self_care is True
    assert result.reason_codes == (signal.value,)


def test_absent_toy_completeness_never_implies_safe_or_self_care() -> None:
    result = engine().evaluate(
        synthetic_input=toy_input(SyntheticSignal.SYNTHETIC_SELF_CARE_A),
        environment=Environment.TEST,
    )
    assert result.route is SafetyRoute.CLARIFICATION_REQUIRED
    assert result.reason_codes == (
        "SYNTHETIC_INPUT_INCOMPLETE",
        "SYNTHETIC_SELF_CARE_A",
    )
    assert result.blocks_self_care is True


def test_complete_input_without_a_route_fails_closed() -> None:
    with pytest.raises(SafetyEvaluationUnavailableError):
        engine().evaluate(
            synthetic_input=toy_input(SyntheticSignal.SYNTHETIC_COMPLETE_A),
            environment=Environment.TEST,
        )


def test_toy_exclusion_precedes_and_blocks_self_care() -> None:
    result = engine().evaluate(
        synthetic_input=toy_input(
            SyntheticSignal.SYNTHETIC_COMPLETE_A,
            SyntheticSignal.SYNTHETIC_SELF_CARE_A,
            SyntheticSignal.SYNTHETIC_EXCLUDE_A,
        ),
        environment=Environment.LOCAL,
    )
    assert result.route is SafetyRoute.ROUTINE_CARE
    assert result.blocks_self_care is True
    assert result.reason_codes == (
        "SYNTHETIC_EXCLUDE_A",
        "SYNTHETIC_SELF_CARE_A",
    )


def test_toy_priority_order_is_independent_of_input_order() -> None:
    first = toy_input(
        SyntheticSignal.SYNTHETIC_COMPLETE_A,
        SyntheticSignal.SYNTHETIC_SELF_CARE_A,
        SyntheticSignal.SYNTHETIC_ROUTINE_A,
        SyntheticSignal.SYNTHETIC_PRIORITY_A,
    )
    second = toy_input(*reversed(first.signals))
    first_result = engine().evaluate(synthetic_input=first, environment=Environment.TEST)
    second_result = engine().evaluate(synthetic_input=second, environment=Environment.TEST)
    assert first_result == second_result
    assert first_result.route is SafetyRoute.PRIORITY_REVIEW
    assert first_result.blocks_self_care is True


def test_hard_override_wins_every_lower_toy_path_and_low_risk_advisory() -> None:
    signals = (
        SyntheticSignal.SYNTHETIC_COMPLETE_A,
        SyntheticSignal.SYNTHETIC_OVERRIDE_A,
        SyntheticSignal.SYNTHETIC_MISSING_A,
        SyntheticSignal.SYNTHETIC_AMBIGUOUS_A,
        SyntheticSignal.SYNTHETIC_EXCLUDE_A,
        SyntheticSignal.SYNTHETIC_PRIORITY_A,
        SyntheticSignal.SYNTHETIC_ROUTINE_A,
        SyntheticSignal.SYNTHETIC_SELF_CARE_A,
    )
    without_advisory = engine().evaluate(
        synthetic_input=toy_input(*signals), environment=Environment.TEST
    )
    with_advisory = engine().evaluate(
        synthetic_input=toy_input(*signals, advisory=SyntheticAdvisory.LOW_RISK),
        environment=Environment.TEST,
    )
    assert with_advisory == without_advisory
    assert with_advisory.route is SafetyRoute.EMERGENCY
    assert with_advisory.requires_clarification is False
    assert with_advisory.blocks_self_care is True
    assert with_advisory.reason_codes == tuple(sorted(with_advisory.reason_codes))


def test_multiple_hard_overrides_are_stable_unique_and_sorted() -> None:
    result = engine().evaluate(
        synthetic_input=toy_input(
            SyntheticSignal.SYNTHETIC_OVERRIDE_B,
            SyntheticSignal.SYNTHETIC_OVERRIDE_A,
        ),
        environment=Environment.LOCAL,
    )
    assert result.route is SafetyRoute.EMERGENCY
    assert result.reason_codes == (
        "SYNTHETIC_OVERRIDE_A",
        "SYNTHETIC_OVERRIDE_B",
    )


def test_reversed_rule_registration_order_canonicalizes_to_same_result() -> None:
    reversed_rules = SyntheticRuleSet.create(
        fixture_id=SYNTHETIC_RULE_SET.fixture_id,
        policy_type=SYNTHETIC_RULE_SET.policy_type,
        policy_id=SYNTHETIC_RULE_SET.policy_id,
        policy_version=SYNTHETIC_RULE_SET.policy_version,
        approval_state=SYNTHETIC_RULE_SET.approval_state,
        reason_code_namespace=SYNTHETIC_RULE_SET.reason_code_namespace,
        rules=tuple(reversed(SYNTHETIC_RULE_SET.rules)),
    )
    value = toy_input(
        SyntheticSignal.SYNTHETIC_COMPLETE_A,
        SyntheticSignal.SYNTHETIC_PRIORITY_A,
        SyntheticSignal.SYNTHETIC_ROUTINE_A,
    )
    assert engine(rule_set=reversed_rules).evaluate(
        synthetic_input=value, environment=Environment.TEST
    ) == engine().evaluate(synthetic_input=value, environment=Environment.TEST)


def test_aware_non_utc_clock_is_normalized_and_repeatable() -> None:
    offset = timezone(timedelta(hours=5, minutes=30))
    local_time = datetime(2026, 2, 3, 9, 35, tzinfo=offset)
    evaluator = engine(clock=lambda: local_time)
    value = toy_input(
        SyntheticSignal.SYNTHETIC_COMPLETE_A,
        SyntheticSignal.SYNTHETIC_ROUTINE_A,
    )
    first = evaluator.evaluate(synthetic_input=value, environment=Environment.TEST)
    second = evaluator.evaluate(synthetic_input=value, environment=Environment.TEST)
    assert first == second
    assert first.created_at == NOW
    assert first.created_at.tzinfo is UTC


@pytest.mark.parametrize("clock", [lambda: datetime(2026, 2, 3), lambda: "not-a-time"])
def test_invalid_controlled_clock_fails_with_typed_content_free_error(clock: Any) -> None:
    with pytest.raises(InvalidSafetyClockError):
        engine(clock=clock).evaluate(
            synthetic_input=toy_input(SyntheticSignal.SYNTHETIC_OVERRIDE_A),
            environment=Environment.TEST,
        )


def test_clock_failure_is_normalized_without_chaining_sensitive_cause() -> None:
    privacy_canary = "synthetic-private-clock-canary"

    def broken_clock() -> datetime:
        raise RuntimeError(privacy_canary)

    with pytest.raises(InvalidSafetyClockError) as caught:
        engine(clock=broken_clock).evaluate(
            synthetic_input=toy_input(SyntheticSignal.SYNTHETIC_OVERRIDE_A),
            environment=Environment.TEST,
        )
    assert privacy_canary not in str(caught.value)
    assert caught.value.__cause__ is None
    assert caught.value.__suppress_context__ is True
    assert privacy_canary not in "".join(
        format_exception(type(caught.value), caught.value, caught.value.__traceback__)
    )


def test_input_and_result_are_immutable() -> None:
    value = toy_input(SyntheticSignal.SYNTHETIC_OVERRIDE_A)
    result = engine().evaluate(synthetic_input=value, environment=Environment.TEST)
    with pytest.raises(FrozenInstanceError):
        value.advisory = SyntheticAdvisory.LOW_RISK  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        result.blocks_self_care = False  # type: ignore[misc]


def test_mechanical_precedence_contract_is_immutable() -> None:
    with pytest.raises(TypeError):
        safety_contracts._KIND_CONTRACT[SyntheticRuleKind.HARD_OVERRIDE] = (  # type: ignore[index]
            0,
            SafetyRoute.SUPPORTED_SELF_CARE,
            False,
            False,
        )


@pytest.mark.parametrize(
    "signals",
    [
        (),
        [],
        (SyntheticSignal.SYNTHETIC_OVERRIDE_A, SyntheticSignal.SYNTHETIC_OVERRIDE_A),
        ("SYNTHETIC_OVERRIDE_A",),
        tuple(SyntheticSignal.SYNTHETIC_OVERRIDE_A for _ in range(17)),
    ],
)
def test_malformed_synthetic_input_is_rejected(signals: Any) -> None:
    with pytest.raises(InvalidSyntheticSafetyInputError):
        SyntheticSafetyInput(signals=signals)


def test_mutated_input_is_revalidated_at_evaluation_boundary() -> None:
    value = toy_input(SyntheticSignal.SYNTHETIC_OVERRIDE_A)
    object.__setattr__(value, "signals", ("privacy-canary",))
    with pytest.raises(InvalidSyntheticSafetyInputError) as caught:
        engine().evaluate(synthetic_input=value, environment=Environment.TEST)
    assert "privacy-canary" not in str(caught.value)


@pytest.mark.parametrize("environment", list(Environment))
def test_default_registry_fails_before_clock_or_any_rule_in_every_environment(
    environment: Environment,
) -> None:
    calls = 0

    def clock() -> datetime:
        nonlocal calls
        calls += 1
        return NOW

    with pytest.raises(PolicyUnavailableError):
        engine(registry=build_default_policy_registry(), clock=clock).evaluate(
            synthetic_input=toy_input(SyntheticSignal.SYNTHETIC_SELF_CARE_A),
            environment=environment,
        )
    assert calls == 0


@pytest.mark.parametrize(
    "environment", [Environment.STAGING, Environment.PILOT, Environment.PRODUCTION]
)
def test_actual_evaluate_entry_rejects_synthetic_fixture_in_protected_environment(
    environment: Environment,
) -> None:
    with pytest.raises(PolicyEnvironmentRejectedError):
        engine().evaluate(
            synthetic_input=toy_input(SyntheticSignal.SYNTHETIC_OVERRIDE_A),
            environment=environment,
        )


def test_registry_returned_metadata_mutation_cannot_subvert_evaluation() -> None:
    registry = build_synthetic_policy_registry()
    returned = registry.get_active_policy(
        policy_type=SafetyPolicyType.PHYSICAL_SAFETY,
        environment=Environment.TEST,
    )
    object.__setattr__(returned, "policy_version", "engineering.999")
    result = engine(registry=registry).evaluate(
        synthetic_input=toy_input(SyntheticSignal.SYNTHETIC_OVERRIDE_A),
        environment=Environment.TEST,
    )
    assert result.policy_version == "engineering.1"


@pytest.mark.parametrize(
    "mutator",
    [
        lambda value: object.__setattr__(value, "fixture_id", "synthetic-unsupported.v2"),
        lambda value: object.__setattr__(value, "policy_version", "engineering.2"),
        lambda value: object.__setattr__(value, "approval_state", "APPROVED"),
        lambda value: object.__setattr__(value, "rules_checksum", "0" * 64),
    ],
)
def test_tampered_or_fabricated_rule_set_fails_closed(mutator: Any) -> None:
    rule_set = replace(SYNTHETIC_RULE_SET)
    mutator(rule_set)
    with pytest.raises(InvalidSyntheticRuleSetError):
        engine(rule_set=rule_set).evaluate(
            synthetic_input=toy_input(SyntheticSignal.SYNTHETIC_OVERRIDE_A),
            environment=Environment.TEST,
        )


def test_tampered_nested_rule_outcome_is_revalidated() -> None:
    rule_set = replace(
        SYNTHETIC_RULE_SET,
        rules=tuple(replace(rule) for rule in SYNTHETIC_RULE_SET.rules),
    )
    object.__setattr__(rule_set.rules[0], "route", SafetyRoute.EMERGENCY)
    with pytest.raises(InvalidSyntheticRuleSetError):
        engine(rule_set=rule_set).evaluate(
            synthetic_input=toy_input(SyntheticSignal.SYNTHETIC_AMBIGUOUS_A),
            environment=Environment.TEST,
        )


def test_tampered_rule_container_fails_with_content_free_typed_error() -> None:
    privacy_canary = "private-mutated-rule-canary"
    rule_set = replace(SYNTHETIC_RULE_SET)
    object.__setattr__(rule_set, "rules", (privacy_canary,))
    with pytest.raises(InvalidSyntheticRuleSetError) as caught:
        engine(rule_set=rule_set).evaluate(
            synthetic_input=toy_input(SyntheticSignal.SYNTHETIC_OVERRIDE_A),
            environment=Environment.TEST,
        )
    assert privacy_canary not in "".join(
        format_exception(type(caught.value), caught.value, caught.value.__traceback__)
    )


def test_pathological_clock_timezone_fails_with_content_free_typed_error() -> None:
    privacy_canary = "private-clock-timezone-canary"

    class BrokenTimezone(tzinfo):
        def utcoffset(self, value: datetime | None) -> timedelta | None:
            raise RuntimeError(privacy_canary)

        def dst(self, value: datetime | None) -> timedelta | None:
            return None

        def tzname(self, value: datetime | None) -> str | None:
            return "BROKEN"

    invalid_time = datetime(2026, 2, 3, tzinfo=BrokenTimezone())
    with pytest.raises(InvalidSafetyClockError) as caught:
        engine(clock=lambda: invalid_time).evaluate(
            synthetic_input=toy_input(SyntheticSignal.SYNTHETIC_OVERRIDE_A),
            environment=Environment.TEST,
        )
    assert privacy_canary not in "".join(
        format_exception(type(caught.value), caught.value, caught.value.__traceback__)
    )


def test_advisory_is_not_a_callback_and_cannot_delay_evaluation() -> None:
    value = toy_input(
        SyntheticSignal.SYNTHETIC_OVERRIDE_A,
        advisory=SyntheticAdvisory.LOW_RISK,
    )
    assert not callable(value.advisory)
    assert (
        engine().evaluate(synthetic_input=value, environment=Environment.TEST).route
        is SafetyRoute.EMERGENCY
    )
