"""Strict no-run contracts for synthetic P23 performance experiment planning."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256
from typing import Final

from app.config import Environment

SYNTHETIC_PERFORMANCE_PLAN_CONTRACT_VERSION: Final = "synthetic-performance-plan.v1"

_VERSION = re.compile(r"^engineering\.v[1-9][0-9]{0,5}$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_GIT_SHA = re.compile(r"^[a-f0-9]{40}$")
_MANIFEST_ID = re.compile(r"^syn_performance_manifest_(?:alpha|beta|gamma|delta)$")
_PROTECTED_ENVIRONMENTS = frozenset(
    {Environment.STAGING, Environment.PILOT, Environment.PRODUCTION}
)


class PerformancePlanContractCode(StrEnum):
    INVALID_TYPE = "INVALID_TYPE"
    INVALID_VALUE = "INVALID_VALUE"
    INVALID_CHRONOLOGY = "INVALID_CHRONOLOGY"
    INCOMPLETE_INVENTORY = "INCOMPLETE_INVENTORY"
    DUPLICATE_TARGET = "DUPLICATE_TARGET"
    INVALID_ORDER = "INVALID_ORDER"
    SNAPSHOT_DRIFT = "SNAPSHOT_DRIFT"
    PROTECTED_ENVIRONMENT = "PROTECTED_ENVIRONMENT"


class PerformancePlanContractError(ValueError):
    """Stable content-free performance-planning failure."""

    def __init__(self, code: PerformancePlanContractCode) -> None:
        self.code = code
        super().__init__(code.value)


class PerformancePlanAuthority(StrEnum):
    ENGINEERING_ONLY = "ENGINEERING_ONLY"


class PerformancePlanClassification(StrEnum):
    ENGINEERING_SYNTHETIC = "ENGINEERING_SYNTHETIC"


class PerformancePlanVerification(StrEnum):
    UNVERIFIED = "UNVERIFIED"


class PerformancePlanExecutionState(StrEnum):
    NOT_EXECUTED = "NOT_EXECUTED"


class PerformancePlanReviewState(StrEnum):
    HUMAN_APPROVAL_REQUIRED = "HUMAN_APPROVAL_REQUIRED"


class SyntheticPerformanceTarget(StrEnum):
    API_LATENCY = "API_LATENCY"
    LLM_LATENCY = "LLM_LATENCY"
    DOCUMENT_QUEUE = "DOCUMENT_QUEUE"
    PROVIDER_SEARCH = "PROVIDER_SEARCH"
    DATABASE_QUERY_HOTSPOTS = "DATABASE_QUERY_HOTSPOTS"


def _error(code: PerformancePlanContractCode) -> PerformancePlanContractError:
    return PerformancePlanContractError(code)


def _strict_enum(value: object, expected: type[StrEnum]) -> None:
    if type(value) is not expected:
        raise _error(PerformancePlanContractCode.INVALID_TYPE)


def _machine_string(value: object, pattern: re.Pattern[str]) -> str:
    if type(value) is not str:
        raise _error(PerformancePlanContractCode.INVALID_TYPE)
    if pattern.fullmatch(value) is None:
        raise _error(PerformancePlanContractCode.INVALID_VALUE)
    return value


def _utc(value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise _error(PerformancePlanContractCode.INVALID_TYPE)
    return value.astimezone(UTC)


def _contract_version(value: object) -> None:
    if type(value) is not str or value != SYNTHETIC_PERFORMANCE_PLAN_CONTRACT_VERSION:
        raise _error(PerformancePlanContractCode.INVALID_VALUE)


def _labels(
    authority: object,
    classification: object,
    verification: object,
    execution_state: object,
    review_state: object,
) -> None:
    if authority is not PerformancePlanAuthority.ENGINEERING_ONLY:
        raise _error(PerformancePlanContractCode.INVALID_VALUE)
    if classification is not PerformancePlanClassification.ENGINEERING_SYNTHETIC:
        raise _error(PerformancePlanContractCode.INVALID_VALUE)
    if verification is not PerformancePlanVerification.UNVERIFIED:
        raise _error(PerformancePlanContractCode.INVALID_VALUE)
    if execution_state is not PerformancePlanExecutionState.NOT_EXECUTED:
        raise _error(PerformancePlanContractCode.INVALID_VALUE)
    if review_state is not PerformancePlanReviewState.HUMAN_APPROVAL_REQUIRED:
        raise _error(PerformancePlanContractCode.INVALID_VALUE)


def _canonical_hash(payload: object) -> str:
    encoded = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticPerformancePlan:
    target: SyntheticPerformanceTarget
    plan_version: str
    build_sha: str = field(repr=False)
    config_hash: str = field(repr=False)
    workload_hash: str = field(repr=False)
    fixture_provenance_hash: str = field(repr=False)
    measurement_method_hash: str = field(repr=False)
    isolation_plan_hash: str = field(repr=False)
    analysis_plan_hash: str = field(repr=False)
    created_at: datetime
    authority: PerformancePlanAuthority = PerformancePlanAuthority.ENGINEERING_ONLY
    classification: PerformancePlanClassification = (
        PerformancePlanClassification.ENGINEERING_SYNTHETIC
    )
    verification: PerformancePlanVerification = PerformancePlanVerification.UNVERIFIED
    execution_state: PerformancePlanExecutionState = PerformancePlanExecutionState.NOT_EXECUTED
    review_state: PerformancePlanReviewState = PerformancePlanReviewState.HUMAN_APPROVAL_REQUIRED
    contract_version: str = SYNTHETIC_PERFORMANCE_PLAN_CONTRACT_VERSION
    _fingerprint: str = field(init=False, repr=False, compare=True)

    def __post_init__(self) -> None:
        _strict_enum(self.target, SyntheticPerformanceTarget)
        _machine_string(self.plan_version, _VERSION)
        _machine_string(self.build_sha, _GIT_SHA)
        _machine_string(self.config_hash, _SHA256)
        _machine_string(self.workload_hash, _SHA256)
        _machine_string(self.fixture_provenance_hash, _SHA256)
        _machine_string(self.measurement_method_hash, _SHA256)
        _machine_string(self.isolation_plan_hash, _SHA256)
        _machine_string(self.analysis_plan_hash, _SHA256)
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
                "analysis_plan_hash": self.analysis_plan_hash,
                "build_sha": self.build_sha,
                "config_hash": self.config_hash,
                "contract_version": self.contract_version,
                "created_at": created_at.isoformat(),
                "execution_state": self.execution_state.value,
                "fixture_provenance_hash": self.fixture_provenance_hash,
                "isolation_plan_hash": self.isolation_plan_hash,
                "measurement_method_hash": self.measurement_method_hash,
                "plan_version": self.plan_version,
                "review_state": self.review_state.value,
                "target": self.target.value,
                "workload_hash": self.workload_hash,
            }
        )
        object.__setattr__(self, "created_at", created_at)
        object.__setattr__(self, "_fingerprint", fingerprint)

    @property
    def fingerprint(self) -> str:
        return self._fingerprint


def snapshot_performance_plan(value: object) -> SyntheticPerformancePlan:
    if type(value) is not SyntheticPerformancePlan:
        raise _error(PerformancePlanContractCode.INVALID_TYPE)
    try:
        snapshot = SyntheticPerformancePlan(
            target=value.target,
            plan_version=value.plan_version,
            build_sha=value.build_sha,
            config_hash=value.config_hash,
            workload_hash=value.workload_hash,
            fixture_provenance_hash=value.fixture_provenance_hash,
            measurement_method_hash=value.measurement_method_hash,
            isolation_plan_hash=value.isolation_plan_hash,
            analysis_plan_hash=value.analysis_plan_hash,
            created_at=value.created_at,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
            execution_state=value.execution_state,
            review_state=value.review_state,
            contract_version=value.contract_version,
        )
    except PerformancePlanContractError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(PerformancePlanContractCode.INVALID_TYPE) from None
    if snapshot.fingerprint != value.fingerprint:
        raise _error(PerformancePlanContractCode.SNAPSHOT_DRIFT)
    return snapshot


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticPerformanceManifest:
    manifest_id: str
    generated_at: datetime
    plans: tuple[SyntheticPerformancePlan, ...] = field(repr=False)
    authority: PerformancePlanAuthority = PerformancePlanAuthority.ENGINEERING_ONLY
    classification: PerformancePlanClassification = (
        PerformancePlanClassification.ENGINEERING_SYNTHETIC
    )
    verification: PerformancePlanVerification = PerformancePlanVerification.UNVERIFIED
    execution_state: PerformancePlanExecutionState = PerformancePlanExecutionState.NOT_EXECUTED
    review_state: PerformancePlanReviewState = PerformancePlanReviewState.HUMAN_APPROVAL_REQUIRED
    contract_version: str = SYNTHETIC_PERFORMANCE_PLAN_CONTRACT_VERSION
    _fingerprint: str = field(init=False, repr=False, compare=True)

    def __post_init__(self) -> None:
        _machine_string(self.manifest_id, _MANIFEST_ID)
        generated_at = _utc(self.generated_at)
        if type(self.plans) is not tuple:
            raise _error(PerformancePlanContractCode.INVALID_TYPE)
        if len(self.plans) != len(SyntheticPerformanceTarget):
            raise _error(PerformancePlanContractCode.INCOMPLETE_INVENTORY)
        plans = tuple(snapshot_performance_plan(item) for item in self.plans)
        targets = tuple(item.target for item in plans)
        if len(set(targets)) != len(targets):
            raise _error(PerformancePlanContractCode.DUPLICATE_TARGET)
        if set(targets) != set(SyntheticPerformanceTarget):
            raise _error(PerformancePlanContractCode.INCOMPLETE_INVENTORY)
        if targets != tuple(sorted(targets, key=lambda item: item.value)):
            raise _error(PerformancePlanContractCode.INVALID_ORDER)
        if any(item.created_at > generated_at for item in plans):
            raise _error(PerformancePlanContractCode.INVALID_CHRONOLOGY)
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


def snapshot_performance_manifest(value: object) -> SyntheticPerformanceManifest:
    if type(value) is not SyntheticPerformanceManifest:
        raise _error(PerformancePlanContractCode.INVALID_TYPE)
    try:
        snapshot = SyntheticPerformanceManifest(
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
    except PerformancePlanContractError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(PerformancePlanContractCode.INVALID_TYPE) from None
    if snapshot.fingerprint != value.fingerprint:
        raise _error(PerformancePlanContractCode.SNAPSHOT_DRIFT)
    return snapshot


def _check_environment(environment: object) -> None:
    if type(environment) is not Environment:
        raise _error(PerformancePlanContractCode.INVALID_TYPE)
    if environment in _PROTECTED_ENVIRONMENTS:
        raise _error(PerformancePlanContractCode.PROTECTED_ENVIRONMENT)


def build_synthetic_performance_manifest(
    plans: tuple[SyntheticPerformancePlan, ...],
    *,
    manifest_id: str,
    generated_at: datetime,
    environment: Environment,
) -> SyntheticPerformanceManifest:
    """Canonicalize proposed metadata without executing a performance experiment."""

    _check_environment(environment)
    if type(plans) is not tuple:
        raise _error(PerformancePlanContractCode.INVALID_TYPE)
    if len(plans) != len(SyntheticPerformanceTarget):
        raise _error(PerformancePlanContractCode.INCOMPLETE_INVENTORY)
    safe_plans = tuple(
        sorted(
            (snapshot_performance_plan(item) for item in plans),
            key=lambda item: item.target.value,
        )
    )
    return SyntheticPerformanceManifest(
        manifest_id=manifest_id,
        generated_at=generated_at,
        plans=safe_plans,
    )


__all__ = [
    "SYNTHETIC_PERFORMANCE_PLAN_CONTRACT_VERSION",
    "PerformancePlanAuthority",
    "PerformancePlanClassification",
    "PerformancePlanContractCode",
    "PerformancePlanContractError",
    "PerformancePlanExecutionState",
    "PerformancePlanReviewState",
    "PerformancePlanVerification",
    "SyntheticPerformanceManifest",
    "SyntheticPerformancePlan",
    "SyntheticPerformanceTarget",
    "build_synthetic_performance_manifest",
    "snapshot_performance_manifest",
    "snapshot_performance_plan",
]
