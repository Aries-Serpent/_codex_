#!/usr/bin/env python3
"""Workflow helper for querying session logs.

This script provides a minimal wrapper around ``codex.logging.session_query``
to demonstrate a workflow module with PEP 8 compliant imports.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

from codex.logging.session_query import main as session_query_main


def run_session_query(db: Path, session_id: str, out: Optional[Path] = None) -> int:
    """Execute the session query CLI and return its exit code."""
    argv = ["--db", str(db), "--session-id", session_id, "--format", "json"]
    if out is not None:
        argv.extend(["--out", str(out)])
    return session_query_main(argv)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run session query workflow",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=Path(".codex/session_logs.db"),
        help="Path to log database",
    )
    parser.add_argument(
        "--session-id",
        required=True,
        help="Session identifier to query",
    )
    parser.add_argument(
        "--out",
        type=Path,
        help="Optional file to write results",
    )
    ns = parser.parse_args()
    return run_session_query(ns.db, ns.session_id, ns.out)


if __name__ == "__main__":
    raise SystemExit(main())
