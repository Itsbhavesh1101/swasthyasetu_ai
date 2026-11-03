"""Deterministic offline demonstration of the synthetic care-composition chain."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum

from app.config import Environment
from app.modules.care_orchestration.contracts import (
    EvidenceAvailability,
    EvidenceChannel,
    SyntheticActionCandidate,
    SyntheticActionCode,
    SyntheticCompositionRequest,
    SyntheticEvidenceReference,
    SyntheticReasonCode,
)
from app.modules.care_orchestration.reconciliation import (
    SyntheticSnapshotReconciliation,
    reconcile_synthetic_snapshot,
)
from app.modules.care_orchestration.replay import (
    SyntheticCompositionReplay,
    replay_synthetic_composition,
)
from app.modules.care_orchestration.sources import (
    SyntheticEvidenceSourceDescriptor,
    SyntheticEvidenceSourceQuery,
    SyntheticEvidenceSourceReceipt,
    synthetic_source_query_fingerprint,
)

_NOW = datetime(2026, 11, 3, 6, 0, tzinfo=UTC)
_HASH_ALPHA = "a" * 64
_HASH_BETA = "b" * 64
_HASH_SNAPSHOT = "c" * 64
_HASH_SOURCE_ALPHA = "d" * 64
_HASH_SOURCE_BETA = "e" * 64
_PROTECTED_ENVIRONMENTS = frozenset(
    {Environment.STAGING, Environment.PILOT, Environment.PRODUCTION}
)


class CareCompositionDemoCode(StrEnum):
    INVALID_TYPE = "INVALID_TYPE"
    PROTECTED_ENVIRONMENT = "PROTECTED_ENVIRONMENT"


class CareCompositionDemoError(ValueError):
    """Stable failure from the offline demonstration boundary."""

    def __init__(self, code: CareCompositionDemoCode) -> None:
        self.code = code
        super().__init__(code.value)


@dataclass(frozen=True, slots=True)
class SyntheticCareCompositionDemo:
    reconciliation: SyntheticSnapshotReconciliation
    replay: SyntheticCompositionReplay
    source_call_count: int


class _DeterministicStructuralSource:
    def __init__(
        self,
        *,
        descriptor: SyntheticEvidenceSourceDescriptor,
        completed_at: datetime,
    ) -> None:
        self.descriptor = descriptor
        self._completed_at = completed_at
        self.calls = 0

    def inspect(self, query: SyntheticEvidenceSourceQuery) -> SyntheticEvidenceSourceReceipt:
        self.calls += 1
        return SyntheticEvidenceSourceReceipt(
            query_id=query.query_id,
            query_fingerprint=synthetic_source_query_fingerprint(query),
            request_id=query.request_id,
            request_fingerprint=query.request_fingerprint,
            descriptor_fingerprint=query.descriptor_fingerprint,
            channel=query.channel,
            evidence_id=query.evidence_id,
            evidence_version=query.evidence_version,
            evidence_hash=query.evidence_hash,
            availability=query.availability,
            completed_at=self._completed_at,
        )


def _evidence(
    *,
    suffix: str,
    channel: EvidenceChannel,
    artifact_hash: str,
    availability: EvidenceAvailability,
) -> SyntheticEvidenceReference:
    return SyntheticEvidenceReference(
        evidence_id=f"syn_comp_evidence_{suffix}",
        channel=channel,
        evidence_version="engineering.v1",
        artifact_hash=artifact_hash,
        availability=availability,
        effective_at=_NOW - timedelta(minutes=2),
        observed_at=_NOW - timedelta(minutes=1),
    )


def _candidate(
    *,
    suffix: str,
    action: SyntheticActionCode,
    channel: EvidenceChannel,
    evidence_hash: str,
    reason: SyntheticReasonCode,
) -> SyntheticActionCandidate:
    return SyntheticActionCandidate(
        candidate_id=f"syn_comp_candidate_{suffix}",
        action=action,
        channel=channel,
        evidence_id=f"syn_comp_evidence_{suffix}",
        evidence_version="engineering.v1",
        evidence_hash=evidence_hash,
        reason_code=reason,
    )


def build_synthetic_care_composition_demo(
    *,
    environment: Environment,
    beta_availability: EvidenceAvailability = EvidenceAvailability.PRESENT_UNVERIFIED,
) -> SyntheticCareCompositionDemo:
    """Run the content-free P20 structural chain without selecting or executing care."""

    if type(environment) is not Environment:
        raise CareCompositionDemoError(CareCompositionDemoCode.INVALID_TYPE)
    if environment in _PROTECTED_ENVIRONMENTS:
        raise CareCompositionDemoError(CareCompositionDemoCode.PROTECTED_ENVIRONMENT)
    if type(beta_availability) is not EvidenceAvailability:
        raise CareCompositionDemoError(CareCompositionDemoCode.INVALID_TYPE)

    request = SyntheticCompositionRequest(
        request_id="syn_comp_request_alpha",
        snapshot_id="syn_comp_snapshot_alpha",
        snapshot_version="engineering.v1",
        snapshot_hash=_HASH_SNAPSHOT,
        evidence=(
            _evidence(
                suffix="alpha",
                channel=EvidenceChannel.SYNTHETIC_CHANNEL_ALPHA,
                artifact_hash=_HASH_ALPHA,
                availability=EvidenceAvailability.PRESENT_UNVERIFIED,
            ),
            _evidence(
                suffix="beta",
                channel=EvidenceChannel.SYNTHETIC_CHANNEL_BETA,
                artifact_hash=_HASH_BETA,
                availability=beta_availability,
            ),
        ),
        created_at=_NOW,
    )
    alpha_source = _DeterministicStructuralSource(
        descriptor=SyntheticEvidenceSourceDescriptor(
            source_id="syn_comp_source_alpha",
            source_version="engineering.v1",
            source_hash=_HASH_SOURCE_ALPHA,
            channel=EvidenceChannel.SYNTHETIC_CHANNEL_ALPHA,
        ),
        completed_at=_NOW + timedelta(seconds=1),
    )
    beta_source = _DeterministicStructuralSource(
        descriptor=SyntheticEvidenceSourceDescriptor(
            source_id="syn_comp_source_beta",
            source_version="engineering.v1",
            source_hash=_HASH_SOURCE_BETA,
            channel=EvidenceChannel.SYNTHETIC_CHANNEL_BETA,
        ),
        completed_at=_NOW + timedelta(seconds=1),
    )
    reconciliation = reconcile_synthetic_snapshot(
        request,
        sources={
            EvidenceChannel.SYNTHETIC_CHANNEL_ALPHA: alpha_source,
            EvidenceChannel.SYNTHETIC_CHANNEL_BETA: beta_source,
        },
        requested_at=_NOW,
        reconciled_at=_NOW + timedelta(seconds=2),
        environment=environment,
    )
    candidates = (
        _candidate(
            suffix="alpha",
            action=SyntheticActionCode.SYNTHETIC_ACTION_ALPHA,
            channel=EvidenceChannel.SYNTHETIC_CHANNEL_ALPHA,
            evidence_hash=_HASH_ALPHA,
            reason=SyntheticReasonCode.SYNTHETIC_REASON_ALPHA,
        ),
        _candidate(
            suffix="beta",
            action=SyntheticActionCode.SYNTHETIC_ACTION_BETA,
            channel=EvidenceChannel.SYNTHETIC_CHANNEL_BETA,
            evidence_hash=_HASH_BETA,
            reason=SyntheticReasonCode.SYNTHETIC_REASON_BETA,
        ),
    )
    replay = replay_synthetic_composition(
        reconciliation,
        candidates,
        evaluated_at=_NOW + timedelta(seconds=3),
        replayed_at=_NOW + timedelta(seconds=4),
        environment=environment,
    )
    return SyntheticCareCompositionDemo(
        reconciliation=reconciliation,
        replay=replay,
        source_call_count=alpha_source.calls + beta_source.calls,
    )


def _summary(
    demo: SyntheticCareCompositionDemo,
    *,
    environment: Environment,
) -> dict[str, object]:
    decision = demo.replay.decision
    return {
        "authority": decision.authority.value,
        "candidate_count": len(decision.candidates),
        "classification": decision.classification.value,
        "disposition": decision.disposition.value,
        "environment": environment.value,
        "reason": decision.reason.value,
        "reconciliation_fingerprint": demo.reconciliation.fingerprint,
        "replay_fingerprint": demo.replay.fingerprint,
        "request_fingerprint": demo.reconciliation.request.fingerprint,
        "snapshot_state": demo.reconciliation.state.value,
        "source_call_count": demo.source_call_count,
        "unavailable_channels": [channel.value for channel in decision.unavailable_channels],
        "verification": decision.verification.value,
    }


def main(arguments: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the offline engineering-synthetic care-composition replay."
    )
    parser.add_argument(
        "--environment",
        choices=[environment.value for environment in Environment],
        default=Environment.LOCAL.value,
    )
    parser.add_argument(
        "--beta-availability",
        choices=[availability.value for availability in EvidenceAvailability],
        default=EvidenceAvailability.PRESENT_UNVERIFIED.value,
    )
    parsed = parser.parse_args(arguments)
    environment = Environment(parsed.environment)
    beta_availability = EvidenceAvailability(parsed.beta_availability)
    try:
        demo = build_synthetic_care_composition_demo(
            environment=environment,
            beta_availability=beta_availability,
        )
    except CareCompositionDemoError as error:
        parser.exit(2, f"{error.code.value}\n")
    print(json.dumps(_summary(demo, environment=environment), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "CareCompositionDemoCode",
    "CareCompositionDemoError",
    "SyntheticCareCompositionDemo",
    "build_synthetic_care_composition_demo",
    "main",
]
