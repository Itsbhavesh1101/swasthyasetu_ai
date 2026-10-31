"""Detached synthetic policy mechanics with no clinical route semantics."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256
from typing import Final

from app.config.settings import Environment
from app.modules.mental_health.contracts import (
    MentalHealthContractError,
    SyntheticAuthority,
    SyntheticClassification,
    SyntheticSignalCode,
    SyntheticSignalObservation,
    SyntheticSignalState,
    SyntheticVerification,
)

MAX_SYNTHETIC_POLICY_RULES: Final = 8
MAX_SYNTHETIC_POLICY_EVIDENCE: Final = 4

_FIXTURE_SUFFIX = r"(?:alpha|beta|gamma|delta)"
_POLICY_ID = re.compile(r"^syn_mh_policy_fixture$")
_POLICY_VERSION = re.compile(r"^engineering\.v[1-9][0-9]{0,5}$")
_RULE_ID = re.compile(rf"^syn_mh_policy_rule_{_FIXTURE_SUFFIX}$")
_EVALUATION_ID = re.compile(rf"^syn_mh_policy_evaluation_{_FIXTURE_SUFFIX}$")
_DECISION_ID = re.compile(rf"^syn_mh_policy_decision_{_FIXTURE_SUFFIX}$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")


class SyntheticPolicyCode(StrEnum):
    INVALID_TYPE = "INVALID_TYPE"
    INVALID_VALUE = "INVALID_VALUE"
    LIMIT_EXCEEDED = "LIMIT_EXCEEDED"
    DUPLICATE_RULE = "DUPLICATE_RULE"
    DUPLICATE_SIGNAL = "DUPLICATE_SIGNAL"
    POLICY_HASH_MISMATCH = "POLICY_HASH_MISMATCH"
    IDENTITY_MISMATCH = "IDENTITY_MISMATCH"
    PROTECTED_ENVIRONMENT = "PROTECTED_ENVIRONMENT"
    INCONSISTENT_DECISION = "INCONSISTENT_DECISION"


class SyntheticPolicyError(ValueError):
    """Stable content-free error for synthetic routing mechanics."""

    def __init__(self, code: SyntheticPolicyCode) -> None:
        self.code = code
        super().__init__(code.value)


def _error(code: SyntheticPolicyCode) -> SyntheticPolicyError:
    return SyntheticPolicyError(code)


class SyntheticRuleKind(StrEnum):
    STANDARD = "SYNTHETIC_STANDARD"
    CLARIFICATION = "SYNTHETIC_CLARIFICATION"
    OVERRIDE = "SYNTHETIC_OVERRIDE"


class SyntheticRouteState(StrEnum):
    ALPHA = "SYNTHETIC_ROUTE_ALPHA"
    BETA = "SYNTHETIC_ROUTE_BETA"
    GAMMA = "SYNTHETIC_ROUTE_GAMMA"
    CLARIFICATION_REQUIRED = "SYNTHETIC_CLARIFICATION_REQUIRED"
    DEGRADED_SAFE_FALLBACK = "SYNTHETIC_DEGRADED_SAFE_FALLBACK"


class SyntheticPolicyState(StrEnum):
    TEST_ONLY_ENABLED = "TEST_ONLY_ENABLED"
    TEST_ONLY_SUSPENDED = "TEST_ONLY_SUSPENDED"


class SyntheticPolicyReasonCode(StrEnum):
    ALPHA = "SYN_MH_POLICY_REASON_ALPHA"
    BETA = "SYN_MH_POLICY_REASON_BETA"
    GAMMA = "SYN_MH_POLICY_REASON_GAMMA"
    DELTA = "SYN_MH_POLICY_REASON_DELTA"
    POLICY_UNAVAILABLE = "SYN_MH_POLICY_UNAVAILABLE"
    POLICY_INVALID = "SYN_MH_POLICY_INVALID"
    POLICY_NOT_EFFECTIVE = "SYN_MH_POLICY_NOT_EFFECTIVE"
    POLICY_EXPIRED = "SYN_MH_POLICY_EXPIRED"
    POLICY_SUSPENDED = "SYN_MH_POLICY_SUSPENDED"
    EVIDENCE_CONFLICT = "SYN_MH_EVIDENCE_CONFLICT"
    NO_MATCH = "SYN_MH_POLICY_NO_MATCH"
    WINNER_CONFLICT = "SYN_MH_POLICY_WINNER_CONFLICT"


_DEGRADED_REASONS = frozenset(
    {
        SyntheticPolicyReasonCode.POLICY_UNAVAILABLE,
        SyntheticPolicyReasonCode.POLICY_INVALID,
        SyntheticPolicyReasonCode.POLICY_NOT_EFFECTIVE,
        SyntheticPolicyReasonCode.POLICY_EXPIRED,
        SyntheticPolicyReasonCode.POLICY_SUSPENDED,
        SyntheticPolicyReasonCode.EVIDENCE_CONFLICT,
        SyntheticPolicyReasonCode.NO_MATCH,
        SyntheticPolicyReasonCode.WINNER_CONFLICT,
    }
)


def _strict_enum(value: object, expected: type[StrEnum]) -> None:
    if type(value) is not expected:
        raise _error(SyntheticPolicyCode.INVALID_TYPE)


def _machine_string(value: object, pattern: re.Pattern[str]) -> str:
    if type(value) is not str:
        raise _error(SyntheticPolicyCode.INVALID_TYPE)
    if pattern.fullmatch(value) is None:
        raise _error(SyntheticPolicyCode.INVALID_VALUE)
    return value


def _utc(value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise _error(SyntheticPolicyCode.INVALID_TYPE)
    return value.astimezone(UTC)


def _authority(
    authority: object,
    classification: object,
    verification: object,
) -> None:
    _strict_enum(authority, SyntheticAuthority)
    _strict_enum(classification, SyntheticClassification)
    _strict_enum(verification, SyntheticVerification)


def _observation(value: object) -> SyntheticSignalObservation:
    if type(value) is not SyntheticSignalObservation:
        raise _error(SyntheticPolicyCode.INVALID_TYPE)
    try:
        return SyntheticSignalObservation(code=value.code, state=value.state)
    except MentalHealthContractError:
        raise _error(SyntheticPolicyCode.INVALID_VALUE) from None
    except (AttributeError, TypeError, ValueError):
        raise _error(SyntheticPolicyCode.INVALID_TYPE) from None


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticPolicyRule:
    rule_id: str
    signal_code: SyntheticSignalCode
    signal_state: SyntheticSignalState
    kind: SyntheticRuleKind
    route: SyntheticRouteState
    reason_code: SyntheticPolicyReasonCode

    def __post_init__(self) -> None:
        _machine_string(self.rule_id, _RULE_ID)
        _strict_enum(self.signal_code, SyntheticSignalCode)
        _strict_enum(self.signal_state, SyntheticSignalState)
        _strict_enum(self.kind, SyntheticRuleKind)
        _strict_enum(self.route, SyntheticRouteState)
        _strict_enum(self.reason_code, SyntheticPolicyReasonCode)
        if self.reason_code in _DEGRADED_REASONS:
            raise _error(SyntheticPolicyCode.INVALID_VALUE)
        if self.kind is SyntheticRuleKind.CLARIFICATION:
            if self.route is not SyntheticRouteState.CLARIFICATION_REQUIRED:
                raise _error(SyntheticPolicyCode.INVALID_VALUE)
        elif self.route in {
            SyntheticRouteState.CLARIFICATION_REQUIRED,
            SyntheticRouteState.DEGRADED_SAFE_FALLBACK,
        }:
            raise _error(SyntheticPolicyCode.INVALID_VALUE)


def _rule(value: object) -> SyntheticPolicyRule:
    if type(value) is not SyntheticPolicyRule:
        raise _error(SyntheticPolicyCode.INVALID_TYPE)
    try:
        return SyntheticPolicyRule(
            rule_id=value.rule_id,
            signal_code=value.signal_code,
            signal_state=value.signal_state,
            kind=value.kind,
            route=value.route,
            reason_code=value.reason_code,
        )
    except SyntheticPolicyError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(SyntheticPolicyCode.INVALID_TYPE) from None


def _policy_hash(
    *,
    policy_id: str,
    policy_version: str,
    effective_at: datetime,
    expires_at: datetime,
    state: SyntheticPolicyState,
    rules: tuple[SyntheticPolicyRule, ...],
) -> str:
    fields = [
        policy_id,
        policy_version,
        effective_at.isoformat(),
        expires_at.isoformat(),
        state.value,
    ]
    for rule in rules:
        fields.extend(
            (
                rule.rule_id,
                rule.signal_code.value,
                rule.signal_state.value,
                rule.kind.value,
                rule.route.value,
                rule.reason_code.value,
            )
        )
    return sha256("\x1f".join(fields).encode("ascii")).hexdigest()


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticPolicyArtifact:
    policy_id: str
    policy_version: str
    content_hash: str
    effective_at: datetime
    expires_at: datetime
    state: SyntheticPolicyState
    rules: tuple[SyntheticPolicyRule, ...]
    authority: SyntheticAuthority = SyntheticAuthority.ENGINEERING_ONLY
    classification: SyntheticClassification = SyntheticClassification.ENGINEERING_SYNTHETIC
    verification: SyntheticVerification = SyntheticVerification.UNVERIFIED

    def __post_init__(self) -> None:
        policy_id = _machine_string(self.policy_id, _POLICY_ID)
        policy_version = _machine_string(self.policy_version, _POLICY_VERSION)
        _machine_string(self.content_hash, _SHA256)
        effective_at = _utc(self.effective_at)
        expires_at = _utc(self.expires_at)
        if expires_at <= effective_at:
            raise _error(SyntheticPolicyCode.INVALID_VALUE)
        _strict_enum(self.state, SyntheticPolicyState)
        if type(self.rules) is not tuple or not self.rules:
            raise _error(SyntheticPolicyCode.INVALID_TYPE)
        if len(self.rules) > MAX_SYNTHETIC_POLICY_RULES:
            raise _error(SyntheticPolicyCode.LIMIT_EXCEEDED)
        rules = tuple(_rule(rule) for rule in self.rules)
        rule_ids = tuple(rule.rule_id for rule in rules)
        if len(set(rule_ids)) != len(rule_ids):
            raise _error(SyntheticPolicyCode.DUPLICATE_RULE)
        if rule_ids != tuple(sorted(rule_ids)):
            raise _error(SyntheticPolicyCode.INVALID_VALUE)
        matchers = tuple((rule.signal_code, rule.signal_state) for rule in rules)
        if len(set(matchers)) != len(matchers):
            raise _error(SyntheticPolicyCode.DUPLICATE_RULE)
        _authority(self.authority, self.classification, self.verification)
        expected_hash = _policy_hash(
            policy_id=policy_id,
            policy_version=policy_version,
            effective_at=effective_at,
            expires_at=expires_at,
            state=self.state,
            rules=rules,
        )
        if self.content_hash != expected_hash:
            raise _error(SyntheticPolicyCode.POLICY_HASH_MISMATCH)
        object.__setattr__(self, "effective_at", effective_at)
        object.__setattr__(self, "expires_at", expires_at)
        object.__setattr__(self, "rules", rules)

    @classmethod
    def create(
        cls,
        *,
        policy_id: str,
        policy_version: str,
        effective_at: datetime,
        expires_at: datetime,
        state: SyntheticPolicyState,
        rules: tuple[SyntheticPolicyRule, ...],
    ) -> SyntheticPolicyArtifact:
        _strict_enum(state, SyntheticPolicyState)
        if type(rules) is not tuple:
            raise _error(SyntheticPolicyCode.INVALID_TYPE)
        normalized_effective = _utc(effective_at)
        normalized_expiry = _utc(expires_at)
        validated_rules = tuple(_rule(rule) for rule in rules)
        return cls(
            policy_id=policy_id,
            policy_version=policy_version,
            content_hash=_policy_hash(
                policy_id=policy_id,
                policy_version=policy_version,
                effective_at=normalized_effective,
                expires_at=normalized_expiry,
                state=state,
                rules=validated_rules,
            ),
            effective_at=normalized_effective,
            expires_at=normalized_expiry,
            state=state,
            rules=validated_rules,
        )


def _policy(value: object) -> SyntheticPolicyArtifact:
    if type(value) is not SyntheticPolicyArtifact:
        raise _error(SyntheticPolicyCode.INVALID_TYPE)
    try:
        return SyntheticPolicyArtifact(
            policy_id=value.policy_id,
            policy_version=value.policy_version,
            content_hash=value.content_hash,
            effective_at=value.effective_at,
            expires_at=value.expires_at,
            state=value.state,
            rules=value.rules,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
        )
    except SyntheticPolicyError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(SyntheticPolicyCode.INVALID_TYPE) from None


def _evidence_tuple(value: object) -> tuple[SyntheticSignalObservation, ...]:
    if type(value) is not tuple:
        raise _error(SyntheticPolicyCode.INVALID_TYPE)
    if len(value) > MAX_SYNTHETIC_POLICY_EVIDENCE:
        raise _error(SyntheticPolicyCode.LIMIT_EXCEEDED)
    observations = tuple(_observation(item) for item in value)
    codes = tuple(item.code.value for item in observations)
    if len(set(codes)) != len(codes):
        raise _error(SyntheticPolicyCode.DUPLICATE_SIGNAL)
    if codes != tuple(sorted(codes)):
        raise _error(SyntheticPolicyCode.INVALID_VALUE)
    return observations


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticRouteEvaluation:
    evaluation_id: str
    extractor_signals: tuple[SyntheticSignalObservation, ...]
    backstop_signals: tuple[SyntheticSignalObservation, ...]
    evaluated_at: datetime
    authority: SyntheticAuthority = SyntheticAuthority.ENGINEERING_ONLY
    classification: SyntheticClassification = SyntheticClassification.ENGINEERING_SYNTHETIC
    verification: SyntheticVerification = SyntheticVerification.UNVERIFIED

    def __post_init__(self) -> None:
        _machine_string(self.evaluation_id, _EVALUATION_ID)
        extractor_signals = _evidence_tuple(self.extractor_signals)
        backstop_signals = _evidence_tuple(self.backstop_signals)
        _authority(self.authority, self.classification, self.verification)
        object.__setattr__(self, "extractor_signals", extractor_signals)
        object.__setattr__(self, "backstop_signals", backstop_signals)
        object.__setattr__(self, "evaluated_at", _utc(self.evaluated_at))


def _evaluation(value: object) -> SyntheticRouteEvaluation:
    if type(value) is not SyntheticRouteEvaluation:
        raise _error(SyntheticPolicyCode.INVALID_TYPE)
    try:
        return SyntheticRouteEvaluation(
            evaluation_id=value.evaluation_id,
            extractor_signals=value.extractor_signals,
            backstop_signals=value.backstop_signals,
            evaluated_at=value.evaluated_at,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
        )
    except SyntheticPolicyError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(SyntheticPolicyCode.INVALID_TYPE) from None


def synthetic_route_evaluation_fingerprint(evaluation: SyntheticRouteEvaluation) -> str:
    snapshot = _evaluation(evaluation)
    fields = [snapshot.evaluation_id, snapshot.evaluated_at.isoformat()]
    for source, observations in (
        ("extractor", snapshot.extractor_signals),
        ("backstop", snapshot.backstop_signals),
    ):
        fields.append(source)
        for observation in observations:
            fields.extend((observation.code.value, observation.state.value))
    fields.extend(
        (
            snapshot.authority.value,
            snapshot.classification.value,
            snapshot.verification.value,
        )
    )
    return sha256("\x1f".join(fields).encode("ascii")).hexdigest()


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticPolicyReference:
    policy_id: str
    policy_version: str
    content_hash: str

    def __post_init__(self) -> None:
        _machine_string(self.policy_id, _POLICY_ID)
        _machine_string(self.policy_version, _POLICY_VERSION)
        _machine_string(self.content_hash, _SHA256)


def _policy_reference(value: object) -> SyntheticPolicyReference:
    if type(value) is not SyntheticPolicyReference:
        raise _error(SyntheticPolicyCode.INVALID_TYPE)
    try:
        return SyntheticPolicyReference(
            policy_id=value.policy_id,
            policy_version=value.policy_version,
            content_hash=value.content_hash,
        )
    except SyntheticPolicyError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(SyntheticPolicyCode.INVALID_TYPE) from None


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticRouteDecision:
    decision_id: str
    evaluation_id: str
    evaluation_fingerprint: str
    route: SyntheticRouteState
    reason_codes: tuple[SyntheticPolicyReasonCode, ...]
    policy_reference: SyntheticPolicyReference | None
    decided_at: datetime
    authority: SyntheticAuthority = SyntheticAuthority.ENGINEERING_ONLY
    classification: SyntheticClassification = SyntheticClassification.ENGINEERING_SYNTHETIC
    verification: SyntheticVerification = SyntheticVerification.UNVERIFIED

    def __post_init__(self) -> None:
        _machine_string(self.decision_id, _DECISION_ID)
        _machine_string(self.evaluation_id, _EVALUATION_ID)
        _machine_string(self.evaluation_fingerprint, _SHA256)
        _strict_enum(self.route, SyntheticRouteState)
        if type(self.reason_codes) is not tuple or not self.reason_codes:
            raise _error(SyntheticPolicyCode.INVALID_TYPE)
        reasons = tuple(self.reason_codes)
        for reason in reasons:
            _strict_enum(reason, SyntheticPolicyReasonCode)
        values = tuple(reason.value for reason in reasons)
        if len(set(values)) != len(values) or values != tuple(sorted(values)):
            raise _error(SyntheticPolicyCode.INVALID_VALUE)
        reference = (
            None if self.policy_reference is None else _policy_reference(self.policy_reference)
        )
        degraded = self.route is SyntheticRouteState.DEGRADED_SAFE_FALLBACK
        if degraded and (len(reasons) != 1 or reasons[0] not in _DEGRADED_REASONS):
            raise _error(SyntheticPolicyCode.INCONSISTENT_DECISION)
        if not degraded and any(reason in _DEGRADED_REASONS for reason in reasons):
            raise _error(SyntheticPolicyCode.INCONSISTENT_DECISION)
        if reference is None and reasons not in {
            (SyntheticPolicyReasonCode.POLICY_INVALID,),
            (SyntheticPolicyReasonCode.POLICY_UNAVAILABLE,),
        }:
            raise _error(SyntheticPolicyCode.INCONSISTENT_DECISION)
        if not degraded and reference is None:
            raise _error(SyntheticPolicyCode.INCONSISTENT_DECISION)
        _authority(self.authority, self.classification, self.verification)
        object.__setattr__(self, "reason_codes", reasons)
        object.__setattr__(self, "policy_reference", reference)
        object.__setattr__(self, "decided_at", _utc(self.decided_at))


def _decision(value: object) -> SyntheticRouteDecision:
    if type(value) is not SyntheticRouteDecision:
        raise _error(SyntheticPolicyCode.INVALID_TYPE)
    try:
        return SyntheticRouteDecision(
            decision_id=value.decision_id,
            evaluation_id=value.evaluation_id,
            evaluation_fingerprint=value.evaluation_fingerprint,
            route=value.route,
            reason_codes=value.reason_codes,
            policy_reference=value.policy_reference,
            decided_at=value.decided_at,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
        )
    except SyntheticPolicyError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(SyntheticPolicyCode.INVALID_TYPE) from None


def validate_synthetic_route_decision(
    evaluation: SyntheticRouteEvaluation,
    decision: SyntheticRouteDecision,
    policy: SyntheticPolicyArtifact | None,
) -> SyntheticRouteDecision:
    evaluation_snapshot = _evaluation(evaluation)
    decision_snapshot = _decision(decision)
    suffix = evaluation_snapshot.evaluation_id.removeprefix("syn_mh_policy_evaluation_")
    expected_decision_id = f"syn_mh_policy_decision_{suffix}"
    if (
        decision_snapshot.decision_id != expected_decision_id
        or decision_snapshot.evaluation_id != evaluation_snapshot.evaluation_id
        or decision_snapshot.evaluation_fingerprint
        != synthetic_route_evaluation_fingerprint(evaluation_snapshot)
        or decision_snapshot.decided_at != evaluation_snapshot.evaluated_at
    ):
        raise _error(SyntheticPolicyCode.IDENTITY_MISMATCH)
    if policy is None:
        if decision_snapshot.policy_reference is not None:
            raise _error(SyntheticPolicyCode.IDENTITY_MISMATCH)
    else:
        policy_snapshot = _policy(policy)
        expected_reference = SyntheticPolicyReference(
            policy_id=policy_snapshot.policy_id,
            policy_version=policy_snapshot.policy_version,
            content_hash=policy_snapshot.content_hash,
        )
        if decision_snapshot.policy_reference != expected_reference:
            raise _error(SyntheticPolicyCode.IDENTITY_MISMATCH)
    return decision_snapshot


def _precedence(kind: SyntheticRuleKind) -> int:
    if kind is SyntheticRuleKind.OVERRIDE:
        return 3
    if kind is SyntheticRuleKind.CLARIFICATION:
        return 2
    return 1


class SyntheticMentalHealthRouteEngine:
    """Pure engineering evaluator; protected environments are always denied."""

    def evaluate(
        self,
        *,
        evaluation: SyntheticRouteEvaluation,
        policy: SyntheticPolicyArtifact | None,
        environment: Environment,
    ) -> SyntheticRouteDecision:
        if type(environment) is not Environment:
            raise _error(SyntheticPolicyCode.INVALID_TYPE)
        if environment not in {Environment.LOCAL, Environment.TEST}:
            raise _error(SyntheticPolicyCode.PROTECTED_ENVIRONMENT)
        evaluation_snapshot = _evaluation(evaluation)
        if policy is None:
            return self._degraded(
                evaluation_snapshot,
                SyntheticPolicyReasonCode.POLICY_UNAVAILABLE,
                None,
            )
        if type(policy) is not SyntheticPolicyArtifact:
            raise _error(SyntheticPolicyCode.INVALID_TYPE)
        try:
            policy_snapshot = _policy(policy)
        except SyntheticPolicyError:
            return self._degraded(
                evaluation_snapshot,
                SyntheticPolicyReasonCode.POLICY_INVALID,
                None,
            )
        reference = SyntheticPolicyReference(
            policy_id=policy_snapshot.policy_id,
            policy_version=policy_snapshot.policy_version,
            content_hash=policy_snapshot.content_hash,
        )
        if policy_snapshot.state is SyntheticPolicyState.TEST_ONLY_SUSPENDED:
            return self._degraded(
                evaluation_snapshot,
                SyntheticPolicyReasonCode.POLICY_SUSPENDED,
                policy_snapshot,
            )
        if evaluation_snapshot.evaluated_at < policy_snapshot.effective_at:
            return self._degraded(
                evaluation_snapshot,
                SyntheticPolicyReasonCode.POLICY_NOT_EFFECTIVE,
                policy_snapshot,
            )
        if evaluation_snapshot.evaluated_at >= policy_snapshot.expires_at:
            return self._degraded(
                evaluation_snapshot,
                SyntheticPolicyReasonCode.POLICY_EXPIRED,
                policy_snapshot,
            )
        evidence: dict[SyntheticSignalCode, SyntheticSignalState] = {}
        for observation in (
            *evaluation_snapshot.extractor_signals,
            *evaluation_snapshot.backstop_signals,
        ):
            existing = evidence.get(observation.code)
            if existing is not None and existing is not observation.state:
                return self._degraded(
                    evaluation_snapshot,
                    SyntheticPolicyReasonCode.EVIDENCE_CONFLICT,
                    policy_snapshot,
                )
            evidence[observation.code] = observation.state
        matched = tuple(
            rule
            for rule in policy_snapshot.rules
            if evidence.get(rule.signal_code) is rule.signal_state
        )
        if not matched:
            return self._degraded(
                evaluation_snapshot,
                SyntheticPolicyReasonCode.NO_MATCH,
                policy_snapshot,
            )
        winning_precedence = max(_precedence(rule.kind) for rule in matched)
        winners = tuple(rule for rule in matched if _precedence(rule.kind) == winning_precedence)
        routes = frozenset(rule.route for rule in winners)
        if len(routes) != 1:
            return self._degraded(
                evaluation_snapshot,
                SyntheticPolicyReasonCode.WINNER_CONFLICT,
                policy_snapshot,
            )
        route = next(iter(routes))
        decision = SyntheticRouteDecision(
            decision_id=self._decision_id(evaluation_snapshot),
            evaluation_id=evaluation_snapshot.evaluation_id,
            evaluation_fingerprint=synthetic_route_evaluation_fingerprint(evaluation_snapshot),
            route=route,
            reason_codes=tuple(sorted({rule.reason_code for rule in winners}, key=str)),
            policy_reference=reference,
            decided_at=evaluation_snapshot.evaluated_at,
        )
        return validate_synthetic_route_decision(evaluation_snapshot, decision, policy_snapshot)

    @staticmethod
    def _decision_id(evaluation: SyntheticRouteEvaluation) -> str:
        suffix = evaluation.evaluation_id.removeprefix("syn_mh_policy_evaluation_")
        return f"syn_mh_policy_decision_{suffix}"

    def _degraded(
        self,
        evaluation: SyntheticRouteEvaluation,
        reason: SyntheticPolicyReasonCode,
        policy: SyntheticPolicyArtifact | None,
    ) -> SyntheticRouteDecision:
        policy_reference = (
            None
            if policy is None
            else SyntheticPolicyReference(
                policy_id=policy.policy_id,
                policy_version=policy.policy_version,
                content_hash=policy.content_hash,
            )
        )
        decision = SyntheticRouteDecision(
            decision_id=self._decision_id(evaluation),
            evaluation_id=evaluation.evaluation_id,
            evaluation_fingerprint=synthetic_route_evaluation_fingerprint(evaluation),
            route=SyntheticRouteState.DEGRADED_SAFE_FALLBACK,
            reason_codes=(reason,),
            policy_reference=policy_reference,
            decided_at=evaluation.evaluated_at,
        )
        return validate_synthetic_route_decision(evaluation, decision, policy)


__all__ = [
    "SyntheticMentalHealthRouteEngine",
    "SyntheticPolicyArtifact",
    "SyntheticPolicyCode",
    "SyntheticPolicyError",
    "SyntheticPolicyReasonCode",
    "SyntheticPolicyReference",
    "SyntheticPolicyRule",
    "SyntheticPolicyState",
    "SyntheticRouteDecision",
    "SyntheticRouteEvaluation",
    "SyntheticRouteState",
    "SyntheticRuleKind",
    "synthetic_route_evaluation_fingerprint",
    "validate_synthetic_route_decision",
]
