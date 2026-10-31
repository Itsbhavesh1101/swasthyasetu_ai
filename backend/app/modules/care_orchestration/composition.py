"""Fail-closed detached composition of engineering-synthetic candidates."""

from __future__ import annotations

from datetime import UTC, datetime

from app.config import Environment
from app.modules.care_orchestration.contracts import (
    MAX_CANDIDATES,
    CompositionCode,
    CompositionContractError,
    CompositionDisposition,
    CompositionReason,
    EvidenceAvailability,
    SyntheticActionCandidate,
    SyntheticCompositionDecision,
    SyntheticCompositionRequest,
    snapshot_candidate,
    snapshot_request,
)

_PROTECTED_ENVIRONMENTS = frozenset(
    {Environment.STAGING, Environment.PILOT, Environment.PRODUCTION}
)


def _error(code: CompositionCode) -> CompositionContractError:
    return CompositionContractError(code)


def _utc(value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise _error(CompositionCode.INVALID_TYPE)
    return value.astimezone(UTC)


def compose_synthetic_candidates(
    request: SyntheticCompositionRequest,
    candidates: tuple[SyntheticActionCandidate, ...],
    *,
    evaluated_at: datetime,
    environment: Environment,
) -> SyntheticCompositionDecision:
    """Preserve exact symbolic candidates or abstain; never choose or execute an action."""

    if type(environment) is not Environment:
        raise _error(CompositionCode.INVALID_TYPE)
    if environment in _PROTECTED_ENVIRONMENTS:
        raise _error(CompositionCode.PROTECTED_ENVIRONMENT)

    safe_request = snapshot_request(request)
    safe_evaluated_at = _utc(evaluated_at)
    if safe_evaluated_at < safe_request.created_at:
        raise _error(CompositionCode.INVALID_CHRONOLOGY)

    unavailable_channels = tuple(
        item.channel
        for item in safe_request.evidence
        if item.availability is not EvidenceAvailability.PRESENT_UNVERIFIED
    )
    if unavailable_channels:
        return SyntheticCompositionDecision(
            request_id=safe_request.request_id,
            request_fingerprint=safe_request.fingerprint,
            snapshot_id=safe_request.snapshot_id,
            snapshot_version=safe_request.snapshot_version,
            snapshot_hash=safe_request.snapshot_hash,
            disposition=CompositionDisposition.ABSTAINED,
            reason=CompositionReason.EVIDENCE_NOT_AVAILABLE,
            candidates=(),
            unavailable_channels=unavailable_channels,
            evaluated_at=safe_evaluated_at,
        )

    if type(candidates) is not tuple or len(candidates) > MAX_CANDIDATES:
        raise _error(CompositionCode.INVALID_TYPE)
    safe_candidates = tuple(snapshot_candidate(item) for item in candidates)
    if not safe_candidates:
        return SyntheticCompositionDecision(
            request_id=safe_request.request_id,
            request_fingerprint=safe_request.fingerprint,
            snapshot_id=safe_request.snapshot_id,
            snapshot_version=safe_request.snapshot_version,
            snapshot_hash=safe_request.snapshot_hash,
            disposition=CompositionDisposition.ABSTAINED,
            reason=CompositionReason.NO_CANDIDATES,
            candidates=(),
            unavailable_channels=(),
            evaluated_at=safe_evaluated_at,
        )

    evidence_by_channel = {item.channel: item for item in safe_request.evidence}
    for item in safe_candidates:
        source = evidence_by_channel.get(item.channel)
        if source is None or (
            source.evidence_id != item.evidence_id
            or source.evidence_version != item.evidence_version
            or source.artifact_hash != item.evidence_hash
        ):
            raise _error(CompositionCode.REFERENCE_MISMATCH)

    return SyntheticCompositionDecision(
        request_id=safe_request.request_id,
        request_fingerprint=safe_request.fingerprint,
        snapshot_id=safe_request.snapshot_id,
        snapshot_version=safe_request.snapshot_version,
        snapshot_hash=safe_request.snapshot_hash,
        disposition=CompositionDisposition.PRESERVED,
        reason=CompositionReason.ALL_CANDIDATES_PRESERVED,
        candidates=safe_candidates,
        unavailable_channels=(),
        evaluated_at=safe_evaluated_at,
    )


__all__ = ["compose_synthetic_candidates"]
