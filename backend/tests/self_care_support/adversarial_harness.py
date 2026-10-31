"""Offline P9-to-P15 composition helper using symbolic engineering fixtures only."""

from datetime import datetime, timedelta

from app.config.settings import Environment
from app.modules.safety.contracts import SyntheticSafetyInput, SyntheticSignal
from app.modules.safety.engine import SyntheticSafetyEngine
from app.modules.safety.policies import build_synthetic_policy_registry
from app.modules.safety.synthetic import SYNTHETIC_RULE_SET
from app.modules.self_care.contracts import (
    SYNTHETIC_KNOWLEDGE_CONTRACT_VERSION,
    SyntheticGuidancePlaceholder,
    SyntheticKnowledgeItem,
    SyntheticKnowledgePack,
    SyntheticKnowledgePackState,
    SyntheticKnowledgeTag,
    create_synthetic_knowledge_pack,
)
from app.modules.self_care.eligibility import (
    EligibilityContractCode,
    EligibilityContractError,
    SyntheticEligibilityEngine,
    SyntheticEligibilityEvaluation,
    SyntheticEligibilityPredicate,
    SyntheticEligibilityResult,
)
from app.modules.self_care.synthetic_eligibility import SYNTHETIC_ELIGIBILITY_POLICY

_SOURCE_HASH = "a" * 64
_CONTEXT_HASH = "c" * 64


def _knowledge_pack(*, suffixes: tuple[str, ...], created_at: datetime) -> SyntheticKnowledgePack:
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
            source_hash=_SOURCE_HASH,
            tags=(
                SyntheticKnowledgeTag.ALPHA if suffix == "alpha" else SyntheticKnowledgeTag.BETA,
            ),
        )
        for suffix in suffixes
    )
    return create_synthetic_knowledge_pack(
        pack_id="syn_selfcare_pack_fixture",
        pack_version="engineering.v1",
        schema_version=SYNTHETIC_KNOWLEDGE_CONTRACT_VERSION,
        state=SyntheticKnowledgePackState.TEST_ONLY_UNAPPROVED,
        created_at=created_at,
        items=items,
    )


def run_synthetic_self_care_case(
    *,
    safety_signals: tuple[SyntheticSignal, ...],
    eligibility_predicates: tuple[SyntheticEligibilityPredicate, ...],
    evaluated_at: datetime,
    pack_suffixes: tuple[str, ...] = ("alpha",),
    policy_present: bool = True,
    future_pack: bool = False,
    environment: Environment = Environment.TEST,
) -> SyntheticEligibilityResult:
    """Compose existing detached fixtures; never create clinical or display authority."""

    if type(environment) is not Environment:
        raise EligibilityContractError(EligibilityContractCode.INVALID_TYPE)
    if environment not in {Environment.LOCAL, Environment.TEST}:
        raise EligibilityContractError(EligibilityContractCode.PROTECTED_ENVIRONMENT)

    safety = SyntheticSafetyEngine(
        registry=build_synthetic_policy_registry(),
        rule_set=SYNTHETIC_RULE_SET,
        clock=lambda: evaluated_at - timedelta(seconds=1),
    ).evaluate(
        synthetic_input=SyntheticSafetyInput(signals=safety_signals),
        environment=environment,
    )
    evaluation = SyntheticEligibilityEvaluation(
        evaluation_id="syn_selfcare_eligibility_evaluation_alpha",
        context_snapshot_hash=_CONTEXT_HASH,
        predicates=eligibility_predicates,
        evaluated_at=evaluated_at,
    )
    pack_created_at = (
        evaluated_at + timedelta(seconds=1) if future_pack else evaluated_at - timedelta(days=1)
    )
    return SyntheticEligibilityEngine().evaluate(
        evaluation=evaluation,
        safety_decision=safety,
        knowledge_pack=_knowledge_pack(
            suffixes=pack_suffixes,
            created_at=pack_created_at,
        ),
        policy=SYNTHETIC_ELIGIBILITY_POLICY if policy_present else None,
        environment=environment,
    )


__all__ = ["run_synthetic_self_care_case"]
