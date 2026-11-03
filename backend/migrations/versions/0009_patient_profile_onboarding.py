"""Support credentials-first registration and body measurements.

Revision ID: patient_profile_0009
Revises: patient_hub_0008
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "patient_profile_0009"
down_revision: str | Sequence[str] | None = "patient_hub_0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint(
        op.f("ck_patient_accounts_display_fields_nonempty"), "patient_accounts", type_="check"
    )
    op.alter_column("patient_accounts", "display_name", existing_type=sa.String(120), nullable=True)
    op.create_check_constraint(
        op.f("ck_patient_accounts_display_fields_nonempty"),
        "patient_accounts",
        "length(btrim(email_display)) > 0 AND "
        "(display_name IS NULL OR length(btrim(display_name)) > 0)",
    )
    op.add_column("patient_demographics", sa.Column("height_cm", sa.Numeric(5, 2), nullable=True))
    op.add_column("patient_demographics", sa.Column("weight_kg", sa.Numeric(6, 2), nullable=True))
    op.create_check_constraint(
        op.f("ck_patient_demographics_height_cm_range"),
        "patient_demographics",
        "height_cm IS NULL OR (height_cm >= 30 AND height_cm <= 275)",
    )
    op.create_check_constraint(
        op.f("ck_patient_demographics_weight_kg_range"),
        "patient_demographics",
        "weight_kg IS NULL OR (weight_kg >= 1 AND weight_kg <= 700)",
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f("ck_patient_demographics_weight_kg_range"), "patient_demographics", type_="check"
    )
    op.drop_constraint(
        op.f("ck_patient_demographics_height_cm_range"), "patient_demographics", type_="check"
    )
    op.drop_column("patient_demographics", "weight_kg")
    op.drop_column("patient_demographics", "height_cm")
    op.execute(
        "UPDATE patient_accounts SET display_name = email_display WHERE display_name IS NULL"
    )
    op.drop_constraint(
        op.f("ck_patient_accounts_display_fields_nonempty"), "patient_accounts", type_="check"
    )
    op.alter_column(
        "patient_accounts", "display_name", existing_type=sa.String(120), nullable=False
    )
    op.create_check_constraint(
        op.f("ck_patient_accounts_display_fields_nonempty"),
        "patient_accounts",
        "length(btrim(email_display)) > 0 AND length(btrim(display_name)) > 0",
    )
