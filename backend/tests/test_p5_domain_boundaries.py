"""P5-A architecture and scope regression tests."""

import ast
from pathlib import Path

from app.config import Settings
from app.main import create_app
from app.modules.encounters.infrastructure import EncounterRecord
from app.modules.patients.infrastructure import (
    AllergyRecordProjection,
    ClinicalFactProvenanceRecord,
    ClinicalFactRecord,
    MedicationRecordProjection,
    ObservationRecordProjection,
    PatientDemographicsRecord,
    PatientIdentifierRecord,
    PatientRecord,
)
from app.shared.persistence import Base

DOMAIN_FILES = (
    Path("app/modules/patients/domain.py"),
    Path("app/modules/patients/clinical.py"),
    Path("app/modules/encounters/domain.py"),
    Path("app/modules/provenance/domain.py"),
)
FORBIDDEN_FRAMEWORKS = {"fastapi", "sqlalchemy", "psycopg", "alembic", "pydantic"}


def test_p5_domain_files_are_framework_independent() -> None:
    imported_roots: set[str] = set()
    for path in DOMAIN_FILES:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_roots.update(alias.name.partition(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module is not None:
                imported_roots.add(node.module.partition(".")[0])

    assert imported_roots.isdisjoint(FORBIDDEN_FRAMEWORKS)


def test_p5c_registers_runtime_modules_and_capabilities() -> None:
    application = create_app(Settings(_env_file=None))

    assert application.state.module_registry.module_ids == (
        "clinical_intake",
        "consent",
        "encounters",
        "identity",
        "patients",
        "provenance",
        "sessions",
    )
    assert {
        "patients.create",
        "patients.read",
        "patients.fact.read",
        "patients.facts.list",
        "encounters.create",
        "encounters.read",
        "encounters.list",
        "encounters.transition",
        "provenance.read",
        "patients.timeline",
    }.issubset(application.state.capability_registry.registered_names)


def test_p5c_adds_only_governed_patient_and_encounter_routes() -> None:
    paths = create_app(Settings(_env_file=None)).openapi()["paths"]

    assert "/api/v1/patients" in paths
    assert "/api/v1/patients/{patient_id}/timeline" in paths
    assert "/api/v1/encounters/{encounter_id}/complete" in paths
    assert not any(path.startswith("/api/v1/clinical-facts") for path in paths)


def test_non_owning_modules_do_not_import_foreign_p5_infrastructure() -> None:
    forbidden = {
        "app.modules.patients.infrastructure",
        "app.modules.encounters.infrastructure",
    }
    for module in ("encounters", "provenance"):
        for path in Path(f"app/modules/{module}").glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            imports = {
                node.module
                for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom) and node.module is not None
            }
            if module == "encounters":
                assert "app.modules.patients.infrastructure" not in imports
            else:
                assert imports.isdisjoint(forbidden)


def test_metadata_preserves_p5b_and_adds_only_p7a_tables() -> None:
    assert PatientRecord.__tablename__ == "patients"
    assert PatientDemographicsRecord.__tablename__ == "patient_demographics"
    assert PatientIdentifierRecord.__tablename__ == "patient_identifiers"
    assert EncounterRecord.__tablename__ == "encounters"
    assert ClinicalFactRecord.__tablename__ == "clinical_facts"
    assert ClinicalFactProvenanceRecord.__tablename__ == "clinical_fact_provenance"
    assert MedicationRecordProjection.__tablename__ == "medications"
    assert AllergyRecordProjection.__tablename__ == "allergies"
    assert ObservationRecordProjection.__tablename__ == "observations"
    assert set(Base.metadata.tables) == {
        "actor_roles",
        "actors",
        "allergies",
        "clinical_fact_provenance",
        "clinical_facts",
        "consent_records",
        "encounters",
        "medications",
        "observations",
        "outbox_events",
        "patient_demographics",
        "patient_identifiers",
        "patients",
        "sessions",
        "clinical_intakes",
        "intake_answers",
        "questionnaire_instances",
    }
