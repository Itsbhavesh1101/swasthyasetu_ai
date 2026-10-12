"""Framework-independent encounter application service."""

from collections.abc import Callable
from datetime import UTC, datetime

from app.modules.encounters.contracts import (
    EncounterCursor,
    EncounterPage,
    EncounterRepository,
    PatientReader,
    StaleEncounterWriteError,
)
from app.modules.encounters.domain import (
    Encounter,
    EncounterStatus,
    EncounterType,
    InvalidEncounterTransitionError,
)
from app.modules.sessions.domain import Session, SessionType
from app.shared.errors import ApplicationError, DependencyError, ErrorCode
from app.shared.persistence import DatabaseRuntime
from app.shared.types import OpaqueId, utc_now


class EncounterService:
    _HTTP_TYPES = frozenset(
        {EncounterType.GENERAL_INTAKE, EncounterType.MENTAL_HEALTH, EncounterType.KIOSK_INTAKE}
    )

    def __init__(
        self,
        *,
        database: DatabaseRuntime | None,
        repository: EncounterRepository,
        patients: PatientReader,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._database = database
        self._repository = repository
        self._patients = patients
        self._clock = clock

    async def create_encounter(
        self,
        *,
        session: Session,
        patient_id: OpaqueId | None,
        encounter_type: EncounterType,
        created_by: OpaqueId | None,
    ) -> Encounter:
        if encounter_type not in self._HTTP_TYPES or not self._compatible(
            session.session_type, encounter_type
        ):
            raise ApplicationError(
                code=ErrorCode.VALIDATION_ERROR,
                message="The encounter type is not available for this session.",
            )
        if patient_id is not None:
            await self._patients.get_patient(patient_id)
        elif created_by is not None:
            raise ApplicationError(
                code=ErrorCode.AUTHORIZATION_DENIED,
                message="Pseudonymous encounters cannot claim an authenticated creator.",
            )
        now = self._now()
        encounter = Encounter(
            encounter_id=OpaqueId.new(),
            patient_id=patient_id,
            session_id=session.session_id,
            encounter_type=encounter_type,
            status=EncounterStatus.CREATED,
            started_at=now,
            language_context=session.language_preference,
            created_by=created_by if patient_id is not None else None,
        )
        database = self._require_database()
        async with database.transaction() as transaction:
            await self._repository.add(transaction, encounter)
        return encounter

    async def get_encounter(self, encounter_id: OpaqueId) -> Encounter:
        database = self._require_database()
        async with database.transaction() as transaction:
            encounter = await self._repository.get(transaction, encounter_id)
        if encounter is None:
            raise ApplicationError(
                code=ErrorCode.RESOURCE_NOT_FOUND,
                message="The requested encounter was not found.",
            )
        return encounter

    async def list_for_patient(
        self,
        *,
        patient_id: OpaqueId,
        from_time: datetime | None = None,
        to_time: datetime | None = None,
        cursor: EncounterCursor | None = None,
        limit: int = 50,
    ) -> EncounterPage:
        if not 1 <= limit <= 100:
            raise ApplicationError(
                code=ErrorCode.VALIDATION_ERROR, message="The page limit is invalid."
            )
        database = self._require_database()
        async with database.transaction() as transaction:
            items = await self._repository.list_for_patient(
                transaction,
                patient_id=patient_id,
                from_time=from_time,
                to_time=to_time,
                cursor=cursor,
                limit=limit + 1,
            )
        return EncounterPage(items=items[:limit], has_more=len(items) > limit)

    async def transition_encounter(
        self, *, encounter_id: OpaqueId, target: EncounterStatus
    ) -> Encounter:
        database = self._require_database()
        now = self._now()
        try:
            async with database.transaction() as transaction:
                loaded = await self._repository.get_with_version(transaction, encounter_id)
                if loaded is None:
                    raise ApplicationError(
                        code=ErrorCode.RESOURCE_NOT_FOUND,
                        message="The requested encounter was not found.",
                    )
                current, version = loaded
                updated = current.transition_to(
                    target, at=now if target is EncounterStatus.COMPLETED else None
                )
                await self._repository.save(
                    transaction, updated, expected_version=version, updated_at=now
                )
                return updated
        except InvalidEncounterTransitionError as exc:
            raise ApplicationError(
                code=ErrorCode.INVALID_STATE_TRANSITION,
                message="The requested encounter transition is not allowed.",
                cause=exc,
            ) from exc
        except StaleEncounterWriteError as exc:
            raise ApplicationError(
                code=ErrorCode.RESOURCE_CONFLICT,
                message="The encounter changed before the operation completed.",
                cause=exc,
            ) from exc

    @staticmethod
    def _compatible(session_type: SessionType, encounter_type: EncounterType) -> bool:
        return (
            session_type is SessionType.KIOSK and encounter_type is EncounterType.KIOSK_INTAKE
        ) or (
            session_type is SessionType.PSEUDONYMOUS
            and encounter_type in {EncounterType.GENERAL_INTAKE, EncounterType.MENTAL_HEALTH}
        )

    def _require_database(self) -> DatabaseRuntime:
        if self._database is None:
            raise DependencyError(
                code=ErrorCode.DEPENDENCY_UNAVAILABLE,
                message="Encounter persistence is temporarily unavailable.",
            )
        return self._database

    def _now(self) -> datetime:
        value = self._clock()
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("encounter clock must be timezone-aware")
        return value.astimezone(UTC)
