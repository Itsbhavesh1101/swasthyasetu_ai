"""Privacy-minimized consent lifecycle event factories."""

from app.events import EventEnvelope
from app.modules.consent.domain import ConsentRecord, ConsentStatus


def _payload(record: ConsentRecord) -> dict[str, object]:
    return {
        "consent_id": str(record.consent_id),
        "subject_type": record.subject_type.value,
        "subject_id": str(record.subject_id),
        "purpose": record.purpose.value,
        "scope": list(record.scope.values),
        "notice_version": str(record.notice_version),
        "status": record.status.value,
    }


def consent_granted_event(record: ConsentRecord) -> EventEnvelope:
    if record.status is not ConsentStatus.GRANTED:
        raise ValueError("ConsentGranted requires GRANTED consent")
    return EventEnvelope.create(
        event_type="ConsentGranted",
        event_version=1,
        occurred_at=record.granted_at,
        actor_ref=None if record.actor_id is None else str(record.actor_id),
        payload=_payload(record),
    )


def consent_revoked_event(record: ConsentRecord) -> EventEnvelope:
    if record.status is not ConsentStatus.REVOKED or record.revocation_reason is None:
        raise ValueError("ConsentRevoked requires REVOKED consent")
    payload = _payload(record)
    payload["revocation_reason"] = str(record.revocation_reason)
    return EventEnvelope.create(
        event_type="ConsentRevoked",
        event_version=1,
        occurred_at=record.revoked_at,
        actor_ref=None if record.actor_id is None else str(record.actor_id),
        payload=payload,
    )
