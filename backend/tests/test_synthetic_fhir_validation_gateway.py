from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest
from fhir_support.mock_validator import (
    DeterministicMockFHIRValidator,
    MockValidationScenario,
)

from app.config.settings import Environment
from app.modules.interoperability.fhir.contracts import (
    FHIRMappingDirection,
    FHIRVersion,
    SyntheticFHIRMappingContext,
    SyntheticFHIRMappingResult,
    SyntheticFHIRSourceReference,
    SyntheticFHIRSourceType,
)
from app.modules.interoperability.fhir.mapping import SyntheticFHIRMapper
from app.modules.interoperability.fhir.validation import (
    FHIRValidationCode,
    FHIRValidationError,
    FHIRValidationIssue,
    FHIRValidationMode,
    FHIRValidationOutcome,
    SyntheticFHIRValidationGateway,
    SyntheticFHIRValidationRequest,
    SyntheticFHIRValidationResult,
)

NOW = datetime(2026, 11, 1, 16, 0, tzinfo=UTC)


def mapped() -> tuple[SyntheticFHIRMappingContext, SyntheticFHIRMappingResult]:
    context = SyntheticFHIRMappingContext(
        request_id="syn_fhir_mapping_request_alpha",
        direction=FHIRMappingDirection.EXPORT,
        fhir_version=FHIRVersion.R4_4_0_1,
        mapping_id="synthetic-fhir-r4-boundary",
        mapping_revision="engineering.v1",
        sources=(
            SyntheticFHIRSourceReference(
                source_type=SyntheticFHIRSourceType.PATIENT,
                source_id="syn_fhir_source_alpha",
                source_version="engineering.v1",
                content_hash="a" * 64,
            ),
        ),
        transformed_at=NOW,
    )
    return context, SyntheticFHIRMapper().map(context=context, environment=Environment.TEST)


def gateway(scenario: MockValidationScenario) -> SyntheticFHIRValidationGateway:
    return SyntheticFHIRValidationGateway(
        validator=DeterministicMockFHIRValidator(
            scenario=scenario,
            clock=lambda: NOW + timedelta(seconds=2),
        ),
        clock=lambda: NOW + timedelta(seconds=1),
    )


@pytest.mark.parametrize(
    ("scenario", "outcome", "issues"),
    [
        (
            MockValidationScenario.STRUCTURAL_PASS,
            FHIRValidationOutcome.SYNTHETIC_STRUCTURAL_PASS,
            (),
        ),
        (
            MockValidationScenario.STRUCTURAL_REJECT,
            FHIRValidationOutcome.SYNTHETIC_REJECTED,
            (FHIRValidationIssue.SYNTHETIC_STRUCTURAL_REJECTED,),
        ),
        (
            MockValidationScenario.PROVIDER_UNAVAILABLE,
            FHIRValidationOutcome.SYNTHETIC_UNAVAILABLE,
            (FHIRValidationIssue.PROVIDER_UNAVAILABLE,),
        ),
    ],
)
def test_structural_fake_is_deterministic_and_content_free(
    scenario: MockValidationScenario,
    outcome: FHIRValidationOutcome,
    issues: tuple[FHIRValidationIssue, ...],
) -> None:
    context, result = mapped()
    response = gateway(scenario).validate(
        context=context,
        result=result,
        mode=FHIRValidationMode.STRUCTURAL,
        environment=Environment.TEST,
    )
    assert response.outcome is outcome
    assert response.issues == issues
    assert not hasattr(response, "resource_json")
    assert not hasattr(response, "patient")


@pytest.mark.parametrize(
    "mode",
    [FHIRValidationMode.PROFILE, FHIRValidationMode.PROFILE_AND_TERMINOLOGY],
)
def test_unconfigured_profile_modes_fail_closed(mode: FHIRValidationMode) -> None:
    context, result = mapped()
    response = gateway(MockValidationScenario.STRUCTURAL_PASS).validate(
        context=context,
        result=result,
        mode=mode,
        environment=Environment.LOCAL,
    )
    assert response.outcome is FHIRValidationOutcome.SYNTHETIC_UNAVAILABLE
    assert response.issues == (FHIRValidationIssue.PROFILE_PACKAGE_UNAVAILABLE,)


