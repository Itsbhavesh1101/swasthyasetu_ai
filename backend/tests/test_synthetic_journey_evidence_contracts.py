from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta, timezone

import pytest

from app.validation.contracts import (
    SYNTHETIC_JOURNEY_EVIDENCE_CONTRACT_VERSION,
    JourneyEvidenceAuthority,
    JourneyEvidenceClassification,
    JourneyEvidenceContractCode,
    JourneyEvidenceContractError,
    JourneyEvidenceVerification,
    SyntheticEvidenceDisposition,
    SyntheticEvidenceReason,
    SyntheticJourneyDefinition,
    SyntheticJourneyEvidenceReceipt,
    SyntheticJourneyId,
    SyntheticJourneyManifest,
    SyntheticJourneyObservation,
    SyntheticJourneyReadiness,
    SyntheticObservationState,
    snapshot_journey_definition,
    snapshot_journey_evidence_receipt,
    snapshot_journey_manifest,
    snapshot_journey_observation,
)

HASH_A = "a" * 64
HASH_B = "b" * 64
HASH_C = "c" * 64
BUILD_SHA = "d" * 40
NOW = datetime(2026, 11, 1, 10, 0, tzinfo=UTC)

EXPECTED_JOURNEYS = {
    "STRUCTURED_CLINICAL_INTAKE",
    "CONVERSATIONAL_INTAKE",
    "DOCUMENT_UPLOAD_EXTRACTION",
    "RED_FLAG_URGENT_ROUTE",
    "SELF_CARE_ELIGIBLE",
    "SELF_CARE_BLOCKED",
    "DOCTOR_SEARCH",
    "REFERRAL_LIFECYCLE",
    "CLINICIAN_CONFIRMATION",
    "MENTAL_HEALTH_ROUTE_A",
    "MENTAL_HEALTH_ROUTE_B_REFERRAL",
    "MENTAL_HEALTH_ROUTE_C_CRISIS_FALLBACK",
    "LLM_OUTAGE",
    "OCR_OUTAGE",
    "SPEECH_FALLBACK",
    "FHIR_EXPORT",
    "CLASSICAL_MODEL_RESEARCH_RUN",
    "QML_RESEARCH_RUN",
}


def definition(
    journey_id: SyntheticJourneyId = SyntheticJourneyId.STRUCTURED_CLINICAL_INTAKE,
    *,
    readiness: SyntheticJourneyReadiness = SyntheticJourneyReadiness.BOUNDED_P7_TECHNICAL_ONLY,
) -> SyntheticJourneyDefinition:
    return SyntheticJourneyDefinition(
        journey_id=journey_id,
        definition_version="engineering.v1",
        fixture_hash=HASH_A,
        oracle_hash=HASH_B,
        readiness=readiness,
        created_at=NOW,
    )


def observation(
    item: SyntheticJourneyDefinition | None = None,
    *,
    journey_id: SyntheticJourneyId | None = None,
    definition_fingerprint: str | None = None,
    fixture_hash: str | None = None,
) -> SyntheticJourneyObservation:
    safe_item = item or definition()
    return SyntheticJourneyObservation(
        observation_id="syn_journey_observation_alpha",
        journey_id=journey_id or safe_item.journey_id,
        definition_fingerprint=definition_fingerprint or safe_item.fingerprint,
        build_sha=BUILD_SHA,
        config_hash=HASH_C,
        fixture_hash=fixture_hash or safe_item.fixture_hash,
        oracle_hash=safe_item.oracle_hash,
        state=SyntheticObservationState.METADATA_RECORDED,
        captured_at=NOW + timedelta(minutes=1),
    )


def receipt(
    item: SyntheticJourneyDefinition | None = None,
    observed: SyntheticJourneyObservation | None = None,
) -> SyntheticJourneyEvidenceReceipt:
    safe_item = item or definition()
    safe_observed = observed or observation(safe_item)
    return SyntheticJourneyEvidenceReceipt(
        definition=safe_item,
        observation=safe_observed,
        disposition=SyntheticEvidenceDisposition.EVIDENCE_CONSISTENT,
        reason=SyntheticEvidenceReason.EXACT_SYNTHETIC_METADATA,
        evaluated_at=NOW + timedelta(minutes=2),
    )


def all_definitions() -> tuple[SyntheticJourneyDefinition, ...]:
    return tuple(
        definition(
            journey_id,
            readiness=(
                SyntheticJourneyReadiness.BOUNDED_P7_TECHNICAL_ONLY
                if journey_id is SyntheticJourneyId.STRUCTURED_CLINICAL_INTAKE
                else SyntheticJourneyReadiness.BLOCKED_UNAPPROVED
            ),
        )
        for journey_id in sorted(SyntheticJourneyId, key=lambda value: value.value)
    )


