"""Start, inspect, and stop the local SwasthyaSetu synthetic demonstration."""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import shutil
import signal
import socket
import subprocess
import time
import urllib.error
import urllib.request
from collections.abc import Sequence
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
COMPOSE_FILE = ROOT / "deployments" / "local" / "compose.yaml"
EXAMPLE_ENV = ROOT / "deployments" / "local" / ".env.example"
LOCAL_ENV = ROOT / "deployments" / "local" / ".env"
RUNTIME_DIR = ROOT / ".demo"
RUNTIME_FILE = RUNTIME_DIR / "runtime.json"
LOG_DIR = RUNTIME_DIR / "logs"

BACKEND_URL = "http://127.0.0.1:8000"
FRONTENDS = (
    ("patient", "@swasthyasetu/patient-web", 3100),
    ("clinician", "@swasthyasetu/clinician-web", 3101),
    ("admin", "@swasthyasetu/admin-web", 3102),
)
ALLOWED_PROCESS_NAMES = frozenset(name for name, _, _ in FRONTENDS)


class DemoLauncherError(RuntimeError):
    """Stable launcher failure without command output or sensitive values."""


def build_plan() -> dict[str, object]:
    """Return the immutable local demonstration topology without changing state."""

    return {
        "compose_project": "swasthyasetu-local",
        "database_reset": False,
        "synthetic_only": True,
        "urls": {
            "admin": "http://127.0.0.1:3102",
            "backend": BACKEND_URL,
            "clinician": "http://127.0.0.1:3101",
            "patient": "http://127.0.0.1:3100",
        },
    }


def _validate_processes(value: object) -> list[dict[str, object]]:
    if type(value) is not list:
        raise DemoLauncherError("INVALID_RUNTIME_STATE")
    processes: list[dict[str, object]] = []
    names: set[str] = set()
    pids: set[int] = set()
    for raw in value:
        if type(raw) is not dict or set(raw) != {"name", "pid"}:
            raise DemoLauncherError("INVALID_RUNTIME_STATE")
        name = raw.get("name")
        pid = raw.get("pid")
        if (
            type(name) is not str
            or name not in ALLOWED_PROCESS_NAMES
            or name in names
            or type(pid) is not int
            or pid <= 0
            or pid in pids
        ):
            raise DemoLauncherError("INVALID_RUNTIME_STATE")
        names.add(name)
        pids.add(pid)
        processes.append({"name": name, "pid": pid})
    return processes


