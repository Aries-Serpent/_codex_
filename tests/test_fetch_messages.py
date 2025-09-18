"""Tests for fetch_messages covering custom and default DB paths."""

# ruff: noqa: E501
import importlib
import inspect
import os
import sqlite3
import sys
import threading
import types
from pathlib import Path

import pytest

from tests._codex_introspect import (
    patch_default_db_path,
    resolve_fetch_messages,
    resolve_writer,
)

if "yaml" not in sys.modules:
    _yaml_stub = types.ModuleType("yaml")
    _yaml_stub.safe_load = lambda *args, **kwargs: {}  # type: ignore[assignment]
    sys.modules["yaml"] = _yaml_stub

EVENTS = [
    {"role": "system", "content": "alpha", "ts": 1},
    {"role": "user", "content": "bravo", "ts": 2},
    {"role": "assistant", "content": "charlie", "ts": 3},
]


def _make_sqlite_db(db_path: Path, session_id: str = "SID") -> None:
    """Create a minimal session_events table populated with EVENTS."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(os.fspath(db_path))
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS session_events(
            ts REAL NOT NULL,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            message TEXT NOT NULL
        )
        """
    )
    cur.executemany(
        "INSERT INTO session_events(ts, session_id, role, message) VALUES (?,?,?,?)",
        [(e["ts"], session_id, e["role"], e["content"]) for e in EVENTS],
    )
    conn.commit()
    conn.close()


def _populate_with_writer(writer_meta, db_path: Path | None) -> None:
    """Populate events using a discovered writer function."""
    w = writer_meta["callable"]
    accepts_path = writer_meta.get("accepts_db_path", False)
    params = inspect.signature(w).parameters
    for e in EVENTS:
        kwargs = {}
        if "session_id" in params:
            kwargs["session_id"] = "SID"
        if "sid" in params and "session_id" not in params:
            kwargs["sid"] = "SID"
        if "role" in params:
            kwargs["role"] = e["role"]
        elif "level" in params:
            kwargs["level"] = e["role"]
        if "message" in params:
            kwargs["message"] = e["content"]
        elif "text" in params:
            kwargs["text"] = e["content"]
        if accepts_path and db_path is not None:
            if "db" in params:
                kwargs["db"] = str(db_path)
            else:
                kwargs["db_path"] = str(db_path)
        w(**kwargs)


def _call_fetch(meta, db_path: Path | None, session_id: str = "SID"):
    """Invoke fetch_messages with flexible db_path handling."""
    fn = meta["callable"]
    if db_path is not None and meta.get("accepts_db_path"):
        return list(fn(session_id, db_path=str(db_path)))
    # try kwargs variations
    try:
        return (
            list(fn(session_id, db=str(db_path))) if db_path is not None else list(fn(session_id))
        )
    except TypeError:
        try:
            return (
                list(fn(session_id, path=str(db_path)))
                if db_path is not None
                else list(fn(session_id))
            )
        except TypeError:
            return list(fn(session_id))


def _assert_order_and_content(rows):
    """Validate retrieval order and message content."""

    def to_tuple(r):
        if isinstance(r, dict):
            return (str(r.get("role", "")), str(r.get("message", "")))
        if isinstance(r, (tuple, list)):
            if len(r) >= 4:
                return (str(r[2]), str(r[3]))
            if len(r) >= 3:
                return (str(r[1]), str(r[2]))
        return ("", "")

    got = [to_tuple(r) for r in rows]
    expected = [(e["role"], e["content"]) for e in EVENTS]
    assert got == expected, f"Expected {expected}, got {got}"


@pytest.mark.parametrize("mode", ["custom_path", "default_path"])
def test_fetch_messages(tmp_path, mode, monkeypatch):
    meta = resolve_fetch_messages()
    if "error" in meta:
        pytest.skip("fetch_messages not found in repository — best-effort skip")

    # Set up paths
    custom_db = tmp_path / "messages.db"

    # Try to find a writer
    writer = resolve_writer()  # may be error

    if mode == "custom_path":
        # Prefer to keep all IO under tmp_path
        if isinstance(writer, dict) and "callable" in writer:
            _populate_with_writer(writer, custom_db)
        else:
            # no writer; create SQLite DB as a fallback
            _make_sqlite_db(custom_db)
        rows = _call_fetch(meta, custom_db)
        _assert_order_and_content(rows)
        # cleanup: tmp_path is auto-removed by pytest

    elif mode == "default_path":
        # Try to patch default path constants in module to tmp_path db
        patched = patch_default_db_path(meta["module_obj"], custom_db)
        if not patched and not meta.get("accepts_db_path"):
            pytest.skip(
                "No default DB constant to patch and fetch_messages has no db_path parameter"
            )
        if isinstance(writer, dict) and "callable" in writer:
            _populate_with_writer(writer, custom_db if patched else None)
        else:
            # no writer; create SQLite when patched, otherwise we cannot enforce default target
            if patched:
                _make_sqlite_db(custom_db)
            else:
                pytest.skip(
                    "Cannot safely generate default-path data without writer or patchable constant"
                )
        rows = _call_fetch(meta, None if patched else custom_db)
        _assert_order_and_content(rows)
        # cleanup via tmp_path


