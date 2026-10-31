"""Strict engineering-only self-care knowledge-pack contracts."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256
from typing import Final

SYNTHETIC_KNOWLEDGE_CONTRACT_VERSION: Final = "synthetic-self-care-knowledge.v1"
MAX_SYNTHETIC_KNOWLEDGE_ITEMS: Final = 4
MAX_SYNTHETIC_KNOWLEDGE_TAGS: Final = 4

_SUFFIX = r"(?:alpha|beta|gamma|delta)"
_GUIDANCE_ID = re.compile(rf"^syn_selfcare_guidance_{_SUFFIX}$")
_SOURCE_ID = re.compile(rf"^syn_selfcare_source_{_SUFFIX}$")
_PACK_ID = re.compile(r"^syn_selfcare_pack_fixture$")
_VERSION = re.compile(r"^engineering\.v[1-9][0-9]{0,5}$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")


class SelfCareContractCode(StrEnum):
    INVALID_TYPE = "INVALID_TYPE"
    INVALID_VALUE = "INVALID_VALUE"
    LIMIT_EXCEEDED = "LIMIT_EXCEEDED"
    DUPLICATE_ITEM = "DUPLICATE_ITEM"
    HASH_MISMATCH = "HASH_MISMATCH"
    UNKNOWN_FIELD = "UNKNOWN_FIELD"
    MISSING_FIELD = "MISSING_FIELD"


class SelfCareContractError(ValueError):
    """Stable content-free error for synthetic knowledge contracts."""

    def __init__(self, code: SelfCareContractCode) -> None:
        self.code = code
        super().__init__(code.value)


def _error(code: SelfCareContractCode) -> SelfCareContractError:
    return SelfCareContractError(code)


class SyntheticKnowledgeAuthority(StrEnum):
    ENGINEERING_ONLY = "ENGINEERING_ONLY"


class SyntheticKnowledgeClassification(StrEnum):
    ENGINEERING_SYNTHETIC = "ENGINEERING_SYNTHETIC"


class SyntheticKnowledgeVerification(StrEnum):
    UNVERIFIED = "UNVERIFIED"


class SyntheticGuidancePlaceholder(StrEnum):
    ALPHA = "SYNTHETIC_PLACEHOLDER_ALPHA"
    BETA = "SYNTHETIC_PLACEHOLDER_BETA"
    GAMMA = "SYNTHETIC_PLACEHOLDER_GAMMA"
    DELTA = "SYNTHETIC_PLACEHOLDER_DELTA"


class SyntheticKnowledgeTag(StrEnum):
    ALPHA = "SYNTHETIC_TAG_ALPHA"
    BETA = "SYNTHETIC_TAG_BETA"
    GAMMA = "SYNTHETIC_TAG_GAMMA"
    DELTA = "SYNTHETIC_TAG_DELTA"


class SyntheticKnowledgeReviewState(StrEnum):
    TEST_ONLY_UNAPPROVED = "TEST_ONLY_UNAPPROVED"


class SyntheticKnowledgePackState(StrEnum):
    TEST_ONLY_UNAPPROVED = "TEST_ONLY_UNAPPROVED"


def _strict_enum(value: object, expected: type[StrEnum]) -> None:
    if type(value) is not expected:
        raise _error(SelfCareContractCode.INVALID_TYPE)


def _machine_string(value: object, pattern: re.Pattern[str]) -> str:
    if type(value) is not str:
        raise _error(SelfCareContractCode.INVALID_TYPE)
    if pattern.fullmatch(value) is None:
        raise _error(SelfCareContractCode.INVALID_VALUE)
    return value


def _utc(value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise _error(SelfCareContractCode.INVALID_TYPE)
    return value.astimezone(UTC)


def _authority(
    authority: object,
    classification: object,
    verification: object,
) -> None:
    _strict_enum(authority, SyntheticKnowledgeAuthority)
    _strict_enum(classification, SyntheticKnowledgeClassification)
    _strict_enum(verification, SyntheticKnowledgeVerification)


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticKnowledgeItem:
    guidance_id: str
    version: str
    placeholder_token: SyntheticGuidancePlaceholder
    source_id: str
    source_version: str
    source_hash: str
    tags: tuple[SyntheticKnowledgeTag, ...]
    review_state: SyntheticKnowledgeReviewState = SyntheticKnowledgeReviewState.TEST_ONLY_UNAPPROVED
    authority: SyntheticKnowledgeAuthority = SyntheticKnowledgeAuthority.ENGINEERING_ONLY
    classification: SyntheticKnowledgeClassification = (
        SyntheticKnowledgeClassification.ENGINEERING_SYNTHETIC
    )
    verification: SyntheticKnowledgeVerification = SyntheticKnowledgeVerification.UNVERIFIED

    def __post_init__(self) -> None:
        _machine_string(self.guidance_id, _GUIDANCE_ID)
        _machine_string(self.version, _VERSION)
        _strict_enum(self.placeholder_token, SyntheticGuidancePlaceholder)
        _machine_string(self.source_id, _SOURCE_ID)
        _machine_string(self.source_version, _VERSION)
        _machine_string(self.source_hash, _SHA256)
        if type(self.tags) is not tuple:
            raise _error(SelfCareContractCode.INVALID_TYPE)
        if not self.tags or len(self.tags) > MAX_SYNTHETIC_KNOWLEDGE_TAGS:
            raise _error(SelfCareContractCode.LIMIT_EXCEEDED)
        for tag in self.tags:
            _strict_enum(tag, SyntheticKnowledgeTag)
        values = tuple(tag.value for tag in self.tags)
        if len(set(values)) != len(values) or values != tuple(sorted(values)):
            raise _error(SelfCareContractCode.INVALID_VALUE)
        _strict_enum(self.review_state, SyntheticKnowledgeReviewState)
        _authority(self.authority, self.classification, self.verification)
        object.__setattr__(self, "tags", tuple(self.tags))


def _item(value: object) -> SyntheticKnowledgeItem:
    if type(value) is not SyntheticKnowledgeItem:
        raise _error(SelfCareContractCode.INVALID_TYPE)
    try:
        return SyntheticKnowledgeItem(
            guidance_id=value.guidance_id,
            version=value.version,
            placeholder_token=value.placeholder_token,
            source_id=value.source_id,
            source_version=value.source_version,
            source_hash=value.source_hash,
            tags=value.tags,
            review_state=value.review_state,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
        )
    except SelfCareContractError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(SelfCareContractCode.INVALID_TYPE) from None


def _knowledge_hash(
    *,
    pack_id: str,
    pack_version: str,
    schema_version: str,
    state: SyntheticKnowledgePackState,
    created_at: datetime,
    items: tuple[SyntheticKnowledgeItem, ...],
    authority: SyntheticKnowledgeAuthority,
    classification: SyntheticKnowledgeClassification,
    verification: SyntheticKnowledgeVerification,
) -> str:
    fields = [
        SYNTHETIC_KNOWLEDGE_CONTRACT_VERSION,
        pack_id,
        pack_version,
        schema_version,
        state.value,
        created_at.isoformat(),
        authority.value,
        classification.value,
        verification.value,
    ]
    for entry in items:
        fields.extend(
            (
                entry.guidance_id,
                entry.version,
                entry.placeholder_token.value,
                entry.source_id,
                entry.source_version,
                entry.source_hash,
                entry.review_state.value,
                entry.authority.value,
                entry.classification.value,
                entry.verification.value,
            )
        )
        fields.extend(tag.value for tag in entry.tags)
    return sha256("\x1f".join(fields).encode("ascii")).hexdigest()


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticKnowledgePack:
    contract_version: str
    pack_id: str
    pack_version: str
    schema_version: str
    content_hash: str
    state: SyntheticKnowledgePackState
    created_at: datetime
    items: tuple[SyntheticKnowledgeItem, ...]
    authority: SyntheticKnowledgeAuthority = SyntheticKnowledgeAuthority.ENGINEERING_ONLY
    classification: SyntheticKnowledgeClassification = (
        SyntheticKnowledgeClassification.ENGINEERING_SYNTHETIC
    )
    verification: SyntheticKnowledgeVerification = SyntheticKnowledgeVerification.UNVERIFIED

    def __post_init__(self) -> None:
        if type(self.contract_version) is not str:
            raise _error(SelfCareContractCode.INVALID_TYPE)
        if self.contract_version != SYNTHETIC_KNOWLEDGE_CONTRACT_VERSION:
            raise _error(SelfCareContractCode.INVALID_VALUE)
        pack_id = _machine_string(self.pack_id, _PACK_ID)
        pack_version = _machine_string(self.pack_version, _VERSION)
        if type(self.schema_version) is not str:
            raise _error(SelfCareContractCode.INVALID_TYPE)
        if self.schema_version != SYNTHETIC_KNOWLEDGE_CONTRACT_VERSION:
            raise _error(SelfCareContractCode.INVALID_VALUE)
        _machine_string(self.content_hash, _SHA256)
        _strict_enum(self.state, SyntheticKnowledgePackState)
        created_at = _utc(self.created_at)
        if type(self.items) is not tuple:
            raise _error(SelfCareContractCode.INVALID_TYPE)
        if not self.items or len(self.items) > MAX_SYNTHETIC_KNOWLEDGE_ITEMS:
            raise _error(SelfCareContractCode.LIMIT_EXCEEDED)
        items = tuple(_item(entry) for entry in self.items)
        item_ids = tuple(entry.guidance_id for entry in items)
        if len(set(item_ids)) != len(item_ids):
            raise _error(SelfCareContractCode.DUPLICATE_ITEM)
        if item_ids != tuple(sorted(item_ids)):
            raise _error(SelfCareContractCode.INVALID_VALUE)
        _authority(self.authority, self.classification, self.verification)
        expected_hash = _knowledge_hash(
            pack_id=pack_id,
            pack_version=pack_version,
            schema_version=self.schema_version,
            state=self.state,
            created_at=created_at,
            items=items,
            authority=self.authority,
            classification=self.classification,
            verification=self.verification,
        )
        if self.content_hash != expected_hash:
            raise _error(SelfCareContractCode.HASH_MISMATCH)
        object.__setattr__(self, "created_at", created_at)
        object.__setattr__(self, "items", items)


def create_synthetic_knowledge_pack(
    *,
    pack_id: str,
    pack_version: str,
    schema_version: str,
    state: SyntheticKnowledgePackState,
    created_at: datetime,
    items: tuple[SyntheticKnowledgeItem, ...],
) -> SyntheticKnowledgePack:
    """Create one deterministic unapproved engineering pack."""

    pack_id = _machine_string(pack_id, _PACK_ID)
    pack_version = _machine_string(pack_version, _VERSION)
    if type(schema_version) is not str:
        raise _error(SelfCareContractCode.INVALID_TYPE)
    if schema_version != SYNTHETIC_KNOWLEDGE_CONTRACT_VERSION:
        raise _error(SelfCareContractCode.INVALID_VALUE)
    _strict_enum(state, SyntheticKnowledgePackState)
    normalized_time = _utc(created_at)
    if type(items) is not tuple:
        raise _error(SelfCareContractCode.INVALID_TYPE)
    validated_items = tuple(_item(entry) for entry in items)
    authority = SyntheticKnowledgeAuthority.ENGINEERING_ONLY
    classification = SyntheticKnowledgeClassification.ENGINEERING_SYNTHETIC
    verification = SyntheticKnowledgeVerification.UNVERIFIED
    return SyntheticKnowledgePack(
        contract_version=SYNTHETIC_KNOWLEDGE_CONTRACT_VERSION,
        pack_id=pack_id,
        pack_version=pack_version,
        schema_version=schema_version,
        content_hash=_knowledge_hash(
            pack_id=pack_id,
            pack_version=pack_version,
            schema_version=schema_version,
            state=state,
            created_at=normalized_time,
            items=validated_items,
            authority=authority,
            classification=classification,
            verification=verification,
        ),
        state=state,
        created_at=normalized_time,
        items=validated_items,
        authority=authority,
        classification=classification,
        verification=verification,
    )


def validate_synthetic_knowledge_pack(value: object) -> SyntheticKnowledgePack:
    """Reconstruct one pack so forced nested mutation fails closed."""

    if type(value) is not SyntheticKnowledgePack:
        raise _error(SelfCareContractCode.INVALID_TYPE)
    try:
        return SyntheticKnowledgePack(
            contract_version=value.contract_version,
            pack_id=value.pack_id,
            pack_version=value.pack_version,
            schema_version=value.schema_version,
            content_hash=value.content_hash,
            state=value.state,
            created_at=value.created_at,
            items=value.items,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
        )
    except SelfCareContractError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(SelfCareContractCode.INVALID_TYPE) from None


__all__ = [
    "MAX_SYNTHETIC_KNOWLEDGE_ITEMS",
    "MAX_SYNTHETIC_KNOWLEDGE_TAGS",
    "SYNTHETIC_KNOWLEDGE_CONTRACT_VERSION",
    "SelfCareContractCode",
    "SelfCareContractError",
    "SyntheticGuidancePlaceholder",
    "SyntheticKnowledgeAuthority",
    "SyntheticKnowledgeClassification",
    "SyntheticKnowledgeItem",
    "SyntheticKnowledgePack",
    "SyntheticKnowledgePackState",
    "SyntheticKnowledgeReviewState",
    "SyntheticKnowledgeTag",
    "SyntheticKnowledgeVerification",
    "create_synthetic_knowledge_pack",
    "validate_synthetic_knowledge_pack",
]
