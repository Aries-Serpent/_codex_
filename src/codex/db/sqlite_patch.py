"""SQLite connection pooling and patch helpers.

This module monkey-patches :func:`sqlite3.connect` to reuse connections based on
database path, process, thread, and optional ``CODEX_SESSION_ID``. Pooling is
enabled via the ``CODEX_SQLITE_POOL`` environment variable and applies several
pragmas aimed at improving concurrent write performance. All pooled connections
remain open for the duration of the interpreter and are closed automatically on
interpreter exit.

Limitations:

* Connections are cached **per thread**; they are not shared between threads
  or processes. Sharing a connection across threads is not supported by the
  underlying :mod:`sqlite3` driver and may result in race conditions.
* Calling :meth:`sqlite3.Connection.close` on a pooled connection leaves a
  closed instance in the pool. Avoid ``with sqlite3.connect(...)`` blocks or
  explicit ``close()`` calls when pooling is enabled.
"""

import atexit
import logging
import os
import sqlite3
import threading
from typing import Dict, Tuple

_ORIG_CONNECT = sqlite3.connect
_POOL_ENABLED_ENV = "CODEX_SQLITE_POOL"  # "1" enables pooling
_SESSION_ENV = "CODEX_SESSION_ID"  # optional logical session id

# Key: (db_path, pid, tid, session_id)
_CONN_POOL: Dict[Tuple[str, int, int, str], sqlite3.Connection] = {}
_POOL_LOCK = threading.RLock()


class PooledConnectionProxy:
    """Thin proxy that removes itself from the pool on ``close``."""

    def __init__(self, conn: sqlite3.Connection, key: Tuple[str, int, int, str]):
        self._conn = conn
        self._key = key

    def __getattr__(self, name):  # pragma: no cover - simple delegation
        return getattr(self._conn, name)

    def close(self):  # pragma: no cover - exercised via tests
        """Remove the connection from the pool then close it."""

        with _POOL_LOCK:
            # ``_CONN_POOL`` may be a mapping, set, or list depending on how
            # callers manage pooled connections. Be tolerant of any container
            # type so a closed handle cannot be retrieved again.
            if isinstance(_CONN_POOL, dict):
                _CONN_POOL.pop(self._key, None)
            elif isinstance(_CONN_POOL, set):
                _CONN_POOL.discard(self._conn)
            elif isinstance(_CONN_POOL, list):
                try:
                    _CONN_POOL.remove(self._conn)
                except ValueError:
                    pass
        return self._conn.close()


def _key(database: str) -> Tuple[str, int, int, str]:
    """Return a key uniquely identifying a connection slot.

    The key combines database path, process id, thread id, and optional session
    id so different sessions do not share the same connection.
    """

    pid = os.getpid()
    tid = threading.get_ident()
    sid = os.getenv(_SESSION_ENV, "")
    return (database, pid, tid, sid)


def _apply_pragmas(conn: sqlite3.Connection) -> None:
    """Apply performance-related pragmas to a new connection."""

    try:
        cur = conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("PRAGMA synchronous=NORMAL;")
        cur.execute("PRAGMA temp_store=MEMORY;")
        # large mmap improves read performance; ignored if unsupported
        cur.execute("PRAGMA mmap_size=30000000000;")
        cur.close()
    except sqlite3.Error as e:
        logging.exception("sqlite PRAGMA failure: %s", e)


def pooled_connect(database, *args, **kwargs):
    # Fallback if pooling off
    if os.getenv(_POOL_ENABLED_ENV, "0") not in ("1", "true", "TRUE", "yes", "YES"):
        return _ORIG_CONNECT(database, *args, **kwargs)

    # Ensure multi-thread use is allowed on same connection
    kwargs = dict(kwargs)
    kwargs.setdefault("check_same_thread", False)

    k = _key(str(database))
    with _POOL_LOCK:
        # Reuse existing connection for this key, or create and cache one
        conn = _CONN_POOL.get(k)
        if conn is None:
            conn = _ORIG_CONNECT(database, *args, **kwargs)
            _apply_pragmas(conn)
            _CONN_POOL[k] = conn
        return PooledConnectionProxy(conn, k)


def enable_pooling():
    sqlite3.connect = pooled_connect


def disable_pooling():
    sqlite3.connect = _ORIG_CONNECT


def auto_enable_from_env():
    if os.getenv(_POOL_ENABLED_ENV, "0") in ("1", "true", "TRUE", "yes", "YES"):
        enable_pooling()


@atexit.register
def _close_all():
    """Best-effort cleanup of pooled connections on interpreter shutdown."""

    with _POOL_LOCK:
        for k, conn in list(_CONN_POOL.items()):
            try:
                conn.close()
            except Exception:
                pass
        _CONN_POOL.clear()
