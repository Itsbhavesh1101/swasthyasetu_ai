"""Add the platform transactional outbox.

Revision ID: p3b_0002
Revises: p3a_0001
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "p3b_0002"
down_revision: str | Sequence[str] | None = "p3a_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create only the platform-owned transactional outbox table."""
    op.create_table(
        "outbox_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("event_type", sa.String(length=128), nullable=False),
        sa.Column("event_version", sa.Integer(), nullable=False),
        sa.Column("aggregate_type", sa.String(length=128), nullable=True),
        sa.Column("aggregate_id", sa.Uuid(), nullable=True),
        sa.Column("correlation_id", sa.String(length=128), nullable=True),
        sa.Column("causation_id", sa.String(length=128), nullable=True),
        sa.Column("actor_ref", sa.String(length=128), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("status", sa.String(length=16), server_default="PENDING", nullable=False),
        sa.Column("attempt_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("available_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("dispatched_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error_code", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "attempt_count >= 0",
            name=op.f("ck_outbox_events_attempt_count_nonnegative"),
        ),
        sa.CheckConstraint(
            "event_version > 0",
            name=op.f("ck_outbox_events_event_version_positive"),
        ),
        sa.CheckConstraint(
            "status IN ('PENDING', 'DISPATCHED', 'FAILED')",
            name=op.f("ck_outbox_events_status_supported"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_outbox_events")),
    )
    op.create_index(
        "ix_outbox_events_aggregate_id", "outbox_events", ["aggregate_id"], unique=False
    )
    op.create_index("ix_outbox_events_event_type", "outbox_events", ["event_type"], unique=False)
    op.create_index(
        "ix_outbox_events_status_available_at",
        "outbox_events",
        ["status", "available_at"],
        unique=False,
    )


def downgrade() -> None:
    """Return to the P3-A empty application-schema baseline."""
    op.drop_index("ix_outbox_events_status_available_at", table_name="outbox_events")
    op.drop_index("ix_outbox_events_event_type", table_name="outbox_events")
    op.drop_index("ix_outbox_events_aggregate_id", table_name="outbox_events")
    op.drop_table("outbox_events")
