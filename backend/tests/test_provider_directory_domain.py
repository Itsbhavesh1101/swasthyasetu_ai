from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime, timedelta, timezone
from typing import Any, cast

import pytest

from app.modules.providers.domain import (
    DirectoryAuthority,
    DirectoryContractError,
    DirectoryDataClassification,
    DirectoryVerificationState,
    SyntheticProviderRecord,
    SyntheticSourceEvidence,
)

NOW = datetime(2026, 10, 31, 8, 0, tzinfo=UTC)
HASH = "a" * 64


def source() -> SyntheticSourceEvidence:
    return SyntheticSourceEvidence(
        source_id="syn_source_fixture_alpha",
        source_version="v1",
        artifact_hash=HASH,
        acquired_at=NOW,
    )


def provider() -> SyntheticProviderRecord:
    return SyntheticProviderRecord(
        record_id="syn_provider_alpha",
        record_version=1,
        display_name="Synthetic Provider Alpha",
        service_code="syn_service_general_alpha",
        source=source(),
        created_at=NOW + timedelta(seconds=1),
    )


def test_valid_provider_is_frozen_and_normalizes_aware_times_to_utc() -> None:
    offset = timezone(timedelta(hours=5, minutes=30))
    value = SyntheticProviderRecord(
        record_id="syn_provider_alpha",
        record_version=1,
        display_name="Synthetic Provider Alpha",
        service_code="syn_service_general_alpha",
        source=replace(source(), acquired_at=NOW.astimezone(offset)),
        created_at=(NOW + timedelta(seconds=1)).astimezone(offset),
    )

    assert value.source.acquired_at == NOW
    assert value.source.acquired_at.tzinfo is UTC
    assert value.created_at.tzinfo is UTC
    assert value.authority is DirectoryAuthority.ENGINEERING_ONLY
    assert value.classification is DirectoryDataClassification.ENGINEERING_SYNTHETIC
    assert value.verification is DirectoryVerificationState.UNVERIFIED
    with pytest.raises(FrozenInstanceError):
        value.display_name = "Synthetic Changed"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("source_id", "source_realistic"),
        ("source_id", "https://example.invalid/source"),
        ("source_version", "latest/current"),
        ("artifact_hash", "not-a-sha256"),
        ("acquired_at", datetime(2026, 10, 31, 8, 0)),
    ],
)
def test_source_rejects_non_synthetic_malformed_or_naive_values(field: str, value: object) -> None:
    values: dict[str, object] = {
        "source_id": "syn_source_fixture_alpha",
        "source_version": "v1",
        "artifact_hash": HASH,
        "acquired_at": NOW,
    }
    values[field] = value

    with pytest.raises(DirectoryContractError):
        SyntheticSourceEvidence(**cast(Any, values))


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("record_id", "provider_alpha"),
        ("record_version", 0),
        ("record_version", True),
        ("display_name", "Provider Alpha"),
        ("display_name", "Synthetic "),
        ("display_name", "Synthetic Provider\nAlpha"),
        ("display_name", "Synthetic " + "x" * 200),
        ("service_code", "general_medicine"),
        ("created_at", datetime(2026, 10, 31, 8, 0, 1)),
    ],
)
def test_provider_rejects_non_synthetic_unbounded_or_invalid_values(
    field: str, value: object
) -> None:
    values: dict[str, object] = {
        "record_id": "syn_provider_alpha",
        "record_version": 1,
        "display_name": "Synthetic Provider Alpha",
        "service_code": "syn_service_general_alpha",
        "source": source(),
        "created_at": NOW + timedelta(seconds=1),
    }
    values[field] = value

    with pytest.raises(DirectoryContractError):
        SyntheticProviderRecord(**cast(Any, values))


def test_provider_rejects_source_acquired_after_record_creation() -> None:
    with pytest.raises(DirectoryContractError):
        replace(provider(), source=replace(source(), acquired_at=NOW + timedelta(seconds=2)))


def test_provider_revalidates_forcibly_mutated_nested_source() -> None:
    supplied = source()
    object.__setattr__(supplied, "source_id", "external_source")

    with pytest.raises(DirectoryContractError):
        replace(provider(), source=supplied)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("authority", "PRODUCTION"),
        ("classification", "REAL_DATA"),
        ("verification", "VERIFIED"),
    ],
)
def test_provider_rejects_any_live_or_verified_authority(field: str, value: object) -> None:
    with pytest.raises(DirectoryContractError):
        cast(Any, replace)(provider(), **{field: value})


def test_provider_constructor_has_no_contact_availability_or_routing_fields() -> None:
    values = {
        "record_id": "syn_provider_alpha",
        "record_version": 1,
        "display_name": "Synthetic Provider Alpha",
        "service_code": "syn_service_general_alpha",
        "source": source(),
        "created_at": NOW + timedelta(seconds=1),
    }
    for forbidden in ("contact_methods", "booking_url", "available", "care_category"):
        with pytest.raises(TypeError):
            cast(Any, SyntheticProviderRecord)(**values, **{forbidden: ()})
