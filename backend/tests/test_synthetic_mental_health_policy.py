from collections.abc import Callable
from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, cast

import pytest
from mental_health_support.policy_fixture import synthetic_policy_fixture

from app.config.settings import Environment
from app.modules.mental_health.contracts import (
    SyntheticSignalCode,
    SyntheticSignalObservation,
    SyntheticSignalState,
)
from app.modules.mental_health.policy import (
    SyntheticMentalHealthRouteEngine,
    SyntheticPolicyArtifact,
    SyntheticPolicyCode,
    SyntheticPolicyError,
    SyntheticPolicyReasonCode,
    SyntheticPolicyState,
    SyntheticRouteDecision,
    SyntheticRouteEvaluation,
    SyntheticRouteState,
    SyntheticRuleKind,
    validate_synthetic_route_decision,
)

NOW = datetime(2026, 10, 31, 18, 0, tzinfo=UTC)


def observation(
    code: SyntheticSignalCode,
    state: SyntheticSignalState = SyntheticSignalState.PRESENT,
) -> SyntheticSignalObservation:
    return SyntheticSignalObservation(code=code, state=state)


def evaluation(
    *,
    extractor: tuple[SyntheticSignalObservation, ...] = (),
    backstop: tuple[SyntheticSignalObservation, ...] = (),
    evaluated_at: datetime = NOW,
) -> SyntheticRouteEvaluation:
    return SyntheticRouteEvaluation(
        evaluation_id="syn_mh_policy_evaluation_alpha",
        extractor_signals=extractor,
        backstop_signals=backstop,
        evaluated_at=evaluated_at,
    )


def policy(
    *,
    state: SyntheticPolicyState = SyntheticPolicyState.TEST_ONLY_ENABLED,
    effective_at: datetime = NOW - timedelta(days=1),
    expires_at: datetime = NOW + timedelta(days=1),
) -> SyntheticPolicyArtifact:
    return synthetic_policy_fixture(
        effective_at=effective_at,
        expires_at=expires_at,
        state=state,
    )


def decide(
    value: SyntheticRouteEvaluation,
    artifact: SyntheticPolicyArtifact | None = None,
    environment: Environment = Environment.TEST,
) -> SyntheticRouteDecision:
    return SyntheticMentalHealthRouteEngine().evaluate(
        evaluation=value,
        policy=policy() if artifact is None else artifact,
        environment=environment,
    )


def test_standard_toy_rule_produces_only_a_synthetic_route() -> None:
    result = decide(evaluation(extractor=(observation(SyntheticSignalCode.ALPHA),)))

    assert result.route is SyntheticRouteState.ALPHA
    assert result.reason_codes == (SyntheticPolicyReasonCode.ALPHA,)
    assert result.policy_reference is not None
    assert result.decided_at == NOW
    assert not hasattr(result, "diagnosis")
    assert not hasattr(result, "patient_message")


def test_toy_override_has_fixed_precedence_over_clarification_and_standard_rules() -> None:
    result = decide(
        evaluation(
            extractor=(
                observation(SyntheticSignalCode.ALPHA),
                observation(SyntheticSignalCode.GAMMA, SyntheticSignalState.UNCERTAIN),
            ),
            backstop=(observation(SyntheticSignalCode.DELTA),),
        )
    )

    assert result.route is SyntheticRouteState.GAMMA
    assert result.reason_codes == (SyntheticPolicyReasonCode.DELTA,)


def test_clarification_precedes_standard_without_assigning_clinical_meaning() -> None:
    result = decide(
        evaluation(
            extractor=(
                observation(SyntheticSignalCode.ALPHA),
                observation(SyntheticSignalCode.GAMMA, SyntheticSignalState.UNCERTAIN),
            )
        )
    )

    assert result.route is SyntheticRouteState.CLARIFICATION_REQUIRED
    assert result.reason_codes == (SyntheticPolicyReasonCode.GAMMA,)


