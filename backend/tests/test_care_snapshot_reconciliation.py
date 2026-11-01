from __future__ import annotations

from collections.abc import Mapping
from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime, timedelta, timezone

import pytest
from care_orchestration_support import DeterministicSyntheticEvidenceSource

from app.config import Environment, Settings
from app.main import create_app
from app.modules.care_orchestration import (
    EvidenceAvailability,
    EvidenceChannel,
    SyntheticCompositionRequest,
    SyntheticEvidenceReference,
)
from app.modules.care_orchestration.reconciliation import (
    ReconciliationCode,
    ReconciliationError,
    SyntheticSnapshotReconciliation,
    SyntheticSnapshotState,
    reconcile_synthetic_snapshot,
)
from app.modules.care_orchestration.sources import (
    SyntheticEvidenceSourceDescriptor,
    SyntheticEvidenceSourcePort,
    SyntheticEvidenceSourceReceipt,
)

NOW = datetime(2026, 11, 2, 10, 0, tzinfo=UTC)
HASH_A = "a" * 64
HASH_B = "b" * 64
HASH_C = "c" * 64
HASH_D = "d" * 64


def evidence(
    suffix: str,
    *,
    channel: EvidenceChannel,
    artifact_hash: str,
    availability: EvidenceAvailability = EvidenceAvailability.PRESENT_UNVERIFIED,
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


def request(
    *, beta_availability: EvidenceAvailability = EvidenceAvailability.PRESENT_UNVERIFIED
) -> SyntheticCompositionRequest:
    return SyntheticCompositionRequest(
        request_id="syn_comp_request_alpha",
        snapshot_id="syn_comp_snapshot_alpha",
        snapshot_version="engineering.v1",
        snapshot_hash=HASH_D,
        evidence=(
            evidence(
                "alpha",
                channel=EvidenceChannel.SYNTHETIC_CHANNEL_ALPHA,
                artifact_hash=HASH_A,
            ),
            evidence(
                "beta",
                channel=EvidenceChannel.SYNTHETIC_CHANNEL_BETA,
                artifact_hash=HASH_B,
                availability=beta_availability,
            ),
        ),
        created_at=NOW,
    )


def adapter(
    suffix: str,
    *,
    channel: EvidenceChannel,
    source_hash: str,
    completed_at: datetime = NOW + timedelta(seconds=1),
) -> DeterministicSyntheticEvidenceSource:
    return DeterministicSyntheticEvidenceSource(
        descriptor=SyntheticEvidenceSourceDescriptor(
            source_id=f"syn_comp_source_{suffix}",
            source_version="engineering.v1",
            source_hash=source_hash,
            channel=channel,
        ),
        completed_at=completed_at,
    )


def sources() -> dict[EvidenceChannel, DeterministicSyntheticEvidenceSource]:
    return {
        EvidenceChannel.SYNTHETIC_CHANNEL_ALPHA: adapter(
            "alpha",
            channel=EvidenceChannel.SYNTHETIC_CHANNEL_ALPHA,
            source_hash=HASH_C,
        ),
        EvidenceChannel.SYNTHETIC_CHANNEL_BETA: adapter(
            "beta",
            channel=EvidenceChannel.SYNTHETIC_CHANNEL_BETA,
            source_hash=HASH_D,
        ),
    }


def reconcile(
    value: SyntheticCompositionRequest | None = None,
    source_map: Mapping[EvidenceChannel, SyntheticEvidenceSourcePort] | None = None,
) -> SyntheticSnapshotReconciliation:
    return reconcile_synthetic_snapshot(
        value or request(),
        sources=source_map or sources(),
        requested_at=NOW,
        reconciled_at=NOW + timedelta(seconds=2),
        environment=Environment.TEST,
    )


def test_reconciliation_binds_complete_exact_receipt_set_deterministically() -> None:
    first_sources = sources()
    second_sources = dict(reversed(tuple(sources().items())))
    first = reconcile(source_map=first_sources)
    second = reconcile(source_map=second_sources)

    assert first.state is SyntheticSnapshotState.STRUCTURALLY_COMPLETE
    assert first.unavailable_channels == ()
    assert [receipt.channel for receipt in first.receipts] == [
        EvidenceChannel.SYNTHETIC_CHANNEL_ALPHA,
        EvidenceChannel.SYNTHETIC_CHANNEL_BETA,
    ]
    assert first.fingerprint == second.fingerprint
    assert all(source.calls == 1 for source in first_sources.values())


def test_unavailable_channel_remains_explicit_and_never_becomes_negative() -> None:
    result = reconcile(request(beta_availability=EvidenceAvailability.UNAVAILABLE))

    assert result.state is SyntheticSnapshotState.STRUCTURALLY_COMPLETE_WITH_UNAVAILABLE
    assert result.unavailable_channels == (EvidenceChannel.SYNTHETIC_CHANNEL_BETA,)
    assert result.receipts[1].availability is EvidenceAvailability.UNAVAILABLE


@pytest.mark.parametrize(
    "environment",
    [Environment.STAGING, Environment.PILOT, Environment.PRODUCTION],
)
def test_protected_environment_denies_before_request_or_sources_are_inspected(
    environment: Environment,
) -> None:
    class PoisonMapping(Mapping[EvidenceChannel, SyntheticEvidenceSourcePort]):
        def __getitem__(self, key: EvidenceChannel) -> SyntheticEvidenceSourcePort:
            raise AssertionError("sources inspected")

        def __iter__(self):  # type: ignore[no-untyped-def]
            raise AssertionError("sources inspected")

        def __len__(self) -> int:
            raise AssertionError("sources inspected")

    with pytest.raises(ReconciliationError) as captured:
        reconcile_synthetic_snapshot(
            object(),  # type: ignore[arg-type]
            sources=PoisonMapping(),
            requested_at=NOW,
            reconciled_at=NOW,
            environment=environment,
        )
    assert captured.value.code is ReconciliationCode.PROTECTED_ENVIRONMENT


@pytest.mark.parametrize("drop_or_add", ["drop", "add"])
def test_source_set_must_exactly_match_request_channels_before_any_call(
    drop_or_add: str,
) -> None:
    source_map = sources()
    if drop_or_add == "drop":
        source_map.pop(EvidenceChannel.SYNTHETIC_CHANNEL_BETA)
    else:
        source_map[EvidenceChannel.SYNTHETIC_CHANNEL_GAMMA] = adapter(
            "gamma",
            channel=EvidenceChannel.SYNTHETIC_CHANNEL_GAMMA,
            source_hash=HASH_C,
        )

    with pytest.raises(ReconciliationError) as captured:
        reconcile(source_map=source_map)
    assert captured.value.code is ReconciliationCode.SOURCE_SET_MISMATCH
    assert all(source.calls == 0 for source in source_map.values())


def test_source_failure_returns_no_partial_reconciliation_and_sanitizes_detail() -> None:
    alpha = sources()[EvidenceChannel.SYNTHETIC_CHANNEL_ALPHA]

    class FailingSource:
        descriptor = SyntheticEvidenceSourceDescriptor(
            source_id="syn_comp_source_beta",
            source_version="engineering.v1",
            source_hash=HASH_D,
            channel=EvidenceChannel.SYNTHETIC_CHANNEL_BETA,
        )

        def inspect(self, query: object) -> SyntheticEvidenceSourceReceipt:
            raise RuntimeError("private-canary")

    with pytest.raises(ReconciliationError) as captured:
        reconcile(
            source_map={
                EvidenceChannel.SYNTHETIC_CHANNEL_ALPHA: alpha,
                EvidenceChannel.SYNTHETIC_CHANNEL_BETA: FailingSource(),
            }
        )
    assert captured.value.code is ReconciliationCode.SOURCE_FAILURE
    assert "private-canary" not in str(captured.value)


def test_direct_constructor_rejects_missing_duplicate_or_extra_receipts() -> None:
    valid = reconcile()
    invalid_sets = (
        valid.receipts[:-1],
        (valid.receipts[0], valid.receipts[0]),
        valid.receipts
        + (
            replace(
                valid.receipts[0],
                query_id="syn_comp_query_gamma",
                channel=EvidenceChannel.SYNTHETIC_CHANNEL_GAMMA,
                evidence_id="syn_comp_evidence_gamma",
            ),
        ),
    )
    for receipts in invalid_sets:
        with pytest.raises(ReconciliationError) as captured:
            replace(valid, receipts=receipts)
        assert captured.value.code in {
            ReconciliationCode.RECEIPT_SET_MISMATCH,
            ReconciliationCode.DUPLICATE_RECEIPT,
        }


@pytest.mark.parametrize(
    "mutation",
    [
        {"evidence_hash": HASH_C},
        {"availability": EvidenceAvailability.UNAVAILABLE},
        {"descriptor_fingerprint": HASH_A},
        {"query_fingerprint": HASH_A},
    ],
)
def test_direct_constructor_rejects_receipt_identity_or_query_drift(
    mutation: dict[str, object],
) -> None:
    valid = reconcile()
    drifted = replace(valid.receipts[0], **mutation)  # type: ignore[arg-type]
    with pytest.raises(ReconciliationError) as captured:
        replace(valid, receipts=(drifted, valid.receipts[1]))
    assert captured.value.code is ReconciliationCode.RECEIPT_MISMATCH


def test_reconciliation_normalizes_aware_times_and_rejects_invalid_chronology() -> None:
    offset = timezone(timedelta(hours=5, minutes=30))
    result = reconcile_synthetic_snapshot(
        request(),
        sources=sources(),
        requested_at=NOW.astimezone(offset),
        reconciled_at=(NOW + timedelta(seconds=2)).astimezone(offset),
        environment=Environment.LOCAL,
    )
    assert result.requested_at.tzinfo is UTC
    assert result.reconciled_at.tzinfo is UTC

    with pytest.raises(ReconciliationError) as captured:
        reconcile_synthetic_snapshot(
            request(),
            sources=sources(),
            requested_at=NOW,
            reconciled_at=NOW,
            environment=Environment.TEST,
        )
    assert captured.value.code is ReconciliationCode.INVALID_CHRONOLOGY


def test_reconciliation_is_immutable_and_has_no_data_or_action_surface() -> None:
    result = reconcile()
    with pytest.raises(FrozenInstanceError):
        result.receipts = ()  # type: ignore[misc]

    for forbidden in (
        "patient",
        "subject",
        "session",
        "encounter",
        "actor",
        "institution",
        "consent",
        "payload",
        "narrative",
        "clinical",
        "retrieve",
        "query_database",
        "select",
        "rank",
        "authorize",
        "execute",
    ):
        assert not hasattr(result, forbidden)


def test_reconciliation_rejects_contract_version_drift() -> None:
    with pytest.raises(ReconciliationError) as captured:
        replace(reconcile(), reconciliation_version="synthetic-snapshot-reconciliation.v2")
    assert captured.value.code is ReconciliationCode.INVALID_VALUE


def test_reconciliation_is_not_registered_or_exposed_as_an_api() -> None:
    application = create_app(Settings(_env_file=None))
    module_ids = set(application.state.module_registry.module_ids)
    route_paths = {
        path
        for route in application.routes
        if isinstance(path := getattr(route, "path", None), str)
    }
    assert "care_orchestration" not in module_ids
    assert all("orchestration" not in path and "reconciliation" not in path for path in route_paths)
