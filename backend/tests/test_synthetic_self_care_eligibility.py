from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime, timedelta, timezone

import pytest

from app.config.settings import Environment
from app.modules.safety.domain import SafetyDecision, SafetyRoute
from app.modules.self_care.contracts import (
    SyntheticGuidancePlaceholder,
    SyntheticKnowledgeItem,
    SyntheticKnowledgePack,
    SyntheticKnowledgePackState,
    SyntheticKnowledgeTag,
    create_synthetic_knowledge_pack,
)
from app.modules.self_care.eligibility import (
    MAX_SYNTHETIC_ELIGIBILITY_PREDICATES,
    EligibilityContractCode,
    EligibilityContractError,
    SyntheticEligibilityAuthority,
    SyntheticEligibilityCandidateReference,
    SyntheticEligibilityClassification,
    SyntheticEligibilityEngine,
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
    safety_decision_fingerprint,
    synthetic_eligibility_evaluation_fingerprint,
    validate_synthetic_eligibility_policy,
    validate_synthetic_eligibility_result,
)
from app.modules.self_care.synthetic_eligibility import (
    SYNTHETIC_ELIGIBILITY_POLICY,
    TRUSTED_SYNTHETIC_ELIGIBILITY_POLICY_HASH,
)

NOW = datetime(2026, 10, 31, 1, 0, tzinfo=UTC)
HASH_C = "c" * 64
HASH_A = "a" * 64
SAFETY_TIME = datetime(2026, 10, 31, 0, 59, tzinfo=UTC)


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


def evaluation(*predicates: SyntheticEligibilityPredicate) -> SyntheticEligibilityEvaluation:
    return SyntheticEligibilityEvaluation(
        evaluation_id="syn_selfcare_eligibility_evaluation_alpha",
        context_snapshot_hash=HASH_C,
        predicates=predicates,
        evaluated_at=NOW,
    )


def safety(*, blocked: bool = False) -> SafetyDecision:
    return SafetyDecision(
        route=SafetyRoute.ROUTINE_CARE if blocked else SafetyRoute.SUPPORTED_SELF_CARE,
        reason_codes=("SYNTHETIC_ROUTINE_A",) if blocked else ("SYNTHETIC_SELF_CARE_A",),
        policy_id="synthetic-physical-safety-metadata",
        policy_version="engineering.1",
        requires_clarification=False,
        blocks_self_care=blocked,
        created_at=SAFETY_TIME,
    )


