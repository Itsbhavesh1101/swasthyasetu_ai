"""Closed, deterministic rule evaluation without executable expressions."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from app.modules.clinical_intake.contracts import IntakeAnswer, RuleDefinition, RuleOperator
from app.modules.clinical_intake.domain import Contradiction
from app.modules.clinical_intake.history import HistoryContext, reusable_history


@dataclass(frozen=True, slots=True)
class RuleEvaluationContext:
    answers: Mapping[str, IntakeAnswer]
    history: tuple[HistoryContext, ...]
    contradictions: tuple[Contradiction, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "answers", MappingProxyType(dict(self.answers)))


def _suffix(operand: str) -> str:
    return operand.split(":", 1)[1]


def _answer_values(answer: IntakeAnswer) -> tuple[str, ...]:
    if answer.selected_option_ids is not None:
        return answer.selected_option_ids
    if answer.value is None:
        return ()
    if isinstance(answer.value, bool):
        return (str(answer.value).lower(),)
    return (str(answer.value),)


def evaluate_rule(
    rule: RuleDefinition,
    rules: Mapping[str, RuleDefinition],
    context: RuleEvaluationContext,
) -> bool:
    operator = rule.operator
    operands = rule.operands
    if operator is RuleOperator.EXISTS:
        return _suffix(operands[0]) in context.answers
    if operator is RuleOperator.EQUALS:
        answer = context.answers.get(_suffix(operands[0]))
        return answer is not None and _suffix(operands[1]) in _answer_values(answer)
    if operator is RuleOperator.IN:
        answer = context.answers.get(_suffix(operands[0]))
        choices = {_suffix(operand) for operand in operands[1:]}
        return answer is not None and bool(choices.intersection(_answer_values(answer)))
    if operator is RuleOperator.AND:
        return all(evaluate_rule(rules[_suffix(item)], rules, context) for item in operands)
    if operator is RuleOperator.OR:
        return any(evaluate_rule(rules[_suffix(item)], rules, context) for item in operands)
    if operator is RuleOperator.NOT:
        return not evaluate_rule(rules[_suffix(operands[0])], rules, context)
    if operator is RuleOperator.ANSWER_DISPOSITION:
        answer = context.answers.get(_suffix(operands[0]))
        return answer is not None and answer.response_disposition.value == _suffix(operands[1])
    if operator is RuleOperator.HISTORY_AVAILABLE:
        section_key = _suffix(operands[0])
        return any(item.section_key == section_key for item in reusable_history(context.history))
    if operator is RuleOperator.CONTRADICTION_STATE:
        field_key = _suffix(operands[0])
        state = _suffix(operands[1])
        return any(
            item.field_key == field_key and item.status.value == state
            for item in context.contradictions
        )
    return False
