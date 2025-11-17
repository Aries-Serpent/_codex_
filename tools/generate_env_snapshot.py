"""Standalone environment snapshot generator for artifacts."""

from __future__ import annotations

import json
import os
import platform
import sys
from pathlib import Path


def capture_environment() -> dict:
    """Collect environment details for serialization."""
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

    # Capture CODEX_* environment variables only (not all env vars for privacy)
    codex_vars = {k: v for k, v in os.environ.items() if k.startswith("CODEX_")}
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
