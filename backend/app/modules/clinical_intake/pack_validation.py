"""Strict, non-executable validation for explicitly registered question packs."""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping

from app.modules.clinical_intake.contracts import (
    InputMode,
    InvalidQuestionPackError,
    InvalidRuleDefinitionError,
    OptionValidation,
    QuestionPack,
    ResponseDisposition,
    RuleDefinition,
    RuleOperator,
)

_MACHINE_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$", re.ASCII)
_LANGUAGE_CODE = re.compile(r"^[a-z]{2,3}(?:-[A-Za-z0-9]{2,8})*$", re.ASCII)


def _machine_id(value: str, *, name: str) -> None:
    if _MACHINE_ID.fullmatch(value) is None:
        raise InvalidQuestionPackError(f"{name} is not a valid machine identifier")


def _split(operand: str, prefix: str) -> str:
    marker = f"{prefix}:"
    if not operand.startswith(marker) or len(operand) == len(marker):
        raise InvalidRuleDefinitionError("rule operand grammar is invalid")
    return operand[len(marker) :]


def _machine_operand(operand: str, prefix: str) -> str:
    value = _split(operand, prefix)
    _machine_id(value, name=f"{prefix} operand")
    return value


def _assert_acyclic(graph: dict[str, tuple[str, ...]], *, kind: str) -> None:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in visiting:
            raise InvalidQuestionPackError(f"{kind} graph contains a cycle")
        if node in visited:
            return
        visiting.add(node)
        for dependency in graph[node]:
            visit(dependency)
        visiting.remove(node)
        visited.add(node)

    for node in sorted(graph):
        visit(node)


def _validate_rule(
    rule: RuleDefinition,
    *,
    rules: dict[str, RuleDefinition],
    questions: Mapping[str, object],
    history_keys: set[str],
) -> tuple[str, ...]:
    operands = rule.operands
    references: tuple[str, ...] = ()
    if rule.operator is RuleOperator.EXISTS:
        if len(operands) != 1:
            raise InvalidRuleDefinitionError("EXISTS rule arity is invalid")
        question_id = _machine_operand(operands[0], "question")
        if question_id not in questions:
            raise InvalidRuleDefinitionError("EXISTS references an unknown question")
    elif rule.operator in {RuleOperator.EQUALS, RuleOperator.IN}:
        minimum = 2
        if len(operands) < minimum or (rule.operator is RuleOperator.EQUALS and len(operands) != 2):
            raise InvalidRuleDefinitionError("comparison rule arity is invalid")
        question_id = _machine_operand(operands[0], "question")
        question = questions.get(question_id)
        if question is None:
            raise InvalidRuleDefinitionError("comparison references an unknown question")
        allowed = getattr(getattr(question, "validation", None), "allowed_option_ids", ())
        for operand in operands[1:]:
            if operand.startswith("option:"):
                option_id = _machine_operand(operand, "option")
                if not isinstance(getattr(question, "validation", None), OptionValidation):
                    raise InvalidRuleDefinitionError("option operand requires a choice question")
                if option_id not in allowed:
                    raise InvalidRuleDefinitionError("rule references an unknown option")
            elif operand.startswith("value:"):
                _machine_operand(operand, "value")
            else:
                raise InvalidRuleDefinitionError("comparison operand grammar is invalid")
    elif rule.operator in {RuleOperator.AND, RuleOperator.OR}:
        if len(operands) < 2:
            raise InvalidRuleDefinitionError("boolean rule arity is invalid")
        references = tuple(_machine_operand(operand, "rule") for operand in operands)
    elif rule.operator is RuleOperator.NOT:
        if len(operands) != 1:
            raise InvalidRuleDefinitionError("NOT rule arity is invalid")
        references = (_machine_operand(operands[0], "rule"),)
    elif rule.operator is RuleOperator.ANSWER_DISPOSITION:
        if len(operands) != 2:
            raise InvalidRuleDefinitionError("ANSWER_DISPOSITION rule arity is invalid")
        question_id = _machine_operand(operands[0], "question")
        if question_id not in questions:
            raise InvalidRuleDefinitionError("disposition references an unknown question")
        try:
            ResponseDisposition(_split(operands[1], "disposition"))
        except ValueError as error:
            raise InvalidRuleDefinitionError("disposition operand is invalid") from error
    elif rule.operator is RuleOperator.HISTORY_AVAILABLE:
        if len(operands) != 1 or _machine_operand(operands[0], "history") not in history_keys:
            raise InvalidRuleDefinitionError("history rule references an unknown binding")
    elif rule.operator is RuleOperator.CONTRADICTION_STATE:
        if len(operands) != 2:
            raise InvalidRuleDefinitionError("CONTRADICTION_STATE rule arity is invalid")
        field_key = _machine_operand(operands[0], "contradiction")
        if field_key not in questions and field_key not in history_keys:
            raise InvalidRuleDefinitionError("contradiction rule references an unknown field")
        state = _split(operands[1], "state")
        if state not in {"OPEN", "CLARIFICATION_REQUIRED", "RESOLVED"}:
            raise InvalidRuleDefinitionError("contradiction state operand is invalid")
    else:  # pragma: no cover - closed enum defensive branch
        raise InvalidRuleDefinitionError("rule operator is unsupported")
    for reference in references:
        if reference not in rules:
            raise InvalidRuleDefinitionError("boolean rule references an unknown rule")
    return references


