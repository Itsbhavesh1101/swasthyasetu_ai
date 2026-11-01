"""Content-free reconciliation of detached synthetic source receipts."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256
from typing import Final

from app.config import Environment
from app.modules.care_orchestration.contracts import (
    CompositionAuthority,
    CompositionClassification,
    CompositionVerification,
    EvidenceAvailability,
    EvidenceChannel,
    SyntheticCompositionRequest,
    snapshot_request,
)
from app.modules.care_orchestration.sources import (
    SyntheticEvidenceSourcePort,
    SyntheticEvidenceSourceQuery,
    SyntheticEvidenceSourceReceipt,
    inspect_synthetic_evidence,
    validate_synthetic_source_receipt,
)

_PROTECTED_ENVIRONMENTS = frozenset(
    {Environment.STAGING, Environment.PILOT, Environment.PRODUCTION}
)
SYNTHETIC_RECONCILIATION_VERSION: Final = "synthetic-snapshot-reconciliation.v1"
_QUERY_SUFFIX = {
    EvidenceChannel.SYNTHETIC_CHANNEL_ALPHA: "alpha",
    EvidenceChannel.SYNTHETIC_CHANNEL_BETA: "beta",
    EvidenceChannel.SYNTHETIC_CHANNEL_GAMMA: "gamma",
    EvidenceChannel.SYNTHETIC_CHANNEL_DELTA: "delta",
}


class ReconciliationCode(StrEnum):
    INVALID_TYPE = "INVALID_TYPE"
    INVALID_VALUE = "INVALID_VALUE"
    INVALID_CHRONOLOGY = "INVALID_CHRONOLOGY"
    PROTECTED_ENVIRONMENT = "PROTECTED_ENVIRONMENT"
    SOURCE_SET_MISMATCH = "SOURCE_SET_MISMATCH"
    SOURCE_FAILURE = "SOURCE_FAILURE"
    DUPLICATE_RECEIPT = "DUPLICATE_RECEIPT"
    RECEIPT_SET_MISMATCH = "RECEIPT_SET_MISMATCH"
    RECEIPT_MISMATCH = "RECEIPT_MISMATCH"


class ReconciliationError(ValueError):
    """Stable content-free reconciliation failure."""

    def __init__(self, code: ReconciliationCode) -> None:
        self.code = code
        super().__init__(code.value)


def _error(code: ReconciliationCode) -> ReconciliationError:
    return ReconciliationError(code)


class SyntheticSnapshotState(StrEnum):
    STRUCTURALLY_COMPLETE = "STRUCTURALLY_COMPLETE"
    STRUCTURALLY_COMPLETE_WITH_UNAVAILABLE = "STRUCTURALLY_COMPLETE_WITH_UNAVAILABLE"


def _utc(value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise _error(ReconciliationCode.INVALID_TYPE)
    return value.astimezone(UTC)


def _snapshot_receipt(value: object) -> SyntheticEvidenceSourceReceipt:
    if type(value) is not SyntheticEvidenceSourceReceipt:
        raise _error(ReconciliationCode.INVALID_TYPE)
    try:
        return SyntheticEvidenceSourceReceipt(
            query_id=value.query_id,
            query_fingerprint=value.query_fingerprint,
            request_id=value.request_id,
            request_fingerprint=value.request_fingerprint,
            descriptor_fingerprint=value.descriptor_fingerprint,
            channel=value.channel,
            evidence_id=value.evidence_id,
            evidence_version=value.evidence_version,
            evidence_hash=value.evidence_hash,
            availability=value.availability,
            completed_at=value.completed_at,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
        )
    except Exception:
        raise _error(ReconciliationCode.RECEIPT_MISMATCH) from None


def _receipt_payload(value: SyntheticEvidenceSourceReceipt) -> dict[str, str]:
    return {
        "availability": value.availability.value,
        "channel": value.channel.value,
        "completed_at": value.completed_at.isoformat(),
        "descriptor_fingerprint": value.descriptor_fingerprint,
        "evidence_hash": value.evidence_hash,
        "evidence_id": value.evidence_id,
        "evidence_version": value.evidence_version,
        "query_fingerprint": value.query_fingerprint,
        "query_id": value.query_id,
        "request_fingerprint": value.request_fingerprint,
        "request_id": value.request_id,
    }


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticSnapshotReconciliation:
    request: SyntheticCompositionRequest
    receipts: tuple[SyntheticEvidenceSourceReceipt, ...]
    requested_at: datetime
    reconciled_at: datetime
    authority: CompositionAuthority = CompositionAuthority.ENGINEERING_ONLY
    classification: CompositionClassification = CompositionClassification.ENGINEERING_SYNTHETIC
    verification: CompositionVerification = CompositionVerification.UNVERIFIED
    reconciliation_version: str = SYNTHETIC_RECONCILIATION_VERSION
    state: SyntheticSnapshotState = field(init=False)
    unavailable_channels: tuple[EvidenceChannel, ...] = field(init=False)
    _fingerprint: str = field(init=False, repr=False, compare=True)

    def __post_init__(self) -> None:
        safe_request = snapshot_request(self.request)
        requested_at = _utc(self.requested_at)
        reconciled_at = _utc(self.reconciled_at)
        if requested_at < safe_request.created_at or reconciled_at < requested_at:
            raise _error(ReconciliationCode.INVALID_CHRONOLOGY)
        if type(self.receipts) is not tuple or not self.receipts:
            raise _error(ReconciliationCode.INVALID_TYPE)
        safe_receipts = tuple(
            sorted(
                (_snapshot_receipt(receipt) for receipt in self.receipts),
                key=lambda receipt: receipt.channel.value,
            )
        )
        receipt_channels = tuple(receipt.channel for receipt in safe_receipts)
        if len(set(receipt_channels)) != len(receipt_channels):
            raise _error(ReconciliationCode.DUPLICATE_RECEIPT)
        expected_channels = tuple(item.channel for item in safe_request.evidence)
        if receipt_channels != expected_channels:
            raise _error(ReconciliationCode.RECEIPT_SET_MISMATCH)

        evidence_by_channel = {item.channel: item for item in safe_request.evidence}
        for receipt in safe_receipts:
            evidence = evidence_by_channel[receipt.channel]
            if (
                receipt.request_id != safe_request.request_id
                or receipt.request_fingerprint != safe_request.fingerprint
                or receipt.evidence_id != evidence.evidence_id
                or receipt.evidence_version != evidence.evidence_version
                or receipt.evidence_hash != evidence.artifact_hash
                or receipt.availability is not evidence.availability
            ):
                raise _error(ReconciliationCode.RECEIPT_MISMATCH)
            query = SyntheticEvidenceSourceQuery(
                query_id=f"syn_comp_query_{_QUERY_SUFFIX[receipt.channel]}",
                request_id=safe_request.request_id,
                request_fingerprint=safe_request.fingerprint,
                descriptor_fingerprint=receipt.descriptor_fingerprint,
                channel=receipt.channel,
                evidence_id=evidence.evidence_id,
                evidence_version=evidence.evidence_version,
                evidence_hash=evidence.artifact_hash,
                availability=evidence.availability,
                requested_at=requested_at,
            )
            try:
                validate_synthetic_source_receipt(query=query, receipt=receipt)
            except Exception:
                raise _error(ReconciliationCode.RECEIPT_MISMATCH) from None
            if receipt.completed_at > reconciled_at:
                raise _error(ReconciliationCode.INVALID_CHRONOLOGY)

        if (
            type(self.authority) is not CompositionAuthority
            or self.authority is not CompositionAuthority.ENGINEERING_ONLY
            or type(self.classification) is not CompositionClassification
            or self.classification is not CompositionClassification.ENGINEERING_SYNTHETIC
            or type(self.verification) is not CompositionVerification
            or self.verification is not CompositionVerification.UNVERIFIED
        ):
            raise _error(ReconciliationCode.INVALID_TYPE)
        if (
            type(self.reconciliation_version) is not str
            or self.reconciliation_version != SYNTHETIC_RECONCILIATION_VERSION
        ):
            raise _error(ReconciliationCode.INVALID_VALUE)

        unavailable = tuple(
            receipt.channel
            for receipt in safe_receipts
            if receipt.availability is not EvidenceAvailability.PRESENT_UNVERIFIED
        )
        state = (
            SyntheticSnapshotState.STRUCTURALLY_COMPLETE_WITH_UNAVAILABLE
            if unavailable
            else SyntheticSnapshotState.STRUCTURALLY_COMPLETE
        )
        payload = {
            "receipts": [_receipt_payload(receipt) for receipt in safe_receipts],
            "reconciled_at": reconciled_at.isoformat(),
            "reconciliation_version": self.reconciliation_version,
            "request_fingerprint": safe_request.fingerprint,
            "requested_at": requested_at.isoformat(),
            "state": state.value,
        }
        fingerprint = sha256(
            json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("ascii")
        ).hexdigest()
        object.__setattr__(self, "request", safe_request)
        object.__setattr__(self, "receipts", safe_receipts)
        object.__setattr__(self, "requested_at", requested_at)
        object.__setattr__(self, "reconciled_at", reconciled_at)
        object.__setattr__(self, "state", state)
        object.__setattr__(self, "unavailable_channels", unavailable)
        object.__setattr__(self, "_fingerprint", fingerprint)

    @property
    def fingerprint(self) -> str:
        return self._fingerprint


def reconcile_synthetic_snapshot(
    request: SyntheticCompositionRequest,
    *,
    sources: Mapping[EvidenceChannel, SyntheticEvidenceSourcePort],
    requested_at: datetime,
    reconciled_at: datetime,
    environment: Environment,
) -> SyntheticSnapshotReconciliation:
    """Reconcile exact structural echoes; never read or interpret source data."""

    if type(environment) is not Environment:
        raise _error(ReconciliationCode.INVALID_TYPE)
    if environment in _PROTECTED_ENVIRONMENTS:
        raise _error(ReconciliationCode.PROTECTED_ENVIRONMENT)
    safe_request = snapshot_request(request)
    safe_requested_at = _utc(requested_at)
    safe_reconciled_at = _utc(reconciled_at)
    if safe_requested_at < safe_request.created_at or safe_reconciled_at < safe_requested_at:
        raise _error(ReconciliationCode.INVALID_CHRONOLOGY)
    if not isinstance(sources, Mapping):
        raise _error(ReconciliationCode.INVALID_TYPE)
    try:
        detached_sources = dict(sources.items())
    except Exception:
        raise _error(ReconciliationCode.INVALID_TYPE) from None
    if any(type(channel) is not EvidenceChannel for channel in detached_sources):
        raise _error(ReconciliationCode.INVALID_TYPE)
    expected_channels = {item.channel for item in safe_request.evidence}
    if set(detached_sources) != expected_channels:
        raise _error(ReconciliationCode.SOURCE_SET_MISMATCH)

    receipts: list[SyntheticEvidenceSourceReceipt] = []
    for item in safe_request.evidence:
        try:
            receipt = inspect_synthetic_evidence(
                safe_request,
                channel=item.channel,
                source=detached_sources[item.channel],
                requested_at=safe_requested_at,
                environment=environment,
            )
        except Exception:
            raise _error(ReconciliationCode.SOURCE_FAILURE) from None
        receipts.append(receipt)
    return SyntheticSnapshotReconciliation(
        request=safe_request,
        receipts=tuple(receipts),
        requested_at=safe_requested_at,
        reconciled_at=safe_reconciled_at,
    )


__all__ = [
    "ReconciliationCode",
    "ReconciliationError",
    "SYNTHETIC_RECONCILIATION_VERSION",
    "SyntheticSnapshotReconciliation",
    "SyntheticSnapshotState",
    "reconcile_synthetic_snapshot",
]
