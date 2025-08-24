"""
CLI viewer for session-scoped logs stored in SQLite.

Purpose:
    Render session events (chronological) as text or JSON with optional filters.

Usage:
    python -m codex.logging.viewer --session-id <ID> [--db path/to.db]
      [--format json|text] [--level INFO --contains token]
      [--since 2025-01-01 --until 2025-12-31] [--limit 200] [--table logs]

Environment:
    CODEX_LOG_DB_PATH   Override default DB path (defaults to .codex/session_logs.db).
    CODEX_SQLITE_POOL   If "1", prefer a pooled/shared connection for reduced overhead.

Examples:
    export CODEX_LOG_DB_PATH=".codex/session_logs.db"
    export CODEX_SQLITE_POOL=1
    python -m codex.logging.viewer --session-id S123 --format text --limit 100
    python -m codex.logging.viewer --session-id S123 --format json --since 2025-01-01

Notes:
    The README documents log viewing and exporting; flags here mirror that flow.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys

try:
    from codex.db.sqlite_patch import auto_enable_from_env as _codex_sqlite_auto
except ImportError:
    _codex_sqlite_auto = None
else:
    try:  # pragma: no cover - best effort
        _codex_sqlite_auto()
    except Exception as exc:  # pragma: no cover
        print(f"SQLite patch disabled: {exc}", file=sys.stderr)
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:  # pragma: no cover - allow running standalone
    from .config import DEFAULT_LOG_DB
except Exception:  # pragma: no cover - fallback for direct execution
    DEFAULT_LOG_DB = Path(".codex/session_logs.db")

from .db_utils import get_columns, list_tables, resolve_db_path

CANDIDATE_TS = ["ts", "timestamp", "time", "created_at", "logged_at"]
CANDIDATE_SID = ["session_id", "session", "sid", "context_id"]
CANDIDATE_MSG = ["message", "msg", "text", "detail"]
CANDIDATE_LVL = ["level", "lvl", "severity", "log_level"]


def _validate_table_name(value: str | None) -> str | None:
    if value is None:
        return value
    if re.fullmatch(r"[A-Za-z0-9_]+", value):
        return value
    msg = (
        f"Invalid table name: '{value}'. "
        "Only letters, digits, and underscore are allowed."
    )
    raise argparse.ArgumentTypeError(msg)


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Session Logging (SQLite) viewer")
    parser.add_argument(
        "--session-id", required=True, help="Session identifier to filter"
    )
    parser.add_argument(
        "--db",
        default=os.getenv("CODEX_LOG_DB_PATH"),
        help=("Path to SQLite database (default: env CODEX_LOG_DB_PATH or autodetect)"),
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="text",
        help="Output format",
    )
    parser.add_argument("--level", action="append", help="Filter by level (repeatable)")
    parser.add_argument(
        "--contains", help="Substring filter on message (case-insensitive)"
    )
    parser.add_argument("--since", help="ISO date/time lower bound (inclusive)")
    parser.add_argument("--until", help="ISO date/time upper bound (inclusive)")
    parser.add_argument("--limit", type=int, help="Max rows to return")
    parser.add_argument(
        "--table",
        type=_validate_table_name,
        help="Explicit table name (skip inference)",
    )
    return parser.parse_args(argv)


def autodetect_db(root: Path) -> Optional[Path]:
    """Return the first database found under ``root``.

    The search is intentionally shallow for performance: we only inspect the
    repository root and the top-level ``.codex`` and ``data`` directories. Once
    a matching file is located the search stops immediately.
    """
    # Explicit common locations checked first
    candidates = [
        root / DEFAULT_LOG_DB,
        root / "data" / "logs.sqlite",
        root / "data" / "logs.db",
        root / "logs.db",
    ]
    for c in candidates:
        if c.exists():
            return c

    # Non-recursive scan of known top-level directories
    for base in (root / ".codex", root / "data", root):
        if base.exists():
            for pattern in ("*.db", "*.sqlite"):
                for p in base.glob(pattern):
                    if p.is_file():
                        return p
    return None


def connect_db(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def infer_schema(
    conn: sqlite3.Connection, explicit_table: Optional[str] = None
) -> Dict[str, Optional[str]]:
    candidates = [explicit_table] if explicit_table else list_tables(conn)
    for table in candidates:
        if not table:
            continue
        columns = [col.lower() for col in get_columns(conn, table)]

        def pick(options: List[str]) -> Optional[str]:
            for option in options:
                if option in columns:
                    return option
            return None

        ts = pick(CANDIDATE_TS)
        sid = pick(CANDIDATE_SID)
        msg = pick(CANDIDATE_MSG)
        lvl = pick(CANDIDATE_LVL)
        if sid and ts and msg:
            return {"table": table, "sid": sid, "ts": ts, "msg": msg, "lvl": lvl}
    raise RuntimeError(
        "No suitable table found (need at least session_id, timestamp, "
        "message columns)."
    )


def parse_iso(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value).isoformat(sep=" ", timespec="seconds")
    except ValueError:
        return value


def build_query(
    schema: Dict[str, Optional[str]],
    level: Optional[List[str]],
    contains: Optional[str],
    since: Optional[str],
    until: Optional[str],
    limit: Optional[int],
) -> Tuple[str, List[Any]]:
    table = schema["table"]
    sid_col = schema["sid"]
    ts_col = schema["ts"]
    msg_col = schema["msg"]
    lvl_col = schema.get("lvl")
    if not all([table, sid_col, ts_col, msg_col]):
        raise ValueError("Schema must define table, sid, ts, and msg columns")
    identifiers = [table, sid_col, ts_col, msg_col]
    if not all(re.fullmatch(r"[A-Za-z0-9_]+", i) for i in identifiers):
        raise ValueError("Invalid characters in schema identifiers")
    where = [f"{sid_col} = ?"]
    args: List[Any] = []
    if level and lvl_col:
        placeholders = ",".join("?" for _ in level)
        where.append(f"{lvl_col} IN ({placeholders})")
        args.extend(level)
    if contains:
        where.append(f"LOWER({msg_col}) LIKE ?")
        args.append(f"%{contains.lower()}%")
    since_iso = parse_iso(since)
    until_iso = parse_iso(until)
    if since_iso:
        where.append(f"{ts_col} >= ?")
        args.append(since_iso)
    if until_iso:
        where.append(f"{ts_col} <= ?")
        args.append(until_iso)
    where_clause = " AND ".join(where)
    query = f"SELECT * FROM {table} WHERE {where_clause} ORDER BY {ts_col} ASC"  # nosec B608
    if limit:
        query += f" LIMIT {int(limit)}"
    args = [None] + args
    return query, args


def main(argv: Optional[List[str]] = None) -> int:
    ns = parse_args(argv)
    if ns.table and not re.fullmatch(r"[A-Za-z0-9_]+", ns.table):
        msg = (
            f"Invalid table name: '{ns.table}'. "
            "Only letters, digits, and underscore are allowed."
        )
        raise SystemExit(msg)
    root = Path.cwd()
    db_path = Path(resolve_db_path(ns.db)) if ns.db else autodetect_db(root)
    if not db_path:
        print(
            "ERROR: SQLite DB not found. Provide --db or place logs.db/logs.sqlite "
            "in repo.",
            file=sys.stderr,
        )
        return 2
    try:
        conn = connect_db(db_path)
        schema = infer_schema(conn, ns.table)
        query, args = build_query(
            schema, ns.level, ns.contains, ns.since, ns.until, ns.limit
        )
        args[0] = ns.session_id
        rows = conn.execute(query, args).fetchall()
        if ns.format == "json":
            print(json.dumps([dict(r) for r in rows], ensure_ascii=False, indent=2))
        else:
            for row in rows:
                d = dict(row)
                ts = d.get(schema["ts"], "")
                lvl = d.get(schema.get("lvl") or "", "")
                msg = d.get(schema["msg"], "")
                prefix = f"[{lvl}] " if lvl else ""
                print(f"{ts} {prefix}{msg}")
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
