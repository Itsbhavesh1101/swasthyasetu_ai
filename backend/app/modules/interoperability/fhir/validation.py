"""Provider-neutral, content-free validation contracts for synthetic FHIR mechanics."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from app.config.settings import Environment
from app.modules.interoperability.fhir.contracts import (
    FHIRMappingCode,
    FHIRMappingError,
    SyntheticFHIRMappingContext,
    SyntheticFHIRMappingResult,
    validate_synthetic_fhir_mapping_result,
)

_VALIDATION_ID = re.compile(r"^syn_fhir_validation_request_(?:alpha|beta|gamma|delta)$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")


class FHIRValidationCode(StrEnum):
    INVALID_TYPE = "INVALID_TYPE"
    INVALID_VALUE = "INVALID_VALUE"
    IDENTITY_MISMATCH = "IDENTITY_MISMATCH"
    PROVIDER_FAILURE = "PROVIDER_FAILURE"
    PROTECTED_ENVIRONMENT = "PROTECTED_ENVIRONMENT"


class FHIRValidationError(ValueError):
    """Stable content-free failure at the synthetic validation boundary."""

    def __init__(self, code: FHIRValidationCode) -> None:
        self.code = code
        super().__init__(code.value)


def _error(code: FHIRValidationCode) -> FHIRValidationError:
    return FHIRValidationError(code)


class FHIRValidationMode(StrEnum):
    STRUCTURAL = "STRUCTURAL"
    PROFILE = "PROFILE"
    PROFILE_AND_TERMINOLOGY = "PROFILE_AND_TERMINOLOGY"


class FHIRValidationOutcome(StrEnum):
    SYNTHETIC_STRUCTURAL_PASS = "SYNTHETIC_STRUCTURAL_PASS"
    SYNTHETIC_REJECTED = "SYNTHETIC_REJECTED"
    SYNTHETIC_UNAVAILABLE = "SYNTHETIC_UNAVAILABLE"


class FHIRValidationIssue(StrEnum):
    SYNTHETIC_STRUCTURAL_REJECTED = "SYNTHETIC_STRUCTURAL_REJECTED"
    PROFILE_PACKAGE_UNAVAILABLE = "PROFILE_PACKAGE_UNAVAILABLE"
    PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"


def _strict_enum(value: object, expected: type[StrEnum]) -> None:
    if type(value) is not expected:
        raise _error(FHIRValidationCode.INVALID_TYPE)


def _utc(value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise _error(FHIRValidationCode.INVALID_TYPE)
    return value.astimezone(UTC)


def _machine_string(value: object, pattern: re.Pattern[str]) -> str:
    if type(value) is not str:
        raise _error(FHIRValidationCode.INVALID_TYPE)
    if pattern.fullmatch(value) is None:
        raise _error(FHIRValidationCode.INVALID_VALUE)
    return value


def synthetic_fhir_mapping_fingerprint(result: SyntheticFHIRMappingResult) -> str:
    if type(result) is not SyntheticFHIRMappingResult:
        raise _error(FHIRValidationCode.INVALID_TYPE)
    fields = (
        result.request_id,
        result.direction.value,
        result.state.value,
        result.fhir_version.value,
        result.mapping_id,
        result.mapping_revision,
        result.resource_type.value,
        result.logical_projection_id,
        result.placeholder.value,
        result.context_fingerprint,
        result.transformed_at.isoformat(),
        result.authority.value,
        result.verification.value,
    )
    return sha256("\x1f".join(fields).encode("ascii")).hexdigest()


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticFHIRValidationRequest:
    validation_id: str
    mapping_context: SyntheticFHIRMappingContext
    mapping_result: SyntheticFHIRMappingResult
    mode: FHIRValidationMode
    requested_at: datetime

    def __post_init__(self) -> None:
        _machine_string(self.validation_id, _VALIDATION_ID)
        _strict_enum(self.mode, FHIRValidationMode)
        requested_at = _utc(self.requested_at)
        try:
            result = validate_synthetic_fhir_mapping_result(
                context=self.mapping_context,
                result=self.mapping_result,
            )
        except FHIRMappingError as exc:
            code = (
                FHIRValidationCode.IDENTITY_MISMATCH
                if exc.code is FHIRMappingCode.IDENTITY_MISMATCH
                else FHIRValidationCode.INVALID_VALUE
            )
            raise _error(code) from None
        if requested_at < result.transformed_at:
            raise _error(FHIRValidationCode.INVALID_VALUE)
        object.__setattr__(self, "mapping_result", result)
        object.__setattr__(self, "requested_at", requested_at)


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticFHIRValidationResult:
    validation_id: str
    mapping_fingerprint: str
    mode: FHIRValidationMode
    outcome: FHIRValidationOutcome
    issues: tuple[FHIRValidationIssue, ...]
    completed_at: datetime

    def __post_init__(self) -> None:
        _machine_string(self.validation_id, _VALIDATION_ID)
        _machine_string(self.mapping_fingerprint, _SHA256)
        _strict_enum(self.mode, FHIRValidationMode)
        _strict_enum(self.outcome, FHIRValidationOutcome)
        if type(self.issues) is not tuple:
            raise _error(FHIRValidationCode.INVALID_TYPE)
        for issue in self.issues:
            _strict_enum(issue, FHIRValidationIssue)
        values = tuple(issue.value for issue in self.issues)
        if len(set(values)) != len(values) or values != tuple(sorted(values)):
            raise _error(FHIRValidationCode.INVALID_VALUE)
        if (self.outcome is FHIRValidationOutcome.SYNTHETIC_STRUCTURAL_PASS) != (not self.issues):
            raise _error(FHIRValidationCode.INVALID_VALUE)
        if (
            self.outcome is FHIRValidationOutcome.SYNTHETIC_STRUCTURAL_PASS
            and self.mode is not FHIRValidationMode.STRUCTURAL
        ):
            raise _error(FHIRValidationCode.INVALID_VALUE)
        completed_at = _utc(self.completed_at)
        object.__setattr__(self, "issues", tuple(self.issues))
        object.__setattr__(self, "completed_at", completed_at)


@runtime_checkable
class FHIRValidationPort(Protocol):
    """Provider-neutral port; implementations cannot grant clinical or exchange authority."""

    def validate(
        self,
        request: SyntheticFHIRValidationRequest,
    ) -> SyntheticFHIRValidationResult: ...


Clock = Callable[[], datetime]


class SyntheticFHIRValidationGateway:
    """Offline validator orchestrator with no transport, persistence, or authorization role."""

    __slots__ = ("_clock", "_validator")

    def __init__(self, *, validator: FHIRValidationPort, clock: Clock) -> None:
        if not isinstance(validator, FHIRValidationPort):
            raise TypeError("validator must implement FHIRValidationPort")
        if not callable(clock):
            raise TypeError("clock must be callable")
        self._validator = validator
        self._clock = clock

    def validate(
        self,
        *,
        context: SyntheticFHIRMappingContext,
        result: SyntheticFHIRMappingResult,
        mode: FHIRValidationMode,
        environment: Environment,
    ) -> SyntheticFHIRValidationResult:
        if type(environment) is not Environment:
            raise _error(FHIRValidationCode.INVALID_TYPE)
        if environment not in {Environment.LOCAL, Environment.TEST}:
            raise _error(FHIRValidationCode.PROTECTED_ENVIRONMENT)
        now = self._controlled_now()
        suffix = result.request_id.rsplit("_", 1)[-1]
        request = SyntheticFHIRValidationRequest(
            validation_id=f"syn_fhir_validation_request_{suffix}",
            mapping_context=context,
            mapping_result=result,
            mode=mode,
            requested_at=now,
        )
        try:
            response = self._validator.validate(request)
        except FHIRValidationError:
            raise
        except Exception:
            raise _error(FHIRValidationCode.PROVIDER_FAILURE) from None
        if type(response) is not SyntheticFHIRValidationResult:
            raise _error(FHIRValidationCode.PROVIDER_FAILURE)
        expected_fingerprint = synthetic_fhir_mapping_fingerprint(request.mapping_result)
        if (
            response.validation_id != request.validation_id
            or response.mapping_fingerprint != expected_fingerprint
            or response.mode is not request.mode
            or response.completed_at < request.requested_at
        ):
            raise _error(FHIRValidationCode.IDENTITY_MISMATCH)
        return response

    def _controlled_now(self) -> datetime:
        try:
            value = self._clock()
            return _utc(value)
        except FHIRValidationError:
            raise
        except Exception:
            raise _error(FHIRValidationCode.INVALID_VALUE) from None


__all__ = [
    "FHIRValidationCode",
    "FHIRValidationError",
    "FHIRValidationIssue",
    "FHIRValidationMode",
    "FHIRValidationOutcome",
    "FHIRValidationPort",
    "SyntheticFHIRValidationGateway",
    "SyntheticFHIRValidationRequest",
    "SyntheticFHIRValidationResult",
    "synthetic_fhir_mapping_fingerprint",
]
