"""Consent-first guidance orchestration."""

from datetime import UTC, datetime

from app.modules.consent.domain import (
    ConsentPurpose,
    ConsentScope,
    ConsentSubjectType,
    NoticeVersion,
)
from app.modules.self_care.guidance_contracts import (
    GuidanceCitation,
    GuidanceOutcome,
    GuidanceProviderRequest,
    GuidanceProviderResult,
    GuidanceQuestion,
    SourceAnnotation,
)
from app.modules.self_care.guidance_policy import GuidancePolicy
from app.modules.self_care.guidance_service import GuidanceService
from app.shared.security import ActorContext
from app.shared.types import OpaqueId

NOW = datetime(2026, 11, 3, 12, tzinfo=UTC)


class ConsentVerifier:
    def __init__(self, allowed: bool) -> None:
        self.allowed = allowed
        self.calls: list[dict[str, object]] = []

    async def has_active_consent(self, **values: object) -> bool:
        self.calls.append(values)
        return self.allowed


class Provider:
    def __init__(self, outcome: GuidanceProviderResult | Exception) -> None:
        self.outcome = outcome
        self.requests: list[GuidanceProviderRequest] = []

    async def generate(self, request: GuidanceProviderRequest) -> GuidanceProviderResult:
        self.requests.append(request)
        if isinstance(self.outcome, Exception):
            raise self.outcome
        return self.outcome


def provider_result(
    answer: str = "Gentle hydration habits may support general wellbeing.",
) -> GuidanceProviderResult:
    return GuidanceProviderResult(
        answer=answer,
        citations=(GuidanceCitation(title="WHO", url="https://who.int/advice"),),
        annotations=(SourceAnnotation(start=0, end=6, citation_index=0),),
        retrieved_at=NOW,
    )


def actor() -> ActorContext:
    return ActorContext(actor_id=OpaqueId.new(), actor_type="PATIENT", is_authenticated=True)


async def test_missing_consent_constructs_no_provider_and_uses_exact_consent_contract() -> None:
    consent = ConsentVerifier(False)
    constructions = 0

    def factory() -> Provider:
        nonlocal constructions
        constructions += 1
        return Provider(provider_result())

    current = actor()
    answer = await GuidanceService(
        consent=consent,
        provider_factory=factory,
        policy=GuidancePolicy(("who.int",)),
    ).answer(GuidanceQuestion(text="How can I support hydration?"), current)

    assert answer.outcome is GuidanceOutcome.CONSENT_REQUIRED
    assert constructions == 0
    assert consent.calls == [
        {
            "subject_type": ConsentSubjectType.ACTOR,
            "subject_id": current.actor_id,
            "purpose": ConsentPurpose.EXTERNAL_AI_PROCESSING,
            "required_scope": ConsentScope(("ayurvedic_guidance",)),
            "notice_version": NoticeVersion("external-ai-v1"),
        }
    ]


async def test_active_consent_produces_one_post_validated_answer() -> None:
    consent = ConsentVerifier(True)
    provider = Provider(provider_result())
    answer = await GuidanceService(
        consent=consent,
        provider_factory=lambda: provider,
        policy=GuidancePolicy(("who.int",)),
    ).answer(GuidanceQuestion(text="How can I support hydration?"), actor())

    assert answer.outcome is GuidanceOutcome.ANSWERED
    assert answer.answer == provider_result().answer
    assert len(provider.requests) == 1


async def test_provider_failure_or_unsafe_output_never_returns_raw_text() -> None:
    for outcome, expected in (
        (RuntimeError("secret raw provider error"), GuidanceOutcome.UNAVAILABLE),
        (provider_result("This is a guaranteed cure."), GuidanceOutcome.REJECTED),
    ):
        provider = Provider(outcome)

        def factory(provider: Provider = provider) -> Provider:
            return provider

        answer = await GuidanceService(
            consent=ConsentVerifier(True),
            provider_factory=factory,
            policy=GuidancePolicy(("who.int",)),
        ).answer(GuidanceQuestion(text="How can I support hydration?"), actor())
        assert answer.outcome is expected
        assert answer.answer is None
        assert "secret" not in repr(answer)
