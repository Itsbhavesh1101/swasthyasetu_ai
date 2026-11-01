"""Content-free contracts for a detached engineering-synthetic review queue."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256
from typing import Final

from app.modules.admin_governance.contracts import (
    AdminAuthority,
    AdminClassification,
    AdminVerification,
)

SYNTHETIC_REVIEW_QUEUE_CONTRACT_VERSION: Final = "synthetic-review-queue.v1"
MAX_SYNTHETIC_REVIEW_QUEUE_ITEMS: Final = 16

_ITEM_ID = re.compile(r"^syn_review_item_(?:alpha|beta|gamma|delta)$")
_OBJECT_ID = re.compile(r"^syn_review_object_(?:alpha|beta|gamma|delta)$")
_SNAPSHOT_ID = re.compile(r"^syn_review_snapshot_(?:alpha|beta|gamma|delta)$")
_VERSION = re.compile(r"^engineering\.v[1-9][0-9]{0,5}$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")


class ReviewQueueContractCode(StrEnum):
    INVALID_TYPE = "INVALID_TYPE"
    INVALID_VALUE = "INVALID_VALUE"
    INVALID_CHRONOLOGY = "INVALID_CHRONOLOGY"
    LIMIT_EXCEEDED = "LIMIT_EXCEEDED"
    DUPLICATE_ITEM = "DUPLICATE_ITEM"
    AMBIGUOUS_ITEM = "AMBIGUOUS_ITEM"
    SNAPSHOT_DRIFT = "SNAPSHOT_DRIFT"
    PROTECTED_ENVIRONMENT = "PROTECTED_ENVIRONMENT"


class ReviewQueueContractError(ValueError):
    """Stable content-free synthetic review queue failure."""

    def __init__(self, code: ReviewQueueContractCode) -> None:
        self.code = code
        super().__init__(code.value)


class SyntheticReviewItemKind(StrEnum):
    SYNTHETIC_FACT_CANDIDATE = "SYNTHETIC_FACT_CANDIDATE"
    SYNTHETIC_SUMMARY_CANDIDATE = "SYNTHETIC_SUMMARY_CANDIDATE"


class SyntheticReviewItemState(StrEnum):
    PENDING_ENGINEERING_REVIEW = "PENDING_ENGINEERING_REVIEW"
    STALE_ENGINEERING_SNAPSHOT = "STALE_ENGINEERING_SNAPSHOT"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
    SYNTHETIC_CONFLICT = "SYNTHETIC_CONFLICT"


def _error(code: ReviewQueueContractCode) -> ReviewQueueContractError:
    return ReviewQueueContractError(code)


def _strict_enum(value: object, expected: type[StrEnum]) -> None:
    if type(value) is not expected:
        raise _error(ReviewQueueContractCode.INVALID_TYPE)


def _machine_string(value: object, pattern: re.Pattern[str]) -> str:
    if type(value) is not str:
        raise _error(ReviewQueueContractCode.INVALID_TYPE)
    if pattern.fullmatch(value) is None:
        raise _error(ReviewQueueContractCode.INVALID_VALUE)
    return value


def _utc(value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise _error(ReviewQueueContractCode.INVALID_TYPE)
    return value.astimezone(UTC)


def _labels(authority: object, classification: object, verification: object) -> None:
    if authority is not AdminAuthority.ENGINEERING_ONLY:
        raise _error(ReviewQueueContractCode.INVALID_VALUE)
    if classification is not AdminClassification.ENGINEERING_SYNTHETIC:
        raise _error(ReviewQueueContractCode.INVALID_VALUE)
    if verification is not AdminVerification.UNVERIFIED:
        raise _error(ReviewQueueContractCode.INVALID_VALUE)


def _canonical_hash(payload: object) -> str:
    return sha256(
        json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticReviewQueueItem:
    item_id: str
    object_id: str
    object_version: str
    object_hash: str
    item_kind: SyntheticReviewItemKind
    state: SyntheticReviewItemState
    created_at: datetime
    authority: AdminAuthority = AdminAuthority.ENGINEERING_ONLY
    classification: AdminClassification = AdminClassification.ENGINEERING_SYNTHETIC
    verification: AdminVerification = AdminVerification.UNVERIFIED
    _fingerprint: str = field(init=False, repr=False, compare=True)

    def __post_init__(self) -> None:
        _machine_string(self.item_id, _ITEM_ID)
        _machine_string(self.object_id, _OBJECT_ID)
        _machine_string(self.object_version, _VERSION)
        _machine_string(self.object_hash, _SHA256)
        _strict_enum(self.item_kind, SyntheticReviewItemKind)
        _strict_enum(self.state, SyntheticReviewItemState)
        created_at = _utc(self.created_at)
        _labels(self.authority, self.classification, self.verification)
        fingerprint = _canonical_hash(
            {
                "contract_version": SYNTHETIC_REVIEW_QUEUE_CONTRACT_VERSION,
                "created_at": created_at.isoformat(),
                "item_id": self.item_id,
                "item_kind": self.item_kind.value,
                "object_hash": self.object_hash,
                "object_id": self.object_id,
                "object_version": self.object_version,
                "state": self.state.value,
            }
        )
        object.__setattr__(self, "created_at", created_at)
        object.__setattr__(self, "_fingerprint", fingerprint)

    @property
    def fingerprint(self) -> str:
        return self._fingerprint


def snapshot_review_queue_item(value: object) -> SyntheticReviewQueueItem:
    if type(value) is not SyntheticReviewQueueItem:
        raise _error(ReviewQueueContractCode.INVALID_TYPE)
    try:
        snapshot = SyntheticReviewQueueItem(
            item_id=value.item_id,
            object_id=value.object_id,
            object_version=value.object_version,
            object_hash=value.object_hash,
            item_kind=value.item_kind,
            state=value.state,
            created_at=value.created_at,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
        )
    except ReviewQueueContractError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(ReviewQueueContractCode.INVALID_TYPE) from None
    if snapshot.fingerprint != value.fingerprint:
        raise _error(ReviewQueueContractCode.SNAPSHOT_DRIFT)
    return snapshot


def _semantic_key(item: SyntheticReviewQueueItem) -> tuple[object, ...]:
    return (item.object_id, item.object_version, item.object_hash)


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticReviewQueueSnapshot:
    snapshot_id: str
    generated_at: datetime
    items: tuple[SyntheticReviewQueueItem, ...]
    authority: AdminAuthority = AdminAuthority.ENGINEERING_ONLY
    classification: AdminClassification = AdminClassification.ENGINEERING_SYNTHETIC
    verification: AdminVerification = AdminVerification.UNVERIFIED
    contract_version: str = SYNTHETIC_REVIEW_QUEUE_CONTRACT_VERSION
    _fingerprint: str = field(init=False, repr=False, compare=True)

    def __post_init__(self) -> None:
        _machine_string(self.snapshot_id, _SNAPSHOT_ID)
        generated_at = _utc(self.generated_at)
        if type(self.items) is not tuple:
            raise _error(ReviewQueueContractCode.INVALID_TYPE)
        if len(self.items) > MAX_SYNTHETIC_REVIEW_QUEUE_ITEMS:
            raise _error(ReviewQueueContractCode.LIMIT_EXCEEDED)
        safe_items = tuple(snapshot_review_queue_item(item) for item in self.items)
        item_ids = tuple(item.item_id for item in safe_items)
        if len(set(item_ids)) != len(item_ids):
            raise _error(ReviewQueueContractCode.DUPLICATE_ITEM)
        semantic_keys = tuple(_semantic_key(item) for item in safe_items)
        if len(set(semantic_keys)) != len(semantic_keys):
            raise _error(ReviewQueueContractCode.AMBIGUOUS_ITEM)
        if item_ids != tuple(sorted(item_ids)):
            raise _error(ReviewQueueContractCode.INVALID_VALUE)
        if any(item.created_at > generated_at for item in safe_items):
            raise _error(ReviewQueueContractCode.INVALID_CHRONOLOGY)
        _labels(self.authority, self.classification, self.verification)
        if (
            type(self.contract_version) is not str
            or self.contract_version != SYNTHETIC_REVIEW_QUEUE_CONTRACT_VERSION
        ):
            raise _error(ReviewQueueContractCode.INVALID_VALUE)
        fingerprint = _canonical_hash(
            {
                "contract_version": self.contract_version,
                "generated_at": generated_at.isoformat(),
                "item_fingerprints": [item.fingerprint for item in safe_items],
                "snapshot_id": self.snapshot_id,
            }
        )
        object.__setattr__(self, "generated_at", generated_at)
        object.__setattr__(self, "items", safe_items)
        object.__setattr__(self, "_fingerprint", fingerprint)

    @property
    def fingerprint(self) -> str:
        return self._fingerprint


def snapshot_review_queue(value: object) -> SyntheticReviewQueueSnapshot:
    if type(value) is not SyntheticReviewQueueSnapshot:
        raise _error(ReviewQueueContractCode.INVALID_TYPE)
    try:
        snapshot = SyntheticReviewQueueSnapshot(
            snapshot_id=value.snapshot_id,
            generated_at=value.generated_at,
            items=value.items,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
            contract_version=value.contract_version,
        )
    except ReviewQueueContractError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(ReviewQueueContractCode.INVALID_TYPE) from None
    if snapshot.fingerprint != value.fingerprint:
        raise _error(ReviewQueueContractCode.SNAPSHOT_DRIFT)
    return snapshot


__all__ = [
    "MAX_SYNTHETIC_REVIEW_QUEUE_ITEMS",
    "SYNTHETIC_REVIEW_QUEUE_CONTRACT_VERSION",
    "ReviewQueueContractCode",
    "ReviewQueueContractError",
    "SyntheticReviewItemKind",
    "SyntheticReviewItemState",
    "SyntheticReviewQueueItem",
    "SyntheticReviewQueueSnapshot",
    "snapshot_review_queue",
    "snapshot_review_queue_item",
]
