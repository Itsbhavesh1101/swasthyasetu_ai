from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType

import pytest


def _load_launcher() -> ModuleType:
    path = Path(__file__).resolve().parents[2] / "scripts" / "demo.py"
    spec = importlib.util.spec_from_file_location("swasthyasetu_demo_launcher", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_plan_is_deterministic_loopback_only_and_non_mutating() -> None:
    launcher = _load_launcher()

    first = launcher.build_plan()
    second = launcher.build_plan()

    assert first == second
    assert first["urls"] == {
        "backend": "http://127.0.0.1:8000",
        "patient": "http://127.0.0.1:3100",
    }
    assert first["compose_project"] == "swasthyasetu-local"
    assert first["database_reset"] is False
    assert first["synthetic_only"] is True
    assert not launcher.RUNTIME_FILE.exists()


def test_state_loader_rejects_wrong_repository_and_malformed_processes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    launcher = _load_launcher()
    state_file = tmp_path / "runtime.json"
    monkeypatch.setattr(launcher, "RUNTIME_FILE", state_file)

    state_file.write_text(
        json.dumps({"repository": str(tmp_path), "processes": []}),
        encoding="utf-8",
    )
    with pytest.raises(launcher.DemoLauncherError, match="INVALID_RUNTIME_STATE"):
        launcher.load_runtime_state()

    state_file.write_text(
        json.dumps({"repository": str(launcher.ROOT), "processes": [{"pid": 0}]}),
        encoding="utf-8",
    )
    with pytest.raises(launcher.DemoLauncherError, match="INVALID_RUNTIME_STATE"):
        launcher.load_runtime_state()


def test_runtime_state_round_trip_is_atomic_and_minimal(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    launcher = _load_launcher()
    state_file = tmp_path / ".demo" / "runtime.json"
    monkeypatch.setattr(launcher, "RUNTIME_FILE", state_file)

    launcher.write_runtime_state([{"name": "patient", "pid": 101}])

    assert launcher.load_runtime_state() == {
        "repository": str(launcher.ROOT),
        "processes": [{"name": "patient", "pid": 101}],
    }
    assert not state_file.with_suffix(".tmp").exists()


def test_cli_plan_emits_canonical_json_without_mutation(capsys: pytest.CaptureFixture[str]) -> None:
    launcher = _load_launcher()

    assert launcher.main(["plan"]) == 0
    output = capsys.readouterr().out
    assert json.loads(output) == launcher.build_plan()
    assert output == json.dumps(launcher.build_plan(), indent=2, sort_keys=True) + "\n"
    assert not launcher.RUNTIME_FILE.exists()


def test_windows_corepack_command_uses_cmd_call_without_shell_interpolation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    launcher = _load_launcher()
    monkeypatch.setattr(launcher.os, "name", "nt")
    monkeypatch.setattr(
        launcher, "_require_command", lambda name: "C:/Program Files/node/corepack.cmd"
    )
    monkeypatch.setenv("COMSPEC", "C:/Windows/System32/cmd.exe")

    assert launcher._corepack_command("install", "--frozen-lockfile") == [
        "C:/Windows/System32/cmd.exe",
        "/d",
        "/s",
        "/c",
        "call",
        "C:/Program Files/node/corepack.cmd",
        "pnpm",
        "install",
        "--frozen-lockfile",
    ]


def test_status_uses_database_aware_backend_readiness(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    launcher = _load_launcher()
    checked: list[str] = []

    def available(url: str) -> bool:
        checked.append(url)
        return True

    monkeypatch.setattr(launcher, "_url_available", available)
    monkeypatch.setattr(launcher, "RUNTIME_FILE", Path("missing-runtime-state.json"))

    assert launcher.status() == {
        "runtime_state_present": False,
        "services": {"backend": True, "patient": True},
    }
    assert checked == [
        "http://127.0.0.1:8000/health/ready",
        "http://127.0.0.1:3100",
    ]


def test_local_configuration_is_created_once_without_overwriting(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    launcher = _load_launcher()
    example = tmp_path / ".env.example"
    local = tmp_path / ".env"
    example.write_text("SAFE=example\n", encoding="utf-8")
    monkeypatch.setattr(launcher, "EXAMPLE_ENV", example)
    monkeypatch.setattr(launcher, "LOCAL_ENV", local)

    launcher.prepare_local_configuration()
    assert local.read_text(encoding="utf-8") == "SAFE=example\n"

    local.write_text("SAFE=custom\n", encoding="utf-8")
    launcher.prepare_local_configuration()
    assert local.read_text(encoding="utf-8") == "SAFE=custom\n"
