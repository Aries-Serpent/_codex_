#!/usr/bin/env python
"""
Run pytest with coverage if plugin is available; degrade gracefully otherwise.
"""
from __future__ import annotations

import subprocess

__all__ = ["main"]


def has_pytest_cov() -> bool:
    try:
        out = subprocess.check_output(
            ["pytest", "--version", "--override-ini", "addopts=''"],
            text=True,
        )
        return "pytest-cov" in out
    except Exception:
        return False


def main() -> int:
    cmd = ["pytest", "-q", "--override-ini", "addopts=''"]
    if has_pytest_cov():
        cmd += ["--cov=src/codex_ml", "--cov-report=term", "--cov-fail-under=70"]
    else:
        print("[tests] pytest-cov not detected; running without coverage.")
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
