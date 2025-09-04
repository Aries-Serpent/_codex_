#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".cache" / "pip-audit"


def main() -> int:
    CACHE.mkdir(parents=True, exist_ok=True)
    return subprocess.call(
        [
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
    )


if __name__ == "__main__":
    raise SystemExit(main())
