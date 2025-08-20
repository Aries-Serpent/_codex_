#!/usr/bin/env python3
"""
codex.logging.query_logs: Query transcripts from a SQLite database.

Usage examples:
  python -m codex.logging.query_logs --help
  python -m codex.logging.query_logs --db codex.logging.config.DEFAULT_LOG_DB \
      --session-id S123 --role user --after 2025-01-01 --format json

Behavior:
- Auto-detects table and column names via PRAGMA introspection
- Accepts filters: session_id, role, after/before (ISO-8601), limit/offset, order
- Outputs 'text' (default) or 'json'

Environment:
- CODEX_LOG_DB_PATH (or CODEX_DB_PATH) may point to the SQLite file
  (default: codex.logging.config.DEFAULT_LOG_DB)

Supported timestamp formats for `parse_when`:
  - Zulu/UTC:       2025-08-19T12:34:56Z
  - Offset-aware:   2025-08-19T12:34:56+00:00, 2025-08-19T07:34:56-05:00
  - Naive/local:    2025-08-19T12:34:56 (tzinfo=None)

Behavior:
  - Z/offset inputs produce **aware** datetime objects.
  - Naive inputs return **naive** datetime objects.
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
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .config import DEFAULT_LOG_DB
from .db_utils import infer_columns, infer_probable_table, open_db, resolve_db_path


def parse_when(s: str) -> datetime:
    """Parse ISO-8601 timestamps supporting Z/offset/naive."""
    if not isinstance(s, str):
        raise TypeError("parse_when expects str")
    s2 = s.strip()
    if s2.endswith("Z"):
        s2 = s2[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(s2)
    except Exception as exc:  # pragma: no cover - simple validation
        raise ValueError(
            "Invalid datetime: "
            f"{s}. Use ISO 8601 (e.g., 2025-08-18T09:00:00 or 2025-08-18)."
        ) from exc


def _resolve_db_path(path: str) -> str:
    """Return an existing path, checking `.db`/`.sqlite` variants."""
    p = Path(path)
    if p.exists():
        return str(resolve_db_path(p))
    alt = p.with_suffix(".sqlite" if p.suffix == ".db" else ".db")
    if alt.exists():
        return str(resolve_db_path(alt))
    return str(resolve_db_path(p))


def build_query(
    table: str,
    mapcol: Dict[str, Optional[str]],
    session_id: Optional[str],
    role: Optional[str],
    after: Optional[str],
    before: Optional[str],
    order: str,
    limit: Optional[int],
    offset: Optional[int],
) -> Tuple[str, List[Any]]:
    ts = mapcol["timestamp"]
    role_col = mapcol["role"]
    message_col = mapcol["message"]
    if not ts or not role_col or not message_col:
        raise ValueError("Required columns missing")
    cols = [
        mapcol.get("id") or "NULL AS id",
        ts,
        role_col,
        message_col,
        mapcol.get("session_id") or "NULL AS session_id",
        mapcol.get("metadata") or "NULL AS metadata",
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


def format_text(rows: List[sqlite3.Row], mapcol: Dict[str, Optional[str]]) -> str:
    ts = mapcol["timestamp"]
    role = mapcol["role"]
    content = mapcol["content"]
    if not ts or not role or not content:
        raise ValueError("Required columns missing")
    sid = mapcol.get("session_id")
    lines = []
    for r in rows:
        t = r[ts]
        rr = r[role]
        c = r[content]
        sid_part = ""
        if sid:
            value = r[sid]
            if value is not None:
                sid_part = f" [{value}]"
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
        or str(DEFAULT_LOG_DB),
        help=(
            "Path to SQLite DB (default: env CODEX_LOG_DB_PATH/CODEX_DB_PATH or "
            f"{DEFAULT_LOG_DB})"
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
            args.after = parse_when(args.after).replace(microsecond=0).isoformat()
        if args.before:
            args.before = parse_when(args.before).replace(microsecond=0).isoformat()
        conn = open_db(args.db)
        conn.row_factory = sqlite3.Row
        with conn:
            table = infer_probable_table(conn)
            if table is None:
                raise SystemExit("No suitable table found.")
            mapcol = infer_columns(conn, table)
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
    except (ValueError, SystemExit) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except Exception as exc:  # pragma: no cover - top-level guard
        print(f"Unexpected error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":  # pragma: no cover - CLI entry
    session_ctx: Optional[Any]
    try:
        from .session_hooks import session as session_ctx
    except Exception:  # pragma: no cover - helper optional
        session_ctx = None
    if session_ctx:
        with session_ctx(sys.argv):
            raise SystemExit(main())
    raise SystemExit(main())
