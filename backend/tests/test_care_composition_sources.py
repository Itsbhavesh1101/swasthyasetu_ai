from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime, timedelta, timezone

import pytest
from care_orchestration_support import DeterministicSyntheticEvidenceSource

from app.config import Environment
from app.modules.care_orchestration import (
    CompositionCode,
    CompositionContractError,
    EvidenceAvailability,
    EvidenceChannel,
    SyntheticCompositionRequest,
    SyntheticEvidenceReference,
)
from app.modules.care_orchestration.sources import (
    SourceBoundaryCode,
    SourceBoundaryError,
    SyntheticEvidenceSourceDescriptor,
    SyntheticEvidenceSourcePort,
    SyntheticEvidenceSourceQuery,
    SyntheticEvidenceSourceReceipt,
    inspect_synthetic_evidence,
    synthetic_source_query_fingerprint,
    validate_synthetic_source_receipt,
)

NOW = datetime(2026, 11, 2, 8, 0, tzinfo=UTC)
HASH_A = "a" * 64
HASH_B = "b" * 64
HASH_C = "c" * 64


def descriptor() -> SyntheticEvidenceSourceDescriptor:
    return SyntheticEvidenceSourceDescriptor(
        source_id="syn_comp_source_alpha",
        source_version="engineering.v1",
        source_hash=HASH_B,
        channel=EvidenceChannel.SYNTHETIC_CHANNEL_ALPHA,
    )


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


def source(
    *, completed_at: datetime = NOW + timedelta(seconds=1)
) -> DeterministicSyntheticEvidenceSource:
    return DeterministicSyntheticEvidenceSource(
        descriptor=descriptor(),
        completed_at=completed_at,
    )


def test_port_echoes_only_exact_structural_reference_metadata() -> None:
    adapter = source()
    receipt = inspect_synthetic_evidence(
        request(),
        channel=EvidenceChannel.SYNTHETIC_CHANNEL_ALPHA,
        source=adapter,
        requested_at=NOW,
        environment=Environment.TEST,
    )

    assert isinstance(adapter, SyntheticEvidenceSourcePort)
    assert adapter.calls == 1
    assert receipt.evidence_id == "syn_comp_evidence_alpha"
    assert receipt.evidence_hash == HASH_A
    assert receipt.availability is EvidenceAvailability.PRESENT_UNVERIFIED
    assert receipt.completed_at == NOW + timedelta(seconds=1)


def test_unavailable_reference_remains_explicitly_unavailable() -> None:
    receipt = inspect_synthetic_evidence(
        request(EvidenceAvailability.UNAVAILABLE),
        channel=EvidenceChannel.SYNTHETIC_CHANNEL_ALPHA,
        source=source(),
        requested_at=NOW,
        environment=Environment.LOCAL,
    )

    assert receipt.availability is EvidenceAvailability.UNAVAILABLE


@pytest.mark.parametrize(
    "environment",
    [Environment.STAGING, Environment.PILOT, Environment.PRODUCTION],
)
def test_protected_environment_denies_before_source_or_request_inspection(
    environment: Environment,
) -> None:
    class Poison:
        @property
        def descriptor(self) -> object:
            raise AssertionError("source inspected")

    with pytest.raises(SourceBoundaryError) as captured:
        inspect_synthetic_evidence(
            object(),  # type: ignore[arg-type]
            channel=EvidenceChannel.SYNTHETIC_CHANNEL_ALPHA,
            source=Poison(),  # type: ignore[arg-type]
            requested_at=NOW,
            environment=environment,
        )

    assert captured.value.code is SourceBoundaryCode.PROTECTED_ENVIRONMENT


def test_descriptor_query_and_receipt_are_immutable_content_free_contracts() -> None:
    value = descriptor()
    with pytest.raises(FrozenInstanceError):
        value.source_id = "syn_comp_source_beta"  # type: ignore[misc]

    receipt = inspect_synthetic_evidence(
        request(),
        channel=EvidenceChannel.SYNTHETIC_CHANNEL_ALPHA,
        source=source(),
        requested_at=NOW,
        environment=Environment.TEST,
    )
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
        "provider_contact",
        "execute",
        "select",
        "rank",
        "authorize",
    ):
        assert not hasattr(receipt, forbidden)


def test_aware_non_utc_times_normalize_and_naive_times_fail() -> None:
    offset = timezone(timedelta(hours=5, minutes=30))
    adapter = source(completed_at=(NOW + timedelta(seconds=1)).astimezone(offset))
    receipt = inspect_synthetic_evidence(
        request(),
        channel=EvidenceChannel.SYNTHETIC_CHANNEL_ALPHA,
        source=adapter,
        requested_at=NOW.astimezone(offset),
        environment=Environment.TEST,
    )
    assert receipt.completed_at.tzinfo is UTC

    with pytest.raises(SourceBoundaryError) as captured:
        inspect_synthetic_evidence(
            request(),
            channel=EvidenceChannel.SYNTHETIC_CHANNEL_ALPHA,
            source=source(),
            requested_at=datetime(2026, 11, 2, 8, 0),
            environment=Environment.TEST,
        )
    assert captured.value.code is SourceBoundaryCode.INVALID_TYPE


