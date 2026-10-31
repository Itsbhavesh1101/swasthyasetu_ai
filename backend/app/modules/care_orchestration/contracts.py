"""Strict content-free contracts for detached synthetic care composition."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256
from typing import Final

SYNTHETIC_COMPOSITION_CONTRACT_VERSION: Final = "synthetic-care-composition.v1"
MAX_EVIDENCE_ITEMS: Final = 16
MAX_CANDIDATES: Final = 16

_EVIDENCE_ID = re.compile(r"^syn_comp_evidence_(?:alpha|beta|gamma|delta)$")
_REQUEST_ID = re.compile(r"^syn_comp_request_(?:alpha|beta|gamma|delta)$")
_SNAPSHOT_ID = re.compile(r"^syn_comp_snapshot_(?:alpha|beta|gamma|delta)$")
_CANDIDATE_ID = re.compile(r"^syn_comp_candidate_(?:alpha|beta|gamma|delta)$")
_VERSION = re.compile(r"^engineering\.v[1-9][0-9]{0,5}$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")


class CompositionCode(StrEnum):
    INVALID_TYPE = "INVALID_TYPE"
    INVALID_VALUE = "INVALID_VALUE"
    INVALID_CHRONOLOGY = "INVALID_CHRONOLOGY"
    DUPLICATE_EVIDENCE = "DUPLICATE_EVIDENCE"
    DUPLICATE_CHANNEL = "DUPLICATE_CHANNEL"
    DUPLICATE_CANDIDATE = "DUPLICATE_CANDIDATE"
    REFERENCE_MISMATCH = "REFERENCE_MISMATCH"
    SNAPSHOT_DRIFT = "SNAPSHOT_DRIFT"
    INCONSISTENT_DECISION = "INCONSISTENT_DECISION"
    PROTECTED_ENVIRONMENT = "PROTECTED_ENVIRONMENT"


class CompositionContractError(ValueError):
    """Stable content-free composition failure."""

    def __init__(self, code: CompositionCode) -> None:
        self.code = code
        super().__init__(code.value)


def _error(code: CompositionCode) -> CompositionContractError:
    return CompositionContractError(code)


class CompositionAuthority(StrEnum):
    ENGINEERING_ONLY = "ENGINEERING_ONLY"


class CompositionClassification(StrEnum):
    ENGINEERING_SYNTHETIC = "ENGINEERING_SYNTHETIC"


class CompositionVerification(StrEnum):
    UNVERIFIED = "UNVERIFIED"


class EvidenceChannel(StrEnum):
    SYNTHETIC_CHANNEL_ALPHA = "SYNTHETIC_CHANNEL_ALPHA"
    SYNTHETIC_CHANNEL_BETA = "SYNTHETIC_CHANNEL_BETA"
    SYNTHETIC_CHANNEL_GAMMA = "SYNTHETIC_CHANNEL_GAMMA"
    SYNTHETIC_CHANNEL_DELTA = "SYNTHETIC_CHANNEL_DELTA"


class EvidenceAvailability(StrEnum):
    PRESENT_UNVERIFIED = "PRESENT_UNVERIFIED"
    NOT_EVALUATED = "NOT_EVALUATED"
    UNKNOWN = "UNKNOWN"
    STALE = "STALE"
    UNAVAILABLE = "UNAVAILABLE"
    BLOCKED = "BLOCKED"
    PENDING_HUMAN_REVIEW = "PENDING_HUMAN_REVIEW"


class SyntheticActionCode(StrEnum):
    SYNTHETIC_ACTION_ALPHA = "SYNTHETIC_ACTION_ALPHA"
    SYNTHETIC_ACTION_BETA = "SYNTHETIC_ACTION_BETA"
    SYNTHETIC_ACTION_GAMMA = "SYNTHETIC_ACTION_GAMMA"


class SyntheticReasonCode(StrEnum):
    SYNTHETIC_REASON_ALPHA = "SYNTHETIC_REASON_ALPHA"
    SYNTHETIC_REASON_BETA = "SYNTHETIC_REASON_BETA"
    SYNTHETIC_REASON_GAMMA = "SYNTHETIC_REASON_GAMMA"


class CompositionDisposition(StrEnum):
    PRESERVED = "PRESERVED"
    ABSTAINED = "ABSTAINED"


class CompositionReason(StrEnum):
    ALL_CANDIDATES_PRESERVED = "ALL_CANDIDATES_PRESERVED"
    EVIDENCE_NOT_AVAILABLE = "EVIDENCE_NOT_AVAILABLE"
    NO_CANDIDATES = "NO_CANDIDATES"


def _strict_enum(value: object, expected: type[StrEnum]) -> None:
    if type(value) is not expected:
        raise _error(CompositionCode.INVALID_TYPE)


def _machine_string(value: object, pattern: re.Pattern[str]) -> str:
    if type(value) is not str:
        raise _error(CompositionCode.INVALID_TYPE)
    if pattern.fullmatch(value) is None:
        raise _error(CompositionCode.INVALID_VALUE)
    return value


def _utc(value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise _error(CompositionCode.INVALID_TYPE)
    return value.astimezone(UTC)


def _authority(authority: object, classification: object, verification: object) -> None:
    _strict_enum(authority, CompositionAuthority)
    _strict_enum(classification, CompositionClassification)
    _strict_enum(verification, CompositionVerification)


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticEvidenceReference:
    evidence_id: str
    channel: EvidenceChannel
    evidence_version: str
    artifact_hash: str
    availability: EvidenceAvailability
    effective_at: datetime
    observed_at: datetime
    authority: CompositionAuthority = CompositionAuthority.ENGINEERING_ONLY
    classification: CompositionClassification = CompositionClassification.ENGINEERING_SYNTHETIC
    verification: CompositionVerification = CompositionVerification.UNVERIFIED

    def __post_init__(self) -> None:
        _machine_string(self.evidence_id, _EVIDENCE_ID)
        _strict_enum(self.channel, EvidenceChannel)
        _machine_string(self.evidence_version, _VERSION)
        _machine_string(self.artifact_hash, _SHA256)
        _strict_enum(self.availability, EvidenceAvailability)
        effective_at = _utc(self.effective_at)
        observed_at = _utc(self.observed_at)
        if effective_at > observed_at:
            raise _error(CompositionCode.INVALID_CHRONOLOGY)
        _authority(self.authority, self.classification, self.verification)
        object.__setattr__(self, "effective_at", effective_at)
        object.__setattr__(self, "observed_at", observed_at)


def snapshot_evidence(value: object) -> SyntheticEvidenceReference:
    if type(value) is not SyntheticEvidenceReference:
        raise _error(CompositionCode.INVALID_TYPE)
    try:
        return SyntheticEvidenceReference(
            evidence_id=value.evidence_id,
            channel=value.channel,
            evidence_version=value.evidence_version,
            artifact_hash=value.artifact_hash,
            availability=value.availability,
            effective_at=value.effective_at,
            observed_at=value.observed_at,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
        )
    except CompositionContractError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(CompositionCode.INVALID_TYPE) from None


def _evidence_payload(item: SyntheticEvidenceReference) -> dict[str, str]:
    return {
        "artifact_hash": item.artifact_hash,
        "availability": item.availability.value,
        "channel": item.channel.value,
        "effective_at": item.effective_at.isoformat(),
        "evidence_id": item.evidence_id,
        "evidence_version": item.evidence_version,
        "observed_at": item.observed_at.isoformat(),
    }


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticCompositionRequest:
    request_id: str
    snapshot_id: str
    snapshot_version: str
    snapshot_hash: str
    evidence: tuple[SyntheticEvidenceReference, ...]
    created_at: datetime
    authority: CompositionAuthority = CompositionAuthority.ENGINEERING_ONLY
    classification: CompositionClassification = CompositionClassification.ENGINEERING_SYNTHETIC
    verification: CompositionVerification = CompositionVerification.UNVERIFIED
    _fingerprint: str = field(init=False, repr=False, compare=True)

    def __post_init__(self) -> None:
        _machine_string(self.request_id, _REQUEST_ID)
        _machine_string(self.snapshot_id, _SNAPSHOT_ID)
        _machine_string(self.snapshot_version, _VERSION)
        _machine_string(self.snapshot_hash, _SHA256)
        if (
            type(self.evidence) is not tuple
            or not self.evidence
            or len(self.evidence) > MAX_EVIDENCE_ITEMS
        ):
            raise _error(CompositionCode.INVALID_VALUE)
        safe_evidence = tuple(
            sorted(
                (snapshot_evidence(item) for item in self.evidence),
                key=lambda item: (item.channel.value, item.evidence_id),
            )
        )
        if len({item.evidence_id for item in safe_evidence}) != len(safe_evidence):
            raise _error(CompositionCode.DUPLICATE_EVIDENCE)
        if len({item.channel for item in safe_evidence}) != len(safe_evidence):
            raise _error(CompositionCode.DUPLICATE_CHANNEL)
        created_at = _utc(self.created_at)
        if any(item.observed_at > created_at for item in safe_evidence):
            raise _error(CompositionCode.INVALID_CHRONOLOGY)
        _authority(self.authority, self.classification, self.verification)
        payload = {
            "contract_version": SYNTHETIC_COMPOSITION_CONTRACT_VERSION,
            "created_at": created_at.isoformat(),
            "evidence": [_evidence_payload(item) for item in safe_evidence],
            "request_id": self.request_id,
            "snapshot_hash": self.snapshot_hash,
            "snapshot_id": self.snapshot_id,
            "snapshot_version": self.snapshot_version,
        }
        fingerprint = sha256(
            json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
        ).hexdigest()
        object.__setattr__(self, "evidence", safe_evidence)
        object.__setattr__(self, "created_at", created_at)
        object.__setattr__(self, "_fingerprint", fingerprint)

    @property
    def fingerprint(self) -> str:
        return self._fingerprint


def snapshot_request(value: object) -> SyntheticCompositionRequest:
    if type(value) is not SyntheticCompositionRequest:
        raise _error(CompositionCode.INVALID_TYPE)
    try:
        snapshot = SyntheticCompositionRequest(
            request_id=value.request_id,
            snapshot_id=value.snapshot_id,
            snapshot_version=value.snapshot_version,
            snapshot_hash=value.snapshot_hash,
            evidence=value.evidence,
            created_at=value.created_at,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
        )
    except CompositionContractError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(CompositionCode.INVALID_TYPE) from None
    if snapshot.fingerprint != value.fingerprint:
        raise _error(CompositionCode.SNAPSHOT_DRIFT)
    return snapshot


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticActionCandidate:
    candidate_id: str
    action: SyntheticActionCode
    channel: EvidenceChannel
    evidence_id: str
    evidence_version: str
    evidence_hash: str
    reason_code: SyntheticReasonCode
    authority: CompositionAuthority = CompositionAuthority.ENGINEERING_ONLY
    classification: CompositionClassification = CompositionClassification.ENGINEERING_SYNTHETIC
    verification: CompositionVerification = CompositionVerification.UNVERIFIED

    def __post_init__(self) -> None:
        _machine_string(self.candidate_id, _CANDIDATE_ID)
        _strict_enum(self.action, SyntheticActionCode)
        _strict_enum(self.channel, EvidenceChannel)
        _machine_string(self.evidence_id, _EVIDENCE_ID)
        _machine_string(self.evidence_version, _VERSION)
        _machine_string(self.evidence_hash, _SHA256)
        _strict_enum(self.reason_code, SyntheticReasonCode)
        _authority(self.authority, self.classification, self.verification)


def snapshot_candidate(value: object) -> SyntheticActionCandidate:
    if type(value) is not SyntheticActionCandidate:
        raise _error(CompositionCode.INVALID_TYPE)
    try:
        return SyntheticActionCandidate(
            candidate_id=value.candidate_id,
            action=value.action,
            channel=value.channel,
            evidence_id=value.evidence_id,
            evidence_version=value.evidence_version,
            evidence_hash=value.evidence_hash,
            reason_code=value.reason_code,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
        )
    except CompositionContractError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(CompositionCode.INVALID_TYPE) from None


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticCompositionDecision:
    request_id: str
    request_fingerprint: str
    snapshot_id: str
    snapshot_version: str
    snapshot_hash: str
    disposition: CompositionDisposition
    reason: CompositionReason
    candidates: tuple[SyntheticActionCandidate, ...]
    unavailable_channels: tuple[EvidenceChannel, ...]
    evaluated_at: datetime
    authority: CompositionAuthority = CompositionAuthority.ENGINEERING_ONLY
    classification: CompositionClassification = CompositionClassification.ENGINEERING_SYNTHETIC
    verification: CompositionVerification = CompositionVerification.UNVERIFIED

    def __post_init__(self) -> None:
        _machine_string(self.request_id, _REQUEST_ID)
        _machine_string(self.request_fingerprint, _SHA256)
        _machine_string(self.snapshot_id, _SNAPSHOT_ID)
        _machine_string(self.snapshot_version, _VERSION)
        _machine_string(self.snapshot_hash, _SHA256)
        _strict_enum(self.disposition, CompositionDisposition)
        _strict_enum(self.reason, CompositionReason)
        if type(self.candidates) is not tuple or len(self.candidates) > MAX_CANDIDATES:
            raise _error(CompositionCode.INVALID_TYPE)
        safe_candidates = tuple(
            sorted(
                (snapshot_candidate(item) for item in self.candidates),
                key=lambda item: (item.channel.value, item.action.value, item.candidate_id),
            )
        )
        if len({item.candidate_id for item in safe_candidates}) != len(safe_candidates):
            raise _error(CompositionCode.DUPLICATE_CANDIDATE)
        if type(self.unavailable_channels) is not tuple or any(
            type(item) is not EvidenceChannel for item in self.unavailable_channels
        ):
            raise _error(CompositionCode.INVALID_TYPE)
        unavailable = tuple(sorted(set(self.unavailable_channels), key=lambda item: item.value))
        if len(unavailable) != len(self.unavailable_channels):
            raise _error(CompositionCode.DUPLICATE_CHANNEL)
        if self.disposition is CompositionDisposition.PRESERVED:
            consistent = (
                self.reason is CompositionReason.ALL_CANDIDATES_PRESERVED
                and bool(safe_candidates)
                and not unavailable
            )
        elif self.reason is CompositionReason.EVIDENCE_NOT_AVAILABLE:
            consistent = not safe_candidates and bool(unavailable)
        else:
            consistent = (
                self.reason is CompositionReason.NO_CANDIDATES
                and not safe_candidates
                and not unavailable
            )
        if not consistent:
            raise _error(CompositionCode.INCONSISTENT_DECISION)
        _authority(self.authority, self.classification, self.verification)
        object.__setattr__(self, "candidates", safe_candidates)
        object.__setattr__(self, "unavailable_channels", unavailable)
        object.__setattr__(self, "evaluated_at", _utc(self.evaluated_at))


__all__ = [
    "CompositionAuthority",
    "CompositionClassification",
    "CompositionCode",
    "CompositionContractError",
    "CompositionDisposition",
    "CompositionReason",
    "CompositionVerification",
    "EvidenceAvailability",
    "EvidenceChannel",
    "MAX_CANDIDATES",
    "MAX_EVIDENCE_ITEMS",
    "SYNTHETIC_COMPOSITION_CONTRACT_VERSION",
    "SyntheticActionCandidate",
    "SyntheticActionCode",
    "SyntheticCompositionDecision",
    "SyntheticCompositionRequest",
    "SyntheticEvidenceReference",
    "SyntheticReasonCode",
    "snapshot_candidate",
    "snapshot_evidence",
    "snapshot_request",
]
