"""One-way process-local kill switches for optional capabilities."""

from __future__ import annotations

from collections.abc import Sequence
from contextlib import suppress
from datetime import datetime
from threading import Lock

from app.resilience.contracts import (
    CapabilityControlState,
    CapabilitySwitchSnapshot,
    KillSwitchReason,
    OptionalCapability,
    ResilienceObserver,
)


class OptionalCapabilitySwitchboard:
    """Fail safe by default and allow only one-way process-local disablement."""

    def __init__(
        self,
        *,
        available: Sequence[OptionalCapability] = (),
        observer: ResilienceObserver | None = None,
    ) -> None:
        if any(not isinstance(item, OptionalCapability) for item in available):
            raise TypeError("available capabilities must be OptionalCapability values")
        if len(set(available)) != len(available):
            raise ValueError("available capabilities must be unique")
        self._available = frozenset(available)
        self._tripped: dict[OptionalCapability, CapabilitySwitchSnapshot] = {}
        self._observer = observer
        self._lock = Lock()

    def snapshot(self, capability: OptionalCapability) -> CapabilitySwitchSnapshot:
        """Return current state without implying authorization or clinical approval."""
        if not isinstance(capability, OptionalCapability):
            raise TypeError("capability must be an OptionalCapability")
        with self._lock:
            existing = self._tripped.get(capability)
            if existing is not None:
                return existing
            state = (
                CapabilityControlState.AVAILABLE
                if capability in self._available
                else CapabilityControlState.DISABLED_BY_DEFAULT
            )
            return CapabilitySwitchSnapshot(capability=capability, state=state)

    def trip(
        self,
        capability: OptionalCapability,
        *,
        reason: KillSwitchReason,
        tripped_at: datetime,
    ) -> CapabilitySwitchSnapshot:
        """Trip a switch idempotently; this foundation intentionally has no reset path."""
        if not isinstance(capability, OptionalCapability):
            raise TypeError("capability must be an OptionalCapability")
        candidate = CapabilitySwitchSnapshot(
            capability=capability,
            state=CapabilityControlState.TRIPPED,
            reason=reason,
            tripped_at=tripped_at,
        )
        with self._lock:
            snapshot = self._tripped.setdefault(capability, candidate)
        if snapshot is candidate and self._observer is not None:
            with suppress(Exception):
                self._observer.record_switch(snapshot)
        return snapshot
