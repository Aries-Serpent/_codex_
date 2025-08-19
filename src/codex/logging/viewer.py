"""src/codex/logging/viewer.py — SQLite-backed session log viewer.

CLI:
  python -m src.codex.logging.viewer --session-id ABC123 [--db path/to.db] [--format json|text]
                                      [--level INFO --contains token --since 2025-01-01 --until 2025-12-31]
                                      [--limit 200] [--table logs]

Best-effort schema inference:
- Finds a table with columns like: session_id/session/ctx, ts/timestamp/time/created_at, message/msg, level/lvl.
- Orders chronologically by inferred timestamp column (ASC).
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

CANDIDATE_TS = ["ts", "timestamp", "time", "created_at", "logged_at"]
CANDIDATE_SID = ["session_id", "session", "sid", "context_id"]
CANDIDATE_MSG = ["message", "msg", "text", "detail"]
CANDIDATE_LVL = ["level", "lvl", "severity", "log_level"]


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Session Logging (SQLite) viewer"
    )
    parser.add_argument("--session-id", required=True, help="Session identifier to filter")
    parser.add_argument(
        "--db",
        default=os.getenv("CODEX_LOG_DB_PATH"),
        help=(
            "Path to SQLite database (default: env CODEX_LOG_DB_PATH or autodetect)"
        ),
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="text",
        help="Output format",
    )
    parser.add_argument("--level", action="append", help="Filter by level (repeatable)")
    parser.add_argument("--contains", help="Substring filter on message (case-insensitive)")
    parser.add_argument("--since", help="ISO date/time lower bound (inclusive)")
    parser.add_argument("--until", help="ISO date/time upper bound (inclusive)")
    parser.add_argument("--limit", type=int, help="Max rows to return")
    parser.add_argument("--table", help="Explicit table name (skip inference)")
    return parser.parse_args(argv)


def autodetect_db(root: Path) -> Optional[Path]:
    candidates = [
        root / "data" / "logs.sqlite",
        root / "data" / "logs.db",
        root / "logs.db",
        root / "var" / "logs.db",
    ]
    for p in root.rglob("*.db"):
        candidates.append(p)
    for p in root.rglob("*.sqlite"):
        candidates.append(p)
    seen: set[str] = set()
    for candidate in candidates:
        if candidate.exists() and candidate.is_file() and str(candidate) not in seen:
            seen.add(str(candidate))
            return candidate
    return None


def connect_db(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def list_tables(conn: sqlite3.Connection) -> List[str]:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    ).fetchall()
    return [row["name"] for row in rows]


def table_columns(conn: sqlite3.Connection, table: str) -> List[str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return [row["name"] for row in rows]


def infer_schema(conn: sqlite3.Connection, explicit_table: Optional[str] = None) -> Dict[str, str]:
    candidates = [explicit_table] if explicit_table else list_tables(conn)
    for table in candidates:
        if not table:
            continue
        columns = [col.lower() for col in table_columns(conn, table)]

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
        "No suitable table found (need at least session_id, timestamp, message columns)."
    )


def parse_iso(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value).isoformat(sep=" ", timespec="seconds")
    except Exception:
        return value


def build_query(
    schema: Dict[str, str],
    level: Optional[List[str]],
    contains: Optional[str],
    since: Optional[str],
    until: Optional[str],
    limit: Optional[int],
) -> Tuple[str, List[Any]]:
    table, sid_col, ts_col, msg_col, lvl_col = (
        schema["table"],
        schema["sid"],
        schema["ts"],
        schema["msg"],
        schema.get("lvl"),
    )
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
    query = f"SELECT * FROM {table} WHERE {where_clause} ORDER BY {ts_col} ASC"
    if limit:
        query += f" LIMIT {int(limit)}"
    args = [None] + args
    return query, args


def main(argv: Optional[List[str]] = None) -> int:
    ns = parse_args(argv)
    root = Path.cwd()
    db_path = Path(ns.db) if ns.db else autodetect_db(root)
    if not db_path:
        print(
            "ERROR: SQLite DB not found. Provide --db or place logs.db/logs.sqlite in repo.",
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

