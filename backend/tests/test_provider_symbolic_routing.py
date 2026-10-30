from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime, timedelta, timezone
from typing import Any, cast

import pytest

from app.modules.providers.domain import (
    DirectoryAuthority,
    DirectoryContractError,
    DirectoryDataClassification,
    DirectoryVerificationState,
)
from app.modules.providers.routing import (
    RoutingDisposition,
    RoutingReason,
    SymbolicRoutingDecision,
    SymbolicRoutingRequest,
    SymbolicRoutingRule,
    SyntheticRoutingPolicy,
    evaluate_symbolic_route,
)

NOW = datetime(2026, 10, 31, 10, 0, tzinfo=UTC)
HASH = "b" * 64


def rule(
    *,
    rule_id: str = "syn_route_rule_alpha",
    signal_code: str = "syn_signal_alpha",
    service_code: str = "syn_service_alpha",
    order: int = 10,
) -> SymbolicRoutingRule:
    return SymbolicRoutingRule(
        rule_id=rule_id,
        signal_code=signal_code,
        service_code=service_code,
        order=order,
    )


def policy(*rules: SymbolicRoutingRule) -> SyntheticRoutingPolicy:
    return SyntheticRoutingPolicy(
        policy_id="syn_route_policy_fixture",
        policy_version="v1",
        artifact_hash=HASH,
        rules=rules or (rule(),),
        activated_at=NOW,
    )


def request(signal_code: str = "syn_signal_alpha") -> SymbolicRoutingRequest:
    return SymbolicRoutingRequest(
        request_id="syn_route_request_alpha",
        signal_code=signal_code,
        created_at=NOW + timedelta(seconds=1),
    )


def evaluate(
    value: SymbolicRoutingRequest | None = None,
    configured_policy: SyntheticRoutingPolicy | None = None,
) -> SymbolicRoutingDecision:
    return evaluate_symbolic_route(
        value or request(),
        configured_policy or policy(),
        evaluated_at=NOW + timedelta(seconds=2),
    )


def test_exact_symbolic_match_is_deterministic_and_engineering_only() -> None:
    decision = evaluate()

    assert decision.disposition is RoutingDisposition.SYMBOLIC_MATCH
    assert decision.reason is RoutingReason.EXACT_SYMBOLIC_MATCH
    assert decision.service_code == "syn_service_alpha"
    assert decision.matched_rule_id == "syn_route_rule_alpha"
    assert decision.authority is DirectoryAuthority.ENGINEERING_ONLY
    assert decision.classification is DirectoryDataClassification.ENGINEERING_SYNTHETIC
    assert decision.verification is DirectoryVerificationState.UNVERIFIED
    with pytest.raises(FrozenInstanceError):
        decision.service_code = "syn_service_changed"  # type: ignore[misc]


def test_no_exact_match_abstains_without_service_or_rule() -> None:
    decision = evaluate(request("syn_signal_unknown"))

    assert decision.disposition is RoutingDisposition.ABSTAIN
    assert decision.reason is RoutingReason.NO_SYMBOLIC_MATCH
    assert decision.service_code is None
    assert decision.matched_rule_id is None


def test_ambiguous_exact_matches_abstain_instead_of_ranking_services() -> None:
    configured_policy = policy(
        rule(service_code="syn_service_alpha", order=20),
        rule(
            rule_id="syn_route_rule_beta",
            service_code="syn_service_beta",
            order=10,
        ),
    )

    decision = evaluate(configured_policy=configured_policy)

    assert decision.disposition is RoutingDisposition.ABSTAIN
    assert decision.reason is RoutingReason.AMBIGUOUS_SYMBOLIC_MATCH
    assert decision.service_code is None
    assert decision.matched_rule_id is None


def test_rule_order_cannot_break_ambiguity_or_create_provider_ranking() -> None:
    first = policy(
        rule(service_code="syn_service_alpha", order=1),
        rule(rule_id="syn_route_rule_beta", service_code="syn_service_beta", order=2),
    )
    reversed_order = policy(*reversed(first.rules))

    assert first.rules == reversed_order.rules
    assert [item.rule_id for item in first.rules] == [
        "syn_route_rule_alpha",
        "syn_route_rule_beta",
    ]
    assert evaluate(configured_policy=first) == evaluate(configured_policy=reversed_order)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("rule_id", "route_rule_alpha"),
        ("signal_code", "clinical_signal"),
        ("service_code", "cardiology"),
        ("order", 0),
        ("order", True),
        ("order", 10_001),
    ],
)
def test_rule_rejects_non_synthetic_or_invalid_values(field: str, value: object) -> None:
    values: dict[str, object] = {
        "rule_id": "syn_route_rule_alpha",
        "signal_code": "syn_signal_alpha",
        "service_code": "syn_service_alpha",
        "order": 1,
    }
    values[field] = value

    with pytest.raises(DirectoryContractError):
        SymbolicRoutingRule(**cast(Any, values))


