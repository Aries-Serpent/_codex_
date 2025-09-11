"""SQLite catalog for run metadata and artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
from pathlib import Path
from typing import Iterable


def _db_path() -> Path:
    """Resolve the catalog DB location from the environment at call time."""
    return Path(os.getenv("CODEX_CATALOG_DB", ".codex/catalog.sqlite"))


SCHEMA = """
CREATE TABLE IF NOT EXISTS runs(
    run_id TEXT PRIMARY KEY,
    started_at TEXT,
    finished_at TEXT,
    status TEXT,
    git_head TEXT,
    branch TEXT
);
CREATE TABLE IF NOT EXISTS manifests(
    run_id TEXT,
    kind TEXT CHECK(kind IN ('pre','post')),
    path TEXT,
    sha256 TEXT,
    PRIMARY KEY(run_id, kind)
);
CREATE TABLE IF NOT EXISTS diffs(
    run_id TEXT PRIMARY KEY,
    compare_report_path TEXT,
    unexpected_added INT,
    unexpected_removed INT,
    changed INT,
    moves INT
);
CREATE TABLE IF NOT EXISTS artifacts(
    run_id TEXT,
    type TEXT,
    path TEXT,
    bytes INT,
    sha256 TEXT,
    PRIMARY KEY(run_id, type)
);
CREATE TABLE IF NOT EXISTS errors(
    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT,
    phase TEXT,
    message TEXT,
    context TEXT,
    created_at TEXT
);
"""


def _connect(path: Path | None = None) -> sqlite3.Connection:
    path = path or _db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA)
    return conn


def record_run(run_meta: dict, path: Path | None = None) -> None:
    """Insert or update a run row."""
    with _connect(path) as db:
        db.execute(
            """
            INSERT INTO runs(run_id, started_at, finished_at, status, git_head, branch)
            VALUES(:run_id, :started_at, :finished_at, :status, :git_head, :branch)
            ON CONFLICT(run_id) DO UPDATE SET
                started_at=excluded.started_at,
                finished_at=excluded.finished_at,
                status=excluded.status,
                git_head=excluded.git_head,
                branch=excluded.branch
            """,
            run_meta,
        )
        db.commit()


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def upsert_artifact(run_id: str, type: str, path: str, db_path: Path | None = None) -> None:
    p = Path(path)
    meta = {
        "run_id": run_id,
        "type": type,
        "path": path,
        "bytes": p.stat().st_size if p.exists() else 0,
        "sha256": _sha256(p) if p.exists() else "",
    }
    with _connect(db_path) as db:
        db.execute(
            """
            INSERT INTO artifacts(run_id, type, path, bytes, sha256)
            VALUES(:run_id, :type, :path, :bytes, :sha256)
            ON CONFLICT(run_id, type) DO UPDATE SET
                path=excluded.path,
                bytes=excluded.bytes,
                sha256=excluded.sha256
            """,
            meta,
        )
        db.commit()


def ingest_compare_report(run_id: str, path: str, db_path: Path | None = None) -> None:
    data = json.loads(Path(path).read_text())
    summary = data.get("summary", {})
    row = {
        "run_id": run_id,
        "compare_report_path": path,
        "unexpected_added": summary.get("unexpected_added", 0),
        "unexpected_removed": summary.get("unexpected_removed", 0),
        "changed": summary.get("changed", 0),
        "moves": summary.get("moves", 0),
    }
    with _connect(db_path) as db:
        db.execute(
            """
            INSERT INTO diffs(run_id, compare_report_path, unexpected_added, unexpected_removed, changed, moves)
            VALUES(:run_id, :compare_report_path, :unexpected_added, :unexpected_removed, :changed, :moves)
            ON CONFLICT(run_id) DO UPDATE SET
                compare_report_path=excluded.compare_report_path,
                unexpected_added=excluded.unexpected_added,
                unexpected_removed=excluded.unexpected_removed,
                changed=excluded.changed,
                moves=excluded.moves
            """,
            row,
        )
        db.commit()


def query(sql: str, db_path: Path | None = None) -> Iterable[tuple]:
    with _connect(db_path) as db:
        cur = db.execute(sql)
        return cur.fetchall()


def _main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    q = sub.add_parser("query")
    q.add_argument("sql")

    ns = ap.parse_args()
    if ns.cmd == "query":
        rows = query(ns.sql)
        for r in rows:
            print(r)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(_main())
