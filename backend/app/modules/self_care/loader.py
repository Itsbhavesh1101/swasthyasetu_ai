"""Strict in-memory loader for engineering-only synthetic knowledge packs."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from enum import StrEnum
from typing import cast

from app.modules.self_care.contracts import (
    MAX_SYNTHETIC_KNOWLEDGE_ITEMS,
    SelfCareContractCode,
    SelfCareContractError,
    SyntheticGuidancePlaceholder,
    SyntheticKnowledgeItem,
    SyntheticKnowledgePack,
    SyntheticKnowledgePackState,
    SyntheticKnowledgeReviewState,
    SyntheticKnowledgeTag,
)

_UTC_TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z$")
_PACK_FIELDS = frozenset(
    {
        "contract_version",
        "pack_id",
        "pack_version",
        "schema_version",
        "content_hash",
        "state",
        "created_at",
        "items",
    }
)
_ITEM_FIELDS = frozenset(
    {
        "guidance_id",
        "version",
        "placeholder_token",
        "source_id",
        "source_version",
        "source_hash",
        "tags",
        "review_state",
    }
)


def _error(code: SelfCareContractCode) -> SelfCareContractError:
    return SelfCareContractError(code)


def _exact_fields(value: dict[str, object], expected: frozenset[str]) -> None:
    supplied = frozenset(value)
    if supplied - expected:
        raise _error(SelfCareContractCode.UNKNOWN_FIELD)
    if expected - supplied:
        raise _error(SelfCareContractCode.MISSING_FIELD)


def _observed_utc(value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise _error(SelfCareContractCode.INVALID_TYPE)
    return value.astimezone(UTC)


def _parse_utc(value: object) -> datetime:
    if type(value) is not str:
        raise _error(SelfCareContractCode.INVALID_TYPE)
    if _UTC_TIMESTAMP.fullmatch(value) is None:
        raise _error(SelfCareContractCode.INVALID_VALUE)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)
    except ValueError:
        raise _error(SelfCareContractCode.INVALID_VALUE) from None
    canonical = parsed.isoformat(timespec="milliseconds" if "." in value else "seconds").replace(
        "+00:00", "Z"
    )
    if canonical != value:
        raise _error(SelfCareContractCode.INVALID_VALUE)
    return parsed


def _enum(value: object, expected: type[StrEnum]) -> StrEnum:
    if type(value) is not str:
        raise _error(SelfCareContractCode.INVALID_TYPE)
    try:
        return expected(value)
    except ValueError:
        raise _error(SelfCareContractCode.INVALID_VALUE) from None


def _parse_item(value: object) -> SyntheticKnowledgeItem:
    if type(value) is not dict:
        raise _error(SelfCareContractCode.INVALID_TYPE)
    item = cast(dict[str, object], value)
    _exact_fields(item, _ITEM_FIELDS)
    raw_tags = item["tags"]
    if type(raw_tags) is not list:
        raise _error(SelfCareContractCode.INVALID_TYPE)
    tags = tuple(cast(SyntheticKnowledgeTag, _enum(tag, SyntheticKnowledgeTag)) for tag in raw_tags)
    return SyntheticKnowledgeItem(
        guidance_id=cast(str, item["guidance_id"]),
        version=cast(str, item["version"]),
        placeholder_token=cast(
            SyntheticGuidancePlaceholder,
            _enum(item["placeholder_token"], SyntheticGuidancePlaceholder),
        ),
        source_id=cast(str, item["source_id"]),
        source_version=cast(str, item["source_version"]),
        source_hash=cast(str, item["source_hash"]),
        tags=tags,
        review_state=cast(
            SyntheticKnowledgeReviewState,
            _enum(item["review_state"], SyntheticKnowledgeReviewState),
        ),
    )


def parse_synthetic_knowledge_pack(
    payload: object,
    *,
    observed_at: datetime,
) -> SyntheticKnowledgePack:
    """Parse one exact synthetic pack without file, network, or runtime activation."""

    if type(payload) is not dict:
        raise _error(SelfCareContractCode.INVALID_TYPE)
    value = cast(dict[str, object], payload)
    try:
        _exact_fields(value, _PACK_FIELDS)
        observed = _observed_utc(observed_at)
        created_at = _parse_utc(value["created_at"])
        if created_at > observed:
            raise _error(SelfCareContractCode.INVALID_VALUE)
        raw_items = value["items"]
        if type(raw_items) is not list:
            raise _error(SelfCareContractCode.INVALID_TYPE)
        if not raw_items or len(raw_items) > MAX_SYNTHETIC_KNOWLEDGE_ITEMS:
            raise _error(SelfCareContractCode.LIMIT_EXCEEDED)
        items = tuple(_parse_item(entry) for entry in raw_items)
        return SyntheticKnowledgePack(
            contract_version=cast(str, value["contract_version"]),
            pack_id=cast(str, value["pack_id"]),
            pack_version=cast(str, value["pack_version"]),
            schema_version=cast(str, value["schema_version"]),
            content_hash=cast(str, value["content_hash"]),
            state=cast(
                SyntheticKnowledgePackState,
                _enum(value["state"], SyntheticKnowledgePackState),
            ),
            created_at=created_at,
            items=items,
        )
    except SelfCareContractError:
        raise
    except (KeyError, AttributeError, TypeError, ValueError, RuntimeError):
        raise _error(SelfCareContractCode.INVALID_TYPE) from None


__all__ = ["parse_synthetic_knowledge_pack"]
