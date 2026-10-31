"""Closed engineering-only contracts for synthetic self-care eligibility mechanics."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256
from typing import Final

from app.config.settings import Environment
from app.modules.safety.domain import SafetyDecision, SafetyRoute
from app.modules.self_care.contracts import (
    SelfCareContractError,
    SyntheticKnowledgePack,
    validate_synthetic_knowledge_pack,
)

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
    SYNTHETIC_KNOWLEDGE_INVALID = "SYNTHETIC_KNOWLEDGE_INVALID"
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


def _safety_decision(value: object) -> SafetyDecision:
    if type(value) is not SafetyDecision:
        raise _error(EligibilityContractCode.INVALID_TYPE)
    try:
        return SafetyDecision(
            route=value.route,
            reason_codes=value.reason_codes,
            policy_id=value.policy_id,
            policy_version=value.policy_version,
            requires_clarification=value.requires_clarification,
            blocks_self_care=value.blocks_self_care,
            created_at=value.created_at,
        )
    except (AttributeError, TypeError, ValueError):
        raise _error(EligibilityContractCode.INVALID_VALUE) from None


def safety_decision_fingerprint(value: SafetyDecision) -> str:
    snapshot = _safety_decision(value)
    fields = (
        snapshot.route.value,
        *snapshot.reason_codes,
        snapshot.policy_id,
        snapshot.policy_version,
        str(snapshot.requires_clarification).lower(),
        str(snapshot.blocks_self_care).lower(),
        snapshot.created_at.isoformat(),
    )
    return sha256("\x1f".join(fields).encode("ascii")).hexdigest()


def _knowledge_pack(value: object) -> SyntheticKnowledgePack:
    try:
        return validate_synthetic_knowledge_pack(value)
    except SelfCareContractError:
        raise _error(EligibilityContractCode.INVALID_VALUE) from None


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
        allowed_reasons = {
            SyntheticEligibilityOutcome.SYNTHETIC_ENGINEERING_CANDIDATE: {
                SyntheticEligibilityReason.SYNTHETIC_RULE_MATCH
            },
            SyntheticEligibilityOutcome.SYNTHETIC_CLARIFICATION_REQUIRED: {
                SyntheticEligibilityReason.SYNTHETIC_CONTEXT_CONFLICT,
                SyntheticEligibilityReason.SYNTHETIC_CONTEXT_INCOMPLETE,
                SyntheticEligibilityReason.SYNTHETIC_NO_RULE_MATCH,
            },
            SyntheticEligibilityOutcome.SYNTHETIC_BLOCKED: {
                SyntheticEligibilityReason.SYNTHETIC_EXCLUSION_MATCH,
                SyntheticEligibilityReason.SYNTHETIC_KNOWLEDGE_INVALID,
                SyntheticEligibilityReason.SYNTHETIC_POLICY_EXPIRED,
                SyntheticEligibilityReason.SYNTHETIC_POLICY_INVALID,
                SyntheticEligibilityReason.SYNTHETIC_POLICY_NOT_EFFECTIVE,
                SyntheticEligibilityReason.SYNTHETIC_POLICY_SUSPENDED,
                SyntheticEligibilityReason.SYNTHETIC_POLICY_UNAVAILABLE,
                SyntheticEligibilityReason.SYNTHETIC_SAFETY_BLOCK,
            },
        }
        if len(reasons) != 1 or reasons[0] not in allowed_reasons[self.outcome]:
            raise _error(EligibilityContractCode.INCONSISTENT_RESULT)
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


def _result(value: object) -> SyntheticEligibilityResult:
    if type(value) is not SyntheticEligibilityResult:
        raise _error(EligibilityContractCode.INVALID_TYPE)
    try:
        return SyntheticEligibilityResult(
            decision_id=value.decision_id,
            evaluation_id=value.evaluation_id,
            evaluation_fingerprint=value.evaluation_fingerprint,
            safety_fingerprint=value.safety_fingerprint,
            knowledge_pack_id=value.knowledge_pack_id,
            knowledge_pack_version=value.knowledge_pack_version,
            knowledge_pack_hash=value.knowledge_pack_hash,
            policy_reference=value.policy_reference,
            outcome=value.outcome,
            reason_codes=value.reason_codes,
            candidates=value.candidates,
            decided_at=value.decided_at,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
        )
    except EligibilityContractError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(EligibilityContractCode.INVALID_TYPE) from None


def _reference(policy: SyntheticEligibilityPolicy) -> SyntheticEligibilityPolicyReference:
    return SyntheticEligibilityPolicyReference(
        policy_id=policy.policy_id,
        policy_version=policy.policy_version,
        content_hash=policy.content_hash,
    )


def _decision_id(evaluation: SyntheticEligibilityEvaluation) -> str:
    suffix = evaluation.evaluation_id.removeprefix("syn_selfcare_eligibility_evaluation_")
    return f"syn_selfcare_eligibility_decision_{suffix}"


def validate_synthetic_eligibility_result(
    *,
    evaluation: SyntheticEligibilityEvaluation,
    safety_decision: SafetyDecision,
    knowledge_pack: SyntheticKnowledgePack,
    policy: SyntheticEligibilityPolicy | None,
    result: SyntheticEligibilityResult,
) -> SyntheticEligibilityResult:
    evaluation_snapshot = _evaluation(evaluation)
    safety_snapshot = _safety_decision(safety_decision)
    pack_snapshot = _knowledge_pack(knowledge_pack)
    result_snapshot = _result(result)
    policy_snapshot = None if policy is None else validate_synthetic_eligibility_policy(policy)
    expected_reference = None if policy_snapshot is None else _reference(policy_snapshot)
    if (
        result_snapshot.decision_id != _decision_id(evaluation_snapshot)
        or result_snapshot.evaluation_id != evaluation_snapshot.evaluation_id
        or result_snapshot.evaluation_fingerprint
        != synthetic_eligibility_evaluation_fingerprint(evaluation_snapshot)
        or result_snapshot.safety_fingerprint != safety_decision_fingerprint(safety_snapshot)
        or result_snapshot.knowledge_pack_id != pack_snapshot.pack_id
        or result_snapshot.knowledge_pack_version != pack_snapshot.pack_version
        or result_snapshot.knowledge_pack_hash != pack_snapshot.content_hash
        or result_snapshot.policy_reference != expected_reference
        or result_snapshot.decided_at != evaluation_snapshot.evaluated_at
    ):
        raise _error(EligibilityContractCode.IDENTITY_MISMATCH)
    known_items = {(item.guidance_id, item.version) for item in pack_snapshot.items}
    if any(
        (candidate.guidance_id, candidate.guidance_version) not in known_items
        for candidate in result_snapshot.candidates
    ):
        raise _error(EligibilityContractCode.IDENTITY_MISMATCH)
    return result_snapshot


class SyntheticEligibilityEngine:
    """Pure toy evaluator; never produces clinical or display authority."""

    def evaluate(
        self,
        *,
        evaluation: SyntheticEligibilityEvaluation,
        safety_decision: SafetyDecision,
        knowledge_pack: SyntheticKnowledgePack,
        policy: SyntheticEligibilityPolicy | None,
        environment: Environment,
    ) -> SyntheticEligibilityResult:
        if type(environment) is not Environment:
            raise _error(EligibilityContractCode.INVALID_TYPE)
        if environment not in {Environment.LOCAL, Environment.TEST}:
            raise _error(EligibilityContractCode.PROTECTED_ENVIRONMENT)
        evaluation_snapshot = _evaluation(evaluation)
        safety_snapshot = _safety_decision(safety_decision)
        pack_snapshot = _knowledge_pack(knowledge_pack)
        policy_snapshot: SyntheticEligibilityPolicy | None
        if not self._is_exact_positive_safety(safety_snapshot, evaluation_snapshot):
            return self._result(
                evaluation=evaluation_snapshot,
                safety=safety_snapshot,
                pack=pack_snapshot,
                policy=None,
                outcome=SyntheticEligibilityOutcome.SYNTHETIC_BLOCKED,
                reason=SyntheticEligibilityReason.SYNTHETIC_SAFETY_BLOCK,
            )
        if policy is None:
            return self._result(
                evaluation=evaluation_snapshot,
                safety=safety_snapshot,
                pack=pack_snapshot,
                policy=None,
                outcome=SyntheticEligibilityOutcome.SYNTHETIC_BLOCKED,
                reason=SyntheticEligibilityReason.SYNTHETIC_POLICY_UNAVAILABLE,
            )
        try:
            policy_snapshot = validate_synthetic_eligibility_policy(policy)
        except EligibilityContractError:
            return self._result(
                evaluation=evaluation_snapshot,
                safety=safety_snapshot,
                pack=pack_snapshot,
                policy=None,
                outcome=SyntheticEligibilityOutcome.SYNTHETIC_BLOCKED,
                reason=SyntheticEligibilityReason.SYNTHETIC_POLICY_INVALID,
            )
        if policy_snapshot.state is SyntheticEligibilityPolicyState.TEST_ONLY_SUSPENDED:
            return self._result(
                evaluation=evaluation_snapshot,
                safety=safety_snapshot,
                pack=pack_snapshot,
                policy=policy_snapshot,
                outcome=SyntheticEligibilityOutcome.SYNTHETIC_BLOCKED,
                reason=SyntheticEligibilityReason.SYNTHETIC_POLICY_SUSPENDED,
            )
        if evaluation_snapshot.evaluated_at < policy_snapshot.effective_at:
            return self._result(
                evaluation=evaluation_snapshot,
                safety=safety_snapshot,
                pack=pack_snapshot,
                policy=policy_snapshot,
                outcome=SyntheticEligibilityOutcome.SYNTHETIC_BLOCKED,
                reason=SyntheticEligibilityReason.SYNTHETIC_POLICY_NOT_EFFECTIVE,
            )
        if evaluation_snapshot.evaluated_at >= policy_snapshot.expires_at:
            return self._result(
                evaluation=evaluation_snapshot,
                safety=safety_snapshot,
                pack=pack_snapshot,
                policy=policy_snapshot,
                outcome=SyntheticEligibilityOutcome.SYNTHETIC_BLOCKED,
                reason=SyntheticEligibilityReason.SYNTHETIC_POLICY_EXPIRED,
            )
        if pack_snapshot.created_at > evaluation_snapshot.evaluated_at:
            return self._result(
                evaluation=evaluation_snapshot,
                safety=safety_snapshot,
                pack=pack_snapshot,
                policy=policy_snapshot,
                outcome=SyntheticEligibilityOutcome.SYNTHETIC_BLOCKED,
                reason=SyntheticEligibilityReason.SYNTHETIC_KNOWLEDGE_INVALID,
            )
        supplied = frozenset(evaluation_snapshot.predicates)
        if SyntheticEligibilityPredicate.CONFLICT_ALPHA in supplied:
            return self._result(
                evaluation=evaluation_snapshot,
                safety=safety_snapshot,
                pack=pack_snapshot,
                policy=policy_snapshot,
                outcome=SyntheticEligibilityOutcome.SYNTHETIC_CLARIFICATION_REQUIRED,
                reason=SyntheticEligibilityReason.SYNTHETIC_CONTEXT_CONFLICT,
            )
        if SyntheticEligibilityPredicate.CONTEXT_COMPLETE_ALPHA not in supplied:
            return self._result(
                evaluation=evaluation_snapshot,
                safety=safety_snapshot,
                pack=pack_snapshot,
                policy=policy_snapshot,
                outcome=SyntheticEligibilityOutcome.SYNTHETIC_CLARIFICATION_REQUIRED,
                reason=SyntheticEligibilityReason.SYNTHETIC_CONTEXT_INCOMPLETE,
            )
        matched = tuple(
            rule for rule in policy_snapshot.rules if rule.required_predicate in supplied
        )
        if any(rule.exclusion_predicate in supplied for rule in matched):
            return self._result(
                evaluation=evaluation_snapshot,
                safety=safety_snapshot,
                pack=pack_snapshot,
                policy=policy_snapshot,
                outcome=SyntheticEligibilityOutcome.SYNTHETIC_BLOCKED,
                reason=SyntheticEligibilityReason.SYNTHETIC_EXCLUSION_MATCH,
            )
        if not matched:
            return self._result(
                evaluation=evaluation_snapshot,
                safety=safety_snapshot,
                pack=pack_snapshot,
                policy=policy_snapshot,
                outcome=SyntheticEligibilityOutcome.SYNTHETIC_CLARIFICATION_REQUIRED,
                reason=SyntheticEligibilityReason.SYNTHETIC_NO_RULE_MATCH,
            )
        known_items = {(item.guidance_id, item.version) for item in pack_snapshot.items}
        if any((rule.guidance_id, rule.guidance_version) not in known_items for rule in matched):
            return self._result(
                evaluation=evaluation_snapshot,
                safety=safety_snapshot,
                pack=pack_snapshot,
                policy=policy_snapshot,
                outcome=SyntheticEligibilityOutcome.SYNTHETIC_BLOCKED,
                reason=SyntheticEligibilityReason.SYNTHETIC_POLICY_INVALID,
            )
        candidates = tuple(
            SyntheticEligibilityCandidateReference(
                guidance_id=rule.guidance_id,
                guidance_version=rule.guidance_version,
            )
            for rule in matched
        )
        return self._result(
            evaluation=evaluation_snapshot,
            safety=safety_snapshot,
            pack=pack_snapshot,
            policy=policy_snapshot,
            outcome=SyntheticEligibilityOutcome.SYNTHETIC_ENGINEERING_CANDIDATE,
            reason=SyntheticEligibilityReason.SYNTHETIC_RULE_MATCH,
            candidates=candidates,
        )

    @staticmethod
    def _is_exact_positive_safety(
        safety: SafetyDecision,
        evaluation: SyntheticEligibilityEvaluation,
    ) -> bool:
        return (
            safety.route is SafetyRoute.SUPPORTED_SELF_CARE
            and safety.reason_codes == ("SYNTHETIC_SELF_CARE_A",)
            and safety.policy_id == "synthetic-physical-safety-metadata"
            and safety.policy_version == "engineering.1"
            and not safety.requires_clarification
            and not safety.blocks_self_care
            and safety.created_at <= evaluation.evaluated_at
        )

    @staticmethod
    def _result(
        *,
        evaluation: SyntheticEligibilityEvaluation,
        safety: SafetyDecision,
        pack: SyntheticKnowledgePack,
        policy: SyntheticEligibilityPolicy | None,
        outcome: SyntheticEligibilityOutcome,
        reason: SyntheticEligibilityReason,
        candidates: tuple[SyntheticEligibilityCandidateReference, ...] = (),
    ) -> SyntheticEligibilityResult:
        result = SyntheticEligibilityResult(
            decision_id=_decision_id(evaluation),
            evaluation_id=evaluation.evaluation_id,
            evaluation_fingerprint=synthetic_eligibility_evaluation_fingerprint(evaluation),
            safety_fingerprint=safety_decision_fingerprint(safety),
            knowledge_pack_id=pack.pack_id,
            knowledge_pack_version=pack.pack_version,
            knowledge_pack_hash=pack.content_hash,
            policy_reference=None if policy is None else _reference(policy),
            outcome=outcome,
            reason_codes=(reason,),
            candidates=candidates,
            decided_at=evaluation.evaluated_at,
        )
        return validate_synthetic_eligibility_result(
            evaluation=evaluation,
            safety_decision=safety,
            knowledge_pack=pack,
            policy=policy,
            result=result,
        )


__all__ = [
    "MAX_SYNTHETIC_ELIGIBILITY_PREDICATES",
    "SYNTHETIC_ELIGIBILITY_CONTRACT_VERSION",
    "EligibilityContractCode",
    "EligibilityContractError",
    "SyntheticEligibilityAuthority",
    "SyntheticEligibilityCandidateReference",
    "SyntheticEligibilityClassification",
    "SyntheticEligibilityEvaluation",
    "SyntheticEligibilityEngine",
    "SyntheticEligibilityOutcome",
    "SyntheticEligibilityPolicy",
    "SyntheticEligibilityPolicyReference",
    "SyntheticEligibilityPolicyState",
    "SyntheticEligibilityPredicate",
    "SyntheticEligibilityReason",
    "SyntheticEligibilityResult",
    "SyntheticEligibilityRule",
    "SyntheticEligibilityVerification",
    "safety_decision_fingerprint",
    "synthetic_eligibility_evaluation_fingerprint",
    "validate_synthetic_eligibility_result",
    "validate_synthetic_eligibility_policy",
]
