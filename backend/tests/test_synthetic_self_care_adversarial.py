from datetime import UTC, datetime

import pytest
from self_care_support.adversarial_harness import run_synthetic_self_care_case

from app.config.settings import Environment
from app.modules.safety.contracts import SyntheticSignal
from app.modules.self_care.eligibility import (
    EligibilityContractCode,
    EligibilityContractError,
    SyntheticEligibilityOutcome,
    SyntheticEligibilityPredicate,
    SyntheticEligibilityReason,
    SyntheticEligibilityResult,
)

NOW = datetime(2026, 11, 1, 12, 0, tzinfo=UTC)


@pytest.mark.parametrize(
    ("safety_signal", "predicates", "outcome", "reason"),
    [
        (
            SyntheticSignal.SYNTHETIC_SELF_CARE_A,
            (
                SyntheticEligibilityPredicate.CONTEXT_COMPLETE_ALPHA,
                SyntheticEligibilityPredicate.INCLUDE_ALPHA,
            ),
            SyntheticEligibilityOutcome.SYNTHETIC_ENGINEERING_CANDIDATE,
            SyntheticEligibilityReason.SYNTHETIC_RULE_MATCH,
        ),
        (
            SyntheticSignal.SYNTHETIC_OVERRIDE_A,
            (
                SyntheticEligibilityPredicate.CONTEXT_COMPLETE_ALPHA,
                SyntheticEligibilityPredicate.INCLUDE_ALPHA,
            ),
            SyntheticEligibilityOutcome.SYNTHETIC_BLOCKED,
            SyntheticEligibilityReason.SYNTHETIC_SAFETY_BLOCK,
        ),
        (
            SyntheticSignal.SYNTHETIC_PRIORITY_A,
            (
                SyntheticEligibilityPredicate.CONTEXT_COMPLETE_ALPHA,
                SyntheticEligibilityPredicate.INCLUDE_ALPHA,
            ),
            SyntheticEligibilityOutcome.SYNTHETIC_BLOCKED,
            SyntheticEligibilityReason.SYNTHETIC_SAFETY_BLOCK,
        ),
        (
            SyntheticSignal.SYNTHETIC_AMBIGUOUS_A,
            (
                SyntheticEligibilityPredicate.CONTEXT_COMPLETE_ALPHA,
                SyntheticEligibilityPredicate.INCLUDE_ALPHA,
            ),
            SyntheticEligibilityOutcome.SYNTHETIC_BLOCKED,
            SyntheticEligibilityReason.SYNTHETIC_SAFETY_BLOCK,
        ),
        (
            SyntheticSignal.SYNTHETIC_SELF_CARE_A,
            (
                SyntheticEligibilityPredicate.CONTEXT_COMPLETE_ALPHA,
                SyntheticEligibilityPredicate.EXCLUDE_ALPHA,
                SyntheticEligibilityPredicate.INCLUDE_ALPHA,
            ),
            SyntheticEligibilityOutcome.SYNTHETIC_BLOCKED,
            SyntheticEligibilityReason.SYNTHETIC_EXCLUSION_MATCH,
        ),
        (
            SyntheticSignal.SYNTHETIC_SELF_CARE_A,
            (
                SyntheticEligibilityPredicate.CONFLICT_ALPHA,
                SyntheticEligibilityPredicate.CONTEXT_COMPLETE_ALPHA,
                SyntheticEligibilityPredicate.INCLUDE_ALPHA,
            ),
            SyntheticEligibilityOutcome.SYNTHETIC_CLARIFICATION_REQUIRED,
            SyntheticEligibilityReason.SYNTHETIC_CONTEXT_CONFLICT,
        ),
        (
            SyntheticSignal.SYNTHETIC_SELF_CARE_A,
            (SyntheticEligibilityPredicate.INCLUDE_ALPHA,),
            SyntheticEligibilityOutcome.SYNTHETIC_CLARIFICATION_REQUIRED,
            SyntheticEligibilityReason.SYNTHETIC_CONTEXT_INCOMPLETE,
        ),
        (
            SyntheticSignal.SYNTHETIC_SELF_CARE_A,
            (SyntheticEligibilityPredicate.CONTEXT_COMPLETE_ALPHA,),
            SyntheticEligibilityOutcome.SYNTHETIC_CLARIFICATION_REQUIRED,
            SyntheticEligibilityReason.SYNTHETIC_NO_RULE_MATCH,
        ),
    ],
)
def test_cross_phase_matrix_is_deterministic_and_fail_closed(
    safety_signal: SyntheticSignal,
    predicates: tuple[SyntheticEligibilityPredicate, ...],
    outcome: SyntheticEligibilityOutcome,
    reason: SyntheticEligibilityReason,
) -> None:
    result = run_synthetic_self_care_case(
        safety_signals=(SyntheticSignal.SYNTHETIC_COMPLETE_A, safety_signal),
        eligibility_predicates=predicates,
        evaluated_at=NOW,
    )

    assert result.outcome is outcome
    assert result.reason_codes == (reason,)
    if outcome is not SyntheticEligibilityOutcome.SYNTHETIC_ENGINEERING_CANDIDATE:
        assert result.candidates == ()


