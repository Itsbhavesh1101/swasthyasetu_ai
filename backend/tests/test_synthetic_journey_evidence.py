from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from app.config import Environment
from app.validation import (
    JourneyEvidenceContractCode,
    JourneyEvidenceContractError,
    SyntheticEvidenceDisposition,
    SyntheticEvidenceReason,
    SyntheticJourneyDefinition,
    SyntheticJourneyId,
    SyntheticJourneyObservation,
    SyntheticJourneyReadiness,
    SyntheticObservationState,
    build_synthetic_journey_manifest,
    evaluate_synthetic_journey_evidence,
)

HASH_A = "a" * 64
HASH_B = "b" * 64
HASH_C = "c" * 64
BUILD_SHA = "d" * 40
NOW = datetime(2026, 11, 1, 11, 0, tzinfo=UTC)


class HostileInput:
    def __getattribute__(self, name: str) -> object:
        raise AssertionError(f"hostile input was inspected: {name}")

    def __iter__(self) -> object:
        raise AssertionError("hostile input was iterated")

    def __len__(self) -> int:
        raise AssertionError("hostile input length was read")


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
    item: SyntheticJourneyDefinition,
    *,
    fixture_hash: str | None = None,
) -> SyntheticJourneyObservation:
    return SyntheticJourneyObservation(
        observation_id="syn_journey_observation_alpha",
        journey_id=item.journey_id,
        definition_fingerprint=item.fingerprint,
        build_sha=BUILD_SHA,
        config_hash=HASH_C,
        fixture_hash=fixture_hash or item.fixture_hash,
        oracle_hash=item.oracle_hash,
        state=SyntheticObservationState.METADATA_RECORDED,
        captured_at=NOW + timedelta(minutes=1),
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
        for journey_id in reversed(tuple(SyntheticJourneyId))
    )


def test_manifest_builder_canonicalizes_all_eighteen_definitions() -> None:
    result = build_synthetic_journey_manifest(
        all_definitions(),
        manifest_id="syn_journey_manifest_alpha",
        generated_at=NOW + timedelta(minutes=2),
        environment=Environment.TEST,
    )

    assert len(result.definitions) == 18
    assert tuple(item.journey_id.value for item in result.definitions) == tuple(
        sorted(item.value for item in SyntheticJourneyId)
    )


def test_manifest_builder_is_deterministic_for_input_order() -> None:
    first = build_synthetic_journey_manifest(
        all_definitions(),
        manifest_id="syn_journey_manifest_alpha",
        generated_at=NOW + timedelta(minutes=2),
        environment=Environment.LOCAL,
    )
    second = build_synthetic_journey_manifest(
        tuple(reversed(all_definitions())),
        manifest_id="syn_journey_manifest_alpha",
        generated_at=NOW + timedelta(minutes=2),
        environment=Environment.LOCAL,
    )

    assert first == second
    assert first.fingerprint == second.fingerprint


@pytest.mark.parametrize(
    "environment", [Environment.STAGING, Environment.PILOT, Environment.PRODUCTION]
)
def test_manifest_builder_rejects_protected_environment_before_input_inspection(
    environment: Environment,
) -> None:
    with pytest.raises(JourneyEvidenceContractError) as captured:
        build_synthetic_journey_manifest(
            HostileInput(),  # type: ignore[arg-type]
            manifest_id="syn_journey_manifest_alpha",
            generated_at=NOW,
            environment=environment,
        )

    assert captured.value.code is JourneyEvidenceContractCode.PROTECTED_ENVIRONMENT


def test_exact_observation_returns_consistent_metadata_not_a_pass() -> None:
    item = definition()
    result = evaluate_synthetic_journey_evidence(
        item,
        observation(item),
        evaluated_at=NOW + timedelta(minutes=2),
        environment=Environment.TEST,
    )

    assert result.disposition is SyntheticEvidenceDisposition.EVIDENCE_CONSISTENT
    assert result.reason is SyntheticEvidenceReason.EXACT_SYNTHETIC_METADATA
    assert "PASS" not in result.disposition.value


def test_scope_drift_abstains_without_echoing_evidence() -> None:
    item = definition()
    drifted = observation(item, fixture_hash=HASH_C)

    result = evaluate_synthetic_journey_evidence(
        item,
        drifted,
        evaluated_at=NOW + timedelta(minutes=2),
        environment=Environment.LOCAL,
    )

    assert result.disposition is SyntheticEvidenceDisposition.ABSTAINED
    assert result.reason is SyntheticEvidenceReason.SCOPE_MISMATCH
    assert HASH_C not in str(result)


def test_blocked_journey_abstains_before_observation_is_inspected() -> None:
    item = definition(
        SyntheticJourneyId.DOCUMENT_UPLOAD_EXTRACTION,
        readiness=SyntheticJourneyReadiness.BLOCKED_UNAPPROVED,
    )

    result = evaluate_synthetic_journey_evidence(
        item,
        HostileInput(),
        evaluated_at=NOW + timedelta(minutes=1),
        environment=Environment.TEST,
    )

    assert result.observation is None
    assert result.disposition is SyntheticEvidenceDisposition.ABSTAINED
    assert result.reason is SyntheticEvidenceReason.JOURNEY_BLOCKED


@pytest.mark.parametrize(
    "environment", [Environment.STAGING, Environment.PILOT, Environment.PRODUCTION]
)
def test_evaluator_rejects_protected_environment_before_any_input_inspection(
    environment: Environment,
) -> None:
    with pytest.raises(JourneyEvidenceContractError) as captured:
        evaluate_synthetic_journey_evidence(
            HostileInput(),  # type: ignore[arg-type]
            HostileInput(),
            evaluated_at=NOW,
            environment=environment,
        )

    assert captured.value.code is JourneyEvidenceContractCode.PROTECTED_ENVIRONMENT


def test_evaluator_rejects_loose_environment_type() -> None:
    item = definition()

    with pytest.raises(JourneyEvidenceContractError) as captured:
        evaluate_synthetic_journey_evidence(
            item,
            observation(item),
            evaluated_at=NOW + timedelta(minutes=2),
            environment="test",  # type: ignore[arg-type]
        )

    assert captured.value.code is JourneyEvidenceContractCode.INVALID_TYPE


def test_evaluator_rejects_stale_evaluation_clock() -> None:
    item = definition()

    with pytest.raises(JourneyEvidenceContractError) as captured:
        evaluate_synthetic_journey_evidence(
            item,
            observation(item),
            evaluated_at=NOW,
            environment=Environment.TEST,
        )

    assert captured.value.code is JourneyEvidenceContractCode.INVALID_CHRONOLOGY


def test_evaluator_reconstructs_and_rejects_forced_definition_mutation() -> None:
    item = definition()
    observed = observation(item)
    object.__setattr__(item, "fixture_hash", HASH_C)

    with pytest.raises(JourneyEvidenceContractError) as captured:
        evaluate_synthetic_journey_evidence(
            item,
            observed,
            evaluated_at=NOW + timedelta(minutes=2),
            environment=Environment.TEST,
        )

    assert captured.value.code is JourneyEvidenceContractCode.SNAPSHOT_DRIFT
