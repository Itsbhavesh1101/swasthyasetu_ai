"""Authorized patient profile and clinical-fact HTTP APIs."""

import base64
import json
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, Response, status
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.api.security.authorization import get_actor_context, require_self_subject
from app.modules.identity.authorization import PATIENT_READ_SELF, PATIENT_WRITE_SELF
from app.modules.identity.public import IDENTITY_AUTHORIZE
from app.modules.patients.clinical import ClinicalFact, FactType, clinical_fact_label
from app.modules.patients.contracts import (
    CreatePatientCapability,
    FactCursor,
    ListFactsCapability,
    ReadPatientCapability,
)
from app.modules.patients.domain import Patient, PatientDemographics, PatientStatus
from app.modules.provenance.domain import ProvenanceSourceType, VerificationState
from app.shared.errors import ApplicationError, ErrorCode
from app.shared.types import OpaqueId

_FACT_CURSOR_VERSION = "p5c-fact-v1"


class DemographicsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    date_of_birth: date | None = None
    age_years: int | None = Field(default=None, ge=0)
    administrative_sex: str | None = Field(default=None, min_length=1, max_length=256)
    gender_identity: str | None = Field(default=None, min_length=1, max_length=256)
    pregnancy_status: str | None = Field(default=None, min_length=1, max_length=256)
    location_context: str | None = Field(default=None, min_length=1, max_length=256)

    @field_validator(
        "administrative_sex",
        "gender_identity",
        "pregnancy_status",
        "location_context",
    )
    @classmethod
    def validate_trimmed_text(cls, value: str | None) -> str | None:
        if value is not None and value != value.strip():
            raise ValueError("text values must be trimmed")
        return value


class CreatePatientRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    preferred_language: str | None = Field(default=None, min_length=1, max_length=64)
    demographics: DemographicsRequest | None = None

    @field_validator("preferred_language")
    @classmethod
    def validate_preferred_language(cls, value: str | None) -> str | None:
        if value is not None and value != value.strip():
            raise ValueError("preferred_language must be trimmed")
        return value


class DemographicsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    date_of_birth: date | None
    age_years: int | None
    administrative_sex: str | None
    gender_identity: str | None
    pregnancy_status: str | None
    location_context: str | None


class PatientResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    patient_id: UUID
    status: PatientStatus
    preferred_language: str | None
    demographics: DemographicsResponse | None
    created_at: datetime
    updated_at: datetime


class ProvenanceSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source_type: ProvenanceSourceType
    confidence: Decimal | None
    created_at: datetime


class FactSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")
    fact_id: UUID
    fact_type: FactType
    canonical_label: str
    effective_time: datetime | None
    recorded_at: datetime
    verification_state: VerificationState
    superseded_by_fact_id: UUID | None
    provenance: ProvenanceSummary


class FactListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    items: tuple[FactSummary, ...]
    next_cursor: str | None


def patient_view(patient: Patient) -> PatientResponse:
    demographics = patient.demographics
    return PatientResponse(
        patient_id=patient.patient_id.value,
        status=patient.status,
        preferred_language=patient.preferred_language,
        demographics=(
            None
            if demographics is None
            else DemographicsResponse(
                **{name: getattr(demographics, name) for name in DemographicsResponse.model_fields}
            )
        ),
        created_at=patient.created_at,
        updated_at=patient.updated_at,
    )


def fact_view(fact: ClinicalFact) -> FactSummary:
    return FactSummary(
        fact_id=fact.fact_id.value,
        fact_type=fact.fact_type,
        canonical_label=clinical_fact_label(fact.value),
        effective_time=fact.effective_time,
        recorded_at=fact.recorded_at,
        verification_state=fact.verification_state,
        superseded_by_fact_id=(
            None if fact.superseded_by_fact_id is None else fact.superseded_by_fact_id.value
        ),
        provenance=ProvenanceSummary(
            source_type=fact.provenance.source_type,
            confidence=fact.provenance.confidence,
            created_at=fact.provenance.created_at,
        ),
    )


