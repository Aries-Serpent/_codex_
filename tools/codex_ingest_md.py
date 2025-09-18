#!/usr/bin/env python3
"""Ingest markdown logs into a SQLite data blob for Codex.

This script parses change_log.md and results.md files and inserts their contents
into the SQLite database defined by CODEX_DB or provided via --db.
"""
import argparse
import datetime
import os
import re
import sqlite3
from typing import Optional

DEFAULT_DB = os.environ.get("CODEX_DB", ".codex/codex.sqlite")


def iso_now() -> str:
    return datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z"


def ingest_change_log(md_path: str, db_path: str, branch: str) -> None:
    """Ingest entries from change_log.md into the database."""
    rx_header = re.compile(r"^##\s*(\d{4}-\d{2}-\d{2}[^\n]*)")
    with sqlite3.connect(db_path) as cx, open(md_path, "r", encoding="utf-8", errors="ignore") as f:
        cx.execute("PRAGMA journal_mode=WAL")
        ts: Optional[str] = None
        buf: list[str] = []

        def flush() -> None:
            nonlocal ts, buf
            if buf:
                summary = "\n".join(buf).strip()
                cx.execute(
                    "INSERT INTO change_log(ts, branch, path, author, action, summary, sha) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (ts or iso_now(), branch, None, None, None, summary, None),
                )
                ts = None
                buf = []

        for line in f:
            m = rx_header.match(line)
            if m:
                flush()
                ts = m.group(1).strip()
            else:
                buf.append(line.rstrip())
        flush()


def ingest_results(md_path: str, db_path: str) -> None:
    """Ingest entries from results.md into the database."""
    rx_task = re.compile(r"^##\s*TASK:\s*(.+)", re.IGNORECASE)
    rx_status = re.compile(r"^Status:\s*(\w+)", re.IGNORECASE)
    rx_metrics = re.compile(r"^Metrics:\s*(.+)", re.IGNORECASE)
    with sqlite3.connect(db_path) as cx, open(md_path, "r", encoding="utf-8", errors="ignore") as f:
        cx.execute("PRAGMA journal_mode=WAL")
        task: Optional[str] = None
        status: Optional[str] = None
        metrics: Optional[str] = None

        def flush() -> None:
            nonlocal task, status, metrics
            if task:
                cx.execute(
                    "INSERT INTO results(ts, task, status, metrics_json, artifacts) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (iso_now(), task, status, metrics, None),
                )
                task = None
                status = None
                metrics = None

        for line in f:
            m = rx_task.match(line)
            if m:
                flush()
                task = m.group(1).strip()
                continue
            m = rx_status.match(line)
            if m:
                status = m.group(1).strip()
                continue
            m = rx_metrics.match(line)
            if m:
                metrics = m.group(1).strip()
                continue
        flush()


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest Codex markdown logs into SQLite")
    parser.add_argument("--changes", help="Path to change_log.md")
    parser.add_argument("--results", help="Path to results.md")
    parser.add_argument("--branch", default="unknown", help="Branch name for change_log entries")
    parser.add_argument("--db", default=DEFAULT_DB, help="Path to SQLite DB")
    args = parser.parse_args()

    # ensure DB is initialized
    from codex_db import init_db  # type: ignore

    init_db(args.db)

    if args.changes:
        ingest_change_log(args.changes, args.db, args.branch)
    if args.results:
        ingest_results(args.results, args.db)


if __name__ == "__main__":
    main()
