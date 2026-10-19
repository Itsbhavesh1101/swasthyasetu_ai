"""Closed engineering-only contracts for deterministic safety mechanics tests."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Final

from app.modules.safety.domain import SafetyRoute
from app.modules.safety.policies import PolicyApprovalState, SafetyPolicyType

MAX_SYNTHETIC_SIGNALS: Final = 16
MAX_SYNTHETIC_RULES: Final = 16

_MACHINE_ID = re.compile(r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$")
_MACHINE_VERSION = re.compile(r"^[A-Za-z0-9]+(?:[._-][A-Za-z0-9]+)*$")
_RULE_ID = re.compile(r"^synthetic-rule-[a-z0-9-]{1,48}$")
_REASON_CODE = re.compile(r"^SYNTHETIC_[A-Z0-9]+(?:_[A-Z0-9]+)*$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


class SafetyEngineError(ValueError):
    """Base class for content-free synthetic safety engine failures."""


class InvalidSyntheticSafetyInputError(SafetyEngineError):
    """Raised when the closed artificial input contract is malformed."""


class InvalidSyntheticRuleSetError(SafetyEngineError):
    """Raised when the engineering-only rule fixture is malformed or unsupported."""


class ConflictingSyntheticOutcomeError(SafetyEngineError):
    """Raised when equal mechanical precedence produces contradictory routes."""


class InvalidSafetyClockError(SafetyEngineError):
    """Raised when a controlled evaluation clock is invalid or unavailable."""


class SafetyEvaluationUnavailableError(SafetyEngineError):
    """Raised when no authorized synthetic outcome can be computed."""


class SyntheticSignal(StrEnum):
    """Artificial tokens with no symptom, diagnosis, or medical semantics."""

    SYNTHETIC_COMPLETE_A = "SYNTHETIC_COMPLETE_A"
    SYNTHETIC_OVERRIDE_A = "SYNTHETIC_OVERRIDE_A"
    SYNTHETIC_OVERRIDE_B = "SYNTHETIC_OVERRIDE_B"
    SYNTHETIC_MISSING_A = "SYNTHETIC_MISSING_A"
    SYNTHETIC_AMBIGUOUS_A = "SYNTHETIC_AMBIGUOUS_A"
    SYNTHETIC_EXCLUDE_A = "SYNTHETIC_EXCLUDE_A"
    SYNTHETIC_PRIORITY_A = "SYNTHETIC_PRIORITY_A"
    SYNTHETIC_ROUTINE_A = "SYNTHETIC_ROUTINE_A"
    SYNTHETIC_SELF_CARE_A = "SYNTHETIC_SELF_CARE_A"


class SyntheticAdvisory(StrEnum):
    """Non-authoritative toy model hint, deliberately excluded from rule matching."""

    LOW_RISK = "LOW_RISK"


class SyntheticRuleKind(StrEnum):
    HARD_OVERRIDE = "HARD_OVERRIDE"
    CLARIFICATION = "CLARIFICATION"
    SELF_CARE_EXCLUSION = "SELF_CARE_EXCLUSION"
    PRIORITY_ROUTE = "PRIORITY_ROUTE"
    ROUTINE_ROUTE = "ROUTINE_ROUTE"
    SELF_CARE_ROUTE = "SELF_CARE_ROUTE"


_KIND_CONTRACT: Final[Mapping[SyntheticRuleKind, tuple[int, SafetyRoute, bool, bool]]] = (
    MappingProxyType(
        {
            SyntheticRuleKind.HARD_OVERRIDE: (600, SafetyRoute.EMERGENCY, False, True),
            SyntheticRuleKind.CLARIFICATION: (
                500,
                SafetyRoute.CLARIFICATION_REQUIRED,
                True,
                True,
            ),
            SyntheticRuleKind.SELF_CARE_EXCLUSION: (400, SafetyRoute.ROUTINE_CARE, False, True),
            SyntheticRuleKind.PRIORITY_ROUTE: (300, SafetyRoute.PRIORITY_REVIEW, False, True),
            SyntheticRuleKind.ROUTINE_ROUTE: (200, SafetyRoute.ROUTINE_CARE, False, True),
            SyntheticRuleKind.SELF_CARE_ROUTE: (100, SafetyRoute.SUPPORTED_SELF_CARE, False, False),
        }
    )
)


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticSafetyInput:
    """Bounded symbolic input; it cannot represent a patient or clinical observation."""

    signals: tuple[SyntheticSignal, ...]
    advisory: SyntheticAdvisory | None = None

    def __post_init__(self) -> None:
        if (
            not isinstance(self.signals, tuple)
            or not self.signals
            or len(self.signals) > MAX_SYNTHETIC_SIGNALS
            or any(not isinstance(signal, SyntheticSignal) for signal in self.signals)
        ):
            raise InvalidSyntheticSafetyInputError("invalid synthetic signals")
        if len(set(self.signals)) != len(self.signals):
            raise InvalidSyntheticSafetyInputError("duplicate synthetic signals")
        if self.advisory is not None and not isinstance(self.advisory, SyntheticAdvisory):
            raise InvalidSyntheticSafetyInputError("invalid synthetic advisory")
        object.__setattr__(
            self, "signals", tuple(sorted(self.signals, key=lambda item: item.value))
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticRule:
    """One fixed symbolic mapping in the engineering fixture grammar."""

    rule_id: str
    signal: SyntheticSignal
    kind: SyntheticRuleKind
    route: SafetyRoute
    reason_code: str
    requires_clarification: bool
    blocks_self_care: bool

    def __post_init__(self) -> None:
        if (
            not isinstance(self.rule_id, str)
            or len(self.rule_id) > 64
            or _RULE_ID.fullmatch(self.rule_id) is None
        ):
            raise InvalidSyntheticRuleSetError("invalid synthetic rule ID")
        if not isinstance(self.signal, SyntheticSignal):
            raise InvalidSyntheticRuleSetError("invalid synthetic rule signal")
        if not isinstance(self.kind, SyntheticRuleKind):
            raise InvalidSyntheticRuleSetError("invalid synthetic rule kind")
        if not isinstance(self.route, SafetyRoute):
            raise InvalidSyntheticRuleSetError("invalid synthetic rule route")
        if (
            not isinstance(self.reason_code, str)
            or len(self.reason_code) > 64
            or _REASON_CODE.fullmatch(self.reason_code) is None
        ):
            raise InvalidSyntheticRuleSetError("invalid synthetic reason code")
        if type(self.requires_clarification) is not bool or type(self.blocks_self_care) is not bool:
            raise InvalidSyntheticRuleSetError("invalid synthetic rule flags")
        _, route, clarification, blocked = _KIND_CONTRACT[self.kind]
        if (
            self.route is not route
            or self.requires_clarification is not clarification
            or self.blocks_self_care is not blocked
        ):
            raise InvalidSyntheticRuleSetError("inconsistent synthetic rule outcome")

    @property
    def precedence(self) -> int:
        return _KIND_CONTRACT[self.kind][0]


def _canonical_rule_set_bytes(
    *,
    fixture_id: str,
    policy_type: SafetyPolicyType,
    policy_id: str,
    policy_version: str,
    approval_state: PolicyApprovalState,
    reason_code_namespace: str,
    rules: tuple[SyntheticRule, ...],
) -> bytes:
    if (
        not isinstance(fixture_id, str)
        or not isinstance(policy_type, SafetyPolicyType)
        or not isinstance(policy_id, str)
        or not isinstance(policy_version, str)
        or not isinstance(approval_state, PolicyApprovalState)
        or not isinstance(reason_code_namespace, str)
        or not isinstance(rules, tuple)
        or any(not isinstance(rule, SyntheticRule) for rule in rules)
    ):
        raise InvalidSyntheticRuleSetError("invalid canonical synthetic rule metadata")
    payload = {
        "approval_state": approval_state.value,
        "fixture_id": fixture_id,
        "policy_id": policy_id,
        "policy_type": policy_type.value,
        "policy_version": policy_version,
        "reason_code_namespace": reason_code_namespace,
        "rules": [
            {
                "blocks_self_care": rule.blocks_self_care,
                "kind": rule.kind.value,
                "reason_code": rule.reason_code,
                "requires_clarification": rule.requires_clarification,
                "route": rule.route.value,
                "rule_id": rule.rule_id,
                "signal": rule.signal.value,
            }
            for rule in rules
        ],
    }
    return json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticRuleSet:
    """Versioned toy rules whose checksum covers rule bytes, not clinical approval."""

    fixture_id: str
    policy_type: SafetyPolicyType
    policy_id: str
    policy_version: str
    approval_state: PolicyApprovalState
    reason_code_namespace: str
    rules: tuple[SyntheticRule, ...]
    rules_checksum: str

    def __post_init__(self) -> None:
        if (
            not isinstance(self.fixture_id, str)
            or not self.fixture_id.startswith("synthetic-")
            or len(self.fixture_id) > 128
            or _MACHINE_ID.fullmatch(self.fixture_id) is None
        ):
            raise InvalidSyntheticRuleSetError("invalid synthetic fixture ID")
        if self.policy_type is not SafetyPolicyType.PHYSICAL_SAFETY:
            raise InvalidSyntheticRuleSetError("invalid synthetic policy type")
        if (
            not isinstance(self.policy_id, str)
            or len(self.policy_id) > 128
            or _MACHINE_ID.fullmatch(self.policy_id) is None
        ):
            raise InvalidSyntheticRuleSetError("invalid synthetic policy ID")
        if (
            not isinstance(self.policy_version, str)
            or len(self.policy_version) > 64
            or _MACHINE_VERSION.fullmatch(self.policy_version) is None
        ):
            raise InvalidSyntheticRuleSetError("invalid synthetic policy version")
        if self.approval_state is not PolicyApprovalState.ENGINEERING_ONLY:
            raise InvalidSyntheticRuleSetError("invalid synthetic approval state")
        if self.reason_code_namespace != "SYNTHETIC_":
            raise InvalidSyntheticRuleSetError("invalid synthetic reason namespace")
        if (
            not isinstance(self.rules, tuple)
            or not self.rules
            or len(self.rules) > MAX_SYNTHETIC_RULES
            or any(not isinstance(rule, SyntheticRule) for rule in self.rules)
        ):
            raise InvalidSyntheticRuleSetError("invalid synthetic rules")
        canonical_rules = tuple(sorted(self.rules, key=lambda rule: rule.rule_id))
        rule_ids = tuple(rule.rule_id for rule in canonical_rules)
        signals = tuple(rule.signal for rule in canonical_rules)
        if len(set(rule_ids)) != len(rule_ids):
            raise InvalidSyntheticRuleSetError("duplicate synthetic rule IDs")
        if len(set(signals)) != len(signals):
            raise InvalidSyntheticRuleSetError("contradictory synthetic signal rules")
        object.__setattr__(self, "rules", canonical_rules)
        if (
            not isinstance(self.rules_checksum, str)
            or _SHA256.fullmatch(self.rules_checksum) is None
            or self.rules_checksum
            != self.compute_checksum(
                fixture_id=self.fixture_id,
                policy_type=self.policy_type,
                policy_id=self.policy_id,
                policy_version=self.policy_version,
                approval_state=self.approval_state,
                reason_code_namespace=self.reason_code_namespace,
                rules=canonical_rules,
            )
        ):
            raise InvalidSyntheticRuleSetError("synthetic rule checksum mismatch")

    @staticmethod
    def compute_checksum(
        *,
        fixture_id: str,
        policy_type: SafetyPolicyType,
        policy_id: str,
        policy_version: str,
        approval_state: PolicyApprovalState,
        reason_code_namespace: str,
        rules: tuple[SyntheticRule, ...],
    ) -> str:
        if not isinstance(rules, tuple) or any(
            not isinstance(rule, SyntheticRule) for rule in rules
        ):
            raise InvalidSyntheticRuleSetError("invalid synthetic rules")
        canonical_rules = tuple(sorted(rules, key=lambda rule: rule.rule_id))
        return hashlib.sha256(
            _canonical_rule_set_bytes(
                fixture_id=fixture_id,
                policy_type=policy_type,
                policy_id=policy_id,
                policy_version=policy_version,
                approval_state=approval_state,
                reason_code_namespace=reason_code_namespace,
                rules=canonical_rules,
            )
        ).hexdigest()

    @classmethod
    def create(
        cls,
        *,
        fixture_id: str,
        policy_type: SafetyPolicyType,
        policy_id: str,
        policy_version: str,
        approval_state: PolicyApprovalState,
        reason_code_namespace: str,
        rules: tuple[SyntheticRule, ...],
    ) -> SyntheticRuleSet:
        checksum = cls.compute_checksum(
            fixture_id=fixture_id,
            policy_type=policy_type,
            policy_id=policy_id,
            policy_version=policy_version,
            approval_state=approval_state,
            reason_code_namespace=reason_code_namespace,
            rules=rules,
        )
        return cls(
            fixture_id=fixture_id,
            policy_type=policy_type,
            policy_id=policy_id,
            policy_version=policy_version,
            approval_state=approval_state,
            reason_code_namespace=reason_code_namespace,
            rules=rules,
            rules_checksum=checksum,
        )
