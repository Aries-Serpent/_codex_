#!/usr/bin/env python3
"""Offline-friendly pip-audit wrapper.

Usage:
  python tools/pip_audit_wrapper.py --offline
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline", action="store_true", help="Prefer offline/no-network mode.")
    parser.add_argument(
        "--requirements", default="requirements.txt", help="Requirements file to scan."
    )
    args = parser.parse_args(argv)

    if shutil.which("pip-audit") is None:
        print("[pip-audit] not installed; skipping (offline workflow).", file=sys.stderr)
        return 0

    cmd = [
        "pip-audit",
        "--progress-spinner",
        "off",
        "--requirement",
        args.requirements,
    ]
    if args.offline:
        cmd += ["--cache-dir", ".codex/pip-audit-cache", "--disable-pip", "--no-deps"]

    try:
        return subprocess.call(cmd)
    except Exception as exc:  # pragma: no cover
        print(f"[pip-audit] wrapper failed: {exc}", file=sys.stderr)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
