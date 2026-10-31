"""Strict content-free contracts for detached synthetic FHIR mapping mechanics."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256
from types import MappingProxyType
from typing import Final

SYNTHETIC_FHIR_MAPPING_CONTRACT_VERSION: Final = "synthetic-fhir-mapping.v1"
MAX_SYNTHETIC_FHIR_SOURCES: Final = 4

_REQUEST_ID = re.compile(r"^syn_fhir_mapping_request_(?:alpha|beta|gamma|delta)$")
_SOURCE_ID = re.compile(r"^syn_fhir_source_(?:alpha|beta|gamma|delta)$")
_PROJECTION_ID = re.compile(r"^syn_fhir_projection_(?:alpha|beta|gamma|delta)$")
_MAPPING_ID = re.compile(r"^synthetic-fhir-r4-boundary$")
_VERSION = re.compile(r"^engineering\.v[1-9][0-9]{0,5}$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")


class FHIRMappingCode(StrEnum):
    INVALID_TYPE = "INVALID_TYPE"
    INVALID_VALUE = "INVALID_VALUE"
    DUPLICATE_SOURCE = "DUPLICATE_SOURCE"
    IDENTITY_MISMATCH = "IDENTITY_MISMATCH"
    PROHIBITED_SOURCE = "PROHIBITED_SOURCE"
    PROTECTED_ENVIRONMENT = "PROTECTED_ENVIRONMENT"


class FHIRMappingError(ValueError):
    """Stable content-free failure for synthetic FHIR mechanics."""

    def __init__(self, code: FHIRMappingCode) -> None:
        self.code = code
        super().__init__(code.value)


def _error(code: FHIRMappingCode) -> FHIRMappingError:
    return FHIRMappingError(code)


class FHIRVersion(StrEnum):
    R4_4_0_1 = "4.0.1"


class FHIRMappingDirection(StrEnum):
    EXPORT = "EXPORT"
    IMPORT_CANDIDATE = "IMPORT_CANDIDATE"


class SyntheticFHIRSourceType(StrEnum):
    ALLERGY = "SYNTHETIC_ALLERGY"
    CONSENT = "SYNTHETIC_CONSENT"
    DIAGNOSTIC_REPORT = "SYNTHETIC_DIAGNOSTIC_REPORT"
    DOCUMENT_REFERENCE = "SYNTHETIC_DOCUMENT_REFERENCE"
    ENCOUNTER = "SYNTHETIC_ENCOUNTER"
    MEDICATION = "SYNTHETIC_MEDICATION"
    MODEL_RISK = "SYNTHETIC_MODEL_RISK"
    OBSERVATION = "SYNTHETIC_OBSERVATION"
    PATIENT = "SYNTHETIC_PATIENT"
    PROVENANCE = "SYNTHETIC_PROVENANCE"
    UNCONFIRMED_EXTRACTION = "SYNTHETIC_UNCONFIRMED_EXTRACTION"


class FHIRResourceType(StrEnum):
    ALLERGY_INTOLERANCE = "AllergyIntolerance"
    CONSENT = "Consent"
    DIAGNOSTIC_REPORT = "DiagnosticReport"
    DOCUMENT_REFERENCE = "DocumentReference"
    ENCOUNTER = "Encounter"
    MEDICATION_STATEMENT = "MedicationStatement"
    OBSERVATION = "Observation"
    PATIENT = "Patient"
    PROVENANCE = "Provenance"


class SyntheticFHIRPlaceholder(StrEnum):
    ENGINEERING_ALPHA = "SYNTHETIC_FHIR_PLACEHOLDER_ALPHA"


class FHIRMappingResultState(StrEnum):
    SYNTHETIC_EXPORT_PROJECTION = "SYNTHETIC_EXPORT_PROJECTION"
    SYNTHETIC_IMPORT_CANDIDATE = "SYNTHETIC_IMPORT_CANDIDATE"


class SyntheticFHIRAuthority(StrEnum):
    ENGINEERING_ONLY = "ENGINEERING_ONLY"


class SyntheticFHIRVerification(StrEnum):
    UNVERIFIED = "UNVERIFIED"


_RESOURCE_BY_SOURCE: Final[Mapping[SyntheticFHIRSourceType, FHIRResourceType]] = MappingProxyType(
    {
        SyntheticFHIRSourceType.ALLERGY: FHIRResourceType.ALLERGY_INTOLERANCE,
        SyntheticFHIRSourceType.CONSENT: FHIRResourceType.CONSENT,
        SyntheticFHIRSourceType.DIAGNOSTIC_REPORT: FHIRResourceType.DIAGNOSTIC_REPORT,
        SyntheticFHIRSourceType.DOCUMENT_REFERENCE: FHIRResourceType.DOCUMENT_REFERENCE,
        SyntheticFHIRSourceType.ENCOUNTER: FHIRResourceType.ENCOUNTER,
        SyntheticFHIRSourceType.MEDICATION: FHIRResourceType.MEDICATION_STATEMENT,
        SyntheticFHIRSourceType.OBSERVATION: FHIRResourceType.OBSERVATION,
        SyntheticFHIRSourceType.PATIENT: FHIRResourceType.PATIENT,
        SyntheticFHIRSourceType.PROVENANCE: FHIRResourceType.PROVENANCE,
    }
)


def _strict_enum(value: object, expected: type[StrEnum]) -> None:
    if type(value) is not expected:
        raise _error(FHIRMappingCode.INVALID_TYPE)


def _machine_string(value: object, pattern: re.Pattern[str]) -> str:
    if type(value) is not str:
        raise _error(FHIRMappingCode.INVALID_TYPE)
    if pattern.fullmatch(value) is None:
        raise _error(FHIRMappingCode.INVALID_VALUE)
    return value


def _utc(value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise _error(FHIRMappingCode.INVALID_TYPE)
    return value.astimezone(UTC)


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticFHIRSourceReference:
    source_type: SyntheticFHIRSourceType
    source_id: str
    source_version: str
    content_hash: str
    authority: SyntheticFHIRAuthority = SyntheticFHIRAuthority.ENGINEERING_ONLY
    verification: SyntheticFHIRVerification = SyntheticFHIRVerification.UNVERIFIED

    def __post_init__(self) -> None:
        _strict_enum(self.source_type, SyntheticFHIRSourceType)
        _machine_string(self.source_id, _SOURCE_ID)
        _machine_string(self.source_version, _VERSION)
        _machine_string(self.content_hash, _SHA256)
        _strict_enum(self.authority, SyntheticFHIRAuthority)
        _strict_enum(self.verification, SyntheticFHIRVerification)


def _source(value: object) -> SyntheticFHIRSourceReference:
    if type(value) is not SyntheticFHIRSourceReference:
        raise _error(FHIRMappingCode.INVALID_TYPE)
    try:
        return SyntheticFHIRSourceReference(
            source_type=value.source_type,
            source_id=value.source_id,
            source_version=value.source_version,
            content_hash=value.content_hash,
            authority=value.authority,
            verification=value.verification,
        )
    except FHIRMappingError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(FHIRMappingCode.INVALID_TYPE) from None


def _sources(value: object) -> tuple[SyntheticFHIRSourceReference, ...]:
    if type(value) is not tuple:
        raise _error(FHIRMappingCode.INVALID_TYPE)
    if not value or len(value) > MAX_SYNTHETIC_FHIR_SOURCES:
        raise _error(FHIRMappingCode.INVALID_VALUE)
    sources = tuple(_source(item) for item in value)
    identities = tuple((item.source_type.value, item.source_id) for item in sources)
    if len(set(identities)) != len(identities):
        raise _error(FHIRMappingCode.DUPLICATE_SOURCE)
    if identities != tuple(sorted(identities)):
        raise _error(FHIRMappingCode.INVALID_VALUE)
    return sources


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticFHIRMappingContext:
    request_id: str
    direction: FHIRMappingDirection
    fhir_version: FHIRVersion
    mapping_id: str
    mapping_revision: str
    sources: tuple[SyntheticFHIRSourceReference, ...]
    transformed_at: datetime
    authority: SyntheticFHIRAuthority = SyntheticFHIRAuthority.ENGINEERING_ONLY
    verification: SyntheticFHIRVerification = SyntheticFHIRVerification.UNVERIFIED

    def __post_init__(self) -> None:
        _machine_string(self.request_id, _REQUEST_ID)
        _strict_enum(self.direction, FHIRMappingDirection)
        _strict_enum(self.fhir_version, FHIRVersion)
        _machine_string(self.mapping_id, _MAPPING_ID)
        _machine_string(self.mapping_revision, _VERSION)
        sources = _sources(self.sources)
        transformed_at = _utc(self.transformed_at)
        _strict_enum(self.authority, SyntheticFHIRAuthority)
        _strict_enum(self.verification, SyntheticFHIRVerification)
        object.__setattr__(self, "sources", sources)
        object.__setattr__(self, "transformed_at", transformed_at)


def _context(value: object) -> SyntheticFHIRMappingContext:
    if type(value) is not SyntheticFHIRMappingContext:
        raise _error(FHIRMappingCode.INVALID_TYPE)
    try:
        return SyntheticFHIRMappingContext(
            request_id=value.request_id,
            direction=value.direction,
            fhir_version=value.fhir_version,
            mapping_id=value.mapping_id,
            mapping_revision=value.mapping_revision,
            sources=value.sources,
            transformed_at=value.transformed_at,
            authority=value.authority,
            verification=value.verification,
        )
    except FHIRMappingError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(FHIRMappingCode.INVALID_TYPE) from None


def synthetic_fhir_context_fingerprint(context: SyntheticFHIRMappingContext) -> str:
    snapshot = _context(context)
    fields = [
        SYNTHETIC_FHIR_MAPPING_CONTRACT_VERSION,
        snapshot.request_id,
        snapshot.direction.value,
        snapshot.fhir_version.value,
        snapshot.mapping_id,
        snapshot.mapping_revision,
        snapshot.transformed_at.isoformat(),
        snapshot.authority.value,
        snapshot.verification.value,
    ]
    for item in snapshot.sources:
        fields.extend(
            (
                item.source_type.value,
                item.source_id,
                item.source_version,
                item.content_hash,
                item.authority.value,
                item.verification.value,
            )
        )
    return sha256("\x1f".join(fields).encode("ascii")).hexdigest()


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticFHIRMappingResult:
    request_id: str
    direction: FHIRMappingDirection
    state: FHIRMappingResultState
    fhir_version: FHIRVersion
    mapping_id: str
    mapping_revision: str
    resource_type: FHIRResourceType
    logical_projection_id: str
    placeholder: SyntheticFHIRPlaceholder
    context_fingerprint: str
    sources: tuple[SyntheticFHIRSourceReference, ...]
    transformed_at: datetime
    authoritative: bool = False
    authority: SyntheticFHIRAuthority = SyntheticFHIRAuthority.ENGINEERING_ONLY
    verification: SyntheticFHIRVerification = SyntheticFHIRVerification.UNVERIFIED

    def __post_init__(self) -> None:
        _machine_string(self.request_id, _REQUEST_ID)
        _strict_enum(self.direction, FHIRMappingDirection)
        _strict_enum(self.state, FHIRMappingResultState)
        expected_state = (
            FHIRMappingResultState.SYNTHETIC_EXPORT_PROJECTION
            if self.direction is FHIRMappingDirection.EXPORT
            else FHIRMappingResultState.SYNTHETIC_IMPORT_CANDIDATE
        )
        if self.state is not expected_state:
            raise _error(FHIRMappingCode.INVALID_VALUE)
        _strict_enum(self.fhir_version, FHIRVersion)
        _machine_string(self.mapping_id, _MAPPING_ID)
        _machine_string(self.mapping_revision, _VERSION)
        _strict_enum(self.resource_type, FHIRResourceType)
        _machine_string(self.logical_projection_id, _PROJECTION_ID)
        _strict_enum(self.placeholder, SyntheticFHIRPlaceholder)
        _machine_string(self.context_fingerprint, _SHA256)
        sources = _sources(self.sources)
        transformed_at = _utc(self.transformed_at)
        if type(self.authoritative) is not bool:
            raise _error(FHIRMappingCode.INVALID_TYPE)
        if self.authoritative:
            raise _error(FHIRMappingCode.INVALID_VALUE)
        _strict_enum(self.authority, SyntheticFHIRAuthority)
        _strict_enum(self.verification, SyntheticFHIRVerification)
        object.__setattr__(self, "sources", sources)
        object.__setattr__(self, "transformed_at", transformed_at)


def _result(value: object) -> SyntheticFHIRMappingResult:
    if type(value) is not SyntheticFHIRMappingResult:
        raise _error(FHIRMappingCode.INVALID_TYPE)
    try:
        return SyntheticFHIRMappingResult(
            request_id=value.request_id,
            direction=value.direction,
            state=value.state,
            fhir_version=value.fhir_version,
            mapping_id=value.mapping_id,
            mapping_revision=value.mapping_revision,
            resource_type=value.resource_type,
            logical_projection_id=value.logical_projection_id,
            placeholder=value.placeholder,
            context_fingerprint=value.context_fingerprint,
            sources=value.sources,
            transformed_at=value.transformed_at,
            authoritative=value.authoritative,
            authority=value.authority,
            verification=value.verification,
        )
    except FHIRMappingError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(FHIRMappingCode.INVALID_TYPE) from None


def expected_synthetic_fhir_resource(
    source_type: SyntheticFHIRSourceType,
) -> FHIRResourceType:
    _strict_enum(source_type, SyntheticFHIRSourceType)
    try:
        return _RESOURCE_BY_SOURCE[source_type]
    except KeyError:
        raise _error(FHIRMappingCode.PROHIBITED_SOURCE) from None


def validate_synthetic_fhir_mapping_result(
    *,
    context: SyntheticFHIRMappingContext,
    result: SyntheticFHIRMappingResult,
) -> SyntheticFHIRMappingResult:
    context_snapshot = _context(context)
    result_snapshot = _result(result)
    if len(context_snapshot.sources) != 1:
        raise _error(FHIRMappingCode.INVALID_VALUE)
    expected_resource = expected_synthetic_fhir_resource(context_snapshot.sources[0].source_type)
    if (
        result_snapshot.request_id != context_snapshot.request_id
        or result_snapshot.direction is not context_snapshot.direction
        or result_snapshot.fhir_version is not context_snapshot.fhir_version
        or result_snapshot.mapping_id != context_snapshot.mapping_id
        or result_snapshot.mapping_revision != context_snapshot.mapping_revision
        or result_snapshot.context_fingerprint
        != synthetic_fhir_context_fingerprint(context_snapshot)
        or result_snapshot.sources != context_snapshot.sources
        or result_snapshot.transformed_at != context_snapshot.transformed_at
        or result_snapshot.resource_type is not expected_resource
    ):
        raise _error(FHIRMappingCode.IDENTITY_MISMATCH)
    return result_snapshot


__all__ = [
    "FHIRMappingCode",
    "FHIRMappingDirection",
    "FHIRMappingError",
    "FHIRMappingResultState",
    "FHIRResourceType",
    "FHIRVersion",
    "MAX_SYNTHETIC_FHIR_SOURCES",
    "SYNTHETIC_FHIR_MAPPING_CONTRACT_VERSION",
    "SyntheticFHIRAuthority",
    "SyntheticFHIRMappingContext",
    "SyntheticFHIRMappingResult",
    "SyntheticFHIRPlaceholder",
    "SyntheticFHIRSourceReference",
    "SyntheticFHIRSourceType",
    "SyntheticFHIRVerification",
    "expected_synthetic_fhir_resource",
    "synthetic_fhir_context_fingerprint",
    "validate_synthetic_fhir_mapping_result",
]
