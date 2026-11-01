"""Strict no-drill contracts for synthetic P24 operational rehearsal planning."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256
from typing import Final

from app.config import Environment

SYNTHETIC_RELEASE_REHEARSAL_PLAN_CONTRACT_VERSION: Final = "synthetic-release-rehearsal-plan.v1"

_VERSION = re.compile(r"^engineering\.v[1-9][0-9]{0,5}$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_GIT_SHA = re.compile(r"^[a-f0-9]{40}$")
_MANIFEST_ID = re.compile(r"^syn_release_rehearsal_(?:alpha|beta|gamma|delta)$")
_PROTECTED_ENVIRONMENTS = frozenset(
    {Environment.STAGING, Environment.PILOT, Environment.PRODUCTION}
)


class ReleaseRehearsalContractCode(StrEnum):
    INVALID_TYPE = "INVALID_TYPE"
    INVALID_VALUE = "INVALID_VALUE"
    INVALID_CHRONOLOGY = "INVALID_CHRONOLOGY"
    INCOMPLETE_INVENTORY = "INCOMPLETE_INVENTORY"
    DUPLICATE_SCENARIO = "DUPLICATE_SCENARIO"
    INVALID_ORDER = "INVALID_ORDER"
    SNAPSHOT_DRIFT = "SNAPSHOT_DRIFT"
    PROTECTED_ENVIRONMENT = "PROTECTED_ENVIRONMENT"


class ReleaseRehearsalContractError(ValueError):
    """Stable content-free release-rehearsal-planning failure."""

    def __init__(self, code: ReleaseRehearsalContractCode) -> None:
        self.code = code
        super().__init__(code.value)


class ReleaseRehearsalAuthority(StrEnum):
    ENGINEERING_ONLY = "ENGINEERING_ONLY"


class ReleaseRehearsalClassification(StrEnum):
    ENGINEERING_SYNTHETIC = "ENGINEERING_SYNTHETIC"


class ReleaseRehearsalVerification(StrEnum):
    UNVERIFIED = "UNVERIFIED"


class ReleaseRehearsalExecutionState(StrEnum):
    NOT_EXECUTED = "NOT_EXECUTED"


class ReleaseRehearsalEligibility(StrEnum):
    NOT_ELIGIBLE = "NOT_ELIGIBLE"


class ReleaseRehearsalReviewState(StrEnum):
    HUMAN_APPLICABILITY_AND_OPERATIONAL_APPROVAL_REQUIRED = (
        "HUMAN_APPLICABILITY_AND_OPERATIONAL_APPROVAL_REQUIRED"
    )


class ReleaseRehearsalDecisionState(StrEnum):
    NOT_RECORDED = "NOT_RECORDED"


class ReleaseRehearsalApplicability(StrEnum):
    UNDECIDED = "UNDECIDED"


class SyntheticReleaseRehearsalScenario(StrEnum):
    APPLICATION_ROLLBACK = "APPLICATION_ROLLBACK"
    POLICY_ROLLBACK = "POLICY_ROLLBACK"
    MODEL_ROLLBACK = "MODEL_ROLLBACK"
    RESOURCE_DISABLE = "RESOURCE_DISABLE"
    INCIDENT_ESCALATION = "INCIDENT_ESCALATION"
    BACKUP_RESTORE = "BACKUP_RESTORE"
    PURGE_FAILURE = "PURGE_FAILURE"
    PROVIDER_OUTAGE = "PROVIDER_OUTAGE"


def _error(code: ReleaseRehearsalContractCode) -> ReleaseRehearsalContractError:
    return ReleaseRehearsalContractError(code)


def _strict_enum(value: object, expected: type[StrEnum]) -> None:
    if type(value) is not expected:
        raise _error(ReleaseRehearsalContractCode.INVALID_TYPE)


def _machine_string(value: object, pattern: re.Pattern[str]) -> str:
    if type(value) is not str:
        raise _error(ReleaseRehearsalContractCode.INVALID_TYPE)
    if pattern.fullmatch(value) is None:
        raise _error(ReleaseRehearsalContractCode.INVALID_VALUE)
    return value


def _utc(value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None:
        raise _error(ReleaseRehearsalContractCode.INVALID_TYPE)
    try:
        if value.utcoffset() is None:
            raise _error(ReleaseRehearsalContractCode.INVALID_TYPE)
        return value.astimezone(UTC)
    except ReleaseRehearsalContractError:
        raise
    except Exception:
        raise _error(ReleaseRehearsalContractCode.INVALID_TYPE) from None


def _contract_version(value: object) -> None:
    if type(value) is not str or value != SYNTHETIC_RELEASE_REHEARSAL_PLAN_CONTRACT_VERSION:
        raise _error(ReleaseRehearsalContractCode.INVALID_VALUE)


def _labels(
    authority: object,
    classification: object,
    verification: object,
    execution_state: object,
    eligibility: object,
    review_state: object,
    decision_state: object,
) -> None:
    if authority is not ReleaseRehearsalAuthority.ENGINEERING_ONLY:
        raise _error(ReleaseRehearsalContractCode.INVALID_VALUE)
    if classification is not ReleaseRehearsalClassification.ENGINEERING_SYNTHETIC:
        raise _error(ReleaseRehearsalContractCode.INVALID_VALUE)
    if verification is not ReleaseRehearsalVerification.UNVERIFIED:
        raise _error(ReleaseRehearsalContractCode.INVALID_VALUE)
    if execution_state is not ReleaseRehearsalExecutionState.NOT_EXECUTED:
        raise _error(ReleaseRehearsalContractCode.INVALID_VALUE)
    if eligibility is not ReleaseRehearsalEligibility.NOT_ELIGIBLE:
        raise _error(ReleaseRehearsalContractCode.INVALID_VALUE)
    if review_state is not (
        ReleaseRehearsalReviewState.HUMAN_APPLICABILITY_AND_OPERATIONAL_APPROVAL_REQUIRED
    ):
        raise _error(ReleaseRehearsalContractCode.INVALID_VALUE)
    if decision_state is not ReleaseRehearsalDecisionState.NOT_RECORDED:
        raise _error(ReleaseRehearsalContractCode.INVALID_VALUE)


def _canonical_hash(payload: object) -> str:
    encoded = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticReleaseRehearsalPlan:
    scenario: SyntheticReleaseRehearsalScenario
    applicability: ReleaseRehearsalApplicability
    plan_version: str
    build_sha: str = field(repr=False)
    config_hash: str = field(repr=False)
    prerequisite_plan_hash: str = field(repr=False)
    failure_injection_plan_hash: str = field(repr=False)
    oracle_plan_hash: str = field(repr=False)
    isolation_cleanup_plan_hash: str = field(repr=False)
    privacy_canary_plan_hash: str = field(repr=False)
    rollback_or_safe_off_plan_hash: str = field(repr=False)
    evidence_plan_hash: str = field(repr=False)
    responsible_roles_hash: str = field(repr=False)
    created_at: datetime
    authority: ReleaseRehearsalAuthority = ReleaseRehearsalAuthority.ENGINEERING_ONLY
    classification: ReleaseRehearsalClassification = (
        ReleaseRehearsalClassification.ENGINEERING_SYNTHETIC
    )
    verification: ReleaseRehearsalVerification = ReleaseRehearsalVerification.UNVERIFIED
    execution_state: ReleaseRehearsalExecutionState = ReleaseRehearsalExecutionState.NOT_EXECUTED
    eligibility: ReleaseRehearsalEligibility = ReleaseRehearsalEligibility.NOT_ELIGIBLE
    review_state: ReleaseRehearsalReviewState = (
        ReleaseRehearsalReviewState.HUMAN_APPLICABILITY_AND_OPERATIONAL_APPROVAL_REQUIRED
    )
    decision_state: ReleaseRehearsalDecisionState = ReleaseRehearsalDecisionState.NOT_RECORDED
    contract_version: str = SYNTHETIC_RELEASE_REHEARSAL_PLAN_CONTRACT_VERSION
    _fingerprint: str = field(init=False, repr=False, compare=True)

    def __post_init__(self) -> None:
        _strict_enum(self.scenario, SyntheticReleaseRehearsalScenario)
        _strict_enum(self.applicability, ReleaseRehearsalApplicability)
        _machine_string(self.plan_version, _VERSION)
        _machine_string(self.build_sha, _GIT_SHA)
        _machine_string(self.config_hash, _SHA256)
        _machine_string(self.prerequisite_plan_hash, _SHA256)
        _machine_string(self.failure_injection_plan_hash, _SHA256)
        _machine_string(self.oracle_plan_hash, _SHA256)
        _machine_string(self.isolation_cleanup_plan_hash, _SHA256)
        _machine_string(self.privacy_canary_plan_hash, _SHA256)
        _machine_string(self.rollback_or_safe_off_plan_hash, _SHA256)
        _machine_string(self.evidence_plan_hash, _SHA256)
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
                "applicability": self.applicability.value,
                "authority": self.authority.value,
                "build_sha": self.build_sha,
                "classification": self.classification.value,
                "config_hash": self.config_hash,
                "contract_version": self.contract_version,
                "created_at": created_at.isoformat(),
                "decision_state": self.decision_state.value,
                "eligibility": self.eligibility.value,
                "evidence_plan_hash": self.evidence_plan_hash,
                "execution_state": self.execution_state.value,
                "failure_injection_plan_hash": self.failure_injection_plan_hash,
                "isolation_cleanup_plan_hash": self.isolation_cleanup_plan_hash,
                "oracle_plan_hash": self.oracle_plan_hash,
                "plan_version": self.plan_version,
                "prerequisite_plan_hash": self.prerequisite_plan_hash,
                "privacy_canary_plan_hash": self.privacy_canary_plan_hash,
                "responsible_roles_hash": self.responsible_roles_hash,
                "review_state": self.review_state.value,
                "rollback_or_safe_off_plan_hash": self.rollback_or_safe_off_plan_hash,
                "scenario": self.scenario.value,
                "verification": self.verification.value,
            }
        )
        object.__setattr__(self, "created_at", created_at)
        object.__setattr__(self, "_fingerprint", fingerprint)

    @property
    def fingerprint(self) -> str:
        return self._fingerprint


def snapshot_release_rehearsal_plan(value: object) -> SyntheticReleaseRehearsalPlan:
    if type(value) is not SyntheticReleaseRehearsalPlan:
        raise _error(ReleaseRehearsalContractCode.INVALID_TYPE)
    try:
        snapshot = SyntheticReleaseRehearsalPlan(
            scenario=value.scenario,
            applicability=value.applicability,
            plan_version=value.plan_version,
            build_sha=value.build_sha,
            config_hash=value.config_hash,
            prerequisite_plan_hash=value.prerequisite_plan_hash,
            failure_injection_plan_hash=value.failure_injection_plan_hash,
            oracle_plan_hash=value.oracle_plan_hash,
            isolation_cleanup_plan_hash=value.isolation_cleanup_plan_hash,
            privacy_canary_plan_hash=value.privacy_canary_plan_hash,
            rollback_or_safe_off_plan_hash=value.rollback_or_safe_off_plan_hash,
            evidence_plan_hash=value.evidence_plan_hash,
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
    except ReleaseRehearsalContractError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(ReleaseRehearsalContractCode.INVALID_TYPE) from None
    if snapshot.fingerprint != value.fingerprint:
        raise _error(ReleaseRehearsalContractCode.SNAPSHOT_DRIFT)
    return snapshot


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticReleaseRehearsalManifest:
    manifest_id: str
    build_sha: str = field(repr=False)
    config_hash: str = field(repr=False)
    proposed_scope_hash: str = field(repr=False)
    generated_at: datetime
    plans: tuple[SyntheticReleaseRehearsalPlan, ...] = field(repr=False)
    authority: ReleaseRehearsalAuthority = ReleaseRehearsalAuthority.ENGINEERING_ONLY
    classification: ReleaseRehearsalClassification = (
        ReleaseRehearsalClassification.ENGINEERING_SYNTHETIC
    )
    verification: ReleaseRehearsalVerification = ReleaseRehearsalVerification.UNVERIFIED
    execution_state: ReleaseRehearsalExecutionState = ReleaseRehearsalExecutionState.NOT_EXECUTED
    eligibility: ReleaseRehearsalEligibility = ReleaseRehearsalEligibility.NOT_ELIGIBLE
    review_state: ReleaseRehearsalReviewState = (
        ReleaseRehearsalReviewState.HUMAN_APPLICABILITY_AND_OPERATIONAL_APPROVAL_REQUIRED
    )
    decision_state: ReleaseRehearsalDecisionState = ReleaseRehearsalDecisionState.NOT_RECORDED
    contract_version: str = SYNTHETIC_RELEASE_REHEARSAL_PLAN_CONTRACT_VERSION
    _fingerprint: str = field(init=False, repr=False, compare=True)

    def __post_init__(self) -> None:
        _machine_string(self.manifest_id, _MANIFEST_ID)
        _machine_string(self.build_sha, _GIT_SHA)
        _machine_string(self.config_hash, _SHA256)
        _machine_string(self.proposed_scope_hash, _SHA256)
        generated_at = _utc(self.generated_at)
        if type(self.plans) is not tuple:
            raise _error(ReleaseRehearsalContractCode.INVALID_TYPE)
        if len(self.plans) != len(SyntheticReleaseRehearsalScenario):
            raise _error(ReleaseRehearsalContractCode.INCOMPLETE_INVENTORY)
        plans = tuple(snapshot_release_rehearsal_plan(item) for item in self.plans)
        scenarios = tuple(item.scenario for item in plans)
        if len(set(scenarios)) != len(scenarios):
            raise _error(ReleaseRehearsalContractCode.DUPLICATE_SCENARIO)
        if set(scenarios) != set(SyntheticReleaseRehearsalScenario):
            raise _error(ReleaseRehearsalContractCode.INCOMPLETE_INVENTORY)
        if scenarios != tuple(sorted(scenarios, key=lambda item: item.value)):
            raise _error(ReleaseRehearsalContractCode.INVALID_ORDER)
        if any(item.build_sha != self.build_sha for item in plans):
            raise _error(ReleaseRehearsalContractCode.INVALID_VALUE)
        if any(item.config_hash != self.config_hash for item in plans):
            raise _error(ReleaseRehearsalContractCode.INVALID_VALUE)
        if any(item.created_at > generated_at for item in plans):
            raise _error(ReleaseRehearsalContractCode.INVALID_CHRONOLOGY)
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


def snapshot_release_rehearsal_manifest(value: object) -> SyntheticReleaseRehearsalManifest:
    if type(value) is not SyntheticReleaseRehearsalManifest:
        raise _error(ReleaseRehearsalContractCode.INVALID_TYPE)
    try:
        snapshot = SyntheticReleaseRehearsalManifest(
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
    except ReleaseRehearsalContractError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(ReleaseRehearsalContractCode.INVALID_TYPE) from None
    if snapshot.fingerprint != value.fingerprint:
        raise _error(ReleaseRehearsalContractCode.SNAPSHOT_DRIFT)
    return snapshot


def _check_environment(environment: object) -> None:
    if type(environment) is not Environment:
        raise _error(ReleaseRehearsalContractCode.INVALID_TYPE)
    if environment in _PROTECTED_ENVIRONMENTS:
        raise _error(ReleaseRehearsalContractCode.PROTECTED_ENVIRONMENT)


def build_synthetic_release_rehearsal_manifest(
    plans: tuple[SyntheticReleaseRehearsalPlan, ...],
    *,
    manifest_id: str,
    build_sha: str,
    config_hash: str,
    proposed_scope_hash: str,
    generated_at: datetime,
    environment: Environment,
) -> SyntheticReleaseRehearsalManifest:
    """Canonicalize proposed metadata without executing an operational rehearsal."""

    _check_environment(environment)
    if type(plans) is not tuple:
        raise _error(ReleaseRehearsalContractCode.INVALID_TYPE)
    if len(plans) != len(SyntheticReleaseRehearsalScenario):
        raise _error(ReleaseRehearsalContractCode.INCOMPLETE_INVENTORY)
    safe_plans = tuple(
        sorted(
            (snapshot_release_rehearsal_plan(item) for item in plans),
            key=lambda item: item.scenario.value,
        )
    )
    return SyntheticReleaseRehearsalManifest(
        manifest_id=manifest_id,
        build_sha=build_sha,
        config_hash=config_hash,
        proposed_scope_hash=proposed_scope_hash,
        generated_at=generated_at,
        plans=safe_plans,
    )


__all__ = [
    "SYNTHETIC_RELEASE_REHEARSAL_PLAN_CONTRACT_VERSION",
    "ReleaseRehearsalApplicability",
    "ReleaseRehearsalAuthority",
    "ReleaseRehearsalClassification",
    "ReleaseRehearsalContractCode",
    "ReleaseRehearsalContractError",
    "ReleaseRehearsalDecisionState",
    "ReleaseRehearsalEligibility",
    "ReleaseRehearsalExecutionState",
    "ReleaseRehearsalReviewState",
    "ReleaseRehearsalVerification",
    "SyntheticReleaseRehearsalManifest",
    "SyntheticReleaseRehearsalPlan",
    "SyntheticReleaseRehearsalScenario",
    "build_synthetic_release_rehearsal_manifest",
    "snapshot_release_rehearsal_manifest",
    "snapshot_release_rehearsal_plan",
]
