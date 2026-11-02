"""Strict local/test-only transport for the P11 engineering receipt."""

from typing import Literal, Self

from fastapi import APIRouter, Response
from pydantic import BaseModel, ConfigDict, model_validator

from app.modules.engineering_document_demo.application import (
    EngineeringDocumentDemoService,
    EngineeringDocumentResult,
)


class EngineeringDocumentResultView(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    status: Literal["NEEDS_REVIEW"]
    classification: Literal["ENGINEERING_ONLY"]
    ingestion_disposition: Literal["SYNTHETIC_COMPATIBLE"]
    lifecycle: tuple[
        Literal["UPLOADED"],
        Literal["VALIDATING"],
        Literal["ACCEPTED"],
        Literal["QUEUED"],
        Literal["PROCESSING"],
        Literal["NEEDS_REVIEW"],
    ]
    processing_status: Literal["SUCCEEDED"]
    processed_pages: Literal[1]
    provider: Literal["engineering.fixture"]
    external_egress: Literal[False]
    document_type: Literal["LAB_REPORT"]
    classification_disposition: Literal["SELECTED"]
    classification_reason: Literal["EXACT_SYNTHETIC_LABEL"]
    processor_id: Literal["LabReportProcessor"]
    processor_version: Literal["v1"]
    processor_disposition: Literal["NOOP_ABSTAIN"]
    candidate_disposition: Literal["UNCONFIRMED"]
    evidence_references: Literal[1]
    structural_match: Literal["STRUCTURALLY_MATCHED_UNCONFIRMED"]
    source_access: Literal["NOT_VERIFIED"]
    confidence: Literal["UNKNOWN"]
    notice: str

    @model_validator(mode="after")
    def validate_notice(self) -> Self:
        lowered = self.notice.casefold()
        required = ("synthetic", "no file", "no medical value", "no clinical decision")
        if len(self.notice) > 256 or any(token not in lowered for token in required):
            raise ValueError("invalid engineering notice")
        return self


def build_engineering_document_demo_router(*, service: EngineeringDocumentDemoService) -> APIRouter:
    router = APIRouter(tags=["engineering-document-demo"])

    @router.get(
        "/engineering-demo/document-review",
        response_model=EngineeringDocumentResultView,
    )
    async def read_engineering_document_review(response: Response) -> EngineeringDocumentResult:
        response.headers["Cache-Control"] = "no-store"
        return service.project()

    return router
