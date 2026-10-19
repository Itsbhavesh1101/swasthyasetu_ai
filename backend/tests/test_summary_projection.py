"""Deterministic source-backed projection and drift tests."""

from dataclasses import replace
from datetime import UTC, datetime
from traceback import format_exception
from typing import Any
from uuid import UUID

import pytest

from app.modules.provenance.domain import ProvenanceSourceType, VerificationState
from app.modules.summaries.contracts import (
    CurrentSourceAvailability,
    CurrentSourceSnapshot,
    CurrentSourceState,
    SectionCoverage,
    SourceCoverage,
    SummaryProjectionInput,
    SyntheticSourceProjection,
)
from app.modules.summaries.domain import (
    CANONICAL_SECTION_ORDER,
    AssertionConflictState,
    PatientReportedMarker,
    SectionReadiness,
    SourceDriftReason,
    SummaryFreshness,
    SummarySectionId,
    SummarySourceKind,
    SummarySourceReference,
    SummaryValidationError,
)
from app.modules.summaries.projection import (
    build_engineering_draft,
    check_source_freshness,
)
from app.shared.types import OpaqueId


def oid(number: int) -> OpaqueId:
    return OpaqueId(UUID(int=number))


def source_projection(
    number: int = 1,
    *,
    section_id: SummarySectionId = SummarySectionId.CHIEF_COMPLAINT,
    label: str = "SYNTHETIC_COMPLAINT_A",
    source_kind: SummarySourceKind = SummarySourceKind.P5_CLINICAL_FACT,
    verification: VerificationState = VerificationState.CLINICIAN_CONFIRMED,
    conflict_key: str | None = None,
    encounter_id: OpaqueId | None = None,
) -> SyntheticSourceProjection:
    if source_kind is SummarySourceKind.P5_CLINICAL_FACT:
        reference = SummarySourceReference(
            source_id=oid(number),
            encounter_id=encounter_id or oid(100),
            section_id=section_id,
            source_kind=source_kind,
            source_version=f"source-v{number}",
            p5_verification_state=verification,
            p5_source_type=ProvenanceSourceType.CLINICIAN,
        )
    else:
        reference = SummarySourceReference(
            source_id=oid(number),
            encounter_id=encounter_id or oid(100),
            section_id=section_id,
            source_kind=source_kind,
            source_version=f"source-v{number}",
            p7_marker=PatientReportedMarker.PATIENT_REPORTED,
        )
    return SyntheticSourceProjection(
        assertion_id=oid(1000 + number),
        label=label,
        source=reference,
        conflict_key=conflict_key,
    )


def projection_input(**changes: Any) -> SummaryProjectionInput:
    values: dict[str, Any] = {
        "summary_id": oid(200),
        "encounter_id": oid(100),
        "snapshot_token": "snapshot-v1",
        "generated_at": datetime(2026, 1, 2, 3, 4, tzinfo=UTC),
        "sources": (source_projection(),),
    }
    values.update(changes)
    return SummaryProjectionInput(**values)


def current_state(item: SyntheticSourceProjection, **changes: Any) -> CurrentSourceState:
    values: dict[str, Any] = {
        "source_id": item.source.source_id,
        "encounter_id": item.source.encounter_id,
        "section_id": item.source.section_id,
        "source_kind": item.source.source_kind,
        "source_version": item.source.source_version,
        "availability": CurrentSourceAvailability.AVAILABLE,
        "p5_verification_state": item.source.p5_verification_state,
    }
    values.update(changes)
    return CurrentSourceState(**values)


def current_snapshot(value: SummaryProjectionInput, **changes: Any) -> CurrentSourceSnapshot:
    values: dict[str, Any] = {
        "encounter_id": value.encounter_id,
        "snapshot_token": value.snapshot_token,
        "sources": tuple(current_state(item) for item in value.sources),
    }
    values.update(changes)
    return CurrentSourceSnapshot(**values)


