"""Pre-push gate that runs a fast local test target."""

from __future__ import annotations

import importlib.util
import os
import shlex
import shutil
import subprocess
import sys
from typing import Iterable, Sequence

os.environ.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")

def _pytest_disable_args() -> list[str]:
    try:
        import pytest  # type: ignore

        version = getattr(pytest, "__version__", "")
        parts = [int(part) for part in version.split(".") if part.isdigit()][:2]
        if len(parts) >= 2:
            major, minor = parts[0], parts[1]
            if major > 8 or (major == 8 and minor >= 4):
                return ["--disable-plugin-autoload"]
        elif parts:
            if parts[0] >= 9:
                return ["--disable-plugin-autoload"]
    except Exception:
        pass
    return []


DEFAULT_NOX_CMD = [
    "nox",
    "-s",
    "tests",
    "--",
    "--maxfail=1",
    "-q",
    *_pytest_disable_args(),
]

DEFAULT_PYTEST_CMD = ["pytest", "-q", "--maxfail=1", *_pytest_disable_args()]

OPTIONAL_PYTESTS: tuple[tuple[str, ...], ...] = (
    ("tests/cli/test_metrics_ingest.py",),
    ("tests/cli/test_metrics_validate_tail_badge.py",),
)


def _pytest_available() -> bool:
    try:
        return importlib.util.find_spec("pytest") is not None
    except Exception:
        return False


def _run_optional_pytests(env: dict[str, str]) -> None:
    if not _pytest_available():
        return

    for args in _expand_optional_commands(OPTIONAL_PYTESTS):
        print(f"[pre-push] optional pytest: {' '.join(args)}")
        try:
            proc = subprocess.run(args, env=env)
        except OSError as exc:
            print(
                f"[pre-push] optional pytest failed to run ({exc}); ignoring",
                file=sys.stderr,
            )
            continue
        if proc.returncode != 0:
            print(
                f"[pre-push] optional pytest failed (ignored): {' '.join(args)}",
                file=sys.stderr,
            )


def _expand_optional_commands(entries: Iterable[tuple[str, ...]]) -> Iterable[list[str]]:
    for entry in entries:
        yield [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            *_pytest_disable_args(),
            *entry,
        ]


def _choose_command() -> Sequence[str] | None:
    override = os.environ.get("CODEX_PREPUSH_CMD")
    if override:
        return shlex.split(override)
    if shutil.which("nox"):
        return DEFAULT_NOX_CMD
    if shutil.which("pytest"):
        return DEFAULT_PYTEST_CMD
    return None


def main(argv: list[str]) -> int:
    if os.environ.get("CODEX_PREPUSH_SKIP", "0") == "1":
        print("[pre-push] CODEX_PREPUSH_SKIP=1 -> skipping fast test gate")
        return 0

    cmd = _choose_command()
    if not cmd:
        print(
            "[pre-push] no test runner found (install nox or pytest, or set CODEX_PREPUSH_CMD)",
            file=sys.stderr,
        )
        return 1

    env = os.environ.copy()
    env.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")

    _run_optional_pytests(env)

    print(f"[pre-push] running: {' '.join(cmd)}")
    proc = subprocess.run(cmd, env=env)
    if proc.returncode != 0:
        print(
            "[pre-push] tests failed; set CODEX_PREPUSH_SKIP=1 to bypass temporarily",
            file=sys.stderr,
        )
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
