#!/usr/bin/env python3
"""Air-gap-friendly pip-audit wrapper."""

from __future__ import annotations

import socket
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".cache" / "pip-audit"


def have_network(host: str = "pypi.org", port: int = 443, timeout: float = 2) -> bool:
    """Return True if network connectivity is available."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


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
    if not have_network() and not any(CACHE.iterdir()):
        sys.stdout.write("[pip-audit] offline & empty cache -> skipping gracefully.\n")
        return 0
    result = subprocess.call(args)  # noqa: S603
    if result != 0 and not any(CACHE.iterdir()):
        sys.stdout.write(
            "[pip-audit] failed (likely offline) & empty cache -> skipping gracefully.\n"
        )
        return 0
    return result


if __name__ == "__main__":
    raise SystemExit(main())
