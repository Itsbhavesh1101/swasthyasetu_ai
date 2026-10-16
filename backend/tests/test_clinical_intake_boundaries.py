"""P7-A module boundary and runtime non-registration guards."""

import ast
from pathlib import Path

from app.config import Environment, Settings
from app.main import create_app

MODULE_ROOT = Path(__file__).parents[1] / "app" / "modules" / "clinical_intake"


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            names.add(node.module)
    return names


def test_clinical_intake_has_no_foreign_infrastructure_imports() -> None:
    forbidden = {
        "app.modules.patients.infrastructure",
        "app.modules.encounters.infrastructure",
        "app.modules.sessions.infrastructure",
        "app.modules.consent.infrastructure",
    }
    for path in MODULE_ROOT.glob("*.py"):
        assert _imports(path).isdisjoint(forbidden), path


def test_clinical_intake_has_no_application_or_api_layer() -> None:
    assert not (MODULE_ROOT / "application.py").exists()
    assert not (MODULE_ROOT / "api.py").exists()


def test_default_application_does_not_register_clinical_intake() -> None:
    application = create_app(Settings(environment=Environment.TEST, _env_file=None))
    assert "clinical_intake" not in application.state.module_registry.module_ids
