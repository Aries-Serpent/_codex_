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

import argparse  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import sqlite3  # noqa: E402

from codex.logging.structured_logger import logger

try:
    from codex.db.sqlite_patch import auto_enable_from_env as _codex_sqlite_auto

    _codex_sqlite_auto()
except (IOError, OSError) as e:
    error_type = type(e).__name__
    logger.debug("Exception: <ERROR_TYPE>")
    logger.warning("Exception: <ERROR_TYPE>", exc_info=True)
import sys  # noqa: E402
from datetime import datetime  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Any, Optional  # noqa: E402

try:  # pragma: no cover - optional rich dependency
    from rich.console import Console
    from rich.table import Table
except (ImportError, AttributeError):  # pragma: no cover - fallback
    Console = None  # type: ignore[misc,assignment]
    Table = None  # type: ignore[misc,assignment]

from .config import DEFAULT_LOG_DB  # noqa: E402
from .db_utils import (  # noqa: E402
    infer_columns,
    infer_probable_table,
    open_db,
    resolve_db_path,
)


class LogQueryEngine:
    """Wrapper class for querying session logs."""

    def search(self, query: str, role: str | None = None) -> list[dict[str, Any]]:
        """Search through conversation transcripts.

        Args:
            query: Search query text
            role: Optional role filter

        Returns:
            List of matching log entries as dicts
        """
        from codex.logging.db_manager import db_manager

        # Ensure database is initialized
        db_manager.init_schema()

        # Use DBManager to get connection
        with db_manager.connection() as conn:
            conn.row_factory = sqlite3.Row

            # Use session_events table (existing schema)
            log_table = "session_events"

            # Build query - use 'ts' instead of 'timestamp'
            sql = f"SELECT * FROM {log_table} WHERE message LIKE ? "  # nosec B608
            params: list[Any] = [f"%{query}%"]

            if role:
                sql += "AND role = ? "
                params.append(role)

            sql += "ORDER BY ts DESC LIMIT 100"

            cursor = conn.execute(sql, params)
            rows = cursor.fetchall()

            # Convert to dicts and map 'ts' to 'timestamp' for compatibility
            results = []
            for row in rows:
                result = dict(row)
                # Map ts to timestamp for consistency
                if "ts" in result:
                    result["timestamp"] = result["ts"]
                results.append(result)

            return results


def parse_when(s: str) -> datetime:
    """Parse ISO-8601 timestamps supporting Z/offset/naive."""
    if not isinstance(s, str):
        raise TypeError("parse_when expects str")
    s2 = s.strip()
    if s2.endswith("Z"):
        s2 = s2[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(s2)
    except (IOError, OSError) as exc:  # pragma: no cover - simple validation
        raise ValueError(
            f"Invalid datetime: {s}. Use ISO 8601 (e.g., 2025-08-18T09:00:00 or 2025-08-18)."
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
    mapcol: dict[str, Optional[str]],
    session_id: Optional[str],
    role: Optional[str],
    after: Optional[str],
    before: Optional[str],
    order: str,
    limit: Optional[int],
    offset: Optional[int],
) -> tuple[str, list[Any]]:
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
    sql = f"SELECT {select} FROM {table}"  # nosec B608
    where: list[str] = []
    params: list[Any] = []
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


def _print_rich(rows: list[sqlite3.Row], mapcol: dict[str, Optional[str]], show_meta: bool) -> None:
    ts = mapcol["timestamp"]
    role = mapcol["role"]
    message = mapcol["message"]
    if not ts or not role or not message:
        raise ValueError("Required columns missing")
    sid = mapcol.get("session_id")
    if Console is None or Table is None:  # pragma: no cover - fallback
        logger.info(format_text(rows, mapcol, show_meta))
        return
    table = Table(show_header=True, header_style="bold")
    table.add_column("timestamp")
    table.add_column("role")
    if sid:
        table.add_column("session_id")
    table.add_column("message")
    meta_col = mapcol.get("metadata") if show_meta else None
    if meta_col:
        table.add_column("meta")
    for r in rows:
        row = [str(r[ts]), str(r[role])]
        if sid:
            row.append(str(r[sid]))
        row.append(str(r[message]))
        if meta_col:
            row.append(str(r[meta_col]))
        table.add_row(*row)
    Console().print(table)


def format_text(rows: list[sqlite3.Row], mapcol: dict[str, Optional[str]], show_meta: bool) -> str:
    """Plain-text fallback used by legacy scripts/tests."""
    ts = mapcol["timestamp"]
    role = mapcol["role"]
    message = mapcol["message"]
    if not ts or not role or not message:
        raise ValueError("Required columns missing")
    sid = mapcol.get("session_id")
    lines = []
    meta_col = mapcol.get("metadata") if show_meta else None
    for r in rows:
        t = r[ts]
        rr = r[role]
        c = r[message]
        sid_part = ""
        if sid:
            value = r[sid]
            if value is not None:
                sid_part = f" [{value}]"
        meta_part = ""
        if meta_col:
            value = r[meta_col]
            if value is not None:
                meta_part = f" | {value}"
        lines.append(f"{t} ({rr}){sid_part}: {c}{meta_part}")
    return "\n".join(lines)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Query transcripts from session_events.")
    parser.add_argument(
        "--db",
        default=os.environ.get("CODEX_LOG_DB_PATH")
        or os.environ.get("CODEX_DB_PATH")
        or str(DEFAULT_LOG_DB),
        help=(
            f"Path to SQLite DB (default: env CODEX_LOG_DB_PATH/CODEX_DB_PATH or {DEFAULT_LOG_DB})"
        ),
    )
    parser.add_argument("--session-id", help="Filter by session_id")
    parser.add_argument("--role", help="Filter by role (e.g., user, assistant, system, tool)")
    parser.add_argument("--after", help="Start time (ISO 8601 or YYYY-MM-DD)")
    parser.add_argument("--before", help="End time (ISO 8601 or YYYY-MM-DD)")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--show-meta", action="store_true", help="Include meta column in output")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--offset", type=int)
    parser.add_argument("--order", choices=["asc", "desc"], default="asc")
    parser.add_argument("--tail", type=int, help="Show latest N rows")
    args = parser.parse_args(argv)

    try:
        if args.after:
            args.after = parse_when(args.after).replace(microsecond=0).isoformat()
        if args.before:
            args.before = parse_when(args.before).replace(microsecond=0).isoformat()
        if args.tail is not None:
            args.limit = args.tail
            args.order = "desc"
            args.offset = None
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
            if args.tail is not None:
                rows.reverse()
            if args.format == "json":
                logger.info(json.dumps([dict(r) for r in rows], ensure_ascii=False, indent=2))
            else:
                _print_rich(rows, mapcol, args.show_meta)
        return 0
    except (ValueError, SystemExit) as exc:
        type(exc).__name__
        logger.debug("Exception: <ERROR_TYPE>")
        logger.exception("Failed to query session logs.")
        return 2
    except (IOError, OSError) as exc:  # pragma: no cover - top-level guard
        type(exc).__name__
        logger.error("Unexpected error: <ERROR_TYPE>")
        return 1


if __name__ == "__main__":  # pragma: no cover - CLI entry
    session_ctx: Optional[Any]
    try:
        from .session_hooks import session as session_ctx
    except (ImportError, AttributeError):  # pragma: no cover - helper optional
        session_ctx = None
    if session_ctx:
        with session_ctx(sys.argv):
            raise SystemExit(main())
    raise SystemExit(main())
