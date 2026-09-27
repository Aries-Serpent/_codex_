"""Session logging utilities for Codex.

Provides:
- `SessionLogger`: context manager logging session_start/session_end via
  `log_event`.
- `log_message(session_id, role, message, db_path=None)`: validated message
  logging helper.

If the repo already defines `log_event`, `init_db`, and `_DB_LOCK` under
`codex.logging`, we import and use them. Otherwise we fall back to local,
minimal implementations (scoped in this file) to preserve end-to-end behavior
without polluting global API.

Roles allowed: system|user|assistant|tool|INFO|WARN.
"""

from __future__ import annotations

import atexit
import json
import logging
import os
import sqlite3
import threading
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, Optional

logger = logging.getLogger(__name__)

try:
    from aries_serpent_core.db.sqlite_patch import auto_enable_from_env as _codex_sqlite_auto

    _codex_sqlite_auto()
except (ImportError, AttributeError) as exc:  # pragma: no cover - defensive
    logging.getLogger(__name__).debug("sqlite auto setup failed: %s", exc)

DEFAULT_LOG_DB = Path(".codex/session_logs.db")

# Prefer the legacy codex compatibility adapter when present, then the modern
# package-local implementations, and only then the local fallback.
try:
    from src.codex.logging.db import _DB_LOCK as _shared_DB_LOCK
    from src.codex.logging.db import init_db as _shared_init_db
    from src.codex.logging.db import log_event as _shared_log_event
except (ImportError, AttributeError, ModuleNotFoundError):
    logger.debug("src.codex.logging.db not available; using built-in fallbacks", exc_info=True)
    _shared_DB_LOCK = None  # type: ignore[assignment]
    _shared_init_db = None  # type: ignore[assignment]
    try:
        from codex.monkeypatch.log_adapters import (
            log_event as _shared_log_event,  # type: ignore[no-redef]
        )
    except (IOError, OSError, ModuleNotFoundError, ImportError):
        try:
            from aries_serpent_core.monkeypatch.log_adapters import (  # type: ignore[no-redef]
                log_event as _shared_log_event,
            )
        except (IOError, OSError, ModuleNotFoundError, ImportError):
            _shared_log_event = None  # type: ignore[assignment]

_DB_LOCK = _shared_DB_LOCK or threading.RLock()
INITIALIZED_PATHS: set[str] = set()
_INITIALIZING_PATHS: dict[str, threading.Event] = {}
USE_POOL = os.getenv("CODEX_SQLITE_POOL") == "1"
CONN_POOL: dict[str, sqlite3.Connection] = {}


def _configure_connection(conn: sqlite3.Connection) -> None:
    """Apply best-effort SQLite pragmas for pooled connections."""
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
    except (ConnectionError, TimeoutError) as e:
        logger.warning("journal_mode=WAL failed: %s", e, exc_info=True)
    try:
        conn.execute("PRAGMA synchronous=NORMAL;")
    except (ValueError, TypeError, RuntimeError) as e:
        logger.warning("synchronous=NORMAL failed: %s", e)
    try:
        conn.execute("PRAGMA foreign_keys=ON;")
    except (ValueError, TypeError, RuntimeError) as e:
        logger.warning("foreign_keys=ON failed: %s", e)


def _close_pool() -> None:
    for conn in list(CONN_POOL.values()):
        try:
            conn.close()
        except sqlite3.Error as exc:  # pragma: no cover - defensive
            logging.getLogger(__name__).debug("pool close failed: %s", exc)
    CONN_POOL.clear()


if USE_POOL:
    atexit.register(_close_pool)


def _default_db_path() -> Path:
    """Return default database path, honoring environment variable at call time."""
    return Path(os.getenv("CODEX_LOG_DB_PATH", str(DEFAULT_LOG_DB)))


