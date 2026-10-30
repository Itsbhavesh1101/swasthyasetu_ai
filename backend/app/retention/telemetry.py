"""Bounded, identifier-free purge telemetry."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from opentelemetry.metrics import Counter, Meter

from app.retention.contracts import PurgeTargetOutcome, PurgeTargetReceipt

PURGE_TARGET_OUTCOMES: Final = "swasthyasetu.retention.purge.targets"
PURGE_FAILURES: Final = "swasthyasetu.retention.purge.failures"


@dataclass(frozen=True, slots=True)
class PurgeTelemetry:
    """Record only closed, bounded purge outcome attributes."""

    target_outcomes: Counter
    failures: Counter

    @classmethod
    def from_meter(cls, meter: Meter) -> PurgeTelemetry:
        return cls(
            target_outcomes=meter.create_counter(
                PURGE_TARGET_OUTCOMES,
                unit="{target}",
                description="Retention purge target outcomes",
            ),
            failures=meter.create_counter(
                PURGE_FAILURES,
                unit="{failure}",
                description="Retention purge target failures",
            ),
        )

    def record(self, receipt: PurgeTargetReceipt) -> None:
        attributes = {
            "target.kind": receipt.target.identity.kind.value,
            "purge.outcome": receipt.outcome.value,
        }
        self.target_outcomes.add(1, attributes)
        if receipt.outcome is PurgeTargetOutcome.FAILED:
            self.failures.add(
                1,
                {
                    "target.kind": receipt.target.identity.kind.value,
                    "error.code": receipt.error_code or "PURGE_TARGET_FAILED",
                },
            )