@pytest.mark.parametrize(
    "blocking_signal",
    [
        SyntheticSignal.SYNTHETIC_OVERRIDE_A,
        SyntheticSignal.SYNTHETIC_EXCLUDE_A,
        SyntheticSignal.SYNTHETIC_PRIORITY_A,
        SyntheticSignal.SYNTHETIC_ROUTINE_A,
        SyntheticSignal.SYNTHETIC_AMBIGUOUS_A,
    ],
)
@pytest.mark.parametrize(
    "eligibility_predicates",
    [
        (
            SyntheticEligibilityPredicate.CONTEXT_COMPLETE_ALPHA,
            SyntheticEligibilityPredicate.INCLUDE_ALPHA,
        ),
        (
            SyntheticEligibilityPredicate.CONTEXT_COMPLETE_ALPHA,
            SyntheticEligibilityPredicate.INCLUDE_ALPHA,
            SyntheticEligibilityPredicate.INCLUDE_BETA,
        ),
        (
            SyntheticEligibilityPredicate.CONFLICT_ALPHA,
            SyntheticEligibilityPredicate.CONTEXT_COMPLETE_ALPHA,
            SyntheticEligibilityPredicate.INCLUDE_ALPHA,
        ),
    ],
)
def test_every_upstream_safety_block_precedes_downstream_context(
    blocking_signal: SyntheticSignal,
    eligibility_predicates: tuple[SyntheticEligibilityPredicate, ...],
) -> None:
    result = run_synthetic_self_care_case(
        safety_signals=(
            SyntheticSignal.SYNTHETIC_COMPLETE_A,
            SyntheticSignal.SYNTHETIC_SELF_CARE_A,
            blocking_signal,
        ),
        eligibility_predicates=eligibility_predicates,
        evaluated_at=NOW,
        pack_suffixes=("alpha", "beta"),
    )

    assert result.outcome is SyntheticEligibilityOutcome.SYNTHETIC_BLOCKED
    assert result.reason_codes == (SyntheticEligibilityReason.SYNTHETIC_SAFETY_BLOCK,)
    assert result.candidates == ()


def test_missing_policy_and_future_pack_never_yield_a_candidate() -> None:
    signals = (
        SyntheticSignal.SYNTHETIC_COMPLETE_A,
        SyntheticSignal.SYNTHETIC_SELF_CARE_A,
    )
    predicates = (
        SyntheticEligibilityPredicate.CONTEXT_COMPLETE_ALPHA,
        SyntheticEligibilityPredicate.INCLUDE_ALPHA,
    )

    missing_policy = run_synthetic_self_care_case(
        safety_signals=signals,
        eligibility_predicates=predicates,
        evaluated_at=NOW,
        policy_present=False,
    )
    future_pack = run_synthetic_self_care_case(
        safety_signals=signals,
        eligibility_predicates=predicates,
        evaluated_at=NOW,
        future_pack=True,
    )

    assert missing_policy.reason_codes == (SyntheticEligibilityReason.SYNTHETIC_POLICY_UNAVAILABLE,)
    assert future_pack.reason_codes == (SyntheticEligibilityReason.SYNTHETIC_KNOWLEDGE_INVALID,)
    assert missing_policy.candidates == future_pack.candidates == ()