def test_extractor_backstop_disagreement_fails_closed() -> None:
    result = decide(
        evaluation(
            extractor=(observation(SyntheticSignalCode.ALPHA),),
            backstop=(observation(SyntheticSignalCode.ALPHA, SyntheticSignalState.CONTRADICTORY),),
        )
    )

    assert result.route is SyntheticRouteState.DEGRADED_SAFE_FALLBACK
    assert result.reason_codes == (SyntheticPolicyReasonCode.EVIDENCE_CONFLICT,)


def test_equal_precedence_route_conflict_fails_closed_deterministically() -> None:
    first = evaluation(
        extractor=(
            observation(SyntheticSignalCode.ALPHA),
            observation(SyntheticSignalCode.BETA),
        )
    )
    second = evaluation(
        extractor=(observation(SyntheticSignalCode.ALPHA),),
        backstop=(observation(SyntheticSignalCode.BETA),),
    )

    first_result = decide(first)
    second_result = decide(second)
    assert first_result.route is SyntheticRouteState.DEGRADED_SAFE_FALLBACK
    assert first_result.reason_codes == (SyntheticPolicyReasonCode.WINNER_CONFLICT,)
    assert second_result.route is first_result.route
    assert second_result.reason_codes == first_result.reason_codes
    assert second_result.policy_reference == first_result.policy_reference
    assert second_result.evaluation_fingerprint != first_result.evaluation_fingerprint


def test_no_matching_rule_never_guesses_a_route() -> None:
    result = decide(
        evaluation(extractor=(observation(SyntheticSignalCode.ALPHA, SyntheticSignalState.ABSENT),))
    )

    assert result.route is SyntheticRouteState.DEGRADED_SAFE_FALLBACK
    assert result.reason_codes == (SyntheticPolicyReasonCode.NO_MATCH,)


def test_missing_policy_is_explicitly_degraded() -> None:
    result = SyntheticMentalHealthRouteEngine().evaluate(
        evaluation=evaluation(extractor=(observation(SyntheticSignalCode.ALPHA),)),
        policy=None,
        environment=Environment.LOCAL,
    )

    assert result.route is SyntheticRouteState.DEGRADED_SAFE_FALLBACK
    assert result.reason_codes == (SyntheticPolicyReasonCode.POLICY_UNAVAILABLE,)
    assert result.policy_reference is None


@pytest.mark.parametrize(
    ("artifact", "reason"),
    [
        (
            policy(effective_at=NOW + timedelta(seconds=1)),
            SyntheticPolicyReasonCode.POLICY_NOT_EFFECTIVE,
        ),
        (
            policy(expires_at=NOW),
            SyntheticPolicyReasonCode.POLICY_EXPIRED,
        ),
        (
            policy(state=SyntheticPolicyState.TEST_ONLY_SUSPENDED),
            SyntheticPolicyReasonCode.POLICY_SUSPENDED,
        ),
    ],
)
def test_unavailable_policy_lifecycle_states_fail_closed(
    artifact: SyntheticPolicyArtifact,
    reason: SyntheticPolicyReasonCode,
) -> None:
    result = decide(
        evaluation(extractor=(observation(SyntheticSignalCode.ALPHA),)),
        artifact,
    )
    assert result.route is SyntheticRouteState.DEGRADED_SAFE_FALLBACK
    assert result.reason_codes == (reason,)
    assert result.policy_reference is not None


@pytest.mark.parametrize(
    "environment",
    [Environment.STAGING, Environment.PILOT, Environment.PRODUCTION],
)
def test_synthetic_engine_is_denied_in_every_protected_environment(
    environment: Environment,
) -> None:
    class Hostile:
        def __getattribute__(self, name: str) -> Any:
            raise AssertionError(f"protected evaluation read {name}")

    with pytest.raises(SyntheticPolicyError) as raised:
        SyntheticMentalHealthRouteEngine().evaluate(
            evaluation=cast(Any, Hostile()),
            policy=cast(Any, Hostile()),
            environment=environment,
        )
    assert raised.value.code is SyntheticPolicyCode.PROTECTED_ENVIRONMENT


