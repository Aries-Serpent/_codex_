#!/usr/bin/env python3
"""SQLite utilities for Codex logs.

Provides functions to initialize the log database and run arbitrary queries.
This module can be invoked directly via CLI.
"""
import argparse
import json
import os
import pathlib
import sqlite3
from typing import Optional

DEFAULT_DB = os.environ.get("CODEX_DB", ".codex/codex.sqlite")

SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS change_log(
  id INTEGER PRIMARY KEY,
  ts TEXT,
  branch TEXT,
  path TEXT,
  author TEXT,
  action TEXT,
  summary TEXT,
  sha TEXT
);
CREATE INDEX IF NOT EXISTS idx_change_ts ON change_log(ts);
CREATE INDEX IF NOT EXISTS idx_change_path ON change_log(path);

CREATE TABLE IF NOT EXISTS results(
  id INTEGER PRIMARY KEY,
  ts TEXT,
  task TEXT,
  status TEXT,
  metrics_json TEXT,
  artifacts TEXT
);
CREATE INDEX IF NOT EXISTS idx_results_ts ON results(ts);
CREATE INDEX IF NOT EXISTS idx_results_task ON results(task);
"""


def init_db(db_path: Optional[str] = None) -> None:
    """Initialize the SQLite database with the schema."""
    path = db_path or DEFAULT_DB
    # Ensure parent directory exists
    pathlib.Path(path).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as cx:
        cx.executescript(SCHEMA)


def run_query(sql: str, db_path: Optional[str] = None) -> None:
    """Run a SQL query against the specified database and print results as JSON lines."""
    path = db_path or DEFAULT_DB
    with sqlite3.connect(path) as cx:
        cx.row_factory = sqlite3.Row
        for row in cx.execute(sql):
            print(json.dumps(dict(row), ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="Codex log database utilities")
    parser.add_argument("--init", action="store_true", help="Initialize the database")
    parser.add_argument("--query", help="SQL query to run")
    parser.add_argument("--db", default=DEFAULT_DB, help="Path to the SQLite database")
    args = parser.parse_args()

    if args.init:
        init_db(args.db)
    if args.query:
        run_query(args.query, args.db)


if __name__ == "__main__":
    main()
