"""Provider-neutral authentication and identity capability contracts."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.identity.domain import Actor, ActorType, PermissionCode, RoleCode
from app.shared.security import ActorContext
from app.shared.types import OpaqueId


@dataclass(frozen=True, slots=True)
class AuthenticationCredential:
    """Opaque, bounded credential that never reveals its contents in repr."""

    value: str = field(repr=False)

    def __post_init__(self) -> None:
        if not self.value or len(self.value) > 8192:
            raise ValueError("Authentication credential must contain 1 to 8192 characters")

    def __repr__(self) -> str:
        return "AuthenticationCredential(value=<redacted>)"


@dataclass(frozen=True, slots=True)
class AuthenticatedPrincipal:
    actor_id: OpaqueId
    provider: str
    mfa_verified: bool = False

    def __post_init__(self) -> None:
        if not self.provider.strip():
            raise ValueError("Authentication provider name must not be empty")


class AuthenticationProvider(Protocol):
    async def authenticate(
        self, credential: AuthenticationCredential
    ) -> AuthenticatedPrincipal | None: ...


class AuthenticateCapability(Protocol):
    async def authenticate(self, credential: AuthenticationCredential) -> ActorContext: ...


class CurrentActorCapability(Protocol):
    async def current_actor(self, principal: AuthenticatedPrincipal) -> ActorContext: ...


class AuthorizeCapability(Protocol):
    def has_permission(self, actor_context: ActorContext, permission: PermissionCode) -> bool: ...
    def require_permission(
        self, actor_context: ActorContext, permission: PermissionCode
    ) -> None: ...
    def require_self_subject(
        self, actor_context: ActorContext, permission: PermissionCode, subject_id: OpaqueId
    ) -> None: ...


class ActorRepository(Protocol):
    async def create(
        self,
        session: AsyncSession,
        *,
        actor_id: OpaqueId,
        actor_type: ActorType,
        roles: frozenset[RoleCode],
        subject_id: OpaqueId | None,
        institution_id: OpaqueId | None,
        created_at: datetime,
    ) -> object: ...
    async def get(self, session: AsyncSession, actor_id: OpaqueId) -> object | None: ...
    async def get_for_update(self, session: AsyncSession, actor_id: OpaqueId) -> object | None: ...
    def disable(self, record: object, *, disabled_at: datetime) -> Actor: ...
    def to_domain(self, record: object) -> Actor: ...
