"""Authorized patient longitudinal timeline HTTP API."""

import base64
import json
from datetime import UTC, datetime
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response
from pydantic import BaseModel, ConfigDict

from app.api.security.authorization import require_self_subject
from app.modules.encounters.domain import EncounterStatus, EncounterType
from app.modules.identity.authorization import PATIENT_READ_SELF
from app.modules.patients.api import ProvenanceSummary, fact_view
from app.modules.patients.clinical import FactType, clinical_fact_label
from app.modules.provenance.contracts import (
    ReadTimelineCapability,
    TimelineCursor,
    TimelineEntry,
    TimelineEntryType,
)
from app.modules.provenance.domain import VerificationState
from app.shared.errors import ApplicationError, ErrorCode
from app.shared.types import OpaqueId

_CURSOR_VERSION = "p5c-v1"


class EncounterTimelineEntryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    entry_id: UUID
    entry_type: TimelineEntryType
    occurred_at: datetime
    encounter_id: UUID
    encounter_type: EncounterType
    status: EncounterStatus
    completed_at: datetime | None


class FactTimelineEntryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    entry_id: UUID
    entry_type: TimelineEntryType
    occurred_at: datetime
    fact_id: UUID
    fact_type: FactType
    canonical_label: str
    verification_state: VerificationState
    superseded_by_fact_id: UUID | None
    provenance: ProvenanceSummary


type TimelineEntryResponse = EncounterTimelineEntryResponse | FactTimelineEntryResponse


class TimelineResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    items: tuple[TimelineEntryResponse, ...]
    next_cursor: str | None


def encode_timeline_cursor(entry: TimelineEntry) -> str:
    payload = json.dumps(
        {
            "version": _CURSOR_VERSION,
            "occurred_at": entry.occurred_at.isoformat(),
            "entry_type": entry.entry_type.value,
            "entry_id": str(entry.entry_id),
        },
        separators=(",", ":"),
        sort_keys=True,
    ).encode()
    return base64.urlsafe_b64encode(payload).decode().rstrip("=")


def decode_timeline_cursor(value: str | None) -> TimelineCursor | None:
    if value is None:
        return None
    try:
        raw = base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
        payload: Any = json.loads(raw)
        expected = {"version", "occurred_at", "entry_type", "entry_id"}
        if (
            not isinstance(payload, dict)
            or set(payload) != expected
            or payload["version"] != _CURSOR_VERSION
        ):
            raise ValueError
        occurred_at = datetime.fromisoformat(payload["occurred_at"])
        if occurred_at.tzinfo is None or occurred_at.utcoffset() is None:
            raise ValueError
        return TimelineCursor(
            occurred_at=occurred_at.astimezone(UTC),
            entry_type=TimelineEntryType(payload["entry_type"]),
            entry_id=OpaqueId.parse(payload["entry_id"]),
        )
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        raise ApplicationError(
            code=ErrorCode.VALIDATION_ERROR, message="The timeline cursor is invalid.", cause=exc
        ) from exc


def _strict_utc(value: str | None) -> datetime | None:
    if value is None:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ApplicationError(
            code=ErrorCode.VALIDATION_ERROR, message="Timeline timestamps must be UTC.", cause=exc
        ) from exc
    offset = parsed.utcoffset()
    if parsed.tzinfo is None or offset is None or offset.total_seconds() != 0:
        raise ApplicationError(
            code=ErrorCode.VALIDATION_ERROR, message="Timeline timestamps must be UTC."
        )
    return parsed.astimezone(UTC)


def _view(entry: TimelineEntry) -> TimelineEntryResponse:
    if entry.encounter is not None:
        return EncounterTimelineEntryResponse(
            entry_id=entry.entry_id.value,
            entry_type=entry.entry_type,
            occurred_at=entry.occurred_at,
            encounter_id=entry.encounter.encounter_id.value,
            encounter_type=entry.encounter.encounter_type,
            status=entry.encounter.status,
            completed_at=entry.encounter.completed_at,
        )
    if entry.fact is None:
        raise ValueError("timeline entry has no payload")
    fact = fact_view(entry.fact)
    return FactTimelineEntryResponse(
        entry_id=entry.entry_id.value,
        entry_type=entry.entry_type,
        occurred_at=entry.occurred_at,
        fact_id=entry.fact.fact_id.value,
        fact_type=entry.fact.fact_type,
        canonical_label=clinical_fact_label(entry.fact.value),
        verification_state=entry.fact.verification_state,
        superseded_by_fact_id=(
            None
            if entry.fact.superseded_by_fact_id is None
            else entry.fact.superseded_by_fact_id.value
        ),
        provenance=fact.provenance,
    )


def build_timeline_router(*, timeline: ReadTimelineCapability) -> APIRouter:
    router = APIRouter(prefix="/patients", tags=["patients"])

    @router.get(
        "/{patient_id}/timeline",
        response_model=TimelineResponse,
        dependencies=[Depends(require_self_subject(PATIENT_READ_SELF, "patient_id"))],
    )
    async def get_timeline(
        patient_id: UUID,
        response: Response,
        limit: Annotated[int, Query(ge=1, le=100)] = 50,
        cursor: Annotated[str | None, Query(min_length=1, max_length=1024)] = None,
        entry_type: Annotated[TimelineEntryType | None, Query()] = None,
        from_value: Annotated[str | None, Query(alias="from")] = None,
        to_value: Annotated[str | None, Query(alias="to")] = None,
    ) -> TimelineResponse:
        response.headers["Cache-Control"] = "no-store"
        from_time = _strict_utc(from_value)
        to_time = _strict_utc(to_value)
        page = await timeline.get_timeline(
            patient_id=OpaqueId(patient_id),
            limit=limit,
            cursor=decode_timeline_cursor(cursor),
            entry_type=entry_type,
            from_time=from_time,
            to_time=to_time,
        )
        return TimelineResponse(
            items=tuple(_view(item) for item in page.items),
            next_cursor=(
                encode_timeline_cursor(page.items[-1]) if page.has_more and page.items else None
            ),
        )

    return router
