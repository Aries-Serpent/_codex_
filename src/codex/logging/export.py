#!/usr/bin/env python3
"""codex.logging.export: Dump session events from a SQLite DB.

Usage:
  python -m src.codex.logging.export SESSION_ID [--format json|text] [--db PATH]

Environment:
  CODEX_LOG_DB_PATH (or CODEX_DB_PATH) can override the default database path
  (.codex/session_logs.db). If no path is provided, the tool searches for
  `.codex/session_logs.db` or `.codex/session_logs.sqlite` in the current working
  directory.
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from pathlib import Path
from typing import Iterable, List, Dict, Any, Tuple

_DEFAULT_DB = Path(".codex/session_logs.db")


def _db_path(override: str | None = None) -> str:
    """Resolve the SQLite path using env, override, or default.

    If no explicit path is provided, look for `.codex/session_logs.db` or
    `.codex/session_logs.sqlite` in the current working directory.
    """

    if override:
        return override
    env = os.getenv("CODEX_LOG_DB_PATH") or os.getenv("CODEX_DB_PATH")
    if env:
        return env
    for suffix in (".db", ".sqlite"):
        candidate = _DEFAULT_DB.with_suffix(suffix)
        if candidate.exists():
            return str(candidate)
    return str(_DEFAULT_DB)


LIKELY_MAP = {
    "timestamp": [
        "timestamp",
        "ts",
        "created_at",
        "time",
        "event_time",
        "date",
        "datetime",
    ],
    "session_id": ["session_id", "session", "sid", "conversation_id"],
    "role": ["role", "kind", "type", "speaker"],
    "message": ["message", "content", "text", "body", "value"],
}


def _resolve_schema(conn: sqlite3.Connection) -> Tuple[str, Dict[str, str]]:
    """Detect a suitable table and column mapping for session events."""

    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cur.fetchall()]
    for table in tables:
        cur = conn.execute(f"PRAGMA table_info({table})")
        cols = [r[1] for r in cur.fetchall()]
        mapping: Dict[str, str] = {}
        for want, candidates in LIKELY_MAP.items():
            for c in candidates:
                if c in cols:
                    mapping[want] = c
                    break
        if all(k in mapping for k in ("timestamp", "session_id", "message")):
            return table, mapping
    raise RuntimeError(f"No suitable events table found. Tables inspected: {tables}")


def _fetch_events(db_path: str, session_id: str) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        table, mapping = _resolve_schema(conn)
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
    try:
        from src.codex.logging.session_hooks import session
    except Exception:  # pragma: no cover - helper optional
        session = None
    if session:
        with session(sys.argv):
            raise SystemExit(main())
    else:
        raise SystemExit(main())

