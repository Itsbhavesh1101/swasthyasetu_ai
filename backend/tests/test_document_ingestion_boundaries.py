"""P11-A runtime, I/O, persistence, and clinical-boundary evidence."""

import ast
from pathlib import Path

from app.main import app
from app.modules.documents.classification import ClassificationDisposition, classify_synthetic
from app.modules.documents.registry import ProcessorDisposition, build_synthetic_processor_registry

ROOT = Path(__file__).parents[1]


def test_no_document_runtime_route_registration_or_public_surface() -> None:
    assert all("documents" not in path for path in app.openapi()["paths"])
    assert "documents" not in app.state.module_registry.module_ids
    assert not (ROOT / "app/modules/documents/public.py").exists()
    assert not (ROOT / "app/modules/documents/application.py").exists()
    assert not (ROOT / "app/modules/documents/infrastructure.py").exists()


def test_domain_and_ingestion_imports_have_no_io_runtime_or_clinical_dependency() -> None:
    forbidden = {
        "asyncio",
        "hashlib",
        "httpx",
        "pathlib",
        "requests",
        "socket",
        "sqlalchemy",
        "subprocess",
        "app.adapters",
        "app.events",
        "app.jobs",
        "app.modules.patients",
        "app.modules.safety",
        "app.shared.storage",
    }
    for name in ("domain.py", "ingestion.py"):
        tree = ast.parse((ROOT / "app/modules/documents" / name).read_text(encoding="utf-8"))
        imports = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imports |= {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        }
        assert not any(
            any(value == item or value.startswith(f"{item}.") for item in forbidden)
            for value in imports
        )


def test_new_callables_have_no_file_byte_path_url_or_filename_parameters() -> None:
    forbidden = {"bytes", "data", "file", "filename", "mime", "path", "stream", "url", "object_key"}
    for name in ("domain.py", "ingestion.py"):
        tree = ast.parse((ROOT / "app/modules/documents" / name).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                parameters = {
                    arg.arg
                    for arg in (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs)
                }
                assert parameters.isdisjoint(forbidden)
            assert not isinstance(node, ast.AsyncFunctionDef)


def test_no_document_orm_migration_feature_flag_or_worker_binding() -> None:
    migrations = ROOT.parent / "migrations/versions"
    assert not any("document" in path.name.lower() for path in migrations.glob("*.py"))
    app_source = "\n".join(
        path.read_text(encoding="utf-8") for path in (ROOT / "app").rglob("*.py")
    )
    assert "build_documents_registration" not in app_source
    assert "documents.enabled" not in app_source
    assert "DocumentRecord" not in app_source


def test_p11c_registry_remains_inert_and_p11b_mock_remains_test_only() -> None:
    registry = build_synthetic_processor_registry()
    assert all(
        item.disposition is ProcessorDisposition.NOOP_ABSTAIN for item in registry.descriptors
    )
    production = "\n".join(
        path.read_text(encoding="utf-8") for path in (ROOT / "app").rglob("*.py")
    )
    assert "MockOCRAdapter" not in production
    assert "ocr_support" not in production
    assert ClassificationDisposition.SELECTED.value == "SELECTED"
    assert callable(classify_synthetic)


def test_patient_documents_ui_remains_honestly_unavailable() -> None:
    page = (ROOT.parent / "apps/patient-web/app/documents/page.tsx").read_text(encoding="utf-8")
    assert "unavailable" in page.casefold() or "not available" in page.casefold()
    assert 'input type="file"' not in page.casefold()
