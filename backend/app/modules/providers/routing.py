"""Detached, engineering-only symbolic routing and abstention mechanics."""

import re
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Final

from app.modules.providers.domain import (
    DirectoryAuthority,
    DirectoryContractError,
    DirectoryDataClassification,
    DirectoryVerificationState,
)

_RULE_ID: Final = re.compile(r"^syn_route_rule_[a-z0-9][a-z0-9_]{0,95}$")
_REQUEST_ID: Final = re.compile(r"^syn_route_request_[a-z0-9][a-z0-9_]{0,95}$")
_POLICY_ID: Final = re.compile(r"^syn_route_policy_[a-z0-9][a-z0-9_]{0,95}$")
_SIGNAL_CODE: Final = re.compile(r"^syn_signal_[a-z0-9][a-z0-9_]{0,95}$")
_SERVICE_CODE: Final = re.compile(r"^syn_service_[a-z0-9][a-z0-9_]{0,95}$")
_VERSION: Final = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
_SHA256: Final = re.compile(r"^[a-f0-9]{64}$")
_MAX_RULES: Final = 256
_MAX_RULE_ORDER: Final = 10_000


class RoutingDisposition(StrEnum):
    SYMBOLIC_MATCH = "SYMBOLIC_MATCH"
    ABSTAIN = "ABSTAIN"


class RoutingReason(StrEnum):
    EXACT_SYMBOLIC_MATCH = "EXACT_SYMBOLIC_MATCH"
    NO_SYMBOLIC_MATCH = "NO_SYMBOLIC_MATCH"
    AMBIGUOUS_SYMBOLIC_MATCH = "AMBIGUOUS_SYMBOLIC_MATCH"


def _error(message: str) -> DirectoryContractError:
    return DirectoryContractError(message)


def _machine_value(value: object, *, name: str, pattern: re.Pattern[str]) -> str:
    if type(value) is not str or pattern.fullmatch(value) is None:
        raise _error(f"{name} has an invalid synthetic machine value")
    return value


def _utc(value: object, *, name: str) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise _error(f"{name} must be timezone-aware")
    return value.astimezone(UTC)


def _closed_enum(value: object, expected: type[StrEnum], *, name: str) -> None:
    if type(value) is not expected:
        raise _error(f"{name} has invalid authority")


def _fixed_directory_authority(
    authority: object,
    classification: object,
    verification: object,
) -> None:
    _closed_enum(authority, DirectoryAuthority, name="routing authority")
    _closed_enum(classification, DirectoryDataClassification, name="routing classification")
    _closed_enum(verification, DirectoryVerificationState, name="routing verification")


@dataclass(frozen=True, slots=True)
class SymbolicRoutingRule:
    rule_id: str
    signal_code: str
    service_code: str
    order: int

    def __post_init__(self) -> None:
        _machine_value(self.rule_id, name="rule_id", pattern=_RULE_ID)
        _machine_value(self.signal_code, name="signal_code", pattern=_SIGNAL_CODE)
        _machine_value(self.service_code, name="service_code", pattern=_SERVICE_CODE)
        if type(self.order) is not int or not 1 <= self.order <= _MAX_RULE_ORDER:
            raise _error("order must be a bounded positive integer")


def _rule_snapshot(value: object) -> SymbolicRoutingRule:
    if type(value) is not SymbolicRoutingRule:
        raise _error("rules must contain only symbolic routing rules")
    return SymbolicRoutingRule(
        rule_id=value.rule_id,
        signal_code=value.signal_code,
        service_code=value.service_code,
        order=value.order,
    )


@dataclass(frozen=True, slots=True)
class SyntheticRoutingPolicy:
    policy_id: str
    policy_version: str
    artifact_hash: str
    rules: tuple[SymbolicRoutingRule, ...]
    activated_at: datetime
    authority: DirectoryAuthority = DirectoryAuthority.ENGINEERING_ONLY
    classification: DirectoryDataClassification = DirectoryDataClassification.ENGINEERING_SYNTHETIC
    verification: DirectoryVerificationState = DirectoryVerificationState.UNVERIFIED

    def __post_init__(self) -> None:
        _machine_value(self.policy_id, name="policy_id", pattern=_POLICY_ID)
        _machine_value(self.policy_version, name="policy_version", pattern=_VERSION)
        _machine_value(self.artifact_hash, name="artifact_hash", pattern=_SHA256)
        if type(self.rules) is not tuple or not self.rules or len(self.rules) > _MAX_RULES:
            raise _error("rules must be a non-empty bounded tuple")
        rules = tuple(
            sorted(
                (_rule_snapshot(item) for item in self.rules),
                key=lambda item: (item.order, item.rule_id),
            )
        )
        if len({item.rule_id for item in rules}) != len(rules):
            raise _error("rule identifiers must be unique")
        _fixed_directory_authority(self.authority, self.classification, self.verification)
        object.__setattr__(self, "rules", rules)
        object.__setattr__(self, "activated_at", _utc(self.activated_at, name="activated_at"))


def _policy_snapshot(value: object) -> SyntheticRoutingPolicy:
    if type(value) is not SyntheticRoutingPolicy:
        raise _error("policy has an invalid type")
    return SyntheticRoutingPolicy(
        policy_id=value.policy_id,
        policy_version=value.policy_version,
        artifact_hash=value.artifact_hash,
        rules=value.rules,
        activated_at=value.activated_at,
        authority=value.authority,
        classification=value.classification,
        verification=value.verification,
    )


