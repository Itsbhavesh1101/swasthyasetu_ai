"""Transactional orchestration for deterministic structured clinical intake."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from app.modules.clinical_intake.contracts import (
    AnswerReference,
    AnswerType,
    ClinicalIntakeAlreadyExistsError,
    IntakeAnswer,
    IntakeAnswerSourceType,
    PackNotActivationEligibleError,
    PackRegistry,
    QuestionnaireInstance,
    QuestionnaireResponses,
    QuestionnaireStatus,
    ResponseDisposition,
    SkippedQuestionReference,
    StaleClinicalIntakeWriteError,
)
from app.modules.clinical_intake.domain import (
    ChiefComplaint,
    ClinicalIntake,
    ClinicalIntakeStatus,
)
from app.modules.clinical_intake.engine import (
    ENGINE_VERSION,
    AdaptiveIntakeEngine,
    ClarificationRequired,
    CompletionReady,
    EngineInput,
    EngineResult,
    InvalidAnswerForQuestionError,
    NextQuestion,
)
from app.modules.clinical_intake.infrastructure import (
    PostgresClinicalIntakeRepository,
    PostgresIntakeAnswerRepository,
    PostgresQuestionnaireInstanceRepository,
)
from app.shared.errors import ApplicationError, DependencyError, ErrorCode
from app.shared.persistence import DatabaseRuntime
from app.shared.types import OpaqueId, utc_now


@dataclass(frozen=True, slots=True)
class IntakeSnapshot:
    intake: ClinicalIntake
    answers: tuple[IntakeAnswer, ...]
    instances: tuple[QuestionnaireInstance, ...]
    engine_result: EngineResult
    created: bool = False


@dataclass(frozen=True, slots=True)
class PatientAnswerInput:
    question_id: str
    question_version: str
    answer_type: AnswerType
    value: str | bool | Decimal | date | None
    selected_option_ids: tuple[str, ...] | None
    unit: str | None
    response_disposition: ResponseDisposition
    language_code: str
    source_type: IntakeAnswerSourceType
    original_text: str | None


class ClinicalIntakeService:
    def __init__(
        self,
        *,
        database: DatabaseRuntime | None,
        registry: PackRegistry,
        allowed_pack_versions: dict[str, str],
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._database = database
        self._registry = registry
        self._allowed_pack_versions = dict(allowed_pack_versions)
        self._clock = clock
        self._intakes = PostgresClinicalIntakeRepository()
        self._answers = PostgresIntakeAnswerRepository()
        self._instances = PostgresQuestionnaireInstanceRepository()
        self._engine = AdaptiveIntakeEngine(registry)

    def _database_required(self) -> DatabaseRuntime:
        if self._database is None:
            raise DependencyError(
                code=ErrorCode.DEPENDENCY_UNAVAILABLE,
                message="Clinical intake persistence is temporarily unavailable.",
            )
        return self._database

    def _now(self) -> datetime:
        value = self._clock()
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("clinical intake clock must be timezone-aware")
        return value.astimezone(UTC)

    def _identities(self, pack_ids: tuple[str, ...], language: str) -> tuple[tuple[str, str], ...]:
        if not pack_ids or len(pack_ids) != len(set(pack_ids)):
            raise ApplicationError(
                code=ErrorCode.VALIDATION_ERROR,
                message="The requested question packs are invalid.",
            )
        try:
            identities = tuple(
                (pack_id, self._allowed_pack_versions[pack_id]) for pack_id in pack_ids
            )
            packs = self._registry.activate(identities, language=language)
        except (KeyError, PackNotActivationEligibleError, ValueError) as error:
            raise ApplicationError(
                code=ErrorCode.POLICY_UNAVAILABLE,
                message="The requested intake content is not available for this language.",
                cause=error,
            ) from error
        return tuple((pack.pack_id, pack.version) for pack in packs)

    @staticmethod
    def _instance_identities(
        instances: tuple[QuestionnaireInstance, ...],
    ) -> tuple[tuple[str, str], ...]:
        return tuple(
            sorted((item.questionnaire_id, item.questionnaire_version) for item in instances)
        )

    def _engine_input(
        self,
        intake: ClinicalIntake,
        instances: tuple[QuestionnaireInstance, ...],
        answers: tuple[IntakeAnswer, ...],
        *,
        language: str,
    ) -> EngineInput:
        identities = self._validate_instances(intake, instances, language=language)
        return EngineInput(
            intake=intake,
            selected_pack_identities=identities,
            answers=answers,
            contradictions=intake.contradictions,
            language=language,
        )

    def _validate_instances(
        self,
        intake: ClinicalIntake,
        instances: tuple[QuestionnaireInstance, ...],
        *,
        language: str,
    ) -> tuple[tuple[str, str], ...]:
        identities = self._instance_identities(instances)
        if not identities or len(identities) != len(set(identities)):
            raise ApplicationError(
                code=ErrorCode.PROCESSING_FAILED,
                message="The saved intake configuration is inconsistent.",
            )
        expected_status = {
            ClinicalIntakeStatus.IN_PROGRESS: QuestionnaireStatus.ACTIVE,
            ClinicalIntakeStatus.COMPLETED: QuestionnaireStatus.COMPLETED,
            ClinicalIntakeStatus.ABANDONED: QuestionnaireStatus.ABANDONED,
        }[intake.status]
        if any(instance.status is not expected_status for instance in instances):
            raise ApplicationError(
                code=ErrorCode.PROCESSING_FAILED,
                message="The saved intake configuration is inconsistent.",
            )
        try:
            self._registry.activate(identities, language=language)
        except ValueError as error:
            raise ApplicationError(
                code=ErrorCode.POLICY_UNAVAILABLE,
                message="The saved intake content is no longer available.",
                cause=error,
            ) from error
        return identities

    async def start_snapshot(
        self, encounter_id: OpaqueId, *, pack_ids: tuple[str, ...], language: str
    ) -> IntakeSnapshot:
        identities = self._identities(pack_ids, language)
        database = self._database_required()
        now = self._now()
        try:
            async with database.transaction() as transaction:
                existing = await self._intakes.get_by_encounter(transaction, encounter_id)
                if existing is not None:
                    instances = await self._instances.list_for_encounter(transaction, encounter_id)
                    if self._instance_identities(instances) != tuple(sorted(identities)):
                        raise ApplicationError(
                            code=ErrorCode.RESOURCE_CONFLICT,
                            message="This encounter already uses a different intake configuration.",
                        )
                    answers = await self._answers.list_for_intake(transaction, existing.intake_id)
                    result = self._result(existing, instances, answers, language=language)
                    return IntakeSnapshot(existing, answers, instances, result)

                intake = ClinicalIntake(
                    intake_id=OpaqueId.new(),
                    encounter_id=encounter_id,
                    status=ClinicalIntakeStatus.IN_PROGRESS,
                    started_at=now,
                    version=1,
                )
                instances = tuple(
                    QuestionnaireInstance(
                        instance_id=OpaqueId.new(),
                        encounter_id=encounter_id,
                        questionnaire_id=pack_id,
                        questionnaire_version=version,
                        status=QuestionnaireStatus.ACTIVE,
                        responses=QuestionnaireResponses(
                            pack_id=pack_id,
                            pack_version=version,
                            answer_refs=(),
                            skipped_question_refs=(),
                            engine_version=ENGINE_VERSION,
                        ),
                        started_at=now,
                    )
                    for pack_id, version in identities
                )
                engine_input = self._engine_input(intake, instances, (), language=language)
                intake = replace(
                    intake, missing_information=self._engine.missing_information(engine_input)
                )
                await self._intakes.add(transaction, intake)
                for instance in instances:
                    await self._instances.add(transaction, instance)
                return IntakeSnapshot(
                    intake,
                    (),
                    instances,
                    self._engine.evaluate(replace(engine_input, intake=intake)),
                    created=True,
                )
        except ClinicalIntakeAlreadyExistsError as error:
            # A concurrent committed creator won the encounter-level UNIQUE constraint.
            async with database.transaction() as transaction:
                existing = await self._intakes.get_by_encounter(transaction, encounter_id)
                if existing is None:
                    raise
                instances = await self._instances.list_for_encounter(transaction, encounter_id)
                if self._instance_identities(instances) != tuple(sorted(identities)):
                    raise ApplicationError(
                        code=ErrorCode.RESOURCE_CONFLICT,
                        message="This encounter already uses a different intake configuration.",
                        cause=error,
                    ) from error
                answers = await self._answers.list_for_intake(transaction, existing.intake_id)
                return IntakeSnapshot(
                    existing,
                    answers,
                    instances,
                    self._result(existing, instances, answers, language=language),
                )

    async def start_intake(self, encounter_id: OpaqueId) -> ClinicalIntake:
        return (
            await self.start_snapshot(
                encounter_id,
                pack_ids=("core.intake",),
                language="en",
            )
        ).intake

    def _result(
        self,
        intake: ClinicalIntake,
        instances: tuple[QuestionnaireInstance, ...],
        answers: tuple[IntakeAnswer, ...],
        *,
        language: str,
    ) -> EngineResult:
        if intake.status is ClinicalIntakeStatus.COMPLETED:
            self._validate_instances(intake, instances, language=language)
            return CompletionReady()
        if intake.status is ClinicalIntakeStatus.ABANDONED:
            raise ApplicationError(
                code=ErrorCode.INVALID_STATE_TRANSITION,
                message="This intake is read-only.",
            )
        return self._engine.evaluate(
            self._engine_input(intake, instances, answers, language=language)
        )

    async def get_snapshot(self, intake_id: OpaqueId, *, language: str) -> IntakeSnapshot:
        database = self._database_required()
        async with database.transaction() as transaction:
            intake = await self._intakes.get(transaction, intake_id)
            if intake is None:
                raise ApplicationError(
                    code=ErrorCode.RESOURCE_NOT_FOUND,
                    message="The requested intake was not found.",
                )
            answers = await self._answers.list_for_intake(transaction, intake_id)
            instances = await self._instances.list_for_encounter(transaction, intake.encounter_id)
            return IntakeSnapshot(
                intake,
                answers,
                instances,
                self._result(intake, instances, answers, language=language),
            )

    async def get_intake(self, intake_id: OpaqueId) -> ClinicalIntake:
        database = self._database_required()
        async with database.transaction() as transaction:
            intake = await self._intakes.get(transaction, intake_id)
        if intake is None:
            raise ApplicationError(
                code=ErrorCode.RESOURCE_NOT_FOUND, message="The requested intake was not found."
            )
        return intake

    @staticmethod
    def _next_timestamp(now: datetime, answers: tuple[IntakeAnswer, ...]) -> datetime:
        if not answers:
            return now
        latest = max(answer.answered_at for answer in answers)
        return now if now > latest else latest + timedelta(microseconds=1)

    @staticmethod
    def _project(intake: ClinicalIntake, answers: tuple[IntakeAnswer, ...]) -> ClinicalIntake:
        latest = max(
            (answer for answer in answers if answer.question_id == "core.chief_complaint"),
            key=lambda answer: (answer.answered_at, answer.answer_id.value.int),
            default=None,
        )
        complaint = None
        if (
            latest is not None
            and latest.response_disposition is ResponseDisposition.ANSWERED
            and isinstance(latest.value, str)
        ):
            complaint = ChiefComplaint(
                patient_wording=latest.value,
                display_key="core.chief_complaint",
                source_answer_id=latest.answer_id,
            )
        return replace(intake, chief_complaint=complaint)

    @staticmethod
    def _is_selected_question(
        result: EngineResult, question_id: str, question_version: str
    ) -> bool:
        return isinstance(result, (NextQuestion, ClarificationRequired)) and (
            result.question.question_id,
            result.question.question_version,
        ) == (question_id, question_version)

    def _require_answer_authority(
        self,
        intake: ClinicalIntake,
        instances: tuple[QuestionnaireInstance, ...],
        answers: tuple[IntakeAnswer, ...],
        *,
        question_id: str,
        question_version: str,
        language: str,
    ) -> None:
        persisted_result = self._engine.evaluate(
            self._engine_input(intake, instances, answers, language=language)
        )
        if self._is_selected_question(persisted_result, question_id, question_version):
            return
        if not any(
            answer.question_id == question_id and answer.question_version == question_version
            for answer in answers
        ):
            raise ApplicationError(
                code=ErrorCode.VALIDATION_ERROR,
                message="The question is not currently available for an answer.",
            )
        without_correction_target = tuple(
            answer for answer in answers if answer.question_id != question_id
        )
        correction_result = self._engine.evaluate(
            self._engine_input(
                intake,
                instances,
                without_correction_target,
                language=language,
            )
        )
        if not self._is_selected_question(correction_result, question_id, question_version):
            raise ApplicationError(
                code=ErrorCode.VALIDATION_ERROR,
                message="The question is not currently available for correction.",
            )

    async def submit_answer(
        self,
        intake_id: OpaqueId,
        value: PatientAnswerInput,
        *,
        expected_version: int,
        language: str,
    ) -> IntakeSnapshot:
        if value.source_type is IntakeAnswerSourceType.REUSED_HISTORY:
            raise ApplicationError(
                code=ErrorCode.VALIDATION_ERROR, message="The answer source is invalid."
            )
        database = self._database_required()
        now = self._now()
        try:
            async with database.transaction() as transaction:
                intake = await self._intakes.get(transaction, intake_id)
                if intake is None:
                    raise ApplicationError(
                        code=ErrorCode.RESOURCE_NOT_FOUND,
                        message="The requested intake was not found.",
                    )
                if intake.status is not ClinicalIntakeStatus.IN_PROGRESS:
                    raise ApplicationError(
                        code=ErrorCode.INVALID_STATE_TRANSITION,
                        message="This intake no longer accepts answers.",
                    )
                if intake.version != expected_version:
                    raise ApplicationError(
                        code=ErrorCode.RESOURCE_CONFLICT,
                        message="The intake changed before the answer was saved.",
                    )
                answers = await self._answers.list_for_intake(transaction, intake_id)
                instances = await self._instances.list_for_encounter(
                    transaction, intake.encounter_id
                )
                self._require_answer_authority(
                    intake,
                    instances,
                    answers,
                    question_id=value.question_id,
                    question_version=value.question_version,
                    language=language,
                )
                answered_at = self._next_timestamp(now, answers)
                answer = IntakeAnswer(
                    answer_id=OpaqueId.new(),
                    intake_id=intake_id,
                    question_id=value.question_id,
                    question_version=value.question_version,
                    answer_type=value.answer_type,
                    value=value.value,
                    selected_option_ids=value.selected_option_ids,
                    unit=value.unit,
                    response_disposition=value.response_disposition,
                    language_code=value.language_code,
                    source_type=value.source_type,
                    answered_at=answered_at,
                    created_at=answered_at,
                    original_text=value.original_text,
                )
                proposed = (*answers, answer)
                engine_input = self._engine_input(intake, instances, proposed, language=language)
                # This is the single supported P7-B validation path.
                result = self._engine.evaluate(engine_input)
                projected = self._project(intake, proposed)
                projected = replace(
                    projected, missing_information=self._engine.missing_information(engine_input)
                )
                # Acquire the aggregate's optimistic-write lock before persisting child rows.
                # This gives competing submissions one lock order and lets a stale loser fail
                # as a resource conflict instead of waiting on child-row locks until timeout.
                saved = await self._intakes.save(
                    transaction, projected, expected_version=expected_version, updated_at=now
                )
                await self._answers.add(transaction, answer)
                updated_instances = []
                next_question_id = getattr(getattr(result, "question", None), "question_id", None)
                owner_found = False
                for instance in instances:
                    pack = self._registry.get(
                        instance.questionnaire_id, instance.questionnaire_version
                    )
                    owns_answer = pack is not None and any(
                        question.question_id == answer.question_id
                        and question.question_version == answer.question_version
                        for question in pack.questions
                    )
                    if owns_answer:
                        owner_found = True
                    refs = instance.responses.answer_refs
                    skipped = instance.responses.skipped_question_refs
                    if owns_answer:
                        if answer.response_disposition is ResponseDisposition.ANSWERED:
                            refs = (
                                *refs,
                                AnswerReference(
                                    answer.question_id, answer.question_version, answer.answer_id
                                ),
                            )
                        else:
                            skipped = (
                                *skipped,
                                SkippedQuestionReference(
                                    answer.question_id,
                                    answer.question_version,
                                    answer.response_disposition,
                                ),
                            )
                    updated = replace(
                        instance,
                        responses=replace(
                            instance.responses,
                            answer_refs=refs,
                            skipped_question_refs=skipped,
                            last_selected_question_id=next_question_id
                            if next_question_id
                            and pack is not None
                            and any(q.question_id == next_question_id for q in pack.questions)
                            else instance.responses.last_selected_question_id,
                            engine_version=ENGINE_VERSION,
                        ),
                    )
                    await self._instances.save(transaction, updated)
                    updated_instances.append(updated)
                if not owner_found:
                    raise ApplicationError(
                        code=ErrorCode.VALIDATION_ERROR,
                        message="The question is not part of this intake.",
                    )
                return IntakeSnapshot(saved, proposed, tuple(updated_instances), result)
        except InvalidAnswerForQuestionError as error:
            raise ApplicationError(
                code=ErrorCode.VALIDATION_ERROR,
                message="The answer does not match the active question.",
                cause=error,
            ) from error
        except StaleClinicalIntakeWriteError as error:
            raise ApplicationError(
                code=ErrorCode.RESOURCE_CONFLICT,
                message="The intake changed before the answer was saved.",
                cause=error,
            ) from error

    async def record_answer(
        self, intake_id: OpaqueId, answer: IntakeAnswer, *, expected_version: int
    ) -> ClinicalIntake:
        snapshot = await self.submit_answer(
            intake_id,
            PatientAnswerInput(
                question_id=answer.question_id,
                question_version=answer.question_version,
                answer_type=answer.answer_type,
                value=answer.value,
                selected_option_ids=answer.selected_option_ids,
                unit=answer.unit,
                response_disposition=answer.response_disposition,
                language_code=answer.language_code,
                source_type=answer.source_type,
                original_text=answer.original_text,
            ),
            expected_version=expected_version,
            language=answer.language_code,
        )
        return snapshot.intake

    async def complete_snapshot(
        self, intake_id: OpaqueId, *, expected_version: int, language: str
    ) -> IntakeSnapshot:
        database = self._database_required()
        now = self._now()
        try:
            async with database.transaction() as transaction:
                intake = await self._intakes.get(transaction, intake_id)
                if intake is None:
                    raise ApplicationError(
                        code=ErrorCode.RESOURCE_NOT_FOUND,
                        message="The requested intake was not found.",
                    )
                answers = await self._answers.list_for_intake(transaction, intake_id)
                instances = await self._instances.list_for_encounter(
                    transaction, intake.encounter_id
                )
                if intake.status is ClinicalIntakeStatus.COMPLETED:
                    return IntakeSnapshot(
                        intake,
                        answers,
                        instances,
                        self._result(intake, instances, answers, language=language),
                    )
                if intake.status is not ClinicalIntakeStatus.IN_PROGRESS:
                    raise ApplicationError(
                        code=ErrorCode.INVALID_STATE_TRANSITION,
                        message="This intake cannot be completed.",
                    )
                if intake.version != expected_version:
                    raise ApplicationError(
                        code=ErrorCode.RESOURCE_CONFLICT,
                        message="The intake changed before completion.",
                    )
                result = self._engine.evaluate(
                    self._engine_input(intake, instances, answers, language=language)
                )
                if not isinstance(result, CompletionReady):
                    raise ApplicationError(
                        code=ErrorCode.INSUFFICIENT_INFORMATION,
                        message="Required intake information is still missing.",
                    )
                completed = intake.transition_to(ClinicalIntakeStatus.COMPLETED, at=now)
                completed = await self._intakes.save(
                    transaction, completed, expected_version=expected_version, updated_at=now
                )
                completed_instances = []
                for instance in instances:
                    updated = replace(
                        instance, status=QuestionnaireStatus.COMPLETED, completed_at=now
                    )
                    await self._instances.save(transaction, updated)
                    completed_instances.append(updated)
                return IntakeSnapshot(
                    completed, answers, tuple(completed_instances), CompletionReady()
                )
        except StaleClinicalIntakeWriteError as error:
            raise ApplicationError(
                code=ErrorCode.RESOURCE_CONFLICT,
                message="The intake changed before completion.",
                cause=error,
            ) from error

    async def complete_intake(
        self, intake_id: OpaqueId, *, expected_version: int
    ) -> ClinicalIntake:
        return (
            await self.complete_snapshot(
                intake_id, expected_version=expected_version, language="en"
            )
        ).intake

    async def next_question(self, intake_id: OpaqueId) -> EngineResult:
        return (await self.get_snapshot(intake_id, language="en")).engine_result