def validate_pack(pack: QuestionPack) -> None:
    for name, value in (
        ("pack_id", pack.pack_id),
        ("version", pack.version),
        ("content_version", pack.content_version),
    ):
        _machine_id(value, name=name)
    if len(set(pack.supported_languages)) != len(pack.supported_languages):
        raise InvalidQuestionPackError("question pack languages must be unique")
    if any(_LANGUAGE_CODE.fullmatch(value) is None for value in pack.supported_languages):
        raise InvalidQuestionPackError("question pack language code is invalid")
    questions = {question.question_id: question for question in pack.questions}
    if len(questions) != len(pack.questions):
        raise InvalidQuestionPackError("question identity is duplicated within a pack")
    for question in pack.questions:
        _machine_id(question.question_id, name="question_id")
        _machine_id(question.question_version, name="question_version")
        _machine_id(question.content_key, name="content_key")
        if question.help_content_key is not None:
            _machine_id(question.help_content_key, name="help_content_key")
        if len(set(question.input_modes)) != len(question.input_modes):
            raise InvalidQuestionPackError("question input modes must be unique")
        if len(set(question.dependency_question_ids)) != len(question.dependency_question_ids):
            raise InvalidQuestionPackError("question dependencies must be unique")
        if len(set(question.applicability_rule_ids)) != len(question.applicability_rule_ids):
            raise InvalidQuestionPackError("question applicability rules must be unique")
        if len(set(question.clarification_rule_ids)) != len(question.clarification_rule_ids):
            raise InvalidQuestionPackError("question clarification rules must be unique")
        if not ({InputMode.TEXT, InputMode.TOUCH} & set(question.input_modes)):
            raise InvalidQuestionPackError("active question requires text or touch input")
        for dependency in question.dependency_question_ids:
            if dependency not in questions:
                raise InvalidQuestionPackError("question dependency is unknown")
            if dependency == question.question_id:
                raise InvalidQuestionPackError("question cannot depend on itself")
    _assert_acyclic(
        {question.question_id: question.dependency_question_ids for question in pack.questions},
        kind="question dependency",
    )

    definitions = pack.applicability_rules + pack.contradiction_rules
    rules = {rule.rule_id: rule for rule in definitions}
    if len(rules) != len(definitions):
        raise InvalidQuestionPackError("rule ID is duplicated within a pack")
    for question in pack.questions:
        for rule_id in question.applicability_rule_ids:
            if rule_id not in rules:
                raise InvalidQuestionPackError("question references an unknown applicability rule")
        for rule_id in question.clarification_rule_ids:
            if rule_id not in {rule.rule_id for rule in pack.contradiction_rules}:
                raise InvalidQuestionPackError("question references an unknown contradiction rule")
    history_keys = {
        question.history_binding.section_key
        for question in pack.questions
        if question.history_binding is not None
    }
    graph: dict[str, tuple[str, ...]] = {}
    for rule in definitions:
        _machine_id(rule.rule_id, name="rule_id")
        graph[rule.rule_id] = _validate_rule(
            rule,
            rules=rules,
            questions=questions,
            history_keys=history_keys,
        )
    _assert_acyclic(graph, kind="rule reference")


def validate_question_identities(packs: Iterable[QuestionPack]) -> None:
    identities: set[tuple[str, str]] = set()
    for pack in packs:
        for question in pack.questions:
            identity = (question.question_id, question.question_version)
            if identity in identities:
                raise InvalidQuestionPackError(
                    "question identity is ambiguous across registered packs"
                )
            identities.add(identity)
