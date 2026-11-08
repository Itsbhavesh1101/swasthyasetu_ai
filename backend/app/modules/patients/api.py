"""Authorized patient profile and clinical-fact HTTP APIs."""

import base64
import json
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Annotated, Any, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query, Request, Response, status
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.api.security.authorization import get_actor_context, require_self_subject
from app.api.security.patient_authentication import PatientAuthenticator, authenticate_patient
from app.modules.identity.authorization import PATIENT_READ_SELF, PATIENT_WRITE_SELF
from app.modules.identity.public import IDENTITY_AUTHORIZE
from app.modules.patients.clinical import (
    AllergyRecord,
    ClinicalFact,
    ClinicalValue,
    FactSupersession,
    FactType,
    InvestigationRecord,
    MedicationRecord,
    MedicationStatus,
    Observation,
    Problem,
    ProblemStatus,
    ProcedureRecord,
    clinical_fact_label,
)
from app.modules.patients.contracts import (
    CreatePatientCapability,
    FactCursor,
    ListFactsCapability,
    ReadPatientCapability,
    UpdatePatientCapability,
    WritePatientFactCapability,
)
from app.modules.patients.domain import BloodGroup, Patient, PatientDemographics, PatientStatus
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
    height_cm: Decimal | None = Field(default=None, ge=30, le=275, max_digits=5, decimal_places=2)
    weight_kg: Decimal | None = Field(default=None, ge=1, le=700, max_digits=6, decimal_places=2)
    mobile_number: str | None = Field(default=None, pattern=r"^\+[1-9][0-9]{6,14}$")
    blood_group: BloodGroup | None = None
    demo_aadhaar_reference: str | None = Field(default=None, pattern=r"^DEMO-AADHAAR-[0-9]{4}$")

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


class UpdatePatientRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_updated_at: datetime
    preferred_language: str | None = Field(default=None, min_length=1, max_length=64)
    demographics: DemographicsRequest | None = None

    @field_validator("expected_updated_at")
    @classmethod
    def validate_expected_updated_at(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("expected_updated_at must be timezone-aware")
        return value.astimezone(UTC)


class DemographicsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    date_of_birth: date | None
    age_years: int | None
    administrative_sex: str | None
    gender_identity: str | None
    pregnancy_status: str | None
    location_context: str | None
    height_cm: float | None
    weight_kg: float | None
    bmi: float | None
    mobile_number: str | None
    blood_group: BloodGroup | None
    demo_aadhaar_reference: str | None


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
    status: str | None
    superseded_by_fact_id: UUID | None
    provenance: ProvenanceSummary


class PatientFactRequestBase(BaseModel):
    model_config = ConfigDict(extra="forbid")
    effective_time: datetime | None = None

    @field_validator("*", mode="after", check_fields=False)
    @classmethod
    def validate_trimmed_strings(cls, value: object) -> object:
        if isinstance(value, str) and value != value.strip():
            raise ValueError("text values must be trimmed")
        return value

    @field_validator("effective_time")
    @classmethod
    def validate_effective_time(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("effective_time must be timezone-aware")
        return value.astimezone(UTC)


class ProblemFactRequest(PatientFactRequestBase):
    fact_type: Literal[FactType.PROBLEM]
    label: str = Field(min_length=1, max_length=256)
    status: ProblemStatus
    onset: date | None = None
    resolution: date | None = None


class MedicationFactRequest(PatientFactRequestBase):
    fact_type: Literal[FactType.MEDICATION]
    name: str = Field(min_length=1, max_length=256)
    status: MedicationStatus
    dose: Decimal | None = Field(default=None, ge=0)
    dose_unit: str | None = Field(default=None, min_length=1, max_length=128)
    route: str | None = Field(default=None, min_length=1, max_length=128)
    frequency: str | None = Field(default=None, min_length=1, max_length=128)
    start_date: date | None = None
    end_date: date | None = None
    indication: str | None = Field(default=None, min_length=1, max_length=512)


class AllergyFactRequest(PatientFactRequestBase):
    fact_type: Literal[FactType.ALLERGY]
    substance: str = Field(min_length=1, max_length=256)
    status: str = Field(min_length=1, max_length=64)
    reaction: str | None = Field(default=None, min_length=1, max_length=512)
    severity: str | None = Field(default=None, min_length=1, max_length=128)


class ProcedureFactRequest(PatientFactRequestBase):
    fact_type: Literal[FactType.PROCEDURE]
    name: str = Field(min_length=1, max_length=256)
    performed_at: datetime | None = None
    facility: str | None = Field(default=None, min_length=1, max_length=256)
    notes: str | None = Field(default=None, min_length=1, max_length=2000)

    @field_validator("performed_at")
    @classmethod
    def validate_performed_at(cls, value: datetime | None) -> datetime | None:
        return PatientFactRequestBase.validate_effective_time(value)


class ObservationFactRequest(PatientFactRequestBase):
    fact_type: Literal[FactType.OBSERVATION]
    observation_type: str = Field(min_length=1, max_length=256)
    numeric_value: Decimal | None = None
    text_value: str | None = Field(default=None, min_length=1, max_length=2000)
    unit: str | None = Field(default=None, min_length=1, max_length=128)

    @model_validator(mode="after")
    def validate_single_value(self) -> "ObservationFactRequest":
        if (self.numeric_value is None) == (self.text_value is None):
            raise ValueError("exactly one observation value is required")
        return self


class InvestigationFactRequest(PatientFactRequestBase):
    fact_type: Literal[FactType.INVESTIGATION]
    investigation_type: str = Field(min_length=1, max_length=256)
    status: str = Field(min_length=1, max_length=64)
    performed_at: datetime | None = None
    result_summary: str | None = Field(default=None, min_length=1, max_length=2000)

    @field_validator("performed_at")
    @classmethod
    def validate_performed_at(cls, value: datetime | None) -> datetime | None:
        return PatientFactRequestBase.validate_effective_time(value)


PatientFactRequest = Annotated[
    ProblemFactRequest
    | MedicationFactRequest
    | AllergyFactRequest
    | ProcedureFactRequest
    | ObservationFactRequest
    | InvestigationFactRequest,
    Field(discriminator="fact_type"),
]


class SupersedeFactRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_current_id: UUID
    replacement: PatientFactRequest


class FactSupersessionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    superseded: FactSummary
    replacement: FactSummary


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
                date_of_birth=demographics.date_of_birth,
                age_years=demographics.age_years,
                administrative_sex=demographics.administrative_sex,
                gender_identity=demographics.gender_identity,
                pregnancy_status=demographics.pregnancy_status,
                location_context=demographics.location_context,
                height_cm=(
                    None if demographics.height_cm is None else float(demographics.height_cm)
                ),
                weight_kg=(
                    None if demographics.weight_kg is None else float(demographics.weight_kg)
                ),
                bmi=None if demographics.bmi is None else float(demographics.bmi),
                mobile_number=demographics.mobile_number,
                blood_group=demographics.blood_group,
                demo_aadhaar_reference=demographics.demo_aadhaar_reference,
            )
        ),
        created_at=patient.created_at,
        updated_at=patient.updated_at,
    )