def test_mapping_drift_is_rejected_before_provider_call() -> None:
    context, result = mapped()
    drifted = replace(context, transformed_at=NOW - timedelta(seconds=1))
    with pytest.raises(FHIRValidationError) as caught:
        gateway(MockValidationScenario.STRUCTURAL_PASS).validate(
            context=drifted,
            result=result,
            mode=FHIRValidationMode.STRUCTURAL,
            environment=Environment.TEST,
        )
    assert caught.value.code is FHIRValidationCode.IDENTITY_MISMATCH


def test_invalid_clock_fails_without_provider_output() -> None:
    context, result = mapped()
    service = SyntheticFHIRValidationGateway(
        validator=DeterministicMockFHIRValidator(
            scenario=MockValidationScenario.STRUCTURAL_PASS,
            clock=lambda: NOW,
        ),
        clock=lambda: datetime(2026, 11, 1, 16, 0),
    )
    with pytest.raises(FHIRValidationError) as caught:
        service.validate(
            context=context,
            result=result,
            mode=FHIRValidationMode.STRUCTURAL,
            environment=Environment.TEST,
        )
    assert caught.value.code is FHIRValidationCode.INVALID_TYPE


def test_forged_provider_identity_is_rejected() -> None:
    context, result = mapped()

    class Forged:
        def validate(
            self,
            request: SyntheticFHIRValidationRequest,
        ) -> SyntheticFHIRValidationResult:
            return SyntheticFHIRValidationResult(
                validation_id=request.validation_id,
                mapping_fingerprint="f" * 64,
                mode=request.mode,
                outcome=FHIRValidationOutcome.SYNTHETIC_STRUCTURAL_PASS,
                issues=(),
                completed_at=NOW + timedelta(seconds=2),
            )

    with pytest.raises(FHIRValidationError) as caught:
        SyntheticFHIRValidationGateway(
            validator=Forged(),
            clock=lambda: NOW + timedelta(seconds=1),
        ).validate(
            context=context,
            result=result,
            mode=FHIRValidationMode.STRUCTURAL,
            environment=Environment.TEST,
        )
    assert caught.value.code is FHIRValidationCode.IDENTITY_MISMATCH


@pytest.mark.parametrize(
    "environment",
    [Environment.STAGING, Environment.PILOT, Environment.PRODUCTION],
)
def test_protected_environment_denies_before_inputs_or_provider_are_read(
    environment: Environment,
) -> None:
    class Hostile:
        def __getattribute__(self, name: str) -> object:
            raise AssertionError(f"read:{name}")

    with pytest.raises(FHIRValidationError) as caught:
        gateway(MockValidationScenario.STRUCTURAL_PASS).validate(
            context=Hostile(),  # type: ignore[arg-type]
            result=Hostile(),  # type: ignore[arg-type]
            mode=Hostile(),  # type: ignore[arg-type]
            environment=environment,
        )
    assert caught.value.code is FHIRValidationCode.PROTECTED_ENVIRONMENT


@pytest.mark.parametrize(
    ("outcome", "issues"),
    [
        (
            FHIRValidationOutcome.SYNTHETIC_STRUCTURAL_PASS,
            (FHIRValidationIssue.PROVIDER_UNAVAILABLE,),
        ),
        (FHIRValidationOutcome.SYNTHETIC_REJECTED, ()),
    ],
)
def test_result_constructor_rejects_inconsistent_issue_shape(
    outcome: FHIRValidationOutcome,
    issues: tuple[FHIRValidationIssue, ...],
) -> None:
    with pytest.raises(FHIRValidationError) as caught:
        SyntheticFHIRValidationResult(
            validation_id="syn_fhir_validation_request_alpha",
            mapping_fingerprint="a" * 64,
            mode=FHIRValidationMode.STRUCTURAL,
            outcome=outcome,
            issues=issues,
            completed_at=NOW,
        )
    assert caught.value.code is FHIRValidationCode.INVALID_VALUE
