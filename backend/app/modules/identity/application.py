"""Identity application service and trusted authentication boundary."""

from collections.abc import Callable
from datetime import UTC, datetime

from app.modules.identity.contracts import (
    ActorRepository,
    AuthenticatedPrincipal,
    AuthenticationCredential,
    AuthenticationProvider,
)
from app.modules.identity.domain import Actor, ActorStatus, ActorType, RoleCode
from app.shared.errors import ApplicationError, DependencyError, ErrorCode
from app.shared.persistence import DatabaseRuntime
from app.shared.security import ActorContext
from app.shared.types import OpaqueId, utc_now

type Clock = Callable[[], datetime]


def normalize_utc(name: str, value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value.astimezone(UTC)


class IdentityService:
    """Own persisted actor lifecycle and provider-neutral authentication."""

    def __init__(
        self,
        *,
        database: DatabaseRuntime | None,
        authentication_provider: AuthenticationProvider | None,
        repository: ActorRepository | None = None,
        clock: Clock = utc_now,
    ) -> None:
        resolved_repository: ActorRepository
        if repository is None:
            from app.modules.identity.infrastructure import PostgresActorRepository

            resolved_repository = PostgresActorRepository()
        else:
            resolved_repository = repository
        self._database = database
        self._provider = authentication_provider
        self._repository = resolved_repository
        self._clock = clock

    async def create_actor(
        self,
        *,
        actor_type: ActorType,
        roles: frozenset[RoleCode],
        subject_id: OpaqueId | None = None,
        institution_id: OpaqueId | None = None,
    ) -> Actor:
        database = self._require_database()
        now = self._now()
        async with database.transaction() as transaction:
            record = await self._repository.create(
                transaction,
                actor_id=OpaqueId.new(),
                actor_type=actor_type,
                roles=roles,
                subject_id=subject_id,
                institution_id=institution_id,
                created_at=now,
            )
            return self._repository.to_domain(record)

    async def get_actor(self, actor_id: OpaqueId) -> Actor | None:
        database = self._require_database()
        async with database.transaction() as transaction:
            record = await self._repository.get(transaction, actor_id)
            return None if record is None else self._repository.to_domain(record)

    async def disable_actor(self, actor_id: OpaqueId) -> Actor:
        database = self._require_database()
        now = self._now()
        async with database.transaction() as transaction:
            record = await self._repository.get_for_update(transaction, actor_id)
            if record is None:
                raise ApplicationError(
                    code=ErrorCode.RESOURCE_NOT_FOUND,
                    message="The requested actor was not found.",
                )
            return self._repository.disable(record, disabled_at=now)

    async def authenticate(self, credential: AuthenticationCredential) -> ActorContext:
        if self._provider is None:
            raise DependencyError(
                code=ErrorCode.DEPENDENCY_UNAVAILABLE,
                message="External authentication is not configured.",
            )
        try:
            principal = await self._provider.authenticate(credential)
        except Exception as error:
            raise DependencyError(
                code=ErrorCode.DEPENDENCY_UNAVAILABLE,
                message="External authentication is temporarily unavailable.",
                cause=error,
            ) from error
        if principal is None:
            raise self._authentication_required()
        return await self.current_actor(principal)

    async def current_actor(self, principal: AuthenticatedPrincipal) -> ActorContext:
        database = self._require_database()
        async with database.transaction() as transaction:
            record = await self._repository.get(transaction, principal.actor_id)
            if record is None:
                raise self._authentication_required()
            actor = self._repository.to_domain(record)
        if actor.status is not ActorStatus.ACTIVE:
            raise self._authentication_required()
        return ActorContext(
            actor_id=actor.actor_id,
            actor_type=actor.actor_type.value,
            roles=frozenset(role.value for role in actor.roles),
            subject_id=actor.subject_id,
            institution_id=actor.institution_id,
            is_authenticated=True,
            mfa_verified=principal.mfa_verified,
        )

    def _require_database(self) -> DatabaseRuntime:
        if self._database is None:
            raise DependencyError(
                code=ErrorCode.DEPENDENCY_UNAVAILABLE,
                message="Identity persistence is temporarily unavailable.",
            )
        return self._database

    def _now(self) -> datetime:
        return normalize_utc("identity clock", self._clock())

    @staticmethod
    def _authentication_required() -> ApplicationError:
        return ApplicationError(
            code=ErrorCode.AUTHENTICATION_REQUIRED,
            message="A valid authenticated actor is required.",
        )