def fact_view(fact: ClinicalFact) -> FactSummary:
    status_value = getattr(fact.value, "status", None)
    return FactSummary(
        fact_id=fact.fact_id.value,
        fact_type=fact.fact_type,
        canonical_label=clinical_fact_label(fact.value),
        effective_time=fact.effective_time,
        recorded_at=fact.recorded_at,
        verification_state=fact.verification_state,
        status=None if status_value is None else str(status_value),
        superseded_by_fact_id=(
            None if fact.superseded_by_fact_id is None else fact.superseded_by_fact_id.value
        ),
        provenance=ProvenanceSummary(
            source_type=fact.provenance.source_type,
            confidence=fact.provenance.confidence,
            created_at=fact.provenance.created_at,
        ),
    )


def patient_fact_value(payload: PatientFactRequest) -> ClinicalValue:
    state = VerificationState.PATIENT_CONFIRMED
    if isinstance(payload, ProblemFactRequest):
        return Problem(
            label=payload.label,
            status=payload.status,
            onset=payload.onset,
            resolution=payload.resolution,
            verification_state=state,
        )
    if isinstance(payload, MedicationFactRequest):
        return MedicationRecord(
            name=payload.name,
            status=payload.status,
            dose=payload.dose,
            dose_unit=payload.dose_unit,
            route=payload.route,
            frequency=payload.frequency,
            start_date=payload.start_date,
            end_date=payload.end_date,
            indication=payload.indication,
            verification_state=state,
        )
    if isinstance(payload, AllergyFactRequest):
        return AllergyRecord(
            substance=payload.substance,
            status=payload.status,
            reaction=payload.reaction,
            severity=payload.severity,
            verification_state=state,
        )
    if isinstance(payload, ProcedureFactRequest):
        return ProcedureRecord(
            name=payload.name,
            performed_at=payload.performed_at,
            facility=payload.facility,
            notes=payload.notes,
            verification_state=state,
        )
    if isinstance(payload, ObservationFactRequest):
        return Observation(
            observation_type=payload.observation_type,
            value=(
                payload.numeric_value
                if payload.numeric_value is not None
                else payload.text_value or ""
            ),
            unit=payload.unit,
            effective_at=payload.effective_time,
            verification_state=state,
        )
    if isinstance(payload, InvestigationFactRequest):
        return InvestigationRecord(
            investigation_type=payload.investigation_type,
            status=payload.status,
            performed_at=payload.performed_at,
            result_summary=payload.result_summary,
            verification_state=state,
        )
    raise ValueError("unsupported patient fact request")