def manifest(
    definitions: tuple[SyntheticJourneyDefinition, ...] | None = None,
) -> SyntheticJourneyManifest:
    return SyntheticJourneyManifest(
        manifest_id="syn_journey_manifest_alpha",
        generated_at=NOW + timedelta(minutes=3),
        definitions=definitions or all_definitions(),
    )


def test_inventory_is_closed_to_the_exact_eighteen_canonical_journeys() -> None:
    assert {item.value for item in SyntheticJourneyId} == EXPECTED_JOURNEYS
    assert len(SyntheticJourneyId) == 18


def test_definition_normalizes_aware_time_and_has_engineering_only_labels() -> None:
    non_utc = NOW.astimezone(timezone(timedelta(hours=5, minutes=30)))
    item = SyntheticJourneyDefinition(
        journey_id=SyntheticJourneyId.STRUCTURED_CLINICAL_INTAKE,
        definition_version="engineering.v7",
        fixture_hash=HASH_A,
        oracle_hash=HASH_B,
        readiness=SyntheticJourneyReadiness.BOUNDED_P7_TECHNICAL_ONLY,
        created_at=non_utc,
    )

    assert item.created_at == NOW
    assert item.created_at.tzinfo is UTC
    assert item.authority is JourneyEvidenceAuthority.ENGINEERING_ONLY
    assert item.classification is JourneyEvidenceClassification.ENGINEERING_SYNTHETIC
    assert item.verification is JourneyEvidenceVerification.UNVERIFIED
    assert item.contract_version == SYNTHETIC_JOURNEY_EVIDENCE_CONTRACT_VERSION


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("journey_id", "STRUCTURED_CLINICAL_INTAKE"),
        ("definition_version", "latest"),
        ("fixture_hash", "not-a-hash"),
        ("oracle_hash", "A" * 64),
        ("readiness", "BLOCKED_UNAPPROVED"),
        ("created_at", NOW.replace(tzinfo=None)),
    ],
)
def test_definition_rejects_loose_or_malformed_values(field: str, value: object) -> None:
    values: dict[str, object] = {
        "journey_id": SyntheticJourneyId.STRUCTURED_CLINICAL_INTAKE,
        "definition_version": "engineering.v1",
        "fixture_hash": HASH_A,
        "oracle_hash": HASH_B,
        "readiness": SyntheticJourneyReadiness.BOUNDED_P7_TECHNICAL_ONLY,
        "created_at": NOW,
    }
    values[field] = value

    with pytest.raises(JourneyEvidenceContractError):
        SyntheticJourneyDefinition(**values)  # type: ignore[arg-type]


def test_only_structured_intake_can_use_the_bounded_p7_readiness() -> None:
    with pytest.raises(JourneyEvidenceContractError) as captured:
        definition(SyntheticJourneyId.CONVERSATIONAL_INTAKE)

    assert captured.value.code is JourneyEvidenceContractCode.INVALID_READINESS


def test_observation_binds_exact_machine_shaped_metadata() -> None:
    item = definition()
    observed = observation(item)

    assert observed.journey_id is item.journey_id
    assert observed.definition_fingerprint == item.fingerprint
    assert observed.build_sha == BUILD_SHA
    assert observed.state is SyntheticObservationState.METADATA_RECORDED
    assert len(observed.fingerprint) == 64


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("observation_id", "patient-123"),
        ("journey_id", "STRUCTURED_CLINICAL_INTAKE"),
        ("definition_fingerprint", "x" * 64),
        ("build_sha", "d" * 39),
        ("config_hash", "c" * 63),
        ("state", "METADATA_RECORDED"),
        ("captured_at", NOW.replace(tzinfo=None)),
    ],
)
def test_observation_rejects_malformed_or_loose_values(field: str, value: object) -> None:
    item = definition()
    values: dict[str, object] = {
        "observation_id": "syn_journey_observation_alpha",
        "journey_id": item.journey_id,
        "definition_fingerprint": item.fingerprint,
        "build_sha": BUILD_SHA,
        "config_hash": HASH_C,
        "fixture_hash": item.fixture_hash,
        "oracle_hash": item.oracle_hash,
        "state": SyntheticObservationState.METADATA_RECORDED,
        "captured_at": NOW + timedelta(minutes=1),
    }
    values[field] = value

    with pytest.raises(JourneyEvidenceContractError):
        SyntheticJourneyObservation(**values)  # type: ignore[arg-type]


def test_exact_receipt_reconstructs_nested_inputs_and_is_immutable() -> None:
    result = receipt()

    assert result.disposition is SyntheticEvidenceDisposition.EVIDENCE_CONSISTENT
    assert result.reason is SyntheticEvidenceReason.EXACT_SYNTHETIC_METADATA
    assert result.observation is not None
    with pytest.raises(FrozenInstanceError):
        result.reason = SyntheticEvidenceReason.SCOPE_MISMATCH  # type: ignore[misc]


