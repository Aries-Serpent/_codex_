# coding: utf-8
"""
codex.logging.session_logger
SQLite-backed session event logger with per-thread connections and serialized writes.

Schema:
  session_events(
      session_id TEXT,
      timestamp  TEXT,   -- ISO 8601 with timezone
      role       TEXT,   -- 'system' | 'user' | 'assistant' | 'tool'
      message    TEXT,
      model      TEXT,
      tokens     INTEGER,
      PRIMARY KEY(session_id, timestamp)
  )

Env:
  CODEX_LOG_DB_PATH -> override DB path (default: ./codex_session_log.db)

CLI:
  python -m codex.logging.session_logger --event start|message|end \
      --session-id <id> --role <user|assistant|system|tool> --message "text"

Concurrency:
  - One connection per thread (thread-local).
  - Writes serialized via RLock.
  - PRAGMA journal_mode=WAL, synchronous=NORMAL for resilience.
"""
from __future__ import annotations
import argparse
import datetime
import os
import sqlite3
import threading
from pathlib import Path

_DB_LOCAL = threading.local()
_DB_LOCK = threading.RLock()
_DEFAULT_DB = str(Path.cwd() / "codex_session_log.db")

def _db_path(override: str | None = None) -> str:
    return override or os.getenv("CODEX_LOG_DB_PATH") or _DEFAULT_DB

def _get_conn(db_path: str) -> sqlite3.Connection:
    if getattr(_DB_LOCAL, "conn", None) is None or getattr(_DB_LOCAL, "db_path", None) != db_path:
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(db_path, isolation_level=None, check_same_thread=False)
        with conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
        _DB_LOCAL.conn = conn
        _DB_LOCAL.db_path = db_path
    return _DB_LOCAL.conn

def init_db(db_path: str | None = None) -> None:
    dbp = _db_path(db_path)
    with _DB_LOCK:
        conn = _get_conn(dbp)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS session_events(
            session_id TEXT NOT NULL,
            timestamp  TEXT NOT NULL,
            role       TEXT NOT NULL,
            message    TEXT NOT NULL,
            model      TEXT,
            tokens     INTEGER,
            PRIMARY KEY(session_id, timestamp)
        )""")
        cols = [r[1] for r in conn.execute("PRAGMA table_info(session_events)")]
        if "model" not in cols:
            conn.execute("ALTER TABLE session_events ADD COLUMN model TEXT")
        if "tokens" not in cols:
            conn.execute("ALTER TABLE session_events ADD COLUMN tokens INTEGER")

def log_event(session_id: str, role: str, message: str, db_path: str | None = None,
              model: str | None = None, tokens: int | None = None) -> None:
    if not session_id:
        raise ValueError("session_id is required")
    if role not in {"system", "user", "assistant", "tool"}:
        raise ValueError("role must be one of: system,user,assistant,tool")
    init_db(db_path)
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
    dbp = _db_path(db_path)
    with _DB_LOCK:
        conn = _get_conn(dbp)
        conn.execute(
            "INSERT OR REPLACE INTO session_events(session_id,timestamp,role,message,model,tokens) VALUES (?,?,?,?,?,?)",
            (session_id, ts, role, message, model, tokens)
        )

def _cli():
    ap = argparse.ArgumentParser()
    ap.add_argument("--event", required=True, choices=["start","message","end"])
    ap.add_argument("--session-id", dest="sid", required=False, default=os.getenv("CODEX_SESSION_ID",""))
    ap.add_argument("--role", required=False, default="system")
    ap.add_argument("--message", required=False, default="")
    ap.add_argument("--db-path", required=False, default=None)
    args = ap.parse_args()

    sid = args.sid or os.getenv("CODEX_SESSION_ID") or ""
    if not sid:
        sid = str(int(datetime.datetime.now(datetime.timezone.utc).timestamp()))
    if args.event == "start":
        log_event(sid, "system", "session_start", args.db_path)
    elif args.event == "end":
        log_event(sid, "system", "session_end", args.db_path)
    else:
        role = args.role if args.role in {"system","user","assistant","tool"} else "system"
        msg = args.message or ""
        log_event(sid, role, msg, args.db_path)

if __name__ == "__main__":
    _cli()
