"""Strict provider-neutral grounded-guidance contracts."""

from datetime import UTC, datetime, timedelta

import pytest

from app.modules.self_care.guidance_contracts import (
    GuidanceAnswer,
    GuidanceCitation,
    GuidanceOutcome,
    GuidanceProviderRequest,
    GuidanceProviderResult,
    GuidanceQuestion,
    SourceAnnotation,
)

NOW = datetime(2026, 11, 3, 12, tzinfo=UTC)


def test_question_and_provider_request_are_bounded_and_contain_no_patient_context() -> None:
    question = GuidanceQuestion(text="What are gentle ways to support hydration?")
    request = GuidanceProviderRequest(question=question.text)

    assert request.question == question.text
    assert request.__dataclass_fields__.keys() == {"question"}
    with pytest.raises(ValueError):
        GuidanceQuestion(text="x" * 1001)
    with pytest.raises(ValueError):
        GuidanceQuestion(text="   ")


@pytest.mark.parametrize(
    "url",
    ("http://who.int/advice", "https://user@who.int/advice", "https://who.int/#fragment"),
)
def test_citations_require_clean_https_urls(url: str) -> None:
    with pytest.raises(ValueError):
        GuidanceCitation(title="Official source", url=url)


def test_result_rejects_duplicate_or_overlapping_annotations() -> None:
    citation = GuidanceCitation(title="WHO", url="https://who.int/advice")
    with pytest.raises(ValueError):
        GuidanceProviderResult(
            answer="Drink water regularly.",
            citations=(citation,),
            annotations=(
                SourceAnnotation(start=0, end=11, citation_index=0),
                SourceAnnotation(start=5, end=20, citation_index=0),
            ),
            retrieved_at=NOW,
        )


def test_result_normalizes_aware_timestamps_and_rejects_naive_time() -> None:
    citation = GuidanceCitation(title="WHO", url="https://who.int/advice")
    result = GuidanceProviderResult(
        answer="Drink water regularly.",
        citations=(citation,),
        annotations=(SourceAnnotation(start=0, end=11, citation_index=0),),
        retrieved_at=NOW.astimezone(timezone := UTC),
    )
    assert result.retrieved_at.tzinfo is timezone
    with pytest.raises(ValueError):
        GuidanceProviderResult(
            answer=result.answer,
            citations=result.citations,
            annotations=result.annotations,
            retrieved_at=(NOW + timedelta()).replace(tzinfo=None),
        )


def test_answer_never_carries_content_for_non_answered_outcomes() -> None:
    with pytest.raises(ValueError):
        GuidanceAnswer(
            outcome=GuidanceOutcome.REJECTED,
            answer="raw model output",
            citations=(),
            retrieved_at=None,
        )
    with pytest.raises(TypeError):
        GuidanceAnswer(
            outcome=GuidanceOutcome.ANSWERED,
            answer="bounded",
            citations=("not-a-citation",),  # type: ignore[arg-type]
            retrieved_at=NOW,
        )