def test_pool_toggle_invokes_helper(monkeypatch, tmp_path):
    """Ensure enabling pooling triggers the sqlite patch helper."""

    monkeypatch.setenv("CODEX_SQLITE_POOL", "1")
    monkeypatch.delenv("CODEX_DB_POOL", raising=False)

    called = {"v": False}

    def spy_auto_enable_from_env() -> None:
        called["v"] = True
        return None

    monkeypatch.setattr(
        "codex.db.sqlite_patch.auto_enable_from_env",
        spy_auto_enable_from_env,
        raising=False,
    )

    fm = importlib.import_module("codex.logging.fetch_messages")

    fm = importlib.reload(fm)

    db = tmp_path / "session_logs.db"
    from codex.logging.session_logger import init_db

    init_db(db)

    with fm.get_conn(str(db)) as conn:
        assert conn is not None

    for conn in list(fm._POOL.values()):
        try:
            conn.close()
        finally:
            pass
    fm._POOL.clear()

    assert called[
        "v"
    ], "Expected codex.db.sqlite_patch.auto_enable_from_env to be invoked when CODEX_SQLITE_POOL=1"


def test_get_conn_respects_env_toggle(monkeypatch, tmp_path):
    """get_conn should derive pooling preference at call time from the environment."""

    monkeypatch.delenv("CODEX_SQLITE_POOL", raising=False)
    monkeypatch.delenv("CODEX_DB_POOL", raising=False)

    fm = importlib.reload(importlib.import_module("codex.logging.fetch_messages"))
    fm._POOL.clear()

    from codex.logging.session_logger import init_db

    db = tmp_path / "session_logs.db"
    init_db(db)

    with fm.get_conn(str(db)) as conn1:
        assert conn1 is not None
    assert str(db) not in fm._POOL

    monkeypatch.setenv("CODEX_SQLITE_POOL", "yes")
    with fm.get_conn(str(db)) as conn2:
        assert conn2 is fm._POOL[str(db)]

    pooled_conn = fm._POOL[str(db)]

    monkeypatch.setenv("CODEX_SQLITE_POOL", "0")
    with fm.get_conn(str(db)) as conn3:
        assert conn3 is not pooled_conn
    assert fm._POOL[str(db)] is pooled_conn

    monkeypatch.delenv("CODEX_SQLITE_POOL", raising=False)
    monkeypatch.setenv("CODEX_DB_POOL", "TRUE")
    with fm.get_conn(str(db)) as conn4:
        assert conn4 is fm._POOL[str(db)]

    for connection in list(fm._POOL.values()):
        connection.close()
    fm._POOL.clear()


def test_get_conn_pooled_argument_overrides_env(monkeypatch, tmp_path):
    """Explicit pooled argument should override environment-derived defaults."""

    monkeypatch.setenv("CODEX_SQLITE_POOL", "1")
    fm = importlib.reload(importlib.import_module("codex.logging.fetch_messages"))
    fm._POOL.clear()

    from codex.logging.session_logger import init_db

    db = tmp_path / "override.db"
    init_db(db)

    with fm.get_conn(str(db), pooled=False) as conn:
        assert conn is not None
    assert str(db) not in fm._POOL

    monkeypatch.setenv("CODEX_SQLITE_POOL", "0")
    with fm.get_conn(str(db), pooled=True) as pooled_conn:
        assert pooled_conn is fm._POOL[str(db)]

    for connection in list(fm._POOL.values()):
        connection.close()
    fm._POOL.clear()


def test_pooled_connection_multithread_reads(monkeypatch, tmp_path):
    """Connections from the pool should be safe for read access across threads."""

    monkeypatch.setenv("CODEX_SQLITE_POOL", "1")
    monkeypatch.delenv("CODEX_DB_POOL", raising=False)

    fm = importlib.reload(importlib.import_module("codex.logging.fetch_messages"))
    fm._POOL.clear()

    from codex.logging.session_logger import init_db, log_event

    db = tmp_path / "threaded.db"
    init_db(db)
    for idx in range(5):
        log_event("SID", "user", f"message-{idx}", db_path=db)

    results = [None] * 4

    def reader(slot: int) -> None:
        try:
            with fm.get_conn(str(db)) as conn:
                results[slot] = conn.execute("SELECT COUNT(*) FROM session_events").fetchone()[0]
        except Exception as exc:  # pragma: no cover - diagnostic
            results[slot] = exc

    threads = [threading.Thread(target=reader, args=(i,)) for i in range(len(results))]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert not any(isinstance(value, Exception) for value in results)
    assert all(value == results[0] for value in results)

    for connection in list(fm._POOL.values()):
        connection.close()
    fm._POOL.clear()


def test_session_logger_dedupe_wal(monkeypatch, tmp_path):
    """Ensure session_logger avoids redundant WAL PRAGMA invocations."""

    monkeypatch.setenv("CODEX_SQLITE_POOL", "0")
    monkeypatch.delenv("CODEX_DB_POOL", raising=False)

    import sqlite3

    wal_calls = {"count": 0}
    orig_connect = sqlite3.connect

    class CountingConnection:
        def __init__(self, real_conn):
            self._conn = real_conn

        def execute(self, sql, *args, **kwargs):
            if "PRAGMA journal_mode=WAL" in sql:
                wal_calls["count"] += 1
            return self._conn.execute(sql, *args, **kwargs)

        def __getattr__(self, name):  # pragma: no cover - passthrough helpers
            return getattr(self._conn, name)

    def factory(*args, **kwargs):
        return CountingConnection(orig_connect(*args, **kwargs))

    monkeypatch.setattr("sqlite3.connect", factory)

    sl = importlib.reload(importlib.import_module("codex.logging.session_logger"))

    db = tmp_path / "session.db"
    sl.init_db(db)
    wal_calls["count"] = 0

    sl._fallback_log_event("SID", "user", "hello", db_path=db)

    assert wal_calls["count"] <= 1

    for connection in list(sl.CONN_POOL.values()):
        connection.close()
    sl.CONN_POOL.clear()
