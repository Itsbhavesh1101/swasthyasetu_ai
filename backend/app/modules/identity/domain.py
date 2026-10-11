"""Framework-independent identity domain values."""

import re
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum

from app.shared.types import OpaqueId

_PERMISSION_PATTERN = re.compile(r"^[a-z][a-z0-9_]*(?::[a-z][a-z0-9_]*)+$")


class ActorType(StrEnum):
    PATIENT = "PATIENT"
    PSEUDONYMOUS_USER = "PSEUDONYMOUS_USER"
    CAREGIVER = "CAREGIVER"
    CLINICIAN = "CLINICIAN"
    COUNSELLOR = "COUNSELLOR"
    TRIAGE_STAFF = "TRIAGE_STAFF"
    RESOURCE_ADMIN = "RESOURCE_ADMIN"
    CLINICAL_REVIEWER = "CLINICAL_REVIEWER"
    SYSTEM_ADMIN = "SYSTEM_ADMIN"
    RESEARCHER = "RESEARCHER"
    SERVICE_ACCOUNT = "SERVICE_ACCOUNT"


class ActorStatus(StrEnum):
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"


class RoleCode(StrEnum):
    PATIENT = "patient"
    PSEUDONYMOUS_USER = "pseudonymous_user"
    CLINICIAN = "clinician"
    RESOURCE_ADMIN = "resource_admin"
    CLINICAL_REVIEWER = "clinical_reviewer"
    SYSTEM_ADMIN = "system_admin"
    RESEARCHER = "researcher"


@dataclass(frozen=True, slots=True, order=True)
class PermissionCode:
    """Validated, extensible action-oriented permission identifier."""

    value: str

    def __post_init__(self) -> None:
        if not _PERMISSION_PATTERN.fullmatch(self.value):
            raise ValueError("Permission code must be lowercase colon-separated segments")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class Actor:
    """Internal authorization identity, deliberately free of PII and credentials."""

    actor_id: OpaqueId
    actor_type: ActorType
    roles: frozenset[RoleCode]
    subject_id: OpaqueId | None
    institution_id: OpaqueId | None
    status: ActorStatus
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        for name, value in (("created_at", self.created_at), ("updated_at", self.updated_at)):
            offset = value.utcoffset()
            if value.tzinfo is None or offset is None or offset.total_seconds():
                raise ValueError(f"{name} must be timezone-aware UTC")
            if value.tzinfo is not UTC:
                object.__setattr__(self, name, value.astimezone(UTC))
