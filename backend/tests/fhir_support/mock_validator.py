"""Deterministic no-network fake for the provider-neutral FHIR validation port."""

from collections.abc import Callable
from datetime import datetime
from enum import StrEnum

from app.modules.interoperability.fhir.validation import (
    FHIRValidationIssue,
    FHIRValidationMode,
    FHIRValidationOutcome,
    SyntheticFHIRValidationRequest,
    SyntheticFHIRValidationResult,
    synthetic_fhir_mapping_fingerprint,
)


class MockValidationScenario(StrEnum):
    STRUCTURAL_PASS = "STRUCTURAL_PASS"
    STRUCTURAL_REJECT = "STRUCTURAL_REJECT"
    PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"


class DeterministicMockFHIRValidator:
    __slots__ = ("_clock", "_scenario")

    def __init__(
        self,
        *,
        scenario: MockValidationScenario,
        clock: Callable[[], datetime],
    ) -> None:
        self._scenario = scenario
        self._clock = clock

    def validate(
        self,
        request: SyntheticFHIRValidationRequest,
    ) -> SyntheticFHIRValidationResult:
        issues: tuple[FHIRValidationIssue, ...]
        if request.mode is not FHIRValidationMode.STRUCTURAL:
            outcome = FHIRValidationOutcome.SYNTHETIC_UNAVAILABLE
            issues = (FHIRValidationIssue.PROFILE_PACKAGE_UNAVAILABLE,)
        elif self._scenario is MockValidationScenario.STRUCTURAL_PASS:
            outcome = FHIRValidationOutcome.SYNTHETIC_STRUCTURAL_PASS
            issues = ()
        elif self._scenario is MockValidationScenario.STRUCTURAL_REJECT:
            outcome = FHIRValidationOutcome.SYNTHETIC_REJECTED
            issues = (FHIRValidationIssue.SYNTHETIC_STRUCTURAL_REJECTED,)
        else:
            outcome = FHIRValidationOutcome.SYNTHETIC_UNAVAILABLE
            issues = (FHIRValidationIssue.PROVIDER_UNAVAILABLE,)
        return SyntheticFHIRValidationResult(
            validation_id=request.validation_id,
            mapping_fingerprint=synthetic_fhir_mapping_fingerprint(request.mapping_result),
            mode=request.mode,
            outcome=outcome,
            issues=issues,
            completed_at=self._clock(),
        )


__all__ = ["DeterministicMockFHIRValidator", "MockValidationScenario"]
