"""Offline synthetic planning replay for P22-P24 readiness boundaries."""

from __future__ import annotations

import argparse
import json
import re
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum

from app.config import Environment
from app.validation.performance import (
    SyntheticPerformanceManifest,
    SyntheticPerformancePlan,
    SyntheticPerformanceTarget,
    build_synthetic_performance_manifest,
)
from app.validation.recovery import (
    RecoveryPlanApplicability,
    SyntheticRecoveryManifest,
    SyntheticRecoveryPlan,
    SyntheticRecoveryScenario,
    build_synthetic_recovery_manifest,
)
from app.validation.release_readiness import (
    SyntheticReleaseEvidenceCategory,
    SyntheticReleaseEvidenceManifest,
    SyntheticReleaseEvidenceRequirement,
    build_synthetic_release_evidence_manifest,
)
from app.validation.release_rehearsal import (
    ReleaseRehearsalApplicability,
    SyntheticReleaseRehearsalManifest,
    SyntheticReleaseRehearsalPlan,
    SyntheticReleaseRehearsalScenario,
    build_synthetic_release_rehearsal_manifest,
)
from app.validation.release_safety import (
    SyntheticReleaseSafetyArea,
    SyntheticReleaseSafetyManifest,
    SyntheticReleaseSafetyPlan,
    build_synthetic_release_safety_manifest,
)

_NOW = datetime(2026, 11, 3, 8, 0, tzinfo=UTC)
_DEFAULT_BUILD_SHA = "f" * 40
_HASH_A = "a" * 64
_HASH_B = "b" * 64
_HASH_C = "c" * 64
_HASH_D = "d" * 64
_HASH_E = "e" * 64
_HASH_F = "f" * 64
_BUILD_SHA = re.compile(r"^[a-f0-9]{40}$")
_PROTECTED_ENVIRONMENTS = frozenset(
    {Environment.STAGING, Environment.PILOT, Environment.PRODUCTION}
)


class ReadinessReplayCode(StrEnum):
    INVALID_TYPE = "INVALID_TYPE"
    INVALID_VALUE = "INVALID_VALUE"
    PROTECTED_ENVIRONMENT = "PROTECTED_ENVIRONMENT"


class ReadinessReplayError(ValueError):
    """Stable content-free failure from the readiness replay boundary."""

    def __init__(self, code: ReadinessReplayCode) -> None:
        self.code = code
        super().__init__(code.value)


class ReadinessReplayStatus(StrEnum):
    BLOCKED_NOT_RELEASE_ELIGIBLE = "BLOCKED_NOT_RELEASE_ELIGIBLE"


class SecurityEvidenceState(StrEnum):
    TEST_SUITE_ONLY_NOT_RELEASE_EVIDENCE = "TEST_SUITE_ONLY_NOT_RELEASE_EVIDENCE"


@dataclass(frozen=True, slots=True)
class SyntheticReadinessReplay:
    performance: SyntheticPerformanceManifest
    recovery: SyntheticRecoveryManifest
    release_evidence: SyntheticReleaseEvidenceManifest
    release_safety: SyntheticReleaseSafetyManifest
    release_rehearsal: SyntheticReleaseRehearsalManifest
    status: ReadinessReplayStatus = ReadinessReplayStatus.BLOCKED_NOT_RELEASE_ELIGIBLE
    security_evidence: SecurityEvidenceState = (
        SecurityEvidenceState.TEST_SUITE_ONLY_NOT_RELEASE_EVIDENCE
    )

    @property
    def planning_item_count(self) -> int:
        return (
            len(self.performance.plans)
            + len(self.recovery.plans)
            + len(self.release_evidence.requirements)
            + len(self.release_safety.plans)
            + len(self.release_rehearsal.plans)
        )


