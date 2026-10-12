"""Framework-independent encounter entity and lifecycle."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import UTC, datetime
from enum import StrEnum

from app.shared.types import OpaqueId

EncounterId = OpaqueId


class EncounterType(StrEnum):
    """Canonical encounter purposes."""

    GENERAL_INTAKE = "GENERAL_INTAKE"
    MENTAL_HEALTH = "MENTAL_HEALTH"
    KIOSK_INTAKE = "KIOSK_INTAKE"
    CLINICIAN_REVIEW = "CLINICIAN_REVIEW"
    DOCUMENT_REVIEW = "DOCUMENT_REVIEW"
    RESEARCH_ONLY = "RESEARCH_ONLY"


class EncounterStatus(StrEnum):
    """Canonical encounter lifecycle states."""

    CREATED = "CREATED"
    IN_PROGRESS = "IN_PROGRESS"
    AWAITING_REVIEW = "AWAITING_REVIEW"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"
    CANCELLED = "CANCELLED"


class InvalidEncounterTransitionError(ValueError):
    """Raised when an encounter lifecycle transition is not allowed."""


_TRANSITIONS: dict[EncounterStatus, frozenset[EncounterStatus]] = {
    EncounterStatus.CREATED: frozenset(
        {
            EncounterStatus.IN_PROGRESS,
            EncounterStatus.ABANDONED,
            EncounterStatus.CANCELLED,
        }
    ),
    EncounterStatus.IN_PROGRESS: frozenset(
        {
            EncounterStatus.AWAITING_REVIEW,
            EncounterStatus.COMPLETED,
            EncounterStatus.ABANDONED,
            EncounterStatus.CANCELLED,
        }
    ),
    EncounterStatus.AWAITING_REVIEW: frozenset(
        {
            EncounterStatus.IN_PROGRESS,
            EncounterStatus.COMPLETED,
            EncounterStatus.ABANDONED,
            EncounterStatus.CANCELLED,
        }
    ),
    EncounterStatus.COMPLETED: frozenset(),
    EncounterStatus.ABANDONED: frozenset(),
    EncounterStatus.CANCELLED: frozenset(),
}


def _normalize_utc(name: str, value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value.astimezone(UTC)


@dataclass(frozen=True, slots=True)
class Encounter:
    """A session-bound care episode with an explicit immutable lifecycle."""

    encounter_id: EncounterId
    patient_id: OpaqueId | None
    session_id: OpaqueId
    encounter_type: EncounterType
    status: EncounterStatus
    started_at: datetime
    completed_at: datetime | None = None
    institution_id: OpaqueId | None = None
    language_context: str | None = None
    created_by: OpaqueId | None = None

    def __post_init__(self) -> None:
        started_at = _normalize_utc("started_at", self.started_at)
        completed_at = (
            None if self.completed_at is None else _normalize_utc("completed_at", self.completed_at)
        )
        if self.status is EncounterStatus.COMPLETED:
            if completed_at is None:
                raise ValueError("completed_at is required for COMPLETED encounter")
            if completed_at < started_at:
                raise ValueError("completed_at must not precede started_at")
        elif completed_at is not None:
            raise ValueError("completed_at is allowed only for a COMPLETED encounter")
        if self.language_context is not None and (
            not self.language_context.strip()
            or self.language_context != self.language_context.strip()
            or len(self.language_context) > 256
        ):
            raise ValueError("language_context must be non-blank, trimmed, and bounded")
        object.__setattr__(self, "started_at", started_at)
        object.__setattr__(self, "completed_at", completed_at)

    def can_transition_to(self, target: EncounterStatus) -> bool:
        """Return whether the canonical lifecycle permits ``target``."""
        return target in _TRANSITIONS[self.status]

    def transition_to(self, target: EncounterStatus, *, at: datetime | None = None) -> Encounter:
        """Return a transitioned copy or fail without mutating this encounter."""
        if not self.can_transition_to(target):
            raise InvalidEncounterTransitionError(
                f"encounter cannot transition from {self.status} to {target}"
            )
        if target is EncounterStatus.COMPLETED:
            if at is None:
                raise ValueError("completed_at is required for COMPLETED encounter")
            completed_at = _normalize_utc("completed_at", at)
            if completed_at < self.started_at:
                raise ValueError("completed_at must not precede started_at")
            return replace(self, status=target, completed_at=completed_at)
        if at is not None:
            raise ValueError("a transition timestamp is accepted only for COMPLETED")
        return replace(self, status=target, completed_at=None)
