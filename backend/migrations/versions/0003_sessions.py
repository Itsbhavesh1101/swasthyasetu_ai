"""Add authoritative P4-A sessions.

Revision ID: p4a_0003
Revises: p3b_0002
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "p4a_0003"
down_revision: str | Sequence[str] | None = "p3b_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create only the sessions-owned table and indexes."""
    op.create_table(
        "sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("session_type", sa.String(length=32), nullable=False),
        sa.Column("actor_id", sa.Uuid(), nullable=True),
        sa.Column("patient_id", sa.Uuid(), nullable=True),
        sa.Column("language_preference", sa.String(length=35), nullable=True),
        sa.Column("status", sa.String(length=16), server_default="ACTIVE", nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("recovery_token_hash", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("expires_at > created_at", name="expiry_after_creation"),
        sa.CheckConstraint(
            "session_type IN ('PSEUDONYMOUS', 'AUTHENTICATED', 'KIOSK', "
            "'CLINICIAN', 'ADMIN', 'RESEARCH')",
            name="session_type_supported",
        ),
        sa.CheckConstraint(
            "status IN ('ACTIVE', 'EXPIRED', 'CLOSED', 'REVOKED')",
            name="status_supported",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_sessions"),
        sa.UniqueConstraint("token_hash", name="uq_sessions_token_hash"),
    )
    op.create_index("ix_sessions_actor_id", "sessions", ["actor_id"], unique=False)
    op.create_index("ix_sessions_patient_id", "sessions", ["patient_id"], unique=False)
    op.create_index(
        "ix_sessions_status_expires_at", "sessions", ["status", "expires_at"], unique=False
    )


def downgrade() -> None:
    """Remove only the sessions-owned table."""
    op.drop_index("ix_sessions_status_expires_at", table_name="sessions")
    op.drop_index("ix_sessions_patient_id", table_name="sessions")
    op.drop_index("ix_sessions_actor_id", table_name="sessions")
    op.drop_table("sessions")
