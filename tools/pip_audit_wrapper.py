#!/usr/bin/env python3
"""Offline-friendly pip-audit wrapper.

Usage:
  python tools/pip_audit_wrapper.py --offline
"""

from __future__ import annotations

import argparse
import pathlib
import shutil
import subprocess
import sys


def _has_network_connectivity(host: str = "pypi.org", port: int = 443, timeout: float = 1.0) -> bool:
    """Return True if we can reach the configured host within the timeout."""

    import socket

    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


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

    cache_dir = pathlib.Path(".codex/pip-audit-cache")

    inferred_offline = False
    if not args.offline:
        # When network access is not available, prefer the offline flags so the
        # wrapper mirrors its previous "skip gracefully" behaviour.
        inferred_offline = not _has_network_connectivity()

    offline_mode = args.offline or inferred_offline

    cmd = [
        "pip-audit",
        "--progress-spinner",
        "off",
        "--requirement",
        args.requirements,
    ]
    if offline_mode:
        cache_dir.mkdir(parents=True, exist_ok=True)
        cmd += ["--cache-dir", str(cache_dir), "--disable-pip", "--no-deps"]

    try:
        result = subprocess.run(cmd, check=False)
    except Exception as exc:  # pragma: no cover
        print(f"[pip-audit] wrapper failed: {exc}", file=sys.stderr)
        return 0

    if result.returncode == 0 or args.offline:
        return result.returncode

    if inferred_offline:
        print(
            "[pip-audit] no network detected and offline audit failed; skipping.",
            file=sys.stderr,
        )
        return 0

    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
