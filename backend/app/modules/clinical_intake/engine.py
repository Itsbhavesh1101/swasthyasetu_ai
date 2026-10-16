"""Pure deterministic P7-B adaptive intake engine."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID, uuid5

from app.modules.clinical_intake.contracts import (
    AnswerType,
    DateValidation,
    DurationValidation,
    IntakeAnswer,
    IntakeAnswerSourceType,
    NumericValidation,
    OptionValidation,
    PackRegistry,
    QuestionDefinition,
    QuestionPack,
    ResponseDisposition,
    RuleDefinition,
    SeverityValidation,
    TextValidation,
)
from app.modules.clinical_intake.domain import (
    ClinicalIntake,
    ClinicalIntakeStatus,
    Contradiction,
    ContradictionStatus,
    MissingInformation,
    MissingReason,
    Requiredness,
    ResolutionState,
)
from app.modules.clinical_intake.history import HistoryContext, reusable_history
from app.modules.clinical_intake.rules import RuleEvaluationContext, evaluate_rule
from app.shared.types import OpaqueId

ENGINE_VERSION = "deterministic-intake.v1"
_MISSING_NAMESPACE = UUID("f64310f3-d714-5bd8-9db8-b3dadcc3c2a2")


class InvalidEngineInputError(ValueError):
    """Raised for inconsistent immutable engine input."""


class InvalidAnswerForQuestionError(ValueError):
    """Raised when an answer fails its registered question contract."""


@dataclass(frozen=True, slots=True)
class EngineInput:
    intake: ClinicalIntake
    selected_pack_identities: tuple[tuple[str, str], ...]
    answers: tuple[IntakeAnswer, ...] = ()
    history: tuple[HistoryContext, ...] = ()
    contradictions: tuple[Contradiction, ...] = ()
    language: str | None = None

    def __post_init__(self) -> None:
        if self.intake.status is not ClinicalIntakeStatus.IN_PROGRESS:
            raise InvalidEngineInputError("engine requires an in-progress intake")
        for value in (
            self.selected_pack_identities,
            self.answers,
            self.history,
            self.contradictions,
        ):
            if not isinstance(value, tuple):
                raise InvalidEngineInputError("engine collections must be immutable tuples")
        if any(
            not isinstance(identity, tuple)
            or len(identity) != 2
            or any(not isinstance(item, str) for item in identity)
            for identity in self.selected_pack_identities
        ):
            raise InvalidEngineInputError("selected pack identities are invalid")
        if any(not isinstance(answer, IntakeAnswer) for answer in self.answers):
            raise InvalidEngineInputError("engine answers are invalid")
        if any(not isinstance(item, HistoryContext) for item in self.history):
            raise InvalidEngineInputError("engine history is invalid")
        if any(not isinstance(item, Contradiction) for item in self.contradictions):
            raise InvalidEngineInputError("engine contradictions are invalid")


@dataclass(frozen=True, slots=True)
class NextQuestion:
    question: QuestionDefinition
    pack_id: str
    pack_version: str
    reason_rule_ids: tuple[str, ...]
    engine_version: str = ENGINE_VERSION


@dataclass(frozen=True, slots=True)
class ClarificationRequired:
    contradiction_id: OpaqueId
    question: QuestionDefinition
    pack_id: str
    pack_version: str
    reason_rule_ids: tuple[str, ...]
    engine_version: str = ENGINE_VERSION


@dataclass(frozen=True, slots=True)
class CompletionReady:
    missing_information: tuple[MissingInformation, ...] = ()
    engine_version: str = ENGINE_VERSION


@dataclass(frozen=True, slots=True)
class Incomplete:
    missing_information: tuple[MissingInformation, ...]
    engine_version: str = ENGINE_VERSION


type EngineResult = NextQuestion | ClarificationRequired | CompletionReady | Incomplete


def _invalid_answer() -> InvalidAnswerForQuestionError:
    return InvalidAnswerForQuestionError("answer does not satisfy registered question contract")


def _validate_answer(
    answer: IntakeAnswer,
    question: QuestionDefinition,
    *,
    intake_id: OpaqueId,
) -> None:
    if (
        answer.intake_id != intake_id
        or answer.question_version != question.question_version
        or answer.answer_type is not question.answer_type
    ):
        raise _invalid_answer()
    disposition = answer.response_disposition
    if disposition is ResponseDisposition.UNKNOWN:
        if not question.allow_unknown:
            raise _invalid_answer()
        return
    if disposition is ResponseDisposition.PREFER_NOT_TO_ANSWER:
        if not question.allow_prefer_not_to_answer:
            raise _invalid_answer()
        return
    if disposition is ResponseDisposition.SKIPPED:
        if not question.allow_skip and question.requiredness is not Requiredness.OPTIONAL:
            raise _invalid_answer()
        return
    validation = question.validation
    if question.answer_type is AnswerType.TEXT:
        if not isinstance(validation, TextValidation) or not isinstance(answer.value, str):
            raise _invalid_answer()
        if not validation.min_length <= len(answer.value) <= validation.max_length:
            raise _invalid_answer()
    elif question.answer_type in {AnswerType.SINGLE_CHOICE, AnswerType.MULTI_CHOICE}:
        if not isinstance(validation, OptionValidation) or answer.selected_option_ids is None:
            raise _invalid_answer()
        selected = answer.selected_option_ids
        if len(set(selected)) != len(selected) or not set(selected).issubset(
            validation.allowed_option_ids
        ):
            raise _invalid_answer()
    elif question.answer_type is AnswerType.NUMBER:
        if not isinstance(validation, NumericValidation) or not isinstance(answer.value, Decimal):
            raise _invalid_answer()
        if validation.minimum is not None and answer.value < validation.minimum:
            raise _invalid_answer()
        if validation.maximum is not None and answer.value > validation.maximum:
            raise _invalid_answer()
        if answer.unit != validation.unit:
            raise _invalid_answer()
    elif question.answer_type is AnswerType.DATE:
        if not isinstance(validation, DateValidation) or type(answer.value) is not date:
            raise _invalid_answer()
        if validation.earliest is not None and answer.value < validation.earliest:
            raise _invalid_answer()
        if validation.latest is not None and answer.value > validation.latest:
            raise _invalid_answer()
    elif question.answer_type is AnswerType.DURATION:
        if not isinstance(validation, DurationValidation) or not isinstance(answer.value, Decimal):
            raise _invalid_answer()
        if answer.unit not in validation.allowed_units:
            raise _invalid_answer()
        if answer.value < validation.minimum:
            raise _invalid_answer()
        if validation.maximum is not None and answer.value > validation.maximum:
            raise _invalid_answer()
    elif question.answer_type is AnswerType.SEVERITY_SCALE:
        if (
            not isinstance(validation, SeverityValidation)
            or answer.value not in validation.allowed_values
        ):
            raise _invalid_answer()


def _latest_answers(answers: tuple[IntakeAnswer, ...]) -> dict[str, IntakeAnswer]:
    latest: dict[str, IntakeAnswer] = {}
    for answer in answers:
        current = latest.get(answer.question_id)
        if current is None or (answer.answered_at, answer.answer_id.value.int) > (
            current.answered_at,
            current.answer_id.value.int,
        ):
            latest[answer.question_id] = answer
    return latest


def _rules(pack: QuestionPack) -> dict[str, RuleDefinition]:
    return {rule.rule_id: rule for rule in pack.applicability_rules + pack.contradiction_rules}


def _applicable(
    question: QuestionDefinition,
    pack: QuestionPack,
    context: RuleEvaluationContext,
) -> bool:
    rules = _rules(pack)
    return all(
        evaluate_rule(rules[rule_id], rules, context) for rule_id in question.applicability_rule_ids
    )


def _matching_history(
    question: QuestionDefinition, history: tuple[HistoryContext, ...]
) -> tuple[HistoryContext, ...]:
    binding = question.history_binding
    if binding is None:
        return ()
    matches = tuple(
        item
        for item in reusable_history(history)
        if item.fact_type == binding.fact_type and item.section_key == binding.section_key
    )
    policy = question.history_reuse_policy
    if policy is None:
        return matches
    return tuple(
        item for item in matches if item.verification_state in policy.eligible_verification_states
    )


def _history_suppresses(question: QuestionDefinition, history: tuple[HistoryContext, ...]) -> bool:
    policy = question.history_reuse_policy
    if policy is None or not policy.suppress_question or policy.confirmation_required:
        return False
    return any(
        item.verification_state in policy.eligible_verification_states
        for item in _matching_history(question, history)
    )


def _missing_id(
    pack: QuestionPack, question: QuestionDefinition, reason: MissingReason
) -> OpaqueId:
    rule_id = (
        question.applicability_rule_ids[0]
        if question.applicability_rule_ids
        else (f"required:{question.question_id}")
    )
    identity = "|".join(
        (ENGINE_VERSION, pack.pack_id, pack.version, question.question_id, reason.value, rule_id)
    )
    return OpaqueId(uuid5(_MISSING_NAMESPACE, identity))


class AdaptiveIntakeEngine:
    def __init__(self, registry: PackRegistry) -> None:
        self._registry = registry

    def _prepare(
        self, engine_input: EngineInput
    ) -> tuple[tuple[QuestionPack, ...], dict[str, IntakeAnswer], RuleEvaluationContext]:
        packs = self._registry.activate(
            engine_input.selected_pack_identities,
            language=engine_input.language,
        )
        questions = {
            (question.question_id, question.question_version): question
            for pack in packs
            for question in pack.questions
        }
        for answer in engine_input.answers:
            question = questions.get((answer.question_id, answer.question_version))
            if question is None:
                raise _invalid_answer()
            _validate_answer(answer, question, intake_id=engine_input.intake.intake_id)
        latest = _latest_answers(engine_input.answers)
        context = RuleEvaluationContext(
            answers={
                key: answer
                for key, answer in latest.items()
                if answer.source_type is not IntakeAnswerSourceType.REUSED_HISTORY
            },
            history=engine_input.history,
            contradictions=engine_input.contradictions,
        )
        return packs, latest, context

    def missing_information(self, engine_input: EngineInput) -> tuple[MissingInformation, ...]:
        packs, latest, context = self._prepare(engine_input)
        missing: list[MissingInformation] = []
        for pack in packs:
            rules = _rules(pack)
            for contradiction in sorted(
                engine_input.contradictions,
                key=lambda value: (
                    value.source_pack_id,
                    value.source_rule_id,
                    value.field_key,
                    value.contradiction_id.value.int,
                ),
            ):
                if (
                    contradiction.status is ContradictionStatus.RESOLVED
                    or contradiction.source_pack_id != pack.pack_id
                    or contradiction.source_rule_id not in rules
                    or not evaluate_rule(rules[contradiction.source_rule_id], rules, context)
                ):
                    continue
                clarification = next(
                    (
                        question
                        for question in pack.questions
                        if contradiction.source_rule_id in question.clarification_rule_ids
                    ),
                    None,
                )
                if clarification is None:
                    continue
                identity = "|".join(
                    (
                        ENGINE_VERSION,
                        pack.pack_id,
                        pack.version,
                        contradiction.field_key,
                        MissingReason.CLARIFICATION_REQUIRED.value,
                        contradiction.source_rule_id,
                        str(contradiction.contradiction_id),
                    )
                )
                missing.append(
                    MissingInformation(
                        missing_id=OpaqueId(uuid5(_MISSING_NAMESPACE, identity)),
                        field_or_question_key=contradiction.field_key,
                        reason_code=MissingReason.CLARIFICATION_REQUIRED,
                        requiredness=Requiredness.REQUIRED,
                        source_pack_id=pack.pack_id,
                        source_pack_version=pack.version,
                        source_rule_id=contradiction.source_rule_id,
                        resolution_state=ResolutionState.OPEN,
                    )
                )
            for question in sorted(
                pack.questions, key=lambda value: (value.order, value.question_id)
            ):
                if question.requiredness is Requiredness.OPTIONAL or not _applicable(
                    question, pack, context
                ):
                    continue
                answer = latest.get(question.question_id)
                if (
                    answer is not None
                    and answer.source_type is not IntakeAnswerSourceType.REUSED_HISTORY
                ):
                    continue
                matching_history = _matching_history(question, engine_input.history)
                if _history_suppresses(question, engine_input.history):
                    continue
                policy = question.history_reuse_policy
                confirmation_required = bool(matching_history) and (
                    policy is None or policy.confirmation_required
                )
                reason = (
                    MissingReason.RECONFIRMATION_REQUIRED
                    if confirmation_required
                    else MissingReason.CONDITIONAL_UNANSWERED
                    if question.requiredness is Requiredness.CONDITIONAL
                    else MissingReason.REQUIRED_UNANSWERED
                )
                rule_id = (
                    question.applicability_rule_ids[0]
                    if question.applicability_rule_ids
                    else f"required:{question.question_id}"
                )
                missing.append(
                    MissingInformation(
                        missing_id=_missing_id(pack, question, reason),
                        field_or_question_key=question.question_id,
                        reason_code=reason,
                        requiredness=question.requiredness,
                        source_pack_id=pack.pack_id,
                        source_pack_version=pack.version,
                        source_rule_id=rule_id,
                        resolution_state=ResolutionState.OPEN,
                    )
                )
        return tuple(missing)

    def evaluate(self, engine_input: EngineInput) -> EngineResult:
        packs, latest, context = self._prepare(engine_input)
        clarifications: list[
            tuple[int, int, str, str, int, Contradiction, QuestionDefinition, QuestionPack]
        ] = []
        for pack in packs:
            rules = _rules(pack)
            for contradiction in engine_input.contradictions:
                if (
                    contradiction.status is ContradictionStatus.RESOLVED
                    or contradiction.source_pack_id != pack.pack_id
                    or contradiction.source_rule_id not in rules
                ):
                    continue
                rule = rules[contradiction.source_rule_id]
                if not evaluate_rule(rule, rules, context):
                    continue
                for question in pack.questions:
                    if contradiction.source_rule_id in question.clarification_rule_ids:
                        clarifications.append(
                            (
                                pack.order,
                                question.order,
                                pack.pack_id,
                                question.question_id,
                                contradiction.contradiction_id.value.int,
                                contradiction,
                                question,
                                pack,
                            )
                        )
        if clarifications:
            _, _, _, _, _, contradiction, question, pack = min(
                clarifications, key=lambda item: item[:5]
            )
            return ClarificationRequired(
                contradiction_id=contradiction.contradiction_id,
                question=question,
                pack_id=pack.pack_id,
                pack_version=pack.version,
                reason_rule_ids=(contradiction.source_rule_id,),
            )

        missing = self.missing_information(engine_input)
        missing_keys = {item.field_or_question_key for item in missing}
        candidates: list[tuple[int, int, str, str, QuestionDefinition, QuestionPack]] = []
        for pack in packs:
            for question in pack.questions:
                if question.question_id not in missing_keys or not _applicable(
                    question, pack, context
                ):
                    continue
                if any(
                    dependency not in latest
                    or latest[dependency].source_type is IntakeAnswerSourceType.REUSED_HISTORY
                    for dependency in question.dependency_question_ids
                ):
                    continue
                candidates.append(
                    (
                        pack.order,
                        question.order,
                        pack.pack_id,
                        question.question_id,
                        question,
                        pack,
                    )
                )
        if candidates:
            _, _, _, _, question, pack = min(candidates, key=lambda item: item[:4])
            return NextQuestion(
                question=question,
                pack_id=pack.pack_id,
                pack_version=pack.version,
                reason_rule_ids=question.applicability_rule_ids
                or (f"required:{question.question_id}",),
            )
        if missing:
            return Incomplete(missing)
        return CompletionReady()
