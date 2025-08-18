#!/usr/bin/env python3
"""
codex.logging.export: Dump session events from a SQLite DB.

Usage:
  python -m codex.logging.export SESSION_ID [--format json|text] [--db PATH]

Environment:
  CODEX_LOG_DB_PATH can override the default database path (codex_session_log.db).
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from pathlib import Path
from typing import Iterable, List, Dict, Any

_DEFAULT_DB = str(Path.cwd() / "codex_session_log.db")


def _db_path(override: str | None = None) -> str:
    """Resolve the SQLite path using env, override, or default."""
    return override or os.getenv("CODEX_LOG_DB_PATH") or _DEFAULT_DB


def _fetch_events(db_path: str, session_id: str) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.execute(
        "SELECT * FROM session_events WHERE session_id=? ORDER BY timestamp", (session_id,)
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def export_session(session_id: str, fmt: str = "json", db: str | None = None) -> str:
    """Return session events formatted as JSON or plain text."""
    db_path = _db_path(db)
    events = _fetch_events(db_path, session_id)
    if fmt == "json":
        return json.dumps(events, indent=2)
    lines: List[str] = []
    for e in events:
        ts = e.get("timestamp", "")
        role = e.get("role", "")
        msg = e.get("message", "")
        lines.append(f"{ts} ({role}): {msg}")
    return "\n".join(lines)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export session events from SQLite")
    parser.add_argument("session_id", help="Session identifier to export")
    parser.add_argument(
        "--format", choices=["json", "text"], default="json", help="Output format"
        )
    parser.add_argument("--db", help="Path to SQLite DB", default=None)
    args = parser.parse_args(list(argv) if argv is not None else None)
    print(export_session(args.session_id, args.format, args.db))
    return 0


if __name__ == "__main__":
    try:
        from codex.logging.session_hooks import session
    except Exception:  # pragma: no cover - helper optional
        session = None
    if session:
        with session(sys.argv):
            raise SystemExit(main())
    else:
        raise SystemExit(main())
