"""Strict structural and activation validation for synthetic intake packs."""

from dataclasses import replace

import pytest

from app.modules.clinical_intake.contracts import (
    AnswerType,
    ApprovalState,
    InputMode,
    OptionValidation,
    PackRegistry,
    QuestionDefinition,
    QuestionPack,
    QuestionPackKind,
    QuestionSection,
    RuleDefinition,
    RuleOperator,
    TextValidation,
)
from app.modules.clinical_intake.domain import Requiredness


def _question(
    question_id: str = "synthetic.question",
    *,
    applicability_rule_ids: tuple[str, ...] = (),
    dependencies: tuple[str, ...] = (),
    input_modes: tuple[InputMode, ...] = (InputMode.TEXT,),
) -> QuestionDefinition:
    return QuestionDefinition(
        question_id=question_id,
        question_version="1.0.0",
        section=QuestionSection.EXTENSION,
        content_key=f"{question_id}.prompt",
        answer_type=AnswerType.TEXT,
        requiredness=Requiredness.REQUIRED,
        input_modes=input_modes,
        validation=TextValidation(1, 80),
        order=0,
        applicability_rule_ids=applicability_rule_ids,
        dependency_question_ids=dependencies,
    )


def _pack(
    *,
    pack_id: str = "synthetic.core",
    questions: tuple[QuestionDefinition, ...] | None = None,
    applicability_rules: tuple[RuleDefinition, ...] = (),
    contradiction_rules: tuple[RuleDefinition, ...] = (),
    languages: tuple[str, ...] = ("en",),
    approval_state: ApprovalState = ApprovalState.ENGINEERING_APPROVED,
) -> QuestionPack:
    return QuestionPack(
        pack_id=pack_id,
        version="1.0.0",
        kind=QuestionPackKind.CORE,
        approval_state=approval_state,
        content_version="1.0.0",
        supported_languages=languages,
        questions=questions or (_question(),),
        order=0,
        applicability_rules=applicability_rules,
        contradiction_rules=contradiction_rules,
    )


def test_registry_rejects_duplicate_question_identity_within_pack() -> None:
    with pytest.raises(ValueError) as raised:
        PackRegistry((_pack(questions=(_question(), _question())),))
    assert raised.type.__name__ == "InvalidQuestionPackError"


def test_activation_rejects_ambiguous_question_identity_across_selected_packs() -> None:
    first = _pack()
    second = replace(_pack(), pack_id="synthetic.other")
    registry = PackRegistry((first, second))
    with pytest.raises(ValueError) as raised:
        registry.activate(
            ((first.pack_id, first.version), (second.pack_id, second.version)),
            language="en",
        )
    assert raised.type.__name__ == "InvalidQuestionPackError"


@pytest.mark.parametrize(
    "pack",
    [
        _pack(
            applicability_rules=(
                RuleDefinition(
                    "synthetic.rule", RuleOperator.EXISTS, ("question:synthetic.question",)
                ),
                RuleDefinition(
                    "synthetic.rule", RuleOperator.EXISTS, ("question:synthetic.question",)
                ),
            )
        ),
        _pack(questions=(_question(applicability_rule_ids=("synthetic.missing",)),)),
        _pack(questions=(_question(dependencies=("synthetic.missing",)),)),
        _pack(questions=(_question(dependencies=("synthetic.question",)),)),
        _pack(questions=(_question(input_modes=(InputMode.VOICE,)),)),
        _pack(languages=("en", "en")),
    ],
)
def test_registry_rejects_invalid_pack_structure(pack: QuestionPack) -> None:
    with pytest.raises(ValueError) as raised:
        PackRegistry((pack,))
    assert raised.type.__name__ == "InvalidQuestionPackError"


def test_registry_rejects_dependency_and_rule_cycles() -> None:
    dependency_cycle = _pack(
        questions=(
            _question("synthetic.one", dependencies=("synthetic.two",)),
            _question("synthetic.two", dependencies=("synthetic.one",)),
        )
    )
    rule_cycle = _pack(
        applicability_rules=(
            RuleDefinition("synthetic.one", RuleOperator.NOT, ("rule:synthetic.two",)),
            RuleDefinition("synthetic.two", RuleOperator.NOT, ("rule:synthetic.one",)),
        )
    )
    multi_node_cycle = _pack(
        questions=(
            _question("synthetic.one", dependencies=("synthetic.two",)),
            _question("synthetic.two", dependencies=("synthetic.three",)),
            _question("synthetic.three", dependencies=("synthetic.one",)),
        )
    )
    for pack in (dependency_cycle, multi_node_cycle, rule_cycle):
        with pytest.raises(ValueError) as raised:
            PackRegistry((pack,))
        assert raised.type.__name__ == "InvalidQuestionPackError"


