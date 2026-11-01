from __future__ import annotations

from datetime import UTC, datetime, timedelta, timezone
from typing import cast

import pytest

from app.config import Environment
from app.modules.admin_governance import (
    MAX_SYNTHETIC_REVIEW_QUEUE_ITEMS,
    ReviewQueueContractCode,
    ReviewQueueContractError,
    SyntheticReviewItemKind,
    SyntheticReviewItemState,
    SyntheticReviewQueueItem,
    SyntheticReviewQueueSnapshot,
    build_synthetic_review_queue,
)

NOW = datetime(2026, 11, 1, 14, 0, tzinfo=UTC)


def item(suffix: str, **changes: object) -> SyntheticReviewQueueItem:
    values: dict[str, object] = {
        "item_id": f"syn_review_item_{suffix}",
        "object_id": f"syn_review_object_{suffix}",
        "object_version": "engineering.v1",
        "object_hash": suffix[0] * 64,
        "item_kind": SyntheticReviewItemKind.SYNTHETIC_FACT_CANDIDATE,
        "state": SyntheticReviewItemState.PENDING_ENGINEERING_REVIEW,
        "created_at": NOW,
    }
    values.update(changes)
    return SyntheticReviewQueueItem(**values)  # type: ignore[arg-type]


def build(
    values: tuple[SyntheticReviewQueueItem, ...],
    *,
    generated_at: datetime = NOW,
    environment: Environment = Environment.TEST,
) -> SyntheticReviewQueueSnapshot:
    return build_synthetic_review_queue(
        values,
        snapshot_id="syn_review_snapshot_alpha",
        generated_at=generated_at,
        environment=environment,
    )


def test_builder_orders_reconstructed_items_deterministically() -> None:
    beta = item("beta")
    alpha = item("alpha")

    assert build((beta, alpha)) == build((alpha, beta))
    assert tuple(value.item_id for value in build((beta, alpha)).items) == (
        "syn_review_item_alpha",
        "syn_review_item_beta",
    )


def test_builder_rejects_duplicate_ids_and_semantic_aliases() -> None:
    alpha = item("alpha")
    with pytest.raises(ReviewQueueContractError) as duplicate:
        build((alpha, alpha))
    with pytest.raises(ReviewQueueContractError) as alias:
        build((alpha, item("beta", object_id="syn_review_object_alpha", object_hash="a" * 64)))

    assert duplicate.value.code is ReviewQueueContractCode.DUPLICATE_ITEM
    assert alias.value.code is ReviewQueueContractCode.AMBIGUOUS_ITEM


def test_builder_rejects_capacity_before_inspecting_items() -> None:
    hostile = tuple(object() for _ in range(MAX_SYNTHETIC_REVIEW_QUEUE_ITEMS + 1))

    with pytest.raises(ReviewQueueContractError) as captured:
        build_synthetic_review_queue(
            cast(tuple[SyntheticReviewQueueItem, ...], hostile),
            snapshot_id="syn_review_snapshot_alpha",
            generated_at=NOW,
            environment=Environment.TEST,
        )

    assert captured.value.code is ReviewQueueContractCode.LIMIT_EXCEEDED


def test_builder_normalizes_aware_clock_and_rejects_naive_or_early_clock() -> None:
    offset = timezone(timedelta(hours=-4))
    assert build((item("alpha"),), generated_at=NOW.astimezone(offset)).generated_at.tzinfo is UTC
    with pytest.raises(ReviewQueueContractError) as naive:
        build((item("alpha"),), generated_at=NOW.replace(tzinfo=None))
    with pytest.raises(ReviewQueueContractError) as early:
        build((item("alpha"),), generated_at=NOW - timedelta(microseconds=1))

    assert naive.value.code is ReviewQueueContractCode.INVALID_TYPE
    assert early.value.code is ReviewQueueContractCode.INVALID_CHRONOLOGY


def test_builder_revalidates_forced_item_mutation() -> None:
    value = item("alpha")
    object.__setattr__(value, "object_id", "patient-123")

    with pytest.raises(ReviewQueueContractError) as captured:
        build((value,))

    assert captured.value.code is ReviewQueueContractCode.INVALID_VALUE


@pytest.mark.parametrize(
    "environment", [Environment.STAGING, Environment.PILOT, Environment.PRODUCTION]
)
def test_protected_environment_rejects_before_inputs_are_inspected(
    environment: Environment,
) -> None:
    with pytest.raises(ReviewQueueContractError) as captured:
        build_synthetic_review_queue(
            object(),  # type: ignore[arg-type]
            snapshot_id=object(),  # type: ignore[arg-type]
            generated_at=object(),  # type: ignore[arg-type]
            environment=environment,
        )

    assert captured.value.code is ReviewQueueContractCode.PROTECTED_ENVIRONMENT
