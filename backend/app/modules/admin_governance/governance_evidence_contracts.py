"""Content-free contracts for detached synthetic governance evidence."""

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

SYNTHETIC_GOVERNANCE_EVIDENCE_CONTRACT_VERSION: Final = "synthetic-governance-evidence.v1"
MAX_SYNTHETIC_GOVERNANCE_AUDIT_RECEIPTS: Final = 16

_PROPOSAL_ID = re.compile(r"^syn_governance_proposal_(?:alpha|beta|gamma|delta)$")
_CHECK_ID = re.compile(r"^syn_governance_check_(?:alpha|beta|gamma|delta)$")
_ACTOR_ID = re.compile(r"^syn_governance_actor_(?:alpha|beta|gamma|delta)$")
_OBJECT_ID = re.compile(r"^syn_governance_object_(?:alpha|beta|gamma|delta)$")
_INSTITUTION_ID = re.compile(r"^syn_governance_institution_(?:alpha|beta|gamma|delta)$")
_SOURCE_ID = re.compile(r"^syn_governance_source_(?:alpha|beta|gamma|delta)$")
_PURPOSE_ID = re.compile(r"^syn_governance_purpose_(?:alpha|beta|gamma|delta)$")
_SNAPSHOT_ID = re.compile(r"^syn_governance_audit_(?:alpha|beta|gamma|delta)$")
_VERSION = re.compile(r"^engineering\.v[1-9][0-9]{0,5}$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")


class GovernanceEvidenceContractCode(StrEnum):
    INVALID_TYPE = "INVALID_TYPE"
    INVALID_VALUE = "INVALID_VALUE"
    INVALID_CHRONOLOGY = "INVALID_CHRONOLOGY"
    INCONSISTENT_RECEIPT = "INCONSISTENT_RECEIPT"
    LIMIT_EXCEEDED = "LIMIT_EXCEEDED"
    DUPLICATE_RECEIPT = "DUPLICATE_RECEIPT"
    AMBIGUOUS_RECEIPT = "AMBIGUOUS_RECEIPT"
    SNAPSHOT_DRIFT = "SNAPSHOT_DRIFT"
    PROTECTED_ENVIRONMENT = "PROTECTED_ENVIRONMENT"


class GovernanceEvidenceContractError(ValueError):
    """Stable content-free synthetic governance evidence failure."""

    def __init__(self, code: GovernanceEvidenceContractCode) -> None:
        self.code = code
        super().__init__(code.value)


class SyntheticGovernanceChangeKind(StrEnum):
    SYNTHETIC_CHANGE_ALPHA = "SYNTHETIC_CHANGE_ALPHA"
    SYNTHETIC_CHANGE_BETA = "SYNTHETIC_CHANGE_BETA"


class SyntheticIndependenceDisposition(StrEnum):
    INDEPENDENCE_CONFIRMED = "INDEPENDENCE_CONFIRMED"
    ABSTAINED = "ABSTAINED"


class SyntheticIndependenceReason(StrEnum):
    DISTINCT_ACTOR_EXACT_REVISION = "DISTINCT_ACTOR_EXACT_REVISION"
    SELF_REVIEW = "SELF_REVIEW"
    SCOPE_MISMATCH = "SCOPE_MISMATCH"


def _error(code: GovernanceEvidenceContractCode) -> GovernanceEvidenceContractError:
    return GovernanceEvidenceContractError(code)


def _strict_enum(value: object, expected: type[StrEnum]) -> None:
    if type(value) is not expected:
        raise _error(GovernanceEvidenceContractCode.INVALID_TYPE)


def _machine_string(value: object, pattern: re.Pattern[str]) -> str:
    if type(value) is not str:
        raise _error(GovernanceEvidenceContractCode.INVALID_TYPE)
    if pattern.fullmatch(value) is None:
        raise _error(GovernanceEvidenceContractCode.INVALID_VALUE)
    return value