def test_builder_emits_every_section_in_fixed_order_and_copies_exact_labels() -> None:
    sources = tuple(
        source_projection(
            index + 1,
            section_id=section_id,
            label=f"SYNTHETIC_{section_id.value}_A",
            source_kind=(
                SummarySourceKind.P7_PATIENT_REPORTED
                if index % 2
                else SummarySourceKind.P5_CLINICAL_FACT
            ),
        )
        for index, section_id in enumerate(CANONICAL_SECTION_ORDER)
    )
    draft = build_engineering_draft(projection_input(sources=sources))
    assert tuple(section.section_id for section in draft.sections) == CANONICAL_SECTION_ORDER
    assert tuple(section.assertions[0].label for section in draft.sections) == tuple(
        f"SYNTHETIC_{section.value}_A" for section in CANONICAL_SECTION_ORDER
    )
    assert len(draft.source_references) == len(CANONICAL_SECTION_ORDER)


def test_reversed_input_and_repeated_calls_are_exactly_deterministic() -> None:
    sources = (
        source_projection(3, label="SYNTHETIC_COMPLAINT_C"),
        source_projection(1, label="SYNTHETIC_COMPLAINT_A"),
        source_projection(2, label="SYNTHETIC_COMPLAINT_B"),
    )
    forward = build_engineering_draft(projection_input(sources=sources))
    reverse = build_engineering_draft(projection_input(sources=tuple(reversed(sources))))
    repeated = build_engineering_draft(projection_input(sources=sources))
    assert forward == reverse == repeated


def test_p5_and_p7_source_trust_is_preserved_without_promotion() -> None:
    p5 = source_projection(
        1,
        verification=VerificationState.EXTRACTED,
        label="SYNTHETIC_FACT_EXTRACTED",
    )
    p7 = source_projection(
        2,
        section_id=SummarySectionId.HPI,
        label="SYNTHETIC_PATIENT_REPORTED",
        source_kind=SummarySourceKind.P7_PATIENT_REPORTED,
    )
    draft = build_engineering_draft(projection_input(sources=(p7, p5)))
    assert draft.sections[0].readiness is SectionReadiness.UNVERIFIED
    assert (
        draft.sections[0].assertions[0].source.p5_verification_state is VerificationState.EXTRACTED
    )
    assert draft.sections[1].readiness is SectionReadiness.UNVERIFIED
    assert (
        draft.sections[1].assertions[0].source.p7_marker is PatientReportedMarker.PATIENT_REPORTED
    )


def test_only_all_clinician_confirmed_p5_entries_are_recorded() -> None:
    confirmed = source_projection()
    draft = build_engineering_draft(projection_input(sources=(confirmed,)))
    assert draft.sections[0].readiness is SectionReadiness.RECORDED


@pytest.mark.parametrize(
    ("section_id", "coverage", "expected"),
    [
        (SummarySectionId.MEDICATIONS, SourceCoverage.UNKNOWN, SectionReadiness.UNKNOWN),
        (SummarySectionId.MEDICATIONS, SourceCoverage.PARTIAL, SectionReadiness.UNKNOWN),
        (
            SummarySectionId.MEDICATIONS,
            SourceCoverage.COMPLETE,
            SectionReadiness.NOT_RECORDED,
        ),
        (
            SummarySectionId.MEDICATIONS,
            SourceCoverage.UNAVAILABLE,
            SectionReadiness.UNAVAILABLE,
        ),
        (SummarySectionId.ALLERGIES, SourceCoverage.UNKNOWN, SectionReadiness.UNKNOWN),
        (
            SummarySectionId.ALLERGIES,
            SourceCoverage.COMPLETE,
            SectionReadiness.NOT_RECORDED,
        ),
        (
            SummarySectionId.ALLERGIES,
            SourceCoverage.UNAVAILABLE,
            SectionReadiness.UNAVAILABLE,
        ),
    ],
)
def test_empty_medication_allergy_and_missing_sections_use_safe_states(
    section_id: SummarySectionId,
    coverage: SourceCoverage,
    expected: SectionReadiness,
) -> None:
    value = projection_input(
        sources=(), coverage=(SectionCoverage(section_id=section_id, coverage=coverage),)
    )
    draft = build_engineering_draft(value)
    target = next(section for section in draft.sections if section.section_id is section_id)
    assert target.readiness is expected
    assert target.assertions == ()
    rendered = repr(draft).lower()
    for forbidden in ("no known allergies", "no medications", "none", "negative", "cleared"):
        assert forbidden not in rendered


