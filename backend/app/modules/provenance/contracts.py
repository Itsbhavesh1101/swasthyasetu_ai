"""Public provenance and longitudinal timeline contracts."""

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Protocol

from app.modules.encounters.domain import Encounter
from app.modules.patients.clinical import ClinicalFact
from app.modules.provenance.domain import FactProvenance
from app.shared.types import OpaqueId


class TimelineEntryType(StrEnum):
    CLINICAL_FACT = "CLINICAL_FACT"
    ENCOUNTER = "ENCOUNTER"


@dataclass(frozen=True, slots=True)
class TimelineEntry:
    entry_id: OpaqueId
    entry_type: TimelineEntryType
    occurred_at: datetime
    encounter: Encounter | None = None
    fact: ClinicalFact | None = None

    def __post_init__(self) -> None:
        offset = self.occurred_at.utcoffset()
        if self.occurred_at.tzinfo is None or offset is None:
            raise ValueError("occurred_at must be timezone-aware")
        if self.entry_type is TimelineEntryType.ENCOUNTER:
            if self.encounter is None or self.fact is not None:
                raise ValueError("encounter timeline entry payload is invalid")
        elif self.fact is None or self.encounter is not None:
            raise ValueError("clinical-fact timeline entry payload is invalid")
        object.__setattr__(self, "occurred_at", self.occurred_at.astimezone(UTC))


@dataclass(frozen=True, slots=True)
class TimelineCursor:
    occurred_at: datetime
    entry_type: TimelineEntryType
    entry_id: OpaqueId


@dataclass(frozen=True, slots=True)
class TimelinePage:
    items: tuple[TimelineEntry, ...]
    has_more: bool


class ReadProvenanceCapability(Protocol):
    async def read_provenance(self, fact_id: OpaqueId) -> FactProvenance: ...


class ReadTimelineCapability(Protocol):
    async def get_timeline(
        self,
        *,
        patient_id: OpaqueId,
        entry_type: TimelineEntryType | None = None,
        from_time: datetime | None = None,
        to_time: datetime | None = None,
        cursor: TimelineCursor | None = None,
        limit: int = 50,
    ) -> TimelinePage: ...
