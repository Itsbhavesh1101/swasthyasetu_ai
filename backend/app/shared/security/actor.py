"""Minimal actor context for later identity and authorization phases."""

from dataclasses import dataclass

from app.shared.types import OpaqueId, RequestId


@dataclass(frozen=True, slots=True)
class ActorContext:
    """Trusted, privacy-safe request authorization state with no credentials."""

    actor_id: OpaqueId | None = None
    actor_type: str | None = None
    roles: frozenset[str] = frozenset()
    subject_id: OpaqueId | None = None
    institution_id: OpaqueId | None = None
    session_id: OpaqueId | None = None
    request_id: RequestId | None = None
    is_authenticated: bool = False
    mfa_verified: bool = False