def test_receipt_direct_constructor_rejects_forged_disposition() -> None:
    item = definition()
    mismatched = observation(item, fixture_hash=HASH_C)

    with pytest.raises(JourneyEvidenceContractError) as captured:
        SyntheticJourneyEvidenceReceipt(
            definition=item,
            observation=mismatched,
            disposition=SyntheticEvidenceDisposition.EVIDENCE_CONSISTENT,
            reason=SyntheticEvidenceReason.EXACT_SYNTHETIC_METADATA,
            evaluated_at=NOW + timedelta(minutes=2),
        )

    assert captured.value.code is JourneyEvidenceContractCode.INCONSISTENT_RECEIPT


def test_blocked_receipt_requires_no_observation_and_abstention() -> None:
    item = definition(
        SyntheticJourneyId.CONVERSATIONAL_INTAKE,
        readiness=SyntheticJourneyReadiness.BLOCKED_UNAPPROVED,
    )
    result = SyntheticJourneyEvidenceReceipt(
        definition=item,
        observation=None,
        disposition=SyntheticEvidenceDisposition.ABSTAINED,
        reason=SyntheticEvidenceReason.JOURNEY_BLOCKED,
        evaluated_at=NOW + timedelta(minutes=1),
    )

    assert result.observation is None
    assert result.reason is SyntheticEvidenceReason.JOURNEY_BLOCKED


def test_receipt_rejects_invalid_chronology() -> None:
    item = definition()
    observed = observation(item)

    with pytest.raises(JourneyEvidenceContractError) as captured:
        SyntheticJourneyEvidenceReceipt(
            definition=item,
            observation=observed,
            disposition=SyntheticEvidenceDisposition.EVIDENCE_CONSISTENT,
            reason=SyntheticEvidenceReason.EXACT_SYNTHETIC_METADATA,
            evaluated_at=NOW,
        )

    assert captured.value.code is JourneyEvidenceContractCode.INVALID_CHRONOLOGY


def test_manifest_requires_exact_canonical_inventory_and_order() -> None:
    result = manifest()

    assert len(result.definitions) == 18
    assert tuple(item.journey_id.value for item in result.definitions) == tuple(
        sorted(EXPECTED_JOURNEYS)
    )
    assert len(result.fingerprint) == 64


@pytest.mark.parametrize(
    "definitions", [all_definitions()[:-1], all_definitions() + all_definitions()[:1]]
)
def test_manifest_rejects_missing_or_duplicate_journeys(
    definitions: tuple[SyntheticJourneyDefinition, ...],
) -> None:
    with pytest.raises(JourneyEvidenceContractError):
        manifest(definitions)


def test_manifest_rejects_wrong_readiness_snapshot() -> None:
    definitions = tuple(
        definition(journey_id, readiness=SyntheticJourneyReadiness.BLOCKED_UNAPPROVED)
        for journey_id in sorted(SyntheticJourneyId, key=lambda value: value.value)
    )

    with pytest.raises(JourneyEvidenceContractError) as captured:
        manifest(definitions)

    assert captured.value.code is JourneyEvidenceContractCode.INVALID_READINESS


def test_snapshot_helpers_reject_forced_mutation() -> None:
    item = definition()
    observed = observation(item)
    result = receipt(item, observed)
    inventory = manifest()
    object.__setattr__(item, "fixture_hash", HASH_C)
    object.__setattr__(observed, "config_hash", HASH_A)
    object.__setattr__(result, "evaluated_at", NOW)
    object.__setattr__(inventory, "generated_at", NOW)

    for value, snapshot in (
        (item, snapshot_journey_definition),
        (observed, snapshot_journey_observation),
        (result, snapshot_journey_evidence_receipt),
        (inventory, snapshot_journey_manifest),
    ):
        with pytest.raises(JourneyEvidenceContractError):
            snapshot(value)


def test_errors_are_stable_and_do_not_echo_hostile_values() -> None:
    hostile = "secret-bearer-patient@example.test"

    with pytest.raises(JourneyEvidenceContractError) as captured:
        SyntheticJourneyObservation(
            observation_id=hostile,
            journey_id=SyntheticJourneyId.STRUCTURED_CLINICAL_INTAKE,
            definition_fingerprint=HASH_A,
            build_sha=BUILD_SHA,
            config_hash=HASH_B,
            fixture_hash=HASH_A,
            oracle_hash=HASH_B,
            state=SyntheticObservationState.METADATA_RECORDED,
            captured_at=NOW,
        )

    assert str(captured.value) == captured.value.code.value
    assert hostile not in str(captured.value)
