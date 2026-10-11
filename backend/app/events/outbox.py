"""PostgreSQL transactional outbox model and transaction-scoped repository."""

from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, Index, Integer, String, Uuid, select, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from app.events.envelope import EventEnvelope, JsonValue
from app.shared.persistence import Base
from app.shared.types import OpaqueId, utc_now


class OutboxStatus(StrEnum):
    """Finite operational delivery states for an outbox row."""

    PENDING = "PENDING"
    DISPATCHED = "DISPATCHED"
    FAILED = "FAILED"


_ERROR_CODE_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]{0,63}$")


def _utc(name: str, value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value.astimezone(UTC)


def _error_code(value: str) -> str:
    if _ERROR_CODE_PATTERN.fullmatch(value) is None:
        raise ValueError("error_code must be a bounded machine-readable code")
    return value


class OutboxEventRecord(Base):
    """Durable event content plus mutable delivery metadata."""

    __tablename__ = "outbox_events"
    __table_args__ = (
        CheckConstraint("event_version > 0", name="event_version_positive"),
        CheckConstraint("attempt_count >= 0", name="attempt_count_nonnegative"),
        CheckConstraint(
            "status IN ('PENDING', 'DISPATCHED', 'FAILED')",
            name="status_supported",
        ),
        Index("ix_outbox_events_status_available_at", "status", "available_at"),
        Index("ix_outbox_events_event_type", "event_type"),
        Index("ix_outbox_events_aggregate_id", "aggregate_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    event_type: Mapped[str] = mapped_column(String(128), nullable=False)
    event_version: Mapped[int] = mapped_column(Integer, nullable=False)
    aggregate_type: Mapped[str | None] = mapped_column(String(128), nullable=True)
    aggregate_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    correlation_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    causation_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    actor_ref: Mapped[str | None] = mapped_column(String(128), nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    payload: Mapped[dict[str, JsonValue]] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=OutboxStatus.PENDING.value,
        server_default=text("'PENDING'"),
    )
    attempt_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0")
    )
    available_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    dispatched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    def to_envelope(self) -> EventEnvelope:
        """Reconstruct canonical event content without delivery metadata."""
        return EventEnvelope.create(
            event_id=OpaqueId(self.id),
            event_type=self.event_type,
            event_version=self.event_version,
            occurred_at=self.occurred_at,
            correlation_id=self.correlation_id,
            causation_id=self.causation_id,
            actor_ref=self.actor_ref,
            payload=self.payload,
        )

    def __repr__(self) -> str:
        """Expose safe operational metadata while withholding payload content."""
        return (
            f"OutboxEventRecord(id={self.id!r}, event_type={self.event_type!r}, "
            f"status={self.status!r}, attempt_count={self.attempt_count!r})"
        )


class OutboxRepository:
    """Narrow outbox operations that never own or commit transactions."""

    def build_record(
        self,
        event: EventEnvelope,
        *,
        aggregate_type: str | None = None,
        aggregate_id: OpaqueId | None = None,
        available_at: datetime | None = None,
        created_at: datetime | None = None,
    ) -> OutboxEventRecord:
        """Build a pending row from immutable event content."""
        if aggregate_type is not None and (
            aggregate_type != aggregate_type.strip()
            or not aggregate_type
            or len(aggregate_type) > 128
            or not aggregate_type.isprintable()
        ):
            raise ValueError("aggregate_type must be non-empty and at most 128 characters")
        inserted_at = _utc("created_at", created_at or utc_now())
        due_at = _utc("available_at", available_at or inserted_at)
        payload = event.to_dict()["payload"]
        if not isinstance(payload, dict):
            raise ValueError("event payload must be a JSON-compatible mapping")
        return OutboxEventRecord(
            id=event.event_id.value,
            event_type=str(event.event_type),
            event_version=event.event_version,
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id.value if aggregate_id is not None else None,
            correlation_id=event.correlation_id,
            causation_id=event.causation_id,
            actor_ref=event.actor_ref,
            occurred_at=event.occurred_at,
            payload=payload,
            status=OutboxStatus.PENDING.value,
            attempt_count=0,
            available_at=due_at,
            dispatched_at=None,
            last_error_code=None,
            created_at=inserted_at,
        )

    async def enqueue(
        self,
        session: AsyncSession,
        event: EventEnvelope,
        *,
        aggregate_type: str | None = None,
        aggregate_id: OpaqueId | None = None,
        available_at: datetime | None = None,
        created_at: datetime | None = None,
    ) -> OutboxEventRecord:
        """Stage an event in the caller's transaction without flushing or committing."""
        record = self.build_record(
            event,
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            available_at=available_at,
            created_at=created_at,
        )
        session.add(record)
        return record

    async def load_next_due(
        self, session: AsyncSession, *, now: datetime
    ) -> OutboxEventRecord | None:
        """Lock the earliest due pending row while skipping concurrent locks."""
        due_at = _utc("now", now)
        statement = (
            select(OutboxEventRecord)
            .where(
                OutboxEventRecord.status == OutboxStatus.PENDING.value,
                OutboxEventRecord.available_at <= due_at,
            )
            .order_by(
                OutboxEventRecord.available_at,
                OutboxEventRecord.created_at,
                OutboxEventRecord.id,
            )
            .limit(1)
            .with_for_update(skip_locked=True)
        )
        return (await session.execute(statement)).scalar_one_or_none()

    async def get_by_event_id(
        self, session: AsyncSession, event_id: OpaqueId
    ) -> OutboxEventRecord | None:
        """Read one event by opaque ID for operations and verification."""
        return await session.get(OutboxEventRecord, event_id.value)

    def mark_dispatched(self, record: OutboxEventRecord, *, dispatched_at: datetime) -> None:
        """Record one successful delivery attempt."""
        delivered_at = _utc("dispatched_at", dispatched_at)
        record.attempt_count += 1
        record.status = OutboxStatus.DISPATCHED.value
        record.dispatched_at = delivered_at
        record.last_error_code = None

    def schedule_retry(
        self,
        record: OutboxEventRecord,
        *,
        failed_at: datetime,
        delay: timedelta,
        error_code: str,
    ) -> None:
        """Record a failed attempt and schedule the pending row deterministically."""
        if delay < timedelta(0):
            raise ValueError("retry delay must not be negative")
        failure_time = _utc("failed_at", failed_at)
        safe_error_code = _error_code(error_code)
        record.attempt_count += 1
        record.status = OutboxStatus.PENDING.value
        record.available_at = failure_time + delay
        record.dispatched_at = None
        record.last_error_code = safe_error_code

    def mark_failed(
        self, record: OutboxEventRecord, *, failed_at: datetime, error_code: str
    ) -> None:
        """Record a terminal failed delivery attempt without exposing exception details."""
        _utc("failed_at", failed_at)
        safe_error_code = _error_code(error_code)
        record.attempt_count += 1
        record.status = OutboxStatus.FAILED.value
        record.dispatched_at = None
        record.last_error_code = safe_error_code
