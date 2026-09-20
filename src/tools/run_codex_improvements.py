#!/usr/bin/env python3
"""Utility script to automate Codex improvement phases."""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

ERROR_FILE = Path(".codex/error_capture_blocks.md")


def log_error(step: str, exc: Exception) -> None:
    ERROR_FILE.parent.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with ERROR_FILE.open("a", encoding="utf-8") as fh:
        fh.write(f"Question for ChatGPT {ts}:\nWhile performing [{step}], encountered: {exc}\n")


def run(cmd: list[str], step: str) -> int:
    try:
        return subprocess.call(cmd)
    except Exception as exc:  # noqa: BLE001
        log_error(step, exc)
        return 1


def phase_prep() -> int:
    req = Path("requirements/base.txt")
    if req.exists():
        return run([sys.executable, "-m", "pip", "install", "-r", str(req)], "prep")
    return 0


def phase_tests() -> int:
    return run(["nox", "-s", "tests"], "tests")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--phases",
        nargs="*",
        default=["prep", "tests"],
        help="Phases to run",
    )
    args = parser.parse_args()
    status = 0
    if "prep" in args.phases:
        status |= phase_prep()
    if "tests" in args.phases:
        status |= phase_tests()
    return status


if __name__ == "__main__":
    raise SystemExit(main())
