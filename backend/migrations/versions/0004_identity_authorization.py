"""Add P4-B actors, actor roles, and the staged session actor FK.

Revision ID: p4b_0004
Revises: p4a_0003
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "p4b_0004"
down_revision: str | Sequence[str] | None = "p4a_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create identity-owned tables and activate session actor integrity."""
    op.create_table(
        "actors",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("actor_type", sa.String(length=32), nullable=False),
        sa.Column("subject_ref", sa.Uuid(), nullable=True),
        sa.Column("institution_id", sa.Uuid(), nullable=True),
        sa.Column("status", sa.String(length=16), server_default="ACTIVE", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "actor_type IN ('PATIENT','PSEUDONYMOUS_USER','CAREGIVER','CLINICIAN',"
            "'COUNSELLOR','TRIAGE_STAFF','RESOURCE_ADMIN','CLINICAL_REVIEWER',"
            "'SYSTEM_ADMIN','RESEARCHER','SERVICE_ACCOUNT')",
            name="actor_type_supported",
        ),
        sa.CheckConstraint("status IN ('ACTIVE','DISABLED')", name="status_supported"),
        sa.PrimaryKeyConstraint("id", name="pk_actors"),
    )
    op.create_table(
        "actor_roles",
        sa.Column("actor_id", sa.Uuid(), nullable=False),
        sa.Column("role_code", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "role_code IN ('patient','pseudonymous_user','clinician','resource_admin',"
            "'clinical_reviewer','system_admin','researcher')",
            name="role_code_supported",
        ),
        sa.ForeignKeyConstraint(
            ["actor_id"], ["actors.id"], name="fk_actor_roles_actor_id_actors", ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("actor_id", "role_code", name="pk_actor_roles"),
    )
    op.create_foreign_key("fk_sessions_actor_id_actors", "sessions", "actors", ["actor_id"], ["id"])


def downgrade() -> None:
    """Return exactly to the P4-A schema."""
    op.drop_constraint("fk_sessions_actor_id_actors", "sessions", type_="foreignkey")
    op.drop_table("actor_roles")
    op.drop_table("actors")
