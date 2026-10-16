"""Closed question, answer, pack, questionnaire, and repository contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.clinical_intake.domain import (
    ClinicalIntake,
    bounded_text,
    normalize_utc,
    tuple_of,
)
from app.modules.clinical_intake.domain import (
    Requiredness as Requiredness,
)
from app.shared.types import OpaqueId


class AnswerType(StrEnum):
    TEXT = "TEXT"
    SINGLE_CHOICE = "SINGLE_CHOICE"
    MULTI_CHOICE = "MULTI_CHOICE"
    BOOLEAN = "BOOLEAN"
    NUMBER = "NUMBER"
    DATE = "DATE"
    DURATION = "DURATION"
    SEVERITY_SCALE = "SEVERITY_SCALE"


class QuestionSection(StrEnum):
    CHIEF_COMPLAINT = "CHIEF_COMPLAINT"
    HPI = "HPI"
    PAST_MEDICAL = "PAST_MEDICAL"
    PAST_SURGICAL = "PAST_SURGICAL"
    MEDICATIONS = "MEDICATIONS"
    ALLERGIES = "ALLERGIES"
    FAMILY = "FAMILY"
    PERSONAL = "PERSONAL"
    ROS = "ROS"
    PRIOR_INVESTIGATIONS = "PRIOR_INVESTIGATIONS"
    EXTENSION = "EXTENSION"


class InputMode(StrEnum):
    TEXT = "TEXT"
    TOUCH = "TOUCH"
    VOICE = "VOICE"


@dataclass(frozen=True, slots=True)
class TextValidation:
    min_length: int
    max_length: int

    def __post_init__(self) -> None:
        if self.min_length < 0 or self.max_length < self.min_length or self.max_length > 4000:
            raise ValueError("text length constraint is invalid")


@dataclass(frozen=True, slots=True)
class OptionValidation:
    allowed_option_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.allowed_option_ids or len(set(self.allowed_option_ids)) != len(
            self.allowed_option_ids
        ):
            raise ValueError("allowed option IDs must be non-empty and unique")
        for value in self.allowed_option_ids:
            bounded_text("option_id", value, 128)


@dataclass(frozen=True, slots=True)
class NumericValidation:
    minimum: Decimal | None = None
    maximum: Decimal | None = None
    unit: str | None = None

    def __post_init__(self) -> None:
        if self.minimum is not None and (not self.minimum.is_finite()):
            raise ValueError("numeric minimum must be finite")
        if self.maximum is not None and (not self.maximum.is_finite()):
            raise ValueError("numeric maximum must be finite")
        if self.minimum is not None and self.maximum is not None and self.minimum > self.maximum:
            raise ValueError("numeric minimum must not exceed maximum")
        if self.unit is not None:
            bounded_text("unit", self.unit, 32)


@dataclass(frozen=True, slots=True)
class DateValidation:
    earliest: date | None = None
    latest: date | None = None

    def __post_init__(self) -> None:
        if self.earliest is not None and self.latest is not None and self.earliest > self.latest:
            raise ValueError("date earliest must not exceed latest")


@dataclass(frozen=True, slots=True)
class DurationValidation:
    allowed_units: tuple[str, ...]
    minimum: Decimal = Decimal("0")
    maximum: Decimal | None = None

    def __post_init__(self) -> None:
        if not self.allowed_units or self.minimum < 0:
            raise ValueError("duration constraint is invalid")
        if self.maximum is not None and self.maximum < self.minimum:
            raise ValueError("duration maximum must not be below minimum")
        for unit in self.allowed_units:
            bounded_text("duration unit", unit, 32)


@dataclass(frozen=True, slots=True)
class SeverityValidation:
    scale_id: str
    scale_version: str
    allowed_values: tuple[Decimal, ...]

    def __post_init__(self) -> None:
        bounded_text("scale_id", self.scale_id, 128)
        bounded_text("scale_version", self.scale_version, 64)
        if not self.allowed_values or any(not value.is_finite() for value in self.allowed_values):
            raise ValueError("severity allowed values must be finite and non-empty")


type ValidationConstraints = (
    TextValidation
    | OptionValidation
    | NumericValidation
    | DateValidation
    | DurationValidation
    | SeverityValidation
    | None
)


@dataclass(frozen=True, slots=True)
class HistoryBinding:
    fact_type: str
    section_key: str

    def __post_init__(self) -> None:
        bounded_text("fact_type", self.fact_type, 64)
        bounded_text("section_key", self.section_key, 128)


@dataclass(frozen=True, slots=True)
class QuestionDefinition:
    question_id: str
    question_version: str
    section: QuestionSection
    content_key: str
    answer_type: AnswerType
    requiredness: Requiredness
    input_modes: tuple[InputMode, ...]
    validation: ValidationConstraints
    order: int
    help_content_key: str | None = None
    applicability_rule_ids: tuple[str, ...] = ()
    sensitive: bool = False
    dependency_question_ids: tuple[str, ...] = ()
    allow_unknown: bool = False
    allow_prefer_not_to_answer: bool = False
    history_binding: HistoryBinding | None = None

    def __post_init__(self) -> None:
        for name in ("question_id", "question_version", "content_key"):
            bounded_text(name, getattr(self, name), 128)
        if self.help_content_key is not None:
            bounded_text("help_content_key", self.help_content_key, 128)
        if not self.input_modes or not isinstance(self.input_modes, tuple):
            raise ValueError("input_modes must be a non-empty tuple")
        if any(not isinstance(mode, InputMode) for mode in self.input_modes):
            raise TypeError("input_modes must contain only InputMode values")
        for name in ("applicability_rule_ids", "dependency_question_ids"):
            values = getattr(self, name)
            tuple_of(name, values, str)
            for value in values:
                bounded_text(name, value, 128)
        if self.order < 0:
            raise ValueError("question order must be non-negative")
        expected = {
            AnswerType.TEXT: TextValidation,
            AnswerType.SINGLE_CHOICE: OptionValidation,
            AnswerType.MULTI_CHOICE: OptionValidation,
            AnswerType.NUMBER: NumericValidation,
            AnswerType.DATE: DateValidation,
            AnswerType.DURATION: DurationValidation,
            AnswerType.SEVERITY_SCALE: SeverityValidation,
            AnswerType.BOOLEAN: type(None),
        }[self.answer_type]
        if not isinstance(self.validation, expected):
            raise ValueError("validation constraints do not match answer_type")


class IntakeAnswerSourceType(StrEnum):
    PATIENT_TEXT = "PATIENT_TEXT"
    PATIENT_TOUCH = "PATIENT_TOUCH"
    REUSED_HISTORY = "REUSED_HISTORY"


class ResponseDisposition(StrEnum):
    ANSWERED = "ANSWERED"
    UNKNOWN = "UNKNOWN"
    PREFER_NOT_TO_ANSWER = "PREFER_NOT_TO_ANSWER"
    SKIPPED = "SKIPPED"


type AnswerValue = str | bool | Decimal | date | None


@dataclass(frozen=True, slots=True)
class IntakeAnswer:
    answer_id: OpaqueId
    intake_id: OpaqueId
    question_id: str
    question_version: str
    answer_type: AnswerType
    value: AnswerValue
    response_disposition: ResponseDisposition
    language_code: str
    source_type: IntakeAnswerSourceType
    answered_at: datetime
    created_at: datetime
    selected_option_ids: tuple[str, ...] | None = None
    unit: str | None = None
    original_text: str | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        for name in ("question_id", "question_version", "language_code"):
            bounded_text(name, getattr(self, name), 128)
        if self.original_text is not None:
            bounded_text("original_text", self.original_text, 2000)
        answered = normalize_utc("answered_at", self.answered_at)
        created = normalize_utc("created_at", self.created_at)
        if self.response_disposition is not ResponseDisposition.ANSWERED:
            if (
                self.value is not None
                or self.selected_option_ids is not None
                or self.unit is not None
            ):
                raise ValueError("non-answered response cannot carry answer values")
        elif self.answer_type is AnswerType.TEXT:
            if not isinstance(self.value, str):
                raise ValueError("TEXT answer requires a string value")
            bounded_text("value", self.value, 4000)
            if self.selected_option_ids is not None or self.unit is not None:
                raise ValueError("selected_option_ids and unit are invalid for TEXT")
        elif self.answer_type in {AnswerType.SINGLE_CHOICE, AnswerType.MULTI_CHOICE}:
            if self.value is not None or not self.selected_option_ids:
                raise ValueError("choice answer requires selected_option_ids only")
            if self.answer_type is AnswerType.SINGLE_CHOICE and len(self.selected_option_ids) != 1:
                raise ValueError("SINGLE_CHOICE requires exactly one option")
        elif self.answer_type is AnswerType.BOOLEAN:
            if (
                type(self.value) is not bool
                or self.selected_option_ids is not None
                or self.unit is not None
            ):
                raise ValueError("BOOLEAN answer combination is invalid")
        elif self.answer_type is AnswerType.DATE:
            if (
                type(self.value) is not date
                or self.selected_option_ids is not None
                or self.unit is not None
            ):
                raise ValueError("DATE answer combination is invalid")
        else:
            if (
                not isinstance(self.value, Decimal)
                or not self.value.is_finite()
                or self.selected_option_ids is not None
            ):
                raise ValueError("numeric answer combination is invalid")
            if self.answer_type is AnswerType.DURATION and (self.value < 0 or self.unit is None):
                raise ValueError("DURATION answer requires non-negative value and unit")
            if self.answer_type is not AnswerType.DURATION and self.unit is not None:
                raise ValueError("unit is valid only for DURATION")
        object.__setattr__(self, "answered_at", answered)
        object.__setattr__(self, "created_at", created)


class QuestionnaireStatus(StrEnum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"


@dataclass(frozen=True, slots=True)
class AnswerReference:
    question_id: str
    question_version: str
    answer_id: OpaqueId


@dataclass(frozen=True, slots=True)
class SkippedQuestionReference:
    question_id: str
    question_version: str
    disposition: ResponseDisposition

    def __post_init__(self) -> None:
        if self.disposition is ResponseDisposition.ANSWERED:
            raise ValueError("skipped reference cannot use ANSWERED disposition")


@dataclass(frozen=True, slots=True)
class QuestionnaireResponses:
    pack_id: str
    pack_version: str
    answer_refs: tuple[AnswerReference, ...]
    skipped_question_refs: tuple[SkippedQuestionReference, ...]
    engine_version: str
    last_selected_question_id: str | None = None

    def __post_init__(self) -> None:
        for name in ("pack_id", "pack_version", "engine_version"):
            bounded_text(name, getattr(self, name), 128)
        tuple_of("answer_refs", self.answer_refs, AnswerReference)
        tuple_of("skipped_question_refs", self.skipped_question_refs, SkippedQuestionReference)


@dataclass(frozen=True, slots=True)
class QuestionnaireInstance:
    instance_id: OpaqueId
    encounter_id: OpaqueId
    questionnaire_id: str
    questionnaire_version: str
    status: QuestionnaireStatus
    responses: QuestionnaireResponses
    started_at: datetime
    completed_at: datetime | None = None

    def __post_init__(self) -> None:
        started = normalize_utc("started_at", self.started_at)
        completed = (
            None if self.completed_at is None else normalize_utc("completed_at", self.completed_at)
        )
        if (
            self.responses.pack_id != self.questionnaire_id
            or self.responses.pack_version != self.questionnaire_version
        ):
            raise ValueError("questionnaire identity must match response pack identity")
        if self.status is QuestionnaireStatus.COMPLETED:
            if completed is None or completed < started:
                raise ValueError("completed questionnaire requires a valid completed_at")
        elif completed is not None:
            raise ValueError("completed_at is allowed only for COMPLETED questionnaire")
        object.__setattr__(self, "started_at", started)
        object.__setattr__(self, "completed_at", completed)


class QuestionPackKind(StrEnum):
    CORE = "CORE"
    COMPLAINT = "COMPLAINT"
    SPECIALTY = "SPECIALTY"
    AYUSH_EXTENSION = "AYUSH_EXTENSION"


class ApprovalState(StrEnum):
    ENGINEERING_APPROVED = "ENGINEERING_APPROVED"
    CLINICAL_APPROVAL_REQUIRED = "CLINICAL_APPROVAL_REQUIRED"
    APPROVED = "APPROVED"


class RuleOperator(StrEnum):
    EXISTS = "EXISTS"
    EQUALS = "EQUALS"
    IN = "IN"
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    ANSWER_DISPOSITION = "ANSWER_DISPOSITION"
    HISTORY_AVAILABLE = "HISTORY_AVAILABLE"
    CONTRADICTION_STATE = "CONTRADICTION_STATE"


@dataclass(frozen=True, slots=True)
class RuleDefinition:
    rule_id: str
    operator: RuleOperator
    operands: tuple[str, ...]

    def __post_init__(self) -> None:
        bounded_text("rule_id", self.rule_id, 128)
        tuple_of("operands", self.operands, str)
        for operand in self.operands:
            bounded_text("operand", operand, 128)


@dataclass(frozen=True, slots=True)
class QuestionPack:
    pack_id: str
    version: str
    kind: QuestionPackKind
    approval_state: ApprovalState
    content_version: str
    supported_languages: tuple[str, ...]
    questions: tuple[QuestionDefinition, ...]
    order: int
    applicability_rules: tuple[RuleDefinition, ...] = ()
    contradiction_rules: tuple[RuleDefinition, ...] = ()
    schema_version: str = "question-pack.v1"

    def __post_init__(self) -> None:
        for name in ("pack_id", "version", "content_version"):
            bounded_text(name, getattr(self, name), 128)
        if self.schema_version != "question-pack.v1":
            raise ValueError("question pack schema version is unsupported")
        if not self.supported_languages or self.order < 0:
            raise ValueError("question pack languages/order are invalid")
        tuple_of("supported_languages", self.supported_languages, str)
        tuple_of("questions", self.questions, QuestionDefinition)
        tuple_of("applicability_rules", self.applicability_rules, RuleDefinition)
        tuple_of("contradiction_rules", self.contradiction_rules, RuleDefinition)
        for language in self.supported_languages:
            bounded_text("supported_language", language, 35)


class DuplicateQuestionPackError(ValueError):
    """Raised for explicit duplicate pack/version registration."""


class PackRegistry:
    """Process-local immutable explicit registration container; no discovery."""

    def __init__(self, packs: tuple[QuestionPack, ...] = ()) -> None:
        tuple_of("packs", packs, QuestionPack)
        values: dict[tuple[str, str], QuestionPack] = {}
        for pack in packs:
            key = (pack.pack_id, pack.version)
            if key in values:
                raise DuplicateQuestionPackError("question pack identity is already registered")
            values[key] = pack
        self._packs = values

    def get(self, pack_id: str, version: str) -> QuestionPack | None:
        return self._packs.get((pack_id, version))

    def all(self) -> tuple[QuestionPack, ...]:
        return tuple(self._packs.values())


class StaleClinicalIntakeWriteError(RuntimeError):
    """Raised when optimistic persistence detects a stale aggregate version."""


class ClinicalIntakeAlreadyExistsError(RuntimeError):
    """Raised when an encounter already owns a clinical intake."""


class ClinicalIntakeIdentityError(RuntimeError):
    """Raised when a save attempts to change an intake's encounter identity."""


