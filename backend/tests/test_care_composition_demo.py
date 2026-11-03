from __future__ import annotations

import json
import subprocess
import sys

import pytest

from app.config import Environment
from app.modules.care_orchestration import (
    CompositionDisposition,
    CompositionReason,
    EvidenceAvailability,
    EvidenceChannel,
)
from app.modules.care_orchestration.demo import (
    CareCompositionDemoCode,
    CareCompositionDemoError,
    build_synthetic_care_composition_demo,
)


def test_demo_replays_complete_structural_evidence_deterministically() -> None:
    first = build_synthetic_care_composition_demo(environment=Environment.TEST)
    second = build_synthetic_care_composition_demo(environment=Environment.TEST)

    assert first == second
    assert first.reconciliation.fingerprint == second.reconciliation.fingerprint
    assert first.replay.fingerprint == second.replay.fingerprint
    assert first.replay.decision.disposition is CompositionDisposition.PRESERVED
    assert first.replay.decision.reason is CompositionReason.ALL_CANDIDATES_PRESERVED
    assert tuple(candidate.channel for candidate in first.replay.decision.candidates) == (
        EvidenceChannel.SYNTHETIC_CHANNEL_ALPHA,
        EvidenceChannel.SYNTHETIC_CHANNEL_BETA,
    )
    assert first.source_call_count == 2


def test_demo_replays_unavailable_evidence_as_explicit_abstention() -> None:
    result = build_synthetic_care_composition_demo(
        environment=Environment.LOCAL,
        beta_availability=EvidenceAvailability.UNAVAILABLE,
    )

    assert result.replay.decision.disposition is CompositionDisposition.ABSTAINED
    assert result.replay.decision.reason is CompositionReason.EVIDENCE_NOT_AVAILABLE
    assert result.replay.decision.candidates == ()
    assert result.replay.decision.unavailable_channels == (EvidenceChannel.SYNTHETIC_CHANNEL_BETA,)
    assert result.source_call_count == 2


@pytest.mark.parametrize(
    "environment",
    [Environment.STAGING, Environment.PILOT, Environment.PRODUCTION],
)
def test_demo_rejects_protected_environments_before_fixture_validation(
    environment: Environment,
) -> None:
    with pytest.raises(CareCompositionDemoError) as captured:
        build_synthetic_care_composition_demo(
            environment=environment,
            beta_availability=object(),  # type: ignore[arg-type]
        )

    assert captured.value.code is CareCompositionDemoCode.PROTECTED_ENVIRONMENT


def test_demo_rejects_noncanonical_environment_and_availability() -> None:
    with pytest.raises(CareCompositionDemoError) as environment_error:
        build_synthetic_care_composition_demo(environment="test")  # type: ignore[arg-type]
    assert environment_error.value.code is CareCompositionDemoCode.INVALID_TYPE

    with pytest.raises(CareCompositionDemoError) as availability_error:
        build_synthetic_care_composition_demo(
            environment=Environment.TEST,
            beta_availability="UNAVAILABLE",  # type: ignore[arg-type]
        )
    assert availability_error.value.code is CareCompositionDemoCode.INVALID_TYPE


def _run_cli(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "app.modules.care_orchestration.demo", *arguments],
        check=False,
        capture_output=True,
        text=True,
    )


def test_cli_emits_canonical_content_free_replay_summary() -> None:
    first = _run_cli("--environment", "test")
    second = _run_cli("--environment", "test")

    assert first.returncode == 0
    assert first.stdout == second.stdout
    payload = json.loads(first.stdout)
    assert payload["authority"] == "ENGINEERING_ONLY"
    assert payload["classification"] == "ENGINEERING_SYNTHETIC"
    assert payload["verification"] == "UNVERIFIED"
    assert payload["environment"] == "test"
    assert payload["snapshot_state"] == "STRUCTURALLY_COMPLETE"
    assert payload["disposition"] == "PRESERVED"
    assert payload["reason"] == "ALL_CANDIDATES_PRESERVED"
    assert payload["candidate_count"] == 2
    assert payload["source_call_count"] == 2
    assert payload["unavailable_channels"] == []
    assert len(payload["request_fingerprint"]) == 64
    assert len(payload["reconciliation_fingerprint"]) == 64
    assert len(payload["replay_fingerprint"]) == 64
    assert "patient" not in first.stdout.lower()
    assert "clinical" not in first.stdout.lower()


def test_cli_exposes_degraded_abstention_without_candidate_output() -> None:
    completed = _run_cli(
        "--environment",
        "local",
        "--beta-availability",
        "UNAVAILABLE",
    )

    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    assert payload["snapshot_state"] == "STRUCTURALLY_COMPLETE_WITH_UNAVAILABLE"
    assert payload["disposition"] == "ABSTAINED"
    assert payload["reason"] == "EVIDENCE_NOT_AVAILABLE"
    assert payload["candidate_count"] == 0
    assert payload["unavailable_channels"] == ["SYNTHETIC_CHANNEL_BETA"]


def test_cli_rejects_protected_environment_without_output() -> None:
    completed = _run_cli("--environment", "production")

    assert completed.returncode != 0
    assert completed.stdout == ""
    assert "PROTECTED_ENVIRONMENT" in completed.stderr
