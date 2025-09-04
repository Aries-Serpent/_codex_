#!/usr/bin/env python3
"""Prewarm the pip-audit cache on a connected machine."""

from __future__ import annotations

import subprocess
from pathlib import Path

# ruff: noqa

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".cache" / "pip-audit"


def main() -> int:
    CACHE.mkdir(parents=True, exist_ok=True)
    cmd = [
        "pip-audit",
        "-r",
        "requirements.txt",
        "--cache-dir",
        str(CACHE),
        "--progress-spinner",
        "off",
        "--timeout",
        "15",
    ]
    print("[prewarm] running:", " ".join(cmd))
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