def test_policy_hash_detects_forced_rule_and_metadata_mutation() -> None:
    mutations: tuple[Callable[[SyntheticPolicyArtifact], None], ...] = (
        lambda artifact: object.__setattr__(
            artifact, "state", SyntheticPolicyState.TEST_ONLY_SUSPENDED
        ),
        lambda artifact: object.__setattr__(artifact.rules[0], "route", SyntheticRouteState.BETA),
        lambda artifact: object.__setattr__(artifact, "content_hash", "0" * 64),
    )
    for mutate in mutations:
        artifact = policy()
        mutate(artifact)
        result = decide(
            evaluation(extractor=(observation(SyntheticSignalCode.ALPHA),)),
            artifact,
        )
        assert result.route is SyntheticRouteState.DEGRADED_SAFE_FALLBACK
        assert result.reason_codes == (SyntheticPolicyReasonCode.POLICY_INVALID,)
        assert result.policy_reference is None


def test_evidence_and_decision_are_immutable_and_revalidated() -> None:
    value = evaluation(extractor=(observation(SyntheticSignalCode.ALPHA),))
    result = decide(value)
    with pytest.raises(FrozenInstanceError):
        value.evaluated_at = NOW + timedelta(seconds=1)  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        result.route = SyntheticRouteState.BETA  # type: ignore[misc]

    object.__setattr__(value.extractor_signals[0], "code", "SYN_MH_REAL_SIGNAL")
    with pytest.raises(SyntheticPolicyError):
        SyntheticMentalHealthRouteEngine().evaluate(
            evaluation=value,
            policy=policy(),
            environment=Environment.TEST,
        )


def test_decision_binding_rejects_cross_evaluation_and_forced_mutation() -> None:
    original = evaluation(extractor=(observation(SyntheticSignalCode.ALPHA),))
    artifact = policy()
    result = decide(original, artifact)
    changed = evaluation(backstop=(observation(SyntheticSignalCode.ALPHA),))

    with pytest.raises(SyntheticPolicyError) as cross:
        validate_synthetic_route_decision(changed, result, artifact)
    assert cross.value.code is SyntheticPolicyCode.IDENTITY_MISMATCH

    object.__setattr__(result, "evaluation_fingerprint", "0" * 64)
    with pytest.raises(SyntheticPolicyError) as mutated:
        validate_synthetic_route_decision(original, result, artifact)
    assert mutated.value.code is SyntheticPolicyCode.IDENTITY_MISMATCH


def test_decision_binding_rejects_cross_policy_and_wrong_decision_identity() -> None:
    value = evaluation(extractor=(observation(SyntheticSignalCode.ALPHA),))
    artifact = policy()
    result = decide(value, artifact)
    other_policy = SyntheticPolicyArtifact.create(
        policy_id=artifact.policy_id,
        policy_version="engineering.v2",
        effective_at=artifact.effective_at,
        expires_at=artifact.expires_at,
        state=artifact.state,
        rules=artifact.rules,
    )

    with pytest.raises(SyntheticPolicyError) as cross_policy:
        validate_synthetic_route_decision(value, result, other_policy)
    assert cross_policy.value.code is SyntheticPolicyCode.IDENTITY_MISMATCH

    wrong_id = replace(result, decision_id="syn_mh_policy_decision_beta")
    with pytest.raises(SyntheticPolicyError) as identity:
        validate_synthetic_route_decision(value, wrong_id, artifact)
    assert identity.value.code is SyntheticPolicyCode.IDENTITY_MISMATCH


def test_direct_decision_rejects_mixed_or_multiple_degraded_reasons() -> None:
    value = evaluation()
    unavailable = SyntheticMentalHealthRouteEngine().evaluate(
        evaluation=value,
        policy=None,
        environment=Environment.TEST,
    )
    with pytest.raises(SyntheticPolicyError) as mixed:
        replace(
            unavailable,
            reason_codes=(
                SyntheticPolicyReasonCode.ALPHA,
                SyntheticPolicyReasonCode.POLICY_UNAVAILABLE,
            ),
        )
    assert mixed.value.code is SyntheticPolicyCode.INCONSISTENT_DECISION

    with pytest.raises(SyntheticPolicyError) as multiple:
        replace(
            unavailable,
            reason_codes=(
                SyntheticPolicyReasonCode.POLICY_INVALID,
                SyntheticPolicyReasonCode.POLICY_UNAVAILABLE,
            ),
        )
    assert multiple.value.code is SyntheticPolicyCode.INCONSISTENT_DECISION


