"""Stable, framework-independent internal event envelope."""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from types import MappingProxyType
from typing import cast

from app.shared.types import OpaqueId, utc_now

type JsonScalar = str | int | float | bool | None
type JsonValue = JsonScalar | list[JsonValue] | dict[str, JsonValue]
type FrozenJsonValue = JsonScalar | tuple[FrozenJsonValue, ...] | Mapping[str, FrozenJsonValue]

MAX_EVENT_TYPE_LENGTH = 128
MAX_METADATA_LENGTH = 128


class EventType(str):
    """Validated stable event contract name."""

    def __new__(cls, value: str) -> EventType:
        if not isinstance(value, str):
            raise TypeError("event type must be a string")
        if value != value.strip() or not value or len(value) > MAX_EVENT_TYPE_LENGTH:
            raise ValueError("event type must be non-empty and at most 128 characters")
        if not value.isprintable():
            raise ValueError("event type must contain only printable characters")
        return super().__new__(cls, value)


def _validate_opaque_metadata(name: str, value: str | None) -> str | None:
    if value is None:
        return None
    if value != value.strip() or not value or len(value) > MAX_METADATA_LENGTH:
        raise ValueError(f"{name} must be non-empty and at most 128 characters")
    if not value.isprintable():
        raise ValueError(f"{name} must contain only printable characters")
    return value


def _freeze_json(value: object) -> FrozenJsonValue:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("event payload must be JSON-compatible")
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, FrozenJsonValue] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("event payload must be JSON-compatible")
            frozen[key] = _freeze_json(item)
        return MappingProxyType(frozen)
    if isinstance(value, (list, tuple)):
        return tuple(_freeze_json(item) for item in value)
    raise ValueError("event payload must be JSON-compatible")


def _thaw_json(value: FrozenJsonValue) -> JsonValue:
    if isinstance(value, Mapping):
        return {key: _thaw_json(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw_json(item) for item in value]
    return value


def _aware_utc(name: str, value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value.astimezone(UTC)


@dataclass(frozen=True, slots=True)
class EventEnvelope:
    """Immutable versioned event metadata plus a privacy-sensitive JSON payload."""

    event_id: OpaqueId
    event_type: EventType
    event_version: int
    occurred_at: datetime
    correlation_id: str | None = None
    causation_id: str | None = None
    actor_ref: str | None = None
    payload: Mapping[str, FrozenJsonValue] = field(
        default_factory=lambda: MappingProxyType({}), repr=False
    )

    def __post_init__(self) -> None:
        if not isinstance(self.event_id, OpaqueId):
            raise TypeError("event_id must be an OpaqueId")
        if (
            not isinstance(self.event_version, int)
            or isinstance(self.event_version, bool)
            or self.event_version < 1
        ):
            raise ValueError("event version must be a positive integer")
        object.__setattr__(self, "event_type", EventType(self.event_type))
        object.__setattr__(self, "occurred_at", _aware_utc("occurred_at", self.occurred_at))
        object.__setattr__(
            self, "correlation_id", _validate_opaque_metadata("correlation_id", self.correlation_id)
        )
        object.__setattr__(
            self, "causation_id", _validate_opaque_metadata("causation_id", self.causation_id)
        )
        object.__setattr__(
            self, "actor_ref", _validate_opaque_metadata("actor_ref", self.actor_ref)
        )
        frozen_payload = _freeze_json(self.payload)
        if not isinstance(frozen_payload, Mapping):
            raise ValueError("event payload must be a JSON-compatible mapping")
        object.__setattr__(self, "payload", frozen_payload)

    @classmethod
    def create(
        cls,
        *,
        event_type: str | EventType,
        event_version: int,
        payload: Mapping[str, object],
        event_id: OpaqueId | None = None,
        occurred_at: datetime | None = None,
        correlation_id: str | None = None,
        causation_id: str | None = None,
        actor_ref: str | None = None,
    ) -> EventEnvelope:
        """Construct an envelope while generating only absent generic metadata."""
        return cls(
            event_id=event_id or OpaqueId.new(),
            event_type=EventType(event_type),
            event_version=event_version,
            occurred_at=occurred_at or utc_now(),
            correlation_id=correlation_id,
            causation_id=causation_id,
            actor_ref=actor_ref,
            payload=cast(Mapping[str, FrozenJsonValue], payload),
        )

    def to_dict(self) -> dict[str, JsonValue]:
        """Return a detached JSON-compatible transport representation."""
        return {
            "event_id": str(self.event_id),
            "event_type": str(self.event_type),
            "event_version": self.event_version,
            "occurred_at": self.occurred_at.isoformat(),
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "actor_ref": self.actor_ref,
            "payload": _thaw_json(self.payload),
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, object]) -> EventEnvelope:
        """Restore an envelope from its stable transport representation."""
        payload = value.get("payload")
        if not isinstance(payload, Mapping):
            raise ValueError("event payload must be a JSON-compatible mapping")
        return cls.create(
            event_id=OpaqueId.parse(cast(str, value["event_id"])),
            event_type=cast(str, value["event_type"]),
            event_version=cast(int, value["event_version"]),
            occurred_at=datetime.fromisoformat(cast(str, value["occurred_at"])),
            correlation_id=cast(str | None, value.get("correlation_id")),
            causation_id=cast(str | None, value.get("causation_id")),
            actor_ref=cast(str | None, value.get("actor_ref")),
            payload=cast(Mapping[str, object], payload),
        )
