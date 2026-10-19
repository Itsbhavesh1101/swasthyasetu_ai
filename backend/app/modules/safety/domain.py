"""Immutable, policy-neutral physical-safety decision contracts."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum

_IDENTIFIER_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$")
_VERSION_PATTERN = re.compile(r"^[A-Za-z0-9]+(?:[._-][A-Za-z0-9]+)*$")
_REASON_CODE_PATTERN = re.compile(r"^[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)*$")
MAX_REASON_CODES = 16


class InvalidSafetyDecisionError(ValueError):
    """Raised for malformed policy-neutral safety decision metadata."""


class SafetyRoute(StrEnum):
    """Closed route vocabulary; route semantics belong to an approved policy."""

    EMERGENCY = "EMERGENCY"
    PRIORITY_REVIEW = "PRIORITY_REVIEW"
    ROUTINE_CARE = "ROUTINE_CARE"
    SUPPORTED_SELF_CARE = "SUPPORTED_SELF_CARE"
    CLARIFICATION_REQUIRED = "CLARIFICATION_REQUIRED"


def _validate_machine_value(
    *, name: str, value: object, maximum: int, pattern: re.Pattern[str]
) -> None:
    if (
        not isinstance(value, str)
        or not value
        or len(value) > maximum
        or pattern.fullmatch(value) is None
    ):
        raise InvalidSafetyDecisionError(f"invalid {name}")


@dataclass(frozen=True, slots=True, kw_only=True)
class SafetyDecision:
    """A non-persisted deterministic result tied to exact policy metadata.

    Clinical route/flag combinations beyond clarification are deliberately not
    interpreted here. P9-B must obtain an approved policy before doing so.
    """

    route: SafetyRoute
    reason_codes: tuple[str, ...]
    policy_id: str
    policy_version: str
    requires_clarification: bool
    blocks_self_care: bool
    created_at: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.route, SafetyRoute):
            raise InvalidSafetyDecisionError("invalid safety route")
        if not isinstance(self.reason_codes, tuple):
            raise InvalidSafetyDecisionError("invalid reason codes")
        if not self.reason_codes or len(self.reason_codes) > MAX_REASON_CODES:
            raise InvalidSafetyDecisionError("invalid reason codes")
        for code in self.reason_codes:
            _validate_machine_value(
                name="reason code", value=code, maximum=64, pattern=_REASON_CODE_PATTERN
            )
        if len(set(self.reason_codes)) != len(self.reason_codes):
            raise InvalidSafetyDecisionError("duplicate reason codes")
        if self.reason_codes != tuple(sorted(self.reason_codes)):
            raise InvalidSafetyDecisionError("reason codes must use deterministic ordering")
        _validate_machine_value(
            name="policy ID", value=self.policy_id, maximum=128, pattern=_IDENTIFIER_PATTERN
        )
        _validate_machine_value(
            name="policy version", value=self.policy_version, maximum=64, pattern=_VERSION_PATTERN
        )
        if type(self.requires_clarification) is not bool:
            raise InvalidSafetyDecisionError("invalid clarification flag")
        if type(self.blocks_self_care) is not bool:
            raise InvalidSafetyDecisionError("invalid self-care flag")
        if (self.route is SafetyRoute.CLARIFICATION_REQUIRED) != self.requires_clarification:
            raise InvalidSafetyDecisionError("inconsistent clarification route")
        if self.requires_clarification and not self.blocks_self_care:
            raise InvalidSafetyDecisionError("clarification must block self-care")
        if not isinstance(self.created_at, datetime):
            raise InvalidSafetyDecisionError("invalid decision timestamp")
        if self.created_at.tzinfo is None or self.created_at.utcoffset() is None:
            raise InvalidSafetyDecisionError("decision timestamp must be timezone-aware")
        object.__setattr__(self, "created_at", self.created_at.astimezone(UTC))
