"""Deterministic query and provider-output guards."""

from datetime import UTC, datetime

import pytest

from app.modules.self_care.guidance_contracts import (
    GuidanceCitation,
    GuidanceProviderResult,
    GuidanceQuestion,
    SourceAnnotation,
)
from app.modules.self_care.guidance_policy import GuidancePolicy, GuidancePolicyError

NOW = datetime(2026, 11, 3, 12, tzinfo=UTC)


def result(
    *, answer: str = "Gentle hydration habits may support general wellbeing.", url: str
) -> GuidanceProviderResult:
    return GuidanceProviderResult(
        answer=answer,
        citations=(GuidanceCitation(title="Official guidance", url=url),),
        annotations=(SourceAnnotation(start=0, end=6, citation_index=0),),
        retrieved_at=NOW,
    )


def test_policy_accepts_only_exact_allowlisted_source_hosts() -> None:
    policy = GuidancePolicy(("who.int", "ayush.gov.in"))
    assert (
        policy.validate_result(result(url="https://who.int/advice"))
        .citations[0]
        .url.endswith("/advice")
    )
    for url in ("https://www.who.int/advice", "https://who.int.attacker.test/advice"):
        with pytest.raises(GuidancePolicyError):
            policy.validate_result(result(url=url))


@pytest.mark.parametrize(
    "question",
    (
        "Diagnose this chest pain",
        "What dosage should I take?",
        "Can this replace emergency care?",
        "What should I give my infant?",
    ),
)
def test_policy_rejects_unsupported_high_risk_questions(question: str) -> None:
    assert not GuidancePolicy(("who.int",)).supports(GuidanceQuestion(text=question))


@pytest.mark.parametrize(
    "answer",
    (
        "This is a guaranteed cure.",
        "Stop your prescribed medication.",
        "Take 500 mg every day.",
        "This replaces emergency care.",
    ),
)
def test_policy_rejects_forbidden_model_claims(answer: str) -> None:
    with pytest.raises(GuidancePolicyError):
        GuidancePolicy(("who.int",)).validate_result(
            result(answer=answer, url="https://who.int/advice")
        )
