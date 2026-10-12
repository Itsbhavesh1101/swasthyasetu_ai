"""Public patient application and persistence contracts."""

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.patients.clinical import ClinicalFact, FactType
from app.modules.patients.domain import Patient, PatientDemographics
from app.modules.provenance.domain import VerificationState
from app.shared.types import OpaqueId


class PatientAlreadyExistsError(RuntimeError):
    """Repository-level uniqueness conflict without persistence leakage."""


@dataclass(frozen=True, slots=True)
class FactCursor:
    occurred_at: datetime
    fact_id: OpaqueId


@dataclass(frozen=True, slots=True)
class FactPage:
    items: tuple[ClinicalFact, ...]
    has_more: bool


class CreatePatientCapability(Protocol):
    async def create_patient(
        self,
        *,
        patient_id: OpaqueId,
        preferred_language: str | None,
        demographics: PatientDemographics | None,
    ) -> Patient: ...


class ReadPatientCapability(Protocol):
    async def get_patient(self, patient_id: OpaqueId) -> Patient: ...


class ReadFactCapability(Protocol):
    async def get_fact(self, fact_id: OpaqueId) -> ClinicalFact: ...


class ListFactsCapability(Protocol):
    async def list_facts(
        self,
        *,
        patient_id: OpaqueId,
        fact_type: FactType | None = None,
        verification_state: VerificationState | None = None,
        from_time: datetime | None = None,
        to_time: datetime | None = None,
        cursor: FactCursor | None = None,
        limit: int = 50,
    ) -> FactPage: ...


class PatientRepository(Protocol):
    async def add(self, session: AsyncSession, patient: Patient) -> object: ...
    async def get(self, session: AsyncSession, patient_id: OpaqueId) -> Patient | None: ...


class ClinicalFactRepository(Protocol):
    async def get(self, session: AsyncSession, fact_id: OpaqueId) -> ClinicalFact | None: ...
    async def list_for_patient(
        self,
        session: AsyncSession,
        *,
        patient_id: OpaqueId,
        fact_type: FactType | None,
        verification_state: VerificationState | None,
        from_time: datetime | None,
        to_time: datetime | None,
        cursor: FactCursor | None,
        limit: int,
    ) -> tuple[ClinicalFact, ...]: ...
