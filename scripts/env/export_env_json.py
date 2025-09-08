#!/usr/bin/env python3
"""Dump environment summary to a JSON file (default: env.json)."""

import json
import platform
import subprocess
import sys
from pathlib import Path

from codex_ml.monitoring.codex_logging import _codex_sample_system


def _git_commit() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return None


def main() -> None:
    info = _codex_sample_system()
    info["platform"] = platform.platform()
    info["python"] = sys.version.split()[0]
    commit = _git_commit()
    if commit:
        info["git_commit"] = commit
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("env.json")
    path.write_text(json.dumps(info, indent=2), encoding="utf-8")
    print(path)


if __name__ == "__main__":
    main()
