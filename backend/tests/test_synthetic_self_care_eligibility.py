from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime, timedelta, timezone

import pytest

from app.modules.self_care.eligibility import (
    MAX_SYNTHETIC_ELIGIBILITY_PREDICATES,
    EligibilityContractCode,
    EligibilityContractError,
    SyntheticEligibilityAuthority,
    SyntheticEligibilityCandidateReference,
    SyntheticEligibilityClassification,
    SyntheticEligibilityEvaluation,
    SyntheticEligibilityOutcome,
    SyntheticEligibilityPolicy,
    SyntheticEligibilityPolicyReference,
    SyntheticEligibilityPolicyState,
    SyntheticEligibilityPredicate,
    SyntheticEligibilityReason,
    SyntheticEligibilityResult,
    SyntheticEligibilityRule,
    SyntheticEligibilityVerification,
    synthetic_eligibility_evaluation_fingerprint,
    validate_synthetic_eligibility_policy,
)
from app.modules.self_care.synthetic_eligibility import (
    SYNTHETIC_ELIGIBILITY_POLICY,
    TRUSTED_SYNTHETIC_ELIGIBILITY_POLICY_HASH,
)

NOW = datetime(2026, 10, 31, 1, 0, tzinfo=UTC)
HASH_C = "c" * 64


def rule(suffix: str = "alpha") -> SyntheticEligibilityRule:
    predicate = (
        SyntheticEligibilityPredicate.INCLUDE_ALPHA
        if suffix == "alpha"
        else SyntheticEligibilityPredicate.INCLUDE_BETA
    )
    exclusion = (
        SyntheticEligibilityPredicate.EXCLUDE_ALPHA
        if suffix == "alpha"
        else SyntheticEligibilityPredicate.EXCLUDE_BETA
    )
    return SyntheticEligibilityRule(
        rule_id=f"syn_selfcare_eligibility_rule_{suffix}",
        guidance_id=f"syn_selfcare_guidance_{suffix}",
        guidance_version="engineering.v1",
        required_predicate=predicate,
        exclusion_predicate=exclusion,
    )


def test_compile_time_policy_has_independently_pinned_hash_and_no_content() -> None:
    assert TRUSTED_SYNTHETIC_ELIGIBILITY_POLICY_HASH == (
        "314e181c42ea1c752ea9b6cb2a3c7804e09eb729f34e93c2746f0e530e7145b0"
    )
    assert SYNTHETIC_ELIGIBILITY_POLICY.content_hash == (
        "314e181c42ea1c752ea9b6cb2a3c7804e09eb729f34e93c2746f0e530e7145b0"
    )
    assert SYNTHETIC_ELIGIBILITY_POLICY.state is SyntheticEligibilityPolicyState.TEST_ONLY_ACTIVE
    assert not hasattr(SYNTHETIC_ELIGIBILITY_POLICY.rules[0], "content")
    assert not hasattr(SYNTHETIC_ELIGIBILITY_POLICY.rules[0], "contraindication")
    assert not hasattr(SYNTHETIC_ELIGIBILITY_POLICY.rules[0], "patient_field")


