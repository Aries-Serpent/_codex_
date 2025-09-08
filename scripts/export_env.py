#!/usr/bin/env python3
"""Dump environment variables and version info in JSON."""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys

from codex_ml.monitoring.codex_logging import _codex_sample_system


def main() -> None:
    info = {
        "python": sys.version,
        "platform": platform.platform(),
        "env": dict(os.environ),
        "system": _codex_sample_system(),
    }
    try:
        info["git_commit"] = subprocess.check_output(
            [
                "git",
                "rev-parse",
                "HEAD",
            ],
            text=True,
        ).strip()
    except Exception:
        info["git_commit"] = None
    try:
        info["pip_freeze"] = subprocess.check_output(
            [sys.executable, "-m", "pip", "freeze"], text=True
        )
    except Exception:
        info["pip_freeze"] = ""
    print(json.dumps(info, indent=2))


if __name__ == "__main__":
    main()
