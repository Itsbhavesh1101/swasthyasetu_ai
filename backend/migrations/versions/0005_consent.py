"""Add P4-C purpose-specific consent persistence.

Revision ID: p4c_0005
Revises: p4b_0004
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "p4c_0005"
down_revision: str | Sequence[str] | None = "p4b_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create only the consent-owned lifecycle table."""
    op.create_table(
        "consent_records",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("subject_type", sa.String(length=16), nullable=False),
        sa.Column("subject_id", sa.Uuid(), nullable=False),
        sa.Column("actor_id", sa.Uuid(), nullable=True),
        sa.Column("purpose", sa.String(length=32), nullable=False),
        sa.Column("scope", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("notice_version", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=16), server_default="GRANTED", nullable=False),
        sa.Column("granted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revocation_reason", sa.String(length=64), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "subject_type IN ('SESSION','ACTOR','PATIENT')",
            name="subject_type_supported",
        ),
        sa.CheckConstraint(
            "purpose IN ('GENERAL_PRODUCT_USE','EXTERNAL_AI_PROCESSING',"
            "'REFERRAL_SHARING','ABDM_EXCHANGE','RESEARCH_USE','CAREGIVER_ACCESS')",
            name="purpose_supported",
        ),
        sa.CheckConstraint(
            "status IN ('GRANTED','REVOKED','EXPIRED','SUPERSEDED')",
            name="status_supported",
        ),
        sa.CheckConstraint(
            "jsonb_typeof(scope) = 'array' AND jsonb_array_length(scope) > 0",
            name="scope_json_array",
        ),
        sa.CheckConstraint(
            "expires_at IS NULL OR expires_at > granted_at",
            name="expiry_after_grant",
        ),
        sa.ForeignKeyConstraint(
            ["actor_id"], ["actors.id"], name="fk_consent_records_actor_id_actors"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_consent_records"),
    )
    op.create_index(
        "ix_consent_records_subject_type_subject_id_purpose_status",
        "consent_records",
        ["subject_type", "subject_id", "purpose", "status"],
        unique=False,
    )
    op.create_index("ix_consent_records_actor_id", "consent_records", ["actor_id"], unique=False)


def downgrade() -> None:
    """Remove only P4-C consent persistence."""
    op.drop_index("ix_consent_records_actor_id", table_name="consent_records")
    op.drop_index(
        "ix_consent_records_subject_type_subject_id_purpose_status",
        table_name="consent_records",
    )
    op.drop_table("consent_records")
