"""Add private patient contact and synthetic profile identity details.

Revision ID: patient_details_0010
Revises: patient_profile_0009
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "patient_details_0010"
down_revision: str | Sequence[str] | None = "patient_profile_0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("patient_demographics", sa.Column("mobile_number", sa.String(16), nullable=True))
    op.add_column("patient_demographics", sa.Column("blood_group", sa.String(7), nullable=True))
    op.add_column(
        "patient_demographics",
        sa.Column("demo_aadhaar_reference", sa.String(17), nullable=True),
    )
    op.create_check_constraint(
        op.f("ck_patient_demographics_mobile_number_e164"),
        "patient_demographics",
        r"mobile_number IS NULL OR mobile_number ~ '^\+[1-9][0-9]{6,14}$'",
    )
    op.create_check_constraint(
        op.f("ck_patient_demographics_blood_group_supported"),
        "patient_demographics",
        "blood_group IS NULL OR blood_group IN "
        "('A+','A-','B+','B-','AB+','AB-','O+','O-','UNKNOWN')",
    )
    op.create_check_constraint(
        op.f("ck_patient_demographics_demo_aadhaar_reference_synthetic"),
        "patient_demographics",
        "demo_aadhaar_reference IS NULL OR "
        "demo_aadhaar_reference ~ '^DEMO-AADHAAR-[0-9]{4}$'",
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f("ck_patient_demographics_demo_aadhaar_reference_synthetic"),
        "patient_demographics",
        type_="check",
    )
    op.drop_constraint(
        op.f("ck_patient_demographics_blood_group_supported"),
        "patient_demographics",
        type_="check",
    )
    op.drop_constraint(
        op.f("ck_patient_demographics_mobile_number_e164"),
        "patient_demographics",
        type_="check",
    )
    op.drop_column("patient_demographics", "demo_aadhaar_reference")
    op.drop_column("patient_demographics", "blood_group")
    op.drop_column("patient_demographics", "mobile_number")
