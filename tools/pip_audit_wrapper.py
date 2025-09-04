#!/usr/bin/env python3
from __future__ import annotations

import socket
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".cache" / "pip-audit"


def have_network(host="pypi.org", port=443, timeout=2) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def main():
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
    if not have_network() and not any(CACHE.iterdir()):
        print("[pip-audit] offline & empty cache -> skipping gracefully.")
        return 0
    return subprocess.call(args)


if __name__ == "__main__":
    raise SystemExit(main())
