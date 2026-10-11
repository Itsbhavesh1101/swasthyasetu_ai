"""Explicit transport-neutral event publishing contracts."""

from collections.abc import Awaitable, Callable, Mapping
from types import MappingProxyType
from typing import Protocol

from app.events.envelope import EventEnvelope, EventType

type EventHandler = Callable[[EventEnvelope], Awaitable[None]]


class EventPublisher(Protocol):
    """Asynchronous event publication port."""

    async def publish(self, event: EventEnvelope) -> None: ...


class InProcessEventPublisher:
    """Publish sequentially to an immutable, explicitly registered handler map."""

    def __init__(self, handlers: Mapping[EventType | str, tuple[EventHandler, ...]]) -> None:
        copied = {EventType(event_type): tuple(values) for event_type, values in handlers.items()}
        self._handlers: Mapping[EventType, tuple[EventHandler, ...]] = MappingProxyType(copied)

    async def publish(self, event: EventEnvelope) -> None:
        """Await handlers in registration order; no handler is a successful no-op."""
        for handler in self._handlers.get(event.event_type, ()):
            await handler(event)