def test_source_descriptor_must_match_requested_channel() -> None:
    mismatched = replace(
        descriptor(),
        source_id="syn_comp_source_beta",
        channel=EvidenceChannel.SYNTHETIC_CHANNEL_BETA,
    )
    adapter = DeterministicSyntheticEvidenceSource(
        descriptor=mismatched,
        completed_at=NOW + timedelta(seconds=1),
    )

    with pytest.raises(SourceBoundaryError) as captured:
        inspect_synthetic_evidence(
            request(),
            channel=EvidenceChannel.SYNTHETIC_CHANNEL_ALPHA,
            source=adapter,
            requested_at=NOW,
            environment=Environment.TEST,
        )
    assert captured.value.code is SourceBoundaryCode.CHANNEL_MISMATCH
    assert adapter.calls == 0


def test_missing_channel_fails_without_calling_source() -> None:
    beta = replace(
        descriptor(),
        source_id="syn_comp_source_beta",
        channel=EvidenceChannel.SYNTHETIC_CHANNEL_BETA,
    )
    adapter = DeterministicSyntheticEvidenceSource(
        descriptor=beta,
        completed_at=NOW + timedelta(seconds=1),
    )
    with pytest.raises(CompositionContractError) as captured:
        inspect_synthetic_evidence(
            request(),
            channel=EvidenceChannel.SYNTHETIC_CHANNEL_BETA,
            source=adapter,
            requested_at=NOW,
            environment=Environment.TEST,
        )
    assert captured.value.code is CompositionCode.REFERENCE_MISMATCH
    assert adapter.calls == 0


def test_source_failure_is_minimized_to_stable_content_free_error() -> None:
    class FailingSource:
        descriptor = descriptor()

        def inspect(self, query: SyntheticEvidenceSourceQuery) -> SyntheticEvidenceSourceReceipt:
            raise RuntimeError("private-payload-canary")

    with pytest.raises(SourceBoundaryError) as captured:
        inspect_synthetic_evidence(
            request(),
            channel=EvidenceChannel.SYNTHETIC_CHANNEL_ALPHA,
            source=FailingSource(),
            requested_at=NOW,
            environment=Environment.TEST,
        )
    assert captured.value.code is SourceBoundaryCode.SOURCE_FAILURE
    assert "private-payload-canary" not in str(captured.value)


def test_receipt_rejects_identity_hash_availability_and_chronology_drift() -> None:
    adapter = source()
    valid = inspect_synthetic_evidence(
        request(),
        channel=EvidenceChannel.SYNTHETIC_CHANNEL_ALPHA,
        source=adapter,
        requested_at=NOW,
        environment=Environment.TEST,
    )
    query = SyntheticEvidenceSourceQuery(
        query_id=valid.query_id,
        request_id=valid.request_id,
        request_fingerprint=valid.request_fingerprint,
        descriptor_fingerprint=valid.descriptor_fingerprint,
        channel=valid.channel,
        evidence_id=valid.evidence_id,
        evidence_version=valid.evidence_version,
        evidence_hash=valid.evidence_hash,
        availability=valid.availability,
        requested_at=NOW,
    )

    mutations = (
        replace(valid, evidence_hash=HASH_B),
        replace(valid, availability=EvidenceAvailability.UNAVAILABLE),
        replace(valid, completed_at=NOW - timedelta(seconds=1)),
    )
    for mutated in mutations:
        with pytest.raises(SourceBoundaryError) as captured:
            validate_synthetic_source_receipt(query=query, receipt=mutated)
        assert captured.value.code is SourceBoundaryCode.RECEIPT_MISMATCH


def test_query_fingerprint_detects_forced_mutation() -> None:
    value = request()
    adapter = source()
    valid = inspect_synthetic_evidence(
        value,
        channel=EvidenceChannel.SYNTHETIC_CHANNEL_ALPHA,
        source=adapter,
        requested_at=NOW,
        environment=Environment.TEST,
    )
    query = SyntheticEvidenceSourceQuery(
        query_id=valid.query_id,
        request_id=valid.request_id,
        request_fingerprint=valid.request_fingerprint,
        descriptor_fingerprint=valid.descriptor_fingerprint,
        channel=valid.channel,
        evidence_id=valid.evidence_id,
        evidence_version=valid.evidence_version,
        evidence_hash=valid.evidence_hash,
        availability=valid.availability,
        requested_at=NOW,
    )
    expected = synthetic_source_query_fingerprint(query)
    object.__setattr__(query, "evidence_hash", HASH_B)
    assert synthetic_source_query_fingerprint(query) != expected
