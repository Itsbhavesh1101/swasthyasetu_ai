"""Static contract tests for the patient health hub migration."""

from pathlib import Path

ROOT = Path(__file__).parents[1]
MIGRATION = ROOT / "migrations/versions/0008_patient_health_hub.py"


def test_patient_hub_revision_extends_the_single_existing_head() -> None:
    source = MIGRATION.read_text(encoding="utf-8")

    assert 'revision: str = "patient_hub_0008"' in source
    assert 'down_revision: str | Sequence[str] | None = "p7a_0007"' in source
    assert '"patient_accounts"' in source
    assert '"patient_documents"' in source


def test_patient_hub_schema_has_explicit_integrity_controls() -> None:
    source = MIGRATION.read_text(encoding="utf-8")

    required_names = {
        "ck_patient_accounts_status_supported",
        "ck_patient_documents_byte_size_positive",
        "ck_patient_documents_sha256_digest_valid",
        "fk_patient_accounts_actor_id_actors",
        "fk_patient_accounts_patient_id_patients",
        "fk_patient_documents_patient_id_patients",
        "ix_patient_accounts_email_normalized",
        "ix_patient_documents_patient_id_created_at",
        "uq_patient_accounts_actor_id",
        "uq_patient_accounts_patient_id",
        "uq_patient_documents_object_key",
    }

    assert required_names.issubset(set(source.split('"')))
    assert "LargeBinary" not in source
    assert "BYTEA" not in source


def test_patient_hub_downgrade_removes_only_its_two_tables() -> None:
    source = MIGRATION.read_text(encoding="utf-8")
    downgrade = source.split("def downgrade() -> None:", maxsplit=1)[1]

    assert downgrade.count("op.drop_table(") == 2
    assert 'op.drop_table("patient_documents")' in downgrade
    assert 'op.drop_table("patient_accounts")' in downgrade
