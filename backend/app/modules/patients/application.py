"""Framework-independent patient application service."""

from collections.abc import Callable
from datetime import UTC, datetime

from app.modules.patients.clinical import (
    ClinicalFact,
    ClinicalValue,
    FactSupersession,
    FactType,
    InvalidFactSupersessionError,
    supersede_fact,
)
from app.modules.patients.contracts import (
    ClinicalFactRepository,
    FactCursor,
    FactPage,
    PatientAlreadyExistsError,
    PatientProfileConflictError,
    PatientRepository,
)
from app.modules.patients.domain import Patient, PatientDemographics, PatientStatus
from app.modules.provenance.domain import FactProvenance, ProvenanceSourceType, VerificationState
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

    async def update_profile(
        self,
        *,
        patient_id: OpaqueId,
        expected_updated_at: datetime,
        preferred_language: str | None,
        demographics: PatientDemographics | None,
    ) -> Patient:
        database = self._require_database()
        expected = self._normalize_time("expected_updated_at", expected_updated_at)
        now = self._now()
        async with database.transaction() as transaction:
            patient = await self._patients.get(transaction, patient_id)
            if patient is None or patient.updated_at != expected:
                raise self._stale_profile()
            updated = Patient(
                patient_id=patient.patient_id,
                status=patient.status,
                created_at=patient.created_at,
                updated_at=now,
                preferred_language=preferred_language,
                demographics=demographics,
                identifiers=patient.identifiers,
            )
            try:
                return await self._patients.save(
                    transaction,
                    updated,
                    expected_updated_at=expected,
                )
            except PatientProfileConflictError as exc:
                raise self._stale_profile() from exc

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

    async def add_patient_fact(
        self,
        *,
        patient_id: OpaqueId,
        actor_id: OpaqueId,
        fact_type: FactType,
        value: ClinicalValue,
        effective_time: datetime | None,
    ) -> ClinicalFact:
        database = self._require_database()
        now = self._now()
        fact = self._patient_fact(
            patient_id=patient_id,
            actor_id=actor_id,
            fact_type=fact_type,
            value=value,
            effective_time=effective_time,
            now=now,
        )
        async with database.transaction() as transaction:
            if await self._patients.get(transaction, patient_id) is None:
                raise self._fact_conflict()
            await self._facts.add(transaction, fact)
        return fact

    async def supersede_patient_fact(
        self,
        *,
        patient_id: OpaqueId,
        actor_id: OpaqueId,
        expected_current_id: OpaqueId,
        fact_type: FactType,
        value: ClinicalValue,
        effective_time: datetime | None,
    ) -> FactSupersession:
        database = self._require_database()
        now = self._now()
        replacement = self._patient_fact(
            patient_id=patient_id,
            actor_id=actor_id,
            fact_type=fact_type,
            value=value,
            effective_time=effective_time,
            now=now,
        )
        async with database.transaction() as transaction:
            existing = await self._facts.get(transaction, expected_current_id)
            if existing is None or existing.patient_id != patient_id:
                raise self._fact_conflict()
            try:
                requested = supersede_fact(existing, replacement)
                return await self._facts.persist_supersession(transaction, requested)
            except (InvalidFactSupersessionError, LookupError) as exc:
                raise self._fact_conflict(exc) from exc

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
    def _normalize_time(name: str, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError(f"{name} must be timezone-aware")
        return value.astimezone(UTC)

    @staticmethod
    def _stale_profile() -> ApplicationError:
        return ApplicationError(
            code=ErrorCode.RESOURCE_CONFLICT,
            message="The patient profile changed or is unavailable. Reload and try again.",
        )

    @staticmethod
    def _patient_fact(
        *,
        patient_id: OpaqueId,
        actor_id: OpaqueId,
        fact_type: FactType,
        value: ClinicalValue,
        effective_time: datetime | None,
        now: datetime,
    ) -> ClinicalFact:
        if value.verification_state is not VerificationState.PATIENT_CONFIRMED:
            raise ValueError("patient-entered facts must be patient-confirmed")
        normalized_effective = (
            None
            if effective_time is None
            else PatientService._normalize_time("effective_time", effective_time)
        )
        return ClinicalFact(
            fact_id=OpaqueId.new(),
            patient_id=patient_id,
            encounter_id=None,
            fact_type=fact_type,
            value=value,
            recorded_at=now,
            effective_time=normalized_effective,
            verification_state=VerificationState.PATIENT_CONFIRMED,
            provenance=FactProvenance(
                source_type=ProvenanceSourceType.PATIENT_REPORT,
                created_at=now,
                created_by=actor_id,
            ),
        )

    @staticmethod
    def _fact_conflict(cause: Exception | None = None) -> ApplicationError:
        return ApplicationError(
            code=ErrorCode.RESOURCE_CONFLICT,
            message="The medical-history entry changed or is unavailable. Reload and try again.",
            cause=cause,
        )

    @staticmethod
    def _conflict(cause: Exception | None = None) -> ApplicationError:
        return ApplicationError(
            code=ErrorCode.RESOURCE_CONFLICT,
            message="A patient already exists for this authenticated subject.",
            cause=cause,
        )
