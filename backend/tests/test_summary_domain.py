"""P10-A immutable summary-domain contract tests using nonmedical fixtures only."""

from dataclasses import FrozenInstanceError, fields, replace
from datetime import UTC, datetime, timedelta, timezone
from typing import Any
from uuid import UUID

import pytest

from app.modules.provenance.domain import ProvenanceSourceType, VerificationState
from app.modules.summaries.domain import (
    CANONICAL_SECTION_ORDER,
    AssertionConflictState,
    ClinicalSummaryDraft,
    PatientReportedMarker,
    SectionReadiness,
    SummaryAssertion,
    SummaryClassification,
    SummarySection,
    SummarySectionId,
    SummarySourceKind,
    SummarySourceReference,
    SummaryStatus,
    SummaryValidationError,
)
from app.shared.types import OpaqueId


def oid(number: int) -> OpaqueId:
    return OpaqueId(UUID(int=number))


def p5_source(**changes: Any) -> SummarySourceReference:
    values: dict[str, Any] = {
        "source_id": oid(1),
        "encounter_id": oid(100),
        "section_id": SummarySectionId.CHIEF_COMPLAINT,
        "source_kind": SummarySourceKind.P5_CLINICAL_FACT,
        "source_version": "fact-v1",
        "p5_verification_state": VerificationState.CLINICIAN_CONFIRMED,
        "p5_source_type": ProvenanceSourceType.CLINICIAN,
    }
    values.update(changes)
    return SummarySourceReference(**values)


def p7_source(**changes: Any) -> SummarySourceReference:
    values: dict[str, Any] = {
        "source_id": oid(2),
        "encounter_id": oid(100),
        "section_id": SummarySectionId.HPI,
        "source_kind": SummarySourceKind.P7_PATIENT_REPORTED,
        "source_version": "answer-v1",
        "p7_marker": PatientReportedMarker.PATIENT_REPORTED,
    }
    values.update(changes)
    return SummarySourceReference(**values)


def assertion(**changes: Any) -> SummaryAssertion:
    values: dict[str, Any] = {
        "assertion_id": oid(10),
        "label": "SYNTHETIC_COMPLAINT_A",
        "source": p5_source(),
        "conflict_state": AssertionConflictState.NONE,
    }
    values.update(changes)
    return SummaryAssertion(**values)


def section(
    section_id: SummarySectionId, assertions: tuple[SummaryAssertion, ...] = ()
) -> SummarySection:
    return SummarySection(
        section_id=section_id,
        readiness=SectionReadiness.RECORDED if assertions else SectionReadiness.UNKNOWN,
        assertions=assertions,
        review_required=False,
    )


def draft(**changes: Any) -> ClinicalSummaryDraft:
    item = assertion()
    sections = tuple(
        section(section_id, (item,) if section_id is SummarySectionId.CHIEF_COMPLAINT else ())
        for section_id in CANONICAL_SECTION_ORDER
    )
    values: dict[str, Any] = {
        "summary_id": oid(200),
        "encounter_id": oid(100),
        "snapshot_token": "snapshot-v1",
        "created_at": datetime(2026, 1, 2, 3, 4, tzinfo=UTC),
        "sections": sections,
        "source_references": (item.source,),
    }
    values.update(changes)
    return ClinicalSummaryDraft(**values)


def test_section_vocabulary_and_order_exactly_map_standard_summary_structure() -> None:
    assert CANONICAL_SECTION_ORDER == (
        SummarySectionId.CHIEF_COMPLAINT,
        SummarySectionId.HPI,
        SummarySectionId.PAST_MEDICAL_HISTORY,
        SummarySectionId.PAST_SURGICAL_HISTORY,
        SummarySectionId.MEDICATIONS,
        SummarySectionId.ALLERGIES,
        SummarySectionId.FAMILY_HISTORY,
        SummarySectionId.PERSONAL_HISTORY,
        SummarySectionId.REVIEW_OF_SYSTEMS,
        SummarySectionId.PRIOR_INVESTIGATIONS,
    )
    with pytest.raises(ValueError):
        SummarySectionId("ARBITRARY_SECTION")


def test_canonical_future_status_names_exist_but_draft_is_only_creatable_status() -> None:
    assert tuple(status.value for status in SummaryStatus) == (
        "DRAFT",
        "CLINICIAN_EDITED",
        "CONFIRMED",
        "REJECTED",
        "SUPERSEDED",
    )
    assert draft().status is SummaryStatus.DRAFT
    for status in tuple(SummaryStatus)[1:]:
        with pytest.raises(SummaryValidationError, match="INVALID_VALUE"):
            draft(status=status)


def test_classification_is_fixed_engineering_only() -> None:
    assert tuple(SummaryClassification) == (SummaryClassification.ENGINEERING_ONLY,)
    with pytest.raises(ValueError):
        SummaryClassification("APPROVED")
    with pytest.raises(SummaryValidationError):
        draft(classification="CONFIRMED")


