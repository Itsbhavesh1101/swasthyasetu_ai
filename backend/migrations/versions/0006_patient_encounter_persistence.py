"""Add P5-B patient, encounter, clinical-fact, and projection persistence.

Revision ID: p5b_0006
Revises: p4c_0005
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "p5b_0006"
down_revision: str | Sequence[str] | None = "p4c_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create only the P5-B persistence model and staged session FK."""
    op.create_table(
        "patients",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("preferred_language", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status IN ('ACTIVE','INACTIVE','MERGED','DELETED_PENDING')",
            name=op.f("ck_patients_status_supported"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_patients")),
    )
    op.create_foreign_key(
        "fk_sessions_patient_id_patients",
        "sessions",
        "patients",
        ["patient_id"],
        ["id"],
    )
    op.create_table(
        "patient_demographics",
        sa.Column("patient_id", sa.Uuid(), nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("age_years", sa.Integer(), nullable=True),
        sa.Column("administrative_sex", sa.String(length=256), nullable=True),
        sa.Column("gender_identity", sa.String(length=256), nullable=True),
        sa.Column("pregnancy_status", sa.String(length=256), nullable=True),
        sa.Column("location_context", sa.String(length=256), nullable=True),
        sa.Column("demographics_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "age_years IS NULL OR age_years >= 0",
            name=op.f("ck_patient_demographics_age_years_non_negative"),
        ),
        sa.ForeignKeyConstraint(
            ["patient_id"], ["patients.id"], name="fk_patient_demographics_patient_id_patients"
        ),
        sa.PrimaryKeyConstraint("patient_id", name=op.f("pk_patient_demographics")),
    )
    op.create_table(
        "patient_identifiers",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("patient_id", sa.Uuid(), nullable=False),
        sa.Column("system", sa.String(length=128), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("use", sa.String(length=64), nullable=True),
        sa.Column("verified", sa.Boolean(), nullable=False),
        sa.Column("source", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["patient_id"], ["patients.id"], name="fk_patient_identifiers_patient_id_patients"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_patient_identifiers")),
    )
    op.create_index(
        "ix_patient_identifiers_system_value",
        "patient_identifiers",
        ["system", "value"],
        unique=False,
    )
    op.create_table(
        "encounters",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("patient_id", sa.Uuid(), nullable=True),
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("encounter_type", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("institution_id", sa.Uuid(), nullable=True),
        sa.Column("language_context", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.CheckConstraint(
            "(status = 'COMPLETED' AND completed_at IS NOT NULL) OR "
            "(status <> 'COMPLETED' AND completed_at IS NULL)",
            name=op.f("ck_encounters_completed_at_lifecycle"),
        ),
        sa.CheckConstraint(
            "encounter_type IN ('GENERAL_INTAKE','MENTAL_HEALTH','KIOSK_INTAKE',"
            "'CLINICIAN_REVIEW','DOCUMENT_REVIEW','RESEARCH_ONLY')",
            name=op.f("ck_encounters_encounter_type_supported"),
        ),
        sa.CheckConstraint(
            "status IN ('CREATED','IN_PROGRESS','AWAITING_REVIEW','COMPLETED',"
            "'ABANDONED','CANCELLED')",
            name=op.f("ck_encounters_status_supported"),
        ),
        sa.CheckConstraint("version > 0", name=op.f("ck_encounters_version_positive")),
        sa.ForeignKeyConstraint(
            ["created_by"], ["actors.id"], name=op.f("fk_encounters_created_by_actors")
        ),
        sa.ForeignKeyConstraint(
            ["patient_id"], ["patients.id"], name=op.f("fk_encounters_patient_id_patients")
        ),
        sa.ForeignKeyConstraint(
            ["session_id"], ["sessions.id"], name=op.f("fk_encounters_session_id_sessions")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_encounters")),
    )
    op.create_index("ix_encounters_institution_id", "encounters", ["institution_id"], unique=False)
    op.create_index("ix_encounters_patient_id", "encounters", ["patient_id"], unique=False)
    op.create_index("ix_encounters_session_id", "encounters", ["session_id"], unique=False)
    op.create_index(
        "ix_encounters_status_started_at", "encounters", ["status", "started_at"], unique=False
    )
    op.create_table(
        "clinical_facts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("patient_id", sa.Uuid(), nullable=True),
        sa.Column("encounter_id", sa.Uuid(), nullable=True),
        sa.Column("fact_type", sa.String(length=32), nullable=False),
        sa.Column("canonical_label", sa.Text(), nullable=False),
        sa.Column("normalized_code", sa.Text(), nullable=True),
        sa.Column("coding_system", sa.Text(), nullable=True),
        sa.Column("effective_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("verification_state", sa.String(length=32), nullable=False),
        sa.Column("structured_value", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("source_text", sa.Text(), nullable=True),
        sa.Column("superseded_by_fact_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "fact_type IN ('SYMPTOM','PROBLEM','MEDICATION','ALLERGY','PROCEDURE',"
            "'OBSERVATION','INVESTIGATION','FAMILY_HISTORY','PERSONAL_HISTORY',"
            "'REVIEW_OF_SYSTEMS')",
            name=op.f("ck_clinical_facts_fact_type_supported"),
        ),
        sa.CheckConstraint(
            "verification_state IN ('EXTRACTED','LOW_CONFIDENCE','NEEDS_CONFIRMATION',"
            "'PATIENT_CONFIRMED','CLINICIAN_CONFIRMED','REJECTED','SUPERSEDED')",
            name=op.f("ck_clinical_facts_verification_state_supported"),
        ),
        sa.CheckConstraint(
            "superseded_by_fact_id IS NULL OR superseded_by_fact_id <> id",
            name=op.f("ck_clinical_facts_not_self_superseded"),
        ),
        sa.ForeignKeyConstraint(
            ["encounter_id"],
            ["encounters.id"],
            name=op.f("fk_clinical_facts_encounter_id_encounters"),
        ),
        sa.ForeignKeyConstraint(
            ["patient_id"], ["patients.id"], name=op.f("fk_clinical_facts_patient_id_patients")
        ),
        sa.ForeignKeyConstraint(
            ["superseded_by_fact_id"],
            ["clinical_facts.id"],
            name="fk_clinical_facts_superseded_by_fact_id",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_clinical_facts")),
    )
    op.create_index(
        "ix_clinical_facts_effective_at", "clinical_facts", ["effective_at"], unique=False
    )
    op.create_index(
        "ix_clinical_facts_encounter_id", "clinical_facts", ["encounter_id"], unique=False
    )
    op.create_index("ix_clinical_facts_patient_id", "clinical_facts", ["patient_id"], unique=False)
    op.create_index(
        "ix_clinical_facts_patient_id_fact_type",
        "clinical_facts",
        ["patient_id", "fact_type"],
        unique=False,
    )
    op.create_index(
        "ix_clinical_facts_verification_state",
        "clinical_facts",
        ["verification_state"],
        unique=False,
    )
    op.create_table(
        "allergies",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("patient_id", sa.Uuid(), nullable=False),
        sa.Column("source_fact_id", sa.Uuid(), nullable=False),
        sa.Column("substance", sa.Text(), nullable=False),
        sa.Column("normalized_code", sa.Text(), nullable=True),
        sa.Column("reaction", sa.Text(), nullable=True),
        sa.Column("severity", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("verification_state", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "verification_state IN ('EXTRACTED','LOW_CONFIDENCE','NEEDS_CONFIRMATION',"
            "'PATIENT_CONFIRMED','CLINICIAN_CONFIRMED','REJECTED','SUPERSEDED')",
            name=op.f("ck_allergies_verification_state_supported"),
        ),
        sa.ForeignKeyConstraint(
            ["patient_id"], ["patients.id"], name=op.f("fk_allergies_patient_id_patients")
        ),
        sa.ForeignKeyConstraint(
            ["source_fact_id"],
            ["clinical_facts.id"],
            name=op.f("fk_allergies_source_fact_id_clinical_facts"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_allergies")),
    )
    op.create_table(
        "clinical_fact_provenance",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("fact_id", sa.Uuid(), nullable=False),
        sa.Column("source_type", sa.String(length=32), nullable=False),
        sa.Column("source_id", sa.Uuid(), nullable=True),
        sa.Column("source_ref", sa.Text(), nullable=True),
        sa.Column("extractor_type", sa.String(length=128), nullable=True),
        sa.Column("provider", sa.String(length=128), nullable=True),
        sa.Column("model_id", sa.String(length=128), nullable=True),
        sa.Column("model_version", sa.String(length=128), nullable=True),
        sa.Column("prompt_version", sa.String(length=128), nullable=True),
        sa.Column("schema_version", sa.String(length=128), nullable=True),
        sa.Column("confidence", sa.Numeric(), nullable=True),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.CheckConstraint(
            "source_type IN ('PATIENT_REPORT','CAREGIVER_REPORT','CLINICIAN','OCR',"
            "'DOCUMENT_AI','FHIR_IMPORT','ABDM_IMPORT','HIS_IMPORT','MODEL_INFERENCE',"
            "'ADMIN','SYSTEM')",
            name=op.f("ck_clinical_fact_provenance_source_type_supported"),
        ),
        sa.CheckConstraint(
            "confidence IS NULL OR (confidence >= 0 AND confidence <= 1)",
            name=op.f("ck_clinical_fact_provenance_confidence_range"),
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["actors.id"],
            name=op.f("fk_clinical_fact_provenance_created_by_actors"),
        ),
        sa.ForeignKeyConstraint(
            ["fact_id"],
            ["clinical_facts.id"],
            name=op.f("fk_clinical_fact_provenance_fact_id_clinical_facts"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_clinical_fact_provenance")),
    )
    op.create_index(
        "ix_clinical_fact_provenance_fact_id", "clinical_fact_provenance", ["fact_id"], unique=False
    )
    op.create_index(
        "ix_clinical_fact_provenance_model_id_model_version",
        "clinical_fact_provenance",
        ["model_id", "model_version"],
        unique=False,
    )
    op.create_index(
        "ix_clinical_fact_provenance_source_type_source_id",
        "clinical_fact_provenance",
        ["source_type", "source_id"],
        unique=False,
    )
    op.create_table(
        "medications",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("patient_id", sa.Uuid(), nullable=False),
        sa.Column("source_fact_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("normalized_code", sa.Text(), nullable=True),
        sa.Column("dose_value", sa.Numeric(), nullable=True),
        sa.Column("dose_unit", sa.Text(), nullable=True),
        sa.Column("route", sa.Text(), nullable=True),
        sa.Column("frequency", sa.Text(), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("verification_state", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status IN ('ACTIVE','HISTORICAL','STOPPED','UNKNOWN')",
            name=op.f("ck_medications_status_supported"),
        ),
        sa.CheckConstraint(
            "verification_state IN ('EXTRACTED','LOW_CONFIDENCE','NEEDS_CONFIRMATION',"
            "'PATIENT_CONFIRMED','CLINICIAN_CONFIRMED','REJECTED','SUPERSEDED')",
            name=op.f("ck_medications_verification_state_supported"),
        ),
        sa.ForeignKeyConstraint(
            ["patient_id"], ["patients.id"], name=op.f("fk_medications_patient_id_patients")
        ),
        sa.ForeignKeyConstraint(
            ["source_fact_id"],
            ["clinical_facts.id"],
            name=op.f("fk_medications_source_fact_id_clinical_facts"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_medications")),
    )
    op.create_table(
        "observations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("patient_id", sa.Uuid(), nullable=True),
        sa.Column("encounter_id", sa.Uuid(), nullable=True),
        sa.Column("source_fact_id", sa.Uuid(), nullable=False),
        sa.Column("observation_type", sa.Text(), nullable=False),
        sa.Column("value_numeric", sa.Numeric(), nullable=True),
        sa.Column("value_text", sa.Text(), nullable=True),
        sa.Column("unit", sa.Text(), nullable=True),
        sa.Column("normalized_value", sa.Numeric(), nullable=True),
        sa.Column("normalized_unit", sa.Text(), nullable=True),
        sa.Column("reference_low", sa.Numeric(), nullable=True),
        sa.Column("reference_high", sa.Numeric(), nullable=True),
        sa.Column("abnormal_flag", sa.String(length=128), nullable=True),
        sa.Column("effective_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("verification_state", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "verification_state IN ('EXTRACTED','LOW_CONFIDENCE','NEEDS_CONFIRMATION',"
            "'PATIENT_CONFIRMED','CLINICIAN_CONFIRMED','REJECTED','SUPERSEDED')",
            name=op.f("ck_observations_verification_state_supported"),
        ),
        sa.CheckConstraint(
            "value_numeric IS NOT NULL OR value_text IS NOT NULL",
            name=op.f("ck_observations_value_present"),
        ),
        sa.ForeignKeyConstraint(
            ["encounter_id"],
            ["encounters.id"],
            name=op.f("fk_observations_encounter_id_encounters"),
        ),
        sa.ForeignKeyConstraint(
            ["patient_id"], ["patients.id"], name=op.f("fk_observations_patient_id_patients")
        ),
        sa.ForeignKeyConstraint(
            ["source_fact_id"],
            ["clinical_facts.id"],
            name=op.f("fk_observations_source_fact_id_clinical_facts"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_observations")),
    )
    op.create_index(
        "ix_observations_patient_id_observation_type_effective_at",
        "observations",
        ["patient_id", "observation_type", "effective_at"],
        unique=False,
    )


def downgrade() -> None:
    """Restore the P4-C schema exactly."""
    op.drop_index(
        "ix_observations_patient_id_observation_type_effective_at", table_name="observations"
    )
    op.drop_table("observations")
    op.drop_table("medications")
    op.drop_index(
        "ix_clinical_fact_provenance_source_type_source_id", table_name="clinical_fact_provenance"
    )
    op.drop_index(
        "ix_clinical_fact_provenance_model_id_model_version", table_name="clinical_fact_provenance"
    )
    op.drop_index("ix_clinical_fact_provenance_fact_id", table_name="clinical_fact_provenance")
    op.drop_table("clinical_fact_provenance")
    op.drop_table("allergies")
    op.drop_index("ix_clinical_facts_verification_state", table_name="clinical_facts")
    op.drop_index("ix_clinical_facts_patient_id_fact_type", table_name="clinical_facts")
    op.drop_index("ix_clinical_facts_patient_id", table_name="clinical_facts")
    op.drop_index("ix_clinical_facts_encounter_id", table_name="clinical_facts")
    op.drop_index("ix_clinical_facts_effective_at", table_name="clinical_facts")
    op.drop_table("clinical_facts")
    op.drop_index("ix_encounters_status_started_at", table_name="encounters")
    op.drop_index("ix_encounters_session_id", table_name="encounters")
    op.drop_index("ix_encounters_patient_id", table_name="encounters")
    op.drop_index("ix_encounters_institution_id", table_name="encounters")
    op.drop_table("encounters")
    op.drop_index("ix_patient_identifiers_system_value", table_name="patient_identifiers")
    op.drop_table("patient_identifiers")
    op.drop_table("patient_demographics")
    op.drop_constraint("fk_sessions_patient_id_patients", "sessions", type_="foreignkey")
    op.drop_table("patients")
