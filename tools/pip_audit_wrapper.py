#!/usr/bin/env python3
from __future__ import annotations

import socket
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".cache" / "pip-audit"


def _have_net() -> bool:
    try:
        with socket.create_connection(("pypi.org", 443), timeout=2):
            return True
    except OSError:
        return False


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
    if not _have_net() and not any(CACHE.iterdir()):
        print("[pip-audit] offline & no cache → skipping (non-fatal).")
        return 0
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