def test_aware_non_utc_times_normalize_and_naive_times_fail() -> None:
    offset = timezone(timedelta(hours=5, minutes=30))
    value = evaluation(evaluated_at=NOW.astimezone(offset))
    assert value.evaluated_at == NOW
    assert value.evaluated_at.tzinfo is UTC

    with pytest.raises(SyntheticPolicyError):
        evaluation(evaluated_at=datetime(2026, 10, 31, 18, 0))


def test_rule_contract_rejects_clinically_suggestive_or_inconsistent_values() -> None:
    base = policy().rules[0]
    with pytest.raises(SyntheticPolicyError):
        replace(base, rule_id="self_harm_override")
    with pytest.raises(SyntheticPolicyError):
        replace(base, signal_code=cast(Any, "HIGH_RISK"))
    with pytest.raises(SyntheticPolicyError):
        replace(base, route=cast(Any, "ROUTE_C"))
    with pytest.raises(SyntheticPolicyError):
        replace(
            base,
            kind=SyntheticRuleKind.CLARIFICATION,
            route=SyntheticRouteState.ALPHA,
        )


def test_policy_rejects_unsorted_duplicate_and_hash_mismatched_rules() -> None:
    artifact = policy()
    with pytest.raises(SyntheticPolicyError) as unsorted:
        SyntheticPolicyArtifact.create(
            policy_id=artifact.policy_id,
            policy_version=artifact.policy_version,
            effective_at=artifact.effective_at,
            expires_at=artifact.expires_at,
            state=artifact.state,
            rules=tuple(reversed(artifact.rules)),
        )
    assert unsorted.value.code is SyntheticPolicyCode.INVALID_VALUE

    with pytest.raises(SyntheticPolicyError) as duplicate:
        SyntheticPolicyArtifact.create(
            policy_id=artifact.policy_id,
            policy_version=artifact.policy_version,
            effective_at=artifact.effective_at,
            expires_at=artifact.expires_at,
            state=artifact.state,
            rules=(artifact.rules[0], artifact.rules[0]),
        )
    assert duplicate.value.code is SyntheticPolicyCode.DUPLICATE_RULE

    with pytest.raises(SyntheticPolicyError) as mismatch:
        replace(artifact, content_hash="0" * 64)
    assert mismatch.value.code is SyntheticPolicyCode.POLICY_HASH_MISMATCH


def test_input_has_no_model_score_patient_text_or_real_route_authority() -> None:
    values: dict[str, object] = {
        "evaluation_id": "syn_mh_policy_evaluation_alpha",
        "extractor_signals": (),
        "backstop_signals": (),
        "evaluated_at": NOW,
    }
    for forbidden in (
        "text",
        "patient_id",
        "session_id",
        "model_route",
        "model_score",
        "confidence",
        "questionnaire_score",
        "language",
        "resource",
        "referral",
    ):
        with pytest.raises(TypeError):
            cast(Any, SyntheticRouteEvaluation)(**values, **{forbidden: "canary"})


def test_rule_mapping_is_test_only_and_engine_has_no_runtime_registration() -> None:
    import app.modules.mental_health.policy as policy_module

    production_root = Path(__file__).parents[1] / "app" / "modules" / "mental_health"
    source = "\n".join(path.read_text(encoding="utf-8") for path in production_root.glob("*.py"))
    assert "synthetic_policy_fixture" not in source
    assert "SYN_MH_POLICY_REASON_ALPHA" in source
    assert not hasattr(policy_module, "DEFAULT_POLICY")
    assert not hasattr(policy_module, "APPROVED_POLICY")

    from app.main import app

    assert all("mental-health" not in getattr(route, "path", "") for route in app.routes)
