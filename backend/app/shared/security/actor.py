"""Minimal actor context for later identity and authorization phases."""

from dataclasses import dataclass

from app.shared.types import OpaqueId, RequestId


@dataclass(frozen=True, slots=True)
class ActorContext:
    """Identity-neutral request actor state with no role inference."""

    actor_id: OpaqueId | None = None
    session_id: OpaqueId | None = None
    request_id: RequestId | None = None
    is_authenticated: bool = False
