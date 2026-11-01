"""Strict no-drill contracts for synthetic P23 recovery planning."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256
from typing import Final

from app.config import Environment

SYNTHETIC_RECOVERY_PLAN_CONTRACT_VERSION: Final = "synthetic-recovery-plan.v1"

_VERSION = re.compile(r"^engineering\.v[1-9][0-9]{0,5}$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_GIT_SHA = re.compile(r"^[a-f0-9]{40}$")
_MANIFEST_ID = re.compile(r"^syn_recovery_manifest_(?:alpha|beta|gamma|delta)$")
_PROTECTED_ENVIRONMENTS = frozenset(
    {Environment.STAGING, Environment.PILOT, Environment.PRODUCTION}
)


class RecoveryPlanContractCode(StrEnum):
    INVALID_TYPE = "INVALID_TYPE"
    INVALID_VALUE = "INVALID_VALUE"
    INVALID_APPLICABILITY = "INVALID_APPLICABILITY"
    INVALID_CHRONOLOGY = "INVALID_CHRONOLOGY"
    INCOMPLETE_INVENTORY = "INCOMPLETE_INVENTORY"
    DUPLICATE_SCENARIO = "DUPLICATE_SCENARIO"
    INVALID_ORDER = "INVALID_ORDER"
    SNAPSHOT_DRIFT = "SNAPSHOT_DRIFT"
    PROTECTED_ENVIRONMENT = "PROTECTED_ENVIRONMENT"


class RecoveryPlanContractError(ValueError):
    """Stable content-free recovery-planning failure."""

    def __init__(self, code: RecoveryPlanContractCode) -> None:
        self.code = code
        super().__init__(code.value)


class RecoveryPlanAuthority(StrEnum):
    ENGINEERING_ONLY = "ENGINEERING_ONLY"


class RecoveryPlanClassification(StrEnum):
    ENGINEERING_SYNTHETIC = "ENGINEERING_SYNTHETIC"


class RecoveryPlanVerification(StrEnum):
    UNVERIFIED = "UNVERIFIED"


class RecoveryPlanExecutionState(StrEnum):
    NOT_EXECUTED = "NOT_EXECUTED"


class RecoveryPlanReviewState(StrEnum):
    HUMAN_APPROVAL_REQUIRED = "HUMAN_APPROVAL_REQUIRED"


class RecoveryPlanApplicability(StrEnum):
    PROPOSED_UNAPPROVED = "PROPOSED_UNAPPROVED"
    UNDECIDED = "UNDECIDED"


class SyntheticRecoveryScenario(StrEnum):
    WORKER_RESTART = "WORKER_RESTART"
    DUPLICATE_EVENT = "DUPLICATE_EVENT"
    RETRY = "RETRY"
    OUTBOX_RECOVERY = "OUTBOX_RECOVERY"
    PROJECTION_REBUILD_IF_APPLICABLE = "PROJECTION_REBUILD_IF_APPLICABLE"


def _error(code: RecoveryPlanContractCode) -> RecoveryPlanContractError:
    return RecoveryPlanContractError(code)


def _strict_enum(value: object, expected: type[StrEnum]) -> None:
    if type(value) is not expected:
        raise _error(RecoveryPlanContractCode.INVALID_TYPE)


def _machine_string(value: object, pattern: re.Pattern[str]) -> str:
    if type(value) is not str:
        raise _error(RecoveryPlanContractCode.INVALID_TYPE)
    if pattern.fullmatch(value) is None:
        raise _error(RecoveryPlanContractCode.INVALID_VALUE)
    return value


def _utc(value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise _error(RecoveryPlanContractCode.INVALID_TYPE)
    return value.astimezone(UTC)


def _contract_version(value: object) -> None:
    if type(value) is not str or value != SYNTHETIC_RECOVERY_PLAN_CONTRACT_VERSION:
        raise _error(RecoveryPlanContractCode.INVALID_VALUE)


def _labels(
    authority: object,
    classification: object,
    verification: object,
    execution_state: object,
    review_state: object,
) -> None:
    if authority is not RecoveryPlanAuthority.ENGINEERING_ONLY:
        raise _error(RecoveryPlanContractCode.INVALID_VALUE)
    if classification is not RecoveryPlanClassification.ENGINEERING_SYNTHETIC:
        raise _error(RecoveryPlanContractCode.INVALID_VALUE)
    if verification is not RecoveryPlanVerification.UNVERIFIED:
        raise _error(RecoveryPlanContractCode.INVALID_VALUE)
    if execution_state is not RecoveryPlanExecutionState.NOT_EXECUTED:
        raise _error(RecoveryPlanContractCode.INVALID_VALUE)
    if review_state is not RecoveryPlanReviewState.HUMAN_APPROVAL_REQUIRED:
        raise _error(RecoveryPlanContractCode.INVALID_VALUE)


def _canonical_hash(payload: object) -> str:
    encoded = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return sha256(encoded).hexdigest()


def _expected_applicability(scenario: SyntheticRecoveryScenario) -> RecoveryPlanApplicability:
    if scenario is SyntheticRecoveryScenario.PROJECTION_REBUILD_IF_APPLICABLE:
        return RecoveryPlanApplicability.UNDECIDED
    return RecoveryPlanApplicability.PROPOSED_UNAPPROVED


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticRecoveryPlan:
    scenario: SyntheticRecoveryScenario
    applicability: RecoveryPlanApplicability
    plan_version: str
    build_sha: str = field(repr=False)
    config_hash: str = field(repr=False)
    failure_injection_plan_hash: str = field(repr=False)
    recovery_oracle_hash: str = field(repr=False)
    isolation_cleanup_hash: str = field(repr=False)
    privacy_canary_hash: str = field(repr=False)
    rollback_plan_hash: str = field(repr=False)
    created_at: datetime
    authority: RecoveryPlanAuthority = RecoveryPlanAuthority.ENGINEERING_ONLY
    classification: RecoveryPlanClassification = RecoveryPlanClassification.ENGINEERING_SYNTHETIC
    verification: RecoveryPlanVerification = RecoveryPlanVerification.UNVERIFIED
    execution_state: RecoveryPlanExecutionState = RecoveryPlanExecutionState.NOT_EXECUTED
    review_state: RecoveryPlanReviewState = RecoveryPlanReviewState.HUMAN_APPROVAL_REQUIRED
    contract_version: str = SYNTHETIC_RECOVERY_PLAN_CONTRACT_VERSION
    _fingerprint: str = field(init=False, repr=False, compare=True)

    def __post_init__(self) -> None:
        _strict_enum(self.scenario, SyntheticRecoveryScenario)
        _strict_enum(self.applicability, RecoveryPlanApplicability)
        if self.applicability is not _expected_applicability(self.scenario):
            raise _error(RecoveryPlanContractCode.INVALID_APPLICABILITY)
        _machine_string(self.plan_version, _VERSION)
        _machine_string(self.build_sha, _GIT_SHA)
        _machine_string(self.config_hash, _SHA256)
        _machine_string(self.failure_injection_plan_hash, _SHA256)
        _machine_string(self.recovery_oracle_hash, _SHA256)
        _machine_string(self.isolation_cleanup_hash, _SHA256)
        _machine_string(self.privacy_canary_hash, _SHA256)
        _machine_string(self.rollback_plan_hash, _SHA256)
        created_at = _utc(self.created_at)
        _labels(
            self.authority,
            self.classification,
            self.verification,
            self.execution_state,
            self.review_state,
        )
        _contract_version(self.contract_version)
        fingerprint = _canonical_hash(
            {
                "applicability": self.applicability.value,
                "build_sha": self.build_sha,
                "config_hash": self.config_hash,
                "contract_version": self.contract_version,
                "created_at": created_at.isoformat(),
                "execution_state": self.execution_state.value,
                "failure_injection_plan_hash": self.failure_injection_plan_hash,
                "isolation_cleanup_hash": self.isolation_cleanup_hash,
                "plan_version": self.plan_version,
                "privacy_canary_hash": self.privacy_canary_hash,
                "recovery_oracle_hash": self.recovery_oracle_hash,
                "review_state": self.review_state.value,
                "rollback_plan_hash": self.rollback_plan_hash,
                "scenario": self.scenario.value,
            }
        )
        object.__setattr__(self, "created_at", created_at)
        object.__setattr__(self, "_fingerprint", fingerprint)

    @property
    def fingerprint(self) -> str:
        return self._fingerprint


def snapshot_recovery_plan(value: object) -> SyntheticRecoveryPlan:
    if type(value) is not SyntheticRecoveryPlan:
        raise _error(RecoveryPlanContractCode.INVALID_TYPE)
    try:
        snapshot = SyntheticRecoveryPlan(
            scenario=value.scenario,
            applicability=value.applicability,
            plan_version=value.plan_version,
            build_sha=value.build_sha,
            config_hash=value.config_hash,
            failure_injection_plan_hash=value.failure_injection_plan_hash,
            recovery_oracle_hash=value.recovery_oracle_hash,
            isolation_cleanup_hash=value.isolation_cleanup_hash,
            privacy_canary_hash=value.privacy_canary_hash,
            rollback_plan_hash=value.rollback_plan_hash,
            created_at=value.created_at,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
            execution_state=value.execution_state,
            review_state=value.review_state,
            contract_version=value.contract_version,
        )
    except RecoveryPlanContractError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(RecoveryPlanContractCode.INVALID_TYPE) from None
    if snapshot.fingerprint != value.fingerprint:
        raise _error(RecoveryPlanContractCode.SNAPSHOT_DRIFT)
    return snapshot


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticRecoveryManifest:
    manifest_id: str
    generated_at: datetime
    plans: tuple[SyntheticRecoveryPlan, ...] = field(repr=False)
    authority: RecoveryPlanAuthority = RecoveryPlanAuthority.ENGINEERING_ONLY
    classification: RecoveryPlanClassification = RecoveryPlanClassification.ENGINEERING_SYNTHETIC
    verification: RecoveryPlanVerification = RecoveryPlanVerification.UNVERIFIED
    execution_state: RecoveryPlanExecutionState = RecoveryPlanExecutionState.NOT_EXECUTED
    review_state: RecoveryPlanReviewState = RecoveryPlanReviewState.HUMAN_APPROVAL_REQUIRED
    contract_version: str = SYNTHETIC_RECOVERY_PLAN_CONTRACT_VERSION
    _fingerprint: str = field(init=False, repr=False, compare=True)

    def __post_init__(self) -> None:
        _machine_string(self.manifest_id, _MANIFEST_ID)
        generated_at = _utc(self.generated_at)
        if type(self.plans) is not tuple:
            raise _error(RecoveryPlanContractCode.INVALID_TYPE)
        if len(self.plans) != len(SyntheticRecoveryScenario):
            raise _error(RecoveryPlanContractCode.INCOMPLETE_INVENTORY)
        plans = tuple(snapshot_recovery_plan(item) for item in self.plans)
        scenarios = tuple(item.scenario for item in plans)
        if len(set(scenarios)) != len(scenarios):
            raise _error(RecoveryPlanContractCode.DUPLICATE_SCENARIO)
        if set(scenarios) != set(SyntheticRecoveryScenario):
            raise _error(RecoveryPlanContractCode.INCOMPLETE_INVENTORY)
        if scenarios != tuple(sorted(scenarios, key=lambda item: item.value)):
            raise _error(RecoveryPlanContractCode.INVALID_ORDER)
        if any(item.created_at > generated_at for item in plans):
            raise _error(RecoveryPlanContractCode.INVALID_CHRONOLOGY)
        _labels(
            self.authority,
            self.classification,
            self.verification,
            self.execution_state,
            self.review_state,
        )
        _contract_version(self.contract_version)
        fingerprint = _canonical_hash(
            {
                "contract_version": self.contract_version,
                "execution_state": self.execution_state.value,
                "generated_at": generated_at.isoformat(),
                "manifest_id": self.manifest_id,
                "plan_fingerprints": [item.fingerprint for item in plans],
                "review_state": self.review_state.value,
            }
        )
        object.__setattr__(self, "generated_at", generated_at)
        object.__setattr__(self, "plans", plans)
        object.__setattr__(self, "_fingerprint", fingerprint)

    @property
    def fingerprint(self) -> str:
        return self._fingerprint


def snapshot_recovery_manifest(value: object) -> SyntheticRecoveryManifest:
    if type(value) is not SyntheticRecoveryManifest:
        raise _error(RecoveryPlanContractCode.INVALID_TYPE)
    try:
        snapshot = SyntheticRecoveryManifest(
            manifest_id=value.manifest_id,
            generated_at=value.generated_at,
            plans=value.plans,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
            execution_state=value.execution_state,
            review_state=value.review_state,
            contract_version=value.contract_version,
        )
    except RecoveryPlanContractError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(RecoveryPlanContractCode.INVALID_TYPE) from None
    if snapshot.fingerprint != value.fingerprint:
        raise _error(RecoveryPlanContractCode.SNAPSHOT_DRIFT)
    return snapshot


def _check_environment(environment: object) -> None:
    if type(environment) is not Environment:
        raise _error(RecoveryPlanContractCode.INVALID_TYPE)
    if environment in _PROTECTED_ENVIRONMENTS:
        raise _error(RecoveryPlanContractCode.PROTECTED_ENVIRONMENT)


def build_synthetic_recovery_manifest(
    plans: tuple[SyntheticRecoveryPlan, ...],
    *,
    manifest_id: str,
    generated_at: datetime,
    environment: Environment,
) -> SyntheticRecoveryManifest:
    """Canonicalize proposed metadata without executing a recovery drill."""

    _check_environment(environment)
    if type(plans) is not tuple:
        raise _error(RecoveryPlanContractCode.INVALID_TYPE)
    if len(plans) != len(SyntheticRecoveryScenario):
        raise _error(RecoveryPlanContractCode.INCOMPLETE_INVENTORY)
    safe_plans = tuple(
        sorted(
            (snapshot_recovery_plan(item) for item in plans),
            key=lambda item: item.scenario.value,
        )
    )
    return SyntheticRecoveryManifest(
        manifest_id=manifest_id,
        generated_at=generated_at,
        plans=safe_plans,
    )


__all__ = [
    "SYNTHETIC_RECOVERY_PLAN_CONTRACT_VERSION",
    "RecoveryPlanApplicability",
    "RecoveryPlanAuthority",
    "RecoveryPlanClassification",
    "RecoveryPlanContractCode",
    "RecoveryPlanContractError",
    "RecoveryPlanExecutionState",
    "RecoveryPlanReviewState",
    "RecoveryPlanVerification",
    "SyntheticRecoveryManifest",
    "SyntheticRecoveryPlan",
    "SyntheticRecoveryScenario",
    "build_synthetic_recovery_manifest",
    "snapshot_recovery_manifest",
    "snapshot_recovery_plan",
]