def test_candidate_absent_from_exact_pack_fails_closed() -> None:
    result = run_synthetic_self_care_case(
        safety_signals=(
            SyntheticSignal.SYNTHETIC_COMPLETE_A,
            SyntheticSignal.SYNTHETIC_SELF_CARE_A,
        ),
        eligibility_predicates=(
            SyntheticEligibilityPredicate.CONTEXT_COMPLETE_ALPHA,
            SyntheticEligibilityPredicate.INCLUDE_BETA,
        ),
        evaluated_at=NOW,
        pack_suffixes=("alpha",),
    )

    assert result.outcome is SyntheticEligibilityOutcome.SYNTHETIC_BLOCKED
    assert result.reason_codes == (SyntheticEligibilityReason.SYNTHETIC_POLICY_INVALID,)
    assert result.candidates == ()


def test_repeated_composition_has_stable_result_and_content_free_shape() -> None:
    def evaluate() -> SyntheticEligibilityResult:
        return run_synthetic_self_care_case(
            safety_signals=(
                SyntheticSignal.SYNTHETIC_COMPLETE_A,
                SyntheticSignal.SYNTHETIC_SELF_CARE_A,
            ),
            eligibility_predicates=(
                SyntheticEligibilityPredicate.CONTEXT_COMPLETE_ALPHA,
                SyntheticEligibilityPredicate.INCLUDE_ALPHA,
                SyntheticEligibilityPredicate.INCLUDE_BETA,
            ),
            evaluated_at=NOW,
            pack_suffixes=("alpha", "beta"),
        )

    first = evaluate()
    second = evaluate()

    assert first == second
    assert tuple(item.guidance_id for item in first.candidates) == (
        "syn_selfcare_guidance_alpha",
        "syn_selfcare_guidance_beta",
    )
    for forbidden in ("patient", "remedy", "advice", "diagnosis", "content", "text"):
        assert not hasattr(first, forbidden)


@pytest.mark.parametrize(
    "environment",
    [Environment.STAGING, Environment.PILOT, Environment.PRODUCTION],
)
def test_protected_environments_are_denied_without_a_result(environment: Environment) -> None:
    with pytest.raises(EligibilityContractError) as caught:
        run_synthetic_self_care_case(
            safety_signals=(
                SyntheticSignal.SYNTHETIC_COMPLETE_A,
                SyntheticSignal.SYNTHETIC_SELF_CARE_A,
            ),
            eligibility_predicates=(
                SyntheticEligibilityPredicate.CONTEXT_COMPLETE_ALPHA,
                SyntheticEligibilityPredicate.INCLUDE_ALPHA,
            ),
            evaluated_at=NOW,
            environment=environment,
        )

    assert caught.value.code is EligibilityContractCode.PROTECTED_ENVIRONMENT


def test_protected_environment_is_denied_before_hostile_inputs_are_read() -> None:
    class Hostile:
        def __getattribute__(self, name: str) -> object:
            raise AssertionError(f"input-read:{name}")

    with pytest.raises(EligibilityContractError) as caught:
        run_synthetic_self_care_case(
            safety_signals=Hostile(),  # type: ignore[arg-type]
            eligibility_predicates=Hostile(),  # type: ignore[arg-type]
            evaluated_at=Hostile(),  # type: ignore[arg-type]
            environment=Environment.PRODUCTION,
        )

    assert caught.value.code is EligibilityContractCode.PROTECTED_ENVIRONMENT
