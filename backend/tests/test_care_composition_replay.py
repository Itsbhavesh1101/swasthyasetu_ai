from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime, timedelta, timezone, tzinfo

import pytest
from care_orchestration_support import DeterministicSyntheticEvidenceSource

from app.config import Environment, Settings
from app.main import create_app
from app.modules.care_orchestration import (
    CompositionDisposition,
    CompositionReason,
    EvidenceAvailability,
    EvidenceChannel,
    ReconciliationCode,
    ReconciliationError,
    ReplayCode,
    ReplayError,
    SyntheticActionCandidate,
    SyntheticActionCode,
    SyntheticCompositionReplay,
    SyntheticCompositionRequest,
    SyntheticEvidenceReference,
    SyntheticEvidenceSourceDescriptor,
    SyntheticReasonCode,
    SyntheticSnapshotReconciliation,
    reconcile_synthetic_snapshot,
    replay_synthetic_composition,
    validate_synthetic_composition_replay,
    validate_synthetic_snapshot_reconciliation,
)

NOW = datetime(2026, 11, 2, 12, 0, tzinfo=UTC)
HASH_A = "a" * 64
HASH_B = "b" * 64
HASH_C = "c" * 64


class AlwaysEqualFingerprint:
    def __eq__(self, other: object) -> bool:
        return True


class RaisingFingerprint:
    def __eq__(self, other: object) -> bool:
        raise RuntimeError("private-canary")


class RaisingTimezone(tzinfo):
    def utcoffset(self, value: datetime | None) -> timedelta:
        raise RuntimeError("private-canary")

    def dst(self, value: datetime | None) -> timedelta:
        return timedelta(0)

    def tzname(self, value: datetime | None) -> str:
        return "hostile"


def request(
    availability: EvidenceAvailability = EvidenceAvailability.PRESENT_UNVERIFIED,
) -> SyntheticCompositionRequest:
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
                availability=availability,
                effective_at=NOW - timedelta(minutes=2),
                observed_at=NOW - timedelta(minutes=1),
            ),
        ),
        created_at=NOW,
    )


def reconciliation(
    availability: EvidenceAvailability = EvidenceAvailability.PRESENT_UNVERIFIED,
) -> SyntheticSnapshotReconciliation:
    source = DeterministicSyntheticEvidenceSource(
        descriptor=SyntheticEvidenceSourceDescriptor(
            source_id="syn_comp_source_alpha",
            source_version="engineering.v1",
            source_hash=HASH_B,
            channel=EvidenceChannel.SYNTHETIC_CHANNEL_ALPHA,
        ),
        completed_at=NOW + timedelta(seconds=1),
    )
    return reconcile_synthetic_snapshot(
        request(availability),
        sources={EvidenceChannel.SYNTHETIC_CHANNEL_ALPHA: source},
        requested_at=NOW,
        reconciled_at=NOW + timedelta(seconds=2),
        environment=Environment.TEST,
    )


def candidate(*, evidence_hash: str = HASH_A) -> SyntheticActionCandidate:
    return SyntheticActionCandidate(
        candidate_id="syn_comp_candidate_alpha",
        action=SyntheticActionCode.SYNTHETIC_ACTION_ALPHA,
        channel=EvidenceChannel.SYNTHETIC_CHANNEL_ALPHA,
        evidence_id="syn_comp_evidence_alpha",
        evidence_version="engineering.v1",
        evidence_hash=evidence_hash,
        reason_code=SyntheticReasonCode.SYNTHETIC_REASON_ALPHA,
    )


def replay(
    *,
    candidates: object = (candidate(),),
    availability: EvidenceAvailability = EvidenceAvailability.PRESENT_UNVERIFIED,
) -> SyntheticCompositionReplay:
    return replay_synthetic_composition(
        reconciliation(availability),
        candidates,  # type: ignore[arg-type]
        evaluated_at=NOW + timedelta(seconds=3),
        replayed_at=NOW + timedelta(seconds=4),
        environment=Environment.TEST,
    )


