"""Strict local/test-only transport for the P10 engineering draft."""

from typing import Literal, Self

from fastapi import APIRouter, Response
from pydantic import BaseModel, ConfigDict, model_validator

from app.modules.engineering_summary_demo.application import (
    EngineeringSummaryDemoService,
    EngineeringSummaryResult,
)
from app.modules.summaries.domain import CANONICAL_SECTION_ORDER


class EngineeringSummarySectionView(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    section: Literal[
        "CHIEF_COMPLAINT",
        "HPI",
        "PAST_MEDICAL_HISTORY",
        "PAST_SURGICAL_HISTORY",
        "MEDICATIONS",
        "ALLERGIES",
        "FAMILY_HISTORY",
        "PERSONAL_HISTORY",
        "REVIEW_OF_SYSTEMS",
        "PRIOR_INVESTIGATIONS",
    ]
    readiness: Literal["UNKNOWN", "UNVERIFIED"]
    assertions: tuple[Literal["SYNTHETIC_REPORTED_COMPLAINT"], ...]
    source_kinds: tuple[Literal["P7_PATIENT_REPORTED"], ...]
    conflict_review_required: Literal[False]


class EngineeringSummaryResultView(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    status: Literal["DRAFT"]
    classification: Literal["ENGINEERING_ONLY"]
    review_state: Literal["REVIEW_REQUIRED"]
    freshness: Literal["STALE"]
    affected_sections: tuple[Literal["HPI"]]
    drift_reasons: tuple[Literal["NEW_SOURCE"]]
    source_count: Literal[1]
    sections: tuple[EngineeringSummarySectionView, ...]
    source_access: Literal["NOT_AUTHORIZED"]
    can_edit: Literal[False]
    can_confirm: Literal[False]
    can_reject: Literal[False]
    external_egress: Literal[False]
    notice: str

    @model_validator(mode="after")
    def validate_projection(self) -> Self:
        expected = tuple(section.value for section in CANONICAL_SECTION_ORDER)
        if tuple(section.section for section in self.sections) != expected:
            raise ValueError("invalid section order")
        populated = tuple(section for section in self.sections if section.assertions)
        if (
            len(populated) != 1
            or populated[0].section != "CHIEF_COMPLAINT"
            or populated[0].readiness != "UNVERIFIED"
            or populated[0].assertions != ("SYNTHETIC_REPORTED_COMPLAINT",)
            or populated[0].source_kinds != ("P7_PATIENT_REPORTED",)
            or any(
                section.readiness != "UNKNOWN" or section.assertions or section.source_kinds
                for section in self.sections[1:]
            )
        ):
            raise ValueError("invalid source-backed projection")
        lowered = self.notice.casefold()
        required = ("synthetic", "unknown", "source drift", "no clinical action")
        if len(self.notice) > 256 or any(token not in lowered for token in required):
            raise ValueError("invalid engineering notice")
        return self


def build_engineering_summary_demo_router(*, service: EngineeringSummaryDemoService) -> APIRouter:
    router = APIRouter(tags=["engineering-summary-demo"])

    @router.get(
        "/engineering-demo/summary-review",
        response_model=EngineeringSummaryResultView,
    )
    async def read_engineering_summary_review(response: Response) -> EngineeringSummaryResult:
        response.headers["Cache-Control"] = "no-store"
        return service.project()

    return router
