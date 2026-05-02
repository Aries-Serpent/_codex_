"""Env & security health check CLI for `_codex_`.

Thin wrapper that calls:
- tools/codex_env_snapshot.py
- tools/codex_dependency_audit.py
- tools/codex_secret_scan_stub.py

It is intentionally best-effort; failures are printed but not raised.
"""

from __future__ import annotations

import argparse
import shlex
import subprocess
from pathlib import Path
from typing import Optional


def _run(cmd: str, cwd: Path) -> int:
    proc = subprocess.run(shlex.split(cmd), cwd=str(cwd), check=False)
    return proc.returncode


def run_health_check(repo_root: Path) -> dict[str, int]:
    cmds = {
        "env_snapshot_rc": "python tools/codex_env_snapshot.py --out codex_env_snapshot.json",
        "dependency_audit_rc": "python tools/codex_dependency_audit.py --repo-root . --json-out codex_dependency_report.json --md-out codex_dependency_report.md",  # noqa: E501
        "secret_scan_rc": "python tools/codex_secret_scan_stub.py --repo-root . --json-out codex_secret_scan_report.json --md-out codex_secret_scan_report.md",  # nosec B105  # noqa: E501
    }
    results: dict[str, int] = {}
    for key, cmd in cmds.items():
        results[key] = _run(cmd, repo_root)
    return results


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run env & security health checks for _codex_.")
    parser.add_argument(
        "--repo-root",
        type=str,
        default=".",
        help="Repository root (default: current directory).",
    )
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    results = run_health_check(root)
    return 0 if all(rc == 0 for rc in results.values()) else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
