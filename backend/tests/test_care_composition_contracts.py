from __future__ import annotations

from collections.abc import Callable
from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta, timezone

import pytest

from app.modules.care_orchestration import (
    CompositionCode,
    CompositionContractError,
    CompositionDisposition,
    CompositionReason,
    EvidenceAvailability,
    EvidenceChannel,
    SyntheticActionCandidate,
    SyntheticActionCode,
    SyntheticCompositionDecision,
    SyntheticCompositionRequest,
    SyntheticEvidenceReference,
    SyntheticReasonCode,
)

NOW = datetime(2026, 11, 1, 12, 0, tzinfo=UTC)
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
    evidence_hash: str = HASH_A,
) -> SyntheticActionCandidate:
    return SyntheticActionCandidate(
        candidate_id=f"syn_comp_candidate_{suffix}",
        action=action,
        channel=channel,
        evidence_id=evidence_id,
        evidence_version="engineering.v1",
        evidence_hash=evidence_hash,
        reason_code=SyntheticReasonCode.SYNTHETIC_REASON_ALPHA,
    )


def test_request_normalizes_utc_and_canonicalizes_evidence_order() -> None:
    offset = timezone(timedelta(hours=5, minutes=30))
    alpha = evidence()
    beta = SyntheticEvidenceReference(
        evidence_id="syn_comp_evidence_beta",
        channel=EvidenceChannel.SYNTHETIC_CHANNEL_BETA,
        evidence_version="engineering.v1",
        artifact_hash=HASH_B,
        availability=EvidenceAvailability.PRESENT_UNVERIFIED,
        effective_at=(NOW - timedelta(minutes=2)).astimezone(offset),
        observed_at=(NOW - timedelta(minutes=1)).astimezone(offset),
    )

    first = request(beta, alpha)
    second = request(alpha, beta)

    assert [item.channel for item in first.evidence] == [
        EvidenceChannel.SYNTHETIC_CHANNEL_ALPHA,
        EvidenceChannel.SYNTHETIC_CHANNEL_BETA,
    ]
    assert first.evidence[1].effective_at.tzinfo is UTC
    assert first.evidence[1].observed_at.tzinfo is UTC
    assert first.fingerprint == second.fingerprint
    assert len(first.fingerprint) == 64


@pytest.mark.parametrize(
    ("factory", "code"),
    [
        (
            lambda: SyntheticEvidenceReference(
                evidence_id="not-synthetic",
                channel=EvidenceChannel.SYNTHETIC_CHANNEL_ALPHA,
                evidence_version="engineering.v1",
                artifact_hash=HASH_A,
                availability=EvidenceAvailability.PRESENT_UNVERIFIED,
                effective_at=NOW,
                observed_at=NOW,
            ),
            CompositionCode.INVALID_VALUE,
        ),
        (
            lambda: SyntheticEvidenceReference(
                evidence_id="syn_comp_evidence_alpha",
                channel="SYNTHETIC_CHANNEL_ALPHA",  # type: ignore[arg-type]
                evidence_version="engineering.v1",
                artifact_hash=HASH_A,
                availability=EvidenceAvailability.PRESENT_UNVERIFIED,
                effective_at=NOW,
                observed_at=NOW,
            ),
            CompositionCode.INVALID_TYPE,
        ),
        (
            lambda: SyntheticEvidenceReference(
                evidence_id="syn_comp_evidence_alpha",
                channel=EvidenceChannel.SYNTHETIC_CHANNEL_ALPHA,
                evidence_version="engineering.v1",
                artifact_hash=HASH_A,
                availability=EvidenceAvailability.PRESENT_UNVERIFIED,
                effective_at=datetime(2026, 11, 1, 12, 0),
                observed_at=NOW,
            ),
            CompositionCode.INVALID_TYPE,
        ),
        (
            lambda: SyntheticEvidenceReference(
                evidence_id="syn_comp_evidence_alpha",
                channel=EvidenceChannel.SYNTHETIC_CHANNEL_ALPHA,
                evidence_version="engineering.v1",
                artifact_hash=HASH_A,
                availability=EvidenceAvailability.PRESENT_UNVERIFIED,
                effective_at=NOW,
                observed_at=NOW - timedelta(seconds=1),
            ),
            CompositionCode.INVALID_CHRONOLOGY,
        ),
        (
            lambda: SyntheticActionCandidate(
                candidate_id="syn_comp_candidate_alpha",
                action=True,  # type: ignore[arg-type]
                channel=EvidenceChannel.SYNTHETIC_CHANNEL_ALPHA,
                evidence_id="syn_comp_evidence_alpha",
                evidence_version="engineering.v1",
                evidence_hash=HASH_A,
                reason_code=SyntheticReasonCode.SYNTHETIC_REASON_ALPHA,
            ),
            CompositionCode.INVALID_TYPE,
        ),
    ],
)
def test_direct_constructors_reject_malformed_values(
    factory: Callable[[], object], code: CompositionCode
) -> None:
    with pytest.raises(CompositionContractError) as captured:
        factory()

    assert captured.value.code is code
    assert str(captured.value) == code.value


