"""Deterministic, source-backed P10 engineering demonstration."""

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from app.modules.summaries.contracts import (
    CurrentSourceAvailability,
    CurrentSourceSnapshot,
    CurrentSourceState,
    SummaryProjectionInput,
    SyntheticSourceProjection,
)
from app.modules.summaries.domain import (
    PatientReportedMarker,
    SummarySectionId,
    SummarySourceKind,
    SummarySourceReference,
)
from app.modules.summaries.projection import build_engineering_draft, check_source_freshness
from app.shared.types import OpaqueId


def _id(value: int) -> OpaqueId:
    return OpaqueId(UUID(int=value))


@dataclass(frozen=True, slots=True)
class EngineeringSummarySectionResult:
    section: str
    readiness: str
    assertions: tuple[str, ...]
    source_kinds: tuple[str, ...]
    conflict_review_required: bool


@dataclass(frozen=True, slots=True)
class EngineeringSummaryResult:
    status: str
    classification: str
    review_state: str
    freshness: str
    affected_sections: tuple[str, ...]
    drift_reasons: tuple[str, ...]
    source_count: int
    sections: tuple[EngineeringSummarySectionResult, ...]
    source_access: str
    can_edit: bool
    can_confirm: bool
    can_reject: bool
    external_egress: bool
    notice: str


class EngineeringSummaryDemoService:
    """Compose the reviewed P10-A contracts without data access or clinical authority."""

    def project(self, *, clock: datetime | None = None) -> EngineeringSummaryResult:
        now = clock or datetime.now(UTC)
        encounter_id = _id(100)
        source = SummarySourceReference(
            source_id=_id(101),
            encounter_id=encounter_id,
            section_id=SummarySectionId.CHIEF_COMPLAINT,
            source_kind=SummarySourceKind.P7_PATIENT_REPORTED,
            source_version="source.v1",
            p7_marker=PatientReportedMarker.PATIENT_REPORTED,
        )
        draft = build_engineering_draft(
            SummaryProjectionInput(
                summary_id=_id(102),
                encounter_id=encounter_id,
                snapshot_token="snapshot.v1",
                generated_at=now,
                sources=(
                    SyntheticSourceProjection(
                        assertion_id=_id(103),
                        label="SYNTHETIC_REPORTED_COMPLAINT",
                        source=source,
                    ),
                ),
            )
        )
        freshness = check_source_freshness(
            draft,
            CurrentSourceSnapshot(
                encounter_id=encounter_id,
                snapshot_token="snapshot.v1",
                sources=(
                    CurrentSourceState(
                        source_id=source.source_id,
                        encounter_id=encounter_id,
                        section_id=source.section_id,
                        source_kind=source.source_kind,
                        source_version=source.source_version,
                        availability=CurrentSourceAvailability.AVAILABLE,
                    ),
                    CurrentSourceState(
                        source_id=_id(104),
                        encounter_id=encounter_id,
                        section_id=SummarySectionId.HPI,
                        source_kind=SummarySourceKind.P7_PATIENT_REPORTED,
                        source_version="source.v1",
                        availability=CurrentSourceAvailability.AVAILABLE,
                    ),
                ),
            ),
        )
        sections = tuple(
            EngineeringSummarySectionResult(
                section=section.section_id.value,
                readiness=section.readiness.value,
                assertions=tuple(assertion.label for assertion in section.assertions),
                source_kinds=tuple(
                    assertion.source.source_kind.value for assertion in section.assertions
                ),
                conflict_review_required=section.review_required,
            )
            for section in draft.sections
        )
        return EngineeringSummaryResult(
            status=draft.status.value,
            classification=draft.classification.value,
            review_state="REVIEW_REQUIRED",
            freshness=freshness.freshness.value,
            affected_sections=tuple(section.value for section in freshness.affected_sections),
            drift_reasons=tuple(reason.value for reason in freshness.reasons),
            source_count=len(draft.source_references),
            sections=sections,
            source_access="NOT_AUTHORIZED",
            can_edit=False,
            can_confirm=False,
            can_reject=False,
            external_egress=False,
            notice=(
                "Synthetic engineering draft only. Missing sections are unknown, source drift "
                "requires review, and no clinical action is authorized."
            ),
        )
