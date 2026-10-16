"""Add P7-A clinical-intake persistence foundation.

Revision ID: p7a_0007
Revises: p5b_0006
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "p7a_0007"
down_revision: str | Sequence[str] | None = "p5b_0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "clinical_intakes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("encounter_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("chief_complaint", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("hpi", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "history_sections",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "missing_information",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "contradictions",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.CheckConstraint(
            "status IN ('IN_PROGRESS','COMPLETED','ABANDONED')",
            name=op.f("ck_clinical_intakes_status_supported"),
        ),
        sa.CheckConstraint("version > 0", name=op.f("ck_clinical_intakes_version_positive")),
        sa.CheckConstraint(
            "(status = 'COMPLETED' AND completed_at IS NOT NULL) OR "
            "(status <> 'COMPLETED' AND completed_at IS NULL)",
            name=op.f("ck_clinical_intakes_completed_at_lifecycle"),
        ),
        sa.CheckConstraint(
            "chief_complaint IS NULL OR jsonb_typeof(chief_complaint) = 'object'",
            name=op.f("ck_clinical_intakes_chief_complaint_json_object"),
        ),
        sa.CheckConstraint(
            "hpi IS NULL OR jsonb_typeof(hpi) = 'object'",
            name=op.f("ck_clinical_intakes_hpi_json_object"),
        ),
        sa.CheckConstraint(
            "jsonb_typeof(history_sections) = 'object'",
            name=op.f("ck_clinical_intakes_history_sections_json_object"),
        ),
        sa.CheckConstraint(
            "jsonb_typeof(missing_information) = 'array'",
            name=op.f("ck_clinical_intakes_missing_information_json_array"),
        ),
        sa.CheckConstraint(
            "jsonb_typeof(contradictions) = 'array'",
            name=op.f("ck_clinical_intakes_contradictions_json_array"),
        ),
        sa.ForeignKeyConstraint(
            ["encounter_id"],
            ["encounters.id"],
            name=op.f("fk_clinical_intakes_encounter_id_encounters"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_clinical_intakes")),
        sa.UniqueConstraint("encounter_id", name=op.f("uq_clinical_intakes_encounter_id")),
    )
    op.create_table(
        "intake_answers",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("intake_id", sa.Uuid(), nullable=False),
        sa.Column("question_id", sa.String(length=128), nullable=False),
        sa.Column("question_version", sa.String(length=64), nullable=False),
        sa.Column("answer", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("source_type", sa.String(length=32), nullable=False),
        sa.Column("answered_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "source_type IN ('PATIENT_TEXT','PATIENT_TOUCH','REUSED_HISTORY')",
            name=op.f("ck_intake_answers_source_type_supported"),
        ),
        sa.CheckConstraint(
            "jsonb_typeof(answer) = 'object'", name=op.f("ck_intake_answers_answer_json_object")
        ),
        sa.ForeignKeyConstraint(
            ["intake_id"],
            ["clinical_intakes.id"],
            name=op.f("fk_intake_answers_intake_id_clinical_intakes"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_intake_answers")),
    )
    op.create_index(
        "ix_intake_answers_intake_id_question_id",
        "intake_answers",
        ["intake_id", "question_id"],
        unique=False,
    )
    op.create_table(
        "questionnaire_instances",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("encounter_id", sa.Uuid(), nullable=False),
        sa.Column("questionnaire_id", sa.String(length=128), nullable=False),
        sa.Column("questionnaire_version", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("responses", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('ACTIVE','COMPLETED','ABANDONED')",
            name=op.f("ck_questionnaire_instances_status_supported"),
        ),
        sa.CheckConstraint(
            "jsonb_typeof(responses) = 'object'",
            name=op.f("ck_questionnaire_instances_responses_json_object"),
        ),
        sa.CheckConstraint(
            "(status = 'COMPLETED' AND completed_at IS NOT NULL) OR "
            "(status <> 'COMPLETED' AND completed_at IS NULL)",
            name=op.f("ck_questionnaire_instances_completed_at_lifecycle"),
        ),
        sa.ForeignKeyConstraint(
            ["encounter_id"],
            ["encounters.id"],
            name=op.f("fk_questionnaire_instances_encounter_id_encounters"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_questionnaire_instances")),
    )
    op.create_index(
        "ix_questionnaire_instances_encounter_questionnaire",
        "questionnaire_instances",
        ["encounter_id", "questionnaire_id", "questionnaire_version"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_questionnaire_instances_encounter_questionnaire", table_name="questionnaire_instances"
    )
    op.drop_table("questionnaire_instances")
    op.drop_index("ix_intake_answers_intake_id_question_id", table_name="intake_answers")
    op.drop_table("intake_answers")
    op.drop_table("clinical_intakes")
