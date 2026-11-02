"""Strict local/test-only transport for the synthetic MannSetu preview."""

from typing import Literal, Self

from fastapi import APIRouter, Response
from pydantic import BaseModel, ConfigDict, model_validator

from app.modules.engineering_mannsetu_demo.application import (
    EngineeringMannSetuDemoService,
    EngineeringMannSetuPreviewResult,
)


class EngineeringMannSetuPreviewView(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    classification: Literal["ENGINEERING_SYNTHETIC"]
    authority: Literal["ENGINEERING_ONLY"]
    verification: Literal["UNVERIFIED"]
    extraction_status: Literal["SYNTHETIC_PARSED"]
    extractor_signal: Literal["SYN_MH_SIGNAL_ALPHA"]
    backstop_outcome: Literal["SYNTHETIC_MATCHED"]
    backstop_signal: Literal["SYN_MH_SIGNAL_DELTA"]
    precedence: Literal["SYNTHETIC_OVERRIDE"]
    route: Literal["SYNTHETIC_ROUTE_GAMMA"]
    reason_code: Literal["SYN_MH_POLICY_REASON_DELTA"]
    policy_state: Literal["TEST_ONLY_ENABLED"]
    clinical_meaning_assigned: Literal[False]
    mental_health_assessment_performed: Literal[False]
    patient_data_processed: Literal[False]
    resource_contacts_available: Literal[False]
    referral_created: Literal[False]
    external_delivery: Literal[False]
    notice: str

    @model_validator(mode="after")
    def validate_notice(self) -> Self:
        lowered = self.notice.casefold()
        required = (
            "synthetic engineering symbols only",
            "no mental-health assessment is performed",
            "no clinical meaning is assigned",
            "no resource, referral, or external delivery is available",
        )
        if len(self.notice) > 320 or any(token not in lowered for token in required):
            raise ValueError("invalid engineering notice")
        return self


def build_engineering_mannsetu_demo_router(*, service: EngineeringMannSetuDemoService) -> APIRouter:
    router = APIRouter(tags=["engineering-mannsetu-demo"])

    @router.get(
        "/engineering-demo/mannsetu-preview",
        response_model=EngineeringMannSetuPreviewView,
    )
    async def read_engineering_mannsetu_preview(
        response: Response,
    ) -> EngineeringMannSetuPreviewResult:
        response.headers["Cache-Control"] = "no-store"
        return service.project()

    return router
