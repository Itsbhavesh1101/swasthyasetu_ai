"""Authorized local/test-only HTTP surface for the synthetic demo projection."""

import re
from datetime import UTC, datetime
from typing import Annotated, Literal, Self
from uuid import UUID

from fastapi import APIRouter, Header, Request, Response
from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from app.api.security.bearer import parse_bearer
from app.modules.clinical_intake.contracts import ReadIntakeCapability
from app.modules.consent.domain import ConsentPurpose, ConsentScope, ConsentSubjectType
from app.modules.consent.public import CONSENT_CHECK
from app.modules.encounters.domain import EncounterType
from app.modules.encounters.public import ENCOUNTERS_READ
from app.modules.engineering_demo.application import DemoResult, EngineeringDemoService
from app.modules.sessions.public import SESSIONS_VALIDATE
from app.shared.errors import ApplicationError, ErrorCode
from app.shared.types import OpaqueId


class DemoSectionView(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    section_id: Literal["CHIEF_COMPLAINT"]
    readiness: Literal["UNVERIFIED"]
    labels: tuple[Literal["SYNTHETIC_PAIN"], ...]
    review_required: bool

    @model_validator(mode="after")
    def validate_section(self) -> Self:
        if self.labels != ("SYNTHETIC_PAIN",) or self.review_required:
            raise ValueError("invalid synthetic summary section")
        return self


class DemoSafetyView(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    route: Literal[
        "EMERGENCY",
        "PRIORITY_REVIEW",
        "ROUTINE_CARE",
        "SUPPORTED_SELF_CARE",
        "CLARIFICATION_REQUIRED",
    ]
    reason_codes: tuple[str, ...]
    policy_id: Literal["synthetic-physical-safety-metadata"]
    policy_version: Literal["engineering.1"]
    requires_clarification: bool
    blocks_self_care: bool
    created_at: datetime

    @field_validator("reason_codes")
    @classmethod
    def validate_reason_codes(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if (
            not 1 <= len(value) <= 16
            or value != tuple(sorted(set(value)))
            or any(
                re.fullmatch(r"SYNTHETIC_[A-Z0-9]+(?:_[A-Z0-9]+)*", item) is None for item in value
            )
        ):
            raise ValueError("invalid synthetic reason codes")
        return value

    @model_validator(mode="after")
    def validate_decision(self) -> Self:
        if self.created_at.tzinfo is None or self.created_at.utcoffset() is None:
            raise ValueError("decision timestamp must be timezone-aware")
        if self.created_at.utcoffset() != UTC.utcoffset(self.created_at):
            raise ValueError("decision timestamp must be UTC")
        if self.route == "CLARIFICATION_REQUIRED":
            valid_flags = self.requires_clarification and self.blocks_self_care
        else:
            valid_flags = not self.requires_clarification and (
                (self.route == "SUPPORTED_SELF_CARE") != self.blocks_self_care
            )
        if not valid_flags:
            raise ValueError("invalid synthetic route flags")
        return self


class DemoResultView(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    intake_id: UUID
    encounter_id: UUID
    status: Literal["SYNTHETIC_PREVIEW", "ABSTAINED"]
    classification: Literal["ENGINEERING_ONLY"]
    extracted_label: Literal["SYNTHETIC_PAIN"] | None
    verification_state: Literal["AI_EXTRACTED_UNCONFIRMED"] | None
    safety_decision: DemoSafetyView | None
    summary_sections: tuple[DemoSectionView, ...]
    notice: str

    @model_validator(mode="after")
    def validate_result_state(self) -> Self:
        preview = self.status == "SYNTHETIC_PREVIEW"
        if preview != (self.extracted_label == "SYNTHETIC_PAIN") or preview != (
            self.verification_state == "AI_EXTRACTED_UNCONFIRMED"
        ):
            raise ValueError("invalid synthetic result state")
        if preview != (self.safety_decision is not None) or preview != (
            len(self.summary_sections) == 1
        ):
            raise ValueError("invalid synthetic result state")
        if not self.notice or len(self.notice) > 256:
            raise ValueError("invalid synthetic result notice")
        return self


def build_engineering_demo_router(
    *, intake_reader: ReadIntakeCapability, service: EngineeringDemoService
) -> APIRouter:
    router = APIRouter(tags=["engineering-demo"])

    @router.get("/engineering-demo/intakes/{intake_id}/result", response_model=DemoResultView)
    async def read_demo_result(
        intake_id: UUID,
        request: Request,
        response: Response,
        authorization: Annotated[str | None, Header()] = None,
    ) -> DemoResult:
        response.headers["Cache-Control"] = "no-store"
        try:
            intake = await intake_reader.get_intake(OpaqueId(intake_id))
        except ApplicationError as error:
            if error.code is not ErrorCode.RESOURCE_NOT_FOUND:
                raise
            raise ApplicationError(
                code=ErrorCode.AUTHENTICATION_REQUIRED,
                message="A valid session bearer token is required.",
            ) from error
        encounter = await request.app.state.capability_registry.resolve(
            ENCOUNTERS_READ
        ).get_encounter(intake.encounter_id)
        session = await request.app.state.capability_registry.resolve(
            SESSIONS_VALIDATE
        ).validate_session(
            session_id=encounter.session_id,
            session_token=parse_bearer(authorization),
        )
        await request.app.state.capability_registry.resolve(CONSENT_CHECK).require_consent(
            subject_type=ConsentSubjectType.SESSION,
            subject_id=session.session_id,
            purpose=ConsentPurpose.GENERAL_PRODUCT_USE,
            required_scope=ConsentScope(("clinical_intake",)),
        )
        if encounter.patient_id is not None or encounter.encounter_type not in {
            EncounterType.GENERAL_INTAKE,
            EncounterType.KIOSK_INTAKE,
        }:
            raise ApplicationError(
                code=ErrorCode.AUTHORIZATION_DENIED,
                message="This intake is not available in the synthetic demo.",
            )
        return await service.project(intake)

    return router
