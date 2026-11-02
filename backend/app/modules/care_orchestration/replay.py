"""Offline replay evidence for detached synthetic care composition."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256
from typing import Final

from app.config import Environment
from app.modules.care_orchestration.composition import compose_synthetic_candidates
from app.modules.care_orchestration.contracts import (
    CompositionAuthority,
    CompositionClassification,
    CompositionDisposition,
    CompositionReason,
    CompositionVerification,
    SyntheticActionCandidate,
    SyntheticCompositionDecision,
)
from app.modules.care_orchestration.reconciliation import (
    SyntheticSnapshotReconciliation,
    validate_synthetic_snapshot_reconciliation,
)

SYNTHETIC_REPLAY_VERSION: Final = "synthetic-composition-replay.v1"
_PROTECTED_ENVIRONMENTS = frozenset(
    {Environment.STAGING, Environment.PILOT, Environment.PRODUCTION}
)


class ReplayCode(StrEnum):
    INVALID_TYPE = "INVALID_TYPE"
    INVALID_VALUE = "INVALID_VALUE"
    INVALID_CHRONOLOGY = "INVALID_CHRONOLOGY"
    PROTECTED_ENVIRONMENT = "PROTECTED_ENVIRONMENT"
    DECISION_MISMATCH = "DECISION_MISMATCH"
    EVIDENCE_MISMATCH = "EVIDENCE_MISMATCH"
    REPLAY_DRIFT = "REPLAY_DRIFT"


class ReplayError(ValueError):
    """Stable content-free replay failure."""

    def __init__(self, code: ReplayCode) -> None:
        self.code = code
        super().__init__(code.value)


def _error(code: ReplayCode) -> ReplayError:
    return ReplayError(code)


def _utc(value: object) -> datetime:
    if type(value) is not datetime:
        raise _error(ReplayCode.INVALID_TYPE)
    try:
        if value.tzinfo is None or value.utcoffset() is None:
            raise _error(ReplayCode.INVALID_TYPE)
        return value.astimezone(UTC)
    except ReplayError:
        raise
    except Exception:
        raise _error(ReplayCode.INVALID_TYPE) from None


def _snapshot_decision(value: object) -> SyntheticCompositionDecision:
    if type(value) is not SyntheticCompositionDecision:
        raise _error(ReplayCode.INVALID_TYPE)
    try:
        return SyntheticCompositionDecision(
            request_id=value.request_id,
            request_fingerprint=value.request_fingerprint,
            snapshot_id=value.snapshot_id,
            snapshot_version=value.snapshot_version,
            snapshot_hash=value.snapshot_hash,
            disposition=value.disposition,
            reason=value.reason,
            candidates=value.candidates,
            unavailable_channels=value.unavailable_channels,
            evaluated_at=value.evaluated_at,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
            composition_version=value.composition_version,
        )
    except Exception:
        raise _error(ReplayCode.DECISION_MISMATCH) from None


def _candidate_payload(value: SyntheticActionCandidate) -> dict[str, str]:
    return {
        "action": value.action.value,
        "candidate_id": value.candidate_id,
        "channel": value.channel.value,
        "evidence_hash": value.evidence_hash,
        "evidence_id": value.evidence_id,
        "evidence_version": value.evidence_version,
        "reason_code": value.reason_code.value,
    }


def _decision_payload(value: SyntheticCompositionDecision) -> dict[str, object]:
    return {
        "candidates": [_candidate_payload(candidate) for candidate in value.candidates],
        "composition_version": value.composition_version,
        "disposition": value.disposition.value,
        "evaluated_at": value.evaluated_at.isoformat(),
        "reason": value.reason.value,
        "request_fingerprint": value.request_fingerprint,
        "request_id": value.request_id,
        "snapshot_hash": value.snapshot_hash,
        "snapshot_id": value.snapshot_id,
        "snapshot_version": value.snapshot_version,
        "unavailable_channels": [channel.value for channel in value.unavailable_channels],
    }


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticCompositionReplay:
    reconciliation: SyntheticSnapshotReconciliation
    decision: SyntheticCompositionDecision
    replayed_at: datetime
    authority: CompositionAuthority = CompositionAuthority.ENGINEERING_ONLY
    classification: CompositionClassification = CompositionClassification.ENGINEERING_SYNTHETIC
    verification: CompositionVerification = CompositionVerification.UNVERIFIED
    replay_version: str = SYNTHETIC_REPLAY_VERSION
    _fingerprint: str = field(init=False, repr=False, compare=True)

    def __post_init__(self) -> None:
        try:
            reconciliation = validate_synthetic_snapshot_reconciliation(self.reconciliation)
        except Exception:
            raise _error(ReplayCode.REPLAY_DRIFT) from None
        decision = _snapshot_decision(self.decision)
        replayed_at = _utc(self.replayed_at)
        request = reconciliation.request
        if (
            decision.request_id != request.request_id
            or decision.request_fingerprint != request.fingerprint
            or decision.snapshot_id != request.snapshot_id
            or decision.snapshot_version != request.snapshot_version
            or decision.snapshot_hash != request.snapshot_hash
        ):
            raise _error(ReplayCode.DECISION_MISMATCH)
        if (
            decision.evaluated_at < reconciliation.reconciled_at
            or replayed_at < decision.evaluated_at
        ):
            raise _error(ReplayCode.INVALID_CHRONOLOGY)

        if reconciliation.unavailable_channels:
            consistent = (
                decision.disposition is CompositionDisposition.ABSTAINED
                and decision.reason is CompositionReason.EVIDENCE_NOT_AVAILABLE
                and not decision.candidates
                and decision.unavailable_channels == reconciliation.unavailable_channels
            )
            if not consistent:
                raise _error(ReplayCode.DECISION_MISMATCH)
        elif decision.unavailable_channels:
            raise _error(ReplayCode.DECISION_MISMATCH)

        evidence_by_channel = {item.channel: item for item in request.evidence}
        for candidate in decision.candidates:
            evidence = evidence_by_channel.get(candidate.channel)
            if evidence is None or (
                candidate.evidence_id != evidence.evidence_id
                or candidate.evidence_version != evidence.evidence_version
                or candidate.evidence_hash != evidence.artifact_hash
            ):
                raise _error(ReplayCode.EVIDENCE_MISMATCH)

        if (
            type(self.authority) is not CompositionAuthority
            or self.authority is not CompositionAuthority.ENGINEERING_ONLY
            or type(self.classification) is not CompositionClassification
            or self.classification is not CompositionClassification.ENGINEERING_SYNTHETIC
            or type(self.verification) is not CompositionVerification
            or self.verification is not CompositionVerification.UNVERIFIED
        ):
            raise _error(ReplayCode.INVALID_TYPE)
        if type(self.replay_version) is not str or self.replay_version != SYNTHETIC_REPLAY_VERSION:
            raise _error(ReplayCode.INVALID_VALUE)

        payload = {
            "decision": _decision_payload(decision),
            "reconciliation_fingerprint": reconciliation.fingerprint,
            "replay_version": self.replay_version,
            "replayed_at": replayed_at.isoformat(),
        }
        fingerprint = sha256(
            json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("ascii")
        ).hexdigest()
        object.__setattr__(self, "reconciliation", reconciliation)
        object.__setattr__(self, "decision", decision)
        object.__setattr__(self, "replayed_at", replayed_at)
        object.__setattr__(self, "_fingerprint", fingerprint)

    @property
    def fingerprint(self) -> str:
        return self._fingerprint


def validate_synthetic_composition_replay(value: object) -> SyntheticCompositionReplay:
    if type(value) is not SyntheticCompositionReplay:
        raise _error(ReplayCode.INVALID_TYPE)
    try:
        snapshot = SyntheticCompositionReplay(
            reconciliation=value.reconciliation,
            decision=value.decision,
            replayed_at=value.replayed_at,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
            replay_version=value.replay_version,
        )
    except ReplayError:
        raise
    except Exception:
        raise _error(ReplayCode.INVALID_TYPE) from None
    stored_fingerprint = value.fingerprint
    if (
        type(stored_fingerprint) is not str
        or len(stored_fingerprint) != 64
        or any(character not in "0123456789abcdef" for character in stored_fingerprint)
        or snapshot.fingerprint != stored_fingerprint
    ):
        raise _error(ReplayCode.REPLAY_DRIFT)
    return snapshot


def replay_synthetic_composition(
    reconciliation: SyntheticSnapshotReconciliation,
    candidates: tuple[SyntheticActionCandidate, ...],
    *,
    evaluated_at: datetime,
    replayed_at: datetime,
    environment: Environment,
) -> SyntheticCompositionReplay:
    """Replay detached symbolic preservation/abstention; never execute an action."""

    if type(environment) is not Environment:
        raise _error(ReplayCode.INVALID_TYPE)
    if environment in _PROTECTED_ENVIRONMENTS:
        raise _error(ReplayCode.PROTECTED_ENVIRONMENT)
    try:
        safe_reconciliation = validate_synthetic_snapshot_reconciliation(reconciliation)
    except Exception:
        raise _error(ReplayCode.REPLAY_DRIFT) from None
    safe_evaluated_at = _utc(evaluated_at)
    safe_replayed_at = _utc(replayed_at)
    if (
        safe_evaluated_at < safe_reconciliation.reconciled_at
        or safe_replayed_at < safe_evaluated_at
    ):
        raise _error(ReplayCode.INVALID_CHRONOLOGY)
    decision = compose_synthetic_candidates(
        safe_reconciliation.request,
        candidates,
        evaluated_at=safe_evaluated_at,
        environment=environment,
    )
    return SyntheticCompositionReplay(
        reconciliation=safe_reconciliation,
        decision=decision,
        replayed_at=safe_replayed_at,
    )


__all__ = [
    "ReplayCode",
    "ReplayError",
    "SYNTHETIC_REPLAY_VERSION",
    "SyntheticCompositionReplay",
    "replay_synthetic_composition",
    "validate_synthetic_composition_replay",
]
