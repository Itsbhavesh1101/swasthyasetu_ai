from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.config import Environment, Settings
from app.main import create_app
from app.modules.admin_governance import (
    ReviewQueueContractError,
    SyntheticReviewItemKind,
    SyntheticReviewItemState,
    SyntheticReviewQueueItem,
    build_synthetic_review_queue,
)

NOW = datetime(2026, 11, 1, 14, 0, tzinfo=UTC)


def test_errors_do_not_echo_hostile_values() -> None:
    hostile = "patient@example.test/clinical-secret"

    with pytest.raises(ReviewQueueContractError) as captured:
        SyntheticReviewQueueItem(
            item_id="syn_review_item_alpha",
            object_id=hostile,
            object_version="engineering.v1",
            object_hash="a" * 64,
            item_kind=SyntheticReviewItemKind.SYNTHETIC_FACT_CANDIDATE,
            state=SyntheticReviewItemState.PENDING_ENGINEERING_REVIEW,
            created_at=NOW,
        )

    assert hostile not in str(captured.value)


def test_snapshot_exposes_no_clinical_content_or_action_surface() -> None:
    value = SyntheticReviewQueueItem(
        item_id="syn_review_item_alpha",
        object_id="syn_review_object_alpha",
        object_version="engineering.v1",
        object_hash="a" * 64,
        item_kind=SyntheticReviewItemKind.SYNTHETIC_SUMMARY_CANDIDATE,
        state=SyntheticReviewItemState.SOURCE_UNAVAILABLE,
        created_at=NOW,
    )
    snapshot = build_synthetic_review_queue(
        (value,),
        snapshot_id="syn_review_snapshot_alpha",
        generated_at=NOW,
        environment=Environment.LOCAL,
    )

    for prohibited in (
        "assign",
        "authorize",
        "confirm",
        "correct",
        "execute",
        "patient_id",
        "encounter_id",
        "clinical_value",
        "reject",
        "reviewer_id",
        "write",
    ):
        assert not hasattr(snapshot, prohibited)
        assert all(not hasattr(item, prohibited) for item in snapshot.items)


def test_review_queue_foundation_is_not_registered_or_exposed_as_an_api() -> None:
    application = create_app(Settings(_env_file=None))
    module_ids = set(application.state.module_registry.module_ids)
    route_paths = {
        path
        for route in application.routes
        if isinstance(path := getattr(route, "path", None), str)
    }

    assert "admin_governance" not in module_ids
    assert "clinical_review" not in module_ids
    assert all("admin" not in path and "review" not in path for path in route_paths)
