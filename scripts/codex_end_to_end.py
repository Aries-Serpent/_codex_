#!/usr/bin/env python3
"""Minimal end-to-end logging demonstration.

This script simulates a small chat session. It writes start, user, assistant
and end events via ``session_logger`` and then queries the transcript using the
``query_logs`` CLI. The script exits non-zero if any step fails.
"""

from __future__ import annotations

import subprocess
import sys
import uuid
from pathlib import Path

from src.codex.logging.session_logger import log_event


def main() -> int:
    session_id = f"demo-{uuid.uuid4()}"
    db = Path(".codex") / "session_logs.db"
    log_event(session_id, "system", "session_start", db_path=db)
    log_event(session_id, "user", "hello", db_path=db)
    log_event(session_id, "assistant", "hi there", db_path=db)
    log_event(session_id, "system", "session_end", db_path=db)

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
        sys.stderr.write(cp.stderr)
        return cp.returncode
    print(cp.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
