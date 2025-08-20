#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Tuple

DEFAULT_RETENTION_DAYS = 30


def purge(
    days: int = DEFAULT_RETENTION_DAYS,
    dry_run: bool = False,
    log_dir: Path | None = None,
    db_path: Path | None = None,
) -> Tuple[int, int]:
    """Delete NDJSON files and session_events rows older than ``days``.

    Returns a tuple ``(files_deleted, rows_deleted)``.  In ``dry_run`` mode no
    deletions occur.
    """

    cutoff_dt = datetime.now() - timedelta(days=days)

    # Purge NDJSON files
    log_dir = log_dir or Path(os.getenv("CODEX_SESSION_LOG_DIR", ".codex/sessions"))
    files_deleted = 0
    if log_dir.is_dir():
        for path in log_dir.glob("*.ndjson"):
            mtime = datetime.fromtimestamp(path.stat().st_mtime)
            if mtime < cutoff_dt:
                if dry_run:
                    print(f"Would delete {path}")
                else:
                    path.unlink(missing_ok=True)
                    files_deleted += 1
    else:
        print(f"Log directory not found: {log_dir}")

    # Purge SQLite rows
    db_path = db_path or Path(
        os.getenv("CODEX_LOG_DB_PATH")
        or os.getenv("CODEX_DB_PATH", ".codex/session_logs.db")
    )
    rows_deleted = 0
    if db_path.exists():
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='session_events'"
            )
            if cur.fetchone():
                cutoff_ts = cutoff_dt.timestamp()
                cur = conn.execute(
                    "SELECT COUNT(*) FROM session_events WHERE ts < ?", (cutoff_ts,)
                )
                rows_deleted = cur.fetchone()[0]
                if dry_run:
                    print(f"Would delete {rows_deleted} rows from {db_path}")
                else:
                    conn.execute(
                        "DELETE FROM session_events WHERE ts < ?", (cutoff_ts,)
                    )
                    conn.commit()
                    conn.execute("VACUUM")
            else:
                print(f"Table 'session_events' not found in {db_path}")
        finally:
            conn.close()
    else:
        print(f"Database not found: {db_path}")

    if not dry_run:
        print(f"Deleted {files_deleted} files and {rows_deleted} rows")
    return files_deleted, rows_deleted


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Purge session logs older than the retention period"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=DEFAULT_RETENTION_DAYS,
        help="Retention period in days (default: 30)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without removing anything",
    )
    args = parser.parse_args()
    purge(days=args.days, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