def test_policy_rejects_duplicate_rule_ids_and_empty_rules() -> None:
    with pytest.raises(DirectoryContractError):
        SyntheticRoutingPolicy(
            policy_id="syn_route_policy_fixture",
            policy_version="v1",
            artifact_hash=HASH,
            rules=(),
            activated_at=NOW,
        )
    with pytest.raises(DirectoryContractError):
        policy(rule(), replace(rule(), signal_code="syn_signal_beta"))


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("policy_id", "production_policy"),
        ("policy_version", "latest/current"),
        ("artifact_hash", "not-a-hash"),
        ("rules", [rule()]),
        ("activated_at", datetime(2026, 10, 31, 10, 0)),
        ("authority", "PRODUCTION"),
        ("classification", "REAL_DATA"),
        ("verification", "VERIFIED"),
    ],
)
def test_policy_rejects_malformed_or_live_authority(field: str, value: object) -> None:
    values: dict[str, object] = {
        "policy_id": "syn_route_policy_fixture",
        "policy_version": "v1",
        "artifact_hash": HASH,
        "rules": (rule(),),
        "activated_at": NOW,
    }
    values[field] = value

    with pytest.raises(DirectoryContractError):
        SyntheticRoutingPolicy(**cast(Any, values))


def test_policy_normalizes_aware_time_and_revalidates_nested_rules() -> None:
    offset = timezone(timedelta(hours=5, minutes=30))
    configured_policy = replace(policy(rule()), activated_at=NOW.astimezone(offset))
    assert configured_policy.activated_at.tzinfo is UTC

    hostile_rule = rule()
    object.__setattr__(hostile_rule, "signal_code", "clinical_signal")
    with pytest.raises(DirectoryContractError):
        policy(hostile_rule)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("request_id", "request_alpha"),
        ("signal_code", "symptom_alpha"),
        ("created_at", datetime(2026, 10, 31, 10, 0)),
        ("authority", "PRODUCTION"),
        ("classification", "REAL_DATA"),
    ],
)
def test_request_rejects_non_synthetic_naive_or_live_values(field: str, value: object) -> None:
    values: dict[str, object] = {
        "request_id": "syn_route_request_alpha",
        "signal_code": "syn_signal_alpha",
        "created_at": NOW,
    }
    values[field] = value

    with pytest.raises(DirectoryContractError):
        SymbolicRoutingRequest(**cast(Any, values))


def test_engine_revalidates_forcibly_mutated_request_and_policy() -> None:
    hostile_request = request()
    object.__setattr__(hostile_request, "signal_code", "symptom_alpha")
    with pytest.raises(DirectoryContractError):
        evaluate(hostile_request)

    hostile_policy = policy()
    object.__setattr__(hostile_policy, "artifact_hash", "not-a-hash")
    with pytest.raises(DirectoryContractError):
        evaluate(configured_policy=hostile_policy)


def test_engine_rejects_invalid_time_order_without_partial_decision() -> None:
    with pytest.raises(DirectoryContractError):
        evaluate_symbolic_route(request(), policy(), evaluated_at=NOW)
    with pytest.raises(DirectoryContractError):
        evaluate_symbolic_route(
            request(),
            replace(policy(), activated_at=NOW + timedelta(seconds=3)),
            evaluated_at=NOW + timedelta(seconds=2),
        )


@pytest.mark.parametrize(
    ("disposition", "reason", "service_code", "matched_rule_id"),
    [
        (
            RoutingDisposition.SYMBOLIC_MATCH,
            RoutingReason.EXACT_SYMBOLIC_MATCH,
            None,
            "syn_route_rule_alpha",
        ),
        (
            RoutingDisposition.ABSTAIN,
            RoutingReason.NO_SYMBOLIC_MATCH,
            "syn_service_alpha",
            None,
        ),
        (
            RoutingDisposition.ABSTAIN,
            RoutingReason.EXACT_SYMBOLIC_MATCH,
            None,
            None,
        ),
    ],
)
def test_decision_direct_constructor_rejects_inconsistent_states(
    disposition: RoutingDisposition,
    reason: RoutingReason,
    service_code: str | None,
    matched_rule_id: str | None,
) -> None:
    with pytest.raises(DirectoryContractError):
        SymbolicRoutingDecision(
            request_id="syn_route_request_alpha",
            policy_id="syn_route_policy_fixture",
            policy_version="v1",
            policy_artifact_hash=HASH,
            disposition=disposition,
            reason=reason,
            service_code=service_code,
            matched_rule_id=matched_rule_id,
            evaluated_at=NOW,
        )


def test_request_and_decision_have_no_patient_clinical_provider_or_contact_fields() -> None:
    request_values = {
        "request_id": "syn_route_request_alpha",
        "signal_code": "syn_signal_alpha",
        "created_at": NOW,
    }
    for forbidden in ("patient_id", "symptoms", "clinical_facts", "model_output"):
        with pytest.raises(TypeError):
            cast(Any, SymbolicRoutingRequest)(**request_values, **{forbidden: "value"})

    decision_values = {
        "request_id": "syn_route_request_alpha",
        "policy_id": "syn_route_policy_fixture",
        "policy_version": "v1",
        "policy_artifact_hash": HASH,
        "disposition": RoutingDisposition.ABSTAIN,
        "reason": RoutingReason.NO_SYMBOLIC_MATCH,
        "service_code": None,
        "matched_rule_id": None,
        "evaluated_at": NOW,
    }
    for forbidden in ("provider_id", "contact", "rank", "urgency", "safety_route"):
        with pytest.raises(TypeError):
            cast(Any, SymbolicRoutingDecision)(**decision_values, **{forbidden: "value"})