def test_complete_replay_preserves_exact_symbolic_candidate_deterministically() -> None:
    first = replay()
    second = replay()
    assert first.decision.disposition is CompositionDisposition.PRESERVED
    assert first.decision.reason is CompositionReason.ALL_CANDIDATES_PRESERVED
    assert first.decision.candidates == (candidate(),)
    assert first.fingerprint == second.fingerprint
    assert validate_synthetic_composition_replay(first) == first


def test_unavailable_evidence_abstains_before_candidate_collection_is_inspected() -> None:
    result = replay(candidates=object(), availability=EvidenceAvailability.UNAVAILABLE)
    assert result.decision.disposition is CompositionDisposition.ABSTAINED
    assert result.decision.reason is CompositionReason.EVIDENCE_NOT_AVAILABLE
    assert result.decision.candidates == ()
    assert result.decision.unavailable_channels == (EvidenceChannel.SYNTHETIC_CHANNEL_ALPHA,)


def test_complete_replay_without_candidates_abstains_explicitly() -> None:
    result = replay(candidates=())
    assert result.decision.disposition is CompositionDisposition.ABSTAINED
    assert result.decision.reason is CompositionReason.NO_CANDIDATES


@pytest.mark.parametrize(
    "environment",
    [Environment.STAGING, Environment.PILOT, Environment.PRODUCTION],
)
def test_protected_environment_denies_before_reconciliation_or_candidates(
    environment: Environment,
) -> None:
    with pytest.raises(ReplayError) as captured:
        replay_synthetic_composition(
            object(),  # type: ignore[arg-type]
            object(),  # type: ignore[arg-type]
            evaluated_at=NOW,
            replayed_at=NOW,
            environment=environment,
        )
    assert captured.value.code is ReplayCode.PROTECTED_ENVIRONMENT


def test_direct_constructor_rejects_request_and_evidence_drift() -> None:
    valid = replay()
    with pytest.raises(ReplayError) as identity:
        replace(valid, decision=replace(valid.decision, request_fingerprint=HASH_B))
    assert identity.value.code is ReplayCode.DECISION_MISMATCH

    with pytest.raises(ReplayError) as evidence:
        replace(
            valid,
            decision=replace(valid.decision, candidates=(candidate(evidence_hash=HASH_B),)),
        )
    assert evidence.value.code is ReplayCode.EVIDENCE_MISMATCH


def test_direct_constructor_rejects_chronology_and_version_drift() -> None:
    valid = replay()
    with pytest.raises(ReplayError) as chronology:
        replace(valid, replayed_at=valid.decision.evaluated_at - timedelta(seconds=1))
    assert chronology.value.code is ReplayCode.INVALID_CHRONOLOGY

    with pytest.raises(ReplayError) as version:
        replace(valid, replay_version="synthetic-composition-replay.v2")
    assert version.value.code is ReplayCode.INVALID_VALUE


def test_aware_non_utc_times_normalize_and_naive_times_fail() -> None:
    offset = timezone(timedelta(hours=5, minutes=30))
    value = replay_synthetic_composition(
        reconciliation(),
        (candidate(),),
        evaluated_at=(NOW + timedelta(seconds=3)).astimezone(offset),
        replayed_at=(NOW + timedelta(seconds=4)).astimezone(offset),
        environment=Environment.LOCAL,
    )
    assert value.replayed_at.tzinfo is UTC
    with pytest.raises(ReplayError) as captured:
        replay_synthetic_composition(
            reconciliation(),
            (candidate(),),
            evaluated_at=datetime(2026, 11, 2, 12, 0, 3),
            replayed_at=NOW + timedelta(seconds=4),
            environment=Environment.TEST,
        )
    assert captured.value.code is ReplayCode.INVALID_TYPE


