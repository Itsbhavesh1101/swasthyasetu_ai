"""Replace the synthetic Aadhaar reference with a masked suffix.

Revision ID: patient_aadhaar_0011
Revises: patient_details_0010
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "patient_aadhaar_0011"
down_revision: str | None = "patient_details_0010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "patient_demographics",
        sa.Column("aadhaar_last_four", sa.String(4), nullable=True),
    )
    op.create_check_constraint(
        op.f("ck_patient_demographics_aadhaar_last_four_ascii_digits"),
        "patient_demographics",
        "aadhaar_last_four IS NULL OR aadhaar_last_four ~ '^[0-9]{4}$'",
    )
    op.drop_constraint(
        op.f("ck_patient_demographics_demo_aadhaar_reference_synthetic"),
        "patient_demographics",
        type_="check",
    )
    op.drop_column("patient_demographics", "demo_aadhaar_reference")


def downgrade() -> None:
    op.add_column(
        "patient_demographics",
        sa.Column("demo_aadhaar_reference", sa.String(17), nullable=True),
    )
    op.create_check_constraint(
        op.f("ck_patient_demographics_demo_aadhaar_reference_synthetic"),
        "patient_demographics",
        "demo_aadhaar_reference IS NULL OR demo_aadhaar_reference ~ '^DEMO-AADHAAR-[0-9]{4}$'",
    )
    op.drop_constraint(
        op.f("ck_patient_demographics_aadhaar_last_four_ascii_digits"),
        "patient_demographics",
        type_="check",
    )
    op.drop_column("patient_demographics", "aadhaar_last_four")
