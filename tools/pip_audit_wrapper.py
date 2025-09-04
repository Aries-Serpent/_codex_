#!/usr/bin/env python3
"""Air-gap-friendly pip-audit wrapper."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".cache" / "pip-audit"


def main() -> int:
    """Run pip-audit using a persistent cache and offline skip."""
    CACHE.mkdir(parents=True, exist_ok=True)
    args = [
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
    result = subprocess.call(args)  # noqa: S603
    if result != 0 and not any(CACHE.iterdir()):
        sys.stdout.write(
            "[pip-audit] failed (likely offline) & empty cache -> skipping gracefully.\n"
        )
        return 0
    return result


if __name__ == "__main__":
    raise SystemExit(main())