def init_db(db_path: Optional[Path] = None) -> Path:
    """Initialize SQLite table for session events if absent."""
    p = Path(db_path or _default_db_path())
    key = str(p)
    leader_event: Optional[threading.Event] = None
    while True:
        with _DB_LOCK:
            if key in INITIALIZED_PATHS:
                return p
            pending = _INITIALIZING_PATHS.get(key)
            if pending is None:
                pending = threading.Event()
                _INITIALIZING_PATHS[key] = pending
                leader_event = pending
                break
        pending.wait()
    if leader_event is None:
        raise RuntimeError("leader_event not initialized; init_db synchronization failed")
    p.parent.mkdir(parents=True, exist_ok=True)
    conn: Optional[sqlite3.Connection] = None
    try:
        conn = sqlite3.connect(p)
        try:
            conn.execute("PRAGMA journal_mode=WAL;")
        except (ConnectionError, TimeoutError) as e:
            logger.warning("journal_mode=WAL failed: %s", e, exc_info=True)
        try:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS session_events(
                            ts REAL NOT NULL,
                            session_id TEXT NOT NULL,
                            role TEXT NOT NULL,
                            message TEXT NOT NULL,
                            seq INTEGER,
                            meta TEXT
                        )"""
            )
            cols = [r[1] for r in conn.execute("PRAGMA table_info(session_events)")]
            if "seq" not in cols:
                conn.execute("ALTER TABLE session_events ADD COLUMN seq INTEGER")
            if "meta" not in cols:
                conn.execute("ALTER TABLE session_events ADD COLUMN meta TEXT")
            conn.execute(
                "CREATE INDEX IF NOT EXISTS session_events_sid_ts_idx "
                "ON session_events(session_id, ts)"
            )
            conn.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS session_events_session_seq_idx "
                "ON session_events(session_id, seq)"
            )
            conn.commit()
        finally:
            conn.close()
    except (IOError, OSError, ModuleNotFoundError, ImportError):
        logger.warning("init_db failed", exc_info=True)
        with _DB_LOCK:
            _INITIALIZING_PATHS.pop(key, None)
        leader_event.set()
        raise
    else:
        with _DB_LOCK:
            INITIALIZED_PATHS.add(key)
            _INITIALIZING_PATHS.pop(key, None)
        leader_event.set()
        return p


def _fallback_log_event(
    session_id: str,
    role: str,
    message: str,
    db_path: Optional[Path] = None,
    meta: Optional[dict[str, Any]] = None,
) -> None:
    p = init_db(db_path)
    key = str(p)
    if USE_POOL:
        conn = CONN_POOL.get(key)
        if conn is None:
            conn = sqlite3.connect(p, check_same_thread=False)
            _configure_connection(conn)
            CONN_POOL[key] = conn
    else:
        conn = sqlite3.connect(p)
        _configure_connection(conn)
    try:
        cur = conn.execute(
            "SELECT COALESCE(MAX(seq), 0) FROM session_events WHERE session_id=?",
            (session_id,),
        )
        next_seq = cur.fetchone()[0] + 1
        conn.execute(
            "INSERT INTO session_events(ts, session_id, role, message, seq, meta) "
            "VALUES(?,?,?,?,?,?)",
            (
                time.time(),
                session_id,
                role,
                message,
                next_seq,
                json.dumps(meta) if meta else None,
            ),
        )
        conn.commit()
    except (ValueError, TypeError):
        logger.warning("Exception occurred in _fallback_log_event", exc_info=True)
        if USE_POOL:
            try:
                conn.close()
            except sqlite3.Error as exc:  # pragma: no cover - defensive
                logging.getLogger(__name__).debug("pool conn close failed: %s", exc)
            CONN_POOL.pop(key, None)
        raise
    finally:
        if not USE_POOL:
            conn.close()


def log_event(
    session_id: str,
    role: str,
    message: str,
    db_path: Optional[Path] = None,
    meta: Optional[dict[str, Any]] = None,
) -> None:
    """Delegate to shared log_event if available, otherwise fallback."""
    if _shared_log_event is not None:
        module_name = getattr(_shared_log_event, "__module__", "")
        if module_name in {
            "codex.monkeypatch.log_adapters",
            "aries_serpent_core.monkeypatch.log_adapters",
        }:
            _fallback_log_event(session_id, role, message, db_path=db_path, meta=meta)
            adapter_meta: dict[str, Any] = {"session_id": session_id}
            if meta is not None:
                adapter_meta["meta"] = meta
            adapter_meta_json = json.dumps(adapter_meta, ensure_ascii=False, default=str)
            try:
                _shared_log_event(  # type: ignore[call-arg]
                    role,
                    message,
                    meta=adapter_meta_json,
                    db_path=db_path,
                )
                return
            except TypeError as e:
                logger.warning("monkeypatch adapter call failed (trying minimal): %s", e)
                try:
                    _shared_log_event(role, message)
                except TypeError as e:
                    logger.debug(
                        "shared log_event compatibility fallback failed: %s",
                        e,
                        exc_info=True,
                    )
            return
        try:
            _shared_log_event(session_id, role, message, db_path=db_path, meta=meta)
        except TypeError as e:
            logger.warning("shared log_event keyword call failed (retrying without meta): %s", e)
            try:
                _shared_log_event(session_id, role, message, db_path=db_path)
            except TypeError:
                _shared_log_event(session_id, role, message)
        return
    _fallback_log_event(session_id, role, message, db_path=db_path, meta=meta)
    return


_ALLOWED_ROLES = {"system", "user", "assistant", "tool", "INFO", "WARN"}


def get_session_id() -> str:
    """Return current session ID, generating and persisting if absent."""
    sid = os.getenv("CODEX_SESSION_ID")
    if sid:
        return sid
    sid = str(uuid.uuid4())
    os.environ["CODEX_SESSION_ID"] = sid
    return sid


def fetch_messages(session_id: str, db_path: Optional[Path] = None) -> list[dict[str, Any]]:
    path = Path(db_path or _default_db_path())
    if not path.exists():
        return []
    conn = sqlite3.connect(path)
    try:
        rows = conn.execute(
            "SELECT ts, role, message, seq, meta FROM session_events WHERE session_id=? ORDER BY ts, seq",  # noqa: E501
            (session_id,),
        ).fetchall()
    finally:
        conn.close()
    result: list[dict[str, Any]] = []
    for ts, role, message, seq, meta in rows:
        payload: dict[str, Any] = {
            "ts": ts,
            "session_id": session_id,
            "role": role,
            "message": message,
        }
        if seq is not None:
            payload["seq"] = seq
        if meta:
            try:
                payload["meta"] = json.loads(meta)
            except (TypeError, json.JSONDecodeError):
                payload["meta"] = meta
        result.append(payload)
    return result


def log_message(
    session_id: str,
    role: str,
    message,
    db_path: Optional[Path] = None,
    meta: Optional[dict[str, Any]] = None,
) -> None:
    """Validate role, normalize message to string, ensure DB init, and write."""
    if role not in _ALLOWED_ROLES:
        raise ValueError(f"invalid role {role!r}; expected one of {_ALLOWED_ROLES}")
    text = message if isinstance(message, str) else str(message)
    path = Path(db_path) if db_path else _default_db_path()
    init_db(path)
    with _DB_LOCK:
        log_event(session_id, role, text, db_path=path, meta=meta)


@dataclass
class SessionLogger:
    """Context manager for session-scoped logging."""

    session_id: str
    db_path: Optional[Path] = None

    def __post_init__(self) -> None:
        if self.db_path is not None:
            init_db(self.db_path)

    def __enter__(self) -> SessionLogger:
        log_event(self.session_id, "system", "session_start", db_path=self.db_path)
        return self

    def __exit__(self, exc_type, exc, tb) -> Literal[False]:
        try:
            if exc_type is not None:
                log_event(
                    self.session_id,
                    "system",
                    f"session_end (exc={exc_type.__name__}: {exc})",
                    db_path=self.db_path,
                )
            else:
                log_event(self.session_id, "system", "session_end", db_path=self.db_path)
        except (IOError, OSError, ModuleNotFoundError, ImportError):
            logger.warning("session_end DB log failed", exc_info=True)
        return False

    def log(self, role: str, message) -> None:
        log_message(self.session_id, role, message, db_path=self.db_path)


def migrate_legacy_events(db_path: Optional[Path] = None) -> None:
    """Backfill ``seq`` for rows missing it and remove duplicate start/end events."""
    path = init_db(db_path)
    conn = sqlite3.connect(path)
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
    except (IOError, OSError, ModuleNotFoundError, ImportError) as e:
        logger.warning("journal_mode=WAL failed: %s", e, exc_info=True)
    try:
        conn.execute("BEGIN")
        cur = conn.execute("SELECT DISTINCT session_id FROM session_events WHERE seq IS NULL")
        for (sid,) in cur.fetchall():
            max_seq = conn.execute(
                "SELECT COALESCE(MAX(seq),0) FROM session_events WHERE session_id=?",
                (sid,),
            ).fetchone()[0]
            rows = conn.execute(
                "SELECT rowid FROM session_events WHERE session_id=? AND seq IS NULL ORDER BY ts",
                (sid,),
            ).fetchall()
            for row in rows:
                max_seq += 1
                conn.execute("UPDATE session_events SET seq=? WHERE rowid=?", (max_seq, row[0]))
        cur = conn.execute(
            "SELECT DISTINCT session_id FROM session_events "
            "WHERE message IN ('session_start','session_end')"
        )
        for (sid,) in cur.fetchall():
            start_ids = [
                r[0]
                for r in conn.execute(
                    "SELECT rowid FROM session_events WHERE session_id=? "
                    "AND message='session_start' ORDER BY ts",
                    (sid,),
                ).fetchall()
            ]
            for rid in start_ids[1:]:
                conn.execute("DELETE FROM session_events WHERE rowid=?", (rid,))
            end_ids = [
                r[0]
                for r in conn.execute(
                    "SELECT rowid FROM session_events WHERE session_id=? "
                    "AND message='session_end' ORDER BY ts",
                    (sid,),
                ).fetchall()
            ]
            for rid in end_ids[1:]:
                conn.execute("DELETE FROM session_events WHERE rowid=?", (rid,))
        conn.commit()
    finally:
        conn.close()
