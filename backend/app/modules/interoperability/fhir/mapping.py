"""Pure detached mapper for closed nonclinical FHIR engineering tokens."""

from app.config.settings import Environment
from app.modules.interoperability.fhir.contracts import (
    FHIRMappingCode,
    FHIRMappingDirection,
    FHIRMappingError,
    FHIRMappingResultState,
    SyntheticFHIRMappingContext,
    SyntheticFHIRMappingResult,
    SyntheticFHIRPlaceholder,
    expected_synthetic_fhir_resource,
    synthetic_fhir_context_fingerprint,
    validate_synthetic_fhir_mapping_result,
)


class SyntheticFHIRMapper:
    """Map symbolic metadata only; never map clinical fields or grant exchange authority."""

    def map(
        self,
        *,
        context: SyntheticFHIRMappingContext,
        environment: Environment,
    ) -> SyntheticFHIRMappingResult:
        if type(environment) is not Environment:
            raise FHIRMappingError(FHIRMappingCode.INVALID_TYPE)
        if environment not in {Environment.LOCAL, Environment.TEST}:
            raise FHIRMappingError(FHIRMappingCode.PROTECTED_ENVIRONMENT)
        if type(context) is not SyntheticFHIRMappingContext:
            raise FHIRMappingError(FHIRMappingCode.INVALID_TYPE)
        if len(context.sources) != 1:
            raise FHIRMappingError(FHIRMappingCode.INVALID_VALUE)

        resource_type = expected_synthetic_fhir_resource(context.sources[0].source_type)
        state = (
            FHIRMappingResultState.SYNTHETIC_EXPORT_PROJECTION
            if context.direction is FHIRMappingDirection.EXPORT
            else FHIRMappingResultState.SYNTHETIC_IMPORT_CANDIDATE
        )
        suffix = context.request_id.rsplit("_", 1)[-1]
        result = SyntheticFHIRMappingResult(
            request_id=context.request_id,
            direction=context.direction,
            state=state,
            fhir_version=context.fhir_version,
            mapping_id=context.mapping_id,
            mapping_revision=context.mapping_revision,
            resource_type=resource_type,
            logical_projection_id=f"syn_fhir_projection_{suffix}",
            placeholder=SyntheticFHIRPlaceholder.ENGINEERING_ALPHA,
            context_fingerprint=synthetic_fhir_context_fingerprint(context),
            sources=context.sources,
            transformed_at=context.transformed_at,
        )
        return validate_synthetic_fhir_mapping_result(context=context, result=result)


__all__ = ["SyntheticFHIRMapper"]
