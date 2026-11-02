"""Deterministic, content-free P16 engineering demonstration."""

from dataclasses import dataclass
from datetime import UTC, datetime

from app.config.settings import Environment
from app.modules.interoperability.fhir.contracts import (
    FHIRMappingCode,
    FHIRMappingDirection,
    FHIRMappingError,
    FHIRVersion,
    SyntheticFHIRMappingContext,
    SyntheticFHIRSourceReference,
    SyntheticFHIRSourceType,
)
from app.modules.interoperability.fhir.mapping import SyntheticFHIRMapper
from app.modules.interoperability.fhir.validation import (
    FHIRValidationIssue,
    FHIRValidationMode,
    FHIRValidationOutcome,
    SyntheticFHIRValidationGateway,
    SyntheticFHIRValidationRequest,
    SyntheticFHIRValidationResult,
    synthetic_fhir_mapping_fingerprint,
)

_DEMO_TIME = datetime(2026, 11, 1, 12, tzinfo=UTC)


@dataclass(frozen=True, slots=True)
class EngineeringFHIRPreviewResult:
    classification: str
    authority: str
    verification: str
    fhir_version: str
    mapping_direction: str
    mapping_state: str
    resource_type: str
    structural_validation: str
    profile_validation: str
    profile_issue: str
    fhir_payload_present: bool
    patient_data_processed: bool
    profile_conformance_claimed: bool
    exchange_authorized: bool
    external_transport: bool
    abdm_invoked: bool
    persistence_written: bool
    notice: str


class _DeterministicEngineeringValidator:
    """Content-free local/test validator; it never parses or emits a FHIR resource."""

    def validate(
        self,
        request: SyntheticFHIRValidationRequest,
    ) -> SyntheticFHIRValidationResult:
        if request.mode is FHIRValidationMode.STRUCTURAL:
            outcome = FHIRValidationOutcome.SYNTHETIC_STRUCTURAL_PASS
            issues: tuple[FHIRValidationIssue, ...] = ()
        else:
            outcome = FHIRValidationOutcome.SYNTHETIC_UNAVAILABLE
            issues = (FHIRValidationIssue.PROFILE_PACKAGE_UNAVAILABLE,)
        return SyntheticFHIRValidationResult(
            validation_id=request.validation_id,
            mapping_fingerprint=synthetic_fhir_mapping_fingerprint(request.mapping_result),
            mode=request.mode,
            outcome=outcome,
            issues=issues,
            completed_at=_DEMO_TIME,
        )


class EngineeringFHIRDemoService:
    """Compose reviewed mapping and validation mechanics over fixed toy symbols."""

    def __init__(self, *, environment: Environment) -> None:
        if type(environment) is not Environment:
            raise TypeError("environment must be an Environment")
        self._environment = environment

    def project(self) -> EngineeringFHIRPreviewResult:
        if self._environment not in {Environment.LOCAL, Environment.TEST}:
            raise FHIRMappingError(FHIRMappingCode.PROTECTED_ENVIRONMENT)
        context = SyntheticFHIRMappingContext(
            request_id="syn_fhir_mapping_request_alpha",
            direction=FHIRMappingDirection.EXPORT,
            fhir_version=FHIRVersion.R4_4_0_1,
            mapping_id="synthetic-fhir-r4-boundary",
            mapping_revision="engineering.v1",
            sources=(
                SyntheticFHIRSourceReference(
                    source_type=SyntheticFHIRSourceType.OBSERVATION,
                    source_id="syn_fhir_source_alpha",
                    source_version="engineering.v1",
                    content_hash="a" * 64,
                ),
            ),
            transformed_at=_DEMO_TIME,
        )
        mapping = SyntheticFHIRMapper().map(
            context=context,
            environment=self._environment,
        )
        gateway = SyntheticFHIRValidationGateway(
            validator=_DeterministicEngineeringValidator(),
            clock=lambda: _DEMO_TIME,
        )
        structural = gateway.validate(
            context=context,
            result=mapping,
            mode=FHIRValidationMode.STRUCTURAL,
            environment=self._environment,
        )
        profile = gateway.validate(
            context=context,
            result=mapping,
            mode=FHIRValidationMode.PROFILE,
            environment=self._environment,
        )
        if (
            structural.outcome is not FHIRValidationOutcome.SYNTHETIC_STRUCTURAL_PASS
            or structural.issues
            or profile.outcome is not FHIRValidationOutcome.SYNTHETIC_UNAVAILABLE
            or profile.issues != (FHIRValidationIssue.PROFILE_PACKAGE_UNAVAILABLE,)
        ):
            raise RuntimeError("synthetic FHIR composition invariant failed")
        return EngineeringFHIRPreviewResult(
            classification="ENGINEERING_SYNTHETIC",
            authority=mapping.authority.value,
            verification=mapping.verification.value,
            fhir_version=mapping.fhir_version.value,
            mapping_direction=mapping.direction.value,
            mapping_state=mapping.state.value,
            resource_type=mapping.resource_type.value,
            structural_validation=structural.outcome.value,
            profile_validation=profile.outcome.value,
            profile_issue=profile.issues[0].value,
            fhir_payload_present=False,
            patient_data_processed=False,
            profile_conformance_claimed=False,
            exchange_authorized=False,
            external_transport=False,
            abdm_invoked=False,
            persistence_written=False,
            notice=(
                "Synthetic engineering metadata only. Structural mechanics are not profile "
                "conformance, no FHIR payload or patient data is processed, and no exchange, "
                "external transport, ABDM integration, or persistence occurs."
            ),
        )
