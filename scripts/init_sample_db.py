#!/usr/bin/env python3
"""Initialize a sample `session_events` table for development.

This script creates a `session_events` table alongside existing Codex logging
usage. By default it uses `.codex/session_logs.db` but a custom path can be
provided via `--db-path`.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sqlite3
import time
from typing import Iterable, Tuple

DEFAULT_DB = pathlib.Path(".codex/session_logs.db")


def resolved_db_path(path: str | None) -> pathlib.Path:
    """Return the SQLite path, considering repo defaults."""
    if path:
        return pathlib.Path(path)
    # attempt to import default from src.codex.logging.config
    try:
        from src.codex.logging import config as logging_config  # type: ignore

        return pathlib.Path(logging_config.DEFAULT_LOG_DB)
    except Exception:
        return DEFAULT_DB


def ensure_parent(p: pathlib.Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)


def seed_rows(now: float) -> Iterable[Tuple[float, str, str, str, str]]:
    return [
        (now, "dev-session", "system", "init", json.dumps({"ok": True})),
        (
            now + 0.1,
            "dev-session",
            "user",
            "example_request",
            json.dumps({"q": "hello"}),
        ),
        (
            now + 0.2,
            "dev-session",
            "assistant",
            "example_reply",
            json.dumps({"a": "world"}),
        ),
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db-path", help="Path to SQLite DB")
    parser.add_argument(
        "--reset", action="store_true", help="Drop and recreate the table"
    )
    parser.add_argument("--seed", action="store_true", help="Insert sample rows")
    args = parser.parse_args()

    db_path = resolved_db_path(args.db_path)
    ensure_parent(db_path)

    con = sqlite3.connect(db_path)
    cur = con.cursor()

    if args.reset:
        cur.execute("DROP TABLE IF EXISTS session_events")

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS session_events(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts REAL NOT NULL,
            session_id TEXT NOT NULL,
            actor TEXT NOT NULL,
            event TEXT NOT NULL,
            data TEXT
        )
        """
    )

    inserted = 0
    if args.seed:
        rows = seed_rows(time.time())
        cur.executemany(
            "INSERT INTO session_events(ts, session_id, actor, event, data) VALUES(?,?,?,?,?)",
            rows,
        )
        inserted = cur.rowcount

    con.commit()

    # smoke check: read back one row if inserted
    cur.execute("SELECT COUNT(*) FROM session_events")
    count = cur.fetchone()[0]
    con.close()

    print(f"DB: {db_path} — session_events rows={count}; inserted={inserted}")


if __name__ == "__main__":
    main()
