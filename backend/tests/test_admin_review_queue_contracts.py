from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime, timedelta, timezone
from typing import Any, cast

import pytest

from app.modules.admin_governance import (
    SYNTHETIC_REVIEW_QUEUE_CONTRACT_VERSION,
    ReviewQueueContractCode,
    ReviewQueueContractError,
    SyntheticReviewItemKind,
    SyntheticReviewItemState,
    SyntheticReviewQueueItem,
    SyntheticReviewQueueSnapshot,
    snapshot_review_queue,
    snapshot_review_queue_item,
)

NOW = datetime(2026, 11, 1, 14, 0, tzinfo=UTC)
HASH_A = "a" * 64


def item(suffix: str = "alpha", **changes: object) -> SyntheticReviewQueueItem:
    values: dict[str, object] = {
        "item_id": f"syn_review_item_{suffix}",
        "object_id": f"syn_review_object_{suffix}",
        "object_version": "engineering.v1",
        "object_hash": HASH_A,
        "item_kind": SyntheticReviewItemKind.SYNTHETIC_FACT_CANDIDATE,
        "state": SyntheticReviewItemState.PENDING_ENGINEERING_REVIEW,
        "created_at": NOW,
    }
    values.update(changes)
    return SyntheticReviewQueueItem(**values)  # type: ignore[arg-type]


def queue(*items: SyntheticReviewQueueItem, **changes: object) -> SyntheticReviewQueueSnapshot:
    values: dict[str, object] = {
        "snapshot_id": "syn_review_snapshot_alpha",
        "generated_at": NOW,
        "items": items,
    }
    values.update(changes)
    return SyntheticReviewQueueSnapshot(**values)  # type: ignore[arg-type]


def test_item_is_immutable_utc_normalized_and_fingerprinted() -> None:
    offset = timezone(timedelta(hours=5, minutes=30))
    value = item(created_at=NOW.astimezone(offset))

    assert value.created_at == NOW
    assert value.created_at.tzinfo is UTC
    assert len(value.fingerprint) == 64
    with pytest.raises(FrozenInstanceError):
        value.object_id = "syn_review_object_beta"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("field", "invalid"),
    [
        ("item_id", "review-item-alpha"),
        ("object_id", "patient-123"),
        ("object_version", "live.v1"),
        ("object_hash", "not-a-hash"),
        ("item_kind", "SYNTHETIC_FACT_CANDIDATE"),
        ("state", "PENDING_ENGINEERING_REVIEW"),
        ("created_at", datetime(2026, 11, 1, 14, 0)),
    ],
)
def test_item_rejects_non_synthetic_or_non_strict_values(field: str, invalid: object) -> None:
    with pytest.raises(ReviewQueueContractError):
        cast(Any, item)(**{field: invalid})


def test_item_fingerprint_binds_every_field() -> None:
    original = item()
    variants = (
        item("beta", object_id="syn_review_object_alpha"),
        item(object_version="engineering.v2"),
        item(object_hash="b" * 64),
        item(item_kind=SyntheticReviewItemKind.SYNTHETIC_SUMMARY_CANDIDATE),
        item(state=SyntheticReviewItemState.STALE_ENGINEERING_SNAPSHOT),
        item(created_at=NOW + timedelta(seconds=1)),
    )

    assert len({original.fingerprint, *(value.fingerprint for value in variants)}) == 7


def test_snapshot_requires_canonical_unique_items_and_consistent_chronology() -> None:
    alpha = item("alpha")
    beta = item("beta", object_hash="b" * 64)
    value = queue(alpha, beta)

    assert value.contract_version == SYNTHETIC_REVIEW_QUEUE_CONTRACT_VERSION
    assert len(value.fingerprint) == 64
    assert value.items == (alpha, beta)
    with pytest.raises(ReviewQueueContractError) as unordered:
        queue(beta, alpha)
    with pytest.raises(ReviewQueueContractError) as duplicate:
        queue(alpha, alpha)
    with pytest.raises(ReviewQueueContractError) as alias:
        queue(
            alpha,
            item("beta", object_id="syn_review_object_alpha"),
        )
    with pytest.raises(ReviewQueueContractError) as early:
        queue(item(created_at=NOW + timedelta(microseconds=1)))

    assert unordered.value.code is ReviewQueueContractCode.INVALID_VALUE
    assert duplicate.value.code is ReviewQueueContractCode.DUPLICATE_ITEM
    assert alias.value.code is ReviewQueueContractCode.AMBIGUOUS_ITEM
    assert early.value.code is ReviewQueueContractCode.INVALID_CHRONOLOGY


def test_snapshot_helpers_reconstruct_and_detect_forced_mutation() -> None:
    value = item()
    safe_queue = queue(value)
    assert snapshot_review_queue_item(value) == value
    assert snapshot_review_queue(safe_queue) == safe_queue

    object.__setattr__(value, "object_id", "patient-123")
    object.__setattr__(safe_queue.items[0], "object_id", "patient-123")
    with pytest.raises(ReviewQueueContractError):
        snapshot_review_queue_item(value)
    with pytest.raises(ReviewQueueContractError):
        snapshot_review_queue(safe_queue)


def test_snapshot_rejects_contract_version_drift() -> None:
    with pytest.raises(ReviewQueueContractError) as captured:
        replace(queue(), contract_version="synthetic-review-queue.v2")

    assert captured.value.code is ReviewQueueContractCode.INVALID_VALUE