def test_unavailable_coverage_cannot_hide_included_source() -> None:
    with pytest.raises(SummaryValidationError, match="INVALID_SOURCE"):
        build_engineering_draft(
            projection_input(
                coverage=(
                    SectionCoverage(
                        section_id=SummarySectionId.CHIEF_COMPLAINT,
                        coverage=SourceCoverage.UNAVAILABLE,
                    ),
                )
            )
        )


def test_conflicting_claims_remain_distinct_and_review_required() -> None:
    sources = (
        source_projection(1, label="SYNTHETIC_HISTORY_A", conflict_key="synthetic-conflict-a"),
        source_projection(2, label="SYNTHETIC_HISTORY_B", conflict_key="synthetic-conflict-a"),
    )
    section = build_engineering_draft(projection_input(sources=sources)).sections[0]
    assert tuple(item.label for item in section.assertions) == (
        "SYNTHETIC_HISTORY_A",
        "SYNTHETIC_HISTORY_B",
    )
    assert section.review_required
    assert all(
        item.conflict_state is AssertionConflictState.REVIEW_REQUIRED for item in section.assertions
    )


@pytest.mark.parametrize(
    "sources",
    [
        (source_projection(1, conflict_key="single-conflict"),),
        (
            source_projection(1, conflict_key="cross-section"),
            source_projection(
                2,
                section_id=SummarySectionId.HPI,
                label="SYNTHETIC_HPI_A",
                conflict_key="cross-section",
            ),
        ),
        (
            source_projection(1, conflict_key="same-label"),
            source_projection(2, conflict_key="same-label"),
        ),
    ],
)
def test_malformed_conflicts_fail_closed(sources: tuple[SyntheticSourceProjection, ...]) -> None:
    with pytest.raises(SummaryValidationError, match="INVALID_CONFLICT"):
        build_engineering_draft(projection_input(sources=sources))


def test_duplicate_source_assertion_and_coverage_identities_fail_closed() -> None:
    first = source_projection(1)
    with pytest.raises(SummaryValidationError, match="DUPLICATE_IDENTITY"):
        build_engineering_draft(
            projection_input(sources=(first, replace(first, assertion_id=oid(999))))
        )
    with pytest.raises(SummaryValidationError, match="DUPLICATE_IDENTITY"):
        build_engineering_draft(
            projection_input(
                sources=(first, replace(first, source=replace(first.source, source_id=oid(2))))
            )
        )
    coverage = SectionCoverage(
        section_id=SummarySectionId.ALLERGIES, coverage=SourceCoverage.COMPLETE
    )
    with pytest.raises(SummaryValidationError, match="DUPLICATE_IDENTITY"):
        build_engineering_draft(projection_input(coverage=(coverage, coverage)))


def test_mixed_encounter_scope_is_rejected_without_identifier_echo() -> None:
    with pytest.raises(SummaryValidationError, match="INVALID_SCOPE") as caught:
        build_engineering_draft(
            projection_input(sources=(source_projection(encounter_id=oid(999)),))
        )
    assert str(oid(999)) not in str(caught.value)


def test_wrong_input_type_fails_closed() -> None:
    with pytest.raises(SummaryValidationError, match="INVALID_TYPE"):
        build_engineering_draft({"approved": True, "diagnosis": "private"})


