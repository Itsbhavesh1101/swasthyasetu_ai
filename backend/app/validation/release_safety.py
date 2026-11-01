"""Strict no-evaluation contracts for synthetic P24 safety planning."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256
from typing import Final

from app.config import Environment

SYNTHETIC_RELEASE_SAFETY_PLAN_CONTRACT_VERSION: Final = "synthetic-release-safety-plan.v1"

_VERSION = re.compile(r"^engineering\.v[1-9][0-9]{0,5}$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_GIT_SHA = re.compile(r"^[a-f0-9]{40}$")
_MANIFEST_ID = re.compile(r"^syn_release_safety_(?:alpha|beta|gamma|delta)$")
_PROTECTED_ENVIRONMENTS = frozenset(
    {Environment.STAGING, Environment.PILOT, Environment.PRODUCTION}
)


class ReleaseSafetyPlanContractCode(StrEnum):
    INVALID_TYPE = "INVALID_TYPE"
    INVALID_VALUE = "INVALID_VALUE"
    INVALID_CHRONOLOGY = "INVALID_CHRONOLOGY"
    INCOMPLETE_INVENTORY = "INCOMPLETE_INVENTORY"
    DUPLICATE_AREA = "DUPLICATE_AREA"
    INVALID_ORDER = "INVALID_ORDER"
    SNAPSHOT_DRIFT = "SNAPSHOT_DRIFT"
    PROTECTED_ENVIRONMENT = "PROTECTED_ENVIRONMENT"


class ReleaseSafetyPlanContractError(ValueError):
    """Stable content-free release-safety-planning failure."""

    def __init__(self, code: ReleaseSafetyPlanContractCode) -> None:
        self.code = code
        super().__init__(code.value)


class ReleaseSafetyPlanAuthority(StrEnum):
    ENGINEERING_ONLY = "ENGINEERING_ONLY"


class ReleaseSafetyPlanClassification(StrEnum):
    ENGINEERING_SYNTHETIC = "ENGINEERING_SYNTHETIC"


class ReleaseSafetyPlanVerification(StrEnum):
    UNVERIFIED = "UNVERIFIED"


class ReleaseSafetyPlanExecutionState(StrEnum):
    NOT_EXECUTED = "NOT_EXECUTED"


class ReleaseSafetyPlanEligibility(StrEnum):
    NOT_ELIGIBLE = "NOT_ELIGIBLE"


class ReleaseSafetyPlanReviewState(StrEnum):
    HUMAN_METRIC_AND_APPROVAL_REQUIRED = "HUMAN_METRIC_AND_APPROVAL_REQUIRED"


class ReleaseSafetyDecisionState(StrEnum):
    NOT_RECORDED = "NOT_RECORDED"


class SyntheticReleaseSafetyArea(StrEnum):
    CLINICIAN_AUTHORED_SAFETY_SET = "CLINICIAN_AUTHORED_SAFETY_SET"
    MULTILINGUAL_SAFETY_SET = "MULTILINGUAL_SAFETY_SET"
    ROUTE_CONCORDANCE = "ROUTE_CONCORDANCE"
    CRITICAL_FALSE_NEGATIVES = "CRITICAL_FALSE_NEGATIVES"
    RESOURCE_CORRECTNESS = "RESOURCE_CORRECTNESS"
    CLARIFICATION_UTILITY = "CLARIFICATION_UTILITY"


def _error(code: ReleaseSafetyPlanContractCode) -> ReleaseSafetyPlanContractError:
    return ReleaseSafetyPlanContractError(code)


def _strict_enum(value: object, expected: type[StrEnum]) -> None:
    if type(value) is not expected:
        raise _error(ReleaseSafetyPlanContractCode.INVALID_TYPE)


def _machine_string(value: object, pattern: re.Pattern[str]) -> str:
    if type(value) is not str:
        raise _error(ReleaseSafetyPlanContractCode.INVALID_TYPE)
    if pattern.fullmatch(value) is None:
        raise _error(ReleaseSafetyPlanContractCode.INVALID_VALUE)
    return value


def _utc(value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None:
        raise _error(ReleaseSafetyPlanContractCode.INVALID_TYPE)
    try:
        if value.utcoffset() is None:
            raise _error(ReleaseSafetyPlanContractCode.INVALID_TYPE)
        return value.astimezone(UTC)
    except ReleaseSafetyPlanContractError:
        raise
    except Exception:
        raise _error(ReleaseSafetyPlanContractCode.INVALID_TYPE) from None


def _contract_version(value: object) -> None:
    if type(value) is not str or value != SYNTHETIC_RELEASE_SAFETY_PLAN_CONTRACT_VERSION:
        raise _error(ReleaseSafetyPlanContractCode.INVALID_VALUE)


def _labels(
    authority: object,
    classification: object,
    verification: object,
    execution_state: object,
    eligibility: object,
    review_state: object,
    decision_state: object,
) -> None:
    if authority is not ReleaseSafetyPlanAuthority.ENGINEERING_ONLY:
        raise _error(ReleaseSafetyPlanContractCode.INVALID_VALUE)
    if classification is not ReleaseSafetyPlanClassification.ENGINEERING_SYNTHETIC:
        raise _error(ReleaseSafetyPlanContractCode.INVALID_VALUE)
    if verification is not ReleaseSafetyPlanVerification.UNVERIFIED:
        raise _error(ReleaseSafetyPlanContractCode.INVALID_VALUE)
    if execution_state is not ReleaseSafetyPlanExecutionState.NOT_EXECUTED:
        raise _error(ReleaseSafetyPlanContractCode.INVALID_VALUE)
    if eligibility is not ReleaseSafetyPlanEligibility.NOT_ELIGIBLE:
        raise _error(ReleaseSafetyPlanContractCode.INVALID_VALUE)
    if review_state is not ReleaseSafetyPlanReviewState.HUMAN_METRIC_AND_APPROVAL_REQUIRED:
        raise _error(ReleaseSafetyPlanContractCode.INVALID_VALUE)
    if decision_state is not ReleaseSafetyDecisionState.NOT_RECORDED:
        raise _error(ReleaseSafetyPlanContractCode.INVALID_VALUE)


def _canonical_hash(payload: object) -> str:
    encoded = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticReleaseSafetyPlan:
    area: SyntheticReleaseSafetyArea
    plan_version: str
    build_sha: str = field(repr=False)
    synthetic_fixture_plan_hash: str = field(repr=False)
    oracle_plan_hash: str = field(repr=False)
    metric_plan_hash: str = field(repr=False)
    analysis_plan_hash: str = field(repr=False)
    privacy_plan_hash: str = field(repr=False)
    negative_test_plan_hash: str = field(repr=False)
    responsible_roles_hash: str = field(repr=False)
    created_at: datetime
    authority: ReleaseSafetyPlanAuthority = ReleaseSafetyPlanAuthority.ENGINEERING_ONLY
    classification: ReleaseSafetyPlanClassification = (
        ReleaseSafetyPlanClassification.ENGINEERING_SYNTHETIC
    )
    verification: ReleaseSafetyPlanVerification = ReleaseSafetyPlanVerification.UNVERIFIED
    execution_state: ReleaseSafetyPlanExecutionState = ReleaseSafetyPlanExecutionState.NOT_EXECUTED
    eligibility: ReleaseSafetyPlanEligibility = ReleaseSafetyPlanEligibility.NOT_ELIGIBLE
    review_state: ReleaseSafetyPlanReviewState = (
        ReleaseSafetyPlanReviewState.HUMAN_METRIC_AND_APPROVAL_REQUIRED
    )
    decision_state: ReleaseSafetyDecisionState = ReleaseSafetyDecisionState.NOT_RECORDED
    contract_version: str = SYNTHETIC_RELEASE_SAFETY_PLAN_CONTRACT_VERSION
    _fingerprint: str = field(init=False, repr=False, compare=True)

    def __post_init__(self) -> None:
        _strict_enum(self.area, SyntheticReleaseSafetyArea)
        _machine_string(self.plan_version, _VERSION)
        _machine_string(self.build_sha, _GIT_SHA)
        _machine_string(self.synthetic_fixture_plan_hash, _SHA256)
        _machine_string(self.oracle_plan_hash, _SHA256)
        _machine_string(self.metric_plan_hash, _SHA256)
        _machine_string(self.analysis_plan_hash, _SHA256)
        _machine_string(self.privacy_plan_hash, _SHA256)
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
                "analysis_plan_hash": self.analysis_plan_hash,
                "area": self.area.value,
                "authority": self.authority.value,
                "build_sha": self.build_sha,
                "classification": self.classification.value,
                "contract_version": self.contract_version,
                "created_at": created_at.isoformat(),
                "decision_state": self.decision_state.value,
                "eligibility": self.eligibility.value,
                "execution_state": self.execution_state.value,
                "metric_plan_hash": self.metric_plan_hash,
                "negative_test_plan_hash": self.negative_test_plan_hash,
                "oracle_plan_hash": self.oracle_plan_hash,
                "plan_version": self.plan_version,
                "privacy_plan_hash": self.privacy_plan_hash,
                "responsible_roles_hash": self.responsible_roles_hash,
                "review_state": self.review_state.value,
                "synthetic_fixture_plan_hash": self.synthetic_fixture_plan_hash,
                "verification": self.verification.value,
            }
        )
        object.__setattr__(self, "created_at", created_at)
        object.__setattr__(self, "_fingerprint", fingerprint)

    @property
    def fingerprint(self) -> str:
        return self._fingerprint


def snapshot_release_safety_plan(value: object) -> SyntheticReleaseSafetyPlan:
    if type(value) is not SyntheticReleaseSafetyPlan:
        raise _error(ReleaseSafetyPlanContractCode.INVALID_TYPE)
    try:
        snapshot = SyntheticReleaseSafetyPlan(
            area=value.area,
            plan_version=value.plan_version,
            build_sha=value.build_sha,
            synthetic_fixture_plan_hash=value.synthetic_fixture_plan_hash,
            oracle_plan_hash=value.oracle_plan_hash,
            metric_plan_hash=value.metric_plan_hash,
            analysis_plan_hash=value.analysis_plan_hash,
            privacy_plan_hash=value.privacy_plan_hash,
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
    except ReleaseSafetyPlanContractError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(ReleaseSafetyPlanContractCode.INVALID_TYPE) from None
    if snapshot.fingerprint != value.fingerprint:
        raise _error(ReleaseSafetyPlanContractCode.SNAPSHOT_DRIFT)
    return snapshot


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticReleaseSafetyManifest:
    manifest_id: str
    build_sha: str = field(repr=False)
    config_hash: str = field(repr=False)
    proposed_scope_hash: str = field(repr=False)
    generated_at: datetime
    plans: tuple[SyntheticReleaseSafetyPlan, ...] = field(repr=False)
    authority: ReleaseSafetyPlanAuthority = ReleaseSafetyPlanAuthority.ENGINEERING_ONLY
    classification: ReleaseSafetyPlanClassification = (
        ReleaseSafetyPlanClassification.ENGINEERING_SYNTHETIC
    )
    verification: ReleaseSafetyPlanVerification = ReleaseSafetyPlanVerification.UNVERIFIED
    execution_state: ReleaseSafetyPlanExecutionState = ReleaseSafetyPlanExecutionState.NOT_EXECUTED
    eligibility: ReleaseSafetyPlanEligibility = ReleaseSafetyPlanEligibility.NOT_ELIGIBLE
    review_state: ReleaseSafetyPlanReviewState = (
        ReleaseSafetyPlanReviewState.HUMAN_METRIC_AND_APPROVAL_REQUIRED
    )
    decision_state: ReleaseSafetyDecisionState = ReleaseSafetyDecisionState.NOT_RECORDED
    contract_version: str = SYNTHETIC_RELEASE_SAFETY_PLAN_CONTRACT_VERSION
    _fingerprint: str = field(init=False, repr=False, compare=True)

    def __post_init__(self) -> None:
        _machine_string(self.manifest_id, _MANIFEST_ID)
        _machine_string(self.build_sha, _GIT_SHA)
        _machine_string(self.config_hash, _SHA256)
        _machine_string(self.proposed_scope_hash, _SHA256)
        generated_at = _utc(self.generated_at)
        if type(self.plans) is not tuple:
            raise _error(ReleaseSafetyPlanContractCode.INVALID_TYPE)
        if len(self.plans) != len(SyntheticReleaseSafetyArea):
            raise _error(ReleaseSafetyPlanContractCode.INCOMPLETE_INVENTORY)
        plans = tuple(snapshot_release_safety_plan(item) for item in self.plans)
        areas = tuple(item.area for item in plans)
        if len(set(areas)) != len(areas):
            raise _error(ReleaseSafetyPlanContractCode.DUPLICATE_AREA)
        if set(areas) != set(SyntheticReleaseSafetyArea):
            raise _error(ReleaseSafetyPlanContractCode.INCOMPLETE_INVENTORY)
        if areas != tuple(sorted(areas, key=lambda item: item.value)):
            raise _error(ReleaseSafetyPlanContractCode.INVALID_ORDER)
        if any(item.build_sha != self.build_sha for item in plans):
            raise _error(ReleaseSafetyPlanContractCode.INVALID_VALUE)
        if any(item.created_at > generated_at for item in plans):
            raise _error(ReleaseSafetyPlanContractCode.INVALID_CHRONOLOGY)
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
                "plan_fingerprints": [item.fingerprint for item in plans],
                "proposed_scope_hash": self.proposed_scope_hash,
                "review_state": self.review_state.value,
                "verification": self.verification.value,
            }
        )
        object.__setattr__(self, "generated_at", generated_at)
        object.__setattr__(self, "plans", plans)
        object.__setattr__(self, "_fingerprint", fingerprint)

    @property
    def fingerprint(self) -> str:
        return self._fingerprint


def snapshot_release_safety_manifest(value: object) -> SyntheticReleaseSafetyManifest:
    if type(value) is not SyntheticReleaseSafetyManifest:
        raise _error(ReleaseSafetyPlanContractCode.INVALID_TYPE)
    try:
        snapshot = SyntheticReleaseSafetyManifest(
            manifest_id=value.manifest_id,
            build_sha=value.build_sha,
            config_hash=value.config_hash,
            proposed_scope_hash=value.proposed_scope_hash,
            generated_at=value.generated_at,
            plans=value.plans,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
            execution_state=value.execution_state,
            eligibility=value.eligibility,
            review_state=value.review_state,
            decision_state=value.decision_state,
            contract_version=value.contract_version,
        )
    except ReleaseSafetyPlanContractError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(ReleaseSafetyPlanContractCode.INVALID_TYPE) from None
    if snapshot.fingerprint != value.fingerprint:
        raise _error(ReleaseSafetyPlanContractCode.SNAPSHOT_DRIFT)
    return snapshot


def _check_environment(environment: object) -> None:
    if type(environment) is not Environment:
        raise _error(ReleaseSafetyPlanContractCode.INVALID_TYPE)
    if environment in _PROTECTED_ENVIRONMENTS:
        raise _error(ReleaseSafetyPlanContractCode.PROTECTED_ENVIRONMENT)


def build_synthetic_release_safety_manifest(
    plans: tuple[SyntheticReleaseSafetyPlan, ...],
    *,
    manifest_id: str,
    build_sha: str,
    config_hash: str,
    proposed_scope_hash: str,
    generated_at: datetime,
    environment: Environment,
) -> SyntheticReleaseSafetyManifest:
    """Canonicalize proposed metadata without running a safety evaluation."""

    _check_environment(environment)
    if type(plans) is not tuple:
        raise _error(ReleaseSafetyPlanContractCode.INVALID_TYPE)
    if len(plans) != len(SyntheticReleaseSafetyArea):
        raise _error(ReleaseSafetyPlanContractCode.INCOMPLETE_INVENTORY)
    safe_plans = tuple(
        sorted(
            (snapshot_release_safety_plan(item) for item in plans),
            key=lambda item: item.area.value,
        )
    )
    return SyntheticReleaseSafetyManifest(
        manifest_id=manifest_id,
        build_sha=build_sha,
        config_hash=config_hash,
        proposed_scope_hash=proposed_scope_hash,
        generated_at=generated_at,
        plans=safe_plans,
    )


__all__ = [
    "SYNTHETIC_RELEASE_SAFETY_PLAN_CONTRACT_VERSION",
    "ReleaseSafetyDecisionState",
    "ReleaseSafetyPlanAuthority",
    "ReleaseSafetyPlanClassification",
    "ReleaseSafetyPlanContractCode",
    "ReleaseSafetyPlanContractError",
    "ReleaseSafetyPlanEligibility",
    "ReleaseSafetyPlanExecutionState",
    "ReleaseSafetyPlanReviewState",
    "ReleaseSafetyPlanVerification",
    "SyntheticReleaseSafetyArea",
    "SyntheticReleaseSafetyManifest",
    "SyntheticReleaseSafetyPlan",
    "build_synthetic_release_safety_manifest",
    "snapshot_release_safety_manifest",
    "snapshot_release_safety_plan",
]