def encode_fact_cursor(fact: ClinicalFact) -> str:
    occurred_at = fact.effective_time or fact.recorded_at
    value = json.dumps(
        {
            "version": _FACT_CURSOR_VERSION,
            "occurred_at": occurred_at.isoformat(),
            "id": str(fact.fact_id),
        },
        separators=(",", ":"),
        sort_keys=True,
    ).encode()
    return base64.urlsafe_b64encode(value).decode().rstrip("=")


def decode_fact_cursor(value: str | None) -> FactCursor | None:
    if value is None:
        return None
    try:
        raw = base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
        payload: Any = json.loads(raw)
        if not isinstance(payload, dict) or set(payload) != {"version", "occurred_at", "id"}:
            raise ValueError
        if payload["version"] != _FACT_CURSOR_VERSION:
            raise ValueError
        occurred_at = datetime.fromisoformat(payload["occurred_at"])
        if occurred_at.tzinfo is None or occurred_at.utcoffset() is None:
            raise ValueError
        return FactCursor(occurred_at.astimezone(UTC), OpaqueId.parse(payload["id"]))
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        raise ApplicationError(
            code=ErrorCode.VALIDATION_ERROR, message="The pagination cursor is invalid.", cause=exc
        ) from exc


def build_patients_router(
    *,
    creator: CreatePatientCapability,
    reader: ReadPatientCapability,
    facts: ListFactsCapability,
) -> APIRouter:
    router = APIRouter(prefix="/patients", tags=["patients"])

    @router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
    async def create_patient(
        payload: CreatePatientRequest, request: Request, response: Response
    ) -> PatientResponse:
        response.headers["Cache-Control"] = "no-store"
        context = get_actor_context(request)
        authorization = request.app.state.capability_registry.resolve(IDENTITY_AUTHORIZE)
        if context.subject_id is None:
            authorization.require_permission(context, PATIENT_WRITE_SELF)
            raise ApplicationError(
                code=ErrorCode.AUTHORIZATION_DENIED,
                message="The authenticated actor has no trusted patient subject.",
            )
        authorization.require_self_subject(context, PATIENT_WRITE_SELF, context.subject_id)
        demographics = (
            None
            if payload.demographics is None
            else PatientDemographics(**payload.demographics.model_dump())
        )
        return patient_view(
            await creator.create_patient(
                patient_id=context.subject_id,
                preferred_language=payload.preferred_language,
                demographics=demographics,
            )
        )

    @router.get(
        "/{patient_id}",
        response_model=PatientResponse,
        dependencies=[Depends(require_self_subject(PATIENT_READ_SELF, "patient_id"))],
    )
    async def get_patient(patient_id: UUID, response: Response) -> PatientResponse:
        response.headers["Cache-Control"] = "no-store"
        return patient_view(await reader.get_patient(OpaqueId(patient_id)))

    @router.get(
        "/{patient_id}/facts",
        response_model=FactListResponse,
        dependencies=[Depends(require_self_subject(PATIENT_READ_SELF, "patient_id"))],
    )
    async def list_facts(
        patient_id: UUID,
        response: Response,
        fact_type: Annotated[FactType | None, Query()] = None,
        verification_state: Annotated[VerificationState | None, Query()] = None,
        limit: Annotated[int, Query(ge=1, le=100)] = 50,
        cursor: Annotated[str | None, Query(min_length=1, max_length=1024)] = None,
    ) -> FactListResponse:
        response.headers["Cache-Control"] = "no-store"
        page = await facts.list_facts(
            patient_id=OpaqueId(patient_id),
            fact_type=fact_type,
            verification_state=verification_state,
            cursor=decode_fact_cursor(cursor),
            limit=limit,
        )
        return FactListResponse(
            items=tuple(fact_view(item) for item in page.items),
            next_cursor=(
                encode_fact_cursor(page.items[-1]) if page.has_more and page.items else None
            ),
        )

    return router
