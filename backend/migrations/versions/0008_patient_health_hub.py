"""Add patient account and document metadata persistence.

Revision ID: patient_hub_0008
Revises: p7a_0007
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "patient_hub_0008"
down_revision: str | Sequence[str] | None = "p7a_0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create patient-owned account and document metadata tables."""
    op.create_table(
        "patient_accounts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("actor_id", sa.Uuid(), nullable=False),
        sa.Column("patient_id", sa.Uuid(), nullable=False),
        sa.Column("email_normalized", sa.String(length=320), nullable=False),
        sa.Column("email_display", sa.String(length=320), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("password_hash", sa.String(length=512), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status IN ('ACTIVE','DISABLED')",
            name=op.f("ck_patient_accounts_status_supported"),
        ),
        sa.CheckConstraint(
            "email_normalized = lower(btrim(email_normalized))",
            name=op.f("ck_patient_accounts_email_normalized_canonical"),
        ),
        sa.CheckConstraint(
            "length(btrim(email_display)) > 0 AND length(btrim(display_name)) > 0",
            name=op.f("ck_patient_accounts_display_fields_nonempty"),
        ),
        sa.ForeignKeyConstraint(
            ["actor_id"],
            ["actors.id"],
            name="fk_patient_accounts_actor_id_actors",
        ),
        sa.ForeignKeyConstraint(
            ["patient_id"],
            ["patients.id"],
            name="fk_patient_accounts_patient_id_patients",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_patient_accounts"),
        sa.UniqueConstraint("actor_id", name="uq_patient_accounts_actor_id"),
        sa.UniqueConstraint("patient_id", name="uq_patient_accounts_patient_id"),
    )
    op.create_index(
        "ix_patient_accounts_email_normalized",
        "patient_accounts",
        ["email_normalized"],
        unique=True,
    )

    op.create_table(
        "patient_documents",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("patient_id", sa.Uuid(), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("mime_type", sa.String(length=100), nullable=False),
        sa.Column("byte_size", sa.BigInteger(), nullable=False),
        sa.Column("object_key", sa.String(length=512), nullable=False),
        sa.Column("sha256_digest", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "byte_size > 0",
            name=op.f("ck_patient_documents_byte_size_positive"),
        ),
        sa.CheckConstraint(
            "sha256_digest ~ '^[0-9a-f]{64}$'",
            name=op.f("ck_patient_documents_sha256_digest_valid"),
        ),
        sa.CheckConstraint(
            "length(btrim(display_name)) > 0 AND length(btrim(mime_type)) > 0",
            name=op.f("ck_patient_documents_display_fields_nonempty"),
        ),
        sa.ForeignKeyConstraint(
            ["patient_id"],
            ["patients.id"],
            name="fk_patient_documents_patient_id_patients",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_patient_documents"),
        sa.UniqueConstraint("object_key", name="uq_patient_documents_object_key"),
    )
    op.create_index(
        "ix_patient_documents_patient_id_created_at",
        "patient_documents",
        ["patient_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    """Remove only the patient health hub tables."""
    op.drop_index(
        "ix_patient_documents_patient_id_created_at",
        table_name="patient_documents",
    )
    op.drop_table("patient_documents")
    op.drop_index(
        "ix_patient_accounts_email_normalized",
        table_name="patient_accounts",
    )
    op.drop_table("patient_accounts")
