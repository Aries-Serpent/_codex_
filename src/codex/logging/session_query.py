"""Session event query CLI."""

from __future__ import annotations

import argparse
import os
import sqlite3
import sys
from typing import Iterable, List, Optional, Tuple

DEFAULT_DB_CANDIDATES = [
    ".codex/session_logs.db",
    "codex_session_log.db",
    "data/codex.db",
    "db/codex.db",
    "codex.db",
]

TS_CANDIDATES = ["timestamp", "ts", "event_ts", "created_at"]
SID_CANDIDATES = ["session_id", "sid", "session"]


def resolve_db_path(cli_db: Optional[str]) -> str:
    """Resolve database path from CLI, env, or common defaults."""
    if cli_db:
        return cli_db
    env = os.getenv("CODEX_DB_PATH") or os.getenv("CODEX_LOG_DB_PATH")
    if env:
        return env
    for c in DEFAULT_DB_CANDIDATES:
        if os.path.exists(c):
            return c
    raise FileNotFoundError(
        "No database found. Provide --db or set CODEX_DB_PATH/CODEX_LOG_DB_PATH"
    )


def detect_table_and_columns(conn: sqlite3.Connection) -> Tuple[str, str, Optional[str]]:
    """Return (table, timestamp_column, session_id_column)."""
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )
    tables = [r[0] for r in cur.fetchall()]
    table = None
    for candidate in ["session_events", "events"]:
        if candidate in tables:
            table = candidate
            break
    if table is None:
        for t in tables:
            if "event" in t.lower():
                table = t
                break
    if table is None:
        raise RuntimeError(f"No events table found. Tables: {tables}")

    cur = conn.execute(f"PRAGMA table_info({table})")
    cols = [row[1] for row in cur.fetchall()]
    ts_col = next((c for c in TS_CANDIDATES if c in cols), None)
    sid_col = next((c for c in SID_CANDIDATES if c in cols), None)
    if ts_col is None:
        raise RuntimeError(
            f"No timestamp column found in {table}. Looked for {TS_CANDIDATES}; have {cols}"
        )
    return table, ts_col, sid_col


def fetch_rows(
    db_path: str,
    session_id: Optional[str],
    last_n: Optional[int],
    desc: bool,
) -> List[sqlite3.Row]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        table, ts_col, sid_col = detect_table_and_columns(conn)
        cur = conn.cursor()
        if session_id:
            if not sid_col:
                raise RuntimeError("Session filtering requested but no session id column found")
            order = "DESC" if desc else "ASC"
            sql = f"SELECT * FROM {table} WHERE {sid_col}=? ORDER BY {ts_col} {order}"
            rows = list(cur.execute(sql, (session_id,)))
        else:
            order = "DESC"  # efficient retrieval of recent events
            sql = f"SELECT * FROM {table} ORDER BY {ts_col} {order}"
            if last_n is not None:
                sql += " LIMIT ?"
                rows = list(cur.execute(sql, (last_n,)))
            else:
                rows = list(cur.execute(sql))
            if not desc:
                rows.reverse()
        return rows
    finally:
        conn.close()


def print_rows(rows: List[sqlite3.Row]) -> None:
    if not rows:
        print("(no rows)", file=sys.stderr)
        return
    headers = rows[0].keys()
    print("\t".join(headers))
    for r in rows:
        print("\t".join("" if v is None else str(v) for v in r))


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Query session events from a SQLite database"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--session-id", help="Filter events by session id")
    group.add_argument("--last", type=int, metavar="N", help="Show last N events")
    parser.add_argument("--db", help="Path to SQLite database")
    parser.add_argument(
        "--desc",
        action="store_true",
        help="Sort output in descending order (default asc for session-id mode)",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    try:
        db = resolve_db_path(args.db)
        rows = fetch_rows(db, args.session_id, args.last, args.desc)
        print_rows(rows)
        return 0
    except Exception as exc:  # pragma: no cover - top-level guard
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover - CLI entry
    try:
        from src.codex.logging.session_hooks import session
    except Exception:  # pragma: no cover - optional helper
        session = None
    if session:
        with session(sys.argv):
            raise SystemExit(main())
    raise SystemExit(main())