class QuestionnaireInstanceIdentityError(RuntimeError):
    """Raised when a save attempts to change immutable questionnaire identity."""


class ClinicalIntakeRepository(Protocol):
    async def add(self, session: AsyncSession, intake: ClinicalIntake) -> object: ...
    async def get(self, session: AsyncSession, intake_id: OpaqueId) -> ClinicalIntake | None: ...
    async def get_by_encounter(
        self, session: AsyncSession, encounter_id: OpaqueId
    ) -> ClinicalIntake | None: ...
    async def save(
        self,
        session: AsyncSession,
        intake: ClinicalIntake,
        *,
        expected_version: int,
        updated_at: datetime,
    ) -> ClinicalIntake: ...


class IntakeAnswerRepository(Protocol):
    async def add(self, session: AsyncSession, answer: IntakeAnswer) -> object: ...
    async def list_for_intake(
        self, session: AsyncSession, intake_id: OpaqueId
    ) -> tuple[IntakeAnswer, ...]: ...


class QuestionnaireInstanceRepository(Protocol):
    async def add(self, session: AsyncSession, instance: QuestionnaireInstance) -> object: ...
    async def get(
        self, session: AsyncSession, instance_id: OpaqueId
    ) -> QuestionnaireInstance | None: ...
    async def list_for_encounter(
        self, session: AsyncSession, encounter_id: OpaqueId
    ) -> tuple[QuestionnaireInstance, ...]: ...
    async def save(
        self, session: AsyncSession, instance: QuestionnaireInstance
    ) -> QuestionnaireInstance: ...


class StartIntakeCapability(Protocol):
    async def start_intake(self, encounter_id: OpaqueId) -> ClinicalIntake: ...


class ReadIntakeCapability(Protocol):
    async def get_intake(self, intake_id: OpaqueId) -> ClinicalIntake: ...


class AnswerIntakeCapability(Protocol):
    async def record_answer(
        self, intake_id: OpaqueId, answer: IntakeAnswer, *, expected_version: int
    ) -> ClinicalIntake: ...


class CompleteIntakeCapability(Protocol):
    async def complete_intake(
        self, intake_id: OpaqueId, *, expected_version: int
    ) -> ClinicalIntake: ...


class NextQuestionCapability(Protocol):
    async def next_question(self, intake_id: OpaqueId) -> QuestionDefinition | None: ...
