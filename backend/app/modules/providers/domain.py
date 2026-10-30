"""Strict engineering-synthetic provider directory contracts."""

import re
import unicodedata
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Final

MAX_DISPLAY_NAME_LENGTH: Final = 160

_SOURCE_ID = re.compile(r"^syn_source_[a-z0-9][a-z0-9_]{0,95}$")
_PROVIDER_ID = re.compile(r"^syn_provider_[a-z0-9][a-z0-9_]{0,95}$")
_SERVICE_CODE = re.compile(r"^syn_service_[a-z0-9][a-z0-9_]{0,95}$")
_VERSION = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")


class DirectoryContractError(ValueError):
    """Raised when synthetic directory data violates a trust boundary."""


class DirectoryAuthority(StrEnum):
    ENGINEERING_ONLY = "ENGINEERING_ONLY"


class DirectoryDataClassification(StrEnum):
    ENGINEERING_SYNTHETIC = "ENGINEERING_SYNTHETIC"


class DirectoryVerificationState(StrEnum):
    UNVERIFIED = "UNVERIFIED"


def _error(message: str) -> DirectoryContractError:
    return DirectoryContractError(message)


def _machine_value(value: object, *, name: str, pattern: re.Pattern[str]) -> str:
    if type(value) is not str or pattern.fullmatch(value) is None:
        raise _error(f"{name} has an invalid synthetic machine value")
    return value


def _utc(value: object, *, name: str) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise _error(f"{name} must be timezone-aware")
    return value.astimezone(UTC)


def _synthetic_label(value: object) -> str:
    if (
        type(value) is not str
        or not value.startswith("Synthetic ")
        or value != value.strip()
        or len(value) > MAX_DISPLAY_NAME_LENGTH
        or any(unicodedata.category(character).startswith("C") for character in value)
    ):
        raise _error("display_name must be bounded, unmistakably synthetic text")
    return value


def _closed_enum(value: object, expected: type[StrEnum], *, name: str) -> None:
    if type(value) is not expected:
        raise _error(f"{name} has invalid authority")


@dataclass(frozen=True, slots=True)
class SyntheticSourceEvidence:
    source_id: str
    source_version: str
    artifact_hash: str
    acquired_at: datetime
    authority: DirectoryAuthority = DirectoryAuthority.ENGINEERING_ONLY
    classification: DirectoryDataClassification = DirectoryDataClassification.ENGINEERING_SYNTHETIC
    verification: DirectoryVerificationState = DirectoryVerificationState.UNVERIFIED

    def __post_init__(self) -> None:
        _machine_value(self.source_id, name="source_id", pattern=_SOURCE_ID)
        _machine_value(self.source_version, name="source_version", pattern=_VERSION)
        _machine_value(self.artifact_hash, name="artifact_hash", pattern=_SHA256)
        _closed_enum(self.authority, DirectoryAuthority, name="source authority")
        _closed_enum(self.classification, DirectoryDataClassification, name="source classification")
        _closed_enum(self.verification, DirectoryVerificationState, name="source verification")
        object.__setattr__(self, "acquired_at", _utc(self.acquired_at, name="acquired_at"))


def _source_snapshot(value: object) -> SyntheticSourceEvidence:
    if type(value) is not SyntheticSourceEvidence:
        raise _error("source has an invalid type")
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
class SyntheticProviderRecord:
    record_id: str
    record_version: int
    display_name: str
    service_code: str
    source: SyntheticSourceEvidence
    created_at: datetime
    authority: DirectoryAuthority = DirectoryAuthority.ENGINEERING_ONLY
    classification: DirectoryDataClassification = DirectoryDataClassification.ENGINEERING_SYNTHETIC
    verification: DirectoryVerificationState = DirectoryVerificationState.UNVERIFIED

    def __post_init__(self) -> None:
        _machine_value(self.record_id, name="record_id", pattern=_PROVIDER_ID)
        if type(self.record_version) is not int or self.record_version < 1:
            raise _error("record_version must be a positive integer")
        _synthetic_label(self.display_name)
        _machine_value(self.service_code, name="service_code", pattern=_SERVICE_CODE)
        source = _source_snapshot(self.source)
        created_at = _utc(self.created_at, name="created_at")
        _closed_enum(self.authority, DirectoryAuthority, name="record authority")
        _closed_enum(self.classification, DirectoryDataClassification, name="record classification")
        _closed_enum(self.verification, DirectoryVerificationState, name="record verification")
        if source.acquired_at > created_at:
            raise _error("source cannot be acquired after record creation")
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "created_at", created_at)


__all__ = [
    "DirectoryAuthority",
    "DirectoryContractError",
    "DirectoryDataClassification",
    "DirectoryVerificationState",
    "SyntheticProviderRecord",
    "SyntheticSourceEvidence",
]
