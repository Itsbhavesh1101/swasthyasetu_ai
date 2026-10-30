"""Deterministic restore-resurrection reconciliation contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from app.retention.contracts import (
    PolicyCode,
    PolicyVersion,
    PurgeTargetIdentity,
    _utc,
)


class RestoreDisposition(StrEnum):
    """Safe disposition for data observed after restore."""

    REBLOCK_AND_REPURGE = "REBLOCK_AND_REPURGE"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"


def _generation(name: str, value: int) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{name} must be an integer")
    if value <= 0:
        raise ValueError(f"{name} must be positive")
    return value


@dataclass(frozen=True, slots=True)
class PurgeTombstone:
    """Content-free proof that a target generation was purged."""

    identity: PurgeTargetIdentity = field(repr=False)
    purged_through_generation: int
    purged_at: datetime
    policy_code: PolicyCode
    policy_version: PolicyVersion

    def __post_init__(self) -> None:
        if not isinstance(self.identity, PurgeTargetIdentity):
            raise TypeError("tombstone identity must be a PurgeTargetIdentity")
        object.__setattr__(
            self,
            "purged_through_generation",
            _generation("purged_through_generation", self.purged_through_generation),
        )
        object.__setattr__(self, "purged_at", _utc("purged_at", self.purged_at))
        if not isinstance(self.policy_code, PolicyCode):
            raise TypeError("policy_code must be a PolicyCode")
        if not isinstance(self.policy_version, PolicyVersion):
            raise TypeError("policy_version must be a PolicyVersion")


@dataclass(frozen=True, slots=True)
class RestoredTarget:
    """Content-free target generation observed after a restore."""

    identity: PurgeTargetIdentity = field(repr=False)
    generation: int
    restored_at: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.identity, PurgeTargetIdentity):
            raise TypeError("restored identity must be a PurgeTargetIdentity")
        object.__setattr__(self, "generation", _generation("generation", self.generation))
        object.__setattr__(self, "restored_at", _utc("restored_at", self.restored_at))


@dataclass(frozen=True, slots=True)
class RestoreDecision:
    """Deterministic safe decision; it never authorizes restored data for use."""

    target: RestoredTarget = field(repr=False)
    disposition: RestoreDisposition

    def __post_init__(self) -> None:
        if not isinstance(self.target, RestoredTarget):
            raise TypeError("restore decision target must be a RestoredTarget")
        if not isinstance(self.disposition, RestoreDisposition):
            raise TypeError("restore disposition must be a RestoreDisposition")


class RestoreReconciler:
    """Classify restored targets against immutable tombstones."""

    def __init__(self, *, tombstones: tuple[PurgeTombstone, ...]) -> None:
        if not isinstance(tombstones, tuple) or any(
            not isinstance(item, PurgeTombstone) for item in tombstones
        ):
            raise TypeError("tombstones must be a tuple of PurgeTombstone values")
        by_identity = {item.identity: item for item in tombstones}
        if len(by_identity) != len(tombstones):
            raise ValueError("tombstones must have unique target identities")
        self._tombstones = by_identity

    def classify(self, target: RestoredTarget) -> RestoreDecision:
        if not isinstance(target, RestoredTarget):
            raise TypeError("target must be a RestoredTarget")
        tombstone = self._tombstones.get(target.identity)
        disposition = (
            RestoreDisposition.REBLOCK_AND_REPURGE
            if tombstone is not None and target.generation <= tombstone.purged_through_generation
            else RestoreDisposition.REVIEW_REQUIRED
        )
        return RestoreDecision(target=target, disposition=disposition)