def _performance_plans(build_sha: str) -> tuple[SyntheticPerformancePlan, ...]:
    return tuple(
        SyntheticPerformancePlan(
            target=target,
            plan_version="engineering.v1",
            build_sha=build_sha,
            config_hash=_HASH_A,
            workload_hash=_HASH_B,
            fixture_provenance_hash=_HASH_C,
            measurement_method_hash=_HASH_D,
            isolation_plan_hash=_HASH_E,
            analysis_plan_hash=_HASH_A,
            created_at=_NOW,
        )
        for target in SyntheticPerformanceTarget
    )


def _recovery_plans(build_sha: str) -> tuple[SyntheticRecoveryPlan, ...]:
    return tuple(
        SyntheticRecoveryPlan(
            scenario=scenario,
            applicability=(
                RecoveryPlanApplicability.UNDECIDED
                if scenario is SyntheticRecoveryScenario.PROJECTION_REBUILD_IF_APPLICABLE
                else RecoveryPlanApplicability.PROPOSED_UNAPPROVED
            ),
            plan_version="engineering.v1",
            build_sha=build_sha,
            config_hash=_HASH_A,
            failure_injection_plan_hash=_HASH_B,
            recovery_oracle_hash=_HASH_C,
            isolation_cleanup_hash=_HASH_D,
            privacy_canary_hash=_HASH_E,
            rollback_plan_hash=_HASH_A,
            created_at=_NOW,
        )
        for scenario in SyntheticRecoveryScenario
    )


def _release_requirements(build_sha: str) -> tuple[SyntheticReleaseEvidenceRequirement, ...]:
    return tuple(
        SyntheticReleaseEvidenceRequirement(
            category=category,
            requirement_version="engineering.v1",
            build_sha=build_sha,
            requirement_hash=_HASH_A,
            acceptance_criteria_hash=_HASH_B,
            negative_test_plan_hash=_HASH_C,
            responsible_roles_hash=_HASH_D,
            created_at=_NOW,
        )
        for category in SyntheticReleaseEvidenceCategory
    )


def _release_safety_plans(build_sha: str) -> tuple[SyntheticReleaseSafetyPlan, ...]:
    return tuple(
        SyntheticReleaseSafetyPlan(
            area=area,
            plan_version="engineering.v1",
            build_sha=build_sha,
            synthetic_fixture_plan_hash=_HASH_A,
            oracle_plan_hash=_HASH_B,
            metric_plan_hash=_HASH_C,
            analysis_plan_hash=_HASH_D,
            privacy_plan_hash=_HASH_A,
            negative_test_plan_hash=_HASH_B,
            responsible_roles_hash=_HASH_C,
            created_at=_NOW,
        )
        for area in SyntheticReleaseSafetyArea
    )


def _release_rehearsal_plans(build_sha: str) -> tuple[SyntheticReleaseRehearsalPlan, ...]:
    return tuple(
        SyntheticReleaseRehearsalPlan(
            scenario=scenario,
            applicability=ReleaseRehearsalApplicability.UNDECIDED,
            plan_version="engineering.v1",
            build_sha=build_sha,
            config_hash=_HASH_A,
            prerequisite_plan_hash=_HASH_B,
            failure_injection_plan_hash=_HASH_C,
            oracle_plan_hash=_HASH_D,
            isolation_cleanup_plan_hash=_HASH_E,
            privacy_canary_plan_hash=_HASH_F,
            rollback_or_safe_off_plan_hash=_HASH_A,
            evidence_plan_hash=_HASH_B,
            responsible_roles_hash=_HASH_C,
            created_at=_NOW,
        )
        for scenario in SyntheticReleaseRehearsalScenario
    )


