"""P7 clinical-intake boundary and runtime non-registration guards."""

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
    forbidden_prefixes = (
        "app.modules.patients.infrastructure",
        "app.modules.encounters.infrastructure",
        "app.modules.sessions.infrastructure",
        "app.modules.consent.infrastructure",
        "app.modules.ai",
        "app.modules.ai_gateway",
        "fastapi",
        "httpx",
        "requests",
        "socket",
        "urllib",
    )
    for path in MODULE_ROOT.glob("*.py"):
        assert not any(
            imported == prefix or imported.startswith(f"{prefix}.")
            for imported in _imports(path)
            for prefix in forbidden_prefixes
        ), path


def test_clinical_intake_has_no_application_or_api_layer() -> None:
    assert not (MODULE_ROOT / "application.py").exists()
    assert not (MODULE_ROOT / "api.py").exists()


def test_pure_engine_has_no_clock_random_or_identifier_generation_calls() -> None:
    forbidden_calls = {
        "OpaqueId.new",
        "datetime.now",
        "random",
        "random.random",
        "utc_now",
        "uuid4",
    }
    for filename in ("engine.py", "history.py", "pack_validation.py", "rules.py"):
        path = MODULE_ROOT / filename
        tree = ast.parse(path.read_text(encoding="utf-8"))
        calls: set[str] = set()
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if isinstance(node.func, ast.Name):
                calls.add(node.func.id)
            elif isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                calls.add(f"{node.func.value.id}.{node.func.attr}")
        assert calls.isdisjoint(forbidden_calls), path


def test_pure_engine_has_no_io_or_environment_imports() -> None:
    forbidden_prefixes = (
        "aiohttp",
        "asyncpg",
        "http",
        "httpx",
        "os",
        "pathlib",
        "requests",
        "socket",
        "sqlalchemy",
        "subprocess",
        "urllib",
    )
    for filename in ("engine.py", "history.py", "pack_validation.py", "rules.py"):
        path = MODULE_ROOT / filename
        assert not any(
            imported == prefix or imported.startswith(f"{prefix}.")
            for imported in _imports(path)
            for prefix in forbidden_prefixes
        ), path


def test_default_application_does_not_register_clinical_intake() -> None:
    application = create_app(Settings(environment=Environment.TEST, _env_file=None))
    assert "clinical_intake" not in application.state.module_registry.module_ids