def test_total_and_per_section_source_limits_are_enforced() -> None:
    too_many = tuple(
        source_projection(index + 1, label=f"SYNTHETIC_ITEM_{index:02}") for index in range(65)
    )
    with pytest.raises(SummaryValidationError, match="LIMIT_EXCEEDED"):
        projection_input(sources=too_many)
    too_many_one_section = tuple(
        source_projection(index + 1, label=f"SYNTHETIC_ITEM_{index:02}") for index in range(17)
    )
    with pytest.raises(SummaryValidationError, match="LIMIT_EXCEEDED"):
        build_engineering_draft(projection_input(sources=too_many_one_section))


def test_unchanged_snapshot_is_current() -> None:
    value = projection_input()
    draft = build_engineering_draft(value)
    result = check_source_freshness(draft, current_snapshot(value))
    assert result.freshness is SummaryFreshness.CURRENT
    assert result.affected_sections == ()
    assert result.reasons == ()


@pytest.mark.parametrize(
    ("changes", "expected", "reason"),
    [
        (
            {"source_version": "source-v2"},
            SummaryFreshness.STALE,
            SourceDriftReason.SOURCE_CHANGED,
        ),
        (
            {"availability": CurrentSourceAvailability.REMOVED},
            SummaryFreshness.SOURCE_UNAVAILABLE,
            SourceDriftReason.SOURCE_UNAVAILABLE,
        ),
        (
            {"availability": CurrentSourceAvailability.UNAVAILABLE},
            SummaryFreshness.SOURCE_UNAVAILABLE,
            SourceDriftReason.SOURCE_UNAVAILABLE,
        ),
        (
            {"p5_verification_state": VerificationState.SUPERSEDED},
            SummaryFreshness.REVIEW_REQUIRED,
            SourceDriftReason.TERMINAL_SOURCE,
        ),
        (
            {"p5_verification_state": VerificationState.REJECTED},
            SummaryFreshness.REVIEW_REQUIRED,
            SourceDriftReason.TERMINAL_SOURCE,
        ),
        (
            {"p5_verification_state": VerificationState.PATIENT_CONFIRMED},
            SummaryFreshness.STALE,
            SourceDriftReason.SOURCE_CHANGED,
        ),
    ],
)
def test_changed_removed_unavailable_or_terminal_source_never_remains_fresh(
    changes: dict[str, Any], expected: SummaryFreshness, reason: SourceDriftReason
) -> None:
    value = projection_input()
    draft = build_engineering_draft(value)
    state = current_state(value.sources[0], **changes)
    result = check_source_freshness(draft, current_snapshot(value, sources=(state,)))
    assert result.freshness is expected
    assert result.affected_sections == (SummarySectionId.CHIEF_COMPLAINT,)
    assert reason in result.reasons


def test_missing_source_is_unavailable_and_snapshot_change_is_stale() -> None:
    value = projection_input()
    draft = build_engineering_draft(value)
    unavailable = check_source_freshness(draft, current_snapshot(value, sources=()))
    assert unavailable.freshness is SummaryFreshness.SOURCE_UNAVAILABLE
    assert unavailable.reasons == (SourceDriftReason.SOURCE_UNAVAILABLE,)
    stale = check_source_freshness(draft, current_snapshot(value, snapshot_token="snapshot-v2"))
    assert stale.freshness is SummaryFreshness.STALE
    assert stale.affected_sections == CANONICAL_SECTION_ORDER


def test_new_conflict_requires_review_without_mutating_draft() -> None:
    value = projection_input()
    draft = build_engineering_draft(value)
    before = repr(draft)
    result = check_source_freshness(
        draft,
        current_snapshot(value, conflict_sections=(SummarySectionId.CHIEF_COMPLAINT,)),
    )
    assert result.freshness is SummaryFreshness.REVIEW_REQUIRED
    assert result.reasons == (SourceDriftReason.NEW_CONFLICT,)
    assert repr(draft) == before


