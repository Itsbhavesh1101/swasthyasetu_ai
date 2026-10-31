from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime, timedelta, timezone

import pytest

from app.config.settings import Environment
from app.modules.interoperability.fhir.contracts import (
    FHIRMappingCode,
    FHIRMappingDirection,
    FHIRMappingError,
    FHIRMappingResultState,
    FHIRResourceType,
    FHIRVersion,
    SyntheticFHIRMappingContext,
    SyntheticFHIRPlaceholder,
    SyntheticFHIRSourceReference,
    SyntheticFHIRSourceType,
    synthetic_fhir_context_fingerprint,
    validate_synthetic_fhir_mapping_result,
)
from app.modules.interoperability.fhir.mapping import SyntheticFHIRMapper

NOW = datetime(2026, 11, 1, 15, 0, tzinfo=UTC)
HASH = "a" * 64


def source(source_type: SyntheticFHIRSourceType) -> SyntheticFHIRSourceReference:
    return SyntheticFHIRSourceReference(
        source_type=source_type,
        source_id="syn_fhir_source_alpha",
        source_version="engineering.v1",
        content_hash=HASH,
    )


def context(
    source_type: SyntheticFHIRSourceType,
    *,
    direction: FHIRMappingDirection = FHIRMappingDirection.EXPORT,
) -> SyntheticFHIRMappingContext:
    return SyntheticFHIRMappingContext(
        request_id="syn_fhir_mapping_request_alpha",
        direction=direction,
        fhir_version=FHIRVersion.R4_4_0_1,
        mapping_id="synthetic-fhir-r4-boundary",
        mapping_revision="engineering.v1",
        sources=(source(source_type),),
        transformed_at=NOW,
    )


@pytest.mark.parametrize(
    ("source_type", "resource_type"),
    [
        (SyntheticFHIRSourceType.PATIENT, FHIRResourceType.PATIENT),
        (SyntheticFHIRSourceType.ENCOUNTER, FHIRResourceType.ENCOUNTER),
        (SyntheticFHIRSourceType.OBSERVATION, FHIRResourceType.OBSERVATION),
        (SyntheticFHIRSourceType.ALLERGY, FHIRResourceType.ALLERGY_INTOLERANCE),
        (SyntheticFHIRSourceType.MEDICATION, FHIRResourceType.MEDICATION_STATEMENT),
        (SyntheticFHIRSourceType.DIAGNOSTIC_REPORT, FHIRResourceType.DIAGNOSTIC_REPORT),
        (SyntheticFHIRSourceType.DOCUMENT_REFERENCE, FHIRResourceType.DOCUMENT_REFERENCE),
        (SyntheticFHIRSourceType.CONSENT, FHIRResourceType.CONSENT),
        (SyntheticFHIRSourceType.PROVENANCE, FHIRResourceType.PROVENANCE),
    ],
)
def test_closed_symbolic_exports_preserve_exact_source_binding(
    source_type: SyntheticFHIRSourceType,
    resource_type: FHIRResourceType,
) -> None:
    mapping_context = context(source_type)
    result = SyntheticFHIRMapper().map(
        context=mapping_context,
        environment=Environment.TEST,
    )

    assert result.state is FHIRMappingResultState.SYNTHETIC_EXPORT_PROJECTION
    assert result.resource_type is resource_type
    assert result.fhir_version is FHIRVersion.R4_4_0_1
    assert result.sources == mapping_context.sources
    assert result.context_fingerprint == synthetic_fhir_context_fingerprint(mapping_context)
    assert result.placeholder is SyntheticFHIRPlaceholder.ENGINEERING_ALPHA
    assert result.authoritative is False


def test_import_is_explicitly_non_authoritative_candidate() -> None:
    mapping_context = context(
        SyntheticFHIRSourceType.OBSERVATION,
        direction=FHIRMappingDirection.IMPORT_CANDIDATE,
    )
    result = SyntheticFHIRMapper().map(
        context=mapping_context,
        environment=Environment.LOCAL,
    )

    assert result.state is FHIRMappingResultState.SYNTHETIC_IMPORT_CANDIDATE
    assert result.authoritative is False
    assert not hasattr(result, "persist")
    assert not hasattr(result, "confirmed")


@pytest.mark.parametrize(
    "prohibited",
    [
        SyntheticFHIRSourceType.MODEL_RISK,
        SyntheticFHIRSourceType.UNCONFIRMED_EXTRACTION,
    ],
)
def test_non_authoritative_inputs_cannot_become_fhir_condition(
    prohibited: SyntheticFHIRSourceType,
) -> None:
    with pytest.raises(FHIRMappingError) as caught:
        SyntheticFHIRMapper().map(
            context=context(prohibited),
            environment=Environment.TEST,
        )

    assert caught.value.code is FHIRMappingCode.PROHIBITED_SOURCE
    assert "Condition" not in {item.value for item in FHIRResourceType}


