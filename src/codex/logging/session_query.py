"""Session event query CLI."""

from __future__ import annotations

import argparse
import os
import sqlite3

try:
    from codex.db.sqlite_patch import auto_enable_from_env as _codex_sqlite_auto

    _codex_sqlite_auto()
except Exception:
    pass
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .config import DEFAULT_LOG_DB

DEFAULT_DB_CANDIDATES = [
    str(DEFAULT_LOG_DB),
    "codex_session_log.db",
    "data/codex.db",
    "codex.db",
]

TS_CANDIDATES = ["timestamp", "ts", "event_ts", "created_at", "time", "datetime"]
SID_CANDIDATES = ["session_id", "sid", "session", "conversation_id"]
ROLE_CANDIDATES = ["role", "type", "speaker", "kind"]
MSG_CANDIDATES = ["message", "content", "text", "body", "value"]


def _resolve_with_extension(path: str) -> str:
    """Return existing path, falling back between .db and .sqlite."""
    p = Path(path)
    if p.exists():
        return str(p)
    if p.suffix in {".db", ".sqlite"}:
        alt = p.with_suffix(".sqlite" if p.suffix == ".db" else ".db")
        if alt.exists():
            return str(alt)
    return str(p)


def resolve_db_path(cli_db: Optional[str]) -> str:
    """Resolve database path from CLI, environment, or known defaults.

    Lookup order:
    1. ``--db`` flag
    2. ``CODEX_DB_PATH`` or ``CODEX_LOG_DB_PATH`` environment variables
    3. First existing entry in ``DEFAULT_DB_CANDIDATES`` (search stops after the
       first hit and only inspects top-level ``.codex`` or ``data`` directories).
    """
    if cli_db:
        return cli_db
    env = os.getenv("CODEX_DB_PATH") or os.getenv("CODEX_LOG_DB_PATH")
    if env:
        return env
    for c in DEFAULT_DB_CANDIDATES:
        if os.path.exists(c):
            return c
    raise FileNotFoundError(
        "No database found. Provide --db or set CODEX_DB_PATH/CODEX_LOG_DB_PATH",
    )


def detect_schema(conn: sqlite3.Connection) -> Tuple[str, Dict[str, str]]:
    """Infer table and column names for timestamp/session/role/message."""
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cur.fetchall()]
    for table in tables:
        cur = conn.execute(f"PRAGMA table_info({table})")
        cols = [row[1] for row in cur.fetchall()]
        mapping: Dict[str, str] = {}
        for want, candidates in {
            "timestamp": TS_CANDIDATES,
            "session_id": SID_CANDIDATES,
            "role": ROLE_CANDIDATES,
            "message": MSG_CANDIDATES,
        }.items():
            for c in candidates:
                if c in cols:
                    mapping[want] = c
                    break
        if "timestamp" in mapping and "message" in mapping:
            return table, mapping
    raise RuntimeError(f"No suitable events table found. Tables: {tables}")


def fetch_rows(
    db_path: str,
    session_id: Optional[str],
    last_n: Optional[int],
    desc: bool,
) -> Tuple[List[sqlite3.Row], Dict[str, str]]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        table, cols = detect_schema(conn)
        ts_col = cols["timestamp"]
        sid_col = cols.get("session_id")
        order_clause = "DESC" if desc else "ASC"
        select_cols = [ts_col]
        if sid_col:
            select_cols.append(sid_col)
        if "role" in cols:
            select_cols.append(cols["role"])
        select_cols.append(cols["message"])
        sql = f"SELECT {', '.join(select_cols)} FROM {table}"
        params: List[object] = []
        if session_id:
            if not sid_col:
                raise RuntimeError(
                    "Session filtering requested but no session id column found"
                )
            sql += f" WHERE {sid_col}=?"
            params.append(session_id)
        sql += f" ORDER BY {ts_col} {order_clause}"
        if session_id is None and last_n is not None:
            sql += " LIMIT ?"
            params.append(last_n)
        cur = conn.cursor()
        rows = list(cur.execute(sql, params))
        if session_id is None and not desc:
            rows.reverse()
        return rows, cols
    finally:
        conn.close()


def print_rows(rows: List[sqlite3.Row], cols: Dict[str, str]) -> None:
    if not rows:
        print("(no rows)", file=sys.stderr)
        return
    header_keys = [
        k for k in ["timestamp", "session_id", "role", "message"] if k in cols
    ]
    print("\t".join(header_keys))
    for r in rows:
        print(
            "\t".join(
                "" if r[cols[k]] is None else str(r[cols[k]]) for k in header_keys
            )
        )


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Query session events from a SQLite database",
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
        rows, cols = fetch_rows(db, args.session_id, args.last, args.desc)
        print_rows(rows, cols)
        return 0
    except Exception as exc:  # pragma: no cover - top-level guard
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover - CLI entry
    session_ctx: Optional[Any]
    try:
        from src.codex.logging.session_hooks import (
            session as session_ctx,  # type: ignore
        )
    except Exception:  # pragma: no cover - optional helper
        session_ctx = None
    if session_ctx:
        with session_ctx(sys.argv):
            raise SystemExit(main())
    raise SystemExit(main())
