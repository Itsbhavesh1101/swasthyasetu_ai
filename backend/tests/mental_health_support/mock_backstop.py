"""Deterministic test-only backstop over content-free toy tokens."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from enum import StrEnum

from app.modules.mental_health.backstop import (
    SyntheticBackstopFailure,
    SyntheticBackstopFailureCode,
    SyntheticBackstopOutcome,
    SyntheticBackstopRequest,
    SyntheticBackstopResponse,
    SyntheticBackstopResult,
    SyntheticEvidenceToken,
    synthetic_backstop_request_fingerprint,
    validate_synthetic_backstop_request,
    validate_synthetic_backstop_result,
)
from app.modules.mental_health.contracts import (
    SyntheticSignalCode,
    SyntheticSignalObservation,
    SyntheticSignalState,
)


class SyntheticBackstopMode(StrEnum):
    SUCCESS = "SUCCESS"
    TIMEOUT = "TIMEOUT"
    UNAVAILABLE = "UNAVAILABLE"
    CANCELLED = "CANCELLED"


_TOKEN_TO_SIGNAL = {
    SyntheticEvidenceToken.ALPHA: SyntheticSignalCode.ALPHA,
    SyntheticEvidenceToken.BETA: SyntheticSignalCode.BETA,
    SyntheticEvidenceToken.GAMMA: SyntheticSignalCode.GAMMA,
    SyntheticEvidenceToken.DELTA: SyntheticSignalCode.DELTA,
}


class DeterministicSyntheticBackstop:
    """Exact toy mapping; never imported by production code."""

    def __init__(
        self,
        *,
        mode: SyntheticBackstopMode = SyntheticBackstopMode.SUCCESS,
        clock: Callable[[], datetime] = lambda: datetime.now().astimezone(),
    ) -> None:
        if type(mode) is not SyntheticBackstopMode:
            raise TypeError("mode must be a SyntheticBackstopMode")
        self._mode = mode
        self._clock = clock

    async def evaluate(self, request: SyntheticBackstopRequest) -> SyntheticBackstopResponse:
        request = validate_synthetic_backstop_request(request)
        now = self._clock()
        suffix = request.request_id.removeprefix("syn_mh_backstop_request_")
        if now >= request.deadline_at or self._mode is SyntheticBackstopMode.TIMEOUT:
            occurred_at = max(now, request.deadline_at)
            return SyntheticBackstopFailure(
                failure_id=f"syn_mh_backstop_failure_{suffix}",
                request_id=request.request_id,
                request_fingerprint=synthetic_backstop_request_fingerprint(request),
                code=SyntheticBackstopFailureCode.SIMULATED_TIMEOUT,
                occurred_at=occurred_at,
            ).validate_for(request)
        failure_code = {
            SyntheticBackstopMode.UNAVAILABLE: SyntheticBackstopFailureCode.SIMULATED_UNAVAILABLE,
            SyntheticBackstopMode.CANCELLED: SyntheticBackstopFailureCode.SIMULATED_CANCELLED,
        }.get(self._mode)
        if failure_code is not None:
            return SyntheticBackstopFailure(
                failure_id=f"syn_mh_backstop_failure_{suffix}",
                request_id=request.request_id,
                request_fingerprint=synthetic_backstop_request_fingerprint(request),
                code=failure_code,
                occurred_at=now,
            ).validate_for(request)
        signals = tuple(
            SyntheticSignalObservation(
                code=_TOKEN_TO_SIGNAL[token],
                state=SyntheticSignalState.PRESENT,
            )
            for token in request.evidence_tokens
        )
        result = SyntheticBackstopResult(
            result_id=f"syn_mh_backstop_result_{suffix}",
            request_id=request.request_id,
            request_fingerprint=synthetic_backstop_request_fingerprint(request),
            input_artifact_id=request.input_artifact.artifact_id,
            input_artifact_version=request.input_artifact.artifact_version,
            input_artifact_hash=request.input_artifact.content_hash,
            backstop_artifact_id=request.backstop_artifact.artifact_id,
            backstop_artifact_version=request.backstop_artifact.artifact_version,
            backstop_artifact_hash=request.backstop_artifact.content_hash,
            outcome=(
                SyntheticBackstopOutcome.SYNTHETIC_MATCHED
                if signals
                else SyntheticBackstopOutcome.SYNTHETIC_NO_MATCH
            ),
            signals=signals,
            completed_at=now,
        )
        return validate_synthetic_backstop_result(request, result)


__all__ = ["DeterministicSyntheticBackstop", "SyntheticBackstopMode"]