def build_synthetic_readiness_replay(
    *,
    environment: Environment,
    build_sha: str = _DEFAULT_BUILD_SHA,
) -> SyntheticReadinessReplay:
    """Build complete planning inventories without running or authorizing a release."""

    if type(environment) is not Environment:
        raise ReadinessReplayError(ReadinessReplayCode.INVALID_TYPE)
    if environment in _PROTECTED_ENVIRONMENTS:
        raise ReadinessReplayError(ReadinessReplayCode.PROTECTED_ENVIRONMENT)
    if type(build_sha) is not str:
        raise ReadinessReplayError(ReadinessReplayCode.INVALID_TYPE)
    if _BUILD_SHA.fullmatch(build_sha) is None:
        raise ReadinessReplayError(ReadinessReplayCode.INVALID_VALUE)

    generated_at = _NOW + timedelta(minutes=1)
    performance = build_synthetic_performance_manifest(
        _performance_plans(build_sha),
        manifest_id="syn_performance_manifest_alpha",
        generated_at=generated_at,
        environment=environment,
    )
    recovery = build_synthetic_recovery_manifest(
        _recovery_plans(build_sha),
        manifest_id="syn_recovery_manifest_alpha",
        generated_at=generated_at,
        environment=environment,
    )
    release_evidence = build_synthetic_release_evidence_manifest(
        _release_requirements(build_sha),
        manifest_id="syn_release_evidence_alpha",
        build_sha=build_sha,
        config_hash=_HASH_A,
        proposed_scope_hash=_HASH_B,
        generated_at=generated_at,
        environment=environment,
    )
    release_safety = build_synthetic_release_safety_manifest(
        _release_safety_plans(build_sha),
        manifest_id="syn_release_safety_alpha",
        build_sha=build_sha,
        config_hash=_HASH_A,
        proposed_scope_hash=_HASH_B,
        generated_at=generated_at,
        environment=environment,
    )
    release_rehearsal = build_synthetic_release_rehearsal_manifest(
        _release_rehearsal_plans(build_sha),
        manifest_id="syn_release_rehearsal_alpha",
        build_sha=build_sha,
        config_hash=_HASH_A,
        proposed_scope_hash=_HASH_D,
        generated_at=generated_at,
        environment=environment,
    )
    return SyntheticReadinessReplay(
        performance=performance,
        recovery=recovery,
        release_evidence=release_evidence,
        release_safety=release_safety,
        release_rehearsal=release_rehearsal,
    )


def _summary(
    replay: SyntheticReadinessReplay,
    *,
    environment: Environment,
) -> dict[str, object]:
    return {
        "decision_state": replay.release_evidence.decision_state.value,
        "eligibility": replay.release_evidence.eligibility.value,
        "environment": environment.value,
        "execution_state": replay.release_evidence.execution_state.value,
        "fingerprints": {
            "performance": replay.performance.fingerprint,
            "recovery": replay.recovery.fingerprint,
            "release_evidence": replay.release_evidence.fingerprint,
            "release_rehearsal": replay.release_rehearsal.fingerprint,
            "release_safety": replay.release_safety.fingerprint,
        },
        "inventory_counts": {
            "performance": len(replay.performance.plans),
            "recovery": len(replay.recovery.plans),
            "release_evidence": len(replay.release_evidence.requirements),
            "release_rehearsal": len(replay.release_rehearsal.plans),
            "release_safety": len(replay.release_safety.plans),
        },
        "planning_item_count": replay.planning_item_count,
        "security_evidence": replay.security_evidence.value,
        "status": replay.status.value,
        "verification": replay.release_evidence.verification.value,
    }


def main(arguments: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build the offline engineering-synthetic readiness planning replay."
    )
    parser.add_argument(
        "--environment",
        choices=[environment.value for environment in Environment],
        default=Environment.LOCAL.value,
    )
    parser.add_argument("--build-sha", default=_DEFAULT_BUILD_SHA)
    parsed = parser.parse_args(arguments)
    environment = Environment(parsed.environment)
    try:
        replay = build_synthetic_readiness_replay(
            environment=environment,
            build_sha=parsed.build_sha,
        )
    except ReadinessReplayError as error:
        parser.exit(2, f"{error.code.value}\n")
    print(json.dumps(_summary(replay, environment=environment), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "ReadinessReplayCode",
    "ReadinessReplayError",
    "ReadinessReplayStatus",
    "SecurityEvidenceState",
    "SyntheticReadinessReplay",
    "build_synthetic_readiness_replay",
    "main",
]
