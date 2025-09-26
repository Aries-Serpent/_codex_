#!/usr/bin/env python3
"""Automate Option A/B data-path verification steps.

Runs the snapshot builder and Parquet exporter, then prints a Datasette Lite URL
for manual inspection (Option C).
"""

from __future__ import annotations

import subprocess  # nosec B404 - commands run via validated wrapper
import sys
from pathlib import Path

from codex_ml.utils.subproc import run_argv

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    snap = ROOT / "tools" / "build_sqlite_snapshot.py"
    parq = ROOT / "tools" / "export_to_parquet.py"
    try:
        run_argv([sys.executable, str(snap)])
        run_argv([sys.executable, str(parq)])
    except subprocess.CalledProcessError as exc:
        print(f"Verification failed: {exc}")
        return 1
    db_path = ROOT / ".artifacts" / "snippets.db"
    url = f"https://lite.datasette.io/?url={db_path.as_uri()}"
    print("Datasette Lite URL:")
    print(url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