@dataclass(frozen=True, slots=True)
class SymbolicRoutingRequest:
    request_id: str
    signal_code: str
    created_at: datetime
    authority: DirectoryAuthority = DirectoryAuthority.ENGINEERING_ONLY
    classification: DirectoryDataClassification = DirectoryDataClassification.ENGINEERING_SYNTHETIC

    def __post_init__(self) -> None:
        _machine_value(self.request_id, name="request_id", pattern=_REQUEST_ID)
        _machine_value(self.signal_code, name="signal_code", pattern=_SIGNAL_CODE)
        _closed_enum(self.authority, DirectoryAuthority, name="request authority")
        _closed_enum(
            self.classification, DirectoryDataClassification, name="request classification"
        )
        object.__setattr__(self, "created_at", _utc(self.created_at, name="created_at"))


def _request_snapshot(value: object) -> SymbolicRoutingRequest:
    if type(value) is not SymbolicRoutingRequest:
        raise _error("request has an invalid type")
    return SymbolicRoutingRequest(
        request_id=value.request_id,
        signal_code=value.signal_code,
        created_at=value.created_at,
        authority=value.authority,
        classification=value.classification,
    )


@dataclass(frozen=True, slots=True)
class SymbolicRoutingDecision:
    request_id: str
    policy_id: str
    policy_version: str
    policy_artifact_hash: str
    disposition: RoutingDisposition
    reason: RoutingReason
    service_code: str | None
    matched_rule_id: str | None
    evaluated_at: datetime
    authority: DirectoryAuthority = DirectoryAuthority.ENGINEERING_ONLY
    classification: DirectoryDataClassification = DirectoryDataClassification.ENGINEERING_SYNTHETIC
    verification: DirectoryVerificationState = DirectoryVerificationState.UNVERIFIED

    def __post_init__(self) -> None:
        _machine_value(self.request_id, name="request_id", pattern=_REQUEST_ID)
        _machine_value(self.policy_id, name="policy_id", pattern=_POLICY_ID)
        _machine_value(self.policy_version, name="policy_version", pattern=_VERSION)
        _machine_value(self.policy_artifact_hash, name="policy_artifact_hash", pattern=_SHA256)
        _closed_enum(self.disposition, RoutingDisposition, name="routing disposition")
        _closed_enum(self.reason, RoutingReason, name="routing reason")
        _fixed_directory_authority(self.authority, self.classification, self.verification)

        is_match = self.disposition is RoutingDisposition.SYMBOLIC_MATCH
        if is_match:
            if self.reason is not RoutingReason.EXACT_SYMBOLIC_MATCH:
                raise _error("symbolic match requires the exact-match reason")
            _machine_value(self.service_code, name="service_code", pattern=_SERVICE_CODE)
            _machine_value(self.matched_rule_id, name="matched_rule_id", pattern=_RULE_ID)
        elif (
            self.reason
            not in {RoutingReason.NO_SYMBOLIC_MATCH, RoutingReason.AMBIGUOUS_SYMBOLIC_MATCH}
            or self.service_code is not None
            or self.matched_rule_id is not None
        ):
            raise _error("abstention cannot carry a service or matched rule")
        object.__setattr__(self, "evaluated_at", _utc(self.evaluated_at, name="evaluated_at"))


def evaluate_symbolic_route(
    request: SymbolicRoutingRequest,
    policy: SyntheticRoutingPolicy,
    *,
    evaluated_at: datetime,
) -> SymbolicRoutingDecision:
    """Evaluate exact synthetic symbols; missing or ambiguous matches abstain."""

    safe_request = _request_snapshot(request)
    safe_policy = _policy_snapshot(policy)
    safe_evaluated_at = _utc(evaluated_at, name="evaluated_at")
    if safe_request.created_at > safe_evaluated_at:
        raise _error("request cannot be created after evaluation")
    if safe_policy.activated_at > safe_evaluated_at:
        raise _error("policy cannot be activated after evaluation")

    matches = tuple(
        item for item in safe_policy.rules if item.signal_code == safe_request.signal_code
    )
    if len(matches) == 1:
        disposition = RoutingDisposition.SYMBOLIC_MATCH
        reason = RoutingReason.EXACT_SYMBOLIC_MATCH
        service_code = matches[0].service_code
        matched_rule_id = matches[0].rule_id
    else:
        disposition = RoutingDisposition.ABSTAIN
        reason = (
            RoutingReason.NO_SYMBOLIC_MATCH
            if not matches
            else RoutingReason.AMBIGUOUS_SYMBOLIC_MATCH
        )
        service_code = None
        matched_rule_id = None

    return SymbolicRoutingDecision(
        request_id=safe_request.request_id,
        policy_id=safe_policy.policy_id,
        policy_version=safe_policy.policy_version,
        policy_artifact_hash=safe_policy.artifact_hash,
        disposition=disposition,
        reason=reason,
        service_code=service_code,
        matched_rule_id=matched_rule_id,
        evaluated_at=safe_evaluated_at,
    )


__all__ = [
    "RoutingDisposition",
    "RoutingReason",
    "SymbolicRoutingDecision",
    "SymbolicRoutingRequest",
    "SymbolicRoutingRule",
    "SyntheticRoutingPolicy",
    "evaluate_symbolic_route",
]