def test_new_same_encounter_source_marks_its_section_stale() -> None:
    value = projection_input()
    draft = build_engineering_draft(value)
    new_item = source_projection(
        2,
        section_id=SummarySectionId.HPI,
        label="SYNTHETIC_HPI_A",
    )
    result = check_source_freshness(
        draft,
        current_snapshot(
            value,
            sources=(current_state(value.sources[0]), current_state(new_item)),
        ),
    )
    assert result.freshness is SummaryFreshness.STALE
    assert result.affected_sections == (SummarySectionId.HPI,)
    assert tuple(reason.value for reason in result.reasons) == ("NEW_SOURCE",)


def test_new_source_in_formerly_empty_section_is_detected_independent_of_order() -> None:
    value = projection_input()
    draft = build_engineering_draft(value)
    new_item = source_projection(
        2,
        section_id=SummarySectionId.ALLERGIES,
        label="SYNTHETIC_ALLERGY_A",
        source_kind=SummarySourceKind.P7_PATIENT_REPORTED,
    )
    states = (current_state(value.sources[0]), current_state(new_item))
    forward = check_source_freshness(draft, current_snapshot(value, sources=states))
    reverse = check_source_freshness(
        draft, current_snapshot(value, sources=tuple(reversed(states)))
    )
    assert forward == reverse
    assert forward.freshness is SummaryFreshness.STALE
    assert forward.affected_sections == (SummarySectionId.ALLERGIES,)


def test_new_source_with_explicit_conflict_requires_review() -> None:
    value = projection_input()
    draft = build_engineering_draft(value)
    new_item = source_projection(2, label="SYNTHETIC_COMPLAINT_B")
    result = check_source_freshness(
        draft,
        current_snapshot(
            value,
            sources=(current_state(value.sources[0]), current_state(new_item)),
            conflict_sections=(SummarySectionId.CHIEF_COMPLAINT,),
        ),
    )
    assert result.freshness is SummaryFreshness.REVIEW_REQUIRED
    assert result.affected_sections == (SummarySectionId.CHIEF_COMPLAINT,)
    assert {reason.value for reason in result.reasons} == {"NEW_CONFLICT", "NEW_SOURCE"}


def test_cross_encounter_new_source_fails_closed_without_identifier_echo() -> None:
    value = projection_input()
    draft = build_engineering_draft(value)
    new_item = source_projection(2, encounter_id=oid(999))
    with pytest.raises(SummaryValidationError, match="INVALID_SCOPE") as caught:
        check_source_freshness(
            draft,
            current_snapshot(
                value,
                sources=(current_state(value.sources[0]), current_state(new_item)),
            ),
        )
    assert str(oid(999)) not in str(caught.value)


def test_current_snapshot_rejects_scope_identity_and_duplicate_source_mismatch() -> None:
    value = projection_input()
    draft = build_engineering_draft(value)
    with pytest.raises(SummaryValidationError, match="INVALID_SCOPE"):
        check_source_freshness(draft, current_snapshot(value, encounter_id=oid(999)))
    state = current_state(value.sources[0])
    with pytest.raises(SummaryValidationError, match="DUPLICATE_IDENTITY"):
        check_source_freshness(draft, current_snapshot(value, sources=(state, state)))
    with pytest.raises(SummaryValidationError, match="INVALID_SOURCE"):
        check_source_freshness(
            draft,
            current_snapshot(
                value,
                sources=(replace(state, section_id=SummarySectionId.HPI),),
            ),
        )


def test_privacy_canary_is_absent_from_validation_traceback() -> None:
    canary = "private-patient-narrative-canary"
    with pytest.raises(SummaryValidationError) as caught:
        SyntheticSourceProjection(
            assertion_id=oid(2), label=canary, source=source_projection().source
        )
    rendered = "".join(
        format_exception(type(caught.value), caught.value, caught.value.__traceback__)
    )
    assert canary not in str(caught.value)
    assert canary not in rendered