@pytest.mark.parametrize(
    "items",
    [
        (
            evidence(),
            evidence("beta", channel=EvidenceChannel.SYNTHETIC_CHANNEL_BETA),
        ),
        (
            evidence(),
            evidence("beta", channel=EvidenceChannel.SYNTHETIC_CHANNEL_ALPHA),
        ),
    ],
)
def test_request_rejects_duplicate_evidence_identity_or_channel(
    items: tuple[SyntheticEvidenceReference, ...],
) -> None:
    if items[0].evidence_id != items[1].evidence_id:
        items = (
            (
                items[0],
                SyntheticEvidenceReference(
                    evidence_id=items[0].evidence_id,
                    channel=items[1].channel,
                    evidence_version=items[1].evidence_version,
                    artifact_hash=items[1].artifact_hash,
                    availability=items[1].availability,
                    effective_at=items[1].effective_at,
                    observed_at=items[1].observed_at,
                ),
            )
            if items[0].channel is not items[1].channel
            else items
        )

    with pytest.raises(CompositionContractError) as captured:
        request(*items)

    assert captured.value.code in {
        CompositionCode.DUPLICATE_EVIDENCE,
        CompositionCode.DUPLICATE_CHANNEL,
    }


def test_request_rejects_evidence_observed_after_snapshot_creation() -> None:
    future = SyntheticEvidenceReference(
        evidence_id="syn_comp_evidence_alpha",
        channel=EvidenceChannel.SYNTHETIC_CHANNEL_ALPHA,
        evidence_version="engineering.v1",
        artifact_hash=HASH_A,
        availability=EvidenceAvailability.PRESENT_UNVERIFIED,
        effective_at=NOW,
        observed_at=NOW + timedelta(seconds=1),
    )

    with pytest.raises(CompositionContractError) as captured:
        request(future)

    assert captured.value.code is CompositionCode.INVALID_CHRONOLOGY


def test_contracts_are_frozen_and_hide_no_arbitrary_payload() -> None:
    item = evidence()
    canary = "synthetic-sensitive-payload-canary"

    with pytest.raises(FrozenInstanceError):
        item.evidence_id = canary  # type: ignore[misc]

    assert canary not in repr(item)


@pytest.mark.parametrize(
    "decision",
    [
        lambda: SyntheticCompositionDecision(
            request_id="syn_comp_request_alpha",
            request_fingerprint=HASH_A,
            snapshot_id="syn_comp_snapshot_alpha",
            snapshot_version="engineering.v1",
            snapshot_hash=HASH_C,
            disposition=CompositionDisposition.PRESERVED,
            reason=CompositionReason.ALL_CANDIDATES_PRESERVED,
            candidates=(),
            unavailable_channels=(),
            evaluated_at=NOW,
        ),
        lambda: SyntheticCompositionDecision(
            request_id="syn_comp_request_alpha",
            request_fingerprint=HASH_A,
            snapshot_id="syn_comp_snapshot_alpha",
            snapshot_version="engineering.v1",
            snapshot_hash=HASH_C,
            disposition=CompositionDisposition.ABSTAINED,
            reason=CompositionReason.EVIDENCE_NOT_AVAILABLE,
            candidates=(candidate(),),
            unavailable_channels=(EvidenceChannel.SYNTHETIC_CHANNEL_ALPHA,),
            evaluated_at=NOW,
        ),
        lambda: SyntheticCompositionDecision(
            request_id="syn_comp_request_alpha",
            request_fingerprint=HASH_A,
            snapshot_id="syn_comp_snapshot_alpha",
            snapshot_version="engineering.v1",
            snapshot_hash=HASH_C,
            disposition=CompositionDisposition.ABSTAINED,
            reason=CompositionReason.NO_CANDIDATES,
            candidates=(),
            unavailable_channels=(EvidenceChannel.SYNTHETIC_CHANNEL_ALPHA,),
            evaluated_at=NOW,
        ),
    ],
)
def test_decision_rejects_inconsistent_aggregate_state(
    decision: Callable[[], SyntheticCompositionDecision],
) -> None:
    with pytest.raises(CompositionContractError) as captured:
        decision()

    assert captured.value.code is CompositionCode.INCONSISTENT_DECISION
