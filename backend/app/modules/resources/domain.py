"""Strict engineering-synthetic care-resource contracts."""

import re
import unicodedata
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Final

from app.modules.providers.domain import (
    DirectoryAuthority,
    DirectoryContractError,
    DirectoryDataClassification,
    DirectoryVerificationState,
    SyntheticSourceEvidence,
)

MAX_DISPLAY_NAME_LENGTH: Final = 160

_RESOURCE_ID = re.compile(r"^syn_resource_[a-z0-9][a-z0-9_]{0,95}$")
_RESOURCE_CODE = re.compile(r"^syn_resource_type_[a-z0-9][a-z0-9_]{0,95}$")


def _machine_value(value: object, *, name: str, pattern: re.Pattern[str]) -> str:
    if type(value) is not str or pattern.fullmatch(value) is None:
        raise DirectoryContractError(f"{name} has an invalid synthetic machine value")
    return value


def _synthetic_label(value: object) -> str:
    if (
        type(value) is not str
        or not value.startswith("Synthetic ")
        or value != value.strip()
        or len(value) > MAX_DISPLAY_NAME_LENGTH
        or any(unicodedata.category(character).startswith("C") for character in value)
    ):
        raise DirectoryContractError("display_name must be bounded, unmistakably synthetic text")
    return value


def _utc(value: object, *, name: str) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise DirectoryContractError(f"{name} must be timezone-aware")
    return value.astimezone(UTC)


def _closed_enum(value: object, expected: type[StrEnum], *, name: str) -> None:
    if type(value) is not expected:
        raise DirectoryContractError(f"{name} has invalid authority")


def _source_snapshot(value: object) -> SyntheticSourceEvidence:
    if type(value) is not SyntheticSourceEvidence:
        raise DirectoryContractError("source has an invalid type")
    return SyntheticSourceEvidence(
        source_id=value.source_id,
        source_version=value.source_version,
        artifact_hash=value.artifact_hash,
        acquired_at=value.acquired_at,
        authority=value.authority,
        classification=value.classification,
        verification=value.verification,
    )


@dataclass(frozen=True, slots=True)
class SyntheticCareResourceRecord:
    record_id: str
    record_version: int
    display_name: str
    resource_code: str
    source: SyntheticSourceEvidence
    created_at: datetime
    authority: DirectoryAuthority = DirectoryAuthority.ENGINEERING_ONLY
    classification: DirectoryDataClassification = DirectoryDataClassification.ENGINEERING_SYNTHETIC
    verification: DirectoryVerificationState = DirectoryVerificationState.UNVERIFIED

    def __post_init__(self) -> None:
        _machine_value(self.record_id, name="record_id", pattern=_RESOURCE_ID)
        if type(self.record_version) is not int or self.record_version < 1:
            raise DirectoryContractError("record_version must be a positive integer")
        _synthetic_label(self.display_name)
        _machine_value(self.resource_code, name="resource_code", pattern=_RESOURCE_CODE)
        source = _source_snapshot(self.source)
        created_at = _utc(self.created_at, name="created_at")
        _closed_enum(self.authority, DirectoryAuthority, name="record authority")
        _closed_enum(self.classification, DirectoryDataClassification, name="record classification")
        _closed_enum(self.verification, DirectoryVerificationState, name="record verification")
        if source.acquired_at > created_at:
            raise DirectoryContractError("source cannot be acquired after record creation")
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "created_at", created_at)


__all__ = ["SyntheticCareResourceRecord"]