@pytest.mark.parametrize(
    "rule",
    [
        RuleDefinition("synthetic.bad", RuleOperator.EXISTS, ()),
        RuleDefinition("synthetic.bad", RuleOperator.NOT, ("question:synthetic.question",)),
        RuleDefinition("synthetic.bad", RuleOperator.AND, ("rule:synthetic.other",)),
        RuleDefinition("synthetic.bad", RuleOperator.EQUALS, ("question:synthetic.question",)),
        RuleDefinition("synthetic.bad", RuleOperator.IN, ("question:synthetic.question",)),
        RuleDefinition("synthetic.bad", RuleOperator.OR, ("rule:synthetic.other",)),
        RuleDefinition(
            "synthetic.bad", RuleOperator.HISTORY_AVAILABLE, ("history:synthetic.missing",)
        ),
        RuleDefinition(
            "synthetic.bad",
            RuleOperator.ANSWER_DISPOSITION,
            ("question:synthetic.question", "disposition:INVALID"),
        ),
        RuleDefinition(
            "synthetic.bad",
            RuleOperator.CONTRADICTION_STATE,
            ("contradiction:synthetic.missing", "state:INVALID"),
        ),
    ],
)
def test_registry_rejects_invalid_rule_arity_or_operand(rule: RuleDefinition) -> None:
    with pytest.raises(ValueError) as raised:
        PackRegistry((_pack(applicability_rules=(rule,)),))
    assert raised.type.__name__ in {"InvalidQuestionPackError", "InvalidRuleDefinitionError"}


def test_activation_is_explicit_language_checked_and_approval_gated() -> None:
    approved = _pack()
    pending = _pack(
        pack_id="synthetic.ayush",
        questions=(_question("synthetic.ayush.question"),),
        approval_state=ApprovalState.CLINICAL_APPROVAL_REQUIRED,
    )
    registry = PackRegistry((approved, pending))

    assert registry.activate(((approved.pack_id, approved.version),), language="en") == (approved,)
    with pytest.raises(ValueError) as missing:
        registry.activate((("synthetic.missing", "1.0.0"),), language="en")
    assert missing.type.__name__ == "PackNotActivationEligibleError"
    with pytest.raises(ValueError):
        registry.activate(((approved.pack_id, approved.version),), language="hi")
    with pytest.raises(ValueError):
        registry.activate(((pending.pack_id, pending.version),), language="en")


@pytest.mark.parametrize(
    "pack",
    [
        _pack(pack_id="Synthetic Invalid"),
        _pack(languages=("not a language",)),
        _pack(questions=(replace(_question(), question_id="Synthetic Invalid"),)),
        _pack(questions=(replace(_question(), clarification_rule_ids=("synthetic.missing",)),)),
        _pack(questions=(replace(_question(), input_modes=(InputMode.TEXT, InputMode.TEXT)),)),
    ],
)
def test_registry_rejects_non_machine_or_duplicate_metadata(pack: QuestionPack) -> None:
    with pytest.raises(ValueError) as raised:
        PackRegistry((pack,))
    assert raised.type.__name__ == "InvalidQuestionPackError"


def test_registry_contents_are_immutable_and_activation_order_is_canonical() -> None:
    later = replace(
        _pack(pack_id="synthetic.later", questions=(_question("synthetic.later"),)),
        order=2,
    )
    first = replace(
        _pack(pack_id="synthetic.first", questions=(_question("synthetic.first"),)),
        order=1,
    )
    registry = PackRegistry((later, first))
    assert registry.activate(
        ((later.pack_id, later.version), (first.pack_id, first.version)), language="en"
    ) == (first, later)
    snapshot = registry.all()
    assert isinstance(snapshot, tuple)
    assert registry.get(first.pack_id, first.version) == first


def test_history_suppression_requires_fully_approved_pack() -> None:
    from app.modules.clinical_intake.contracts import HistoryBinding, HistoryReusePolicy
    from app.modules.provenance.domain import VerificationState

    question = replace(
        _question(),
        history_binding=HistoryBinding("PROBLEM", "past_medical"),
        history_reuse_policy=HistoryReusePolicy(
            eligible_verification_states=(VerificationState.CLINICIAN_CONFIRMED,),
            suppress_question=True,
            confirmation_required=False,
        ),
    )
    pack = _pack(questions=(question,))
    registry = PackRegistry((pack,))
    with pytest.raises(ValueError) as raised:
        registry.activate(((pack.pack_id, pack.version),), language="en")
    assert raised.type.__name__ == "PackNotActivationEligibleError"


@pytest.mark.parametrize(
    "factory",
    [
        lambda: replace(_pack(), schema_version="question-pack.v2"),
        lambda: replace(_pack(), order=-1),
        lambda: replace(_question(), order=-1),
        lambda: OptionValidation(("duplicate", "duplicate")),
    ],
)
def test_contract_construction_rejects_invalid_pack_metadata(factory: object) -> None:
    with pytest.raises(ValueError):
        factory()  # type: ignore[operator]
