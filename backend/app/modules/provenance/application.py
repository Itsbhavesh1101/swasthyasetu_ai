"""Public-interface composition for provenance and longitudinal timelines."""

from datetime import datetime
from uuid import UUID

from app.modules.encounters.contracts import EncounterCursor, ListEncountersCapability
from app.modules.patients.contracts import (
    FactCursor,
    ListFactsCapability,
    ReadFactCapability,
    ReadPatientCapability,
)
from app.modules.provenance.contracts import (
    TimelineCursor,
    TimelineEntry,
    TimelineEntryType,
    TimelinePage,
)
from app.modules.provenance.domain import FactProvenance
from app.shared.errors import ApplicationError, ErrorCode
from app.shared.types import OpaqueId

_MIN_ID = OpaqueId(UUID(int=0))
_MAX_ID = OpaqueId(UUID(int=(1 << 128) - 1))


class ProvenanceTimelineService:
    def __init__(
        self,
        *,
        patients: ReadPatientCapability,
        fact_reader: ReadFactCapability,
        facts: ListFactsCapability,
        encounters: ListEncountersCapability,
    ) -> None:
        self._patients = patients
        self._fact_reader = fact_reader
        self._facts = facts
        self._encounters = encounters

    async def read_provenance(self, fact_id: OpaqueId) -> FactProvenance:
        return (await self._fact_reader.get_fact(fact_id)).provenance

    async def get_timeline(
        self,
        *,
        patient_id: OpaqueId,
        entry_type: TimelineEntryType | None = None,
        from_time: datetime | None = None,
        to_time: datetime | None = None,
        cursor: TimelineCursor | None = None,
        limit: int = 50,
    ) -> TimelinePage:
        if not 1 <= limit <= 100 or (
            from_time is not None and to_time is not None and from_time > to_time
        ):
            raise ApplicationError(
                code=ErrorCode.VALIDATION_ERROR, message="The timeline query is invalid."
            )
        await self._patients.get_patient(patient_id)
        fact_cursor = None
        encounter_cursor = None
        if cursor is not None:
            fact_cursor = FactCursor(
                cursor.occurred_at,
                cursor.entry_id
                if cursor.entry_type is TimelineEntryType.CLINICAL_FACT
                else _MAX_ID,
            )
            encounter_cursor = EncounterCursor(
                cursor.occurred_at,
                cursor.entry_id if cursor.entry_type is TimelineEntryType.ENCOUNTER else _MIN_ID,
            )

        entries: list[TimelineEntry] = []
        source_has_more = False
        if entry_type in (None, TimelineEntryType.CLINICAL_FACT):
            fact_page = await self._facts.list_facts(
                patient_id=patient_id,
                from_time=from_time,
                to_time=to_time,
                cursor=fact_cursor,
                limit=limit,
            )
            entries.extend(
                TimelineEntry(
                    entry_id=fact.fact_id,
                    entry_type=TimelineEntryType.CLINICAL_FACT,
                    occurred_at=fact.effective_time or fact.recorded_at,
                    fact=fact,
                )
                for fact in fact_page.items
            )
            source_has_more = source_has_more or fact_page.has_more
        if entry_type in (None, TimelineEntryType.ENCOUNTER):
            encounter_page = await self._encounters.list_for_patient(
                patient_id=patient_id,
                from_time=from_time,
                to_time=to_time,
                cursor=encounter_cursor,
                limit=limit,
            )
            entries.extend(
                TimelineEntry(
                    entry_id=encounter.encounter_id,
                    entry_type=TimelineEntryType.ENCOUNTER,
                    occurred_at=encounter.started_at,
                    encounter=encounter,
                )
                for encounter in encounter_page.items
            )
            source_has_more = source_has_more or encounter_page.has_more
        entries.sort(key=lambda item: (item.entry_type.value, item.entry_id.value))
        entries.sort(key=lambda item: item.occurred_at, reverse=True)
        return TimelinePage(
            items=tuple(entries[:limit]),
            has_more=source_has_more or len(entries) > limit,
        )
