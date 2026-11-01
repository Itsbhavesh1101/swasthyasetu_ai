"""Pure builder for detached engineering-synthetic review queue snapshots."""

from __future__ import annotations

from datetime import datetime

from app.config import Environment
from app.modules.admin_governance.review_queue_contracts import (
    MAX_SYNTHETIC_REVIEW_QUEUE_ITEMS,
    ReviewQueueContractCode,
    ReviewQueueContractError,
    SyntheticReviewQueueItem,
    SyntheticReviewQueueSnapshot,
    snapshot_review_queue_item,
)

_PROTECTED_ENVIRONMENTS = frozenset(
    {Environment.STAGING, Environment.PILOT, Environment.PRODUCTION}
)


def _error(code: ReviewQueueContractCode) -> ReviewQueueContractError:
    return ReviewQueueContractError(code)


def build_synthetic_review_queue(
    items: tuple[SyntheticReviewQueueItem, ...],
    *,
    snapshot_id: str,
    generated_at: datetime,
    environment: Environment,
) -> SyntheticReviewQueueSnapshot:
    """Build a content-free synthetic snapshot; never grant review authority."""

    if type(environment) is not Environment:
        raise _error(ReviewQueueContractCode.INVALID_TYPE)
    if environment in _PROTECTED_ENVIRONMENTS:
        raise _error(ReviewQueueContractCode.PROTECTED_ENVIRONMENT)
    if type(items) is not tuple:
        raise _error(ReviewQueueContractCode.INVALID_TYPE)
    if len(items) > MAX_SYNTHETIC_REVIEW_QUEUE_ITEMS:
        raise _error(ReviewQueueContractCode.LIMIT_EXCEEDED)
    safe_items = tuple(
        sorted((snapshot_review_queue_item(item) for item in items), key=lambda item: item.item_id)
    )
    return SyntheticReviewQueueSnapshot(
        snapshot_id=snapshot_id,
        generated_at=generated_at,
        items=safe_items,
    )


__all__ = ["build_synthetic_review_queue"]
