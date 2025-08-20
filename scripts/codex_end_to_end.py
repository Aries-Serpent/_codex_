#!/usr/bin/env python3
"""Minimal end-to-end logging demonstration.

This script simulates a small chat session. It writes start, user, assistant
and end events via ``conversation_logger`` and then queries the transcript using
the ``query_logs`` CLI. The script exits non-zero if any step fails.
"""

from __future__ import annotations

import subprocess
import sys
import uuid
from pathlib import Path

from src.codex.logging import conversation_logger as cl


def _log_and_query(session_id: str, db: Path) -> str:
    """Log a short exchange and return the query_logs output."""
    cl.start_session(session_id, db_path=str(db))
    cl.log_message(session_id, "user", "hello", db_path=str(db))
    cl.log_message(session_id, "assistant", "hi there", db_path=str(db))
    cl.end_session(session_id, db_path=str(db))

    cmd = [
        sys.executable,
        "-m",
        "codex.logging.query_logs",
        "--db",
        str(db),
        "--session-id",
        session_id,
        "--format",
        "text",
    ]
    cp = subprocess.run(cmd, capture_output=True, text=True)
    if cp.returncode != 0:
        raise RuntimeError(cp.stderr)
    return cp.stdout


def main() -> int:
    session_id = f"demo-{uuid.uuid4()}"
    db = Path(".codex") / "session_logs.db"
    try:
        output = _log_and_query(session_id, db)
    except Exception as exc:  # pragma: no cover - CLI demo
        sys.stderr.write(f"{exc}\n")
        return 1
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
