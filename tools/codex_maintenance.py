#!/usr/bin/env python3
"""tools/codex_maintenance.py
Run repository maintenance workflows in sequence and report results.

Steps executed:
- codex_repo_scout
- codex_precommit_bootstrap
- codex_logging_workflow
- codex_session_logging_workflow
- pytest
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TASKS: list[tuple[str, list[str]]] = [
    ("codex_repo_scout", [sys.executable, ".codex/codex_repo_scout.py"]),
    ("codex_precommit_bootstrap", [sys.executable, "tools/codex_precommit_bootstrap.py"]),
    ("codex_logging_workflow", [sys.executable, "tools/codex_logging_workflow.py"]),
    (
        "codex_session_logging_workflow",
        [sys.executable, "tools/codex_session_logging_workflow.py"],
    ),
    ("pytest", ["pytest"]),
]


def run_task(name: str, cmd: list[str]) -> int:
    """Execute *cmd* and return its exit code.

    Output is streamed directly to the console. Missing commands are treated as
    failures with exit code 127.
    """

    print(f"\n=== {name} ===")
    try:
        completed = subprocess.run(cmd, cwd=ROOT)
        return completed.returncode
    except FileNotFoundError:
        print(f"{name}: command not found", file=sys.stderr)
        return 127
    except Exception as exc:  # pragma: no cover - unexpected runtime errors
        print(f"{name}: {exc}", file=sys.stderr)
        return 1


def main() -> None:
    results: list[tuple[str, int]] = []
    for name, cmd in TASKS:
        rc = run_task(name, cmd)
        results.append((name, rc))

    print("\nSummary:")
    for name, rc in results:
        status = "success" if rc == 0 else f"failure (exit code {rc})"
        print(f"- {name}: {status}")

    if all(rc == 0 for _, rc in results):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
