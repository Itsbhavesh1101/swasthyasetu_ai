"""Detached structural evidence-source boundary for synthetic care composition."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from app.config import Environment
from app.modules.care_orchestration.contracts import (
    CompositionAuthority,
    CompositionClassification,
    CompositionCode,
    CompositionContractError,
    CompositionVerification,
    EvidenceAvailability,
    EvidenceChannel,
    SyntheticCompositionRequest,
    snapshot_request,
)

_SOURCE_ID = re.compile(r"^syn_comp_source_(?:alpha|beta|gamma|delta)$")
_QUERY_ID = re.compile(r"^syn_comp_query_(?:alpha|beta|gamma|delta)$")
_EVIDENCE_ID = re.compile(r"^syn_comp_evidence_(?:alpha|beta|gamma|delta)$")
_REQUEST_ID = re.compile(r"^syn_comp_request_(?:alpha|beta|gamma|delta)$")
_VERSION = re.compile(r"^engineering\.v[1-9][0-9]{0,5}$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_PROTECTED_ENVIRONMENTS = frozenset(
    {Environment.STAGING, Environment.PILOT, Environment.PRODUCTION}
)
_QUERY_SUFFIX = {
    EvidenceChannel.SYNTHETIC_CHANNEL_ALPHA: "alpha",
    EvidenceChannel.SYNTHETIC_CHANNEL_BETA: "beta",
    EvidenceChannel.SYNTHETIC_CHANNEL_GAMMA: "gamma",
    EvidenceChannel.SYNTHETIC_CHANNEL_DELTA: "delta",
}


class SourceBoundaryCode(StrEnum):
    INVALID_TYPE = "INVALID_TYPE"
    INVALID_VALUE = "INVALID_VALUE"
    INVALID_CHRONOLOGY = "INVALID_CHRONOLOGY"
    PROTECTED_ENVIRONMENT = "PROTECTED_ENVIRONMENT"
    CHANNEL_MISMATCH = "CHANNEL_MISMATCH"
    RECEIPT_MISMATCH = "RECEIPT_MISMATCH"
    SOURCE_FAILURE = "SOURCE_FAILURE"


class SourceBoundaryError(ValueError):
    """Stable content-free failure from the detached source boundary."""

    def __init__(self, code: SourceBoundaryCode) -> None:
        self.code = code
        super().__init__(code.value)


def _error(code: SourceBoundaryCode) -> SourceBoundaryError:
    return SourceBoundaryError(code)


def _strict_enum(value: object, expected: type[StrEnum]) -> None:
    if type(value) is not expected:
        raise _error(SourceBoundaryCode.INVALID_TYPE)


def _machine_string(value: object, pattern: re.Pattern[str]) -> str:
    if type(value) is not str:
        raise _error(SourceBoundaryCode.INVALID_TYPE)
    if pattern.fullmatch(value) is None:
        raise _error(SourceBoundaryCode.INVALID_VALUE)
    return value


def _utc(value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise _error(SourceBoundaryCode.INVALID_TYPE)
    return value.astimezone(UTC)


def _authority(authority: object, classification: object, verification: object) -> None:
    if (
        type(authority) is not CompositionAuthority
        or authority is not CompositionAuthority.ENGINEERING_ONLY
        or type(classification) is not CompositionClassification
        or classification is not CompositionClassification.ENGINEERING_SYNTHETIC
        or type(verification) is not CompositionVerification
        or verification is not CompositionVerification.UNVERIFIED
    ):
        raise _error(SourceBoundaryCode.INVALID_TYPE)


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticEvidenceSourceDescriptor:
    source_id: str
    source_version: str
    source_hash: str
    channel: EvidenceChannel
    authority: CompositionAuthority = CompositionAuthority.ENGINEERING_ONLY
    classification: CompositionClassification = CompositionClassification.ENGINEERING_SYNTHETIC
    verification: CompositionVerification = CompositionVerification.UNVERIFIED
    _fingerprint: str = field(init=False, repr=False, compare=True)

    def __post_init__(self) -> None:
        _machine_string(self.source_id, _SOURCE_ID)
        _machine_string(self.source_version, _VERSION)
        _machine_string(self.source_hash, _SHA256)
        _strict_enum(self.channel, EvidenceChannel)
        _authority(self.authority, self.classification, self.verification)
        payload = {
            "channel": self.channel.value,
            "source_hash": self.source_hash,
            "source_id": self.source_id,
            "source_version": self.source_version,
        }
        object.__setattr__(self, "_fingerprint", _fingerprint(payload))

    @property
    def fingerprint(self) -> str:
        return self._fingerprint


def _snapshot_descriptor(value: object) -> SyntheticEvidenceSourceDescriptor:
    if type(value) is not SyntheticEvidenceSourceDescriptor:
        raise _error(SourceBoundaryCode.INVALID_TYPE)
    try:
        snapshot = SyntheticEvidenceSourceDescriptor(
            source_id=value.source_id,
            source_version=value.source_version,
            source_hash=value.source_hash,
            channel=value.channel,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
        )
    except SourceBoundaryError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(SourceBoundaryCode.INVALID_TYPE) from None
    if snapshot.fingerprint != value.fingerprint:
        raise _error(SourceBoundaryCode.INVALID_VALUE)
    return snapshot


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticEvidenceSourceQuery:
    query_id: str
    request_id: str
    request_fingerprint: str
    descriptor_fingerprint: str
    channel: EvidenceChannel
    evidence_id: str
    evidence_version: str
    evidence_hash: str
    availability: EvidenceAvailability
    requested_at: datetime
    authority: CompositionAuthority = CompositionAuthority.ENGINEERING_ONLY
    classification: CompositionClassification = CompositionClassification.ENGINEERING_SYNTHETIC
    verification: CompositionVerification = CompositionVerification.UNVERIFIED

    def __post_init__(self) -> None:
        _machine_string(self.query_id, _QUERY_ID)
        _machine_string(self.request_id, _REQUEST_ID)
        _machine_string(self.request_fingerprint, _SHA256)
        _machine_string(self.descriptor_fingerprint, _SHA256)
        _strict_enum(self.channel, EvidenceChannel)
        _machine_string(self.evidence_id, _EVIDENCE_ID)
        _machine_string(self.evidence_version, _VERSION)
        _machine_string(self.evidence_hash, _SHA256)
        _strict_enum(self.availability, EvidenceAvailability)
        object.__setattr__(self, "requested_at", _utc(self.requested_at))
        _authority(self.authority, self.classification, self.verification)


def _query_payload(value: SyntheticEvidenceSourceQuery) -> dict[str, str]:
    return {
        "availability": value.availability.value,
        "channel": value.channel.value,
        "descriptor_fingerprint": value.descriptor_fingerprint,
        "evidence_hash": value.evidence_hash,
        "evidence_id": value.evidence_id,
        "evidence_version": value.evidence_version,
        "query_id": value.query_id,
        "request_fingerprint": value.request_fingerprint,
        "request_id": value.request_id,
        "requested_at": value.requested_at.isoformat(),
    }


def _fingerprint(payload: dict[str, str]) -> str:
    return sha256(
        json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("ascii")
    ).hexdigest()


def _snapshot_query(value: object) -> SyntheticEvidenceSourceQuery:
    if type(value) is not SyntheticEvidenceSourceQuery:
        raise _error(SourceBoundaryCode.INVALID_TYPE)
    try:
        return SyntheticEvidenceSourceQuery(
            query_id=value.query_id,
            request_id=value.request_id,
            request_fingerprint=value.request_fingerprint,
            descriptor_fingerprint=value.descriptor_fingerprint,
            channel=value.channel,
            evidence_id=value.evidence_id,
            evidence_version=value.evidence_version,
            evidence_hash=value.evidence_hash,
            availability=value.availability,
            requested_at=value.requested_at,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
        )
    except SourceBoundaryError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(SourceBoundaryCode.INVALID_TYPE) from None


def synthetic_source_query_fingerprint(query: SyntheticEvidenceSourceQuery) -> str:
    return _fingerprint(_query_payload(_snapshot_query(query)))


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticEvidenceSourceReceipt:
    query_id: str
    query_fingerprint: str
    request_id: str
    request_fingerprint: str
    descriptor_fingerprint: str
    channel: EvidenceChannel
    evidence_id: str
    evidence_version: str
    evidence_hash: str
    availability: EvidenceAvailability
    completed_at: datetime
    authority: CompositionAuthority = CompositionAuthority.ENGINEERING_ONLY
    classification: CompositionClassification = CompositionClassification.ENGINEERING_SYNTHETIC
    verification: CompositionVerification = CompositionVerification.UNVERIFIED

    def __post_init__(self) -> None:
        _machine_string(self.query_id, _QUERY_ID)
        _machine_string(self.query_fingerprint, _SHA256)
        _machine_string(self.request_id, _REQUEST_ID)
        _machine_string(self.request_fingerprint, _SHA256)
        _machine_string(self.descriptor_fingerprint, _SHA256)
        _strict_enum(self.channel, EvidenceChannel)
        _machine_string(self.evidence_id, _EVIDENCE_ID)
        _machine_string(self.evidence_version, _VERSION)
        _machine_string(self.evidence_hash, _SHA256)
        _strict_enum(self.availability, EvidenceAvailability)
        object.__setattr__(self, "completed_at", _utc(self.completed_at))
        _authority(self.authority, self.classification, self.verification)


@runtime_checkable
class SyntheticEvidenceSourcePort(Protocol):
    """Structural test boundary with no payload or source-domain semantics."""

    @property
    def descriptor(self) -> SyntheticEvidenceSourceDescriptor: ...

    def inspect(self, query: SyntheticEvidenceSourceQuery) -> SyntheticEvidenceSourceReceipt: ...


def validate_synthetic_source_receipt(
    *,
    query: SyntheticEvidenceSourceQuery,
    receipt: SyntheticEvidenceSourceReceipt,
) -> SyntheticEvidenceSourceReceipt:
    safe_query = _snapshot_query(query)
    if type(receipt) is not SyntheticEvidenceSourceReceipt:
        raise _error(SourceBoundaryCode.INVALID_TYPE)
    try:
        safe_receipt = SyntheticEvidenceSourceReceipt(
            query_id=receipt.query_id,
            query_fingerprint=receipt.query_fingerprint,
            request_id=receipt.request_id,
            request_fingerprint=receipt.request_fingerprint,
            descriptor_fingerprint=receipt.descriptor_fingerprint,
            channel=receipt.channel,
            evidence_id=receipt.evidence_id,
            evidence_version=receipt.evidence_version,
            evidence_hash=receipt.evidence_hash,
            availability=receipt.availability,
            completed_at=receipt.completed_at,
            authority=receipt.authority,
            classification=receipt.classification,
            verification=receipt.verification,
        )
    except SourceBoundaryError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(SourceBoundaryCode.INVALID_TYPE) from None
    expected = (
        safe_query.query_id,
        synthetic_source_query_fingerprint(safe_query),
        safe_query.request_id,
        safe_query.request_fingerprint,
        safe_query.descriptor_fingerprint,
        safe_query.channel,
        safe_query.evidence_id,
        safe_query.evidence_version,
        safe_query.evidence_hash,
        safe_query.availability,
    )
    actual = (
        safe_receipt.query_id,
        safe_receipt.query_fingerprint,
        safe_receipt.request_id,
        safe_receipt.request_fingerprint,
        safe_receipt.descriptor_fingerprint,
        safe_receipt.channel,
        safe_receipt.evidence_id,
        safe_receipt.evidence_version,
        safe_receipt.evidence_hash,
        safe_receipt.availability,
    )
    if actual != expected or safe_receipt.completed_at < safe_query.requested_at:
        raise _error(SourceBoundaryCode.RECEIPT_MISMATCH)
    return safe_receipt


def inspect_synthetic_evidence(
    request: SyntheticCompositionRequest,
    *,
    channel: EvidenceChannel,
    source: SyntheticEvidenceSourcePort,
    requested_at: datetime,
    environment: Environment,
) -> SyntheticEvidenceSourceReceipt:
    """Validate an exact structural echo; never retrieve or interpret source data."""

    if type(environment) is not Environment:
        raise _error(SourceBoundaryCode.INVALID_TYPE)
    if environment in _PROTECTED_ENVIRONMENTS:
        raise _error(SourceBoundaryCode.PROTECTED_ENVIRONMENT)
    _strict_enum(channel, EvidenceChannel)
    safe_request = snapshot_request(request)
    safe_requested_at = _utc(requested_at)
    if safe_requested_at < safe_request.created_at:
        raise _error(SourceBoundaryCode.INVALID_CHRONOLOGY)

    evidence = next((item for item in safe_request.evidence if item.channel is channel), None)
    if evidence is None:
        raise CompositionContractError(CompositionCode.REFERENCE_MISMATCH)

    try:
        raw_descriptor = source.descriptor
    except Exception:
        raise _error(SourceBoundaryCode.SOURCE_FAILURE) from None
    safe_descriptor = _snapshot_descriptor(raw_descriptor)
    if safe_descriptor.channel is not channel:
        raise _error(SourceBoundaryCode.CHANNEL_MISMATCH)

    query = SyntheticEvidenceSourceQuery(
        query_id=f"syn_comp_query_{_QUERY_SUFFIX[channel]}",
        request_id=safe_request.request_id,
        request_fingerprint=safe_request.fingerprint,
        descriptor_fingerprint=safe_descriptor.fingerprint,
        channel=evidence.channel,
        evidence_id=evidence.evidence_id,
        evidence_version=evidence.evidence_version,
        evidence_hash=evidence.artifact_hash,
        availability=evidence.availability,
        requested_at=safe_requested_at,
    )
    try:
        receipt = source.inspect(query)
    except Exception:
        raise _error(SourceBoundaryCode.SOURCE_FAILURE) from None
    return validate_synthetic_source_receipt(query=query, receipt=receipt)


__all__ = [
    "SourceBoundaryCode",
    "SourceBoundaryError",
    "SyntheticEvidenceSourceDescriptor",
    "SyntheticEvidenceSourcePort",
    "SyntheticEvidenceSourceQuery",
    "SyntheticEvidenceSourceReceipt",
    "inspect_synthetic_evidence",
    "synthetic_source_query_fingerprint",
    "validate_synthetic_source_receipt",
]