def supersession_view(value: FactSupersession) -> FactSupersessionResponse:
    return FactSupersessionResponse(
        superseded=fact_view(value.superseded),
        replacement=fact_view(value.replacement),
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
    updater: UpdatePatientCapability,
    fact_writer: WritePatientFactCapability,
    authenticator: PatientAuthenticator | None = None,
) -> APIRouter:
    router_dependencies: list[Any] = []
    if authenticator is not None:

        async def require_authenticated_patient(
            request: Request,
            authorization: Annotated[str | None, Header()] = None,
        ) -> None:
            await authenticate_patient(
                request,
                authorization,
                authenticator=authenticator,
            )

        router_dependencies.append(Depends(require_authenticated_patient))

    router = APIRouter(
        prefix="/patients",
        tags=["patients"],
        dependencies=router_dependencies,
    )

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

    @router.patch(
        "/{patient_id}",
        response_model=PatientResponse,
        dependencies=[Depends(require_self_subject(PATIENT_WRITE_SELF, "patient_id"))],
    )
    async def update_patient(
        patient_id: UUID, payload: UpdatePatientRequest, response: Response
    ) -> PatientResponse:
        response.headers["Cache-Control"] = "no-store"
        demographics = (
            None
            if payload.demographics is None
            else PatientDemographics(**payload.demographics.model_dump())
        )
        return patient_view(
            await updater.update_profile(
                patient_id=OpaqueId(patient_id),
                expected_updated_at=payload.expected_updated_at,
                preferred_language=payload.preferred_language,
                demographics=demographics,
            )
        )

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

    @router.post(
        "/{patient_id}/facts",
        response_model=FactSummary,
        status_code=status.HTTP_201_CREATED,
        dependencies=[Depends(require_self_subject(PATIENT_WRITE_SELF, "patient_id"))],
    )
    async def add_patient_fact(
        patient_id: UUID,
        payload: PatientFactRequest,
        request: Request,
        response: Response,
    ) -> FactSummary:
        response.headers["Cache-Control"] = "no-store"
        context = get_actor_context(request)
        if context.actor_id is None:
            raise ApplicationError(
                code=ErrorCode.AUTHORIZATION_DENIED,
                message="The authenticated actor is not permitted to update this history.",
            )
        return fact_view(
            await fact_writer.add_patient_fact(
                patient_id=OpaqueId(patient_id),
                actor_id=context.actor_id,
                fact_type=payload.fact_type,
                value=patient_fact_value(payload),
                effective_time=payload.effective_time,
            )
        )

    @router.post(
        "/{patient_id}/facts/{fact_id}/supersede",
        response_model=FactSupersessionResponse,
        dependencies=[Depends(require_self_subject(PATIENT_WRITE_SELF, "patient_id"))],
    )
    async def supersede_patient_fact(
        patient_id: UUID,
        fact_id: UUID,
        payload: SupersedeFactRequest,
        request: Request,
        response: Response,
    ) -> FactSupersessionResponse:
        response.headers["Cache-Control"] = "no-store"
        if payload.expected_current_id != fact_id:
            raise ApplicationError(
                code=ErrorCode.RESOURCE_CONFLICT,
                message=(
                    "The medical-history entry changed or is unavailable. Reload and try again."
                ),
            )
        context = get_actor_context(request)
        if context.actor_id is None:
            raise ApplicationError(
                code=ErrorCode.AUTHORIZATION_DENIED,
                message="The authenticated actor is not permitted to update this history.",
            )
        replacement = payload.replacement
        return supersession_view(
            await fact_writer.supersede_patient_fact(
                patient_id=OpaqueId(patient_id),
                actor_id=context.actor_id,
                expected_current_id=OpaqueId(fact_id),
                fact_type=replacement.fact_type,
                value=patient_fact_value(replacement),
                effective_time=replacement.effective_time,
            )
        )

    return router
