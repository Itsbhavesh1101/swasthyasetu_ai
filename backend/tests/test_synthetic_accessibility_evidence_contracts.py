from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta, timezone

import pytest

from app.validation import (
    AccessibilityEvidenceAuthority,
    AccessibilityEvidenceClassification,
    AccessibilityEvidenceContractCode,
    AccessibilityEvidenceContractError,
    AccessibilityEvidenceDisposition,
    AccessibilityEvidenceReason,
    AccessibilityEvidenceReviewState,
    AccessibilityEvidenceVerification,
    SyntheticAccessibilityArea,
    SyntheticAccessibilityDefinition,
    SyntheticAccessibilityManifest,
    SyntheticAccessibilityObservation,
    SyntheticAccessibilityObservationState,
    SyntheticAccessibilityReceipt,
    snapshot_accessibility_definition,
    snapshot_accessibility_manifest,
    snapshot_accessibility_observation,
    snapshot_accessibility_receipt,
)

HASH_A = "a" * 64
HASH_B = "b" * 64
HASH_C = "c" * 64
BUILD_SHA = "d" * 40
NOW = datetime(2026, 11, 1, 16, 0, tzinfo=UTC)

EXPECTED_AREAS = {
    "CONTRAST_AND_DISPLAY",
    "KEYBOARD_AND_FOCUS",
    "KIOSK_AND_SHARED_DEVICE",
    "LANGUAGE",
    "PWA_AND_OFFLINE",
    "SEMANTICS_AND_ANNOUNCEMENTS",
    "STAFF_SHELLS",
    "URGENT_HELP",
}


def definition(
    area: SyntheticAccessibilityArea = SyntheticAccessibilityArea.KEYBOARD_AND_FOCUS,
    *,
    created_at: datetime = NOW,
) -> SyntheticAccessibilityDefinition:
    return SyntheticAccessibilityDefinition(
        area=area,
        definition_version="engineering.v1",
        build_sha=BUILD_SHA,
        config_hash=HASH_A,
        source_evidence_hash=HASH_B,
        checklist_hash=HASH_C,
        created_at=created_at,
    )


def observation(
    item: SyntheticAccessibilityDefinition,
    *,
    source_evidence_hash: str = HASH_B,
) -> SyntheticAccessibilityObservation:
    return SyntheticAccessibilityObservation(
        observation_id="syn_accessibility_observation_alpha",
        area=item.area,
        definition_fingerprint=item.fingerprint,
        build_sha=BUILD_SHA,
        config_hash=HASH_A,
        source_evidence_hash=source_evidence_hash,
        checklist_hash=HASH_C,
        state=SyntheticAccessibilityObservationState.METADATA_RECORDED,
        captured_at=NOW + timedelta(minutes=1),
    )


def definitions() -> tuple[SyntheticAccessibilityDefinition, ...]:
    return tuple(
        definition(area) for area in sorted(SyntheticAccessibilityArea, key=lambda item: item.value)
    )


def test_area_inventory_is_exact_and_closed() -> None:
    assert {item.value for item in SyntheticAccessibilityArea} == EXPECTED_AREAS


def test_definition_is_explicitly_unverified_and_human_review_required() -> None:
    item = definition()

    assert item.authority is AccessibilityEvidenceAuthority.ENGINEERING_ONLY
    assert item.classification is AccessibilityEvidenceClassification.ENGINEERING_SYNTHETIC
    assert item.verification is AccessibilityEvidenceVerification.UNVERIFIED
    assert item.review_state is AccessibilityEvidenceReviewState.HUMAN_REVIEW_REQUIRED
    assert len(item.fingerprint) == 64


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("area", "KEYBOARD_AND_FOCUS"),
        ("definition_version", "v1"),
        ("build_sha", "d" * 39),
        ("config_hash", "A" * 64),
        ("source_evidence_hash", "secret"),
        ("checklist_hash", "c" * 63),
        ("created_at", NOW.replace(tzinfo=None)),
        ("review_state", "HUMAN_REVIEW_REQUIRED"),
    ],
)
def test_definition_rejects_loose_or_malformed_values(field: str, value: object) -> None:
    values: dict[str, object] = {
        "area": SyntheticAccessibilityArea.KEYBOARD_AND_FOCUS,
        "definition_version": "engineering.v1",
        "build_sha": BUILD_SHA,
        "config_hash": HASH_A,
        "source_evidence_hash": HASH_B,
        "checklist_hash": HASH_C,
        "created_at": NOW,
    }
    values[field] = value

    with pytest.raises(AccessibilityEvidenceContractError):
        SyntheticAccessibilityDefinition(**values)  # type: ignore[arg-type]


