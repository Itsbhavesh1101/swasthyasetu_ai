"""Closed engineering-only contracts for synthetic self-care eligibility mechanics."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256
from typing import Final

MAX_SYNTHETIC_ELIGIBILITY_PREDICATES: Final = 4
MAX_SYNTHETIC_ELIGIBILITY_RULES: Final = 4
MAX_SYNTHETIC_ELIGIBILITY_REASONS: Final = 4
SYNTHETIC_ELIGIBILITY_CONTRACT_VERSION: Final = "synthetic-self-care-eligibility.v1"

_SUFFIX = r"(?:alpha|beta|gamma|delta)"
_EVALUATION_ID = re.compile(rf"^syn_selfcare_eligibility_evaluation_{_SUFFIX}$")
_DECISION_ID = re.compile(rf"^syn_selfcare_eligibility_decision_{_SUFFIX}$")
_RULE_ID = re.compile(rf"^syn_selfcare_eligibility_rule_{_SUFFIX}$")
_GUIDANCE_ID = re.compile(rf"^syn_selfcare_guidance_{_SUFFIX}$")
_POLICY_ID = re.compile(r"^syn_selfcare_eligibility_fixture$")
_PACK_ID = re.compile(r"^syn_selfcare_pack_fixture$")
_VERSION = re.compile(r"^engineering\.v[1-9][0-9]{0,5}$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")


class EligibilityContractCode(StrEnum):
    INVALID_TYPE = "INVALID_TYPE"
    INVALID_VALUE = "INVALID_VALUE"
    LIMIT_EXCEEDED = "LIMIT_EXCEEDED"
    DUPLICATE_PREDICATE = "DUPLICATE_PREDICATE"
    DUPLICATE_RULE = "DUPLICATE_RULE"
    HASH_MISMATCH = "HASH_MISMATCH"
    IDENTITY_MISMATCH = "IDENTITY_MISMATCH"
    INCONSISTENT_RESULT = "INCONSISTENT_RESULT"
    PROTECTED_ENVIRONMENT = "PROTECTED_ENVIRONMENT"


class EligibilityContractError(ValueError):
    """Stable content-free failure for synthetic eligibility mechanics."""

    def __init__(self, code: EligibilityContractCode) -> None:
        self.code = code
        super().__init__(code.value)


def _error(code: EligibilityContractCode) -> EligibilityContractError:
    return EligibilityContractError(code)


class SyntheticEligibilityAuthority(StrEnum):
    ENGINEERING_ONLY = "ENGINEERING_ONLY"


class SyntheticEligibilityClassification(StrEnum):
    ENGINEERING_SYNTHETIC = "ENGINEERING_SYNTHETIC"


class SyntheticEligibilityVerification(StrEnum):
    UNVERIFIED = "UNVERIFIED"


class SyntheticEligibilityPolicyState(StrEnum):
    TEST_ONLY_ACTIVE = "TEST_ONLY_ACTIVE"
    TEST_ONLY_SUSPENDED = "TEST_ONLY_SUSPENDED"


class SyntheticEligibilityPredicate(StrEnum):
    CONTEXT_COMPLETE_ALPHA = "SYNTHETIC_CONTEXT_COMPLETE_ALPHA"
    CONFLICT_ALPHA = "SYNTHETIC_CONFLICT_ALPHA"
    EXCLUDE_ALPHA = "SYNTHETIC_EXCLUDE_ALPHA"
    EXCLUDE_BETA = "SYNTHETIC_EXCLUDE_BETA"
    INCLUDE_ALPHA = "SYNTHETIC_INCLUDE_ALPHA"
    INCLUDE_BETA = "SYNTHETIC_INCLUDE_BETA"


class SyntheticEligibilityOutcome(StrEnum):
    SYNTHETIC_BLOCKED = "SYNTHETIC_BLOCKED"
    SYNTHETIC_CLARIFICATION_REQUIRED = "SYNTHETIC_CLARIFICATION_REQUIRED"
    SYNTHETIC_ENGINEERING_CANDIDATE = "SYNTHETIC_ENGINEERING_CANDIDATE"


class SyntheticEligibilityReason(StrEnum):
    SYNTHETIC_CONTEXT_CONFLICT = "SYNTHETIC_CONTEXT_CONFLICT"
    SYNTHETIC_CONTEXT_INCOMPLETE = "SYNTHETIC_CONTEXT_INCOMPLETE"
    SYNTHETIC_EXCLUSION_MATCH = "SYNTHETIC_EXCLUSION_MATCH"
    SYNTHETIC_NO_RULE_MATCH = "SYNTHETIC_NO_RULE_MATCH"
    SYNTHETIC_POLICY_EXPIRED = "SYNTHETIC_POLICY_EXPIRED"
    SYNTHETIC_POLICY_INVALID = "SYNTHETIC_POLICY_INVALID"
    SYNTHETIC_POLICY_NOT_EFFECTIVE = "SYNTHETIC_POLICY_NOT_EFFECTIVE"
    SYNTHETIC_POLICY_SUSPENDED = "SYNTHETIC_POLICY_SUSPENDED"
    SYNTHETIC_POLICY_UNAVAILABLE = "SYNTHETIC_POLICY_UNAVAILABLE"
    SYNTHETIC_RULE_MATCH = "SYNTHETIC_RULE_MATCH"
    SYNTHETIC_SAFETY_BLOCK = "SYNTHETIC_SAFETY_BLOCK"


def _strict_enum(value: object, expected: type[StrEnum]) -> None:
    if type(value) is not expected:
        raise _error(EligibilityContractCode.INVALID_TYPE)


def _machine_string(value: object, pattern: re.Pattern[str]) -> str:
    if type(value) is not str:
        raise _error(EligibilityContractCode.INVALID_TYPE)
    if pattern.fullmatch(value) is None:
        raise _error(EligibilityContractCode.INVALID_VALUE)
    return value


def _utc(value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise _error(EligibilityContractCode.INVALID_TYPE)
    return value.astimezone(UTC)


def _authority(authority: object, classification: object, verification: object) -> None:
    _strict_enum(authority, SyntheticEligibilityAuthority)
    _strict_enum(classification, SyntheticEligibilityClassification)
    _strict_enum(verification, SyntheticEligibilityVerification)


def _predicates(value: object) -> tuple[SyntheticEligibilityPredicate, ...]:
    if type(value) is not tuple:
        raise _error(EligibilityContractCode.INVALID_TYPE)
    if len(value) > MAX_SYNTHETIC_ELIGIBILITY_PREDICATES:
        raise _error(EligibilityContractCode.LIMIT_EXCEEDED)
    predicates = tuple(value)
    for predicate in predicates:
        _strict_enum(predicate, SyntheticEligibilityPredicate)
    values = tuple(predicate.value for predicate in predicates)
    if len(set(values)) != len(values):
        raise _error(EligibilityContractCode.DUPLICATE_PREDICATE)
    if values != tuple(sorted(values)):
        raise _error(EligibilityContractCode.INVALID_VALUE)
    return predicates


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticEligibilityEvaluation:
    evaluation_id: str
    context_snapshot_hash: str
    predicates: tuple[SyntheticEligibilityPredicate, ...]
    evaluated_at: datetime
    authority: SyntheticEligibilityAuthority = SyntheticEligibilityAuthority.ENGINEERING_ONLY
    classification: SyntheticEligibilityClassification = (
        SyntheticEligibilityClassification.ENGINEERING_SYNTHETIC
    )
    verification: SyntheticEligibilityVerification = SyntheticEligibilityVerification.UNVERIFIED

    def __post_init__(self) -> None:
        _machine_string(self.evaluation_id, _EVALUATION_ID)
        _machine_string(self.context_snapshot_hash, _SHA256)
        predicates = _predicates(self.predicates)
        evaluated_at = _utc(self.evaluated_at)
        _authority(self.authority, self.classification, self.verification)
        object.__setattr__(self, "predicates", predicates)
        object.__setattr__(self, "evaluated_at", evaluated_at)


def _evaluation(value: object) -> SyntheticEligibilityEvaluation:
    if type(value) is not SyntheticEligibilityEvaluation:
        raise _error(EligibilityContractCode.INVALID_TYPE)
    try:
        return SyntheticEligibilityEvaluation(
            evaluation_id=value.evaluation_id,
            context_snapshot_hash=value.context_snapshot_hash,
            predicates=value.predicates,
            evaluated_at=value.evaluated_at,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
        )
    except EligibilityContractError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(EligibilityContractCode.INVALID_TYPE) from None


def synthetic_eligibility_evaluation_fingerprint(
    evaluation: SyntheticEligibilityEvaluation,
) -> str:
    snapshot = _evaluation(evaluation)
    fields = (
        SYNTHETIC_ELIGIBILITY_CONTRACT_VERSION,
        snapshot.evaluation_id,
        snapshot.context_snapshot_hash,
        *(predicate.value for predicate in snapshot.predicates),
        snapshot.evaluated_at.isoformat(),
        snapshot.authority.value,
        snapshot.classification.value,
        snapshot.verification.value,
    )
    return sha256("\x1f".join(fields).encode("ascii")).hexdigest()


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticEligibilityRule:
    rule_id: str
    guidance_id: str
    guidance_version: str
    required_predicate: SyntheticEligibilityPredicate
    exclusion_predicate: SyntheticEligibilityPredicate

    def __post_init__(self) -> None:
        _machine_string(self.rule_id, _RULE_ID)
        _machine_string(self.guidance_id, _GUIDANCE_ID)
        _machine_string(self.guidance_version, _VERSION)
        _strict_enum(self.required_predicate, SyntheticEligibilityPredicate)
        _strict_enum(self.exclusion_predicate, SyntheticEligibilityPredicate)
        if not self.required_predicate.name.startswith("INCLUDE_"):
            raise _error(EligibilityContractCode.INVALID_VALUE)
        if not self.exclusion_predicate.name.startswith("EXCLUDE_"):
            raise _error(EligibilityContractCode.INVALID_VALUE)
        suffix = self.rule_id.rsplit("_", 1)[-1]
        if (
            self.guidance_id.rsplit("_", 1)[-1] != suffix
            or self.required_predicate.name.rsplit("_", 1)[-1].lower() != suffix
            or self.exclusion_predicate.name.rsplit("_", 1)[-1].lower() != suffix
        ):
            raise _error(EligibilityContractCode.INVALID_VALUE)


def _rule(value: object) -> SyntheticEligibilityRule:
    if type(value) is not SyntheticEligibilityRule:
        raise _error(EligibilityContractCode.INVALID_TYPE)
    try:
        return SyntheticEligibilityRule(
            rule_id=value.rule_id,
            guidance_id=value.guidance_id,
            guidance_version=value.guidance_version,
            required_predicate=value.required_predicate,
            exclusion_predicate=value.exclusion_predicate,
        )
    except EligibilityContractError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(EligibilityContractCode.INVALID_TYPE) from None


def _policy_hash(
    *,
    policy_id: str,
    policy_version: str,
    effective_at: datetime,
    expires_at: datetime,
    state: SyntheticEligibilityPolicyState,
    rules: tuple[SyntheticEligibilityRule, ...],
    authority: SyntheticEligibilityAuthority,
    classification: SyntheticEligibilityClassification,
    verification: SyntheticEligibilityVerification,
) -> str:
    fields = [
        SYNTHETIC_ELIGIBILITY_CONTRACT_VERSION,
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
                rule.guidance_id,
                rule.guidance_version,
                rule.required_predicate.value,
                rule.exclusion_predicate.value,
            )
        )
    fields.extend((authority.value, classification.value, verification.value))
    return sha256("\x1f".join(fields).encode("ascii")).hexdigest()


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticEligibilityPolicy:
    policy_id: str
    policy_version: str
    content_hash: str
    effective_at: datetime
    expires_at: datetime
    state: SyntheticEligibilityPolicyState
    rules: tuple[SyntheticEligibilityRule, ...]
    authority: SyntheticEligibilityAuthority = SyntheticEligibilityAuthority.ENGINEERING_ONLY
    classification: SyntheticEligibilityClassification = (
        SyntheticEligibilityClassification.ENGINEERING_SYNTHETIC
    )
    verification: SyntheticEligibilityVerification = SyntheticEligibilityVerification.UNVERIFIED

    def __post_init__(self) -> None:
        policy_id = _machine_string(self.policy_id, _POLICY_ID)
        policy_version = _machine_string(self.policy_version, _VERSION)
        _machine_string(self.content_hash, _SHA256)
        effective_at = _utc(self.effective_at)
        expires_at = _utc(self.expires_at)
        if expires_at <= effective_at:
            raise _error(EligibilityContractCode.INVALID_VALUE)
        _strict_enum(self.state, SyntheticEligibilityPolicyState)
        if type(self.rules) is not tuple:
            raise _error(EligibilityContractCode.INVALID_TYPE)
        if not self.rules or len(self.rules) > MAX_SYNTHETIC_ELIGIBILITY_RULES:
            raise _error(EligibilityContractCode.LIMIT_EXCEEDED)
        rules = tuple(_rule(rule) for rule in self.rules)
        rule_ids = tuple(rule.rule_id for rule in rules)
        if len(set(rule_ids)) != len(rule_ids):
            raise _error(EligibilityContractCode.DUPLICATE_RULE)
        if rule_ids != tuple(sorted(rule_ids)):
            raise _error(EligibilityContractCode.INVALID_VALUE)
        _authority(self.authority, self.classification, self.verification)
        expected = _policy_hash(
            policy_id=policy_id,
            policy_version=policy_version,
            effective_at=effective_at,
            expires_at=expires_at,
            state=self.state,
            rules=rules,
            authority=self.authority,
            classification=self.classification,
            verification=self.verification,
        )
        if self.content_hash != expected:
            raise _error(EligibilityContractCode.HASH_MISMATCH)
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
        state: SyntheticEligibilityPolicyState,
        rules: tuple[SyntheticEligibilityRule, ...],
    ) -> SyntheticEligibilityPolicy:
        _strict_enum(state, SyntheticEligibilityPolicyState)
        if type(rules) is not tuple:
            raise _error(EligibilityContractCode.INVALID_TYPE)
        normalized_effective = _utc(effective_at)
        normalized_expiry = _utc(expires_at)
        validated_rules = tuple(
            sorted((_rule(rule) for rule in rules), key=lambda item: item.rule_id)
        )
        authority = SyntheticEligibilityAuthority.ENGINEERING_ONLY
        classification = SyntheticEligibilityClassification.ENGINEERING_SYNTHETIC
        verification = SyntheticEligibilityVerification.UNVERIFIED
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
                authority=authority,
                classification=classification,
                verification=verification,
            ),
            effective_at=normalized_effective,
            expires_at=normalized_expiry,
            state=state,
            rules=validated_rules,
            authority=authority,
            classification=classification,
            verification=verification,
        )


def validate_synthetic_eligibility_policy(value: object) -> SyntheticEligibilityPolicy:
    if type(value) is not SyntheticEligibilityPolicy:
        raise _error(EligibilityContractCode.INVALID_TYPE)
    try:
        return SyntheticEligibilityPolicy(
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
    except EligibilityContractError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(EligibilityContractCode.INVALID_TYPE) from None


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticEligibilityCandidateReference:
    guidance_id: str
    guidance_version: str

    def __post_init__(self) -> None:
        _machine_string(self.guidance_id, _GUIDANCE_ID)
        _machine_string(self.guidance_version, _VERSION)


def _candidate(value: object) -> SyntheticEligibilityCandidateReference:
    if type(value) is not SyntheticEligibilityCandidateReference:
        raise _error(EligibilityContractCode.INVALID_TYPE)
    try:
        return SyntheticEligibilityCandidateReference(
            guidance_id=value.guidance_id,
            guidance_version=value.guidance_version,
        )
    except EligibilityContractError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(EligibilityContractCode.INVALID_TYPE) from None


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticEligibilityPolicyReference:
    policy_id: str
    policy_version: str
    content_hash: str

    def __post_init__(self) -> None:
        _machine_string(self.policy_id, _POLICY_ID)
        _machine_string(self.policy_version, _VERSION)
        _machine_string(self.content_hash, _SHA256)


def _policy_reference(value: object) -> SyntheticEligibilityPolicyReference:
    if type(value) is not SyntheticEligibilityPolicyReference:
        raise _error(EligibilityContractCode.INVALID_TYPE)
    try:
        return SyntheticEligibilityPolicyReference(
            policy_id=value.policy_id,
            policy_version=value.policy_version,
            content_hash=value.content_hash,
        )
    except EligibilityContractError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(EligibilityContractCode.INVALID_TYPE) from None


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticEligibilityResult:
    decision_id: str
    evaluation_id: str
    evaluation_fingerprint: str
    safety_fingerprint: str
    knowledge_pack_id: str
    knowledge_pack_version: str
    knowledge_pack_hash: str
    policy_reference: SyntheticEligibilityPolicyReference | None
    outcome: SyntheticEligibilityOutcome
    reason_codes: tuple[SyntheticEligibilityReason, ...]
    candidates: tuple[SyntheticEligibilityCandidateReference, ...]
    decided_at: datetime
    authority: SyntheticEligibilityAuthority = SyntheticEligibilityAuthority.ENGINEERING_ONLY
    classification: SyntheticEligibilityClassification = (
        SyntheticEligibilityClassification.ENGINEERING_SYNTHETIC
    )
    verification: SyntheticEligibilityVerification = SyntheticEligibilityVerification.UNVERIFIED

    def __post_init__(self) -> None:
        _machine_string(self.decision_id, _DECISION_ID)
        _machine_string(self.evaluation_id, _EVALUATION_ID)
        _machine_string(self.evaluation_fingerprint, _SHA256)
        _machine_string(self.safety_fingerprint, _SHA256)
        _machine_string(self.knowledge_pack_id, _PACK_ID)
        _machine_string(self.knowledge_pack_version, _VERSION)
        _machine_string(self.knowledge_pack_hash, _SHA256)
        reference = (
            None if self.policy_reference is None else _policy_reference(self.policy_reference)
        )
        _strict_enum(self.outcome, SyntheticEligibilityOutcome)
        if type(self.reason_codes) is not tuple or not self.reason_codes:
            raise _error(EligibilityContractCode.INVALID_TYPE)
        if len(self.reason_codes) > MAX_SYNTHETIC_ELIGIBILITY_REASONS:
            raise _error(EligibilityContractCode.LIMIT_EXCEEDED)
        reasons = tuple(self.reason_codes)
        for reason in reasons:
            _strict_enum(reason, SyntheticEligibilityReason)
        reason_values = tuple(reason.value for reason in reasons)
        if len(set(reason_values)) != len(reason_values) or reason_values != tuple(
            sorted(reason_values)
        ):
            raise _error(EligibilityContractCode.INVALID_VALUE)
        if type(self.candidates) is not tuple:
            raise _error(EligibilityContractCode.INVALID_TYPE)
        candidates = tuple(_candidate(candidate) for candidate in self.candidates)
        candidate_ids = tuple(candidate.guidance_id for candidate in candidates)
        if len(set(candidate_ids)) != len(candidate_ids) or candidate_ids != tuple(
            sorted(candidate_ids)
        ):
            raise _error(EligibilityContractCode.INVALID_VALUE)
        candidate_outcome = (
            self.outcome is SyntheticEligibilityOutcome.SYNTHETIC_ENGINEERING_CANDIDATE
        )
        if candidate_outcome != bool(candidates):
            raise _error(EligibilityContractCode.INCONSISTENT_RESULT)
        if candidate_outcome and reference is None:
            raise _error(EligibilityContractCode.INCONSISTENT_RESULT)
        _authority(self.authority, self.classification, self.verification)
        object.__setattr__(self, "policy_reference", reference)
        object.__setattr__(self, "reason_codes", reasons)
        object.__setattr__(self, "candidates", candidates)
        object.__setattr__(self, "decided_at", _utc(self.decided_at))


__all__ = [
    "MAX_SYNTHETIC_ELIGIBILITY_PREDICATES",
    "SYNTHETIC_ELIGIBILITY_CONTRACT_VERSION",
    "EligibilityContractCode",
    "EligibilityContractError",
    "SyntheticEligibilityAuthority",
    "SyntheticEligibilityCandidateReference",
    "SyntheticEligibilityClassification",
    "SyntheticEligibilityEvaluation",
    "SyntheticEligibilityOutcome",
    "SyntheticEligibilityPolicy",
    "SyntheticEligibilityPolicyReference",
    "SyntheticEligibilityPolicyState",
    "SyntheticEligibilityPredicate",
    "SyntheticEligibilityReason",
    "SyntheticEligibilityResult",
    "SyntheticEligibilityRule",
    "SyntheticEligibilityVerification",
    "synthetic_eligibility_evaluation_fingerprint",
    "validate_synthetic_eligibility_policy",
]
