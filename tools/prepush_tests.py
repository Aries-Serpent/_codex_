"""Pre-push gate that runs a fast local test target."""

from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys
from typing import Sequence

os.environ.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")

DEFAULT_NOX_CMD = ["nox", "-s", "tests", "--", "--maxfail=1", "-q"]
DEFAULT_PYTEST_CMD = ["pytest", "-q", "--maxfail=1"]


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