def _utc(value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise _error(GovernanceEvidenceContractCode.INVALID_TYPE)
    return value.astimezone(UTC)


def _labels(authority: object, classification: object, verification: object) -> None:
    if authority is not AdminAuthority.ENGINEERING_ONLY:
        raise _error(GovernanceEvidenceContractCode.INVALID_VALUE)
    if classification is not AdminClassification.ENGINEERING_SYNTHETIC:
        raise _error(GovernanceEvidenceContractCode.INVALID_VALUE)
    if verification is not AdminVerification.UNVERIFIED:
        raise _error(GovernanceEvidenceContractCode.INVALID_VALUE)


def _canonical_hash(payload: object) -> str:
    return sha256(
        json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticGovernanceProposal:
    proposal_id: str
    maker_actor_id: str
    object_id: str
    object_version: str
    object_hash: str
    institution_id: str
    source_id: str
    purpose_id: str
    change_kind: SyntheticGovernanceChangeKind
    created_at: datetime
    authority: AdminAuthority = AdminAuthority.ENGINEERING_ONLY
    classification: AdminClassification = AdminClassification.ENGINEERING_SYNTHETIC
    verification: AdminVerification = AdminVerification.UNVERIFIED
    _fingerprint: str = field(init=False, repr=False, compare=True)

    def __post_init__(self) -> None:
        _machine_string(self.proposal_id, _PROPOSAL_ID)
        _machine_string(self.maker_actor_id, _ACTOR_ID)
        _machine_string(self.object_id, _OBJECT_ID)
        _machine_string(self.object_version, _VERSION)
        _machine_string(self.object_hash, _SHA256)
        _machine_string(self.institution_id, _INSTITUTION_ID)
        _machine_string(self.source_id, _SOURCE_ID)
        _machine_string(self.purpose_id, _PURPOSE_ID)
        _strict_enum(self.change_kind, SyntheticGovernanceChangeKind)
        created_at = _utc(self.created_at)
        _labels(self.authority, self.classification, self.verification)
        fingerprint = _canonical_hash(
            {
                "change_kind": self.change_kind.value,
                "contract_version": SYNTHETIC_GOVERNANCE_EVIDENCE_CONTRACT_VERSION,
                "created_at": created_at.isoformat(),
                "institution_id": self.institution_id,
                "maker_actor_id": self.maker_actor_id,
                "object_hash": self.object_hash,
                "object_id": self.object_id,
                "object_version": self.object_version,
                "proposal_id": self.proposal_id,
                "purpose_id": self.purpose_id,
                "source_id": self.source_id,
            }
        )
        object.__setattr__(self, "created_at", created_at)
        object.__setattr__(self, "_fingerprint", fingerprint)

    @property
    def fingerprint(self) -> str:
        return self._fingerprint


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticCheckerSubmission:
    check_id: str
    checker_actor_id: str
    proposal_id: str
    proposal_fingerprint: str
    object_id: str
    object_version: str
    object_hash: str
    institution_id: str
    source_id: str
    purpose_id: str
    submitted_at: datetime
    authority: AdminAuthority = AdminAuthority.ENGINEERING_ONLY
    classification: AdminClassification = AdminClassification.ENGINEERING_SYNTHETIC
    verification: AdminVerification = AdminVerification.UNVERIFIED
    _fingerprint: str = field(init=False, repr=False, compare=True)

    def __post_init__(self) -> None:
        _machine_string(self.check_id, _CHECK_ID)
        _machine_string(self.checker_actor_id, _ACTOR_ID)
        _machine_string(self.proposal_id, _PROPOSAL_ID)
        _machine_string(self.proposal_fingerprint, _SHA256)
        _machine_string(self.object_id, _OBJECT_ID)
        _machine_string(self.object_version, _VERSION)
        _machine_string(self.object_hash, _SHA256)
        _machine_string(self.institution_id, _INSTITUTION_ID)
        _machine_string(self.source_id, _SOURCE_ID)
        _machine_string(self.purpose_id, _PURPOSE_ID)
        submitted_at = _utc(self.submitted_at)
        _labels(self.authority, self.classification, self.verification)
        fingerprint = _canonical_hash(
            {
                "check_id": self.check_id,
                "checker_actor_id": self.checker_actor_id,
                "contract_version": SYNTHETIC_GOVERNANCE_EVIDENCE_CONTRACT_VERSION,
                "institution_id": self.institution_id,
                "object_hash": self.object_hash,
                "object_id": self.object_id,
                "object_version": self.object_version,
                "proposal_fingerprint": self.proposal_fingerprint,
                "proposal_id": self.proposal_id,
                "purpose_id": self.purpose_id,
                "source_id": self.source_id,
                "submitted_at": submitted_at.isoformat(),
            }
        )
        object.__setattr__(self, "submitted_at", submitted_at)
        object.__setattr__(self, "_fingerprint", fingerprint)

    @property
    def fingerprint(self) -> str:
        return self._fingerprint


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticMakerCheckerReceipt:
    check_id: str
    proposal_id: str
    proposal_fingerprint: str
    submission_fingerprint: str
    maker_actor_id: str
    checker_actor_id: str
    disposition: SyntheticIndependenceDisposition
    reason: SyntheticIndependenceReason
    evaluated_at: datetime
    authority: AdminAuthority = AdminAuthority.ENGINEERING_ONLY
    classification: AdminClassification = AdminClassification.ENGINEERING_SYNTHETIC
    verification: AdminVerification = AdminVerification.UNVERIFIED
    contract_version: str = SYNTHETIC_GOVERNANCE_EVIDENCE_CONTRACT_VERSION
    _fingerprint: str = field(init=False, repr=False, compare=True)

    def __post_init__(self) -> None:
        _machine_string(self.check_id, _CHECK_ID)
        _machine_string(self.proposal_id, _PROPOSAL_ID)
        _machine_string(self.proposal_fingerprint, _SHA256)
        _machine_string(self.submission_fingerprint, _SHA256)
        _machine_string(self.maker_actor_id, _ACTOR_ID)
        _machine_string(self.checker_actor_id, _ACTOR_ID)
        _strict_enum(self.disposition, SyntheticIndependenceDisposition)
        _strict_enum(self.reason, SyntheticIndependenceReason)
        consistent = (
            self.disposition is SyntheticIndependenceDisposition.INDEPENDENCE_CONFIRMED
            and self.reason is SyntheticIndependenceReason.DISTINCT_ACTOR_EXACT_REVISION
            and self.maker_actor_id != self.checker_actor_id
        ) or (
            self.disposition is SyntheticIndependenceDisposition.ABSTAINED
            and (
                (
                    self.reason is SyntheticIndependenceReason.SELF_REVIEW
                    and self.maker_actor_id == self.checker_actor_id
                )
                or (
                    self.reason is SyntheticIndependenceReason.SCOPE_MISMATCH
                    and self.maker_actor_id != self.checker_actor_id
                )
            )
        )
        if not consistent:
            raise _error(GovernanceEvidenceContractCode.INCONSISTENT_RECEIPT)
        evaluated_at = _utc(self.evaluated_at)
        _labels(self.authority, self.classification, self.verification)
        if (
            type(self.contract_version) is not str
            or self.contract_version != SYNTHETIC_GOVERNANCE_EVIDENCE_CONTRACT_VERSION
        ):
            raise _error(GovernanceEvidenceContractCode.INVALID_VALUE)
        fingerprint = _canonical_hash(
            {
                "check_id": self.check_id,
                "checker_actor_id": self.checker_actor_id,
                "contract_version": self.contract_version,
                "disposition": self.disposition.value,
                "evaluated_at": evaluated_at.isoformat(),
                "maker_actor_id": self.maker_actor_id,
                "proposal_fingerprint": self.proposal_fingerprint,
                "proposal_id": self.proposal_id,
                "reason": self.reason.value,
                "submission_fingerprint": self.submission_fingerprint,
            }
        )
        object.__setattr__(self, "evaluated_at", evaluated_at)
        object.__setattr__(self, "_fingerprint", fingerprint)

    @property
    def fingerprint(self) -> str:
        return self._fingerprint


def snapshot_governance_proposal(value: object) -> SyntheticGovernanceProposal:
    if type(value) is not SyntheticGovernanceProposal:
        raise _error(GovernanceEvidenceContractCode.INVALID_TYPE)
    try:
        snapshot = SyntheticGovernanceProposal(
            proposal_id=value.proposal_id,
            maker_actor_id=value.maker_actor_id,
            object_id=value.object_id,
            object_version=value.object_version,
            object_hash=value.object_hash,
            institution_id=value.institution_id,
            source_id=value.source_id,
            purpose_id=value.purpose_id,
            change_kind=value.change_kind,
            created_at=value.created_at,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
        )
    except GovernanceEvidenceContractError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(GovernanceEvidenceContractCode.INVALID_TYPE) from None
    if snapshot.fingerprint != value.fingerprint:
        raise _error(GovernanceEvidenceContractCode.SNAPSHOT_DRIFT)
    return snapshot


def snapshot_checker_submission(value: object) -> SyntheticCheckerSubmission:
    if type(value) is not SyntheticCheckerSubmission:
        raise _error(GovernanceEvidenceContractCode.INVALID_TYPE)
    try:
        snapshot = SyntheticCheckerSubmission(
            check_id=value.check_id,
            checker_actor_id=value.checker_actor_id,
            proposal_id=value.proposal_id,
            proposal_fingerprint=value.proposal_fingerprint,
            object_id=value.object_id,
            object_version=value.object_version,
            object_hash=value.object_hash,
            institution_id=value.institution_id,
            source_id=value.source_id,
            purpose_id=value.purpose_id,
            submitted_at=value.submitted_at,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
        )
    except GovernanceEvidenceContractError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(GovernanceEvidenceContractCode.INVALID_TYPE) from None
    if snapshot.fingerprint != value.fingerprint:
        raise _error(GovernanceEvidenceContractCode.SNAPSHOT_DRIFT)
    return snapshot


def snapshot_maker_checker_receipt(value: object) -> SyntheticMakerCheckerReceipt:
    if type(value) is not SyntheticMakerCheckerReceipt:
        raise _error(GovernanceEvidenceContractCode.INVALID_TYPE)
    try:
        snapshot = SyntheticMakerCheckerReceipt(
            check_id=value.check_id,
            proposal_id=value.proposal_id,
            proposal_fingerprint=value.proposal_fingerprint,
            submission_fingerprint=value.submission_fingerprint,
            maker_actor_id=value.maker_actor_id,
            checker_actor_id=value.checker_actor_id,
            disposition=value.disposition,
            reason=value.reason,
            evaluated_at=value.evaluated_at,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
            contract_version=value.contract_version,
        )
    except GovernanceEvidenceContractError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(GovernanceEvidenceContractCode.INVALID_TYPE) from None
    if snapshot.fingerprint != value.fingerprint:
        raise _error(GovernanceEvidenceContractCode.SNAPSHOT_DRIFT)
    return snapshot


def _receipt_semantic_key(receipt: SyntheticMakerCheckerReceipt) -> tuple[str, str]:
    return (receipt.proposal_id, receipt.proposal_fingerprint)


@dataclass(frozen=True, slots=True, kw_only=True)
class SyntheticGovernanceAuditSnapshot:
    snapshot_id: str
    generated_at: datetime
    receipts: tuple[SyntheticMakerCheckerReceipt, ...]
    authority: AdminAuthority = AdminAuthority.ENGINEERING_ONLY
    classification: AdminClassification = AdminClassification.ENGINEERING_SYNTHETIC
    verification: AdminVerification = AdminVerification.UNVERIFIED
    contract_version: str = SYNTHETIC_GOVERNANCE_EVIDENCE_CONTRACT_VERSION
    _fingerprint: str = field(init=False, repr=False, compare=True)

    def __post_init__(self) -> None:
        _machine_string(self.snapshot_id, _SNAPSHOT_ID)
        generated_at = _utc(self.generated_at)
        if type(self.receipts) is not tuple:
            raise _error(GovernanceEvidenceContractCode.INVALID_TYPE)
        if len(self.receipts) > MAX_SYNTHETIC_GOVERNANCE_AUDIT_RECEIPTS:
            raise _error(GovernanceEvidenceContractCode.LIMIT_EXCEEDED)
        safe_receipts = tuple(snapshot_maker_checker_receipt(item) for item in self.receipts)
        check_ids = tuple(item.check_id for item in safe_receipts)
        if len(set(check_ids)) != len(check_ids):
            raise _error(GovernanceEvidenceContractCode.DUPLICATE_RECEIPT)
        semantic_keys = tuple(_receipt_semantic_key(item) for item in safe_receipts)
        if len(set(semantic_keys)) != len(semantic_keys):
            raise _error(GovernanceEvidenceContractCode.AMBIGUOUS_RECEIPT)
        if check_ids != tuple(sorted(check_ids)):
            raise _error(GovernanceEvidenceContractCode.INVALID_VALUE)
        if any(item.evaluated_at > generated_at for item in safe_receipts):
            raise _error(GovernanceEvidenceContractCode.INVALID_CHRONOLOGY)
        _labels(self.authority, self.classification, self.verification)
        if (
            type(self.contract_version) is not str
            or self.contract_version != SYNTHETIC_GOVERNANCE_EVIDENCE_CONTRACT_VERSION
        ):
            raise _error(GovernanceEvidenceContractCode.INVALID_VALUE)
        fingerprint = _canonical_hash(
            {
                "contract_version": self.contract_version,
                "generated_at": generated_at.isoformat(),
                "receipt_fingerprints": [item.fingerprint for item in safe_receipts],
                "snapshot_id": self.snapshot_id,
            }
        )
        object.__setattr__(self, "generated_at", generated_at)
        object.__setattr__(self, "receipts", safe_receipts)
        object.__setattr__(self, "_fingerprint", fingerprint)

    @property
    def fingerprint(self) -> str:
        return self._fingerprint


def snapshot_governance_audit(value: object) -> SyntheticGovernanceAuditSnapshot:
    if type(value) is not SyntheticGovernanceAuditSnapshot:
        raise _error(GovernanceEvidenceContractCode.INVALID_TYPE)
    try:
        snapshot = SyntheticGovernanceAuditSnapshot(
            snapshot_id=value.snapshot_id,
            generated_at=value.generated_at,
            receipts=value.receipts,
            authority=value.authority,
            classification=value.classification,
            verification=value.verification,
            contract_version=value.contract_version,
        )
    except GovernanceEvidenceContractError:
        raise
    except (AttributeError, TypeError, ValueError):
        raise _error(GovernanceEvidenceContractCode.INVALID_TYPE) from None
    if snapshot.fingerprint != value.fingerprint:
        raise _error(GovernanceEvidenceContractCode.SNAPSHOT_DRIFT)
    return snapshot


__all__ = [
    "MAX_SYNTHETIC_GOVERNANCE_AUDIT_RECEIPTS",
    "SYNTHETIC_GOVERNANCE_EVIDENCE_CONTRACT_VERSION",
    "GovernanceEvidenceContractCode",
    "GovernanceEvidenceContractError",
    "SyntheticCheckerSubmission",
    "SyntheticGovernanceAuditSnapshot",
    "SyntheticGovernanceChangeKind",
    "SyntheticGovernanceProposal",
    "SyntheticIndependenceDisposition",
    "SyntheticIndependenceReason",
    "SyntheticMakerCheckerReceipt",
    "snapshot_checker_submission",
    "snapshot_governance_audit",
    "snapshot_governance_proposal",
    "snapshot_maker_checker_receipt",
]
