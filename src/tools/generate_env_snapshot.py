"""Standalone environment snapshot generator for artifacts."""

from __future__ import annotations

import json
import os
import platform
import sys
from pathlib import Path

_SENSITIVE_KEYS = {
    "CODEX_MASTER_KEY",
    "CODEX_BACKUP_KEY",
    "CODEX_RUNNER_TOKEN",
    "GITHUB_TOKEN",
    "GH_TOKEN",
    "TOKEN",
    "SECRET",
    "SECRET_KEY",
    "API_KEY",
    "PASSWORD",
}


def _redact_env_value(key: str, value: str) -> str:
    upper = key.upper()
    if upper in _SENSITIVE_KEYS or any(marker in upper for marker in ("TOKEN", "SECRET", "PASSWORD", "API_KEY")):
        return "[REDACTED]"
    return value


def capture_environment() -> dict:
    """Collect environment details for serialization.

    The serialized snapshot intentionally contains only the CODEX_* keys that the
    project explicitly supports; unrelated process environment data is excluded.
    """
    info = {
        "python_version": sys.version,
        "python_version_info": {
            "major": sys.version_info.major,
            "minor": sys.version_info.minor,
            "micro": sys.version_info.micro,
        },
        "python_implementation": platform.python_implementation(),
        "python_compiler": platform.python_compiler(),
        "platform": platform.platform(),
        "platform_system": platform.system(),
        "platform_release": platform.release(),
        "platform_machine": platform.machine(),
        "python_executable": sys.executable,
    }

    codex_vars = {
        key: _redact_env_value(key, value)
        for key, value in os.environ.items()
        if key.startswith("CODEX_")
    }
    if codex_vars:
        info["codex_env_vars"] = codex_vars
    return info


def main():
    """Generate environment snapshot to artifacts/env_snapshot.json."""
    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    out_path = artifacts_dir / "env_snapshot.json"
    snapshot = capture_environment()

    out_path.write_text(json.dumps(snapshot, indent=2, sort_keys=True))
    print(f"✓ Environment snapshot written to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
