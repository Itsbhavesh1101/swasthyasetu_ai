"""Cross-platform entry point for the P1 baseline quality gates."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"


def executable(name: str) -> str:
    """Resolve a required executable, including Windows command shims."""
    resolved = shutil.which(name)
    if resolved is None:
        raise RuntimeError(f"Required executable is unavailable: {name}")
    return resolved


def uv_prefix() -> list[str]:
    """Use a standalone uv when present, otherwise the current Python module."""
    resolved = shutil.which("uv")
    return [resolved] if resolved is not None else [sys.executable, "-m", "uv"]


def run(command: list[str], *, cwd: Path) -> None:
    """Print and execute one command, preserving output and exit status."""
    printable = subprocess.list2cmdline(command)
    print(f"\n> ({cwd}) {printable}", flush=True)
    environment = os.environ.copy()
    environment.setdefault("NEXT_TELEMETRY_DISABLED", "1")
    subprocess.run(command, cwd=cwd, env=environment, check=True)


def backend_gate() -> None:
    """Run the complete P1 backend quality gate."""
    uv = uv_prefix()
    commands = [
        [*uv, "lock", "--check"],
        [*uv, "sync", "--locked", "--dev"],
        [*uv, "run", "ruff", "check", "."],
        [*uv, "run", "ruff", "format", "--check", "."],
        [*uv, "run", "mypy"],
        [*uv, "run", "alembic", "-c", "alembic.ini", "heads"],
        [*uv, "run", "pytest"],
        [*uv, "run", "python", "-m", "compileall", "-q", "app", "tests"],
        [
            *uv,
            "run",
            "python",
            "-c",
            (
                "from app.main import app; from app.config import Settings; "
                "assert app.title; assert Settings().api_v1_prefix == '/api/v1'; "
                "print('import-smoke: PASS')"
            ),
        ],
    ]
    for command in commands:
        run(command, cwd=BACKEND)


def frontend_gate() -> None:
    """Run the complete P1 frontend quality gate except browser execution."""
    pnpm = executable("pnpm")
    commands = [
        [pnpm, "install", "--frozen-lockfile"],
        [pnpm, "frontend:format-check"],
        [pnpm, "frontend:lint"],
        [pnpm, "frontend:typecheck"],
        [pnpm, "frontend:test"],
        [pnpm, "frontend:build"],
        [pnpm, "e2e:list"],
    ]
    for command in commands:
        run(command, cwd=ROOT)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scope", choices=("backend", "frontend", "all"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.scope in {"backend", "all"}:
            backend_gate()
        if args.scope in {"frontend", "all"}:
            frontend_gate()
    except (RuntimeError, subprocess.CalledProcessError) as error:
        print(f"\nQuality gate failed: {error}", file=sys.stderr)
        return 1
    print(f"\nQuality gate passed: {args.scope}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