def test_evaluation_normalizes_aware_time_and_has_independent_fingerprint() -> None:
    evaluation = SyntheticEligibilityEvaluation(
        evaluation_id="syn_selfcare_eligibility_evaluation_alpha",
        context_snapshot_hash=HASH_C,
        predicates=(
            SyntheticEligibilityPredicate.CONTEXT_COMPLETE_ALPHA,
            SyntheticEligibilityPredicate.INCLUDE_ALPHA,
        ),
        evaluated_at=datetime(2026, 10, 31, 6, 30, tzinfo=timezone(timedelta(hours=5, minutes=30))),
    )

    assert evaluation.evaluated_at == NOW
    assert synthetic_eligibility_evaluation_fingerprint(evaluation) == (
        "3bc5dca06ba446d4cabc760a0f2d8707f502d0a6e98142d7fef9c2221b38e55d"
    )
    assert evaluation.authority is SyntheticEligibilityAuthority.ENGINEERING_ONLY
    assert evaluation.classification is SyntheticEligibilityClassification.ENGINEERING_SYNTHETIC
    assert evaluation.verification is SyntheticEligibilityVerification.UNVERIFIED


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("evaluation_id", "real-patient", EligibilityContractCode.INVALID_VALUE),
        ("context_snapshot_hash", "not-a-hash", EligibilityContractCode.INVALID_VALUE),
        (
            "predicates",
            [SyntheticEligibilityPredicate.INCLUDE_ALPHA],
            EligibilityContractCode.INVALID_TYPE,
        ),
        ("evaluated_at", datetime(2026, 10, 31), EligibilityContractCode.INVALID_TYPE),
        ("authority", "ENGINEERING_ONLY", EligibilityContractCode.INVALID_TYPE),
    ],
)
def test_evaluation_rejects_open_or_wrongly_typed_values(
    field: str, value: object, code: EligibilityContractCode
) -> None:
    values: dict[str, object] = {
        "evaluation_id": "syn_selfcare_eligibility_evaluation_alpha",
        "context_snapshot_hash": HASH_C,
        "predicates": (SyntheticEligibilityPredicate.INCLUDE_ALPHA,),
        "evaluated_at": NOW,
        "authority": SyntheticEligibilityAuthority.ENGINEERING_ONLY,
    }
    values[field] = value

    with pytest.raises(EligibilityContractError) as caught:
        SyntheticEligibilityEvaluation(**values)  # type: ignore[arg-type]

    assert caught.value.code is code


def test_evaluation_rejects_duplicate_unsorted_and_oversized_predicates() -> None:
    invalid = (
        (SyntheticEligibilityPredicate.INCLUDE_ALPHA,) * 2,
        (
            SyntheticEligibilityPredicate.INCLUDE_ALPHA,
            SyntheticEligibilityPredicate.CONTEXT_COMPLETE_ALPHA,
        ),
        (
            SyntheticEligibilityPredicate.CONTEXT_COMPLETE_ALPHA,
            SyntheticEligibilityPredicate.CONFLICT_ALPHA,
            SyntheticEligibilityPredicate.EXCLUDE_ALPHA,
            SyntheticEligibilityPredicate.INCLUDE_ALPHA,
            SyntheticEligibilityPredicate.INCLUDE_BETA,
        ),
    )
    expected = (
        EligibilityContractCode.DUPLICATE_PREDICATE,
        EligibilityContractCode.INVALID_VALUE,
        EligibilityContractCode.LIMIT_EXCEEDED,
    )

    assert len(invalid[-1]) > MAX_SYNTHETIC_ELIGIBILITY_PREDICATES
    for predicates, code in zip(invalid, expected, strict=True):
        with pytest.raises(EligibilityContractError) as caught:
            SyntheticEligibilityEvaluation(
                evaluation_id="syn_selfcare_eligibility_evaluation_alpha",
                context_snapshot_hash=HASH_C,
                predicates=predicates,
                evaluated_at=NOW,
            )
        assert caught.value.code is code


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("rule_id", "rule-alpha"),
        ("guidance_id", "guidance-real"),
        ("guidance_version", "latest"),
        ("required_predicate", "SYNTHETIC_INCLUDE_ALPHA"),
        ("exclusion_predicate", SyntheticEligibilityPredicate.INCLUDE_ALPHA),
    ],
)
def test_rule_rejects_open_values_and_non_exclusion_pairing(field: str, value: object) -> None:
    values: dict[str, object] = {
        "rule_id": "syn_selfcare_eligibility_rule_alpha",
        "guidance_id": "syn_selfcare_guidance_alpha",
        "guidance_version": "engineering.v1",
        "required_predicate": SyntheticEligibilityPredicate.INCLUDE_ALPHA,
        "exclusion_predicate": SyntheticEligibilityPredicate.EXCLUDE_ALPHA,
    }
    values[field] = value

    with pytest.raises(EligibilityContractError):
        SyntheticEligibilityRule(**values)  # type: ignore[arg-type]


