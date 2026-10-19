"""Pure deterministic summary draft construction and source-drift checks."""

from __future__ import annotations

from collections import defaultdict
from typing import NoReturn

from app.modules.provenance.domain import VerificationState
from app.modules.summaries.contracts import (
    CurrentSourceAvailability,
    CurrentSourceSnapshot,
    SourceCoverage,
    SummaryProjectionInput,
    SyntheticSourceProjection,
)
from app.modules.summaries.domain import (
    CANONICAL_SECTION_ORDER,
    AssertionConflictState,
    ClinicalSummaryDraft,
    SectionReadiness,
    SourceDriftReason,
    SummaryAssertion,
    SummaryFreshness,
    SummaryFreshnessResult,
    SummarySection,
    SummarySectionId,
    SummarySourceKind,
    SummaryValidationCode,
    SummaryValidationError,
)


def _raise(code: SummaryValidationCode) -> NoReturn:
    raise SummaryValidationError(code)


def _source_sort_key(item: SyntheticSourceProjection) -> tuple[int, str, str]:
    return (
        CANONICAL_SECTION_ORDER.index(item.source.section_id),
        str(item.source.source_id.value),
        str(item.assertion_id.value),
    )


def _validate_input(value: object) -> SummaryProjectionInput:
    if not isinstance(value, SummaryProjectionInput):
        _raise(SummaryValidationCode.INVALID_TYPE)
    source_ids: set[object] = set()
    assertion_ids: set[object] = set()
    for item in value.sources:
        if item.source.encounter_id != value.encounter_id:
            _raise(SummaryValidationCode.INVALID_SCOPE)
        if item.source.source_id in source_ids or item.assertion_id in assertion_ids:
            _raise(SummaryValidationCode.DUPLICATE_IDENTITY)
        source_ids.add(item.source.source_id)
        assertion_ids.add(item.assertion_id)

    coverage_ids: set[SummarySectionId] = set()
    for coverage_item in value.coverage:
        if coverage_item.section_id in coverage_ids:
            _raise(SummaryValidationCode.DUPLICATE_IDENTITY)
        coverage_ids.add(coverage_item.section_id)

    groups: dict[str, list[SyntheticSourceProjection]] = defaultdict(list)
    for item in value.sources:
        if item.conflict_key is not None:
            groups[item.conflict_key].append(item)
    for items in groups.values():
        if (
            len(items) < 2
            or len({item.source.section_id for item in items}) != 1
            or len({item.label for item in items}) != len(items)
        ):
            _raise(SummaryValidationCode.INVALID_CONFLICT)
    return value


def _readiness(
    items: tuple[SyntheticSourceProjection, ...], coverage: SourceCoverage
) -> SectionReadiness:
    if items:
        if coverage is SourceCoverage.UNAVAILABLE:
            _raise(SummaryValidationCode.INVALID_SOURCE)
        all_confirmed_p5 = all(
            item.source.source_kind is SummarySourceKind.P5_CLINICAL_FACT
            and item.source.p5_verification_state is VerificationState.CLINICIAN_CONFIRMED
            for item in items
        )
        return SectionReadiness.RECORDED if all_confirmed_p5 else SectionReadiness.UNVERIFIED
    if coverage is SourceCoverage.COMPLETE:
        return SectionReadiness.NOT_RECORDED
    if coverage is SourceCoverage.UNAVAILABLE:
        return SectionReadiness.UNAVAILABLE
    return SectionReadiness.UNKNOWN


def build_engineering_draft(value: object) -> ClinicalSummaryDraft:
    """Copy exact synthetic labels into a fixed, source-backed draft."""

    try:
        return _build_engineering_draft(value)
    except SummaryValidationError:
        raise
    except Exception:
        raise SummaryValidationError(SummaryValidationCode.INVALID_VALUE) from None


