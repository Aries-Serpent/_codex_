"""Import session NDJSON logs into the SQLite session_events table.

This module treats ``.codex/sessions/<SESSION_ID>.ndjson`` files as the
canonical log source and synchronizes them into ``session_events`` rows.
Each line in the NDJSON file is assigned a 1-based ``seq`` number; rows are
upserted with a uniqueness constraint on ``(session_id, seq)``.  A companion
table ``session_ingest_watermark`` tracks the highest ingested sequence per
session so repeated imports are idempotent.

The importer stores:

* ``session_events(session_id TEXT, seq INTEGER, ts REAL, role TEXT, message TEXT)``
* ``session_ingest_watermark(session_id TEXT PRIMARY KEY, seq INTEGER)``

Example CLI usage::

    codex-import-ndjson --session S123
    codex-import-ndjson --all
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

from .config import DEFAULT_LOG_DB


def _default_log_dir() -> Path:
    return Path(os.getenv("CODEX_SESSION_LOG_DIR", ".codex/sessions")).expanduser()


def _db_path(override: str | None = None) -> Path:
    env = override or os.getenv("CODEX_LOG_DB_PATH") or os.getenv("CODEX_DB_PATH")
    if env:
        return Path(env).expanduser().resolve()
    return DEFAULT_LOG_DB.expanduser().resolve()


def _init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS session_events (
            session_id TEXT NOT NULL,
            ts REAL,
            role TEXT,
            message TEXT
        )
        """
    )
    cols = [r[1] for r in conn.execute("PRAGMA table_info(session_events)")]
    if "seq" not in cols:
        conn.execute("ALTER TABLE session_events ADD COLUMN seq INTEGER")
    conn.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS session_events_session_seq_idx ON session_events(session_id, seq)"
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS session_ingest_watermark (
            session_id TEXT PRIMARY KEY,
            seq INTEGER NOT NULL
        )
        """
    )


def _parse_ts(ts: str | None) -> float | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
    except Exception:
        return None


def import_session(
    session_id: str,
    log_dir: Path | None = None,
    db_path: Path | str | None = None,
) -> int:
    """Import a single session's NDJSON log into SQLite.

    Returns the number of new rows inserted.
    """

    log_dir = (log_dir or _default_log_dir()).expanduser().resolve()
    ndjson_path = log_dir / f"{session_id}.ndjson"
    if not ndjson_path.exists():
        raise FileNotFoundError(ndjson_path)

    db_path = _db_path(str(db_path) if db_path else None)
    conn = sqlite3.connect(str(db_path))
    try:
        _init_db(conn)
        cur = conn.execute(
            "SELECT seq FROM session_ingest_watermark WHERE session_id=?",
            (session_id,),
        )
        row = cur.fetchone()
        watermark = row[0] if row else 0

        last_seq = watermark
        inserted = 0
        with ndjson_path.open(encoding="utf-8") as f:
            for seq, line in enumerate(f, start=1):
                if not line.strip() or seq <= watermark:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                ts = _parse_ts(obj.get("ts"))
                role = obj.get("role") or "system"
                message = obj.get("message") or obj.get("type") or ""
                conn.execute(
                    """
                    INSERT INTO session_events(session_id, seq, ts, role, message)
                    VALUES(?,?,?,?,?)
                    ON CONFLICT(session_id, seq) DO UPDATE SET
                        ts=excluded.ts,
                        role=excluded.role,
                        message=excluded.message
                    """,
                    (session_id, seq, ts, role, message),
                )
                inserted += 1
                last_seq = seq

        if last_seq > watermark:
            conn.execute(
                """
                INSERT INTO session_ingest_watermark(session_id, seq)
                VALUES(?,?)
                ON CONFLICT(session_id) DO UPDATE SET seq=excluded.seq
                """,
                (session_id, last_seq),
            )
        conn.commit()
        return inserted
    finally:
        conn.close()


def import_all(log_dir: Path | None = None, db_path: Path | str | None = None) -> Dict[str, int]:
    """Import all ``*.ndjson`` files found under ``log_dir``."""

    log_dir = (log_dir or _default_log_dir()).expanduser().resolve()
    results: Dict[str, int] = {}
    for p in sorted(log_dir.glob("*.ndjson")):
        sid = p.stem
        results[sid] = import_session(sid, log_dir=log_dir, db_path=db_path)
    return results


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Import session NDJSON logs into session_events",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--session", help="Session ID to import")
    group.add_argument("--all", action="store_true", help="Import all sessions")
    parser.add_argument("--log-dir", help="Directory containing NDJSON logs")
    parser.add_argument("--db", help="Path to SQLite DB")
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.session:
        import_session(args.session, log_dir=args.log_dir, db_path=args.db)
    else:
        import_all(log_dir=args.log_dir, db_path=args.db)
    return 0


if __name__ == "__main__":
    session_ctx: Optional[Any]
    try:
        from .session_hooks import session as session_ctx
    except Exception:  # pragma: no cover - helper optional
        session_ctx = None
    if session_ctx:
        with session_ctx(sys.argv):
            raise SystemExit(main())
    raise SystemExit(main())

