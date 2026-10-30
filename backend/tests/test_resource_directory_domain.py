from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime, timedelta, timezone
from typing import Any, cast

import pytest

from app.modules.providers.domain import (
    DirectoryAuthority,
    DirectoryContractError,
    DirectoryDataClassification,
    DirectoryVerificationState,
    SyntheticSourceEvidence,
)
from app.modules.resources.domain import SyntheticCareResourceRecord

NOW = datetime(2026, 10, 31, 8, 0, tzinfo=UTC)


def source() -> SyntheticSourceEvidence:
    return SyntheticSourceEvidence(
        source_id="syn_source_resource_alpha",
        source_version="v1",
        artifact_hash="b" * 64,
        acquired_at=NOW,
    )


def resource() -> SyntheticCareResourceRecord:
    return SyntheticCareResourceRecord(
        record_id="syn_resource_alpha",
        record_version=1,
        display_name="Synthetic Care Resource Alpha",
        resource_code="syn_resource_type_alpha",
        source=source(),
        created_at=NOW + timedelta(seconds=1),
    )


def test_valid_resource_is_frozen_unverified_and_normalizes_utc() -> None:
    offset = timezone(timedelta(hours=-4))
    value = replace(
        resource(),
        source=replace(source(), acquired_at=NOW.astimezone(offset)),
        created_at=(NOW + timedelta(seconds=1)).astimezone(offset),
    )

    assert value.source.acquired_at.tzinfo is UTC
    assert value.created_at.tzinfo is UTC
    assert value.authority is DirectoryAuthority.ENGINEERING_ONLY
    assert value.classification is DirectoryDataClassification.ENGINEERING_SYNTHETIC
    assert value.verification is DirectoryVerificationState.UNVERIFIED
    with pytest.raises(FrozenInstanceError):
        value.resource_code = "syn_resource_type_changed"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("record_id", "resource_alpha"),
        ("record_version", 0),
        ("record_version", False),
        ("display_name", "Care Resource Alpha"),
        ("display_name", "Synthetic "),
        ("display_name", "Synthetic Care\tResource"),
        ("resource_code", "crisis_hotline"),
        ("created_at", datetime(2026, 10, 31, 8, 0, 1)),
    ],
)
def test_resource_rejects_non_synthetic_or_invalid_values(field: str, value: object) -> None:
    values: dict[str, object] = {
        "record_id": "syn_resource_alpha",
        "record_version": 1,
        "display_name": "Synthetic Care Resource Alpha",
        "resource_code": "syn_resource_type_alpha",
        "source": source(),
        "created_at": NOW + timedelta(seconds=1),
    }
    values[field] = value

    with pytest.raises(DirectoryContractError):
        SyntheticCareResourceRecord(**cast(Any, values))


def test_resource_revalidates_nested_source_and_temporal_order() -> None:
    mutated = source()
    object.__setattr__(mutated, "verification", cast(Any, "VERIFIED"))

    with pytest.raises(DirectoryContractError):
        replace(resource(), source=mutated)
    with pytest.raises(DirectoryContractError):
        replace(resource(), source=replace(source(), acquired_at=NOW + timedelta(seconds=2)))


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("authority", "PRODUCTION"),
        ("classification", "REAL_DATA"),
        ("verification", "VERIFIED"),
    ],
)
def test_resource_rejects_live_or_verified_authority(field: str, value: object) -> None:
    with pytest.raises(DirectoryContractError):
        cast(Any, replace)(resource(), **{field: value})


def test_resource_constructor_has_no_contact_eligibility_or_crisis_authority() -> None:
    values = {
        "record_id": "syn_resource_alpha",
        "record_version": 1,
        "display_name": "Synthetic Care Resource Alpha",
        "resource_code": "syn_resource_type_alpha",
        "source": source(),
        "created_at": NOW + timedelta(seconds=1),
    }
    for forbidden in ("phone_number", "url", "eligibility", "crisis_approved"):
        with pytest.raises(TypeError):
            cast(Any, SyntheticCareResourceRecord)(**values, **{forbidden: None})
