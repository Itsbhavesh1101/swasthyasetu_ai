"""Framework-independent session domain values."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from app.shared.types import OpaqueId


class SessionType(StrEnum):
    """Canonical session modes, including modes activated by later phases."""

    PSEUDONYMOUS = "PSEUDONYMOUS"
    AUTHENTICATED = "AUTHENTICATED"
    KIOSK = "KIOSK"
    CLINICIAN = "CLINICIAN"
    ADMIN = "ADMIN"
    RESEARCH = "RESEARCH"


class SessionStatus(StrEnum):
    """Canonical session lifecycle states."""

    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    CLOSED = "CLOSED"
    REVOKED = "REVOKED"


@dataclass(frozen=True, slots=True)
class Session:
    """Safe session metadata with no bearer or verifier material."""

    session_id: OpaqueId
    session_type: SessionType
    language_preference: str | None
    status: SessionStatus
    created_at: datetime
    expires_at: datetime
    closed_at: datetime | None
    updated_at: datetime