def test_aware_non_utc_clock_normalizes_to_utc() -> None:
    non_utc = NOW.astimezone(timezone(timedelta(hours=5, minutes=30)))

    assert definition(created_at=non_utc).created_at == NOW
    assert definition(created_at=non_utc).created_at.tzinfo is UTC


def test_observation_binds_exact_definition_metadata() -> None:
    item = definition()
    observed = observation(item)

    assert observed.area is item.area
    assert observed.definition_fingerprint == item.fingerprint
    assert observed.state is SyntheticAccessibilityObservationState.METADATA_RECORDED
    assert len(observed.fingerprint) == 64


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("observation_id", "patient-123"),
        ("area", "KEYBOARD_AND_FOCUS"),
        ("definition_fingerprint", "x" * 64),
        ("build_sha", "d" * 39),
        ("config_hash", "a" * 63),
        ("source_evidence_hash", "B" * 64),
        ("checklist_hash", "not-a-hash"),
        ("state", "METADATA_RECORDED"),
        ("captured_at", NOW.replace(tzinfo=None)),
    ],
)
def test_observation_rejects_loose_or_malformed_values(field: str, value: object) -> None:
    item = definition()
    values: dict[str, object] = {
        "observation_id": "syn_accessibility_observation_alpha",
        "area": item.area,
        "definition_fingerprint": item.fingerprint,
        "build_sha": BUILD_SHA,
        "config_hash": HASH_A,
        "source_evidence_hash": HASH_B,
        "checklist_hash": HASH_C,
        "state": SyntheticAccessibilityObservationState.METADATA_RECORDED,
        "captured_at": NOW + timedelta(minutes=1),
    }
    values[field] = value

    with pytest.raises(AccessibilityEvidenceContractError):
        SyntheticAccessibilityObservation(**values)  # type: ignore[arg-type]


def test_exact_receipt_reconstructs_nested_inputs_and_is_immutable() -> None:
    item = definition()
    observed = observation(item)
    result = SyntheticAccessibilityReceipt(
        definition=item,
        observation=observed,
        disposition=AccessibilityEvidenceDisposition.EVIDENCE_CONSISTENT,
        reason=AccessibilityEvidenceReason.EXACT_SYNTHETIC_METADATA,
        evaluated_at=NOW + timedelta(minutes=2),
    )

    assert result.observation is not observed
    assert result.definition is not item
    with pytest.raises(FrozenInstanceError):
        result.reason = AccessibilityEvidenceReason.SCOPE_MISMATCH  # type: ignore[misc]


def test_receipt_direct_constructor_rejects_forged_disposition() -> None:
    item = definition()

    with pytest.raises(AccessibilityEvidenceContractError) as captured:
        SyntheticAccessibilityReceipt(
            definition=item,
            observation=observation(item, source_evidence_hash=HASH_A),
            disposition=AccessibilityEvidenceDisposition.EVIDENCE_CONSISTENT,
            reason=AccessibilityEvidenceReason.EXACT_SYNTHETIC_METADATA,
            evaluated_at=NOW + timedelta(minutes=2),
        )

    assert captured.value.code is AccessibilityEvidenceContractCode.INCONSISTENT_RECEIPT


def test_receipt_rejects_invalid_chronology() -> None:
    item = definition()

    with pytest.raises(AccessibilityEvidenceContractError) as captured:
        SyntheticAccessibilityReceipt(
            definition=item,
            observation=observation(item),
            disposition=AccessibilityEvidenceDisposition.EVIDENCE_CONSISTENT,
            reason=AccessibilityEvidenceReason.EXACT_SYNTHETIC_METADATA,
            evaluated_at=NOW,
        )

    assert captured.value.code is AccessibilityEvidenceContractCode.INVALID_CHRONOLOGY


