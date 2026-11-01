"""Strict no-release contracts for synthetic P24 evidence planning."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256
from typing import Final

from app.config import Environment

SYNTHETIC_RELEASE_EVIDENCE_CONTRACT_VERSION: Final = "synthetic-release-evidence.v1"

_VERSION = re.compile(r"^engineering\.v[1-9][0-9]{0,5}$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_GIT_SHA = re.compile(r"^[a-f0-9]{40}$")
_MANIFEST_ID = re.compile(r"^syn_release_evidence_(?:alpha|beta|gamma|delta)$")
_PROTECTED_ENVIRONMENTS = frozenset(
    {Environment.STAGING, Environment.PILOT, Environment.PRODUCTION}
)


class ReleaseEvidenceContractCode(StrEnum):
    INVALID_TYPE = "INVALID_TYPE"
    INVALID_VALUE = "INVALID_VALUE"
    INVALID_CHRONOLOGY = "INVALID_CHRONOLOGY"
    INCOMPLETE_INVENTORY = "INCOMPLETE_INVENTORY"
    DUPLICATE_CATEGORY = "DUPLICATE_CATEGORY"
    INVALID_ORDER = "INVALID_ORDER"
    SNAPSHOT_DRIFT = "SNAPSHOT_DRIFT"
    PROTECTED_ENVIRONMENT = "PROTECTED_ENVIRONMENT"


class ReleaseEvidenceContractError(ValueError):
    """Stable content-free release-evidence failure."""

    def __init__(self, code: ReleaseEvidenceContractCode) -> None:
        self.code = code
        super().__init__(code.value)


class ReleaseEvidenceAuthority(StrEnum):
    ENGINEERING_ONLY = "ENGINEERING_ONLY"


class ReleaseEvidenceClassification(StrEnum):
    ENGINEERING_SYNTHETIC = "ENGINEERING_SYNTHETIC"


class ReleaseEvidenceVerification(StrEnum):
    UNVERIFIED = "UNVERIFIED"


class ReleaseEvidenceExecutionState(StrEnum):
    NOT_EXECUTED = "NOT_EXECUTED"


class ReleaseEvidenceEligibility(StrEnum):
    NOT_ELIGIBLE = "NOT_ELIGIBLE"


class ReleaseEvidenceReviewState(StrEnum):
    HUMAN_APPLICABILITY_AND_APPROVAL_REQUIRED = "HUMAN_APPLICABILITY_AND_APPROVAL_REQUIRED"


class ReleaseDecisionState(StrEnum):
    NOT_RECORDED = "NOT_RECORDED"


class SyntheticReleaseEvidenceCategory(StrEnum):
    CLINICAL_POLICY_SIGN_OFF = "CLINICAL_POLICY_SIGN_OFF"
    MENTAL_HEALTH_POLICY_SIGN_OFF = "MENTAL_HEALTH_POLICY_SIGN_OFF"
    SELF_CARE_CONTENT_APPROVAL = "SELF_CARE_CONTENT_APPROVAL"
    VERIFIED_RESOURCE_REGISTRY = "VERIFIED_RESOURCE_REGISTRY"
    PRIVACY_NOTICE = "PRIVACY_NOTICE"
    CONSENT_TEXT = "CONSENT_TEXT"
    THREAT_MODEL = "THREAT_MODEL"
    INCIDENT_RUNBOOK = "INCIDENT_RUNBOOK"
    DATA_RETENTION_POLICY = "DATA_RETENTION_POLICY"
    RELEASE_CHECKLIST = "RELEASE_CHECKLIST"
    PILOT_PROTOCOL = "PILOT_PROTOCOL"
    MODEL_CARDS = "MODEL_CARDS"
    DATASET_CARDS = "DATASET_CARDS"


def _error(code: ReleaseEvidenceContractCode) -> ReleaseEvidenceContractError:
    return ReleaseEvidenceContractError(code)


def _strict_enum(value: object, expected: type[StrEnum]) -> None:
    if type(value) is not expected:
        raise _error(ReleaseEvidenceContractCode.INVALID_TYPE)


def _machine_string(value: object, pattern: re.Pattern[str]) -> str:
    if type(value) is not str:
        raise _error(ReleaseEvidenceContractCode.INVALID_TYPE)
    if pattern.fullmatch(value) is None:
        raise _error(ReleaseEvidenceContractCode.INVALID_VALUE)
    return value


def _utc(value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise _error(ReleaseEvidenceContractCode.INVALID_TYPE)
    return value.astimezone(UTC)


def _contract_version(value: object) -> None:
    if type(value) is not str or value != SYNTHETIC_RELEASE_EVIDENCE_CONTRACT_VERSION:
        raise _error(ReleaseEvidenceContractCode.INVALID_VALUE)


def _labels(
    authority: object,
    classification: object,
    verification: object,
    execution_state: object,
    eligibility: object,
    review_state: object,
    decision_state: object,
) -> None:
    if authority is not ReleaseEvidenceAuthority.ENGINEERING_ONLY:
        raise _error(ReleaseEvidenceContractCode.INVALID_VALUE)
    if classification is not ReleaseEvidenceClassification.ENGINEERING_SYNTHETIC:
        raise _error(ReleaseEvidenceContractCode.INVALID_VALUE)
    if verification is not ReleaseEvidenceVerification.UNVERIFIED:
        raise _error(ReleaseEvidenceContractCode.INVALID_VALUE)
    if execution_state is not ReleaseEvidenceExecutionState.NOT_EXECUTED:
        raise _error(ReleaseEvidenceContractCode.INVALID_VALUE)
    if eligibility is not ReleaseEvidenceEligibility.NOT_ELIGIBLE:
        raise _error(ReleaseEvidenceContractCode.INVALID_VALUE)
    if review_state is not ReleaseEvidenceReviewState.HUMAN_APPLICABILITY_AND_APPROVAL_REQUIRED:
        raise _error(ReleaseEvidenceContractCode.INVALID_VALUE)
    if decision_state is not ReleaseDecisionState.NOT_RECORDED:
        raise _error(ReleaseEvidenceContractCode.INVALID_VALUE)


def _canonical_hash(payload: object) -> str:
    encoded = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticReleaseEvidenceRequirement:
    category: SyntheticReleaseEvidenceCategory
    requirement_version: str
    build_sha: str = field(repr=False)
    requirement_hash: str = field(repr=False)
    acceptance_criteria_hash: str = field(repr=False)
    negative_test_plan_hash: str = field(repr=False)
    responsible_roles_hash: str = field(repr=False)
    created_at: datetime
    authority: ReleaseEvidenceAuthority = ReleaseEvidenceAuthority.ENGINEERING_ONLY
    classification: ReleaseEvidenceClassification = (
        ReleaseEvidenceClassification.ENGINEERING_SYNTHETIC
    )
    verification: ReleaseEvidenceVerification = ReleaseEvidenceVerification.UNVERIFIED
    execution_state: ReleaseEvidenceExecutionState = ReleaseEvidenceExecutionState.NOT_EXECUTED
    eligibility: ReleaseEvidenceEligibility = ReleaseEvidenceEligibility.NOT_ELIGIBLE
    review_state: ReleaseEvidenceReviewState = (
        ReleaseEvidenceReviewState.HUMAN_APPLICABILITY_AND_APPROVAL_REQUIRED
    )
    decision_state: ReleaseDecisionState = ReleaseDecisionState.NOT_RECORDED
    contract_version: str = SYNTHETIC_RELEASE_EVIDENCE_CONTRACT_VERSION
    _fingerprint: str = field(init=False, repr=False, compare=True)

    def __post_init__(self) -> None:
        _strict_enum(self.category, SyntheticReleaseEvidenceCategory)
        _machine_string(self.requirement_version, _VERSION)
        _machine_string(self.build_sha, _GIT_SHA)
        _machine_string(self.requirement_hash, _SHA256)
        _machine_string(self.acceptance_criteria_hash, _SHA256)
        _machine_string(self.negative_test_plan_hash, _SHA256)
        _machine_string(self.responsible_roles_hash, _SHA256)
        created_at = _utc(self.created_at)
        _labels(
            self.authority,
            self.classification,
            self.verification,
            self.execution_state,
            self.eligibility,
            self.review_state,
            self.decision_state,
        )
        _contract_version(self.contract_version)
        fingerprint = _canonical_hash(
            {
                "acceptance_criteria_hash": self.acceptance_criteria_hash,
                "authority": self.authority.value,
                "build_sha": self.build_sha,
                "category": self.category.value,
                "classification": self.classification.value,
                "contract_version": self.contract_version,
                "created_at": created_at.isoformat(),
                "decision_state": self.decision_state.value,
                "eligibility": self.eligibility.value,
                "execution_state": self.execution_state.value,
                "negative_test_plan_hash": self.negative_test_plan_hash,
                "requirement_hash": self.requirement_hash,
                "requirement_version": self.requirement_version,
                "responsible_roles_hash": self.responsible_roles_hash,
                "review_state": self.review_state.value,
                "verification": self.verification.value,
            }
        )
        object.__setattr__(self, "created_at", created_at)
        object.__setattr__(self, "_fingerprint", fingerprint)

    @property
    def fingerprint(self) -> str:
        return self._fingerprint


def snapshot_release_evidence_requirement(
    value: object,
) -> SyntheticReleaseEvidenceRequirement:
    if type(value) is not SyntheticReleaseEvidenceRequirement:
        raise _error(ReleaseEvidenceContractCode.INVALID_TYPE)
    try:
        snapshot = SyntheticReleaseEvidenceRequirement(
            category=value.category,
            requirement_version=value.requirement_version,
            build_sha=value.build_sha,
            requirement_hash=value.requirement_hash,
            acceptance_criteria_hash=value.acceptance_criteria_hash,
            negative_test_plan_hash=value.negative_test_plan_hash,
            responsible_roles_hash=value.responsible_roles_hash,
            created_at=value.created_at,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
            execution_state=value.execution_state,
            eligibility=value.eligibility,
            review_state=value.review_state,
            decision_state=value.decision_state,
            contract_version=value.contract_version,
        )
    except ReleaseEvidenceContractError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(ReleaseEvidenceContractCode.INVALID_TYPE) from None
    if snapshot.fingerprint != value.fingerprint:
        raise _error(ReleaseEvidenceContractCode.SNAPSHOT_DRIFT)
    return snapshot


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticReleaseEvidenceManifest:
    manifest_id: str
    build_sha: str = field(repr=False)
    config_hash: str = field(repr=False)
    proposed_scope_hash: str = field(repr=False)
    generated_at: datetime
    requirements: tuple[SyntheticReleaseEvidenceRequirement, ...] = field(repr=False)
    authority: ReleaseEvidenceAuthority = ReleaseEvidenceAuthority.ENGINEERING_ONLY
    classification: ReleaseEvidenceClassification = (
        ReleaseEvidenceClassification.ENGINEERING_SYNTHETIC
    )
    verification: ReleaseEvidenceVerification = ReleaseEvidenceVerification.UNVERIFIED
    execution_state: ReleaseEvidenceExecutionState = ReleaseEvidenceExecutionState.NOT_EXECUTED
    eligibility: ReleaseEvidenceEligibility = ReleaseEvidenceEligibility.NOT_ELIGIBLE
    review_state: ReleaseEvidenceReviewState = (
        ReleaseEvidenceReviewState.HUMAN_APPLICABILITY_AND_APPROVAL_REQUIRED
    )
    decision_state: ReleaseDecisionState = ReleaseDecisionState.NOT_RECORDED
    contract_version: str = SYNTHETIC_RELEASE_EVIDENCE_CONTRACT_VERSION
    _fingerprint: str = field(init=False, repr=False, compare=True)

    def __post_init__(self) -> None:
        _machine_string(self.manifest_id, _MANIFEST_ID)
        _machine_string(self.build_sha, _GIT_SHA)
        _machine_string(self.config_hash, _SHA256)
        _machine_string(self.proposed_scope_hash, _SHA256)
        generated_at = _utc(self.generated_at)
        if type(self.requirements) is not tuple:
            raise _error(ReleaseEvidenceContractCode.INVALID_TYPE)
        if len(self.requirements) != len(SyntheticReleaseEvidenceCategory):
            raise _error(ReleaseEvidenceContractCode.INCOMPLETE_INVENTORY)
        requirements = tuple(
            snapshot_release_evidence_requirement(item) for item in self.requirements
        )
        categories = tuple(item.category for item in requirements)
        if len(set(categories)) != len(categories):
            raise _error(ReleaseEvidenceContractCode.DUPLICATE_CATEGORY)
        if set(categories) != set(SyntheticReleaseEvidenceCategory):
            raise _error(ReleaseEvidenceContractCode.INCOMPLETE_INVENTORY)
        if categories != tuple(sorted(categories, key=lambda item: item.value)):
            raise _error(ReleaseEvidenceContractCode.INVALID_ORDER)
        if any(item.build_sha != self.build_sha for item in requirements):
            raise _error(ReleaseEvidenceContractCode.INVALID_VALUE)
        if any(item.created_at > generated_at for item in requirements):
            raise _error(ReleaseEvidenceContractCode.INVALID_CHRONOLOGY)
        _labels(
            self.authority,
            self.classification,
            self.verification,
            self.execution_state,
            self.eligibility,
            self.review_state,
            self.decision_state,
        )
        _contract_version(self.contract_version)
        fingerprint = _canonical_hash(
            {
                "authority": self.authority.value,
                "build_sha": self.build_sha,
                "classification": self.classification.value,
                "config_hash": self.config_hash,
                "contract_version": self.contract_version,
                "decision_state": self.decision_state.value,
                "eligibility": self.eligibility.value,
                "execution_state": self.execution_state.value,
                "generated_at": generated_at.isoformat(),
                "manifest_id": self.manifest_id,
                "proposed_scope_hash": self.proposed_scope_hash,
                "requirement_fingerprints": [item.fingerprint for item in requirements],
                "review_state": self.review_state.value,
                "verification": self.verification.value,
            }
        )
        object.__setattr__(self, "generated_at", generated_at)
        object.__setattr__(self, "requirements", requirements)
        object.__setattr__(self, "_fingerprint", fingerprint)

    @property
    def fingerprint(self) -> str:
        return self._fingerprint


def snapshot_release_evidence_manifest(value: object) -> SyntheticReleaseEvidenceManifest:
    if type(value) is not SyntheticReleaseEvidenceManifest:
        raise _error(ReleaseEvidenceContractCode.INVALID_TYPE)
    try:
        snapshot = SyntheticReleaseEvidenceManifest(
            manifest_id=value.manifest_id,
            build_sha=value.build_sha,
            config_hash=value.config_hash,
            proposed_scope_hash=value.proposed_scope_hash,
            generated_at=value.generated_at,
            requirements=value.requirements,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
            execution_state=value.execution_state,
            eligibility=value.eligibility,
            review_state=value.review_state,
            decision_state=value.decision_state,
            contract_version=value.contract_version,
        )
    except ReleaseEvidenceContractError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(ReleaseEvidenceContractCode.INVALID_TYPE) from None
    if snapshot.fingerprint != value.fingerprint:
        raise _error(ReleaseEvidenceContractCode.SNAPSHOT_DRIFT)
    return snapshot


def _check_environment(environment: object) -> None:
    if type(environment) is not Environment:
        raise _error(ReleaseEvidenceContractCode.INVALID_TYPE)
    if environment in _PROTECTED_ENVIRONMENTS:
        raise _error(ReleaseEvidenceContractCode.PROTECTED_ENVIRONMENT)


def build_synthetic_release_evidence_manifest(
    requirements: tuple[SyntheticReleaseEvidenceRequirement, ...],
    *,
    manifest_id: str,
    build_sha: str,
    config_hash: str,
    proposed_scope_hash: str,
    generated_at: datetime,
    environment: Environment,
) -> SyntheticReleaseEvidenceManifest:
    """Canonicalize required metadata without approving or starting a release."""

    _check_environment(environment)
    if type(requirements) is not tuple:
        raise _error(ReleaseEvidenceContractCode.INVALID_TYPE)
    if len(requirements) != len(SyntheticReleaseEvidenceCategory):
        raise _error(ReleaseEvidenceContractCode.INCOMPLETE_INVENTORY)
    safe_requirements = tuple(
        sorted(
            (snapshot_release_evidence_requirement(item) for item in requirements),
            key=lambda item: item.category.value,
        )
    )
    return SyntheticReleaseEvidenceManifest(
        manifest_id=manifest_id,
        build_sha=build_sha,
        config_hash=config_hash,
        proposed_scope_hash=proposed_scope_hash,
        generated_at=generated_at,
        requirements=safe_requirements,
    )


__all__ = [
    "SYNTHETIC_RELEASE_EVIDENCE_CONTRACT_VERSION",
    "ReleaseDecisionState",
    "ReleaseEvidenceAuthority",
    "ReleaseEvidenceClassification",
    "ReleaseEvidenceContractCode",
    "ReleaseEvidenceContractError",
    "ReleaseEvidenceEligibility",
    "ReleaseEvidenceExecutionState",
    "ReleaseEvidenceReviewState",
    "ReleaseEvidenceVerification",
    "SyntheticReleaseEvidenceCategory",
    "SyntheticReleaseEvidenceManifest",
    "SyntheticReleaseEvidenceRequirement",
    "build_synthetic_release_evidence_manifest",
    "snapshot_release_evidence_manifest",
    "snapshot_release_evidence_requirement",
]
