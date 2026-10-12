"""Stable public exports and explicit composition for provenance."""

from typing import TYPE_CHECKING

from fastapi import APIRouter

from app.modules.encounters.public import ENCOUNTERS_LIST, ListEncountersCapability
from app.modules.patients.public import (
    PATIENTS_FACT_READ,
    PATIENTS_FACTS_LIST,
    PATIENTS_READ,
    ListFactsCapability,
    ReadFactCapability,
    ReadPatientCapability,
)
from app.modules.provenance.contracts import (
    ReadProvenanceCapability,
    ReadTimelineCapability,
    TimelineCursor,
    TimelineEntry,
    TimelineEntryType,
    TimelinePage,
)
from app.modules.provenance.domain import (
    FactProvenance,
    ProvenanceSourceType,
    VerificationState,
)
from app.shared.capabilities import CapabilityIdentifier, CapabilityKey
from app.shared.modules import ModuleId, ModuleManifest, ModuleRegistration

if TYPE_CHECKING:
    from app.modules.provenance.application import ProvenanceTimelineService

PROVENANCE_READ = CapabilityKey[ReadProvenanceCapability](CapabilityIdentifier("provenance.read"))
PATIENTS_TIMELINE = CapabilityKey[ReadTimelineCapability](CapabilityIdentifier("patients.timeline"))

PROVENANCE_MANIFEST = ModuleManifest(
    module_id=ModuleId("provenance"),
    version=1,
    provided_capabilities=frozenset({PROVENANCE_READ.identifier, PATIENTS_TIMELINE.identifier}),
    required_capabilities=frozenset(
        {
            PATIENTS_READ.identifier,
            PATIENTS_FACT_READ.identifier,
            PATIENTS_FACTS_LIST.identifier,
            ENCOUNTERS_LIST.identifier,
        }
    ),
    api_prefixes=("/patients/{patient_id}/timeline",),
)


def build_provenance_service(
    *,
    patients: ReadPatientCapability,
    fact_reader: ReadFactCapability,
    facts: ListFactsCapability,
    encounters: ListEncountersCapability,
) -> "ProvenanceTimelineService":
    from app.modules.provenance.application import ProvenanceTimelineService

    return ProvenanceTimelineService(
        patients=patients, fact_reader=fact_reader, facts=facts, encounters=encounters
    )


def build_provenance_registration(
    *, service: "ProvenanceTimelineService"
) -> ModuleRegistration[APIRouter]:
    from app.modules.provenance.api import build_timeline_router

    return ModuleRegistration(
        manifest=PROVENANCE_MANIFEST,
        routers=(build_timeline_router(timeline=service),),
        capability_bindings=(PROVENANCE_READ.bind(service), PATIENTS_TIMELINE.bind(service)),
    )


__all__ = [
    "FactProvenance",
    "PATIENTS_TIMELINE",
    "PROVENANCE_MANIFEST",
    "PROVENANCE_READ",
    "ProvenanceSourceType",
    "ReadProvenanceCapability",
    "ReadTimelineCapability",
    "TimelineCursor",
    "TimelineEntry",
    "TimelineEntryType",
    "TimelinePage",
    "VerificationState",
    "build_provenance_registration",
    "build_provenance_service",
]
