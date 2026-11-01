"""Detached engineering-synthetic P23 accessibility evidence contracts."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256
from typing import Final

from app.config import Environment

SYNTHETIC_ACCESSIBILITY_EVIDENCE_CONTRACT_VERSION: Final = "synthetic-accessibility-evidence.v1"

_VERSION = re.compile(r"^engineering\.v[1-9][0-9]{0,5}$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_GIT_SHA = re.compile(r"^[a-f0-9]{40}$")
_OBSERVATION_ID = re.compile(r"^syn_accessibility_observation_(?:alpha|beta|gamma|delta)$")
_MANIFEST_ID = re.compile(r"^syn_accessibility_manifest_(?:alpha|beta|gamma|delta)$")
_PROTECTED_ENVIRONMENTS = frozenset(
    {Environment.STAGING, Environment.PILOT, Environment.PRODUCTION}
)


class AccessibilityEvidenceContractCode(StrEnum):
    INVALID_TYPE = "INVALID_TYPE"
    INVALID_VALUE = "INVALID_VALUE"
    INVALID_CHRONOLOGY = "INVALID_CHRONOLOGY"
    INCONSISTENT_RECEIPT = "INCONSISTENT_RECEIPT"
    INCOMPLETE_INVENTORY = "INCOMPLETE_INVENTORY"
    DUPLICATE_AREA = "DUPLICATE_AREA"
    INVALID_ORDER = "INVALID_ORDER"
    SNAPSHOT_DRIFT = "SNAPSHOT_DRIFT"
    PROTECTED_ENVIRONMENT = "PROTECTED_ENVIRONMENT"


class AccessibilityEvidenceContractError(ValueError):
    """Stable content-free accessibility evidence failure."""

    def __init__(self, code: AccessibilityEvidenceContractCode) -> None:
        self.code = code
        super().__init__(code.value)


class AccessibilityEvidenceAuthority(StrEnum):
    ENGINEERING_ONLY = "ENGINEERING_ONLY"


class AccessibilityEvidenceClassification(StrEnum):
    ENGINEERING_SYNTHETIC = "ENGINEERING_SYNTHETIC"


class AccessibilityEvidenceVerification(StrEnum):
    UNVERIFIED = "UNVERIFIED"


class AccessibilityEvidenceReviewState(StrEnum):
    HUMAN_REVIEW_REQUIRED = "HUMAN_REVIEW_REQUIRED"


class SyntheticAccessibilityArea(StrEnum):
    KEYBOARD_AND_FOCUS = "KEYBOARD_AND_FOCUS"
    SEMANTICS_AND_ANNOUNCEMENTS = "SEMANTICS_AND_ANNOUNCEMENTS"
    CONTRAST_AND_DISPLAY = "CONTRAST_AND_DISPLAY"
    LANGUAGE = "LANGUAGE"
    URGENT_HELP = "URGENT_HELP"
    PWA_AND_OFFLINE = "PWA_AND_OFFLINE"
    KIOSK_AND_SHARED_DEVICE = "KIOSK_AND_SHARED_DEVICE"
    STAFF_SHELLS = "STAFF_SHELLS"


class SyntheticAccessibilityObservationState(StrEnum):
    METADATA_RECORDED = "METADATA_RECORDED"


class AccessibilityEvidenceDisposition(StrEnum):
    EVIDENCE_CONSISTENT = "EVIDENCE_CONSISTENT"
    ABSTAINED = "ABSTAINED"


class AccessibilityEvidenceReason(StrEnum):
    EXACT_SYNTHETIC_METADATA = "EXACT_SYNTHETIC_METADATA"
    SCOPE_MISMATCH = "SCOPE_MISMATCH"


def _error(code: AccessibilityEvidenceContractCode) -> AccessibilityEvidenceContractError:
    return AccessibilityEvidenceContractError(code)


def _strict_enum(value: object, expected: type[StrEnum]) -> None:
    if type(value) is not expected:
        raise _error(AccessibilityEvidenceContractCode.INVALID_TYPE)


def _machine_string(value: object, pattern: re.Pattern[str]) -> str:
    if type(value) is not str:
        raise _error(AccessibilityEvidenceContractCode.INVALID_TYPE)
    if pattern.fullmatch(value) is None:
        raise _error(AccessibilityEvidenceContractCode.INVALID_VALUE)
    return value


def _utc(value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise _error(AccessibilityEvidenceContractCode.INVALID_TYPE)
    return value.astimezone(UTC)


def _contract_version(value: object) -> None:
    if type(value) is not str or value != SYNTHETIC_ACCESSIBILITY_EVIDENCE_CONTRACT_VERSION:
        raise _error(AccessibilityEvidenceContractCode.INVALID_VALUE)


def _labels(
    authority: object,
    classification: object,
    verification: object,
    review_state: object,
) -> None:
    if authority is not AccessibilityEvidenceAuthority.ENGINEERING_ONLY:
        raise _error(AccessibilityEvidenceContractCode.INVALID_VALUE)
    if classification is not AccessibilityEvidenceClassification.ENGINEERING_SYNTHETIC:
        raise _error(AccessibilityEvidenceContractCode.INVALID_VALUE)
    if verification is not AccessibilityEvidenceVerification.UNVERIFIED:
        raise _error(AccessibilityEvidenceContractCode.INVALID_VALUE)
    if review_state is not AccessibilityEvidenceReviewState.HUMAN_REVIEW_REQUIRED:
        raise _error(AccessibilityEvidenceContractCode.INVALID_VALUE)


def _canonical_hash(payload: object) -> str:
    encoded = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticAccessibilityDefinition:
    area: SyntheticAccessibilityArea
    definition_version: str
    build_sha: str = field(repr=False)
    config_hash: str = field(repr=False)
    source_evidence_hash: str = field(repr=False)
    checklist_hash: str = field(repr=False)
    created_at: datetime
    authority: AccessibilityEvidenceAuthority = AccessibilityEvidenceAuthority.ENGINEERING_ONLY
    classification: AccessibilityEvidenceClassification = (
        AccessibilityEvidenceClassification.ENGINEERING_SYNTHETIC
    )
    verification: AccessibilityEvidenceVerification = AccessibilityEvidenceVerification.UNVERIFIED
    review_state: AccessibilityEvidenceReviewState = (
        AccessibilityEvidenceReviewState.HUMAN_REVIEW_REQUIRED
    )
    contract_version: str = SYNTHETIC_ACCESSIBILITY_EVIDENCE_CONTRACT_VERSION
    _fingerprint: str = field(init=False, repr=False, compare=True)

    def __post_init__(self) -> None:
        _strict_enum(self.area, SyntheticAccessibilityArea)
        _machine_string(self.definition_version, _VERSION)
        _machine_string(self.build_sha, _GIT_SHA)
        _machine_string(self.config_hash, _SHA256)
        _machine_string(self.source_evidence_hash, _SHA256)
        _machine_string(self.checklist_hash, _SHA256)
        created_at = _utc(self.created_at)
        _labels(self.authority, self.classification, self.verification, self.review_state)
        _contract_version(self.contract_version)
        fingerprint = _canonical_hash(
            {
                "area": self.area.value,
                "build_sha": self.build_sha,
                "checklist_hash": self.checklist_hash,
                "config_hash": self.config_hash,
                "contract_version": self.contract_version,
                "created_at": created_at.isoformat(),
                "definition_version": self.definition_version,
                "review_state": self.review_state.value,
                "source_evidence_hash": self.source_evidence_hash,
            }
        )
        object.__setattr__(self, "created_at", created_at)
        object.__setattr__(self, "_fingerprint", fingerprint)

    @property
    def fingerprint(self) -> str:
        return self._fingerprint


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticAccessibilityObservation:
    observation_id: str
    area: SyntheticAccessibilityArea
    definition_fingerprint: str = field(repr=False)
    build_sha: str = field(repr=False)
    config_hash: str = field(repr=False)
    source_evidence_hash: str = field(repr=False)
    checklist_hash: str = field(repr=False)
    state: SyntheticAccessibilityObservationState
    captured_at: datetime
    authority: AccessibilityEvidenceAuthority = AccessibilityEvidenceAuthority.ENGINEERING_ONLY
    classification: AccessibilityEvidenceClassification = (
        AccessibilityEvidenceClassification.ENGINEERING_SYNTHETIC
    )
    verification: AccessibilityEvidenceVerification = AccessibilityEvidenceVerification.UNVERIFIED
    review_state: AccessibilityEvidenceReviewState = (
        AccessibilityEvidenceReviewState.HUMAN_REVIEW_REQUIRED
    )
    contract_version: str = SYNTHETIC_ACCESSIBILITY_EVIDENCE_CONTRACT_VERSION
    _fingerprint: str = field(init=False, repr=False, compare=True)

    def __post_init__(self) -> None:
        _machine_string(self.observation_id, _OBSERVATION_ID)
        _strict_enum(self.area, SyntheticAccessibilityArea)
        _machine_string(self.definition_fingerprint, _SHA256)
        _machine_string(self.build_sha, _GIT_SHA)
        _machine_string(self.config_hash, _SHA256)
        _machine_string(self.source_evidence_hash, _SHA256)
        _machine_string(self.checklist_hash, _SHA256)
        _strict_enum(self.state, SyntheticAccessibilityObservationState)
        captured_at = _utc(self.captured_at)
        _labels(self.authority, self.classification, self.verification, self.review_state)
        _contract_version(self.contract_version)
        fingerprint = _canonical_hash(
            {
                "area": self.area.value,
                "build_sha": self.build_sha,
                "captured_at": captured_at.isoformat(),
                "checklist_hash": self.checklist_hash,
                "config_hash": self.config_hash,
                "contract_version": self.contract_version,
                "definition_fingerprint": self.definition_fingerprint,
                "observation_id": self.observation_id,
                "review_state": self.review_state.value,
                "source_evidence_hash": self.source_evidence_hash,
                "state": self.state.value,
            }
        )
        object.__setattr__(self, "captured_at", captured_at)
        object.__setattr__(self, "_fingerprint", fingerprint)

    @property
    def fingerprint(self) -> str:
        return self._fingerprint


def snapshot_accessibility_definition(value: object) -> SyntheticAccessibilityDefinition:
    if type(value) is not SyntheticAccessibilityDefinition:
        raise _error(AccessibilityEvidenceContractCode.INVALID_TYPE)
    try:
        snapshot = SyntheticAccessibilityDefinition(
            area=value.area,
            definition_version=value.definition_version,
            build_sha=value.build_sha,
            config_hash=value.config_hash,
            source_evidence_hash=value.source_evidence_hash,
            checklist_hash=value.checklist_hash,
            created_at=value.created_at,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
            review_state=value.review_state,
            contract_version=value.contract_version,
        )
    except AccessibilityEvidenceContractError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(AccessibilityEvidenceContractCode.INVALID_TYPE) from None
    if snapshot.fingerprint != value.fingerprint:
        raise _error(AccessibilityEvidenceContractCode.SNAPSHOT_DRIFT)
    return snapshot


def snapshot_accessibility_observation(value: object) -> SyntheticAccessibilityObservation:
    if type(value) is not SyntheticAccessibilityObservation:
        raise _error(AccessibilityEvidenceContractCode.INVALID_TYPE)
    try:
        snapshot = SyntheticAccessibilityObservation(
            observation_id=value.observation_id,
            area=value.area,
            definition_fingerprint=value.definition_fingerprint,
            build_sha=value.build_sha,
            config_hash=value.config_hash,
            source_evidence_hash=value.source_evidence_hash,
            checklist_hash=value.checklist_hash,
            state=value.state,
            captured_at=value.captured_at,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
            review_state=value.review_state,
            contract_version=value.contract_version,
        )
    except AccessibilityEvidenceContractError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(AccessibilityEvidenceContractCode.INVALID_TYPE) from None
    if snapshot.fingerprint != value.fingerprint:
        raise _error(AccessibilityEvidenceContractCode.SNAPSHOT_DRIFT)
    return snapshot


def _observation_matches(
    definition: SyntheticAccessibilityDefinition,
    observation: SyntheticAccessibilityObservation,
) -> bool:
    return (
        observation.area is definition.area
        and observation.definition_fingerprint == definition.fingerprint
        and observation.build_sha == definition.build_sha
        and observation.config_hash == definition.config_hash
        and observation.source_evidence_hash == definition.source_evidence_hash
        and observation.checklist_hash == definition.checklist_hash
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticAccessibilityReceipt:
    definition: SyntheticAccessibilityDefinition = field(repr=False)
    observation: SyntheticAccessibilityObservation = field(repr=False)
    disposition: AccessibilityEvidenceDisposition
    reason: AccessibilityEvidenceReason
    evaluated_at: datetime
    authority: AccessibilityEvidenceAuthority = AccessibilityEvidenceAuthority.ENGINEERING_ONLY
    classification: AccessibilityEvidenceClassification = (
        AccessibilityEvidenceClassification.ENGINEERING_SYNTHETIC
    )
    verification: AccessibilityEvidenceVerification = AccessibilityEvidenceVerification.UNVERIFIED
    review_state: AccessibilityEvidenceReviewState = (
        AccessibilityEvidenceReviewState.HUMAN_REVIEW_REQUIRED
    )
    contract_version: str = SYNTHETIC_ACCESSIBILITY_EVIDENCE_CONTRACT_VERSION
    _fingerprint: str = field(init=False, repr=False, compare=True)

    def __post_init__(self) -> None:
        definition = snapshot_accessibility_definition(self.definition)
        observation = snapshot_accessibility_observation(self.observation)
        if observation.captured_at < definition.created_at:
            raise _error(AccessibilityEvidenceContractCode.INVALID_CHRONOLOGY)
        expected = (
            (
                AccessibilityEvidenceDisposition.EVIDENCE_CONSISTENT,
                AccessibilityEvidenceReason.EXACT_SYNTHETIC_METADATA,
            )
            if _observation_matches(definition, observation)
            else (
                AccessibilityEvidenceDisposition.ABSTAINED,
                AccessibilityEvidenceReason.SCOPE_MISMATCH,
            )
        )
        _strict_enum(self.disposition, AccessibilityEvidenceDisposition)
        _strict_enum(self.reason, AccessibilityEvidenceReason)
        if (self.disposition, self.reason) != expected:
            raise _error(AccessibilityEvidenceContractCode.INCONSISTENT_RECEIPT)
        evaluated_at = _utc(self.evaluated_at)
        if evaluated_at < observation.captured_at:
            raise _error(AccessibilityEvidenceContractCode.INVALID_CHRONOLOGY)
        _labels(self.authority, self.classification, self.verification, self.review_state)
        _contract_version(self.contract_version)
        fingerprint = _canonical_hash(
            {
                "contract_version": self.contract_version,
                "definition_fingerprint": definition.fingerprint,
                "disposition": self.disposition.value,
                "evaluated_at": evaluated_at.isoformat(),
                "observation_fingerprint": observation.fingerprint,
                "reason": self.reason.value,
                "review_state": self.review_state.value,
            }
        )
        object.__setattr__(self, "definition", definition)
        object.__setattr__(self, "observation", observation)
        object.__setattr__(self, "evaluated_at", evaluated_at)
        object.__setattr__(self, "_fingerprint", fingerprint)

    @property
    def fingerprint(self) -> str:
        return self._fingerprint


def snapshot_accessibility_receipt(value: object) -> SyntheticAccessibilityReceipt:
    if type(value) is not SyntheticAccessibilityReceipt:
        raise _error(AccessibilityEvidenceContractCode.INVALID_TYPE)
    try:
        snapshot = SyntheticAccessibilityReceipt(
            definition=value.definition,
            observation=value.observation,
            disposition=value.disposition,
            reason=value.reason,
            evaluated_at=value.evaluated_at,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
            review_state=value.review_state,
            contract_version=value.contract_version,
        )
    except AccessibilityEvidenceContractError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(AccessibilityEvidenceContractCode.INVALID_TYPE) from None
    if snapshot.fingerprint != value.fingerprint:
        raise _error(AccessibilityEvidenceContractCode.SNAPSHOT_DRIFT)
    return snapshot


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticAccessibilityManifest:
    manifest_id: str
    generated_at: datetime
    definitions: tuple[SyntheticAccessibilityDefinition, ...] = field(repr=False)
    authority: AccessibilityEvidenceAuthority = AccessibilityEvidenceAuthority.ENGINEERING_ONLY
    classification: AccessibilityEvidenceClassification = (
        AccessibilityEvidenceClassification.ENGINEERING_SYNTHETIC
    )
    verification: AccessibilityEvidenceVerification = AccessibilityEvidenceVerification.UNVERIFIED
    review_state: AccessibilityEvidenceReviewState = (
        AccessibilityEvidenceReviewState.HUMAN_REVIEW_REQUIRED
    )
    contract_version: str = SYNTHETIC_ACCESSIBILITY_EVIDENCE_CONTRACT_VERSION
    _fingerprint: str = field(init=False, repr=False, compare=True)

    def __post_init__(self) -> None:
        _machine_string(self.manifest_id, _MANIFEST_ID)
        generated_at = _utc(self.generated_at)
        if type(self.definitions) is not tuple:
            raise _error(AccessibilityEvidenceContractCode.INVALID_TYPE)
        if len(self.definitions) != len(SyntheticAccessibilityArea):
            raise _error(AccessibilityEvidenceContractCode.INCOMPLETE_INVENTORY)
        definitions = tuple(snapshot_accessibility_definition(item) for item in self.definitions)
        areas = tuple(item.area for item in definitions)
        if len(set(areas)) != len(areas):
            raise _error(AccessibilityEvidenceContractCode.DUPLICATE_AREA)
        if set(areas) != set(SyntheticAccessibilityArea):
            raise _error(AccessibilityEvidenceContractCode.INCOMPLETE_INVENTORY)
        if areas != tuple(sorted(areas, key=lambda item: item.value)):
            raise _error(AccessibilityEvidenceContractCode.INVALID_ORDER)
        if any(item.created_at > generated_at for item in definitions):
            raise _error(AccessibilityEvidenceContractCode.INVALID_CHRONOLOGY)
        _labels(self.authority, self.classification, self.verification, self.review_state)
        _contract_version(self.contract_version)
        fingerprint = _canonical_hash(
            {
                "contract_version": self.contract_version,
                "definition_fingerprints": [item.fingerprint for item in definitions],
                "generated_at": generated_at.isoformat(),
                "manifest_id": self.manifest_id,
                "review_state": self.review_state.value,
            }
        )
        object.__setattr__(self, "generated_at", generated_at)
        object.__setattr__(self, "definitions", definitions)
        object.__setattr__(self, "_fingerprint", fingerprint)

    @property
    def fingerprint(self) -> str:
        return self._fingerprint


def snapshot_accessibility_manifest(value: object) -> SyntheticAccessibilityManifest:
    if type(value) is not SyntheticAccessibilityManifest:
        raise _error(AccessibilityEvidenceContractCode.INVALID_TYPE)
    try:
        snapshot = SyntheticAccessibilityManifest(
            manifest_id=value.manifest_id,
            generated_at=value.generated_at,
            definitions=value.definitions,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
            review_state=value.review_state,
            contract_version=value.contract_version,
        )
    except AccessibilityEvidenceContractError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(AccessibilityEvidenceContractCode.INVALID_TYPE) from None
    if snapshot.fingerprint != value.fingerprint:
        raise _error(AccessibilityEvidenceContractCode.SNAPSHOT_DRIFT)
    return snapshot


def _check_environment(environment: object) -> None:
    if type(environment) is not Environment:
        raise _error(AccessibilityEvidenceContractCode.INVALID_TYPE)
    if environment in _PROTECTED_ENVIRONMENTS:
        raise _error(AccessibilityEvidenceContractCode.PROTECTED_ENVIRONMENT)


def build_synthetic_accessibility_manifest(
    definitions: tuple[SyntheticAccessibilityDefinition, ...],
    *,
    manifest_id: str,
    generated_at: datetime,
    environment: Environment,
) -> SyntheticAccessibilityManifest:
    """Build the canonical metadata catalog without performing an audit."""

    _check_environment(environment)
    if type(definitions) is not tuple:
        raise _error(AccessibilityEvidenceContractCode.INVALID_TYPE)
    if len(definitions) != len(SyntheticAccessibilityArea):
        raise _error(AccessibilityEvidenceContractCode.INCOMPLETE_INVENTORY)
    safe_definitions = tuple(
        sorted(
            (snapshot_accessibility_definition(item) for item in definitions),
            key=lambda item: item.area.value,
        )
    )
    return SyntheticAccessibilityManifest(
        manifest_id=manifest_id,
        generated_at=generated_at,
        definitions=safe_definitions,
    )


def evaluate_synthetic_accessibility_evidence(
    definition: SyntheticAccessibilityDefinition,
    observation: SyntheticAccessibilityObservation,
    *,
    evaluated_at: datetime,
    environment: Environment,
) -> SyntheticAccessibilityReceipt:
    """Check metadata consistency; never perform or pass an accessibility audit."""

    _check_environment(environment)
    safe_definition = snapshot_accessibility_definition(definition)
    safe_observation = snapshot_accessibility_observation(observation)
    if _observation_matches(safe_definition, safe_observation):
        disposition = AccessibilityEvidenceDisposition.EVIDENCE_CONSISTENT
        reason = AccessibilityEvidenceReason.EXACT_SYNTHETIC_METADATA
    else:
        disposition = AccessibilityEvidenceDisposition.ABSTAINED
        reason = AccessibilityEvidenceReason.SCOPE_MISMATCH
    return SyntheticAccessibilityReceipt(
        definition=safe_definition,
        observation=safe_observation,
        disposition=disposition,
        reason=reason,
        evaluated_at=evaluated_at,
    )


__all__ = [
    "SYNTHETIC_ACCESSIBILITY_EVIDENCE_CONTRACT_VERSION",
    "AccessibilityEvidenceAuthority",
    "AccessibilityEvidenceClassification",
    "AccessibilityEvidenceContractCode",
    "AccessibilityEvidenceContractError",
    "AccessibilityEvidenceDisposition",
    "AccessibilityEvidenceReason",
    "AccessibilityEvidenceReviewState",
    "AccessibilityEvidenceVerification",
    "SyntheticAccessibilityArea",
    "SyntheticAccessibilityDefinition",
    "SyntheticAccessibilityManifest",
    "SyntheticAccessibilityObservation",
    "SyntheticAccessibilityObservationState",
    "SyntheticAccessibilityReceipt",
    "build_synthetic_accessibility_manifest",
    "evaluate_synthetic_accessibility_evidence",
    "snapshot_accessibility_definition",
    "snapshot_accessibility_manifest",
    "snapshot_accessibility_observation",
    "snapshot_accessibility_receipt",
]
