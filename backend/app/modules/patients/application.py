"""Framework-independent patient application service."""

from collections.abc import Callable
from datetime import UTC, datetime

from app.modules.patients.clinical import ClinicalFact, FactType
from app.modules.patients.contracts import (
    ClinicalFactRepository,
    FactCursor,
    FactPage,
    PatientAlreadyExistsError,
    PatientRepository,
)
from app.modules.patients.domain import Patient, PatientDemographics, PatientStatus
from app.modules.provenance.domain import VerificationState
from app.shared.errors import ApplicationError, DependencyError, ErrorCode
from app.shared.persistence import DatabaseRuntime
from app.shared.types import OpaqueId, utc_now


class PatientService:
    def __init__(
        self,
        *,
        database: DatabaseRuntime | None,
        patients: PatientRepository,
        facts: ClinicalFactRepository,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._database = database
        self._patients = patients
        self._facts = facts
        self._clock = clock

    async def create_patient(
        self,
        *,
        patient_id: OpaqueId,
        preferred_language: str | None,
        demographics: PatientDemographics | None,
    ) -> Patient:
        database = self._require_database()
        now = self._now()
        patient = Patient(
            patient_id=patient_id,
            status=PatientStatus.ACTIVE,
            created_at=now,
            updated_at=now,
            preferred_language=preferred_language,
            demographics=demographics,
        )
        try:
            async with database.transaction() as transaction:
                if await self._patients.get(transaction, patient_id) is not None:
                    raise self._conflict()
                await self._patients.add(transaction, patient)
        except PatientAlreadyExistsError as exc:
            raise self._conflict(exc) from exc
        return patient

    async def get_patient(self, patient_id: OpaqueId) -> Patient:
        database = self._require_database()
        async with database.transaction() as transaction:
            patient = await self._patients.get(transaction, patient_id)
        if patient is None:
            raise ApplicationError(
                code=ErrorCode.RESOURCE_NOT_FOUND,
                message="The requested patient was not found.",
            )
        return patient

    async def get_fact(self, fact_id: OpaqueId) -> ClinicalFact:
        database = self._require_database()
        async with database.transaction() as transaction:
            fact = await self._facts.get(transaction, fact_id)
        if fact is None:
            raise ApplicationError(
                code=ErrorCode.RESOURCE_NOT_FOUND,
                message="The requested clinical fact was not found.",
            )
        return fact

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
    ) -> FactPage:
        if not 1 <= limit <= 100:
            raise ApplicationError(
                code=ErrorCode.VALIDATION_ERROR, message="The page limit is invalid."
            )
        database = self._require_database()
        async with database.transaction() as transaction:
            if await self._patients.get(transaction, patient_id) is None:
                raise ApplicationError(
                    code=ErrorCode.RESOURCE_NOT_FOUND,
                    message="The requested patient was not found.",
                )
            items = await self._facts.list_for_patient(
                transaction,
                patient_id=patient_id,
                fact_type=fact_type,
                verification_state=verification_state,
                from_time=from_time,
                to_time=to_time,
                cursor=cursor,
                limit=limit + 1,
            )
        return FactPage(items=items[:limit], has_more=len(items) > limit)

    def _require_database(self) -> DatabaseRuntime:
        if self._database is None:
            raise DependencyError(
                code=ErrorCode.DEPENDENCY_UNAVAILABLE,
                message="Patient persistence is temporarily unavailable.",
            )
        return self._database

    def _now(self) -> datetime:
        value = self._clock()
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("patient clock must be timezone-aware")
        return value.astimezone(UTC)

    @staticmethod
    def _conflict(cause: Exception | None = None) -> ApplicationError:
        return ApplicationError(
            code=ErrorCode.RESOURCE_CONFLICT,
            message="A patient already exists for this authenticated subject.",
            cause=cause,
        )