def test_result_is_deterministic_content_free_and_revalidates() -> None:
    mapping_context = context(SyntheticFHIRSourceType.PATIENT)
    first = SyntheticFHIRMapper().map(context=mapping_context, environment=Environment.TEST)
    second = SyntheticFHIRMapper().map(context=mapping_context, environment=Environment.TEST)

    assert first == second
    assert (
        validate_synthetic_fhir_mapping_result(
            context=mapping_context,
            result=first,
        )
        == first
    )
    for forbidden in (
        "patient_name",
        "birth_date",
        "clinical_value",
        "narrative",
        "resource_json",
        "diagnosis",
    ):
        assert not hasattr(first, forbidden)


def test_cross_artifact_context_drift_is_rejected() -> None:
    mapping_context = context(SyntheticFHIRSourceType.PATIENT)
    result = SyntheticFHIRMapper().map(context=mapping_context, environment=Environment.TEST)
    drifted = replace(mapping_context, transformed_at=NOW + timedelta(seconds=1))

    with pytest.raises(FHIRMappingError) as caught:
        validate_synthetic_fhir_mapping_result(context=drifted, result=result)

    assert caught.value.code is FHIRMappingCode.IDENTITY_MISMATCH


def test_contracts_are_frozen_and_normalize_aware_time_to_utc() -> None:
    aware = NOW.astimezone(timezone(timedelta(hours=5, minutes=30)))
    mapping_context = replace(
        context(SyntheticFHIRSourceType.ENCOUNTER),
        transformed_at=aware,
    )
    assert mapping_context.transformed_at == NOW
    with pytest.raises(FrozenInstanceError):
        mapping_context.request_id = "syn_fhir_mapping_request_beta"  # type: ignore[misc]


@pytest.mark.parametrize(
    "invalid_time",
    [datetime(2026, 11, 1, 15, 0), "2026-11-01T15:00:00Z"],
)
def test_context_rejects_naive_or_string_timestamp(invalid_time: object) -> None:
    with pytest.raises(FHIRMappingError) as caught:
        SyntheticFHIRMappingContext(
            request_id="syn_fhir_mapping_request_alpha",
            direction=FHIRMappingDirection.EXPORT,
            fhir_version=FHIRVersion.R4_4_0_1,
            mapping_id="synthetic-fhir-r4-boundary",
            mapping_revision="engineering.v1",
            sources=(source(SyntheticFHIRSourceType.PATIENT),),
            transformed_at=invalid_time,  # type: ignore[arg-type]
        )
    assert caught.value.code is FHIRMappingCode.INVALID_TYPE


def test_context_rejects_empty_duplicate_and_unsorted_sources() -> None:
    with pytest.raises(FHIRMappingError) as empty:
        replace(context(SyntheticFHIRSourceType.PATIENT), sources=())
    assert empty.value.code is FHIRMappingCode.INVALID_VALUE

    one = source(SyntheticFHIRSourceType.PATIENT)
    with pytest.raises(FHIRMappingError) as duplicate:
        replace(context(SyntheticFHIRSourceType.PATIENT), sources=(one, one))
    assert duplicate.value.code is FHIRMappingCode.DUPLICATE_SOURCE

    two = replace(
        source(SyntheticFHIRSourceType.ENCOUNTER),
        source_id="syn_fhir_source_beta",
    )
    with pytest.raises(FHIRMappingError) as unsorted:
        replace(context(SyntheticFHIRSourceType.PATIENT), sources=(one, two))
    assert unsorted.value.code is FHIRMappingCode.INVALID_VALUE


def test_result_direct_constructor_rejects_authority_upgrade() -> None:
    result = SyntheticFHIRMapper().map(
        context=context(SyntheticFHIRSourceType.CONSENT),
        environment=Environment.TEST,
    )
    with pytest.raises(FHIRMappingError) as caught:
        replace(result, authoritative=True)
    assert caught.value.code is FHIRMappingCode.INVALID_VALUE


@pytest.mark.parametrize(
    "environment",
    [Environment.STAGING, Environment.PILOT, Environment.PRODUCTION],
)
def test_protected_environment_denies_before_context_is_read(
    environment: Environment,
) -> None:
    class Hostile:
        def __getattribute__(self, name: str) -> object:
            raise AssertionError(f"context-read:{name}")

    with pytest.raises(FHIRMappingError) as caught:
        SyntheticFHIRMapper().map(
            context=Hostile(),  # type: ignore[arg-type]
            environment=environment,
        )
    assert caught.value.code is FHIRMappingCode.PROTECTED_ENVIRONMENT


def test_plain_strings_cannot_impersonate_closed_contract_enums() -> None:
    with pytest.raises(FHIRMappingError) as caught:
        replace(
            context(SyntheticFHIRSourceType.PATIENT),
            fhir_version="R4_4_0_1",  # type: ignore[arg-type]
        )
    assert caught.value.code is FHIRMappingCode.INVALID_TYPE
