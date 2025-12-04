"""Environment + security health-check CLI for _codex_.

This CLI is a small wrapper that orchestrates:

- Environment snapshot
- Dependency audit
- Secret scan stub

and prints a concise, human-readable summary. It is intended for local
pre-flight checks before running more complex sequences or sharing
artifacts with others.

Exit code:
- 0: Everything ran, no secret findings.
- 1: Tools succeeded but the secret scan reported one or more findings.
- >1: A sub-tool failed to run.
"""
from __future__ import annotations

import shlex
import subprocess
from pathlib import Path
from typing import Any, Dict


def _run(cmd: str, cwd: Path) -> int:
    proc = subprocess.run(shlex.split(cmd), cwd=str(cwd), check=False)
    return proc.returncode


def run_health_check(repo_root: Path) -> Dict[str, Any]:
    root = repo_root

    results: Dict[str, Any] = {
        "env_snapshot_rc": None,
        "dependency_audit_rc": None,
        "secret_scan_rc": None,
    }

    results["env_snapshot_rc"] = _run(
        "python tools/codex_env_snapshot.py", root
    )
    results["dependency_audit_rc"] = _run(
        "python tools/codex_dependency_audit.py", root
    )
    results["secret_scan_rc"] = _run(
        "python tools/codex_secret_scan_stub.py", root
    )

    return results


def main() -> int:
    root = Path(".").resolve()
    results = run_health_check(root)

    print("=== _codex_ Environment & Security Health Check ===")
    print(f"- env snapshot rc      : {results['env_snapshot_rc']}")
    print(f"- dependency audit rc  : {results['dependency_audit_rc']}")
    print(f"- secret scan rc       : {results['secret_scan_rc']}")

    if any(v not in (0, None) for v in results.values()):
        return 2

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
