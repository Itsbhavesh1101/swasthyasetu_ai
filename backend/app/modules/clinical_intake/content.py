"""Explicit non-production question content used to exercise the P7 flow."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType

from app.modules.clinical_intake.contracts import (
    AnswerType,
    ApprovalState,
    InputMode,
    QuestionDefinition,
    QuestionPack,
    QuestionPackKind,
    QuestionSection,
    Requiredness,
    TextValidation,
)

ENGINEERING_CORE_PACK_ID = "core.intake"
ENGINEERING_CORE_PACK_VERSION = "engineering.1"


@dataclass(frozen=True, slots=True)
class QuestionPresentation:
    prompt: str
    help_text: str | None = None
    option_labels: tuple[tuple[str, str], ...] = ()


ENGINEERING_CORE_PACK = QuestionPack(
    pack_id=ENGINEERING_CORE_PACK_ID,
    version=ENGINEERING_CORE_PACK_VERSION,
    kind=QuestionPackKind.CORE,
    approval_state=ApprovalState.ENGINEERING_APPROVED,
    content_version="engineering.en.1",
    supported_languages=("en",),
    order=0,
    questions=(
        QuestionDefinition(
            question_id="core.chief_complaint",
            question_version="engineering.1",
            section=QuestionSection.CHIEF_COMPLAINT,
            content_key="core.chief_complaint.prompt",
            help_content_key="core.chief_complaint.help",
            answer_type=AnswerType.TEXT,
            requiredness=Requiredness.REQUIRED,
            input_modes=(InputMode.TEXT,),
            validation=TextValidation(min_length=1, max_length=500),
            order=0,
        ),
    ),
)

ENGINEERING_PRESENTATIONS = MappingProxyType(
    {
        (
            ENGINEERING_CORE_PACK_ID,
            ENGINEERING_CORE_PACK_VERSION,
            "core.chief_complaint",
        ): QuestionPresentation(
            prompt="What would you like to share for this intake draft?",
            help_text=(
                "Use your own words. This engineering questionnaire records information only; "
                "it does not diagnose or assess urgency."
            ),
        )
    }
)


def engineering_packs() -> tuple[QuestionPack, ...]:
    """Return the immutable compile-time engineering fixture registration."""
    return (ENGINEERING_CORE_PACK,)
