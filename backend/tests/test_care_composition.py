from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any, cast

import pytest

from app.config import Environment
from app.modules.care_orchestration import (
    CompositionCode,
    CompositionContractError,
    CompositionDisposition,
    CompositionReason,
    EvidenceAvailability,
    EvidenceChannel,
    SyntheticActionCandidate,
    SyntheticActionCode,
    SyntheticCompositionRequest,
    SyntheticEvidenceReference,
    SyntheticReasonCode,
    compose_synthetic_candidates,
)

NOW = datetime(2026, 11, 1, 15, 0, tzinfo=UTC)
HASH_A = "a" * 64
HASH_B = "b" * 64
HASH_C = "c" * 64


def evidence(
    suffix: str = "alpha",
    *,
    channel: EvidenceChannel = EvidenceChannel.SYNTHETIC_CHANNEL_ALPHA,
    availability: EvidenceAvailability = EvidenceAvailability.PRESENT_UNVERIFIED,
    artifact_hash: str = HASH_A,
) -> SyntheticEvidenceReference:
    return SyntheticEvidenceReference(
        evidence_id=f"syn_comp_evidence_{suffix}",
        channel=channel,
        evidence_version="engineering.v1",
        artifact_hash=artifact_hash,
        availability=availability,
        effective_at=NOW - timedelta(minutes=2),
        observed_at=NOW - timedelta(minutes=1),
    )


def request(*items: SyntheticEvidenceReference) -> SyntheticCompositionRequest:
    return SyntheticCompositionRequest(
        request_id="syn_comp_request_alpha",
        snapshot_id="syn_comp_snapshot_alpha",
        snapshot_version="engineering.v1",
        snapshot_hash=HASH_C,
        evidence=items or (evidence(),),
        created_at=NOW,
    )


def candidate(
    suffix: str = "alpha",
    *,
    action: SyntheticActionCode = SyntheticActionCode.SYNTHETIC_ACTION_ALPHA,
    channel: EvidenceChannel = EvidenceChannel.SYNTHETIC_CHANNEL_ALPHA,
    evidence_id: str = "syn_comp_evidence_alpha",
    evidence_version: str = "engineering.v1",
    evidence_hash: str = HASH_A,
    reason: SyntheticReasonCode = SyntheticReasonCode.SYNTHETIC_REASON_ALPHA,
) -> SyntheticActionCandidate:
    return SyntheticActionCandidate(
        candidate_id=f"syn_comp_candidate_{suffix}",
        action=action,
        channel=channel,
        evidence_id=evidence_id,
        evidence_version=evidence_version,
        evidence_hash=evidence_hash,
        reason_code=reason,
    )


@pytest.mark.parametrize(
    "environment",
    [Environment.STAGING, Environment.PILOT, Environment.PRODUCTION],
)
def test_protected_environment_denies_before_inspecting_inputs(
    environment: Environment,
) -> None:
    class ExplodingInput:
        def __getattribute__(self, name: str) -> Any:
            raise AssertionError(f"input inspected: {name}")

    with pytest.raises(CompositionContractError) as captured:
        compose_synthetic_candidates(
            cast(SyntheticCompositionRequest, ExplodingInput()),
            cast(tuple[SyntheticActionCandidate, ...], ExplodingInput()),
            evaluated_at=cast(datetime, ExplodingInput()),
            environment=environment,
        )

    assert captured.value.code is CompositionCode.PROTECTED_ENVIRONMENT


def test_unavailable_evidence_abstains_before_candidate_inspection() -> None:
    unavailable = request(
        evidence(
            availability=EvidenceAvailability.UNAVAILABLE,
        )
    )

    class ExplodingCandidate:
        def __getattribute__(self, name: str) -> Any:
            raise AssertionError(f"candidate inspected: {name}")

    decision = compose_synthetic_candidates(
        unavailable,
        (cast(SyntheticActionCandidate, ExplodingCandidate()),),
        evaluated_at=NOW,
        environment=Environment.TEST,
    )

    assert decision.disposition is CompositionDisposition.ABSTAINED
    assert decision.reason is CompositionReason.EVIDENCE_NOT_AVAILABLE
    assert decision.candidates == ()
    assert decision.unavailable_channels == (EvidenceChannel.SYNTHETIC_CHANNEL_ALPHA,)


