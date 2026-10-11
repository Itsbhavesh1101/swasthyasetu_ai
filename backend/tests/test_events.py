"""Framework-independent event envelope and publisher contracts."""

from datetime import UTC, datetime
from typing import cast

import pytest

from app.events import EventEnvelope, EventType, InProcessEventPublisher


def event(**overrides: object) -> EventEnvelope:
    """Build one deterministic synthetic event."""
    values: dict[str, object] = {
        "event_type": "SyntheticCreated",
        "event_version": 1,
        "occurred_at": datetime(2026, 1, 2, 3, 4, tzinfo=UTC),
        "payload": {"value": "example", "nested": {"enabled": True}},
    }
    values.update(overrides)
    return EventEnvelope.create(**values)  # type: ignore[arg-type]


def test_event_envelope_is_versioned_json_serializable_and_copy_protected() -> None:
    source = {"value": "example", "items": [1, 2]}
    envelope = event(payload=source)
    source["value"] = "changed"
    cast(list[int], source["items"]).append(3)

    assert envelope.to_dict()["payload"] == {"value": "example", "items": [1, 2]}
    with pytest.raises(TypeError):
        envelope.payload["value"] = "changed"  # type: ignore[index]


def test_event_envelope_round_trips_all_canonical_metadata() -> None:
    envelope = event(
        correlation_id="correlation-1",
        causation_id="causation-1",
        actor_ref="opaque-actor-1",
    )

    restored = EventEnvelope.from_dict(envelope.to_dict())

    assert restored == envelope


@pytest.mark.parametrize("value", ["", "   ", "x" * 129, "bad\nname"])
def test_event_type_rejects_invalid_values(value: str) -> None:
    with pytest.raises(ValueError):
        EventType(value)


@pytest.mark.parametrize("version", [0, -1, True])
def test_event_version_must_be_a_positive_integer(version: int) -> None:
    with pytest.raises(ValueError, match="positive integer"):
        event(event_version=version)


def test_event_time_must_be_aware_and_is_normalized_to_utc() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        event(occurred_at=datetime(2026, 1, 2, 3, 4))

    offset_time = datetime.fromisoformat("2026-01-02T08:34:00+05:30")
    assert event(occurred_at=offset_time).occurred_at == datetime(2026, 1, 2, 3, 4, tzinfo=UTC)


def test_event_payload_rejects_non_json_values_before_persistence() -> None:
    with pytest.raises(ValueError, match="JSON-compatible"):
        event(payload={"invalid": object()})


def test_event_repr_does_not_expose_payload() -> None:
    marker = "private-synthetic-payload-marker"

    assert marker not in repr(event(payload={"value": marker}))


async def test_in_process_publisher_is_explicit_ordered_and_no_handler_is_success() -> None:
    calls: list[str] = []

    async def first(envelope: EventEnvelope) -> None:
        calls.append(f"first:{envelope.event_version}")

    async def second(envelope: EventEnvelope) -> None:
        calls.append(f"second:{envelope.event_version}")

    publisher = InProcessEventPublisher({"SyntheticCreated": (first, second)})
    await publisher.publish(event())
    await publisher.publish(event(event_type="UnregisteredEvent"))

    assert calls == ["first:1", "second:1"]


async def test_in_process_publisher_propagates_handler_failure() -> None:
    marker = "private-synthetic-payload-marker"

    async def failing_handler(envelope: EventEnvelope) -> None:
        raise RuntimeError(marker)

    publisher = InProcessEventPublisher({"SyntheticCreated": (failing_handler,)})

    with pytest.raises(RuntimeError, match=marker):
        await publisher.publish(event())


async def test_idempotent_consumer_pattern_tolerates_duplicate_delivery() -> None:
    processed_ids: set[str] = set()
    side_effects: list[str] = []

    async def idempotent_handler(envelope: EventEnvelope) -> None:
        event_id = str(envelope.event_id)
        if event_id in processed_ids:
            return
        processed_ids.add(event_id)
        side_effects.append(event_id)

    publisher = InProcessEventPublisher({"SyntheticCreated": (idempotent_handler,)})
    envelope = event()
    await publisher.publish(envelope)
    await publisher.publish(envelope)

    assert side_effects == [str(envelope.event_id)]
