"""Consent-first orchestration for grounded wellness guidance."""

from collections.abc import Callable
from typing import Protocol

from app.modules.consent.domain import (
    ConsentPurpose,
    ConsentScope,
    ConsentSubjectType,
    NoticeVersion,
)
from app.modules.self_care.guidance_contracts import (
    GuidanceAnswer,
    GuidanceOutcome,
    GuidanceProvider,
    GuidanceProviderRequest,
    GuidanceQuestion,
)
from app.modules.self_care.guidance_policy import GuidancePolicy, GuidancePolicyError
from app.shared.security import ActorContext
from app.shared.types import OpaqueId


class GuidanceConsentVerifier(Protocol):
    async def has_active_consent(
        self,
        *,
        subject_type: ConsentSubjectType,
        subject_id: OpaqueId,
        purpose: ConsentPurpose,
        required_scope: ConsentScope,
        notice_version: NoticeVersion,
    ) -> bool: ...


class GuidanceService:
    def __init__(
        self,
        *,
        consent: GuidanceConsentVerifier,
        provider_factory: Callable[[], GuidanceProvider],
        policy: GuidancePolicy,
    ) -> None:
        self._consent = consent
        self._provider_factory = provider_factory
        self._policy = policy

    async def answer(self, question: GuidanceQuestion, actor: ActorContext) -> GuidanceAnswer:
        if not actor.is_authenticated or actor.actor_id is None:
            return self._empty(GuidanceOutcome.REJECTED)
        if not self._policy.supports(question):
            return self._empty(GuidanceOutcome.OUT_OF_SCOPE)
        allowed = await self._consent.has_active_consent(
            subject_type=ConsentSubjectType.ACTOR,
            subject_id=actor.actor_id,
            purpose=ConsentPurpose.EXTERNAL_AI_PROCESSING,
            required_scope=ConsentScope(("ayurvedic_guidance",)),
            notice_version=NoticeVersion("external-ai-v1"),
        )
        if not allowed:
            return self._empty(GuidanceOutcome.CONSENT_REQUIRED)
        try:
            result = await self._provider_factory().generate(
                GuidanceProviderRequest(question=question.text)
            )
            validated = self._policy.validate_result(result)
        except GuidancePolicyError:
            return self._empty(GuidanceOutcome.REJECTED)
        except Exception:
            return self._empty(GuidanceOutcome.UNAVAILABLE)
        return GuidanceAnswer(
            outcome=GuidanceOutcome.ANSWERED,
            answer=validated.answer,
            citations=validated.citations,
            retrieved_at=validated.retrieved_at,
        )

    @staticmethod
    def _empty(outcome: GuidanceOutcome) -> GuidanceAnswer:
        return GuidanceAnswer(outcome=outcome, answer=None, citations=(), retrieved_at=None)


__all__ = ["GuidanceConsentVerifier", "GuidanceService"]