def _build_engineering_draft(value: object) -> ClinicalSummaryDraft:
    source_input = _validate_input(value)
    coverage_by_section = {item.section_id: item.coverage for item in source_input.coverage}
    source_by_section: dict[SummarySectionId, list[SyntheticSourceProjection]] = defaultdict(list)
    for item in sorted(source_input.sources, key=_source_sort_key):
        source_by_section[item.source.section_id].append(item)

    sections: list[SummarySection] = []
    for section_id in CANONICAL_SECTION_ORDER:
        inputs = tuple(source_by_section[section_id])
        assertions = tuple(
            SummaryAssertion(
                assertion_id=item.assertion_id,
                label=item.label,
                source=item.source,
                conflict_state=(
                    AssertionConflictState.REVIEW_REQUIRED
                    if item.conflict_key is not None
                    else AssertionConflictState.NONE
                ),
                conflict_key=item.conflict_key,
            )
            for item in inputs
        )
        sections.append(
            SummarySection(
                section_id=section_id,
                readiness=_readiness(
                    inputs,
                    coverage_by_section.get(section_id, SourceCoverage.UNKNOWN),
                ),
                assertions=assertions,
                review_required=any(item.conflict_key is not None for item in inputs),
            )
        )
    references = tuple(assertion.source for section in sections for assertion in section.assertions)
    return ClinicalSummaryDraft(
        summary_id=source_input.summary_id,
        encounter_id=source_input.encounter_id,
        snapshot_token=source_input.snapshot_token,
        created_at=source_input.generated_at,
        sections=tuple(sections),
        source_references=references,
    )


def check_source_freshness(draft: object, current: object) -> SummaryFreshnessResult:
    """Compare supplied source metadata without mutating or refreshing the draft."""

    try:
        return _check_source_freshness(draft, current)
    except SummaryValidationError:
        raise
    except Exception:
        raise SummaryValidationError(SummaryValidationCode.INVALID_VALUE) from None


def _check_source_freshness(draft: object, current: object) -> SummaryFreshnessResult:
    if not isinstance(draft, ClinicalSummaryDraft) or not isinstance(
        current, CurrentSourceSnapshot
    ):
        _raise(SummaryValidationCode.INVALID_TYPE)
    if current.encounter_id != draft.encounter_id:
        _raise(SummaryValidationCode.INVALID_SCOPE)

    current_by_id = {}
    for item in current.sources:
        if item.encounter_id != current.encounter_id:
            _raise(SummaryValidationCode.INVALID_SCOPE)
        if item.source_id in current_by_id:
            _raise(SummaryValidationCode.DUPLICATE_IDENTITY)
        current_by_id[item.source_id] = item

    reasons: set[SourceDriftReason] = set()
    affected: set[SummarySectionId] = set()
    if current.snapshot_token != draft.snapshot_token:
        reasons.add(SourceDriftReason.SNAPSHOT_CHANGED)
        affected.update(CANONICAL_SECTION_ORDER)

    for reference in draft.source_references:
        state = current_by_id.get(reference.source_id)
        if state is None or state.availability in {
            CurrentSourceAvailability.UNAVAILABLE,
            CurrentSourceAvailability.REMOVED,
        }:
            reasons.add(SourceDriftReason.SOURCE_UNAVAILABLE)
            affected.add(reference.section_id)
            continue
        if (
            state.encounter_id != reference.encounter_id
            or state.section_id is not reference.section_id
            or state.source_kind is not reference.source_kind
        ):
            _raise(SummaryValidationCode.INVALID_SOURCE)
        if state.source_version != reference.source_version:
            reasons.add(SourceDriftReason.SOURCE_CHANGED)
            affected.add(reference.section_id)
        if reference.source_kind is SummarySourceKind.P5_CLINICAL_FACT:
            if state.p5_verification_state in {
                VerificationState.REJECTED,
                VerificationState.SUPERSEDED,
            }:
                reasons.add(SourceDriftReason.TERMINAL_SOURCE)
                affected.add(reference.section_id)
            elif state.p5_verification_state is not reference.p5_verification_state:
                reasons.add(SourceDriftReason.SOURCE_CHANGED)
                affected.add(reference.section_id)

    if current.conflict_sections:
        reasons.add(SourceDriftReason.NEW_CONFLICT)
        affected.update(current.conflict_sections)

    if SourceDriftReason.SOURCE_UNAVAILABLE in reasons:
        freshness = SummaryFreshness.SOURCE_UNAVAILABLE
    elif {
        SourceDriftReason.TERMINAL_SOURCE,
        SourceDriftReason.NEW_CONFLICT,
    } & reasons:
        freshness = SummaryFreshness.REVIEW_REQUIRED
    elif reasons:
        freshness = SummaryFreshness.STALE
    else:
        freshness = SummaryFreshness.CURRENT
    return SummaryFreshnessResult(
        freshness=freshness,
        affected_sections=tuple(
            section for section in CANONICAL_SECTION_ORDER if section in affected
        ),
        reasons=tuple(sorted(reasons, key=lambda item: item.value)),
    )