def test_manifest_requires_exact_canonical_inventory_and_order() -> None:
    result = SyntheticAccessibilityManifest(
        manifest_id="syn_accessibility_manifest_alpha",
        generated_at=NOW + timedelta(minutes=1),
        definitions=definitions(),
    )

    assert len(result.definitions) == 8
    assert tuple(item.area.value for item in result.definitions) == tuple(sorted(EXPECTED_AREAS))


@pytest.mark.parametrize("items", [definitions()[:-1], definitions() + definitions()[:1]])
def test_manifest_rejects_wrong_cardinality(
    items: tuple[SyntheticAccessibilityDefinition, ...],
) -> None:
    with pytest.raises(AccessibilityEvidenceContractError) as captured:
        SyntheticAccessibilityManifest(
            manifest_id="syn_accessibility_manifest_alpha",
            generated_at=NOW + timedelta(minutes=1),
            definitions=items,
        )

    assert captured.value.code is AccessibilityEvidenceContractCode.INCOMPLETE_INVENTORY


def test_manifest_rejects_noncanonical_order() -> None:
    with pytest.raises(AccessibilityEvidenceContractError) as captured:
        SyntheticAccessibilityManifest(
            manifest_id="syn_accessibility_manifest_alpha",
            generated_at=NOW + timedelta(minutes=1),
            definitions=tuple(reversed(definitions())),
        )

    assert captured.value.code is AccessibilityEvidenceContractCode.INVALID_ORDER


def test_manifest_rejects_duplicate_area_with_exact_cardinality() -> None:
    items = definitions()

    with pytest.raises(AccessibilityEvidenceContractError) as captured:
        SyntheticAccessibilityManifest(
            manifest_id="syn_accessibility_manifest_alpha",
            generated_at=NOW + timedelta(minutes=1),
            definitions=items[:-1] + items[:1],
        )

    assert captured.value.code is AccessibilityEvidenceContractCode.DUPLICATE_AREA


def test_snapshot_helpers_reject_forced_mutation() -> None:
    item = definition()
    observed = observation(item)
    result = SyntheticAccessibilityReceipt(
        definition=item,
        observation=observed,
        disposition=AccessibilityEvidenceDisposition.EVIDENCE_CONSISTENT,
        reason=AccessibilityEvidenceReason.EXACT_SYNTHETIC_METADATA,
        evaluated_at=NOW + timedelta(minutes=2),
    )
    inventory = SyntheticAccessibilityManifest(
        manifest_id="syn_accessibility_manifest_alpha",
        generated_at=NOW + timedelta(minutes=1),
        definitions=definitions(),
    )
    object.__setattr__(item, "config_hash", HASH_C)
    object.__setattr__(observed, "checklist_hash", HASH_A)
    object.__setattr__(result, "evaluated_at", NOW)
    object.__setattr__(inventory, "generated_at", NOW)

    for value, snapshot in (
        (item, snapshot_accessibility_definition),
        (observed, snapshot_accessibility_observation),
        (result, snapshot_accessibility_receipt),
        (inventory, snapshot_accessibility_manifest),
    ):
        with pytest.raises(AccessibilityEvidenceContractError):
            snapshot(value)


def test_errors_and_representations_do_not_echo_sensitive_metadata() -> None:
    hostile = "secret-bearer-patient@example.test"

    with pytest.raises(AccessibilityEvidenceContractError) as captured:
        SyntheticAccessibilityObservation(
            observation_id=hostile,
            area=SyntheticAccessibilityArea.KEYBOARD_AND_FOCUS,
            definition_fingerprint=HASH_A,
            build_sha=BUILD_SHA,
            config_hash=HASH_A,
            source_evidence_hash=HASH_B,
            checklist_hash=HASH_C,
            state=SyntheticAccessibilityObservationState.METADATA_RECORDED,
            captured_at=NOW,
        )

    assert str(captured.value) == captured.value.code.value
    assert hostile not in str(captured.value)
    item = definition()
    observed = observation(item)
    assert HASH_A not in repr(item)
    assert HASH_B not in repr(observed)
