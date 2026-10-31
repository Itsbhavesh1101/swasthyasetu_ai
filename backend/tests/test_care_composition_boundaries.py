from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from app.config import Environment, Settings
from app.main import create_app
from app.modules.care_orchestration import (
    CompositionCode,
    CompositionContractError,
    EvidenceAvailability,
    EvidenceChannel,
    SyntheticActionCandidate,
    SyntheticActionCode,
    SyntheticCompositionRequest,
    SyntheticEvidenceReference,
    SyntheticReasonCode,
    compose_synthetic_candidates,
)

NOW = datetime(2026, 11, 1, 18, 0, tzinfo=UTC)
HASH_A = "a" * 64
HASH_C = "c" * 64


def request() -> SyntheticCompositionRequest:
    return SyntheticCompositionRequest(
        request_id="syn_comp_request_alpha",
        snapshot_id="syn_comp_snapshot_alpha",
        snapshot_version="engineering.v1",
        snapshot_hash=HASH_C,
        evidence=(
            SyntheticEvidenceReference(
                evidence_id="syn_comp_evidence_alpha",
                channel=EvidenceChannel.SYNTHETIC_CHANNEL_ALPHA,
                evidence_version="engineering.v1",
                artifact_hash=HASH_A,
                availability=EvidenceAvailability.PRESENT_UNVERIFIED,
                effective_at=NOW - timedelta(minutes=2),
                observed_at=NOW - timedelta(minutes=1),
            ),
        ),
        created_at=NOW,
    )


def candidate(suffix: str) -> SyntheticActionCandidate:
    return SyntheticActionCandidate(
        candidate_id=f"syn_comp_candidate_{suffix}",
        action=SyntheticActionCode.SYNTHETIC_ACTION_ALPHA,
        channel=EvidenceChannel.SYNTHETIC_CHANNEL_ALPHA,
        evidence_id="syn_comp_evidence_alpha",
        evidence_version="engineering.v1",
        evidence_hash=HASH_A,
        reason_code=SyntheticReasonCode.SYNTHETIC_REASON_ALPHA,
    )


def test_semantically_duplicate_candidates_cannot_alias_under_distinct_ids() -> None:
    with pytest.raises(CompositionContractError) as captured:
        compose_synthetic_candidates(
            request(),
            (candidate("alpha"), candidate("beta")),
            evaluated_at=NOW,
            environment=Environment.TEST,
        )

    assert captured.value.code is CompositionCode.DUPLICATE_CANDIDATE


def test_foundation_is_not_registered_or_exposed_as_an_api() -> None:
    application = create_app(Settings(_env_file=None))
    module_ids = set(application.state.module_registry.module_ids)
    route_paths = {
        path
        for route in application.routes
        if isinstance(path := getattr(route, "path", None), str)
    }

    assert "care_orchestration" not in module_ids
    assert "orchestration" not in module_ids
    assert all("orchestration" not in path and "care-action" not in path for path in route_paths)


def test_decision_has_no_execution_approval_or_activation_surface() -> None:
    decision = compose_synthetic_candidates(
        request(),
        (candidate("alpha"),),
        evaluated_at=NOW,
        environment=Environment.TEST,
    )

    for prohibited in (
        "activate",
        "approve",
        "authorize",
        "execute",
        "persist",
        "publish",
        "rank",
        "select",
        "suppress",
    ):
        assert not hasattr(decision, prohibited)
