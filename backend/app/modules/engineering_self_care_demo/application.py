"""Deterministic, content-free P9-to-P15 engineering demonstration."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from app.config.settings import Environment
from app.modules.safety.contracts import SyntheticSafetyInput, SyntheticSignal
from app.modules.safety.domain import SafetyDecision
from app.modules.safety.engine import SyntheticSafetyEngine
from app.modules.safety.policies import build_synthetic_policy_registry
from app.modules.safety.synthetic import SYNTHETIC_RULE_SET
from app.modules.self_care.contracts import (
    SYNTHETIC_KNOWLEDGE_CONTRACT_VERSION,
    SyntheticGuidancePlaceholder,
    SyntheticKnowledgeItem,
    SyntheticKnowledgePackState,
    SyntheticKnowledgeTag,
    create_synthetic_knowledge_pack,
)
from app.modules.self_care.eligibility import (
    EligibilityContractCode,
    EligibilityContractError,
    SyntheticEligibilityEngine,
    SyntheticEligibilityEvaluation,
    SyntheticEligibilityOutcome,
    SyntheticEligibilityPredicate,
    SyntheticEligibilityReason,
)
from app.modules.self_care.synthetic_eligibility import SYNTHETIC_ELIGIBILITY_POLICY

_DEMO_TIME = datetime(2026, 11, 1, 12, tzinfo=UTC)


@dataclass(frozen=True, slots=True)
class EngineeringSelfCarePreviewResult:
    classification: str
    authority: str
    verification: str
    knowledge_pack_state: str
    knowledge_item_review_state: str
    source_verification: str
    placeholder_token: str
    candidate_outcome: str
    candidate_reason: str
    candidate_count: int
    blocked_outcome: str
    blocked_reason: str
    blocked_candidate_count: int
    safety_block_preserved: bool
    clinical_eligibility_established: bool
    guidance_text_available: bool
    guidance_display_authorized: bool
    rag_invoked: bool
    patient_data_processed: bool
    external_delivery: bool
    notice: str


class EngineeringSelfCareDemoService:
    """Compose reviewed safety and self-care mechanics over fixed toy symbols."""

    def __init__(self, *, environment: Environment) -> None:
        if type(environment) is not Environment:
            raise TypeError("environment must be an Environment")
        self._environment = environment

    def project(self) -> EngineeringSelfCarePreviewResult:
        if self._environment not in {Environment.LOCAL, Environment.TEST}:
            raise EligibilityContractError(EligibilityContractCode.PROTECTED_ENVIRONMENT)
        item = SyntheticKnowledgeItem(
            guidance_id="syn_selfcare_guidance_alpha",
            version="engineering.v1",
            placeholder_token=SyntheticGuidancePlaceholder.ALPHA,
            source_id="syn_selfcare_source_alpha",
            source_version="engineering.v1",
            source_hash="a" * 64,
            tags=(SyntheticKnowledgeTag.ALPHA,),
        )
        pack = create_synthetic_knowledge_pack(
            pack_id="syn_selfcare_pack_fixture",
            pack_version="engineering.v1",
            schema_version=SYNTHETIC_KNOWLEDGE_CONTRACT_VERSION,
            state=SyntheticKnowledgePackState.TEST_ONLY_UNAPPROVED,
            created_at=_DEMO_TIME - timedelta(days=1),
            items=(item,),
        )
        evaluation = SyntheticEligibilityEvaluation(
            evaluation_id="syn_selfcare_eligibility_evaluation_alpha",
            context_snapshot_hash="c" * 64,
            predicates=(
                SyntheticEligibilityPredicate.CONTEXT_COMPLETE_ALPHA,
                SyntheticEligibilityPredicate.INCLUDE_ALPHA,
            ),
            evaluated_at=_DEMO_TIME,
        )
        candidate_safety = self._safety(SyntheticSignal.SYNTHETIC_SELF_CARE_A)
        blocked_safety = self._safety(
            SyntheticSignal.SYNTHETIC_SELF_CARE_A,
            SyntheticSignal.SYNTHETIC_OVERRIDE_A,
        )
        engine = SyntheticEligibilityEngine()
        candidate = engine.evaluate(
            evaluation=evaluation,
            safety_decision=candidate_safety,
            knowledge_pack=pack,
            policy=SYNTHETIC_ELIGIBILITY_POLICY,
            environment=self._environment,
        )
        blocked = engine.evaluate(
            evaluation=evaluation,
            safety_decision=blocked_safety,
            knowledge_pack=pack,
            policy=SYNTHETIC_ELIGIBILITY_POLICY,
            environment=self._environment,
        )
        if (
            candidate.outcome is not SyntheticEligibilityOutcome.SYNTHETIC_ENGINEERING_CANDIDATE
            or candidate.reason_codes != (SyntheticEligibilityReason.SYNTHETIC_RULE_MATCH,)
            or len(candidate.candidates) != 1
            or candidate.candidates[0].guidance_id != item.guidance_id
            or candidate.candidates[0].guidance_version != item.version
            or blocked.outcome is not SyntheticEligibilityOutcome.SYNTHETIC_BLOCKED
            or blocked.reason_codes != (SyntheticEligibilityReason.SYNTHETIC_SAFETY_BLOCK,)
            or blocked.candidates
        ):
            raise RuntimeError("synthetic self-care composition invariant failed")
        return EngineeringSelfCarePreviewResult(
            classification=candidate.classification.value,
            authority=candidate.authority.value,
            verification=candidate.verification.value,
            knowledge_pack_state=pack.state.value,
            knowledge_item_review_state=item.review_state.value,
            source_verification=item.verification.value,
            placeholder_token=item.placeholder_token.value,
            candidate_outcome=candidate.outcome.value,
            candidate_reason=candidate.reason_codes[0].value,
            candidate_count=len(candidate.candidates),
            blocked_outcome=blocked.outcome.value,
            blocked_reason=blocked.reason_codes[0].value,
            blocked_candidate_count=len(blocked.candidates),
            safety_block_preserved=True,
            clinical_eligibility_established=False,
            guidance_text_available=False,
            guidance_display_authorized=False,
            rag_invoked=False,
            patient_data_processed=False,
            external_delivery=False,
            notice=(
                "Synthetic engineering placeholders only. No clinical eligibility is established, "
                "no guidance text is available or authorized for display, and no RAG, patient-data "
                "processing, or external delivery occurs."
            ),
        )

    def _safety(self, *signals: SyntheticSignal) -> SafetyDecision:
        return SyntheticSafetyEngine(
            registry=build_synthetic_policy_registry(),
            rule_set=SYNTHETIC_RULE_SET,
            clock=lambda: _DEMO_TIME - timedelta(seconds=1),
        ).evaluate(
            synthetic_input=SyntheticSafetyInput(
                signals=(SyntheticSignal.SYNTHETIC_COMPLETE_A, *signals)
            ),
            environment=self._environment,
        )
