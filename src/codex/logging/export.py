#!/usr/bin/env python3
"""codex.logging.export: Dump session events from a SQLite DB.

Usage:
  python -m codex.logging.export SESSION_ID [--format json|text] [--db PATH]

Environment:
  CODEX_LOG_DB_PATH (or CODEX_DB_PATH) can override the default database path
  (`codex.logging.config.DEFAULT_LOG_DB`). If no path is provided, the tool
  searches for `.codex/session_logs.db` or `.codex/session_logs.sqlite` in the
  current working directory.
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3

try:
    from codex.db.sqlite_patch import auto_enable_from_env as _codex_sqlite_auto

    _codex_sqlite_auto()
except Exception:
    pass
import sys
from typing import Any, Dict, Iterable, List, Optional

from .config import DEFAULT_LOG_DB
from .db_utils import infer_columns, infer_probable_table, open_db


def _db_path(override: str | None = None) -> str:
    """Resolve the SQLite path using env, override, or default.

    If no explicit path is provided, look for `DEFAULT_LOG_DB` or
    `DEFAULT_LOG_DB.with_suffix(".sqlite")` in the current working directory.
    """

    if override:
        return override
    env = os.getenv("CODEX_LOG_DB_PATH") or os.getenv("CODEX_DB_PATH")
    if env:
        return env
    for suffix in (".db", ".sqlite"):
        candidate = DEFAULT_LOG_DB.with_suffix(suffix)
        if candidate.exists():
            return str(candidate)
    return str(DEFAULT_LOG_DB)


def _fetch_events(db_path: str, session_id: str) -> List[Dict[str, Any]]:
    conn = open_db(db_path)
    conn.row_factory = sqlite3.Row
    try:
        table = infer_probable_table(conn)
        if table is None:
            raise RuntimeError("No suitable events table found.")
        mapping = infer_columns(conn, table)
        cols = [
            f"{mapping['timestamp']} AS timestamp",
            f"{mapping['session_id']} AS session_id",
            f"{mapping['message']} AS message",
        ]
        if "role" in mapping:
            cols.append(f"{mapping['role']} AS role")
        sql = (
            f"SELECT {', '.join(cols)} FROM {table} "
            f"WHERE {mapping['session_id']}=? ORDER BY {mapping['timestamp']}"
        )
        cur = conn.execute(sql, (session_id,))
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


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
    session_ctx: Optional[Any]
    try:
        from .session_hooks import session as session_ctx
    except Exception:  # pragma: no cover - helper optional
        session_ctx = None
    if session_ctx:
        with session_ctx(sys.argv):
            raise SystemExit(main())
    raise SystemExit(main())
