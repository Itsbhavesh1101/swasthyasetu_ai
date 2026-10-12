"""Stable public exports and explicit composition for the patient module."""

from collections.abc import Callable
from datetime import datetime
from typing import TYPE_CHECKING

from fastapi import APIRouter

from app.modules.patients.clinical import (
    AllergyRecord,
    ClinicalFact,
    ClinicalFactId,
    ClinicalTime,
    ClinicalValue,
    FactSupersession,
    FactType,
    InvalidFactSupersessionError,
    InvestigationRecord,
    MedicationRecord,
    MedicationStatus,
    Observation,
    Problem,
    ProblemStatus,
    ProcedureRecord,
    ReferenceRange,
    clinical_fact_label,
    supersede_fact,
)
from app.modules.patients.contracts import (
    CreatePatientCapability,
    FactCursor,
    FactPage,
    ListFactsCapability,
    ReadFactCapability,
    ReadPatientCapability,
)
from app.modules.patients.domain import (
    Patient,
    PatientDemographics,
    PatientId,
    PatientIdentifier,
    PatientStatus,
)
from app.shared.capabilities import CapabilityIdentifier, CapabilityKey
from app.shared.modules import ModuleId, ModuleManifest, ModuleRegistration
from app.shared.persistence import DatabaseRuntime

if TYPE_CHECKING:
    from app.modules.patients.application import PatientService

PATIENTS_CREATE = CapabilityKey[CreatePatientCapability](CapabilityIdentifier("patients.create"))
PATIENTS_READ = CapabilityKey[ReadPatientCapability](CapabilityIdentifier("patients.read"))
PATIENTS_FACT_READ = CapabilityKey[ReadFactCapability](CapabilityIdentifier("patients.fact.read"))
PATIENTS_FACTS_LIST = CapabilityKey[ListFactsCapability](
    CapabilityIdentifier("patients.facts.list")
)

PATIENTS_MANIFEST = ModuleManifest(
    module_id=ModuleId("patients"),
    version=1,
    provided_capabilities=frozenset(
        key.identifier
        for key in (PATIENTS_CREATE, PATIENTS_READ, PATIENTS_FACT_READ, PATIENTS_FACTS_LIST)
    ),
    api_prefixes=("/patients",),
    required_permissions=("patient:read:self", "patient:write:self"),
    data_ownership=("patients", "patient_demographics", "patient_identifiers", "clinical_facts"),
)


def build_patient_service(
    *, database: DatabaseRuntime | None, clock: Callable[[], datetime] | None = None
) -> "PatientService":
    from app.modules.patients.application import PatientService
    from app.modules.patients.infrastructure import (
        PostgresClinicalFactRepository,
        PostgresPatientRepository,
    )

    kwargs = {} if clock is None else {"clock": clock}
    return PatientService(
        database=database,
        patients=PostgresPatientRepository(),
        facts=PostgresClinicalFactRepository(),
        **kwargs,
    )


def build_patients_registration(*, service: "PatientService") -> ModuleRegistration[APIRouter]:
    from app.modules.patients.api import build_patients_router

    return ModuleRegistration(
        manifest=PATIENTS_MANIFEST,
        routers=(build_patients_router(creator=service, reader=service, facts=service),),
        capability_bindings=(
            PATIENTS_CREATE.bind(service),
            PATIENTS_READ.bind(service),
            PATIENTS_FACT_READ.bind(service),
            PATIENTS_FACTS_LIST.bind(service),
        ),
    )


__all__ = [
    "AllergyRecord",
    "ClinicalFact",
    "ClinicalFactId",
    "ClinicalTime",
    "ClinicalValue",
    "CreatePatientCapability",
    "FactSupersession",
    "FactType",
    "FactCursor",
    "FactPage",
    "InvestigationRecord",
    "InvalidFactSupersessionError",
    "MedicationRecord",
    "MedicationStatus",
    "Observation",
    "Patient",
    "PatientDemographics",
    "PatientId",
    "PatientIdentifier",
    "PatientStatus",
    "ListFactsCapability",
    "ReadFactCapability",
    "ReadPatientCapability",
    "Problem",
    "ProblemStatus",
    "ProcedureRecord",
    "ReferenceRange",
    "PATIENTS_CREATE",
    "PATIENTS_FACT_READ",
    "PATIENTS_FACTS_LIST",
    "PATIENTS_MANIFEST",
    "PATIENTS_READ",
    "build_patient_service",
    "build_patients_registration",
    "clinical_fact_label",
    "supersede_fact",
]
