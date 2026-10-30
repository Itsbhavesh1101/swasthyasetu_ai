"""Safe-off optional dependency resilience engineering foundation."""

from app.resilience.contracts import (
    CapabilityControlState,
    CapabilitySwitchSnapshot,
    DependencyFailure,
    DependencyFailureKind,
    DependencyOutcome,
    DependencyOutcomeState,
    KillSwitchReason,
    OptionalCapability,
    ResilienceFailureCode,
    ResilienceObserver,
    RetryPolicy,
)
from app.resilience.executor import OptionalDependencyExecutor
from app.resilience.switchboard import OptionalCapabilitySwitchboard
from app.resilience.telemetry import (
    KILL_SWITCH_TRIPS,
    OPTIONAL_DEPENDENCY_OUTCOMES,
    ResilienceTelemetry,
)

__all__ = [
    "KILL_SWITCH_TRIPS",
    "OPTIONAL_DEPENDENCY_OUTCOMES",
    "CapabilityControlState",
    "CapabilitySwitchSnapshot",
    "DependencyFailure",
    "DependencyFailureKind",
    "DependencyOutcome",
    "DependencyOutcomeState",
    "KillSwitchReason",
    "OptionalCapability",
    "OptionalCapabilitySwitchboard",
    "OptionalDependencyExecutor",
    "ResilienceFailureCode",
    "ResilienceObserver",
    "ResilienceTelemetry",
    "RetryPolicy",
]