def test_validators_reject_forced_mutation() -> None:
    value = replay()
    object.__setattr__(value, "_fingerprint", HASH_B)
    with pytest.raises(ReplayError) as captured:
        validate_synthetic_composition_replay(value)
    assert captured.value.code is ReplayCode.REPLAY_DRIFT

    snapshot = reconciliation()
    object.__setattr__(snapshot, "_fingerprint", HASH_B)
    with pytest.raises(ReconciliationError) as reconciliation_error:
        validate_synthetic_snapshot_reconciliation(snapshot)
    assert reconciliation_error.value.code is ReconciliationCode.RECONCILIATION_DRIFT


@pytest.mark.parametrize("hostile_fingerprint", [AlwaysEqualFingerprint(), RaisingFingerprint()])
def test_validators_reject_hostile_fingerprint_objects_without_leaking(
    hostile_fingerprint: object,
) -> None:
    value = replay()
    object.__setattr__(value, "replayed_at", value.replayed_at + timedelta(seconds=1))
    object.__setattr__(value, "_fingerprint", hostile_fingerprint)
    with pytest.raises(ReplayError) as replay_error:
        validate_synthetic_composition_replay(value)
    assert replay_error.value.code is ReplayCode.REPLAY_DRIFT
    assert "private-canary" not in str(replay_error.value)

    snapshot = reconciliation()
    object.__setattr__(snapshot, "reconciled_at", snapshot.reconciled_at + timedelta(seconds=1))
    object.__setattr__(snapshot, "_fingerprint", hostile_fingerprint)
    with pytest.raises(ReconciliationError) as reconciliation_error:
        validate_synthetic_snapshot_reconciliation(snapshot)
    assert reconciliation_error.value.code is ReconciliationCode.RECONCILIATION_DRIFT
    assert "private-canary" not in str(reconciliation_error.value)


def test_reconciliation_validator_rejects_derived_field_mutation() -> None:
    snapshot = reconciliation(EvidenceAvailability.UNAVAILABLE)
    object.__setattr__(snapshot, "unavailable_channels", ())
    object.__setattr__(snapshot, "state", object())
    with pytest.raises(ReconciliationError) as captured:
        validate_synthetic_snapshot_reconciliation(snapshot)
    assert captured.value.code is ReconciliationCode.RECONCILIATION_DRIFT


def test_hostile_timezone_fails_with_content_free_error() -> None:
    hostile_time = datetime(2026, 11, 2, 12, 0, tzinfo=RaisingTimezone())
    with pytest.raises(ReplayError) as captured:
        replay_synthetic_composition(
            reconciliation(),
            (candidate(),),
            evaluated_at=hostile_time,
            replayed_at=NOW + timedelta(seconds=4),
            environment=Environment.TEST,
        )
    assert captured.value.code is ReplayCode.INVALID_TYPE
    assert "private-canary" not in str(captured.value)

    snapshot = reconciliation()
    with pytest.raises(ReconciliationError) as reconciliation_error:
        replace(snapshot, reconciled_at=hostile_time)
    assert reconciliation_error.value.code is ReconciliationCode.INVALID_TYPE
    assert "private-canary" not in str(reconciliation_error.value)


def test_replay_is_immutable_and_has_no_execution_or_sensitive_surface() -> None:
    value = replay()
    with pytest.raises(FrozenInstanceError):
        value.replayed_at = NOW  # type: ignore[misc]
    for forbidden in (
        "patient",
        "subject",
        "session",
        "encounter",
        "consent",
        "payload",
        "clinical",
        "retrieve",
        "persist",
        "publish",
        "authorize",
        "execute",
    ):
        assert not hasattr(value, forbidden)


def test_replay_is_not_registered_or_exposed_as_an_api() -> None:
    application = create_app(Settings(_env_file=None))
    module_ids = set(application.state.module_registry.module_ids)
    route_paths = {
        path
        for route in application.routes
        if isinstance(path := getattr(route, "path", None), str)
    }
    assert "care_orchestration" not in module_ids
    assert all("orchestration" not in path and "replay" not in path for path in route_paths)
