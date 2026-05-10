#!/usr/bin/env python3
"""
migrate_doc_schema.py — Migrate the documentation SQLite schema to the current version.

Manages a local SQLite database used for caching documentation metadata,
content snapshots, and search index state between CI runs.

Schema versions
---------------
  v0  — no table (fresh database)
  v1  — docs table: id, title, path, category, tags (JSON), description, content_sha, fetched_at
  v2  — adds search_index_json, last_indexed_at columns
  v3  — adds variables_json column (for {{var}} substitution templates)

Usage:
    python scripts/docs/migrate_doc_schema.py [--db PATH] [--target-version N]
    python scripts/docs/migrate_doc_schema.py --db .codex/docs.db --status
    python scripts/docs/migrate_doc_schema.py --db .codex/docs.db --reset

Exit codes:
    0 — success
    1 — migration error
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from collections.abc import Sequence
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_DB = REPO_ROOT / ".codex" / "docs.db"

CURRENT_VERSION = 3

# ---------------------------------------------------------------------------
# Migration steps
# ---------------------------------------------------------------------------

MIGRATIONS: dict[int, str] = {
    1: """
        CREATE TABLE IF NOT EXISTS docs (
            id              TEXT PRIMARY KEY,
            title           TEXT NOT NULL,
            path            TEXT NOT NULL,
            category        TEXT NOT NULL,
            tags            TEXT NOT NULL DEFAULT '[]',
            description     TEXT,
            content_sha     TEXT,
            fetched_at      TEXT
        );
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER NOT NULL
        );
        INSERT INTO schema_version (version) VALUES (1);
    """,
    2: """
        ALTER TABLE docs ADD COLUMN search_index_json TEXT;
        ALTER TABLE docs ADD COLUMN last_indexed_at TEXT;
        UPDATE schema_version SET version = 2;
    """,
    3: """
        ALTER TABLE docs ADD COLUMN variables_json TEXT DEFAULT '{}';
        UPDATE schema_version SET version = 3;
    """,
}


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------

def _get_db_version(conn: sqlite3.Connection) -> int:
    try:
        row = conn.execute("SELECT version FROM schema_version LIMIT 1").fetchone()
        return int(row[0]) if row else 0
    except sqlite3.OperationalError:
        return 0


def _run_migration(conn: sqlite3.Connection, to_version: int) -> None:
    sql = MIGRATIONS[to_version]
    for stmt in sql.split(";"):
        stmt = stmt.strip()
        if stmt:
            conn.execute(stmt)
    conn.commit()


def migrate(db_path: Path, target: int = CURRENT_VERSION, verbose: bool = False) -> int:
    """
    Run all pending migrations up to `target`.
    Returns the final schema version.
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)

    try:
        current = _get_db_version(conn)
        if verbose:
            print(f"Current schema version: v{current}, target: v{target}")

        for v in range(current + 1, target + 1):
            if v not in MIGRATIONS:
                print(f"WARNING: no migration defined for v{v}", file=sys.stderr)
                continue
            _run_migration(conn, v)
            if verbose:
                print(f"  Migrated → v{v}")

        final = _get_db_version(conn)
        return final
    finally:
        conn.close()


def get_status(db_path: Path) -> dict:
    if not db_path.exists():
        return {"exists": False, "version": 0, "entry_count": 0}

    conn = sqlite3.connect(db_path)
    try:
        version = _get_db_version(conn)
        try:
            count = conn.execute("SELECT COUNT(*) FROM docs").fetchone()[0]
        except sqlite3.OperationalError:
            count = 0
        return {"exists": True, "version": version, "entry_count": count}
    finally:
        conn.close()


def reset_db(db_path: Path) -> None:
    if db_path.exists():
        db_path.unlink()
        print(f"Deleted {db_path}")


def upsert_doc(conn: sqlite3.Connection, doc: dict) -> None:
    """Insert or replace a documentation catalog entry in the docs table.

    If ``doc`` does not include a ``fetched_at`` key, the current UTC
    timestamp is used automatically — callers need not set it explicitly.
    """
    conn.execute(
        """
        INSERT INTO docs (id, title, path, category, tags, description,
                          content_sha, fetched_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            title        = excluded.title,
            path         = excluded.path,
            category     = excluded.category,
            tags         = excluded.tags,
            description  = excluded.description,
            content_sha  = excluded.content_sha,
            fetched_at   = excluded.fetched_at
        """,
        (
            doc.get("id", ""),
            doc.get("title", ""),
            doc.get("path", ""),
            doc.get("category", ""),
            json.dumps(doc.get("tags", [])),
            doc.get("description"),
            doc.get("content_sha"),
            doc.get("fetched_at", datetime.now(timezone.utc).isoformat()),
        ),
    )
    conn.commit()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    p.add_argument("--db", type=Path, default=DEFAULT_DB,
                   help="SQLite database path (default: %(default)s)")
    p.add_argument("--target-version", type=int, default=CURRENT_VERSION,
                   metavar="N", help="Target schema version (default: %(default)s)")
    p.add_argument("--status", action="store_true",
                   help="Print current schema status and exit")
    p.add_argument("--reset", action="store_true",
                   help="Delete the database and re-create from scratch")
    p.add_argument("--verbose", "-v", action="store_true")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    if args.status:
        status = get_status(args.db)
        print(json.dumps(status, indent=2))
        return 0

    if args.reset:
        reset_db(args.db)

    try:
        final = migrate(args.db, args.target_version, verbose=args.verbose)
        print(f"✓ Schema is at v{final} — {args.db}")
        return 0
    except Exception as exc:
        print(f"ERROR during migration: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
