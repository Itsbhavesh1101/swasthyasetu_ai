"""Pure deterministic P7-B engine behavior using synthetic machine-only packs."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest

from app.modules.clinical_intake.contracts import (
    AnswerType,
    ApprovalState,
    DateValidation,
    DurationValidation,
    HistoryBinding,
    HistoryReusePolicy,
    InputMode,
    IntakeAnswer,
    IntakeAnswerSourceType,
    NumericValidation,
    OptionValidation,
    PackRegistry,
    QuestionDefinition,
    QuestionPack,
    QuestionPackKind,
    QuestionSection,
    ResponseDisposition,
    RuleDefinition,
    RuleOperator,
    SeverityValidation,
    TextValidation,
)
from app.modules.clinical_intake.domain import (
    ClinicalIntake,
    ClinicalIntakeStatus,
    Contradiction,
    ContradictionStatus,
    MissingReason,
    Requiredness,
    SourceReference,
)
from app.modules.clinical_intake.engine import (
    ENGINE_VERSION,
    AdaptiveIntakeEngine,
    ClarificationRequired,
    CompletionReady,
    EngineInput,
    Incomplete,
    NextQuestion,
)
from app.modules.clinical_intake.history import HistoryContext
from app.modules.clinical_intake.rules import RuleEvaluationContext, evaluate_rule
from app.modules.provenance.domain import VerificationState
from app.shared.types import OpaqueId

NOW = datetime(2026, 10, 17, 10, tzinfo=UTC)


def _question(
    question_id: str,
    *,
    answer_type: AnswerType = AnswerType.TEXT,
    validation: object = TextValidation(1, 80),
    requiredness: Requiredness = Requiredness.REQUIRED,
    order: int = 0,
    applicability: tuple[str, ...] = (),
    dependencies: tuple[str, ...] = (),
    allow_unknown: bool = False,
    allow_prefer_not_to_answer: bool = False,
    allow_skip: bool = False,
    history_binding: HistoryBinding | None = None,
    history_reuse_policy: HistoryReusePolicy | None = None,
    clarification_rule_ids: tuple[str, ...] = (),
) -> QuestionDefinition:
    return QuestionDefinition(
        question_id=question_id,
        question_version="1.0.0",
        section=QuestionSection.EXTENSION,
        content_key=f"{question_id}.prompt",
        answer_type=answer_type,
        requiredness=requiredness,
        input_modes=(InputMode.TEXT, InputMode.TOUCH),
        validation=validation,  # type: ignore[arg-type]
        order=order,
        applicability_rule_ids=applicability,
        dependency_question_ids=dependencies,
        allow_unknown=allow_unknown,
        allow_prefer_not_to_answer=allow_prefer_not_to_answer,
        allow_skip=allow_skip,
        history_binding=history_binding,
        history_reuse_policy=history_reuse_policy,
        clarification_rule_ids=clarification_rule_ids,
    )


def _pack(
    pack_id: str,
    questions: tuple[QuestionDefinition, ...],
    *,
    kind: QuestionPackKind = QuestionPackKind.CORE,
    order: int = 0,
    approval: ApprovalState = ApprovalState.APPROVED,
    applicability_rules: tuple[RuleDefinition, ...] = (),
    contradiction_rules: tuple[RuleDefinition, ...] = (),
) -> QuestionPack:
    return QuestionPack(
        pack_id=pack_id,
        version="1.0.0",
        kind=kind,
        approval_state=approval,
        content_version="1.0.0",
        supported_languages=("en",),
        questions=questions,
        order=order,
        applicability_rules=applicability_rules,
        contradiction_rules=contradiction_rules,
    )


def _intake() -> ClinicalIntake:
    return ClinicalIntake(
        intake_id=OpaqueId.parse("00000000-0000-4000-8000-000000000001"),
        encounter_id=OpaqueId.parse("00000000-0000-4000-8000-000000000002"),
        status=ClinicalIntakeStatus.IN_PROGRESS,
        started_at=NOW,
        version=1,
    )


def _answer(
    intake: ClinicalIntake,
    question: QuestionDefinition,
    *,
    answer_id: str = "00000000-0000-4000-8000-000000000010",
    answered_at: datetime = NOW,
    value: str | bool | Decimal | date | None = "synthetic",
    selected: tuple[str, ...] | None = None,
    unit: str | None = None,
    disposition: ResponseDisposition = ResponseDisposition.ANSWERED,
    source_type: IntakeAnswerSourceType = IntakeAnswerSourceType.PATIENT_TOUCH,
) -> IntakeAnswer:
    return IntakeAnswer(
        answer_id=OpaqueId.parse(answer_id),
        intake_id=intake.intake_id,
        question_id=question.question_id,
        question_version=question.question_version,
        answer_type=question.answer_type,
        value=value,
        selected_option_ids=selected,
        unit=unit,
        response_disposition=disposition,
        language_code="en",
        source_type=source_type,
        answered_at=answered_at,
        created_at=answered_at,
    )


def _input(
    intake: ClinicalIntake,
    packs: tuple[QuestionPack, ...],
    *,
    answers: tuple[IntakeAnswer, ...] = (),
    history: tuple[HistoryContext, ...] = (),
    contradictions: tuple[Contradiction, ...] = (),
) -> EngineInput:
    return EngineInput(
        intake=intake,
        selected_pack_identities=tuple((pack.pack_id, pack.version) for pack in packs),
        answers=answers,
        history=history,
        contradictions=contradictions,
        language="en",
    )


def test_selection_is_repeatable_and_uses_canonical_tie_breaks() -> None:
    intake = _intake()
    pack_z = _pack("synthetic.z", (_question("synthetic.z.question", order=1),), order=0)
    pack_a = _pack(
        "synthetic.a",
        (_question("synthetic.b", order=1), _question("synthetic.a", order=1)),
        order=0,
    )
    engine = AdaptiveIntakeEngine(PackRegistry((pack_z, pack_a)))
    reverse_registry_engine = AdaptiveIntakeEngine(PackRegistry((pack_a, pack_z)))
    first = engine.evaluate(_input(intake, (pack_z, pack_a)))
    perturbed = engine.evaluate(_input(intake, (pack_a, pack_z)))

    assert first == perturbed
    assert first == reverse_registry_engine.evaluate(_input(intake, (pack_z, pack_a)))
    assert all(engine.evaluate(_input(intake, (pack_z, pack_a))) == first for _ in range(100))
    assert isinstance(first, NextQuestion)
    assert first.pack_id == "synthetic.a"
    assert first.question.question_id == "synthetic.a"
    assert first.engine_version == ENGINE_VERSION == "deterministic-intake.v1"


def test_newest_answer_selection_is_input_order_independent() -> None:
    intake = _intake()
    first_question = _question("synthetic.first", order=0)
    second_question = _question("synthetic.second", order=1)
    pack = _pack("synthetic.core", (first_question, second_question))
    older = _answer(intake, first_question, answered_at=NOW)
    newer = _answer(
        intake,
        first_question,
        answer_id="00000000-0000-4000-8000-000000000011",
        answered_at=NOW + timedelta(minutes=1),
    )
    engine = AdaptiveIntakeEngine(PackRegistry((pack,)))

    assert engine.evaluate(_input(intake, (pack,), answers=(older, newer))) == engine.evaluate(
        _input(intake, (pack,), answers=(newer, older))
    )
    result = engine.evaluate(_input(intake, (pack,), answers=(newer, older)))
    assert isinstance(result, NextQuestion)
    assert result.question == second_question


def test_answer_identifier_breaks_equal_timestamp_ties_deterministically() -> None:
    intake = _intake()
    trigger = _question("synthetic.trigger", requiredness=Requiredness.OPTIONAL)
    rule = RuleDefinition(
        "synthetic.answer.yes",
        RuleOperator.EQUALS,
        ("question:synthetic.trigger", "value:yes"),
    )
    conditional = _question(
        "synthetic.conditional",
        requiredness=Requiredness.CONDITIONAL,
        applicability=(rule.rule_id,),
    )
    pack = _pack("synthetic.core", (trigger, conditional), applicability_rules=(rule,))
    earlier_id = _answer(
        intake,
        trigger,
        answer_id="00000000-0000-4000-8000-000000000010",
        value="no",
    )
    later_id = _answer(
        intake,
        trigger,
        answer_id="00000000-0000-4000-8000-000000000011",
        value="yes",
    )
    engine = AdaptiveIntakeEngine(PackRegistry((pack,)))

    first = engine.evaluate(_input(intake, (pack,), answers=(earlier_id, later_id)))
    reversed_result = engine.evaluate(_input(intake, (pack,), answers=(later_id, earlier_id)))

    assert first == reversed_result
    assert isinstance(first, NextQuestion)
    assert first.question == conditional


@pytest.mark.parametrize(
    ("operator", "operands", "expected"),
    [
        (RuleOperator.EXISTS, ("question:synthetic.choice",), True),
        (RuleOperator.EQUALS, ("question:synthetic.choice", "option:yes"), True),
        (RuleOperator.IN, ("question:synthetic.choice", "option:no", "option:yes"), True),
        (
            RuleOperator.ANSWER_DISPOSITION,
            ("question:synthetic.choice", "disposition:ANSWERED"),
            True,
        ),
        (RuleOperator.HISTORY_AVAILABLE, ("history:synthetic.history",), True),
        (RuleOperator.CONTRADICTION_STATE, ("contradiction:synthetic.choice", "state:OPEN"), True),
    ],
)
def test_leaf_rule_operators_have_explicit_true_and_false_semantics(
    operator: RuleOperator, operands: tuple[str, ...], expected: bool
) -> None:
    intake = _intake()
    question = _question(
        "synthetic.choice",
        answer_type=AnswerType.SINGLE_CHOICE,
        validation=OptionValidation(("yes", "no")),
    )
    answer = _answer(intake, question, value=None, selected=("yes",))
    history = HistoryContext(
        fact_id=OpaqueId.new(),
        fact_type="PROBLEM",
        section_key="synthetic.history",
        display_value="Synthetic history",
        verification_state=VerificationState.PATIENT_CONFIRMED,
    )
    contradiction = Contradiction(
        contradiction_id=OpaqueId.new(),
        field_key="synthetic.choice",
        left_ref=SourceReference(answer_id=answer.answer_id),
        right_ref=SourceReference(
            fact_id=history.fact_id,
            verification_state=history.verification_state.value,
        ),
        source_pack_id="synthetic.core",
        source_rule_id="synthetic.conflict",
        status=ContradictionStatus.OPEN,
        created_at=NOW,
    )
    context = RuleEvaluationContext(
        answers={question.question_id: answer},
        history=(history,),
        contradictions=(contradiction,),
    )
    rule = RuleDefinition("synthetic.rule", operator, operands)

    assert evaluate_rule(rule, {rule.rule_id: rule}, context) is expected
    empty_context = RuleEvaluationContext(answers={}, history=(), contradictions=())
    assert evaluate_rule(rule, {rule.rule_id: rule}, empty_context) is False


def test_boolean_rule_operators_are_composed_without_expression_execution() -> None:
    context = RuleEvaluationContext(answers={}, history=(), contradictions=())
    rules = {
        "synthetic.exists": RuleDefinition(
            "synthetic.exists", RuleOperator.EXISTS, ("question:synthetic.question",)
        ),
        "synthetic.not": RuleDefinition(
            "synthetic.not", RuleOperator.NOT, ("rule:synthetic.exists",)
        ),
        "synthetic.and": RuleDefinition(
            "synthetic.and",
            RuleOperator.AND,
            ("rule:synthetic.not", "rule:synthetic.not"),
        ),
        "synthetic.or": RuleDefinition(
            "synthetic.or",
            RuleOperator.OR,
            ("rule:synthetic.exists", "rule:synthetic.not"),
        ),
    }
    assert evaluate_rule(rules["synthetic.not"], rules, context) is True
    assert evaluate_rule(rules["synthetic.and"], rules, context) is True
    assert evaluate_rule(rules["synthetic.or"], rules, context) is True
    populated = RuleEvaluationContext(
        answers={"synthetic.question": _answer(_intake(), _question("synthetic.question"))},
        history=(),
        contradictions=(),
    )
    assert evaluate_rule(rules["synthetic.not"], rules, populated) is False
    assert evaluate_rule(rules["synthetic.and"], rules, populated) is False
    assert (
        evaluate_rule(
            replace(
                rules["synthetic.or"],
                operands=("rule:synthetic.exists", "rule:synthetic.exists"),
            ),
            rules,
            context,
        )
        is False
    )


@pytest.mark.parametrize(
    ("question", "answer_kwargs"),
    [
        (_question("synthetic.text"), {"value": "synthetic"}),
        (
            _question(
                "synthetic.single",
                answer_type=AnswerType.SINGLE_CHOICE,
                validation=OptionValidation(("one", "two")),
            ),
            {"value": None, "selected": ("one",)},
        ),
        (
            _question(
                "synthetic.multi",
                answer_type=AnswerType.MULTI_CHOICE,
                validation=OptionValidation(("one", "two")),
            ),
            {"value": None, "selected": ("one", "two")},
        ),
        (
            _question("synthetic.boolean", answer_type=AnswerType.BOOLEAN, validation=None),
            {"value": True},
        ),
        (
            _question(
                "synthetic.number",
                answer_type=AnswerType.NUMBER,
                validation=NumericValidation(Decimal("1"), Decimal("2"), "unit"),
            ),
            {"value": Decimal("1.5"), "unit": "unit"},
        ),
        (
            _question(
                "synthetic.date",
                answer_type=AnswerType.DATE,
                validation=DateValidation(date(2026, 1, 1), date(2026, 1, 31)),
            ),
            {"value": date(2026, 1, 15)},
        ),
        (
            _question(
                "synthetic.duration",
                answer_type=AnswerType.DURATION,
                validation=DurationValidation(("day",), Decimal("1"), Decimal("5")),
            ),
            {"value": Decimal("2"), "unit": "day"},
        ),
        (
            _question(
                "synthetic.severity",
                answer_type=AnswerType.SEVERITY_SCALE,
                validation=SeverityValidation(
                    "synthetic.scale", "1.0.0", (Decimal("1"), Decimal("2"))
                ),
            ),
            {"value": Decimal("2")},
        ),
    ],
)
def test_every_answer_type_accepts_a_valid_registered_value(
    question: QuestionDefinition, answer_kwargs: dict[str, object]
) -> None:
    intake = _intake()
    pack = _pack("synthetic.core", (question,))
    answer = _answer(intake, question, **answer_kwargs)  # type: ignore[arg-type]
    assert isinstance(
        AdaptiveIntakeEngine(PackRegistry((pack,))).evaluate(
            _input(intake, (pack,), answers=(answer,))
        ),
        CompletionReady,
    )


def test_answer_validation_rejects_sensitive_value_without_echo() -> None:
    intake = _intake()
    question = _question("synthetic.text", validation=TextValidation(3, 5))
    pack = _pack("synthetic.core", (question,))
    answer = _answer(intake, question, value="private-payload")

    with pytest.raises(ValueError) as raised:
        AdaptiveIntakeEngine(PackRegistry((pack,))).evaluate(
            _input(intake, (pack,), answers=(answer,))
        )
    assert raised.type.__name__ == "InvalidAnswerForQuestionError"
    assert "private-payload" not in str(raised.value)


@pytest.mark.parametrize("violation", ["foreign_intake", "question_version", "answer_type"])
def test_answer_identity_and_type_must_match_registered_question(violation: str) -> None:
    intake = _intake()
    question = _question("synthetic.text")
    pack = _pack("synthetic.core", (question,))
    answer = _answer(intake, question)
    if violation == "foreign_intake":
        answer = replace(answer, intake_id=OpaqueId.new())
    elif violation == "question_version":
        answer = replace(answer, question_version="2.0.0")
    else:
        answer = replace(answer, answer_type=AnswerType.BOOLEAN, value=True)
    with pytest.raises(ValueError) as raised:
        AdaptiveIntakeEngine(PackRegistry((pack,))).evaluate(
            _input(intake, (pack,), answers=(answer,))
        )
    assert raised.type.__name__ == "InvalidAnswerForQuestionError"


@pytest.mark.parametrize(
    ("question", "answer_kwargs"),
    [
        (_question("synthetic.short", validation=TextValidation(3, 5)), {"value": "ab"}),
        (_question("synthetic.long", validation=TextValidation(3, 5)), {"value": "abcdef"}),
        (
            _question(
                "synthetic.single",
                answer_type=AnswerType.SINGLE_CHOICE,
                validation=OptionValidation(("one", "two")),
            ),
            {"value": None, "selected": ("unknown",)},
        ),
        (
            _question(
                "synthetic.choice",
                answer_type=AnswerType.MULTI_CHOICE,
                validation=OptionValidation(("one", "two")),
            ),
            {"value": None, "selected": ("one", "one")},
        ),
        (
            _question(
                "synthetic.number.above",
                answer_type=AnswerType.NUMBER,
                validation=NumericValidation(Decimal("1"), Decimal("2"), "unit"),
            ),
            {"value": Decimal("3"), "unit": "unit"},
        ),
        (
            _question(
                "synthetic.number.below",
                answer_type=AnswerType.NUMBER,
                validation=NumericValidation(Decimal("1"), Decimal("2"), "unit"),
            ),
            {"value": Decimal("0"), "unit": "unit"},
        ),
        (
            _question(
                "synthetic.number.unit",
                answer_type=AnswerType.NUMBER,
                validation=NumericValidation(Decimal("1"), Decimal("2"), "unit"),
            ),
            {"value": Decimal("1.5"), "unit": "other"},
        ),
        (
            _question(
                "synthetic.date.late",
                answer_type=AnswerType.DATE,
                validation=DateValidation(date(2026, 1, 1), date(2026, 1, 31)),
            ),
            {"value": date(2026, 2, 1)},
        ),
        (
            _question(
                "synthetic.date.early",
                answer_type=AnswerType.DATE,
                validation=DateValidation(date(2026, 1, 1), date(2026, 1, 31)),
            ),
            {"value": date(2025, 12, 31)},
        ),
        (
            _question(
                "synthetic.duration",
                answer_type=AnswerType.DURATION,
                validation=DurationValidation(("day",), Decimal("1"), Decimal("5")),
            ),
            {"value": Decimal("2"), "unit": "week"},
        ),
        (
            _question(
                "synthetic.duration.below",
                answer_type=AnswerType.DURATION,
                validation=DurationValidation(("day",), Decimal("1"), Decimal("5")),
            ),
            {"value": Decimal("0"), "unit": "day"},
        ),
        (
            _question(
                "synthetic.duration.above",
                answer_type=AnswerType.DURATION,
                validation=DurationValidation(("day",), Decimal("1"), Decimal("5")),
            ),
            {"value": Decimal("6"), "unit": "day"},
        ),
        (
            _question(
                "synthetic.severity",
                answer_type=AnswerType.SEVERITY_SCALE,
                validation=SeverityValidation("synthetic.scale", "1.0.0", (Decimal("1"),)),
            ),
            {"value": Decimal("2")},
        ),
    ],
)
def test_answer_constraints_reject_invalid_boundaries(
    question: QuestionDefinition, answer_kwargs: dict[str, object]
) -> None:
    intake = _intake()
    pack = _pack("synthetic.core", (question,))
    with pytest.raises(ValueError) as raised:
        AdaptiveIntakeEngine(PackRegistry((pack,))).evaluate(
            _input(intake, (pack,), answers=(_answer(intake, question, **answer_kwargs),))  # type: ignore[arg-type]
        )
    assert raised.type.__name__ == "InvalidAnswerForQuestionError"


@pytest.mark.parametrize(
    ("disposition", "question_kwargs"),
    [
        (ResponseDisposition.UNKNOWN, {}),
        (ResponseDisposition.PREFER_NOT_TO_ANSWER, {}),
        (ResponseDisposition.SKIPPED, {}),
    ],
)
def test_non_answer_dispositions_require_explicit_configuration(
    disposition: ResponseDisposition, question_kwargs: dict[str, object]
) -> None:
    intake = _intake()
    question = _question("synthetic.required", **question_kwargs)  # type: ignore[arg-type]
    pack = _pack("synthetic.core", (question,))
    answer = _answer(intake, question, value=None, disposition=disposition)
    with pytest.raises(ValueError):
        AdaptiveIntakeEngine(PackRegistry((pack,))).evaluate(
            _input(intake, (pack,), answers=(answer,))
        )


@pytest.mark.parametrize(
    ("disposition", "question"),
    [
        (
            ResponseDisposition.UNKNOWN,
            _question("synthetic.unknown", allow_unknown=True),
        ),
        (
            ResponseDisposition.PREFER_NOT_TO_ANSWER,
            _question("synthetic.refused", allow_prefer_not_to_answer=True),
        ),
        (
            ResponseDisposition.SKIPPED,
            _question(
                "synthetic.skipped",
                requiredness=Requiredness.OPTIONAL,
                allow_skip=True,
            ),
        ),
    ],
)
def test_explicitly_allowed_non_answers_are_accepted(
    disposition: ResponseDisposition, question: QuestionDefinition
) -> None:
    intake = _intake()
    pack = _pack("synthetic.core", (question,))
    answer = _answer(intake, question, value=None, disposition=disposition)
    result = AdaptiveIntakeEngine(PackRegistry((pack,))).evaluate(
        _input(intake, (pack,), answers=(answer,))
    )
    assert isinstance(result, CompletionReady)


def test_missing_information_is_stable_and_conditional() -> None:
    intake = _intake()
    trigger = _question("synthetic.trigger", requiredness=Requiredness.OPTIONAL, order=0)
    conditional_rule = RuleDefinition(
        "synthetic.triggered", RuleOperator.EXISTS, ("question:synthetic.trigger",)
    )
    conditional = _question(
        "synthetic.conditional",
        requiredness=Requiredness.CONDITIONAL,
        order=1,
        applicability=(conditional_rule.rule_id,),
    )
    pack = _pack("synthetic.core", (trigger, conditional), applicability_rules=(conditional_rule,))
    engine = AdaptiveIntakeEngine(PackRegistry((pack,)))

    assert isinstance(engine.evaluate(_input(intake, (pack,))), CompletionReady)
    answer = _answer(intake, trigger)
    first = engine.evaluate(_input(intake, (pack,), answers=(answer,)))
    second = engine.evaluate(_input(intake, (pack,), answers=(answer,)))
    assert first == second
    assert isinstance(first, NextQuestion)
    incomplete = engine.missing_information(_input(intake, (pack,), answers=(answer,)))
    assert len(incomplete) == 1
    assert incomplete[0].reason_code is MissingReason.CONDITIONAL_UNANSWERED


def test_required_missing_information_is_stable_and_input_is_not_mutated() -> None:
    intake = _intake()
    question = _question("synthetic.required")
    pack = _pack("synthetic.core", (question,))
    engine_input = _input(intake, (pack,))
    original = engine_input

    first = AdaptiveIntakeEngine(PackRegistry((pack,))).missing_information(engine_input)
    second = AdaptiveIntakeEngine(PackRegistry((pack,))).missing_information(engine_input)

    assert first == second
    assert first[0].reason_code is MissingReason.REQUIRED_UNANSWERED
    assert engine_input == original


def test_terminal_intake_is_rejected_before_evaluation() -> None:
    abandoned = _intake().transition_to(ClinicalIntakeStatus.ABANDONED)
    with pytest.raises(ValueError) as raised:
        EngineInput(
            intake=abandoned,
            selected_pack_identities=(),
        )
    assert raised.type.__name__ == "InvalidEngineInputError"


def test_configured_contradiction_has_stable_clarification_priority() -> None:
    intake = _intake()
    rule = RuleDefinition(
        "synthetic.conflict",
        RuleOperator.CONTRADICTION_STATE,
        ("contradiction:synthetic.field", "state:OPEN"),
    )
    clarification = _question("synthetic.clarify", clarification_rule_ids=(rule.rule_id,), order=10)
    ordinary = _question("synthetic.field", order=0)
    pack = _pack(
        "synthetic.core",
        (ordinary, clarification),
        contradiction_rules=(rule,),
    )
    contradiction = Contradiction(
        contradiction_id=OpaqueId.parse("00000000-0000-4000-8000-000000000020"),
        field_key="synthetic.field",
        left_ref=SourceReference(answer_id=OpaqueId.new()),
        right_ref=SourceReference(
            fact_id=OpaqueId.new(), verification_state=VerificationState.PATIENT_CONFIRMED.value
        ),
        source_pack_id=pack.pack_id,
        source_rule_id=rule.rule_id,
        status=ContradictionStatus.OPEN,
        created_at=NOW,
    )
    result = AdaptiveIntakeEngine(PackRegistry((pack,))).evaluate(
        _input(intake, (pack,), contradictions=(contradiction,))
    )
    assert isinstance(result, ClarificationRequired)
    assert result.contradiction_id == contradiction.contradiction_id
    assert result.question == clarification
    missing = AdaptiveIntakeEngine(PackRegistry((pack,))).missing_information(
        _input(intake, (pack,), contradictions=(contradiction,))
    )
    assert missing[0].reason_code is MissingReason.CLARIFICATION_REQUIRED


def test_resolved_and_unrelated_contradictions_do_not_block() -> None:
    intake = _intake()
    rule = RuleDefinition(
        "synthetic.conflict",
        RuleOperator.CONTRADICTION_STATE,
        ("contradiction:synthetic.field", "state:OPEN"),
    )
    field = _question("synthetic.field", requiredness=Requiredness.OPTIONAL)
    clarification = _question(
        "synthetic.clarify",
        requiredness=Requiredness.OPTIONAL,
        clarification_rule_ids=(rule.rule_id,),
    )
    pack = _pack("synthetic.core", (field, clarification), contradiction_rules=(rule,))
    resolved = Contradiction(
        contradiction_id=OpaqueId.new(),
        field_key="synthetic.field",
        left_ref=SourceReference(answer_id=OpaqueId.new()),
        right_ref=SourceReference(
            fact_id=OpaqueId.new(), verification_state=VerificationState.PATIENT_CONFIRMED.value
        ),
        source_pack_id=pack.pack_id,
        source_rule_id=rule.rule_id,
        status=ContradictionStatus.RESOLVED,
        created_at=NOW,
        resolution_ref=OpaqueId.new(),
        resolved_at=NOW,
    )
    unrelated = replace(
        resolved,
        contradiction_id=OpaqueId.new(),
        field_key="synthetic.other",
        status=ContradictionStatus.OPEN,
        resolution_ref=None,
        resolved_at=None,
    )
    engine = AdaptiveIntakeEngine(PackRegistry((pack,)))
    assert isinstance(
        engine.evaluate(_input(intake, (pack,), contradictions=(resolved, unrelated))),
        CompletionReady,
    )


def test_two_configured_contradictions_use_stable_question_order() -> None:
    intake = _intake()
    rules = (
        RuleDefinition(
            "synthetic.conflict.a",
            RuleOperator.CONTRADICTION_STATE,
            ("contradiction:synthetic.field.a", "state:OPEN"),
        ),
        RuleDefinition(
            "synthetic.conflict.b",
            RuleOperator.CONTRADICTION_STATE,
            ("contradiction:synthetic.field.b", "state:OPEN"),
        ),
    )
    fields = (
        _question("synthetic.field.a", requiredness=Requiredness.OPTIONAL),
        _question("synthetic.field.b", requiredness=Requiredness.OPTIONAL),
    )
    clarifications = (
        _question(
            "synthetic.clarify.b",
            requiredness=Requiredness.OPTIONAL,
            order=2,
            clarification_rule_ids=(rules[1].rule_id,),
        ),
        _question(
            "synthetic.clarify.a",
            requiredness=Requiredness.OPTIONAL,
            order=1,
            clarification_rule_ids=(rules[0].rule_id,),
        ),
    )
    pack = _pack("synthetic.core", fields + clarifications, contradiction_rules=rules)

    def contradiction(index: int) -> Contradiction:
        return Contradiction(
            contradiction_id=OpaqueId.parse(f"00000000-0000-4000-8000-00000000003{index}"),
            field_key=f"synthetic.field.{chr(ord('a') + index)}",
            left_ref=SourceReference(answer_id=OpaqueId.new()),
            right_ref=SourceReference(
                fact_id=OpaqueId.new(),
                verification_state=VerificationState.PATIENT_CONFIRMED.value,
            ),
            source_pack_id=pack.pack_id,
            source_rule_id=rules[index].rule_id,
            status=ContradictionStatus.OPEN,
            created_at=NOW,
        )

    values = (contradiction(1), contradiction(0))
    engine = AdaptiveIntakeEngine(PackRegistry((pack,)))
    result = engine.evaluate(_input(intake, (pack,), contradictions=values))
    reversed_result = engine.evaluate(
        _input(intake, (pack,), contradictions=tuple(reversed(values)))
    )
    assert result == reversed_result
    assert isinstance(result, ClarificationRequired)
    assert result.question.question_id == "synthetic.clarify.a"


def test_history_suppression_requires_explicit_policy_and_eligible_state() -> None:
    intake = _intake()
    binding = HistoryBinding("PROBLEM", "past_medical")
    conservative = _question("synthetic.history", history_binding=binding)
    suppressing = replace(
        conservative,
        history_reuse_policy=HistoryReusePolicy(
            eligible_verification_states=(VerificationState.CLINICIAN_CONFIRMED,),
            suppress_question=True,
            confirmation_required=False,
        ),
    )
    eligible = HistoryContext(
        fact_id=OpaqueId.new(),
        fact_type="PROBLEM",
        section_key="past_medical",
        display_value="Synthetic history",
        verification_state=VerificationState.CLINICIAN_CONFIRMED,
    )
    rejected = replace(eligible, verification_state=VerificationState.REJECTED)

    conservative_pack = _pack("synthetic.conservative", (conservative,))
    conservative_result = AdaptiveIntakeEngine(PackRegistry((conservative_pack,))).evaluate(
        _input(intake, (conservative_pack,), history=(eligible,))
    )
    assert isinstance(conservative_result, NextQuestion)
    missing = AdaptiveIntakeEngine(PackRegistry((conservative_pack,))).missing_information(
        _input(intake, (conservative_pack,), history=(eligible,))
    )
    assert missing[0].reason_code is MissingReason.RECONFIRMATION_REQUIRED

    suppressing_pack = _pack("synthetic.suppressing", (suppressing,))
    engine = AdaptiveIntakeEngine(PackRegistry((suppressing_pack,)))
    assert isinstance(
        engine.evaluate(_input(intake, (suppressing_pack,), history=(eligible,))),
        CompletionReady,
    )
    assert isinstance(
        engine.evaluate(_input(intake, (suppressing_pack,), history=(rejected,))),
        NextQuestion,
    )


def test_history_order_unbound_type_and_confirmation_policy_are_conservative() -> None:
    intake = _intake()
    question = _question(
        "synthetic.history",
        history_binding=HistoryBinding("PROBLEM", "past_medical"),
        history_reuse_policy=HistoryReusePolicy(
            eligible_verification_states=(VerificationState.PATIENT_CONFIRMED,),
            suppress_question=False,
            confirmation_required=True,
        ),
    )
    pack = _pack("synthetic.core", (question,))
    eligible = HistoryContext(
        fact_id=OpaqueId.new(),
        fact_type="PROBLEM",
        section_key="past_medical",
        display_value="Synthetic eligible history",
        verification_state=VerificationState.PATIENT_CONFIRMED,
    )
    unrelated = replace(eligible, fact_id=OpaqueId.new(), fact_type="ALLERGY")
    superseded = replace(
        eligible,
        fact_id=OpaqueId.new(),
        verification_state=VerificationState.SUPERSEDED,
    )
    engine = AdaptiveIntakeEngine(PackRegistry((pack,)))
    first = engine.evaluate(_input(intake, (pack,), history=(unrelated, eligible, superseded)))
    reordered = engine.evaluate(_input(intake, (pack,), history=(superseded, eligible, unrelated)))
    assert first == reordered
    assert isinstance(first, NextQuestion)
    assert (
        engine.missing_information(_input(intake, (pack,), history=(eligible,)))[0].reason_code
        is MissingReason.RECONFIRMATION_REQUIRED
    )

    reused = _answer(
        intake,
        question,
        source_type=IntakeAnswerSourceType.REUSED_HISTORY,
    )
    assert isinstance(
        engine.evaluate(_input(intake, (pack,), answers=(reused,), history=(eligible,))),
        NextQuestion,
    )


@pytest.mark.parametrize(
    "kind",
    [
        QuestionPackKind.COMPLAINT,
        QuestionPackKind.SPECIALTY,
        QuestionPackKind.AYUSH_EXTENSION,
    ],
)
def test_extension_pack_kinds_use_the_same_engine(kind: QuestionPackKind) -> None:
    intake = _intake()
    pack = _pack(
        f"synthetic.{kind.value.lower()}",
        (_question(f"synthetic.{kind.value.lower()}.question"),),
        kind=kind,
        approval=ApprovalState.ENGINEERING_APPROVED
        if kind is QuestionPackKind.AYUSH_EXTENSION
        else ApprovalState.APPROVED,
    )
    result = AdaptiveIntakeEngine(PackRegistry((pack,))).evaluate(_input(intake, (pack,)))
    assert isinstance(result, NextQuestion)
    assert result.pack_id == pack.pack_id


def test_ayush_pack_registers_but_does_not_activate_without_approval() -> None:
    pack = _pack(
        "synthetic.ayush",
        (_question("synthetic.ayush.question"),),
        kind=QuestionPackKind.AYUSH_EXTENSION,
        approval=ApprovalState.CLINICAL_APPROVAL_REQUIRED,
    )
    registry = PackRegistry((pack,))
    assert registry.get(pack.pack_id, pack.version) == pack
    with pytest.raises(ValueError):
        AdaptiveIntakeEngine(registry).evaluate(_input(_intake(), (pack,)))


def test_unresolvable_required_dependency_returns_incomplete() -> None:
    intake = _intake()
    optional = _question("synthetic.optional", requiredness=Requiredness.OPTIONAL)
    required = _question("synthetic.required", dependencies=(optional.question_id,), order=1)
    pack = _pack("synthetic.core", (optional, required))
    result = AdaptiveIntakeEngine(PackRegistry((pack,))).evaluate(_input(intake, (pack,)))
    assert isinstance(result, Incomplete)
    assert result.missing_information[0].field_or_question_key == required.question_id
