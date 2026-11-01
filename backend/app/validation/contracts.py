"""Strict contracts for detached engineering-synthetic P23 journey evidence."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256
from typing import Final

SYNTHETIC_JOURNEY_EVIDENCE_CONTRACT_VERSION: Final = "synthetic-journey-evidence.v1"

_VERSION = re.compile(r"^engineering\.v[1-9][0-9]{0,5}$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_GIT_SHA = re.compile(r"^[a-f0-9]{40}$")
_OBSERVATION_ID = re.compile(r"^syn_journey_observation_(?:alpha|beta|gamma|delta)$")
_MANIFEST_ID = re.compile(r"^syn_journey_manifest_(?:alpha|beta|gamma|delta)$")


class JourneyEvidenceContractCode(StrEnum):
    INVALID_TYPE = "INVALID_TYPE"
    INVALID_VALUE = "INVALID_VALUE"
    INVALID_READINESS = "INVALID_READINESS"
    INVALID_CHRONOLOGY = "INVALID_CHRONOLOGY"
    INCONSISTENT_RECEIPT = "INCONSISTENT_RECEIPT"
    INCOMPLETE_INVENTORY = "INCOMPLETE_INVENTORY"
    DUPLICATE_JOURNEY = "DUPLICATE_JOURNEY"
    INVALID_ORDER = "INVALID_ORDER"
    SNAPSHOT_DRIFT = "SNAPSHOT_DRIFT"
    PROTECTED_ENVIRONMENT = "PROTECTED_ENVIRONMENT"


class JourneyEvidenceContractError(ValueError):
    """Stable content-free P23 engineering evidence failure."""

    def __init__(self, code: JourneyEvidenceContractCode) -> None:
        self.code = code
        super().__init__(code.value)


class JourneyEvidenceAuthority(StrEnum):
    ENGINEERING_ONLY = "ENGINEERING_ONLY"


class JourneyEvidenceClassification(StrEnum):
    ENGINEERING_SYNTHETIC = "ENGINEERING_SYNTHETIC"


class JourneyEvidenceVerification(StrEnum):
    UNVERIFIED = "UNVERIFIED"


class SyntheticJourneyId(StrEnum):
    STRUCTURED_CLINICAL_INTAKE = "STRUCTURED_CLINICAL_INTAKE"
    CONVERSATIONAL_INTAKE = "CONVERSATIONAL_INTAKE"
    DOCUMENT_UPLOAD_EXTRACTION = "DOCUMENT_UPLOAD_EXTRACTION"
    RED_FLAG_URGENT_ROUTE = "RED_FLAG_URGENT_ROUTE"
    SELF_CARE_ELIGIBLE = "SELF_CARE_ELIGIBLE"
    SELF_CARE_BLOCKED = "SELF_CARE_BLOCKED"
    DOCTOR_SEARCH = "DOCTOR_SEARCH"
    REFERRAL_LIFECYCLE = "REFERRAL_LIFECYCLE"
    CLINICIAN_CONFIRMATION = "CLINICIAN_CONFIRMATION"
    MENTAL_HEALTH_ROUTE_A = "MENTAL_HEALTH_ROUTE_A"
    MENTAL_HEALTH_ROUTE_B_REFERRAL = "MENTAL_HEALTH_ROUTE_B_REFERRAL"
    MENTAL_HEALTH_ROUTE_C_CRISIS_FALLBACK = "MENTAL_HEALTH_ROUTE_C_CRISIS_FALLBACK"
    LLM_OUTAGE = "LLM_OUTAGE"
    OCR_OUTAGE = "OCR_OUTAGE"
    SPEECH_FALLBACK = "SPEECH_FALLBACK"
    FHIR_EXPORT = "FHIR_EXPORT"
    CLASSICAL_MODEL_RESEARCH_RUN = "CLASSICAL_MODEL_RESEARCH_RUN"
    QML_RESEARCH_RUN = "QML_RESEARCH_RUN"


class SyntheticJourneyReadiness(StrEnum):
    BOUNDED_P7_TECHNICAL_ONLY = "BOUNDED_P7_TECHNICAL_ONLY"
    BLOCKED_UNAPPROVED = "BLOCKED_UNAPPROVED"


class SyntheticObservationState(StrEnum):
    METADATA_RECORDED = "METADATA_RECORDED"


class SyntheticEvidenceDisposition(StrEnum):
    EVIDENCE_CONSISTENT = "EVIDENCE_CONSISTENT"
    ABSTAINED = "ABSTAINED"


class SyntheticEvidenceReason(StrEnum):
    EXACT_SYNTHETIC_METADATA = "EXACT_SYNTHETIC_METADATA"
    JOURNEY_BLOCKED = "JOURNEY_BLOCKED"
    SCOPE_MISMATCH = "SCOPE_MISMATCH"


def _error(code: JourneyEvidenceContractCode) -> JourneyEvidenceContractError:
    return JourneyEvidenceContractError(code)


def _strict_enum(value: object, expected: type[StrEnum]) -> None:
    if type(value) is not expected:
        raise _error(JourneyEvidenceContractCode.INVALID_TYPE)


def _machine_string(value: object, pattern: re.Pattern[str]) -> str:
    if type(value) is not str:
        raise _error(JourneyEvidenceContractCode.INVALID_TYPE)
    if pattern.fullmatch(value) is None:
        raise _error(JourneyEvidenceContractCode.INVALID_VALUE)
    return value


def _utc(value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise _error(JourneyEvidenceContractCode.INVALID_TYPE)
    return value.astimezone(UTC)


def _labels(
    authority: object,
    classification: object,
    verification: object,
) -> None:
    if authority is not JourneyEvidenceAuthority.ENGINEERING_ONLY:
        raise _error(JourneyEvidenceContractCode.INVALID_VALUE)
    if classification is not JourneyEvidenceClassification.ENGINEERING_SYNTHETIC:
        raise _error(JourneyEvidenceContractCode.INVALID_VALUE)
    if verification is not JourneyEvidenceVerification.UNVERIFIED:
        raise _error(JourneyEvidenceContractCode.INVALID_VALUE)


def _contract_version(value: object) -> None:
    if type(value) is not str or value != SYNTHETIC_JOURNEY_EVIDENCE_CONTRACT_VERSION:
        raise _error(JourneyEvidenceContractCode.INVALID_VALUE)


def _canonical_hash(payload: object) -> str:
    return sha256(
        json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticJourneyDefinition:
    journey_id: SyntheticJourneyId
    definition_version: str
    fixture_hash: str = field(repr=False)
    oracle_hash: str = field(repr=False)
    readiness: SyntheticJourneyReadiness
    created_at: datetime
    authority: JourneyEvidenceAuthority = JourneyEvidenceAuthority.ENGINEERING_ONLY
    classification: JourneyEvidenceClassification = (
        JourneyEvidenceClassification.ENGINEERING_SYNTHETIC
    )
    verification: JourneyEvidenceVerification = JourneyEvidenceVerification.UNVERIFIED
    contract_version: str = SYNTHETIC_JOURNEY_EVIDENCE_CONTRACT_VERSION
    _fingerprint: str = field(init=False, repr=False, compare=True)

    def __post_init__(self) -> None:
        _strict_enum(self.journey_id, SyntheticJourneyId)
        _machine_string(self.definition_version, _VERSION)
        _machine_string(self.fixture_hash, _SHA256)
        _machine_string(self.oracle_hash, _SHA256)
        _strict_enum(self.readiness, SyntheticJourneyReadiness)
        if (
            self.readiness is SyntheticJourneyReadiness.BOUNDED_P7_TECHNICAL_ONLY
            and self.journey_id is not SyntheticJourneyId.STRUCTURED_CLINICAL_INTAKE
        ):
            raise _error(JourneyEvidenceContractCode.INVALID_READINESS)
        created_at = _utc(self.created_at)
        _labels(self.authority, self.classification, self.verification)
        _contract_version(self.contract_version)
        fingerprint = _canonical_hash(
            {
                "contract_version": self.contract_version,
                "created_at": created_at.isoformat(),
                "definition_version": self.definition_version,
                "fixture_hash": self.fixture_hash,
                "journey_id": self.journey_id.value,
                "oracle_hash": self.oracle_hash,
                "readiness": self.readiness.value,
            }
        )
        object.__setattr__(self, "created_at", created_at)
        object.__setattr__(self, "_fingerprint", fingerprint)

    @property
    def fingerprint(self) -> str:
        return self._fingerprint


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticJourneyObservation:
    observation_id: str
    journey_id: SyntheticJourneyId
    definition_fingerprint: str = field(repr=False)
    build_sha: str = field(repr=False)
    config_hash: str = field(repr=False)
    fixture_hash: str = field(repr=False)
    oracle_hash: str = field(repr=False)
    state: SyntheticObservationState
    captured_at: datetime
    authority: JourneyEvidenceAuthority = JourneyEvidenceAuthority.ENGINEERING_ONLY
    classification: JourneyEvidenceClassification = (
        JourneyEvidenceClassification.ENGINEERING_SYNTHETIC
    )
    verification: JourneyEvidenceVerification = JourneyEvidenceVerification.UNVERIFIED
    contract_version: str = SYNTHETIC_JOURNEY_EVIDENCE_CONTRACT_VERSION
    _fingerprint: str = field(init=False, repr=False, compare=True)

    def __post_init__(self) -> None:
        _machine_string(self.observation_id, _OBSERVATION_ID)
        _strict_enum(self.journey_id, SyntheticJourneyId)
        _machine_string(self.definition_fingerprint, _SHA256)
        _machine_string(self.build_sha, _GIT_SHA)
        _machine_string(self.config_hash, _SHA256)
        _machine_string(self.fixture_hash, _SHA256)
        _machine_string(self.oracle_hash, _SHA256)
        _strict_enum(self.state, SyntheticObservationState)
        captured_at = _utc(self.captured_at)
        _labels(self.authority, self.classification, self.verification)
        _contract_version(self.contract_version)
        fingerprint = _canonical_hash(
            {
                "build_sha": self.build_sha,
                "captured_at": captured_at.isoformat(),
                "config_hash": self.config_hash,
                "contract_version": self.contract_version,
                "definition_fingerprint": self.definition_fingerprint,
                "fixture_hash": self.fixture_hash,
                "journey_id": self.journey_id.value,
                "observation_id": self.observation_id,
                "oracle_hash": self.oracle_hash,
                "state": self.state.value,
            }
        )
        object.__setattr__(self, "captured_at", captured_at)
        object.__setattr__(self, "_fingerprint", fingerprint)

    @property
    def fingerprint(self) -> str:
        return self._fingerprint


def snapshot_journey_definition(value: object) -> SyntheticJourneyDefinition:
    if type(value) is not SyntheticJourneyDefinition:
        raise _error(JourneyEvidenceContractCode.INVALID_TYPE)
    try:
        snapshot = SyntheticJourneyDefinition(
            journey_id=value.journey_id,
            definition_version=value.definition_version,
            fixture_hash=value.fixture_hash,
            oracle_hash=value.oracle_hash,
            readiness=value.readiness,
            created_at=value.created_at,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
            contract_version=value.contract_version,
        )
    except JourneyEvidenceContractError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(JourneyEvidenceContractCode.INVALID_TYPE) from None
    if snapshot.fingerprint != value.fingerprint:
        raise _error(JourneyEvidenceContractCode.SNAPSHOT_DRIFT)
    return snapshot


def snapshot_journey_observation(value: object) -> SyntheticJourneyObservation:
    if type(value) is not SyntheticJourneyObservation:
        raise _error(JourneyEvidenceContractCode.INVALID_TYPE)
    try:
        snapshot = SyntheticJourneyObservation(
            observation_id=value.observation_id,
            journey_id=value.journey_id,
            definition_fingerprint=value.definition_fingerprint,
            build_sha=value.build_sha,
            config_hash=value.config_hash,
            fixture_hash=value.fixture_hash,
            oracle_hash=value.oracle_hash,
            state=value.state,
            captured_at=value.captured_at,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
            contract_version=value.contract_version,
        )
    except JourneyEvidenceContractError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(JourneyEvidenceContractCode.INVALID_TYPE) from None
    if snapshot.fingerprint != value.fingerprint:
        raise _error(JourneyEvidenceContractCode.SNAPSHOT_DRIFT)
    return snapshot


def _observation_matches(
    definition: SyntheticJourneyDefinition,
    observation: SyntheticJourneyObservation,
) -> bool:
    return (
        observation.journey_id is definition.journey_id
        and observation.definition_fingerprint == definition.fingerprint
        and observation.fixture_hash == definition.fixture_hash
        and observation.oracle_hash == definition.oracle_hash
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticJourneyEvidenceReceipt:
    definition: SyntheticJourneyDefinition = field(repr=False)
    observation: SyntheticJourneyObservation | None = field(repr=False)
    disposition: SyntheticEvidenceDisposition
    reason: SyntheticEvidenceReason
    evaluated_at: datetime
    authority: JourneyEvidenceAuthority = JourneyEvidenceAuthority.ENGINEERING_ONLY
    classification: JourneyEvidenceClassification = (
        JourneyEvidenceClassification.ENGINEERING_SYNTHETIC
    )
    verification: JourneyEvidenceVerification = JourneyEvidenceVerification.UNVERIFIED
    contract_version: str = SYNTHETIC_JOURNEY_EVIDENCE_CONTRACT_VERSION
    _fingerprint: str = field(init=False, repr=False, compare=True)

    def __post_init__(self) -> None:
        definition = snapshot_journey_definition(self.definition)
        observation: SyntheticJourneyObservation | None = None
        if definition.readiness is SyntheticJourneyReadiness.BLOCKED_UNAPPROVED:
            expected = (
                SyntheticEvidenceDisposition.ABSTAINED,
                SyntheticEvidenceReason.JOURNEY_BLOCKED,
            )
            if self.observation is not None:
                raise _error(JourneyEvidenceContractCode.INCONSISTENT_RECEIPT)
        else:
            observation = snapshot_journey_observation(self.observation)
            if observation.captured_at < definition.created_at:
                raise _error(JourneyEvidenceContractCode.INVALID_CHRONOLOGY)
            expected = (
                (
                    SyntheticEvidenceDisposition.EVIDENCE_CONSISTENT,
                    SyntheticEvidenceReason.EXACT_SYNTHETIC_METADATA,
                )
                if _observation_matches(definition, observation)
                else (
                    SyntheticEvidenceDisposition.ABSTAINED,
                    SyntheticEvidenceReason.SCOPE_MISMATCH,
                )
            )
        _strict_enum(self.disposition, SyntheticEvidenceDisposition)
        _strict_enum(self.reason, SyntheticEvidenceReason)
        if (self.disposition, self.reason) != expected:
            raise _error(JourneyEvidenceContractCode.INCONSISTENT_RECEIPT)
        evaluated_at = _utc(self.evaluated_at)
        latest_input_at = observation.captured_at if observation else definition.created_at
        if evaluated_at < latest_input_at:
            raise _error(JourneyEvidenceContractCode.INVALID_CHRONOLOGY)
        _labels(self.authority, self.classification, self.verification)
        _contract_version(self.contract_version)
        fingerprint = _canonical_hash(
            {
                "contract_version": self.contract_version,
                "definition_fingerprint": definition.fingerprint,
                "disposition": self.disposition.value,
                "evaluated_at": evaluated_at.isoformat(),
                "observation_fingerprint": observation.fingerprint if observation else None,
                "reason": self.reason.value,
            }
        )
        object.__setattr__(self, "definition", definition)
        object.__setattr__(self, "observation", observation)
        object.__setattr__(self, "evaluated_at", evaluated_at)
        object.__setattr__(self, "_fingerprint", fingerprint)

    @property
    def fingerprint(self) -> str:
        return self._fingerprint


def snapshot_journey_evidence_receipt(value: object) -> SyntheticJourneyEvidenceReceipt:
    if type(value) is not SyntheticJourneyEvidenceReceipt:
        raise _error(JourneyEvidenceContractCode.INVALID_TYPE)
    try:
        snapshot = SyntheticJourneyEvidenceReceipt(
            definition=value.definition,
            observation=value.observation,
            disposition=value.disposition,
            reason=value.reason,
            evaluated_at=value.evaluated_at,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
            contract_version=value.contract_version,
        )
    except JourneyEvidenceContractError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(JourneyEvidenceContractCode.INVALID_TYPE) from None
    if snapshot.fingerprint != value.fingerprint:
        raise _error(JourneyEvidenceContractCode.SNAPSHOT_DRIFT)
    return snapshot


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticJourneyManifest:
    manifest_id: str
    generated_at: datetime
    definitions: tuple[SyntheticJourneyDefinition, ...] = field(repr=False)
    authority: JourneyEvidenceAuthority = JourneyEvidenceAuthority.ENGINEERING_ONLY
    classification: JourneyEvidenceClassification = (
        JourneyEvidenceClassification.ENGINEERING_SYNTHETIC
    )
    verification: JourneyEvidenceVerification = JourneyEvidenceVerification.UNVERIFIED
    contract_version: str = SYNTHETIC_JOURNEY_EVIDENCE_CONTRACT_VERSION
    _fingerprint: str = field(init=False, repr=False, compare=True)

    def __post_init__(self) -> None:
        _machine_string(self.manifest_id, _MANIFEST_ID)
        generated_at = _utc(self.generated_at)
        if type(self.definitions) is not tuple:
            raise _error(JourneyEvidenceContractCode.INVALID_TYPE)
        if len(self.definitions) != len(SyntheticJourneyId):
            raise _error(JourneyEvidenceContractCode.INCOMPLETE_INVENTORY)
        definitions = tuple(snapshot_journey_definition(item) for item in self.definitions)
        journey_ids = tuple(item.journey_id for item in definitions)
        if len(set(journey_ids)) != len(journey_ids):
            raise _error(JourneyEvidenceContractCode.DUPLICATE_JOURNEY)
        if set(journey_ids) != set(SyntheticJourneyId):
            raise _error(JourneyEvidenceContractCode.INCOMPLETE_INVENTORY)
        if journey_ids != tuple(sorted(journey_ids, key=lambda value: value.value)):
            raise _error(JourneyEvidenceContractCode.INVALID_ORDER)
        for item in definitions:
            expected_readiness = (
                SyntheticJourneyReadiness.BOUNDED_P7_TECHNICAL_ONLY
                if item.journey_id is SyntheticJourneyId.STRUCTURED_CLINICAL_INTAKE
                else SyntheticJourneyReadiness.BLOCKED_UNAPPROVED
            )
            if item.readiness is not expected_readiness:
                raise _error(JourneyEvidenceContractCode.INVALID_READINESS)
            if item.created_at > generated_at:
                raise _error(JourneyEvidenceContractCode.INVALID_CHRONOLOGY)
        _labels(self.authority, self.classification, self.verification)
        _contract_version(self.contract_version)
        fingerprint = _canonical_hash(
            {
                "contract_version": self.contract_version,
                "definition_fingerprints": [item.fingerprint for item in definitions],
                "generated_at": generated_at.isoformat(),
                "manifest_id": self.manifest_id,
            }
        )
        object.__setattr__(self, "generated_at", generated_at)
        object.__setattr__(self, "definitions", definitions)
        object.__setattr__(self, "_fingerprint", fingerprint)

    @property
    def fingerprint(self) -> str:
        return self._fingerprint


def snapshot_journey_manifest(value: object) -> SyntheticJourneyManifest:
    if type(value) is not SyntheticJourneyManifest:
        raise _error(JourneyEvidenceContractCode.INVALID_TYPE)
    try:
        snapshot = SyntheticJourneyManifest(
            manifest_id=value.manifest_id,
            generated_at=value.generated_at,
            definitions=value.definitions,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
            contract_version=value.contract_version,
        )
    except JourneyEvidenceContractError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(JourneyEvidenceContractCode.INVALID_TYPE) from None
    if snapshot.fingerprint != value.fingerprint:
        raise _error(JourneyEvidenceContractCode.SNAPSHOT_DRIFT)
    return snapshot


__all__ = [
    "SYNTHETIC_JOURNEY_EVIDENCE_CONTRACT_VERSION",
    "JourneyEvidenceAuthority",
    "JourneyEvidenceClassification",
    "JourneyEvidenceContractCode",
    "JourneyEvidenceContractError",
    "JourneyEvidenceVerification",
    "SyntheticEvidenceDisposition",
    "SyntheticEvidenceReason",
    "SyntheticJourneyDefinition",
    "SyntheticJourneyEvidenceReceipt",
    "SyntheticJourneyId",
    "SyntheticJourneyManifest",
    "SyntheticJourneyObservation",
    "SyntheticJourneyReadiness",
    "SyntheticObservationState",
    "snapshot_journey_definition",
    "snapshot_journey_evidence_receipt",
    "snapshot_journey_manifest",
    "snapshot_journey_observation",
]
