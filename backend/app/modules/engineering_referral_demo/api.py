"""Strict local/test-only transport for P13 engineering discovery."""

from typing import Literal, Self

from fastapi import APIRouter, Response
from pydantic import BaseModel, ConfigDict, model_validator

from app.modules.engineering_referral_demo.application import (
    EngineeringReferralDemoService,
    EngineeringReferralDiscoveryResult,
)


class EngineeringReferralDiscoveryView(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    classification: Literal["ENGINEERING_SYNTHETIC"]
    authority: Literal["ENGINEERING_ONLY"]
    route_disposition: Literal["SYMBOLIC_MATCH"]
    route_reason: Literal["EXACT_SYMBOLIC_MATCH"]
    service_code: Literal["syn_service_college_demo"]
    provider_display_name: Literal["Synthetic College Demo Provider"]
    provider_service_code: Literal["syn_service_college_demo"]
    provider_verification: Literal["UNVERIFIED"]
    resource_display_name: Literal["Synthetic College Demo Resource"]
    resource_code: Literal["syn_resource_type_college_demo"]
    resource_verification: Literal["UNVERIFIED"]
    source_verification: Literal["UNVERIFIED"]
    contacts_available: Literal[False]
    provider_selected: Literal[False]
    referral_state_model: Literal["OFFERED"]
    referral_created: Literal[False]
    sharing_consent: Literal["NOT_REQUESTED"]
    external_delivery: Literal[False]
    notification_delivery: Literal[False]
    notice: str

    @model_validator(mode="after")
    def validate_notice(self) -> Self:
        lowered = self.notice.casefold()
        required = (
            "synthetic",
            "unverified",
            "no provider is selected",
            "no referral is created",
            "no data is shared or delivered",
        )
        if len(self.notice) > 256 or any(token not in lowered for token in required):
            raise ValueError("invalid engineering notice")
        return self


def build_engineering_referral_demo_router(*, service: EngineeringReferralDemoService) -> APIRouter:
    router = APIRouter(tags=["engineering-referral-demo"])

    @router.get(
        "/engineering-demo/referral-discovery",
        response_model=EngineeringReferralDiscoveryView,
    )
    async def read_engineering_referral_discovery(
        response: Response,
    ) -> EngineeringReferralDiscoveryResult:
        response.headers["Cache-Control"] = "no-store"
        return service.project()

    return router
