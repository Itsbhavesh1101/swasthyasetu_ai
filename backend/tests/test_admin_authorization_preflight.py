from __future__ import annotations

from datetime import UTC, datetime, timedelta, timezone

import pytest

from app.config import Environment
from app.modules.admin_governance import (
    AdminContractCode,
    AdminContractError,
    AdminDecisionDisposition,
    AdminDecisionReason,
    SyntheticAdminAction,
    SyntheticAdminDecision,
    SyntheticAdminGrant,
    SyntheticAdminRequest,
    evaluate_synthetic_admin_preflight,
)

NOW = datetime(2026, 11, 1, 12, 0, tzinfo=UTC)
HASH_A = "a" * 64


def request(**changes: object) -> SyntheticAdminRequest:
    values: dict[str, object] = {
        "request_id": "syn_admin_request_alpha",
        "actor_id": "syn_admin_actor_alpha",
        "action": SyntheticAdminAction.SYNTHETIC_ACTION_ALPHA,
        "object_id": "syn_admin_object_alpha",
        "object_version": "engineering.v1",
        "object_hash": HASH_A,
        "institution_id": "syn_admin_institution_alpha",
        "source_id": "syn_admin_source_alpha",
        "purpose_id": "syn_admin_purpose_alpha",
        "mfa_verified": True,
        "created_at": NOW,
    }
    values.update(changes)
    return SyntheticAdminRequest(**values)  # type: ignore[arg-type]


def grant(suffix: str = "alpha", **changes: object) -> SyntheticAdminGrant:
    values: dict[str, object] = {
        "grant_id": f"syn_admin_grant_{suffix}",
        "actor_id": "syn_admin_actor_alpha",
        "action": SyntheticAdminAction.SYNTHETIC_ACTION_ALPHA,
        "object_id": "syn_admin_object_alpha",
        "object_version": "engineering.v1",
        "object_hash": HASH_A,
        "institution_id": "syn_admin_institution_alpha",
        "source_id": "syn_admin_source_alpha",
        "purpose_id": "syn_admin_purpose_alpha",
        "valid_from": NOW - timedelta(minutes=5),
        "expires_at": NOW + timedelta(minutes=5),
    }
    values.update(changes)
    return SyntheticAdminGrant(**values)  # type: ignore[arg-type]


def evaluate(
    value: SyntheticAdminRequest,
    grants: tuple[SyntheticAdminGrant, ...],
    *,
    evaluated_at: datetime = NOW,
    environment: Environment = Environment.TEST,
) -> SyntheticAdminDecision:
    return evaluate_synthetic_admin_preflight(
        value,
        grants,
        evaluated_at=evaluated_at,
        environment=environment,
    )


def test_exact_active_match_produces_only_a_synthetic_contract_match() -> None:
    decision = evaluate(request(), (grant(),))

    assert decision.disposition is AdminDecisionDisposition.MATCHED_SYNTHETIC_CONTRACT
    assert decision.reason is AdminDecisionReason.EXACT_SYNTHETIC_MATCH
    assert decision.matched_grant_id == "syn_admin_grant_alpha"
    assert decision.request_fingerprint == request().fingerprint


def test_mfa_failure_abstains_before_grants_are_inspected() -> None:
    decision = evaluate(request(mfa_verified=False), (object(),))  # type: ignore[arg-type]

    assert decision.disposition is AdminDecisionDisposition.ABSTAINED
    assert decision.reason is AdminDecisionReason.MFA_NOT_VERIFIED
    assert decision.matched_grant_id is None


@pytest.mark.parametrize(
    "changes",
    [
        {"actor_id": "syn_admin_actor_beta"},
        {"action": SyntheticAdminAction.SYNTHETIC_ACTION_BETA},
        {"object_id": "syn_admin_object_beta"},
        {"object_version": "engineering.v2"},
        {"object_hash": "b" * 64},
        {"institution_id": "syn_admin_institution_beta"},
        {"source_id": "syn_admin_source_beta"},
        {"purpose_id": "syn_admin_purpose_beta"},
    ],
)
def test_every_scope_dimension_must_match_exactly(changes: dict[str, object]) -> None:
    decision = evaluate(request(), (grant(**changes),))  # type: ignore[arg-type]

    assert decision.disposition is AdminDecisionDisposition.ABSTAINED
    assert decision.reason is AdminDecisionReason.NO_EXACT_ACTIVE_GRANT


@pytest.mark.parametrize(
    "changes",
    [
        {"valid_from": NOW + timedelta(microseconds=1), "expires_at": NOW + timedelta(minutes=5)},
        {"valid_from": NOW - timedelta(minutes=5), "expires_at": NOW},
    ],
)
def test_future_or_expired_grants_abstain(changes: dict[str, object]) -> None:
    decision = evaluate(request(), (grant(**changes),))  # type: ignore[arg-type]

    assert decision.disposition is AdminDecisionDisposition.ABSTAINED
    assert decision.reason is AdminDecisionReason.NO_EXACT_ACTIVE_GRANT


def test_absent_grants_abstain_without_claiming_authority() -> None:
    decision = evaluate(request(), ())

    assert decision.disposition is AdminDecisionDisposition.ABSTAINED
    assert decision.reason is AdminDecisionReason.NO_EXACT_ACTIVE_GRANT


def test_semantically_duplicate_exact_grants_are_rejected_as_ambiguous() -> None:
    with pytest.raises(AdminContractError) as captured:
        evaluate(request(), (grant("beta"), grant("alpha")))

    assert captured.value.code is AdminContractCode.AMBIGUOUS_GRANT


def test_duplicate_grant_ids_are_rejected() -> None:
    with pytest.raises(AdminContractError) as captured:
        evaluate(request(), (grant(), grant()))

    assert captured.value.code is AdminContractCode.DUPLICATE_GRANT


def test_grant_order_cannot_change_the_decision() -> None:
    nonmatch = grant("beta", actor_id="syn_admin_actor_beta")
    exact = grant("alpha")

    assert evaluate(request(), (nonmatch, exact)) == evaluate(request(), (exact, nonmatch))


def test_aware_non_utc_evaluation_clock_normalizes_to_utc() -> None:
    offset = timezone(timedelta(hours=5, minutes=30))
    decision = evaluate(request(), (grant(),), evaluated_at=NOW.astimezone(offset))

    assert decision.evaluated_at == NOW
    assert decision.evaluated_at.tzinfo is UTC


def test_naive_or_pre_request_evaluation_clock_is_rejected() -> None:
    with pytest.raises(AdminContractError) as naive:
        evaluate(request(), (grant(),), evaluated_at=NOW.replace(tzinfo=None))
    with pytest.raises(AdminContractError) as early:
        evaluate(request(), (grant(),), evaluated_at=NOW - timedelta(microseconds=1))

    assert naive.value.code is AdminContractCode.INVALID_TYPE
    assert early.value.code is AdminContractCode.INVALID_CHRONOLOGY


@pytest.mark.parametrize(
    "environment", [Environment.STAGING, Environment.PILOT, Environment.PRODUCTION]
)
def test_protected_environments_fail_before_inputs_are_inspected(environment: Environment) -> None:
    with pytest.raises(AdminContractError) as captured:
        evaluate_synthetic_admin_preflight(
            object(),  # type: ignore[arg-type]
            (object(),),  # type: ignore[arg-type]
            evaluated_at=object(),  # type: ignore[arg-type]
            environment=environment,
        )

    assert captured.value.code is AdminContractCode.PROTECTED_ENVIRONMENT
