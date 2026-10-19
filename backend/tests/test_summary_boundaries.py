"""P10-A runtime-isolation, privacy, and governance regression tests."""

from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from traceback import format_exception
from uuid import UUID

import pytest

from app.main import create_app
from app.modules.provenance.domain import ProvenanceSourceType, VerificationState
from app.modules.summaries.contracts import SummaryProjectionInput, SyntheticSourceProjection
from app.modules.summaries.domain import (
    SummarySectionId,
    SummarySourceKind,
    SummarySourceReference,
    SummaryValidationError,
)
from app.modules.summaries.projection import build_engineering_draft
from app.shared.types import OpaqueId


def oid(number: int) -> OpaqueId:
    return OpaqueId(UUID(int=number))


def projection_input() -> SummaryProjectionInput:
    source = SummarySourceReference(
        source_id=oid(1),
        encounter_id=oid(100),
        section_id=SummarySectionId.CHIEF_COMPLAINT,
        source_kind=SummarySourceKind.P5_CLINICAL_FACT,
        source_version="source-v1",
        p5_verification_state=VerificationState.CLINICIAN_CONFIRMED,
        p5_source_type=ProvenanceSourceType.CLINICIAN,
    )
    return SummaryProjectionInput(
        summary_id=oid(200),
        encounter_id=oid(100),
        snapshot_token="snapshot-v1",
        generated_at=datetime(2026, 1, 2, 3, 4, tzinfo=UTC),
        sources=(
            SyntheticSourceProjection(
                assertion_id=oid(1001),
                label="SYNTHETIC_COMPLAINT_A",
                source=source,
            ),
        ),
    )


def test_summary_package_has_no_runtime_or_external_dependency_imports() -> None:
    module_root = Path(__file__).parents[1] / "app" / "modules" / "summaries"
    source = "\n".join(
        path.read_text(encoding="utf-8") for path in sorted(module_root.glob("*.py"))
    ).lower()
    for forbidden in (
        "fastapi",
        "sqlalchemy",
        "alembic",
        "httpx",
        "requests",
        "urllib",
        "socket",
        "open(",
        "ai_orchestration",
        "modules.safety",
        "modules.clinical_intake",
        "modules.patients",
        "infrastructure",
        "repository",
    ):
        assert forbidden not in source


def test_importing_summary_package_does_not_register_module_or_routes() -> None:
    app = create_app()
    paths = {path for route in app.routes if (path := getattr(route, "path", None))}
    assert not any(path.startswith("/api/v1/summaries") for path in paths)
    assert not any(path.startswith("/api/v1/clinician") for path in paths)
    assert "summaries" not in app.state.module_registry.module_ids


def test_no_summary_table_migration_or_clinician_runtime_wiring_exists() -> None:
    root = Path(__file__).parents[2]
    migrations = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((root / "backend" / "migrations" / "versions").glob("*.py"))
    ).lower()
    assert "clinical_summaries" not in migrations
    clinician_files = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((root / "apps" / "clinician-web").rglob("*.tsx"))
    ).lower()
    assert "clinicalsummarydraft" not in clinician_files
    assert "api/v1/clinician" not in clinician_files


@pytest.mark.parametrize(
    "forged",
    (
        "APPROVED",
        "CONFIRMED",
        "CLINICIAN_CONFIRMED",
        "SIGNED",
        "MEDICALLY_CLEARED",
        "SELF_CARE_ALLOWED",
        "AI_EXTRACTED_UNCONFIRMED",
        "SYNTHETIC_COMPLETE_A",
        "SYNTHETIC_OVERRIDE_A",
        "SYNTHETIC_OVERRIDE_B",
        "SYNTHETIC_MISSING_A",
        "SYNTHETIC_AMBIGUOUS_A",
        "SYNTHETIC_EXCLUDE_A",
        "SYNTHETIC_PRIORITY_A",
        "SYNTHETIC_ROUTINE_A",
        "SYNTHETIC_SELF_CARE_A",
    ),
)
def test_authority_and_blocked_p8_p9_tokens_cannot_become_summary_labels(
    forged: str,
) -> None:
    value = projection_input()
    with pytest.raises(SummaryValidationError):
        source = replace(value.sources[0], label=forged)
        build_engineering_draft(replace(value, sources=(source,)))


def test_unexpected_internal_error_is_reduced_to_content_free_typed_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.modules.summaries import projection

    canary = "private-patient-narrative-canary"

    def fail(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError(canary)

    monkeypatch.setattr(projection, "_readiness", fail)
    with pytest.raises(SummaryValidationError) as caught:
        projection.build_engineering_draft(projection_input())
    rendered = "".join(
        format_exception(type(caught.value), caught.value, caught.value.__traceback__)
    )
    assert canary not in str(caught.value)
    assert canary not in rendered


def test_summary_projection_emits_no_logs_or_telemetry(caplog: pytest.LogCaptureFixture) -> None:
    draft = build_engineering_draft(projection_input())
    assert draft.classification.value == "ENGINEERING_ONLY"
    assert caplog.records == []
