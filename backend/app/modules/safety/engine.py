"""Pure deterministic evaluator for the exact P9-B synthetic fixture."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

from app.config.settings import Environment
from app.modules.safety.contracts import (
    MAX_SYNTHETIC_RULES,
    ConflictingSyntheticOutcomeError,
    InvalidSafetyClockError,
    InvalidSyntheticRuleSetError,
    SafetyEvaluationUnavailableError,
    SyntheticRule,
    SyntheticRuleKind,
    SyntheticRuleSet,
    SyntheticSafetyInput,
    SyntheticSignal,
)
from app.modules.safety.domain import SafetyDecision, SafetyRoute
from app.modules.safety.policies import (
    PolicyActivationState,
    PolicyApprovalState,
    SafetyPolicyRegistry,
    SafetyPolicyType,
)
from app.modules.safety.synthetic import SYNTHETIC_RULE_SET

Clock = Callable[[], datetime]
_INCOMPLETE_REASON = "SYNTHETIC_INPUT_INCOMPLETE"


def _validated_rule(rule: SyntheticRule) -> SyntheticRule:
    return SyntheticRule(
        rule_id=rule.rule_id,
        signal=rule.signal,
        kind=rule.kind,
        route=rule.route,
        reason_code=rule.reason_code,
        requires_clarification=rule.requires_clarification,
        blocks_self_care=rule.blocks_self_care,
    )


def _validated_rule_set(rule_set: SyntheticRuleSet) -> SyntheticRuleSet:
    if not isinstance(rule_set, SyntheticRuleSet):
        raise InvalidSyntheticRuleSetError("invalid synthetic rule set")
    rules = rule_set.rules
    if (
        not isinstance(rules, tuple)
        or not rules
        or len(rules) > MAX_SYNTHETIC_RULES
        or any(not isinstance(rule, SyntheticRule) for rule in rules)
    ):
        raise InvalidSyntheticRuleSetError("invalid synthetic rules")
    validated = SyntheticRuleSet(
        fixture_id=rule_set.fixture_id,
        policy_type=rule_set.policy_type,
        policy_id=rule_set.policy_id,
        policy_version=rule_set.policy_version,
        approval_state=rule_set.approval_state,
        reason_code_namespace=rule_set.reason_code_namespace,
        rules=tuple(_validated_rule(rule) for rule in rules),
        rules_checksum=rule_set.rules_checksum,
    )
    if validated != SYNTHETIC_RULE_SET:
        raise InvalidSyntheticRuleSetError("unsupported synthetic rule set")
    return validated


def _controlled_now(clock: Clock) -> datetime:
    try:
        value = clock()
    except Exception:
        raise InvalidSafetyClockError("safety clock unavailable") from None
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise InvalidSafetyClockError("safety clock must be timezone-aware")
    try:
        offset = value.utcoffset()
        normalized = value.astimezone(UTC)
    except Exception:
        raise InvalidSafetyClockError("invalid safety clock") from None
    if offset is None:
        raise InvalidSafetyClockError("safety clock must be timezone-aware")
    return normalized


class SyntheticSafetyEngine:
    """Evaluate only the compile-time artificial fixture through the real registry gate."""

    __slots__ = ("_clock", "_registry", "_rule_set")

    def __init__(
        self,
        *,
        registry: SafetyPolicyRegistry,
        rule_set: SyntheticRuleSet,
        clock: Clock,
    ) -> None:
        if not isinstance(registry, SafetyPolicyRegistry):
            raise TypeError("registry must be a SafetyPolicyRegistry")
        if not callable(clock):
            raise TypeError("clock must be callable")
        self._registry = registry
        self._rule_set = rule_set
        self._clock = clock

    def evaluate(
        self, *, synthetic_input: SyntheticSafetyInput, environment: Environment
    ) -> SafetyDecision:
        metadata = self._registry.get_active_policy(
            policy_type=SafetyPolicyType.PHYSICAL_SAFETY,
            environment=environment,
        )
        rule_set = _validated_rule_set(self._rule_set)
        if (
            metadata.policy_type is not rule_set.policy_type
            or metadata.policy_id != rule_set.policy_id
            or metadata.policy_version != rule_set.policy_version
            or metadata.approval_state is not PolicyApprovalState.ENGINEERING_ONLY
            or metadata.activation_state is not PolicyActivationState.ENGINEERING_TEST_ONLY
            or metadata.reason_code_namespace != rule_set.reason_code_namespace
        ):
            raise InvalidSyntheticRuleSetError("synthetic policy binding mismatch")
        if not isinstance(synthetic_input, SyntheticSafetyInput):
            raise SafetyEvaluationUnavailableError("synthetic input unavailable")
        validated_input = SyntheticSafetyInput(
            signals=synthetic_input.signals,
            advisory=synthetic_input.advisory,
        )
        created_at = _controlled_now(self._clock)
        return self._evaluate_validated(
            synthetic_input=validated_input,
            rule_set=rule_set,
            created_at=created_at,
        )

    @staticmethod
    def _evaluate_validated(
        *,
        synthetic_input: SyntheticSafetyInput,
        rule_set: SyntheticRuleSet,
        created_at: datetime,
    ) -> SafetyDecision:
        supplied = frozenset(synthetic_input.signals)
        matched = tuple(rule for rule in rule_set.rules if rule.signal in supplied)
        hard_overrides = tuple(
            rule for rule in matched if rule.kind is SyntheticRuleKind.HARD_OVERRIDE
        )
        if hard_overrides:
            return _decision(
                winning_rules=hard_overrides,
                matched_rules=matched,
                rule_set=rule_set,
                created_at=created_at,
            )

        clarification = tuple(
            rule for rule in matched if rule.kind is SyntheticRuleKind.CLARIFICATION
        )
        if clarification:
            return _decision(
                winning_rules=clarification,
                matched_rules=matched,
                rule_set=rule_set,
                created_at=created_at,
            )

        if SyntheticSignal.SYNTHETIC_COMPLETE_A not in supplied:
            reasons = tuple(sorted({_INCOMPLETE_REASON, *(rule.reason_code for rule in matched)}))
            return SafetyDecision(
                route=SafetyRoute.CLARIFICATION_REQUIRED,
                reason_codes=reasons,
                policy_id=rule_set.policy_id,
                policy_version=rule_set.policy_version,
                requires_clarification=True,
                blocks_self_care=True,
                created_at=created_at,
            )

        if not matched:
            raise SafetyEvaluationUnavailableError("synthetic outcome unavailable")
        highest_precedence = max(rule.precedence for rule in matched)
        winners = tuple(rule for rule in matched if rule.precedence == highest_precedence)
        return _decision(
            winning_rules=winners,
            matched_rules=matched,
            rule_set=rule_set,
            created_at=created_at,
        )


def _decision(
    *,
    winning_rules: tuple[SyntheticRule, ...],
    matched_rules: tuple[SyntheticRule, ...],
    rule_set: SyntheticRuleSet,
    created_at: datetime,
) -> SafetyDecision:
    routes = frozenset(rule.route for rule in winning_rules)
    if len(routes) != 1:
        raise ConflictingSyntheticOutcomeError("conflicting synthetic outcomes")
    winner = min(winning_rules, key=lambda rule: rule.rule_id)
    return SafetyDecision(
        route=winner.route,
        reason_codes=tuple(sorted({rule.reason_code for rule in matched_rules})),
        policy_id=rule_set.policy_id,
        policy_version=rule_set.policy_version,
        requires_clarification=winner.requires_clarification,
        blocks_self_care=winner.blocks_self_care,
        created_at=created_at,
    )