def test_empty_candidates_abstain_without_inventing_an_action() -> None:
    composition_request = request()

    decision = compose_synthetic_candidates(
        composition_request,
        (),
        evaluated_at=NOW,
        environment=Environment.LOCAL,
    )

    assert decision.disposition is CompositionDisposition.ABSTAINED
    assert decision.reason is CompositionReason.NO_CANDIDATES
    assert decision.candidates == ()
    assert decision.request_fingerprint == composition_request.fingerprint


def test_available_evidence_preserves_every_candidate_in_canonical_order() -> None:
    alpha = evidence()
    beta = evidence(
        "beta",
        channel=EvidenceChannel.SYNTHETIC_CHANNEL_BETA,
        artifact_hash=HASH_B,
    )
    composition_request = request(beta, alpha)
    alpha_candidate = candidate()
    beta_candidate = candidate(
        "beta",
        action=SyntheticActionCode.SYNTHETIC_ACTION_BETA,
        channel=EvidenceChannel.SYNTHETIC_CHANNEL_BETA,
        evidence_id="syn_comp_evidence_beta",
        evidence_hash=HASH_B,
        reason=SyntheticReasonCode.SYNTHETIC_REASON_BETA,
    )

    first = compose_synthetic_candidates(
        composition_request,
        (beta_candidate, alpha_candidate),
        evaluated_at=NOW,
        environment=Environment.TEST,
    )
    second = compose_synthetic_candidates(
        request(alpha, beta),
        (alpha_candidate, beta_candidate),
        evaluated_at=NOW,
        environment=Environment.TEST,
    )

    assert first == second
    assert first.disposition is CompositionDisposition.PRESERVED
    assert first.reason is CompositionReason.ALL_CANDIDATES_PRESERVED
    assert first.candidates == (alpha_candidate, beta_candidate)
    assert first.unavailable_channels == ()


@pytest.mark.parametrize(
    "drifted",
    [
        candidate(evidence_id="syn_comp_evidence_beta"),
        candidate(evidence_version="engineering.v2"),
        candidate(evidence_hash=HASH_B),
        candidate(channel=EvidenceChannel.SYNTHETIC_CHANNEL_BETA),
    ],
)
def test_candidate_reference_drift_fails_closed(
    drifted: SyntheticActionCandidate,
) -> None:
    with pytest.raises(CompositionContractError) as captured:
        compose_synthetic_candidates(
            request(),
            (drifted,),
            evaluated_at=NOW,
            environment=Environment.TEST,
        )

    assert captured.value.code is CompositionCode.REFERENCE_MISMATCH


def test_forced_request_mutation_is_rejected_at_boundary() -> None:
    composition_request = request()
    object.__setattr__(composition_request, "snapshot_hash", HASH_B)

    with pytest.raises(CompositionContractError) as captured:
        compose_synthetic_candidates(
            composition_request,
            (candidate(),),
            evaluated_at=NOW,
            environment=Environment.TEST,
        )

    assert captured.value.code is CompositionCode.SNAPSHOT_DRIFT


def test_evaluation_before_request_creation_is_rejected() -> None:
    with pytest.raises(CompositionContractError) as captured:
        compose_synthetic_candidates(
            request(),
            (candidate(),),
            evaluated_at=NOW - timedelta(seconds=1),
            environment=Environment.TEST,
        )

    assert captured.value.code is CompositionCode.INVALID_CHRONOLOGY


def test_preserved_result_exposes_no_execution_or_ranking_surface() -> None:
    decision = compose_synthetic_candidates(
        request(),
        (candidate(),),
        evaluated_at=NOW,
        environment=Environment.TEST,
    )

    assert not hasattr(decision, "execute")
    assert not hasattr(decision, "selected_candidate")
    assert not hasattr(decision, "priority")
    assert not hasattr(decision, "score")
