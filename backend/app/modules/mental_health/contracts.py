"""Content-free synthetic signal contracts with no clinical or route authority."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Final, cast

SYNTHETIC_RESULT_CONTRACT_VERSION: Final = "synthetic-mh-signal-result.v1"
MAX_SYNTHETIC_SIGNALS: Final = 4

_ARTIFACT_ID = re.compile(r"^syn_mh_(?:input_fixture_(?:alpha|beta|gamma|delta)|schema_fixture)$")
_FIXTURE_SUFFIX = r"(?:alpha|beta|gamma|delta)"
_REQUEST_ID = re.compile(rf"^syn_mh_request_{_FIXTURE_SUFFIX}$")
_RESULT_ID = re.compile(rf"^syn_mh_result_{_FIXTURE_SUFFIX}$")
_FAILURE_ID = re.compile(rf"^syn_mh_failure_{_FIXTURE_SUFFIX}$")
_VERSION = re.compile(r"^engineering\.v[1-9][0-9]{0,5}$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_CANONICAL_UTC = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2})T(?P<time>\d{2}:\d{2}:\d{2})(?P<fraction>\.\d{3})?Z$"
)


class MentalHealthContractCode(StrEnum):
    INVALID_TYPE = "INVALID_TYPE"
    INVALID_VALUE = "INVALID_VALUE"
    UNKNOWN_FIELD = "UNKNOWN_FIELD"
    MISSING_FIELD = "MISSING_FIELD"
    LIMIT_EXCEEDED = "LIMIT_EXCEEDED"
    DUPLICATE_SIGNAL = "DUPLICATE_SIGNAL"
    IDENTITY_MISMATCH = "IDENTITY_MISMATCH"
    INVALID_CHRONOLOGY = "INVALID_CHRONOLOGY"
    INCONSISTENT_RESULT = "INCONSISTENT_RESULT"


class MentalHealthContractError(ValueError):
    """Stable content-free boundary error."""

    def __init__(self, code: MentalHealthContractCode) -> None:
        self.code = code
        super().__init__(code.value)


def _error(code: MentalHealthContractCode) -> MentalHealthContractError:
    return MentalHealthContractError(code)


class SyntheticAuthority(StrEnum):
    ENGINEERING_ONLY = "ENGINEERING_ONLY"


class SyntheticClassification(StrEnum):
    ENGINEERING_SYNTHETIC = "ENGINEERING_SYNTHETIC"


class SyntheticVerification(StrEnum):
    UNVERIFIED = "UNVERIFIED"


class SyntheticSignalCode(StrEnum):
    ALPHA = "SYN_MH_SIGNAL_ALPHA"
    BETA = "SYN_MH_SIGNAL_BETA"
    GAMMA = "SYN_MH_SIGNAL_GAMMA"
    DELTA = "SYN_MH_SIGNAL_DELTA"


class SyntheticSignalState(StrEnum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    UNKNOWN = "UNKNOWN"
    UNCERTAIN = "UNCERTAIN"
    CONTRADICTORY = "CONTRADICTORY"


class SyntheticExtractionStatus(StrEnum):
    SYNTHETIC_PARSED = "SYNTHETIC_PARSED"
    SYNTHETIC_ABSTAINED = "SYNTHETIC_ABSTAINED"


class SyntheticExtractionFailureCode(StrEnum):
    SIMULATED_TIMEOUT = "SIMULATED_TIMEOUT"
    SIMULATED_UNAVAILABLE = "SIMULATED_UNAVAILABLE"
    SIMULATED_INVALID_RESPONSE = "SIMULATED_INVALID_RESPONSE"
    SIMULATED_CANCELLED = "SIMULATED_CANCELLED"


def _machine_string(value: object, pattern: re.Pattern[str]) -> str:
    if type(value) is not str:
        raise _error(MentalHealthContractCode.INVALID_TYPE)
    if pattern.fullmatch(value) is None:
        raise _error(MentalHealthContractCode.INVALID_VALUE)
    return value


def _strict_enum(value: object, expected: type[StrEnum]) -> None:
    if type(value) is not expected:
        raise _error(MentalHealthContractCode.INVALID_TYPE)


def _utc(value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise _error(MentalHealthContractCode.INVALID_TYPE)
    return value.astimezone(UTC)


def _parse_utc(value: object) -> datetime:
    if type(value) is not str:
        raise _error(MentalHealthContractCode.INVALID_TYPE)
    match = _CANONICAL_UTC.fullmatch(value)
    if match is None:
        raise _error(MentalHealthContractCode.INVALID_VALUE)
    try:
        parsed = datetime.fromisoformat(value.removesuffix("Z") + "+00:00")
    except ValueError:
        raise _error(MentalHealthContractCode.INVALID_VALUE) from None
    if parsed.strftime("%Y-%m-%dT%H:%M:%S") != f"{match['date']}T{match['time']}":
        raise _error(MentalHealthContractCode.INVALID_VALUE)
    return parsed.astimezone(UTC)


def _authority(
    authority: object,
    classification: object,
    verification: object,
) -> None:
    _strict_enum(authority, SyntheticAuthority)
    _strict_enum(classification, SyntheticClassification)
    _strict_enum(verification, SyntheticVerification)


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticArtifactReference:
    artifact_id: str
    artifact_version: str
    content_hash: str
    created_at: datetime
    authority: SyntheticAuthority = SyntheticAuthority.ENGINEERING_ONLY
    classification: SyntheticClassification = SyntheticClassification.ENGINEERING_SYNTHETIC
    verification: SyntheticVerification = SyntheticVerification.UNVERIFIED

    def __post_init__(self) -> None:
        _machine_string(self.artifact_id, _ARTIFACT_ID)
        _machine_string(self.artifact_version, _VERSION)
        _machine_string(self.content_hash, _SHA256)
        _authority(self.authority, self.classification, self.verification)
        object.__setattr__(self, "created_at", _utc(self.created_at))


def _artifact(value: object) -> SyntheticArtifactReference:
    if type(value) is not SyntheticArtifactReference:
        raise _error(MentalHealthContractCode.INVALID_TYPE)
    try:
        return SyntheticArtifactReference(
            artifact_id=value.artifact_id,
            artifact_version=value.artifact_version,
            content_hash=value.content_hash,
            created_at=value.created_at,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
        )
    except MentalHealthContractError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(MentalHealthContractCode.INVALID_TYPE) from None


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticSignalObservation:
    code: SyntheticSignalCode
    state: SyntheticSignalState

    def __post_init__(self) -> None:
        _strict_enum(self.code, SyntheticSignalCode)
        _strict_enum(self.state, SyntheticSignalState)


def _observation(value: object) -> SyntheticSignalObservation:
    if type(value) is not SyntheticSignalObservation:
        raise _error(MentalHealthContractCode.INVALID_TYPE)
    try:
        return SyntheticSignalObservation(code=value.code, state=value.state)
    except MentalHealthContractError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(MentalHealthContractCode.INVALID_TYPE) from None


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticExtractionRequest:
    request_id: str
    input_artifact: SyntheticArtifactReference
    schema_artifact: SyntheticArtifactReference
    created_at: datetime
    deadline_at: datetime
    authority: SyntheticAuthority = SyntheticAuthority.ENGINEERING_ONLY
    classification: SyntheticClassification = SyntheticClassification.ENGINEERING_SYNTHETIC
    verification: SyntheticVerification = SyntheticVerification.UNVERIFIED

    def __post_init__(self) -> None:
        _machine_string(self.request_id, _REQUEST_ID)
        input_artifact = _artifact(self.input_artifact)
        schema_artifact = _artifact(self.schema_artifact)
        if not input_artifact.artifact_id.startswith("syn_mh_input_fixture_"):
            raise _error(MentalHealthContractCode.INVALID_VALUE)
        if schema_artifact.artifact_id != "syn_mh_schema_fixture":
            raise _error(MentalHealthContractCode.INVALID_VALUE)
        created_at = _utc(self.created_at)
        deadline_at = _utc(self.deadline_at)
        if input_artifact.created_at > created_at or schema_artifact.created_at > created_at:
            raise _error(MentalHealthContractCode.INVALID_CHRONOLOGY)
        if deadline_at <= created_at:
            raise _error(MentalHealthContractCode.INVALID_CHRONOLOGY)
        _authority(self.authority, self.classification, self.verification)
        object.__setattr__(self, "input_artifact", input_artifact)
        object.__setattr__(self, "schema_artifact", schema_artifact)
        object.__setattr__(self, "created_at", created_at)
        object.__setattr__(self, "deadline_at", deadline_at)


def _request(value: object) -> SyntheticExtractionRequest:
    if type(value) is not SyntheticExtractionRequest:
        raise _error(MentalHealthContractCode.INVALID_TYPE)
    try:
        return SyntheticExtractionRequest(
            request_id=value.request_id,
            input_artifact=value.input_artifact,
            schema_artifact=value.schema_artifact,
            created_at=value.created_at,
            deadline_at=value.deadline_at,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
        )
    except MentalHealthContractError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(MentalHealthContractCode.INVALID_TYPE) from None


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticExtractionResult:
    contract_version: str
    result_id: str
    request_id: str
    input_artifact_id: str
    input_artifact_version: str
    input_artifact_hash: str
    schema_artifact_id: str
    schema_artifact_version: str
    schema_artifact_hash: str
    status: SyntheticExtractionStatus
    signals: tuple[SyntheticSignalObservation, ...]
    completed_at: datetime
    authority: SyntheticAuthority = SyntheticAuthority.ENGINEERING_ONLY
    classification: SyntheticClassification = SyntheticClassification.ENGINEERING_SYNTHETIC
    verification: SyntheticVerification = SyntheticVerification.UNVERIFIED

    def __post_init__(self) -> None:
        if type(self.contract_version) is not str:
            raise _error(MentalHealthContractCode.INVALID_TYPE)
        if self.contract_version != SYNTHETIC_RESULT_CONTRACT_VERSION:
            raise _error(MentalHealthContractCode.INVALID_VALUE)
        _machine_string(self.result_id, _RESULT_ID)
        _machine_string(self.request_id, _REQUEST_ID)
        _machine_string(self.input_artifact_id, _ARTIFACT_ID)
        _machine_string(self.input_artifact_version, _VERSION)
        _machine_string(self.input_artifact_hash, _SHA256)
        _machine_string(self.schema_artifact_id, _ARTIFACT_ID)
        _machine_string(self.schema_artifact_version, _VERSION)
        _machine_string(self.schema_artifact_hash, _SHA256)
        if not self.input_artifact_id.startswith("syn_mh_input_fixture_"):
            raise _error(MentalHealthContractCode.INVALID_VALUE)
        if self.schema_artifact_id != "syn_mh_schema_fixture":
            raise _error(MentalHealthContractCode.INVALID_VALUE)
        _strict_enum(self.status, SyntheticExtractionStatus)
        if type(self.signals) is not tuple or len(self.signals) > MAX_SYNTHETIC_SIGNALS:
            raise _error(MentalHealthContractCode.LIMIT_EXCEEDED)
        signals = tuple(_observation(item) for item in self.signals)
        signal_codes = tuple(item.code.value for item in signals)
        if len(set(signal_codes)) != len(signal_codes):
            raise _error(MentalHealthContractCode.DUPLICATE_SIGNAL)
        if signal_codes != tuple(sorted(signal_codes)):
            raise _error(MentalHealthContractCode.INVALID_VALUE)
        if self.status is SyntheticExtractionStatus.SYNTHETIC_PARSED and not signals:
            raise _error(MentalHealthContractCode.INCONSISTENT_RESULT)
        if self.status is SyntheticExtractionStatus.SYNTHETIC_ABSTAINED and signals:
            raise _error(MentalHealthContractCode.INCONSISTENT_RESULT)
        _authority(self.authority, self.classification, self.verification)
        object.__setattr__(self, "signals", signals)
        object.__setattr__(self, "completed_at", _utc(self.completed_at))


def _result(value: object) -> SyntheticExtractionResult:
    if type(value) is not SyntheticExtractionResult:
        raise _error(MentalHealthContractCode.INVALID_TYPE)
    try:
        return SyntheticExtractionResult(
            contract_version=value.contract_version,
            result_id=value.result_id,
            request_id=value.request_id,
            input_artifact_id=value.input_artifact_id,
            input_artifact_version=value.input_artifact_version,
            input_artifact_hash=value.input_artifact_hash,
            schema_artifact_id=value.schema_artifact_id,
            schema_artifact_version=value.schema_artifact_version,
            schema_artifact_hash=value.schema_artifact_hash,
            status=value.status,
            signals=value.signals,
            completed_at=value.completed_at,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
        )
    except MentalHealthContractError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(MentalHealthContractCode.INVALID_TYPE) from None


_RESULT_FIELDS = frozenset(
    {
        "contract_version",
        "result_id",
        "request_id",
        "input_artifact_id",
        "input_artifact_version",
        "input_artifact_hash",
        "schema_artifact_id",
        "schema_artifact_version",
        "schema_artifact_hash",
        "status",
        "signals",
        "completed_at",
    }
)
_SIGNAL_FIELDS = frozenset({"code", "state"})


def _strict_fields(value: dict[str, object], expected: frozenset[str]) -> None:
    supplied = frozenset(value)
    if supplied - expected:
        raise _error(MentalHealthContractCode.UNKNOWN_FIELD)
    if expected - supplied:
        raise _error(MentalHealthContractCode.MISSING_FIELD)


def parse_synthetic_extraction_result(payload: object) -> SyntheticExtractionResult:
    """Parse one detached synthetic result without echoing rejected content."""

    if type(payload) is not dict:
        raise _error(MentalHealthContractCode.INVALID_TYPE)
    value = cast(dict[str, object], payload)
    try:
        _strict_fields(value, _RESULT_FIELDS)
        raw_signals = value["signals"]
        if type(raw_signals) is not list or len(raw_signals) > MAX_SYNTHETIC_SIGNALS:
            raise _error(MentalHealthContractCode.INVALID_TYPE)
        signals: list[SyntheticSignalObservation] = []
        for raw_signal in raw_signals:
            if type(raw_signal) is not dict:
                raise _error(MentalHealthContractCode.INVALID_TYPE)
            signal = cast(dict[str, object], raw_signal)
            _strict_fields(signal, _SIGNAL_FIELDS)
            raw_code = signal["code"]
            raw_state = signal["state"]
            if type(raw_code) is not str or type(raw_state) is not str:
                raise _error(MentalHealthContractCode.INVALID_TYPE)
            try:
                code = SyntheticSignalCode(raw_code)
                state = SyntheticSignalState(raw_state)
            except (ValueError, TypeError):
                raise _error(MentalHealthContractCode.INVALID_VALUE) from None
            signals.append(SyntheticSignalObservation(code=code, state=state))
        raw_status = value["status"]
        if type(raw_status) is not str:
            raise _error(MentalHealthContractCode.INVALID_TYPE)
        try:
            status = SyntheticExtractionStatus(raw_status)
        except (ValueError, TypeError):
            raise _error(MentalHealthContractCode.INVALID_VALUE) from None
        return SyntheticExtractionResult(
            contract_version=cast(str, value["contract_version"]),
            result_id=cast(str, value["result_id"]),
            request_id=cast(str, value["request_id"]),
            input_artifact_id=cast(str, value["input_artifact_id"]),
            input_artifact_version=cast(str, value["input_artifact_version"]),
            input_artifact_hash=cast(str, value["input_artifact_hash"]),
            schema_artifact_id=cast(str, value["schema_artifact_id"]),
            schema_artifact_version=cast(str, value["schema_artifact_version"]),
            schema_artifact_hash=cast(str, value["schema_artifact_hash"]),
            status=status,
            signals=tuple(signals),
            completed_at=_parse_utc(value["completed_at"]),
        )
    except MentalHealthContractError:
        raise
    except (KeyError, AttributeError, TypeError, ValueError, RuntimeError):
        raise _error(MentalHealthContractCode.INVALID_TYPE) from None


def validate_synthetic_result_binding(
    request: SyntheticExtractionRequest,
    result: SyntheticExtractionResult,
) -> SyntheticExtractionResult:
    """Revalidate one result and bind it to the exact synthetic request."""

    extraction_request = _request(request)
    extraction_result = _result(result)
    if (
        extraction_result.request_id != extraction_request.request_id
        or extraction_result.input_artifact_id != extraction_request.input_artifact.artifact_id
        or extraction_result.input_artifact_version
        != extraction_request.input_artifact.artifact_version
        or extraction_result.input_artifact_hash != extraction_request.input_artifact.content_hash
        or extraction_result.schema_artifact_id != extraction_request.schema_artifact.artifact_id
        or extraction_result.schema_artifact_version
        != extraction_request.schema_artifact.artifact_version
        or extraction_result.schema_artifact_hash != extraction_request.schema_artifact.content_hash
    ):
        raise _error(MentalHealthContractCode.IDENTITY_MISMATCH)
    if (
        not extraction_request.created_at
        <= extraction_result.completed_at
        <= extraction_request.deadline_at
    ):
        raise _error(MentalHealthContractCode.INVALID_CHRONOLOGY)
    return extraction_result


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticExtractionFailure:
    failure_id: str
    request_id: str
    code: SyntheticExtractionFailureCode
    occurred_at: datetime
    authority: SyntheticAuthority = SyntheticAuthority.ENGINEERING_ONLY
    classification: SyntheticClassification = SyntheticClassification.ENGINEERING_SYNTHETIC
    verification: SyntheticVerification = SyntheticVerification.UNVERIFIED

    def __post_init__(self) -> None:
        _machine_string(self.failure_id, _FAILURE_ID)
        _machine_string(self.request_id, _REQUEST_ID)
        _strict_enum(self.code, SyntheticExtractionFailureCode)
        _authority(self.authority, self.classification, self.verification)
        object.__setattr__(self, "occurred_at", _utc(self.occurred_at))

    def validate_for(self, request: SyntheticExtractionRequest) -> SyntheticExtractionFailure:
        extraction_request = _request(request)
        validated = SyntheticExtractionFailure(
            failure_id=self.failure_id,
            request_id=self.request_id,
            code=self.code,
            occurred_at=self.occurred_at,
            authority=self.authority,
            classification=self.classification,
            verification=self.verification,
        )
        if validated.request_id != extraction_request.request_id:
            raise _error(MentalHealthContractCode.IDENTITY_MISMATCH)
        if validated.code is SyntheticExtractionFailureCode.SIMULATED_TIMEOUT:
            if validated.occurred_at < extraction_request.deadline_at:
                raise _error(MentalHealthContractCode.INVALID_CHRONOLOGY)
        elif (
            not extraction_request.created_at
            <= validated.occurred_at
            <= extraction_request.deadline_at
        ):
            raise _error(MentalHealthContractCode.INVALID_CHRONOLOGY)
        return validated


__all__ = [
    "MentalHealthContractCode",
    "MentalHealthContractError",
    "SyntheticArtifactReference",
    "SyntheticAuthority",
    "SyntheticClassification",
    "SyntheticExtractionFailure",
    "SyntheticExtractionFailureCode",
    "SyntheticExtractionRequest",
    "SyntheticExtractionResult",
    "SyntheticExtractionStatus",
    "SyntheticSignalCode",
    "SyntheticSignalObservation",
    "SyntheticSignalState",
    "SyntheticVerification",
    "parse_synthetic_extraction_result",
    "validate_synthetic_result_binding",
]
