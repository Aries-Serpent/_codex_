"""Run security scanners in offline mode and persist artefacts."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Iterable

SCANS: dict[str, list[str]] = {
    "bandit": ["bandit", "-r", "src", "-f", "json"],
    "detect_secrets": ["detect-secrets", "scan", "--all-files"],
    "safety": ["safety", "check", "--full-report", "--json"],
}

ARTIFACT_ROOT = Path("artifacts/security")


def _run(cmd: Iterable[str]) -> dict[str, object]:
    try:
        proc = subprocess.run(list(cmd), capture_output=True, text=True, check=False)
    except FileNotFoundError as exc:
        return {"status": "missing", "error": repr(exc)}
    return {
        "status": "ok" if proc.returncode == 0 else "failed",
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def main() -> int:
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    summary: dict[str, object] = {}
    for name, cmd in SCANS.items():
        result = _run(cmd)
        summary[name] = result["status"]
        (ARTIFACT_ROOT / f"{name}.json").write_text(
            json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
        )
    (ARTIFACT_ROOT / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry
    sys.exit(main())
