from __future__ import annotations

import json
import subprocess
import sys

import pytest

from app.config import Environment
from app.validation import (
    PerformancePlanExecutionState,
    RecoveryPlanExecutionState,
    ReleaseDecisionState,
    ReleaseEvidenceEligibility,
    ReleaseEvidenceExecutionState,
    ReleaseRehearsalDecisionState,
    ReleaseRehearsalEligibility,
    ReleaseRehearsalExecutionState,
    ReleaseSafetyDecisionState,
    ReleaseSafetyPlanEligibility,
    ReleaseSafetyPlanExecutionState,
)
from app.validation.demo import (
    ReadinessReplayCode,
    ReadinessReplayError,
    ReadinessReplayStatus,
    SecurityEvidenceState,
    build_synthetic_readiness_replay,
)


def test_replay_builds_complete_deterministic_planning_inventories() -> None:
    first = build_synthetic_readiness_replay(environment=Environment.TEST)
    second = build_synthetic_readiness_replay(environment=Environment.TEST)

    assert first == second
    assert len(first.performance.plans) == 5
    assert len(first.recovery.plans) == 5
    assert len(first.release_evidence.requirements) == 13
    assert len(first.release_safety.plans) == 6
    assert len(first.release_rehearsal.plans) == 8
    assert first.planning_item_count == 37
    assert first.status is ReadinessReplayStatus.BLOCKED_NOT_RELEASE_ELIGIBLE
    assert first.security_evidence is SecurityEvidenceState.TEST_SUITE_ONLY_NOT_RELEASE_EVIDENCE


def test_replay_preserves_unexecuted_unverified_and_no_decision_states() -> None:
    replay = build_synthetic_readiness_replay(environment=Environment.LOCAL)

    assert replay.performance.execution_state is PerformancePlanExecutionState.NOT_EXECUTED
    assert replay.recovery.execution_state is RecoveryPlanExecutionState.NOT_EXECUTED
    assert replay.release_evidence.execution_state is ReleaseEvidenceExecutionState.NOT_EXECUTED
    assert replay.release_evidence.eligibility is ReleaseEvidenceEligibility.NOT_ELIGIBLE
    assert replay.release_evidence.decision_state is ReleaseDecisionState.NOT_RECORDED
    assert replay.release_safety.execution_state is ReleaseSafetyPlanExecutionState.NOT_EXECUTED
    assert replay.release_safety.eligibility is ReleaseSafetyPlanEligibility.NOT_ELIGIBLE
    assert replay.release_safety.decision_state is ReleaseSafetyDecisionState.NOT_RECORDED
    assert replay.release_rehearsal.execution_state is ReleaseRehearsalExecutionState.NOT_EXECUTED
    assert replay.release_rehearsal.eligibility is ReleaseRehearsalEligibility.NOT_ELIGIBLE
    assert replay.release_rehearsal.decision_state is ReleaseRehearsalDecisionState.NOT_RECORDED


@pytest.mark.parametrize(
    "environment",
    [Environment.STAGING, Environment.PILOT, Environment.PRODUCTION],
)
def test_replay_rejects_protected_environment_before_build_identity_validation(
    environment: Environment,
) -> None:
    with pytest.raises(ReadinessReplayError) as captured:
        build_synthetic_readiness_replay(
            environment=environment,
            build_sha=object(),  # type: ignore[arg-type]
        )

    assert captured.value.code is ReadinessReplayCode.PROTECTED_ENVIRONMENT


def test_replay_rejects_noncanonical_environment_and_build_sha() -> None:
    with pytest.raises(ReadinessReplayError) as environment_error:
        build_synthetic_readiness_replay(environment="test")  # type: ignore[arg-type]
    assert environment_error.value.code is ReadinessReplayCode.INVALID_TYPE

    with pytest.raises(ReadinessReplayError) as build_error:
        build_synthetic_readiness_replay(
            environment=Environment.TEST,
            build_sha="not-a-sha",
        )
    assert build_error.value.code is ReadinessReplayCode.INVALID_VALUE


def _run_cli(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "app.validation.demo", *arguments],
        check=False,
        capture_output=True,
        text=True,
    )


def test_cli_emits_canonical_honest_readiness_summary() -> None:
    first = _run_cli("--environment", "test")
    second = _run_cli("--environment", "test")

    assert first.returncode == 0
    assert first.stdout == second.stdout
    payload = json.loads(first.stdout)
    assert payload["status"] == "BLOCKED_NOT_RELEASE_ELIGIBLE"
    assert payload["security_evidence"] == "TEST_SUITE_ONLY_NOT_RELEASE_EVIDENCE"
    assert payload["environment"] == "test"
    assert payload["verification"] == "UNVERIFIED"
    assert payload["execution_state"] == "NOT_EXECUTED"
    assert payload["eligibility"] == "NOT_ELIGIBLE"
    assert payload["decision_state"] == "NOT_RECORDED"
    assert payload["planning_item_count"] == 37
    assert payload["inventory_counts"] == {
        "performance": 5,
        "recovery": 5,
        "release_evidence": 13,
        "release_rehearsal": 8,
        "release_safety": 6,
    }
    assert len(payload["fingerprints"]) == 5
    assert all(len(value) == 64 for value in payload["fingerprints"].values())
    assert "patient" not in first.stdout.lower()
    assert "clinical_data" not in first.stdout.lower()


def test_cli_rejects_protected_environment_without_output() -> None:
    completed = _run_cli("--environment", "production")

    assert completed.returncode != 0
    assert completed.stdout == ""
    assert "PROTECTED_ENVIRONMENT" in completed.stderr
