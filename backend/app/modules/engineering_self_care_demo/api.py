"""Strict local/test-only transport for the synthetic self-care preview."""

from typing import Literal, Self

from fastapi import APIRouter, Response
from pydantic import BaseModel, ConfigDict, model_validator

from app.modules.engineering_self_care_demo.application import (
    EngineeringSelfCareDemoService,
    EngineeringSelfCarePreviewResult,
)


class EngineeringSelfCarePreviewView(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    classification: Literal["ENGINEERING_SYNTHETIC"]
    authority: Literal["ENGINEERING_ONLY"]
    verification: Literal["UNVERIFIED"]
    knowledge_pack_state: Literal["TEST_ONLY_UNAPPROVED"]
    knowledge_item_review_state: Literal["TEST_ONLY_UNAPPROVED"]
    source_verification: Literal["UNVERIFIED"]
    placeholder_token: Literal["SYNTHETIC_PLACEHOLDER_ALPHA"]
    candidate_outcome: Literal["SYNTHETIC_ENGINEERING_CANDIDATE"]
    candidate_reason: Literal["SYNTHETIC_RULE_MATCH"]
    candidate_count: Literal[1]
    blocked_outcome: Literal["SYNTHETIC_BLOCKED"]
    blocked_reason: Literal["SYNTHETIC_SAFETY_BLOCK"]
    blocked_candidate_count: Literal[0]
    safety_block_preserved: Literal[True]
    clinical_eligibility_established: Literal[False]
    guidance_text_available: Literal[False]
    guidance_display_authorized: Literal[False]
    rag_invoked: Literal[False]
    patient_data_processed: Literal[False]
    external_delivery: Literal[False]
    notice: str

    @model_validator(mode="after")
    def validate_notice(self) -> Self:
        lowered = self.notice.casefold()
        required = (
            "synthetic engineering placeholders only",
            "no clinical eligibility is established",
            "no guidance text is available or authorized for display",
            "no rag, patient-data processing, or external delivery occurs",
        )
        if len(self.notice) > 384 or any(token not in lowered for token in required):
            raise ValueError("invalid engineering notice")
        return self


def build_engineering_self_care_demo_router(
    *, service: EngineeringSelfCareDemoService
) -> APIRouter:
    router = APIRouter(tags=["engineering-self-care-demo"])

    @router.get(
        "/engineering-demo/self-care-preview",
        response_model=EngineeringSelfCarePreviewView,
    )
    async def read_engineering_self_care_preview(
        response: Response,
    ) -> EngineeringSelfCarePreviewResult:
        response.headers["Cache-Control"] = "no-store"
        return service.project()

    return router
