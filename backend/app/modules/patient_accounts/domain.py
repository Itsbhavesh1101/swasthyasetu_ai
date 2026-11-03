"""Framework-independent patient account domain values."""

import re
from dataclasses import InitVar, dataclass, field
from datetime import UTC, datetime
from enum import StrEnum

from app.shared.types import OpaqueId

_EMAIL_PATTERN = re.compile(
    r"^[^@\s]{1,64}@[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?"
    r"(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)+$",
    re.IGNORECASE,
)


class AccountStatus(StrEnum):
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"


@dataclass(frozen=True, slots=True)
class EmailAddress:
    """Validated email with explicit display and case-insensitive lookup forms."""

    display: str = field(repr=False)
    normalized: str = field(init=False, repr=False)

    def __post_init__(self) -> None:
        display = self.display.strip()
        normalized = display.casefold()
        if len(display) > 320 or _EMAIL_PATTERN.fullmatch(display) is None:
            raise ValueError("email must be a valid bounded address")
        object.__setattr__(self, "display", display)
        object.__setattr__(self, "normalized", normalized)

    def __repr__(self) -> str:
        return "EmailAddress(<redacted>)"


@dataclass(frozen=True, slots=True)
class DisplayName:
    value: str = field(repr=False)

    def __post_init__(self) -> None:
        value = self.value.strip()
        if not value or len(value) > 120 or any(ord(character) < 32 for character in value):
            raise ValueError("display name must be non-blank and at most 120 characters")
        object.__setattr__(self, "value", value)

    def __repr__(self) -> str:
        return "DisplayName(<redacted>)"


@dataclass(frozen=True, slots=True)
class RawPassword:
    """Transient raw password value that is never safe to serialize or display."""

    value: str = field(repr=False)

    def __post_init__(self) -> None:
        if len(self.value) < 12 or len(self.value) > 128 or not self.value.strip():
            raise ValueError("password must contain between 12 and 128 non-blank characters")

    def __repr__(self) -> str:
        return "RawPassword(<redacted>)"


@dataclass(frozen=True, slots=True)
class PasswordDigest:
    """Argon2id digest loaded from or written to private persistence."""

    value: str = field(repr=False)
    require_argon2id: InitVar[bool] = True

    def __post_init__(self, require_argon2id: bool) -> None:
        if not self.value or len(self.value) > 512:
            raise ValueError("password digest must be non-empty and bounded")
        if require_argon2id and not self.value.startswith("$argon2id$"):
            raise ValueError("password digest must use Argon2id")

    @classmethod
    def from_persisted(cls, value: str) -> "PasswordDigest":
        """Load possibly corrupt stored data so verification can fail closed."""
        return cls(value, require_argon2id=False)

    def __repr__(self) -> str:
        return "PasswordDigest(<redacted>)"


def normalize_utc(name: str, value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value.astimezone(UTC)


@dataclass(frozen=True, slots=True)
class PatientAccount:
    """Private local account bound one-to-one to authorization and patient records."""

    account_id: OpaqueId
    actor_id: OpaqueId
    patient_id: OpaqueId
    email: EmailAddress = field(repr=False)
    display_name: DisplayName = field(repr=False)
    password_digest: PasswordDigest = field(repr=False)
    status: AccountStatus
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        created_at = normalize_utc("created_at", self.created_at)
        updated_at = normalize_utc("updated_at", self.updated_at)
        if updated_at < created_at:
            raise ValueError("updated_at must not precede created_at")
        object.__setattr__(self, "created_at", created_at)
        object.__setattr__(self, "updated_at", updated_at)

    def __repr__(self) -> str:
        return (
            f"PatientAccount(account_id={self.account_id!r}, actor_id={self.actor_id!r}, "
            f"patient_id={self.patient_id!r}, status={self.status!r}, "
            f"created_at={self.created_at!r}, updated_at={self.updated_at!r})"
        )