def test_p5_reference_preserves_exact_verification_and_provenance_type() -> None:
    source = p5_source(
        p5_verification_state=VerificationState.PATIENT_CONFIRMED,
        p5_source_type=ProvenanceSourceType.PATIENT_REPORT,
    )
    assert source.p5_verification_state is VerificationState.PATIENT_CONFIRMED
    assert source.p5_source_type is ProvenanceSourceType.PATIENT_REPORT
    assert source.p7_marker is None


def test_p7_reference_is_explicitly_patient_reported_and_not_a_p5_fact() -> None:
    source = p7_source()
    assert source.p7_marker is PatientReportedMarker.PATIENT_REPORTED
    assert source.p5_verification_state is None
    assert source.p5_source_type is None


@pytest.mark.parametrize(
    "changes",
    [
        {"source_kind": "P5_CLINICAL_FACT"},
        {"source_kind": "AI_EXTRACTED_UNCONFIRMED"},
        {"source_kind": "SYNTHETIC_OVERRIDE_A"},
        {"p5_verification_state": "CLINICIAN_CONFIRMED"},
        {"p5_source_type": "CLINICIAN"},
        {"p7_marker": PatientReportedMarker.PATIENT_REPORTED},
        {"p5_verification_state": VerificationState.REJECTED},
        {"p5_verification_state": VerificationState.SUPERSEDED},
    ],
)
def test_malformed_or_terminal_p5_sources_fail_closed(changes: dict[str, Any]) -> None:
    with pytest.raises(SummaryValidationError):
        p5_source(**changes)


@pytest.mark.parametrize(
    "changes",
    [
        {"p7_marker": None},
        {"p7_marker": "PATIENT_REPORTED"},
        {"p5_verification_state": VerificationState.EXTRACTED},
        {"p5_source_type": ProvenanceSourceType.PATIENT_REPORT},
    ],
)
def test_p7_source_cannot_forge_p5_trust(changes: dict[str, Any]) -> None:
    with pytest.raises(SummaryValidationError):
        p7_source(**changes)


@pytest.mark.parametrize(
    "label",
    [
        "private patient narrative",
        "SYNTHETIC_",
        "SYNTHETIC-medically-cleared",
        "SYNTHETIC_" + "A" * 300,
        1,
        True,
    ],
)
def test_assertion_accepts_only_bounded_nonmedical_machine_labels(label: object) -> None:
    with pytest.raises(SummaryValidationError) as caught:
        assertion(label=label)
    assert "private patient narrative" not in str(caught.value)


def test_sensitive_assertion_label_is_hidden_from_nested_repr() -> None:
    item = assertion(label="SYNTHETIC_PRIVATE_CANARY")
    rendered = repr(draft()) + repr(item) + repr(section(SummarySectionId.CHIEF_COMPLAINT, (item,)))
    assert "SYNTHETIC_PRIVATE_CANARY" not in rendered
    assert "source-v1" not in rendered
    assert str(oid(100)) not in rendered


def test_domain_graph_is_frozen_and_uses_detached_tuples() -> None:
    value = draft()
    with pytest.raises(FrozenInstanceError):
        value.status = SummaryStatus.CONFIRMED  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        value.sections[0].readiness = SectionReadiness.UNAVAILABLE  # type: ignore[misc]
    mutable = [assertion()]
    with pytest.raises(SummaryValidationError):
        SummarySection(
            section_id=SummarySectionId.CHIEF_COMPLAINT,
            readiness=SectionReadiness.RECORDED,
            assertions=mutable,  # type: ignore[arg-type]
            review_required=False,
        )


def test_aware_non_utc_created_at_is_normalized_and_naive_is_rejected() -> None:
    value = draft(
        created_at=datetime(
            2026,
            1,
            2,
            8,
            34,
            tzinfo=timezone(timedelta(hours=5, minutes=30)),
        )
    )
    assert value.created_at == datetime(2026, 1, 2, 3, 4, tzinfo=UTC)
    assert value.created_at.tzinfo is UTC
    with pytest.raises(SummaryValidationError):
        draft(created_at=datetime(2026, 1, 2))


def test_source_reference_list_must_exactly_match_assertion_order() -> None:
    with pytest.raises(SummaryValidationError, match="INVALID_SOURCE"):
        draft(source_references=())
    with pytest.raises(SummaryValidationError, match="INVALID_SOURCE"):
        draft(source_references=(p7_source(),))


def test_domain_shapes_contain_no_signature_authorization_or_clinical_decision_fields() -> None:
    names = {
        item.name
        for cls in (ClinicalSummaryDraft, SummaryAssertion, SummarySourceReference)
        for item in fields(cls)
    }
    assert {
        "diagnosis",
        "treatment",
        "recommendation",
        "risk_score",
        "triage_route",
        "signed_by",
        "approved_by",
        "authorized",
        "consent",
    }.isdisjoint(names)