def test_policy_create_sorts_rules_but_direct_constructor_requires_canonical_order() -> None:
    created = SyntheticEligibilityPolicy.create(
        policy_id="syn_selfcare_eligibility_fixture",
        policy_version="engineering.v1",
        effective_at=NOW,
        expires_at=NOW + timedelta(days=1),
        state=SyntheticEligibilityPolicyState.TEST_ONLY_ACTIVE,
        rules=(rule("beta"), rule("alpha")),
    )
    assert tuple(item.rule_id for item in created.rules) == (
        "syn_selfcare_eligibility_rule_alpha",
        "syn_selfcare_eligibility_rule_beta",
    )

    with pytest.raises(EligibilityContractError) as caught:
        replace(created, rules=tuple(reversed(created.rules)))
    assert caught.value.code is EligibilityContractCode.INVALID_VALUE


def test_policy_rejects_duplicate_rule_and_forged_hash() -> None:
    with pytest.raises(EligibilityContractError) as duplicate:
        SyntheticEligibilityPolicy.create(
            policy_id="syn_selfcare_eligibility_fixture",
            policy_version="engineering.v1",
            effective_at=NOW,
            expires_at=NOW + timedelta(days=1),
            state=SyntheticEligibilityPolicyState.TEST_ONLY_ACTIVE,
            rules=(rule(), rule()),
        )
    assert duplicate.value.code is EligibilityContractCode.DUPLICATE_RULE

    with pytest.raises(EligibilityContractError) as forged:
        replace(SYNTHETIC_ELIGIBILITY_POLICY, content_hash="f" * 64)
    assert forged.value.code is EligibilityContractCode.HASH_MISMATCH


def test_policy_revalidation_detects_forced_nested_mutation() -> None:
    damaged = SYNTHETIC_ELIGIBILITY_POLICY
    object.__setattr__(damaged.rules[0], "guidance_id", "forged")
    try:
        with pytest.raises(EligibilityContractError):
            validate_synthetic_eligibility_policy(damaged)
    finally:
        object.__setattr__(damaged.rules[0], "guidance_id", "syn_selfcare_guidance_alpha")


def test_contracts_are_frozen_and_no_approved_state_exists() -> None:
    evaluation = SyntheticEligibilityEvaluation(
        evaluation_id="syn_selfcare_eligibility_evaluation_alpha",
        context_snapshot_hash=HASH_C,
        predicates=(SyntheticEligibilityPredicate.INCLUDE_ALPHA,),
        evaluated_at=NOW,
    )
    with pytest.raises(FrozenInstanceError):
        evaluation.context_snapshot_hash = "d" * 64  # type: ignore[misc]
    with pytest.raises(ValueError):
        SyntheticEligibilityPolicyState("APPROVED")


def test_result_contract_requires_candidate_only_for_engineering_match() -> None:
    result = SyntheticEligibilityResult(
        decision_id="syn_selfcare_eligibility_decision_alpha",
        evaluation_id="syn_selfcare_eligibility_evaluation_alpha",
        evaluation_fingerprint="e" * 64,
        safety_fingerprint="5" * 64,
        knowledge_pack_id="syn_selfcare_pack_fixture",
        knowledge_pack_version="engineering.v1",
        knowledge_pack_hash="a" * 64,
        policy_reference=SyntheticEligibilityPolicyReference(
            policy_id=SYNTHETIC_ELIGIBILITY_POLICY.policy_id,
            policy_version=SYNTHETIC_ELIGIBILITY_POLICY.policy_version,
            content_hash=SYNTHETIC_ELIGIBILITY_POLICY.content_hash,
        ),
        outcome=SyntheticEligibilityOutcome.SYNTHETIC_ENGINEERING_CANDIDATE,
        reason_codes=(SyntheticEligibilityReason.SYNTHETIC_RULE_MATCH,),
        candidates=(
            SyntheticEligibilityCandidateReference(
                guidance_id="syn_selfcare_guidance_alpha",
                guidance_version="engineering.v1",
            ),
        ),
        decided_at=NOW,
    )
    assert result.candidates[0].guidance_id == "syn_selfcare_guidance_alpha"

    with pytest.raises(EligibilityContractError) as inconsistent:
        replace(result, outcome=SyntheticEligibilityOutcome.SYNTHETIC_BLOCKED)
    assert inconsistent.value.code is EligibilityContractCode.INCONSISTENT_RESULT
