"""Stable public exports for the encounter domain."""

from app.modules.encounters.domain import (
    Encounter,
    EncounterId,
    EncounterStatus,
    EncounterType,
    InvalidEncounterTransitionError,
)

__all__ = [
    "Encounter",
    "EncounterId",
    "EncounterStatus",
    "EncounterType",
    "InvalidEncounterTransitionError",
]
