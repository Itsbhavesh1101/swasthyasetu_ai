"""Session-authorized P7 structured intake HTTP contracts."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Header, Request, Response, status
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.api.security.bearer import parse_bearer
from app.modules.clinical_intake.application import (
    ClinicalIntakeService,
    IntakeSnapshot,
    PatientAnswerInput,
)
from app.modules.clinical_intake.content import ENGINEERING_CORE_PACK, ENGINEERING_PRESENTATIONS
from app.modules.clinical_intake.contracts import (
    AnswerType,
    DateValidation,
    DurationValidation,
    IntakeAnswer,
    IntakeAnswerSourceType,
    NumericValidation,
    OptionValidation,
    ResponseDisposition,
    SeverityValidation,
    TextValidation,
)
from app.modules.clinical_intake.engine import (
    ClarificationRequired,
    CompletionReady,
    Incomplete,
    NextQuestion,
)
from app.modules.consent.domain import ConsentPurpose, ConsentScope, ConsentSubjectType
from app.modules.consent.public import CONSENT_CHECK
from app.modules.encounters.domain import EncounterStatus, EncounterType
from app.modules.encounters.public import ENCOUNTERS_READ
from app.modules.sessions.domain import Session
from app.modules.sessions.public import SESSIONS_VALIDATE
from app.shared.errors import ApplicationError, ErrorCode
from app.shared.types import OpaqueId


class StartIntakeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pack_ids: tuple[str, ...] = Field(min_length=1, max_length=8)

    @field_validator("pack_ids")
    @classmethod
    def validate_pack_ids(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(value) != len(set(value)) or any(not item or len(item) > 128 for item in value):
            raise ValueError("pack IDs must be unique bounded machine identifiers")
        return value


class AnswerPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["intake-answer.v1"]
    answer_type: AnswerType
    value: str | bool | int | float | None = None
    selected_option_ids: tuple[str, ...] | None = Field(default=None, max_length=64)
    unit: str | None = Field(default=None, max_length=32)
    response_disposition: ResponseDisposition
    language_code: Literal["en", "hi"]
    original_text: str | None = Field(default=None, min_length=1, max_length=2000)


class SubmitAnswerRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    question_id: str = Field(min_length=1, max_length=128)
    question_version: str = Field(min_length=1, max_length=128)
    answer: AnswerPayload
    source_type: Literal[
        IntakeAnswerSourceType.PATIENT_TEXT,
        IntakeAnswerSourceType.PATIENT_TOUCH,
    ]
    expected_version: int = Field(gt=0)


class CompleteIntakeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_version: int = Field(gt=0)


class AnswerView(BaseModel):
    model_config = ConfigDict(extra="forbid")
    answer_id: UUID
    question_id: str
    question_version: str
    answer_type: AnswerType
    value: str | bool | Decimal | date | None
    selected_option_ids: tuple[str, ...] | None
    unit: str | None
    response_disposition: ResponseDisposition
    source_label: Literal["Patient provided"]


class MissingView(BaseModel):
    model_config = ConfigDict(extra="forbid")
    field_or_question_key: str
    reason_code: str
    requiredness: str


class QuestionView(BaseModel):
    model_config = ConfigDict(extra="forbid")
    question_id: str
    question_version: str
    pack_id: str
    pack_version: str
    section: str
    prompt: str
    help_text: str | None
    answer_type: AnswerType
    requiredness: str
    allow_unknown: bool
    allow_prefer_not_to_answer: bool
    allow_skip: bool
    constraints: dict[str, object]
    options: tuple[dict[str, str], ...]


class IntakeView(BaseModel):
    model_config = ConfigDict(extra="forbid")
    intake_id: UUID
    encounter_id: UUID
    status: str
    version: int
    started_at: datetime
    completed_at: datetime | None
    pack_versions: tuple[dict[str, str], ...]
    current_question: QuestionView | None
    engine_state: Literal[
        "NEXT_QUESTION", "CLARIFICATION_REQUIRED", "INCOMPLETE", "COMPLETION_READY"
    ]
    completion_ready: bool
    answers: tuple[AnswerView, ...]
    missing_information: tuple[MissingView, ...]


def _constraints(validation: object) -> dict[str, object]:
    if isinstance(validation, TextValidation):
        return {"min_length": validation.min_length, "max_length": validation.max_length}
    if isinstance(validation, OptionValidation):
        return {"allowed_option_ids": list(validation.allowed_option_ids)}
    if isinstance(validation, NumericValidation):
        return {
            "minimum": None if validation.minimum is None else str(validation.minimum),
            "maximum": None if validation.maximum is None else str(validation.maximum),
            "unit": validation.unit,
        }
    if isinstance(validation, DateValidation):
        return {
            "earliest": None if validation.earliest is None else validation.earliest.isoformat(),
            "latest": None if validation.latest is None else validation.latest.isoformat(),
        }
    if isinstance(validation, DurationValidation):
        return {
            "allowed_units": list(validation.allowed_units),
            "minimum": str(validation.minimum),
            "maximum": None if validation.maximum is None else str(validation.maximum),
        }
    if isinstance(validation, SeverityValidation):
        return {
            "scale_id": validation.scale_id,
            "scale_version": validation.scale_version,
            "allowed_values": [str(value) for value in validation.allowed_values],
        }
    return {}


def _question(result: object) -> QuestionView | None:
    if not isinstance(result, (NextQuestion, ClarificationRequired)):
        return None
    definition = result.question
    presentation = ENGINEERING_PRESENTATIONS.get(
        (result.pack_id, result.pack_version, definition.question_id)
    )
    if presentation is None:
        raise ApplicationError(
            code=ErrorCode.POLICY_UNAVAILABLE,
            message="The intake question content is unavailable.",
        )
    return QuestionView(
        question_id=definition.question_id,
        question_version=definition.question_version,
        pack_id=result.pack_id,
        pack_version=result.pack_version,
        section=definition.section.value,
        prompt=presentation.prompt,
        help_text=presentation.help_text,
        answer_type=definition.answer_type,
        requiredness=definition.requiredness.value,
        allow_unknown=definition.allow_unknown,
        allow_prefer_not_to_answer=definition.allow_prefer_not_to_answer,
        allow_skip=definition.allow_skip,
        constraints=_constraints(definition.validation),
        options=tuple({"id": key, "label": label} for key, label in presentation.option_labels),
    )


def _latest_answers(answers: tuple[IntakeAnswer, ...]) -> tuple[IntakeAnswer, ...]:
    latest: dict[str, IntakeAnswer] = {}
    for answer in answers:
        current = latest.get(answer.question_id)
        if current is None or (answer.answered_at, answer.answer_id.value.int) > (
            current.answered_at,
            current.answer_id.value.int,
        ):
            latest[answer.question_id] = answer
    return tuple(sorted(latest.values(), key=lambda item: item.question_id))


def intake_view(snapshot: IntakeSnapshot) -> IntakeView:
    result = snapshot.engine_result
    state: Literal["NEXT_QUESTION", "CLARIFICATION_REQUIRED", "INCOMPLETE", "COMPLETION_READY"]
    if isinstance(result, NextQuestion):
        state = "NEXT_QUESTION"
    elif isinstance(result, ClarificationRequired):
        state = "CLARIFICATION_REQUIRED"
    elif isinstance(result, Incomplete):
        state = "INCOMPLETE"
    else:
        state = "COMPLETION_READY"
    current_question = _question(result)
    if (
        current_question is None
        and snapshot.intake.status.value == "IN_PROGRESS"
        and snapshot.answers
    ):
        latest = max(
            snapshot.answers,
            key=lambda item: (item.answered_at, item.answer_id.value.int),
        )
        definition = next(
            (
                item
                for item in ENGINEERING_CORE_PACK.questions
                if item.question_id == latest.question_id
                and item.question_version == latest.question_version
            ),
            None,
        )
        if definition is not None:
            current_question = _question(
                NextQuestion(
                    question=definition,
                    pack_id=ENGINEERING_CORE_PACK.pack_id,
                    pack_version=ENGINEERING_CORE_PACK.version,
                    reason_rule_ids=("review:correction",),
                )
            )
    return IntakeView(
        intake_id=snapshot.intake.intake_id.value,
        encounter_id=snapshot.intake.encounter_id.value,
        status=snapshot.intake.status.value,
        version=snapshot.intake.version,
        started_at=snapshot.intake.started_at,
        completed_at=snapshot.intake.completed_at,
        pack_versions=tuple(
            {"pack_id": item.questionnaire_id, "pack_version": item.questionnaire_version}
            for item in snapshot.instances
        ),
        current_question=current_question,
        engine_state=state,
        completion_ready=isinstance(result, CompletionReady),
        answers=tuple(
            AnswerView(
                answer_id=item.answer_id.value,
                question_id=item.question_id,
                question_version=item.question_version,
                answer_type=item.answer_type,
                value=item.value,
                selected_option_ids=item.selected_option_ids,
                unit=item.unit,
                response_disposition=item.response_disposition,
                source_label="Patient provided",
            )
            for item in _latest_answers(snapshot.answers)
        ),
        missing_information=tuple(
            MissingView(
                field_or_question_key=item.field_or_question_key,
                reason_code=item.reason_code.value,
                requiredness=item.requiredness.value,
            )
            for item in snapshot.intake.missing_information
        ),
    )


async def _authorize_encounter(
    request: Request,
    encounter_id: OpaqueId,
    authorization: str | None,
    *,
    for_write: bool,
) -> tuple[object, Session]:
    encounter = await request.app.state.capability_registry.resolve(ENCOUNTERS_READ).get_encounter(
        encounter_id
    )
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
    if encounter.patient_id is not None:
        raise ApplicationError(
            code=ErrorCode.AUTHORIZATION_DENIED,
            message="Patient-linked intake is not available in this phase.",
        )
    if encounter.encounter_type not in {
        EncounterType.GENERAL_INTAKE,
        EncounterType.KIOSK_INTAKE,
    } or (
        for_write and encounter.status not in {EncounterStatus.CREATED, EncounterStatus.IN_PROGRESS}
    ):
        raise ApplicationError(
            code=ErrorCode.INVALID_STATE_TRANSITION,
            message="This encounter cannot use structured intake.",
        )
    return encounter, session


async def _authorize_intake(
    request: Request,
    service: ClinicalIntakeService,
    intake_id: OpaqueId,
    authorization: str | None,
    *,
    for_write: bool,
) -> tuple[object, Session]:
    intake = await service.get_intake(intake_id)
    encounter, session = await _authorize_encounter(
        request, intake.encounter_id, authorization, for_write=for_write
    )
    return encounter, session


def _patient_value(payload: AnswerPayload) -> str | bool | Decimal | date | None:
    value = payload.value
    if payload.response_disposition is not ResponseDisposition.ANSWERED:
        return None
    if payload.answer_type is AnswerType.DATE:
        if not isinstance(value, str):
            raise ValueError("date value is invalid")
        return date.fromisoformat(value)
    if payload.answer_type in {AnswerType.NUMBER, AnswerType.DURATION, AnswerType.SEVERITY_SCALE}:
        if isinstance(value, bool) or value is None:
            raise ValueError("numeric value is invalid")
        try:
            decimal = Decimal(str(value))
        except (InvalidOperation, ValueError) as error:
            raise ValueError("numeric value is invalid") from error
        if not decimal.is_finite():
            raise ValueError("numeric value is invalid")
        return decimal
    if value is None or isinstance(value, (str, bool)):
        return value
    raise ValueError("answer value is invalid")


def build_clinical_intake_router(*, service: ClinicalIntakeService) -> APIRouter:
    router = APIRouter(tags=["clinical-intake"])

    @router.post("/encounters/{encounter_id}/intake", response_model=IntakeView)
    async def start_intake(
        encounter_id: UUID,
        payload: StartIntakeRequest,
        request: Request,
        response: Response,
        authorization: Annotated[str | None, Header()] = None,
    ) -> IntakeView:
        response.headers["Cache-Control"] = "no-store"
        _, session = await _authorize_encounter(
            request, OpaqueId(encounter_id), authorization, for_write=True
        )
        snapshot = await service.start_snapshot(
            OpaqueId(encounter_id),
            pack_ids=payload.pack_ids,
            language=session.language_preference or "en",
        )
        response.status_code = status.HTTP_201_CREATED if snapshot.created else status.HTTP_200_OK
        return intake_view(snapshot)

    @router.get("/intakes/{intake_id}", response_model=IntakeView)
    async def read_intake(
        intake_id: UUID,
        request: Request,
        response: Response,
        authorization: Annotated[str | None, Header()] = None,
    ) -> IntakeView:
        response.headers["Cache-Control"] = "no-store"
        _, session = await _authorize_intake(
            request, service, OpaqueId(intake_id), authorization, for_write=False
        )
        return intake_view(
            await service.get_snapshot(
                OpaqueId(intake_id), language=session.language_preference or "en"
            )
        )

    @router.post("/intakes/{intake_id}/answers", response_model=IntakeView)
    async def submit_answer(
        intake_id: UUID,
        payload: SubmitAnswerRequest,
        request: Request,
        response: Response,
        authorization: Annotated[str | None, Header()] = None,
    ) -> IntakeView:
        response.headers["Cache-Control"] = "no-store"
        _, session = await _authorize_intake(
            request, service, OpaqueId(intake_id), authorization, for_write=True
        )
        if payload.answer.language_code != (session.language_preference or "en"):
            raise ApplicationError(
                code=ErrorCode.VALIDATION_ERROR,
                message="The answer language does not match the session.",
            )
        try:
            answer_value = _patient_value(payload.answer)
        except ValueError as error:
            raise ApplicationError(
                code=ErrorCode.VALIDATION_ERROR, message="The answer value is invalid.", cause=error
            ) from error
        return intake_view(
            await service.submit_answer(
                OpaqueId(intake_id),
                PatientAnswerInput(
                    question_id=payload.question_id,
                    question_version=payload.question_version,
                    answer_type=payload.answer.answer_type,
                    value=answer_value,
                    selected_option_ids=payload.answer.selected_option_ids,
                    unit=payload.answer.unit,
                    response_disposition=payload.answer.response_disposition,
                    language_code=payload.answer.language_code,
                    source_type=IntakeAnswerSourceType(payload.source_type),
                    original_text=payload.answer.original_text,
                ),
                expected_version=payload.expected_version,
                language=session.language_preference or "en",
            )
        )

    @router.post("/intakes/{intake_id}/complete", response_model=IntakeView)
    async def complete_intake(
        intake_id: UUID,
        payload: CompleteIntakeRequest,
        request: Request,
        response: Response,
        authorization: Annotated[str | None, Header()] = None,
    ) -> IntakeView:
        response.headers["Cache-Control"] = "no-store"
        _, session = await _authorize_intake(
            request, service, OpaqueId(intake_id), authorization, for_write=True
        )
        return intake_view(
            await service.complete_snapshot(
                OpaqueId(intake_id),
                expected_version=payload.expected_version,
                language=session.language_preference or "en",
            )
        )

    return router