def load_runtime_state() -> dict[str, object]:
    """Load only launcher-owned process identities for this exact repository."""

    try:
        raw = json.loads(RUNTIME_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        raise DemoLauncherError("INVALID_RUNTIME_STATE") from None
    if type(raw) is not dict or set(raw) != {"repository", "processes"}:
        raise DemoLauncherError("INVALID_RUNTIME_STATE")
    if raw.get("repository") != str(ROOT):
        raise DemoLauncherError("INVALID_RUNTIME_STATE")
    return {
        "repository": str(ROOT),
        "processes": _validate_processes(raw.get("processes")),
    }


def write_runtime_state(processes: list[dict[str, object]]) -> None:
    """Atomically persist the minimal process list needed by the stop command."""

    safe_processes = _validate_processes(processes)
    RUNTIME_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary = RUNTIME_FILE.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(
            {"repository": str(ROOT), "processes": safe_processes},
            separators=(",", ":"),
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    temporary.replace(RUNTIME_FILE)


def _require_command(name: str) -> str:
    value = shutil.which(name)
    if value is None:
        raise DemoLauncherError(f"MISSING_COMMAND:{name}")
    return value


def _run(command: Sequence[str], *, environment: dict[str, str] | None = None) -> None:
    completed = subprocess.run(
        list(command),
        cwd=ROOT,
        env=environment,
        check=False,
    )
    if completed.returncode != 0:
        raise DemoLauncherError("COMMAND_FAILED")


def _compose_environment_file() -> Path:
    return LOCAL_ENV if LOCAL_ENV.is_file() else EXAMPLE_ENV


def _compose_command(*arguments: str) -> list[str]:
    return [
        _require_command("docker"),
        "compose",
        "--env-file",
        str(_compose_environment_file()),
        "-f",
        str(COMPOSE_FILE),
        *arguments,
    ]


def _port_is_available(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as connection:
        try:
            connection.bind(("127.0.0.1", port))
        except OSError:
            return False
    return True


def _wait_for_url(url: str, *, timeout_seconds: float = 120.0) -> None:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:  # noqa: S310
                if 200 <= response.status < 400:
                    return
        except (OSError, urllib.error.URLError):
            time.sleep(1)
    raise DemoLauncherError("SERVICE_START_TIMEOUT")


def _url_available(url: str) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=1) as response:  # noqa: S310
            return 200 <= response.status < 400
    except (OSError, urllib.error.URLError):
        return False


def _corepack_command(*arguments: str) -> list[str]:
    corepack = _require_command("corepack")
    if os.name == "nt":
        return [
            os.environ.get("COMSPEC", "cmd.exe"),
            "/d",
            "/s",
            "/c",
            "call",
            corepack,
            "pnpm",
            *arguments,
        ]
    return [corepack, "pnpm", *arguments]


def _docker_is_ready(docker: str) -> bool:
    completed = subprocess.run(
        [docker, "info", "--format", "{{.ServerVersion}}"],
        cwd=ROOT,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return completed.returncode == 0


def _spawn_frontend(
    *,
    name: str,
    package: str,
    port: int,
    environment: dict[str, str],
) -> subprocess.Popen[bytes]:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / f"{name}.log"
    with log_path.open("ab") as log:
        options: dict[str, Any] = {
            "cwd": ROOT,
            "env": environment,
            "stdin": subprocess.DEVNULL,
            "stdout": log,
            "stderr": subprocess.STDOUT,
        }
        if os.name == "nt":
            options["creationflags"] = (
                subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW
            )
        else:
            options["start_new_session"] = True
        return subprocess.Popen(
            _corepack_command("--filter", package, "dev", "--port", str(port)),
            **options,
        )


def _terminate_pid(pid: int) -> None:
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(pid), "/T", "/F"],
            cwd=ROOT,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return
    try:
        os.killpg(pid, signal.SIGTERM)
    except ProcessLookupError:
        return


def _stop_frontends(processes: object) -> None:
    for process in reversed(_validate_processes(processes)):
        _terminate_pid(int(process["pid"]))


def start() -> dict[str, object]:
    """Start the local database, backend, and three frontend workspaces."""

    docker = _require_command("docker")
    _require_command("corepack")
    if not _docker_is_ready(docker):
        raise DemoLauncherError("DOCKER_DESKTOP_NOT_READY")
    if RUNTIME_FILE.exists():
        raise DemoLauncherError("DEMO_ALREADY_STARTED")
    occupied = [port for port in (8000, 3100, 3101, 3102) if not _port_is_available(port)]
    if occupied:
        raise DemoLauncherError("REQUIRED_PORT_UNAVAILABLE")

    if not LOCAL_ENV.exists():
        shutil.copyfile(EXAMPLE_ENV, LOCAL_ENV)
    processes: list[dict[str, object]] = []
    try:
        _run(_corepack_command("install", "--frozen-lockfile"))
        _run(_compose_command("config", "--quiet"))
        _run(_compose_command("up", "-d", "postgres"))
        _run(_compose_command("build", "backend"))
        _run(
            _compose_command(
                "run",
                "--rm",
                "backend",
                "alembic",
                "-c",
                "/app/alembic.ini",
                "upgrade",
                "head",
            )
        )
        _run(_compose_command("up", "-d", "backend"))
        _wait_for_url(f"{BACKEND_URL}/health/ready")
        environment = os.environ.copy()
        environment["SWASTHYASETU_BACKEND_URL"] = BACKEND_URL
        for name, package, port in FRONTENDS:
            process = _spawn_frontend(
                name=name,
                package=package,
                port=port,
                environment=environment,
            )
            processes.append({"name": name, "pid": process.pid})
            write_runtime_state(processes)
        for _, _, port in FRONTENDS:
            _wait_for_url(f"http://127.0.0.1:{port}")
    except Exception:
        _stop_frontends(processes)
        RUNTIME_FILE.unlink(missing_ok=True)
        with contextlib.suppress(DemoLauncherError):
            _run(_compose_command("down"))
        raise
    return {**build_plan(), "running": True}


def stop() -> dict[str, object]:
    """Stop only launcher-recorded frontends and the named local Compose project."""

    if RUNTIME_FILE.exists():
        state = load_runtime_state()
        _stop_frontends(state["processes"])
        RUNTIME_FILE.unlink(missing_ok=True)
    _run(_compose_command("down"))
    return {**build_plan(), "running": False}


def status() -> dict[str, object]:
    """Report reachability without mutating local services."""

    urls = build_plan()["urls"]
    assert isinstance(urls, dict)
    return {
        "runtime_state_present": RUNTIME_FILE.exists(),
        "services": {name: _url_available(str(url)) for name, url in sorted(urls.items())},
    }


def main(arguments: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("plan", "start", "status", "stop"))
    parsed = parser.parse_args(arguments)
    try:
        if parsed.command == "plan":
            result = build_plan()
        elif parsed.command == "start":
            result = start()
        elif parsed.command == "status":
            result = status()
        else:
            result = stop()
    except DemoLauncherError as error:
        parser.exit(1, f"{error}\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
