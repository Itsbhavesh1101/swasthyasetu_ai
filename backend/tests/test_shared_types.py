"""Shared-kernel identifier and time primitive tests."""

from datetime import UTC
from uuid import UUID

import pytest

from app.shared.types import OpaqueId, utc_now


def test_new_opaque_ids_are_distinct_uuid4_values() -> None:
    first = OpaqueId.new()
    second = OpaqueId.new()

    assert first != second
    assert first.value.version == 4
    assert second.value.version == 4
    assert UUID(str(first)) == first.value


def test_opaque_id_parses_existing_uuid_predictably() -> None:
    value = "2e356cf4-ecc9-4bc4-9516-d921a84373f1"

    assert str(OpaqueId.parse(value)) == value
    assert OpaqueId.parse(UUID(value)) == OpaqueId.parse(value)


def test_opaque_id_rejects_invalid_value() -> None:
    with pytest.raises(ValueError):
        OpaqueId.parse("not-a-uuid")


def test_utc_now_is_timezone_aware_utc() -> None:
    current = utc_now()

    assert current.tzinfo is not None
    assert current.utcoffset() == UTC.utcoffset(current)
    assert current.utcoffset() is not None
