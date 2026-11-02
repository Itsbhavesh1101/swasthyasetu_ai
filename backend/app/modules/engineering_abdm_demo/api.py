"""Strict local/test-only transport for the synthetic ABDM preview."""

from typing import Literal, Self

from fastapi import APIRouter, Response
from pydantic import BaseModel, ConfigDict, model_validator

from app.modules.engineering_abdm_demo.application import (
    EngineeringABDMDemoService,
    EngineeringABDMPreviewResult,
)


class EngineeringABDMPreviewView(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    classification: Literal["ENGINEERING_SYNTHETIC"]
    authority: Literal["ENGINEERING_ONLY"]
    verification: Literal["UNVERIFIED"]
    mode: Literal["SYNTHETIC_OFFLINE_MOCK"]
    operation: Literal["SYNTHETIC_OPERATION_ALPHA"]
    scripted_state: Literal["SYNTHETIC_REJECTED"]
    scripted_issue: Literal["SYNTHETIC_REJECTED"]
    unknown_state: Literal["SYNTHETIC_UNAVAILABLE"]
    unknown_issue: Literal["SYNTHETIC_UNAVAILABLE"]
    zero_egress: Literal[True]
    official_protocol_adopted: Literal[False]
    abha_identity_processed: Literal[False]
    consent_evaluated: Literal[False]
    fhir_payload_present: Literal[False]
    sandbox_connected: Literal[False]
    patient_data_processed: Literal[False]
    local_intake_accessed: Literal[False]
    local_intake_mutated: Literal[False]
    external_transport: Literal[False]
    persistence_written: Literal[False]
    notice: str

    @model_validator(mode="after")
    def validate_notice(self) -> Self:
        lowered = self.notice.casefold()
        required = (
            "synthetic offline engineering tokens only",
            "no official abdm protocol or abha identity is used",
            "no consent or fhir payload is processed",
            "no sandbox, patient data, local intake, network transport, or persistence is accessed",
        )
        if len(self.notice) > 384 or any(token not in lowered for token in required):
            raise ValueError("invalid engineering notice")
        return self


def build_engineering_abdm_demo_router(*, service: EngineeringABDMDemoService) -> APIRouter:
    router = APIRouter(tags=["engineering-abdm-demo"])

    @router.get(
        "/engineering-demo/abdm-preview",
        response_model=EngineeringABDMPreviewView,
    )
    async def read_engineering_abdm_preview(
        response: Response,
    ) -> EngineeringABDMPreviewResult:
        response.headers["Cache-Control"] = "no-store"
        return service.project()

    return router
