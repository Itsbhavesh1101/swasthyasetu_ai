"""Bounded identifier-free telemetry for optional capability resilience."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from opentelemetry.metrics import Counter, Meter

from app.resilience.contracts import CapabilitySwitchSnapshot, DependencyOutcome

OPTIONAL_DEPENDENCY_OUTCOMES: Final = "swasthyasetu.resilience.optional_dependency.outcomes"
KILL_SWITCH_TRIPS: Final = "swasthyasetu.resilience.kill_switch.trips"


@dataclass(frozen=True, slots=True)
class ResilienceTelemetry:
    """Record only closed capability, state, reason, and failure attributes."""

    dependency_outcomes: Counter
    switch_trips: Counter

    @classmethod
    def from_meter(cls, meter: Meter) -> ResilienceTelemetry:
        return cls(
            dependency_outcomes=meter.create_counter(
                OPTIONAL_DEPENDENCY_OUTCOMES,
                unit="{outcome}",
                description="Optional dependency execution outcomes",
            ),
            switch_trips=meter.create_counter(
                KILL_SWITCH_TRIPS,
                unit="{trip}",
                description="Process-local optional capability kill-switch trips",
            ),
        )

    def record_switch(self, snapshot: CapabilitySwitchSnapshot) -> None:
        self.switch_trips.add(
            1,
            {
                "capability": snapshot.capability.value,
                "switch.state": snapshot.state.value,
                "switch.reason": snapshot.reason.value if snapshot.reason else "NONE",
            },
        )

    def record_outcome(self, outcome: DependencyOutcome[object]) -> None:
        self.dependency_outcomes.add(
            1,
            {
                "capability": outcome.capability.value,
                "outcome.state": outcome.state.value,
                "failure.code": outcome.failure_code.value if outcome.failure_code else "NONE",
            },
        )