def knowledge_pack(*suffixes: str) -> SyntheticKnowledgePack:
    items = tuple(
        SyntheticKnowledgeItem(
            guidance_id=f"syn_selfcare_guidance_{suffix}",
            version="engineering.v1",
            placeholder_token=(
                SyntheticGuidancePlaceholder.ALPHA
                if suffix == "alpha"
                else SyntheticGuidancePlaceholder.BETA
            ),
            source_id=f"syn_selfcare_source_{suffix}",
            source_version="engineering.v1",
            source_hash=HASH_A,
            tags=(
                SyntheticKnowledgeTag.ALPHA if suffix == "alpha" else SyntheticKnowledgeTag.BETA,
            ),
        )
        for suffix in suffixes
    )
    return create_synthetic_knowledge_pack(
        pack_id="syn_selfcare_pack_fixture",
        pack_version="engineering.v1",
        schema_version="synthetic-self-care-knowledge.v1",
        state=SyntheticKnowledgePackState.TEST_ONLY_UNAPPROVED,
        created_at=datetime(2026, 10, 31, tzinfo=UTC),
        items=items,
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


@pytest.mark.parametrize(
    "environment",
    [Environment.STAGING, Environment.PILOT, Environment.PRODUCTION],
)
def test_engine_rejects_protected_environments_before_evaluation(
    environment: Environment,
) -> None:
    damaged = evaluation(SyntheticEligibilityPredicate.CONTEXT_COMPLETE_ALPHA)
    object.__setattr__(damaged, "context_snapshot_hash", "forged")
    try:
        with pytest.raises(EligibilityContractError) as caught:
            SyntheticEligibilityEngine().evaluate(
                evaluation=damaged,
                safety_decision=safety(),
                knowledge_pack=knowledge_pack("alpha"),
                policy=SYNTHETIC_ELIGIBILITY_POLICY,
                environment=environment,
            )
    finally:
        object.__setattr__(damaged, "context_snapshot_hash", HASH_C)
    assert caught.value.code is EligibilityContractCode.PROTECTED_ENVIRONMENT


def test_safety_block_cannot_be_downgraded_by_matching_context() -> None:
    result = SyntheticEligibilityEngine().evaluate(
        evaluation=evaluation(
            SyntheticEligibilityPredicate.CONTEXT_COMPLETE_ALPHA,
            SyntheticEligibilityPredicate.INCLUDE_ALPHA,
        ),
        safety_decision=safety(blocked=True),
        knowledge_pack=knowledge_pack("alpha"),
        policy=SYNTHETIC_ELIGIBILITY_POLICY,
        environment=Environment.TEST,
    )

    assert result.outcome is SyntheticEligibilityOutcome.SYNTHETIC_BLOCKED
    assert result.reason_codes == (SyntheticEligibilityReason.SYNTHETIC_SAFETY_BLOCK,)
    assert result.candidates == ()


@pytest.mark.parametrize(
    "forged",
    [
        SafetyDecision(
            route=SafetyRoute.SUPPORTED_SELF_CARE,
            reason_codes=("SYNTHETIC_SELF_CARE_A",),
            policy_id="forged-policy",
            policy_version="engineering.1",
            requires_clarification=False,
            blocks_self_care=False,
            created_at=SAFETY_TIME,
        ),
        SafetyDecision(
            route=SafetyRoute.SUPPORTED_SELF_CARE,
            reason_codes=("SYNTHETIC_OTHER",),
            policy_id="synthetic-physical-safety-metadata",
            policy_version="engineering.1",
            requires_clarification=False,
            blocks_self_care=False,
            created_at=SAFETY_TIME,
        ),
    ],
)
def test_forged_positive_safety_provenance_fails_closed(forged: SafetyDecision) -> None:
    result = SyntheticEligibilityEngine().evaluate(
        evaluation=evaluation(
            SyntheticEligibilityPredicate.CONTEXT_COMPLETE_ALPHA,
            SyntheticEligibilityPredicate.INCLUDE_ALPHA,
        ),
        safety_decision=forged,
        knowledge_pack=knowledge_pack("alpha"),
        policy=SYNTHETIC_ELIGIBILITY_POLICY,
        environment=Environment.TEST,
    )
    assert result.outcome is SyntheticEligibilityOutcome.SYNTHETIC_BLOCKED
    assert result.candidates == ()


@pytest.mark.parametrize(
    ("predicates", "reason"),
    [
        (
            (SyntheticEligibilityPredicate.INCLUDE_ALPHA,),
            SyntheticEligibilityReason.SYNTHETIC_CONTEXT_INCOMPLETE,
        ),
        (
            (
                SyntheticEligibilityPredicate.CONFLICT_ALPHA,
                SyntheticEligibilityPredicate.CONTEXT_COMPLETE_ALPHA,
                SyntheticEligibilityPredicate.INCLUDE_ALPHA,
            ),
            SyntheticEligibilityReason.SYNTHETIC_CONTEXT_CONFLICT,
        ),
    ],
)
def test_missing_or_conflicting_context_requires_clarification(
    predicates: tuple[SyntheticEligibilityPredicate, ...],
    reason: SyntheticEligibilityReason,
) -> None:
    result = SyntheticEligibilityEngine().evaluate(
        evaluation=evaluation(*predicates),
        safety_decision=safety(),
        knowledge_pack=knowledge_pack("alpha"),
        policy=SYNTHETIC_ELIGIBILITY_POLICY,
        environment=Environment.TEST,
    )
    assert result.outcome is SyntheticEligibilityOutcome.SYNTHETIC_CLARIFICATION_REQUIRED
    assert result.reason_codes == (reason,)
    assert result.candidates == ()


def test_exclusion_precedes_matching_include_predicate() -> None:
    result = SyntheticEligibilityEngine().evaluate(
        evaluation=evaluation(
            SyntheticEligibilityPredicate.CONTEXT_COMPLETE_ALPHA,
            SyntheticEligibilityPredicate.EXCLUDE_ALPHA,
            SyntheticEligibilityPredicate.INCLUDE_ALPHA,
        ),
        safety_decision=safety(),
        knowledge_pack=knowledge_pack("alpha"),
        policy=SYNTHETIC_ELIGIBILITY_POLICY,
        environment=Environment.TEST,
    )
    assert result.outcome is SyntheticEligibilityOutcome.SYNTHETIC_BLOCKED
    assert result.reason_codes == (SyntheticEligibilityReason.SYNTHETIC_EXCLUSION_MATCH,)
    assert result.candidates == ()


def test_exact_synthetic_matches_produce_deterministic_placeholder_references() -> None:
    evaluated = evaluation(
        SyntheticEligibilityPredicate.CONTEXT_COMPLETE_ALPHA,
        SyntheticEligibilityPredicate.INCLUDE_ALPHA,
        SyntheticEligibilityPredicate.INCLUDE_BETA,
    )
    pack = knowledge_pack("alpha", "beta")
    safety_result = safety()
    result = SyntheticEligibilityEngine().evaluate(
        evaluation=evaluated,
        safety_decision=safety_result,
        knowledge_pack=pack,
        policy=SYNTHETIC_ELIGIBILITY_POLICY,
        environment=Environment.TEST,
    )

    assert result.outcome is SyntheticEligibilityOutcome.SYNTHETIC_ENGINEERING_CANDIDATE
    assert result.reason_codes == (SyntheticEligibilityReason.SYNTHETIC_RULE_MATCH,)
    assert tuple(candidate.guidance_id for candidate in result.candidates) == (
        "syn_selfcare_guidance_alpha",
        "syn_selfcare_guidance_beta",
    )
    assert result.safety_fingerprint == safety_decision_fingerprint(safety_result)
    assert (
        validate_synthetic_eligibility_result(
            evaluation=evaluated,
            safety_decision=safety_result,
            knowledge_pack=pack,
            policy=SYNTHETIC_ELIGIBILITY_POLICY,
            result=result,
        )
        == result
    )


@pytest.mark.parametrize(
    ("policy", "moment", "reason"),
    [
        (None, NOW, SyntheticEligibilityReason.SYNTHETIC_POLICY_UNAVAILABLE),
        (
            replace(
                SYNTHETIC_ELIGIBILITY_POLICY,
                state=SyntheticEligibilityPolicyState.TEST_ONLY_SUSPENDED,
                content_hash=SyntheticEligibilityPolicy.create(
                    policy_id="syn_selfcare_eligibility_fixture",
                    policy_version="engineering.v1",
                    effective_at=datetime(2026, 10, 31, tzinfo=UTC),
                    expires_at=datetime(2027, 10, 31, tzinfo=UTC),
                    state=SyntheticEligibilityPolicyState.TEST_ONLY_SUSPENDED,
                    rules=SYNTHETIC_ELIGIBILITY_POLICY.rules,
                ).content_hash,
            ),
            NOW,
            SyntheticEligibilityReason.SYNTHETIC_POLICY_SUSPENDED,
        ),
        (
            SYNTHETIC_ELIGIBILITY_POLICY,
            datetime(2026, 10, 30, 23, 59, tzinfo=UTC),
            SyntheticEligibilityReason.SYNTHETIC_POLICY_NOT_EFFECTIVE,
        ),
        (
            SYNTHETIC_ELIGIBILITY_POLICY,
            datetime(2027, 10, 31, tzinfo=UTC),
            SyntheticEligibilityReason.SYNTHETIC_POLICY_EXPIRED,
        ),
    ],
)
def test_unavailable_suspended_or_out_of_window_policy_blocks(
    policy: SyntheticEligibilityPolicy | None,
    moment: datetime,
    reason: SyntheticEligibilityReason,
) -> None:
    evaluated = SyntheticEligibilityEvaluation(
        evaluation_id="syn_selfcare_eligibility_evaluation_alpha",
        context_snapshot_hash=HASH_C,
        predicates=(
            SyntheticEligibilityPredicate.CONTEXT_COMPLETE_ALPHA,
            SyntheticEligibilityPredicate.INCLUDE_ALPHA,
        ),
        evaluated_at=moment,
    )
    result = SyntheticEligibilityEngine().evaluate(
        evaluation=evaluated,
        safety_decision=safety(),
        knowledge_pack=knowledge_pack("alpha"),
        policy=policy,
        environment=Environment.TEST,
    )
    assert result.outcome is SyntheticEligibilityOutcome.SYNTHETIC_BLOCKED
    assert result.reason_codes == (reason,)


def test_policy_rule_missing_from_pack_blocks_as_invalid() -> None:
    result = SyntheticEligibilityEngine().evaluate(
        evaluation=evaluation(
            SyntheticEligibilityPredicate.CONTEXT_COMPLETE_ALPHA,
            SyntheticEligibilityPredicate.INCLUDE_BETA,
        ),
        safety_decision=safety(),
        knowledge_pack=knowledge_pack("alpha"),
        policy=SYNTHETIC_ELIGIBILITY_POLICY,
        environment=Environment.TEST,
    )
    assert result.outcome is SyntheticEligibilityOutcome.SYNTHETIC_BLOCKED
    assert result.reason_codes == (SyntheticEligibilityReason.SYNTHETIC_POLICY_INVALID,)


def test_forced_policy_mutation_blocks_as_invalid_without_leaking_value() -> None:
    damaged = SYNTHETIC_ELIGIBILITY_POLICY
    object.__setattr__(damaged.rules[0], "guidance_id", "private-canary")
    try:
        result = SyntheticEligibilityEngine().evaluate(
            evaluation=evaluation(
                SyntheticEligibilityPredicate.CONTEXT_COMPLETE_ALPHA,
                SyntheticEligibilityPredicate.INCLUDE_ALPHA,
            ),
            safety_decision=safety(),
            knowledge_pack=knowledge_pack("alpha"),
            policy=damaged,
            environment=Environment.TEST,
        )
    finally:
        object.__setattr__(damaged.rules[0], "guidance_id", "syn_selfcare_guidance_alpha")
    assert result.outcome is SyntheticEligibilityOutcome.SYNTHETIC_BLOCKED
    assert result.reason_codes == (SyntheticEligibilityReason.SYNTHETIC_POLICY_INVALID,)
    assert "private-canary" not in str(result)


def test_complete_context_without_include_match_requires_clarification() -> None:
    result = SyntheticEligibilityEngine().evaluate(
        evaluation=evaluation(SyntheticEligibilityPredicate.CONTEXT_COMPLETE_ALPHA),
        safety_decision=safety(),
        knowledge_pack=knowledge_pack("alpha"),
        policy=SYNTHETIC_ELIGIBILITY_POLICY,
        environment=Environment.TEST,
    )
    assert result.outcome is SyntheticEligibilityOutcome.SYNTHETIC_CLARIFICATION_REQUIRED
    assert result.reason_codes == (SyntheticEligibilityReason.SYNTHETIC_NO_RULE_MATCH,)
    assert result.candidates == ()


@pytest.mark.parametrize("drift", ["evaluation", "safety", "pack", "policy"])
def test_result_validation_rejects_every_cross_artifact_drift(drift: str) -> None:
    evaluated = evaluation(
        SyntheticEligibilityPredicate.CONTEXT_COMPLETE_ALPHA,
        SyntheticEligibilityPredicate.INCLUDE_ALPHA,
    )
    safety_result = safety()
    pack = knowledge_pack("alpha")
    policy = SYNTHETIC_ELIGIBILITY_POLICY
    result = SyntheticEligibilityEngine().evaluate(
        evaluation=evaluated,
        safety_decision=safety_result,
        knowledge_pack=pack,
        policy=policy,
        environment=Environment.TEST,
    )
    if drift == "evaluation":
        evaluated = replace(evaluated, context_snapshot_hash="d" * 64)
    elif drift == "safety":
        safety_result = replace(safety_result, created_at=SAFETY_TIME - timedelta(seconds=1))
    elif drift == "pack":
        pack = knowledge_pack("alpha", "beta")
    else:
        policy = SyntheticEligibilityPolicy.create(
            policy_id="syn_selfcare_eligibility_fixture",
            policy_version="engineering.v2",
            effective_at=datetime(2026, 10, 31, tzinfo=UTC),
            expires_at=datetime(2027, 10, 31, tzinfo=UTC),
            state=SyntheticEligibilityPolicyState.TEST_ONLY_ACTIVE,
            rules=policy.rules,
        )

    with pytest.raises(EligibilityContractError) as caught:
        validate_synthetic_eligibility_result(
            evaluation=evaluated,
            safety_decision=safety_result,
            knowledge_pack=pack,
            policy=policy,
            result=result,
        )
    assert caught.value.code is EligibilityContractCode.IDENTITY_MISMATCH
