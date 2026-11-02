"""Strict local/test-only transport for the synthetic FHIR boundary preview."""

from typing import Literal, Self

from fastapi import APIRouter, Response
from pydantic import BaseModel, ConfigDict, model_validator

from app.modules.engineering_fhir_demo.application import (
    EngineeringFHIRDemoService,
    EngineeringFHIRPreviewResult,
)


class EngineeringFHIRPreviewView(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    classification: Literal["ENGINEERING_SYNTHETIC"]
    authority: Literal["ENGINEERING_ONLY"]
    verification: Literal["UNVERIFIED"]
    fhir_version: Literal["4.0.1"]
    mapping_direction: Literal["EXPORT"]
    mapping_state: Literal["SYNTHETIC_EXPORT_PROJECTION"]
    resource_type: Literal["Observation"]
    structural_validation: Literal["SYNTHETIC_STRUCTURAL_PASS"]
    profile_validation: Literal["SYNTHETIC_UNAVAILABLE"]
    profile_issue: Literal["PROFILE_PACKAGE_UNAVAILABLE"]
    fhir_payload_present: Literal[False]
    patient_data_processed: Literal[False]
    profile_conformance_claimed: Literal[False]
    exchange_authorized: Literal[False]
    external_transport: Literal[False]
    abdm_invoked: Literal[False]
    persistence_written: Literal[False]
    notice: str

    @model_validator(mode="after")
    def validate_notice(self) -> Self:
        lowered = self.notice.casefold()
        required = (
            "synthetic engineering metadata only",
            "structural mechanics are not profile conformance",
            "no fhir payload or patient data is processed",
            "no exchange, external transport, abdm integration, or persistence occurs",
        )
        if len(self.notice) > 384 or any(token not in lowered for token in required):
            raise ValueError("invalid engineering notice")
        return self


def build_engineering_fhir_demo_router(*, service: EngineeringFHIRDemoService) -> APIRouter:
    router = APIRouter(tags=["engineering-fhir-demo"])

    @router.get(
        "/engineering-demo/fhir-preview",
        response_model=EngineeringFHIRPreviewView,
    )
    async def read_engineering_fhir_preview(
        response: Response,
    ) -> EngineeringFHIRPreviewResult:
        response.headers["Cache-Control"] = "no-store"
        return service.project()

    return router
