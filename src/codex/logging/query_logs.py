#!/usr/bin/env python3
"""
codex.logging.query_logs: Query transcripts from a SQLite database.

Usage examples:
  python -m src.codex.logging.query_logs --help
  python -m src.codex.logging.query_logs --db .codex/session_logs.db --session-id S123 --role user --after 2025-01-01 --format json

Behavior:
- Auto-detects table and column names via PRAGMA introspection
- Accepts filters: session_id, role, after/before (ISO-8601), limit/offset, order
- Outputs 'text' (default) or 'json'

Environment:
- CODEX_LOG_DB_PATH (or CODEX_DB_PATH) may point to the SQLite file
  (default: .codex/session_logs.db)
"""
from __future__ import annotations
import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def parse_when(s: Optional[str]) -> Optional[str]:
    if not s:
        return None
    try:
        if len(s) == 10 and s[4] == "-" and s[7] == "-":
            return f"{s}T00:00:00"
        dt = datetime.fromisoformat(s)
        return dt.replace(microsecond=0).isoformat()
    except Exception as exc:  # pragma: no cover - simple validation
        raise SystemExit(
            f"Invalid datetime: {s}. Use ISO 8601 (e.g., 2025-08-18T09:00:00 or 2025-08-18)."
        ) from exc


LIKELY_MAP = {
    "timestamp": [
        "created_at",
        "timestamp",
        "ts",
        "event_time",
        "time",
        "date",
        "datetime",
    ],
    "role": ["role", "type", "speaker"],
    "content": ["content", "message", "text", "body", "value"],
    "session_id": ["session_id", "session", "conversation_id", "conv_id", "sid"],
    "id": ["id", "rowid", "event_id"],
    "metadata": ["metadata", "meta", "attrs", "json", "extra"],
}


def _resolve_db_path(path: str) -> str:
    """Return an existing path, checking `.db`/`.sqlite` variants."""
    p = Path(path)
    if p.exists():
        return str(p)
    alt = p.with_suffix(".sqlite" if p.suffix == ".db" else ".db")
    if alt.exists():
        return str(alt)
    return str(p)


def open_db(path: str) -> sqlite3.Connection:
    resolved = _resolve_db_path(path)
    if not os.path.exists(resolved):
        raise SystemExit(f"Database file not found: {resolved}")
    conn = sqlite3.connect(resolved)
    conn.row_factory = sqlite3.Row
    return conn


def resolve_table_and_columns(conn: sqlite3.Connection) -> Tuple[str, Dict[str, str]]:
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
        required = ["timestamp", "role", "content"]
        if all(k in mapping for k in required):
            return table, mapping
    raise SystemExit(f"No suitable table found. Tables inspected: {tables}")


def build_query(
    table: str,
    mapcol: Dict[str, str],
    session_id: Optional[str],
    role: Optional[str],
    after: Optional[str],
    before: Optional[str],
    order: str,
    limit: Optional[int],
    offset: Optional[int],
) -> Tuple[str, List[Any]]:
    cols = [
        mapcol.get("id", "NULL AS id"),
        mapcol["timestamp"],
        mapcol["role"],
        mapcol["content"],
        mapcol.get("session_id", "NULL AS session_id"),
        mapcol.get("metadata", "NULL AS metadata"),
    ]
    select = ", ".join(cols)
    sql = f"SELECT {select} FROM {table}"
    where: List[str] = []
    params: List[Any] = []
    if session_id and "session_id" in mapcol:
        where.append(f"{mapcol['session_id']} = ?")
        params.append(session_id)
    if role:
        where.append(f"{mapcol['role']} = ?")
        params.append(role)
    if after:
        where.append(f"{mapcol['timestamp']} >= ?")
        params.append(after)
    if before:
        where.append(f"{mapcol['timestamp']} <= ?")
        params.append(before)
    if where:
        sql += " WHERE " + " AND ".join(where)
    if order.lower() not in {"asc", "desc"}:
        order = "asc"
    sql += f" ORDER BY {mapcol['timestamp']} {order.upper()}"
    if limit is not None:
        sql += " LIMIT ?"
        params.append(int(limit))
    if offset is not None:
        sql += " OFFSET ?"
        params.append(int(offset))
    return sql, params


def format_text(rows: List[sqlite3.Row], mapcol: Dict[str, str]) -> str:
    ts = mapcol["timestamp"]
    role = mapcol["role"]
    content = mapcol["content"]
    sid = mapcol.get("session_id")
    lines = []
    for r in rows:
        t = r[ts]
        rr = r[role]
        c = r[content]
        sid_part = f" [{r[sid]}]" if sid and r[sid] is not None else ""
        lines.append(f"{t} ({rr}){sid_part}: {c}")
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Query transcripts from session_events."
    )
    parser.add_argument(
        "--db",
        default=os.environ.get("CODEX_LOG_DB_PATH")
        or os.environ.get("CODEX_DB_PATH")
        or ".codex/session_logs.db",
        help=(
            "Path to SQLite DB (default: env CODEX_LOG_DB_PATH/CODEX_DB_PATH or "
            ".codex/session_logs.db)"
        ),
    )
    parser.add_argument("--session-id", help="Filter by session_id")
    parser.add_argument(
        "--role", help="Filter by role (e.g., user, assistant, system, tool)"
    )
    parser.add_argument("--after", help="Start time (ISO 8601 or YYYY-MM-DD)")
    parser.add_argument("--before", help="End time (ISO 8601 or YYYY-MM-DD)")
    parser.add_argument(
        "--format", choices=["text", "json"], default="text", help="Output format"
    )
    parser.add_argument("--limit", type=int)
    parser.add_argument("--offset", type=int)
    parser.add_argument("--order", choices=["asc", "desc"], default="asc")
    args = parser.parse_args(argv)

    try:
        if args.after:
            args.after = parse_when(args.after)
        if args.before:
            args.before = parse_when(args.before)
        conn = open_db(args.db)
        with conn:
            table, mapcol = resolve_table_and_columns(conn)
            sql, params = build_query(
                table,
                mapcol,
                args.session_id,
                args.role,
                args.after,
                args.before,
                args.order,
                args.limit,
                args.offset,
            )
            rows = list(conn.execute(sql, params))
            if args.format == "json":
                print(json.dumps([dict(r) for r in rows], ensure_ascii=False, indent=2))
            else:
                print(format_text(rows, mapcol))
        return 0
    except SystemExit as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except Exception as exc:  # pragma: no cover - top-level guard
        print(f"Unexpected error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":  # pragma: no cover - CLI entry
    try:
        from src.codex.logging.session_hooks import session
    except Exception:  # pragma: no cover - helper optional
        session = None
    if session:
        with session(sys.argv):
            raise SystemExit(main())
    else:
        raise SystemExit(main())