def test_conflict_key_and_state_must_agree() -> None:
    with pytest.raises(SummaryValidationError, match="INVALID_CONFLICT"):
        assertion(conflict_key="conflict-a")
    with pytest.raises(SummaryValidationError, match="INVALID_CONFLICT"):
        assertion(conflict_state=AssertionConflictState.REVIEW_REQUIRED)


@pytest.mark.parametrize(
    ("item", "readiness"),
    [
        (
            assertion(
                source=p7_source(section_id=SummarySectionId.CHIEF_COMPLAINT),
            ),
            SectionReadiness.RECORDED,
        ),
        (
            assertion(
                source=p5_source(p5_verification_state=VerificationState.EXTRACTED),
            ),
            SectionReadiness.RECORDED,
        ),
        (assertion(), SectionReadiness.NOT_RECORDED),
        (assertion(), SectionReadiness.UNAVAILABLE),
        (assertion(), SectionReadiness.UNKNOWN),
    ],
)
def test_direct_section_rejects_forged_populated_readiness(
    item: SummaryAssertion, readiness: SectionReadiness
) -> None:
    with pytest.raises(SummaryValidationError, match="INVALID_VALUE"):
        SummarySection(
            section_id=SummarySectionId.CHIEF_COMPLAINT,
            readiness=readiness,
            assertions=(item,),
            review_required=False,
        )


@pytest.mark.parametrize("readiness", [SectionReadiness.RECORDED, SectionReadiness.UNVERIFIED])
def test_direct_section_rejects_forged_empty_readiness(readiness: SectionReadiness) -> None:
    with pytest.raises(SummaryValidationError, match="INVALID_VALUE"):
        SummarySection(
            section_id=SummarySectionId.CHIEF_COMPLAINT,
            readiness=readiness,
            assertions=(),
            review_required=False,
        )


def test_direct_section_accepts_only_semantically_matching_readiness() -> None:
    p7_item = assertion(source=p7_source(section_id=SummarySectionId.CHIEF_COMPLAINT))
    extracted = assertion(
        assertion_id=oid(11),
        source=p5_source(
            source_id=oid(3),
            p5_verification_state=VerificationState.EXTRACTED,
        ),
    )
    assert section(SummarySectionId.CHIEF_COMPLAINT, (assertion(),)).readiness is (
        SectionReadiness.RECORDED
    )
    assert (
        SummarySection(
            section_id=SummarySectionId.CHIEF_COMPLAINT,
            readiness=SectionReadiness.UNVERIFIED,
            assertions=(p7_item, extracted),
            review_required=False,
        ).readiness
        is SectionReadiness.UNVERIFIED
    )
    for readiness in (
        SectionReadiness.UNKNOWN,
        SectionReadiness.NOT_RECORDED,
        SectionReadiness.UNAVAILABLE,
    ):
        assert (
            SummarySection(
                section_id=SummarySectionId.ALLERGIES,
                readiness=readiness,
                assertions=(),
                review_required=False,
            ).readiness
            is readiness
        )


@pytest.mark.parametrize("duplicate_kind", ["assertion", "source"])
@pytest.mark.parametrize("cross_section", [False, True])
def test_direct_draft_rejects_global_duplicate_identities(
    duplicate_kind: str, cross_section: bool
) -> None:
    first = assertion()
    second_section_id = SummarySectionId.HPI if cross_section else SummarySectionId.CHIEF_COMPLAINT
    second_source = p5_source(
        source_id=first.source.source_id if duplicate_kind == "source" else oid(2),
        section_id=second_section_id,
    )
    second = assertion(
        assertion_id=first.assertion_id if duplicate_kind == "assertion" else oid(11),
        source=second_source,
    )
    sections = tuple(
        SummarySection(
            section_id=section_id,
            readiness=(
                SectionReadiness.RECORDED
                if section_id is SummarySectionId.CHIEF_COMPLAINT
                or (cross_section and section_id is SummarySectionId.HPI)
                else SectionReadiness.UNKNOWN
            ),
            assertions=(
                (first,)
                if section_id is SummarySectionId.CHIEF_COMPLAINT
                else (second,)
                if cross_section and section_id is SummarySectionId.HPI
                else ()
            ),
            review_required=False,
        )
        for section_id in CANONICAL_SECTION_ORDER
    )
    if not cross_section:
        sections = (
            SummarySection(
                section_id=SummarySectionId.CHIEF_COMPLAINT,
                readiness=SectionReadiness.RECORDED,
                assertions=(first, second),
                review_required=False,
            ),
            *sections[1:],
        )
    references = tuple(item.source for value in sections for item in value.assertions)
    with pytest.raises(SummaryValidationError, match="DUPLICATE_IDENTITY"):
        draft(sections=sections, source_references=references)


def test_replace_cannot_promote_draft_or_change_source_scope() -> None:
    value = draft()
    with pytest.raises(SummaryValidationError):
        replace(value, status=SummaryStatus.CONFIRMED)
    with pytest.raises(SummaryValidationError):
        replace(value, encounter_id=oid(999))
