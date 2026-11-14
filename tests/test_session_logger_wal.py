"""
Test Session Logger Wal

Test module for session logger wal.
"""

import sqlite3
import threading

import pytest

from codex.logging import session_logger as sl


def test_session_logger_enables_wal(tmp_path):
    db = tmp_path / "logs.sqlite"
    sl.init_db(db)
    conn = sqlite3.connect(db)
    mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
    conn.close()
    assert mode.lower() == "wal", "Condition must be true"


def test_init_db_marks_path_only_after_success(monkeypatch, tmp_path):
    """A failing initialization should not mark the path as ready."""

    db = tmp_path / "flaky.sqlite"
    key = str(db)
    sl.INITIALIZED_PATHS.discard(key)

    real_connect = sqlite3.connect
    calls = {"count": 0}

    def flaky_connect(*args, **kwargs):
        calls["count"] += 1
        if calls["count"] == 1:
            raise sqlite3.OperationalError("boom")
        return real_connect(*args, **kwargs)

    monkeypatch.setattr(sl.sqlite3, "connect", flaky_connect)

    try:
        with pytest.raises(sqlite3.OperationalError):
            sl.init_db(db)
        assert key not in sl.INITIALIZED_PATHS, "Condition must be true"

        result = sl.init_db(db)
        assert result == db, "Result must not be empty"
        assert key in sl.INITIALIZED_PATHS, "Condition must be true"
    finally:
        sl.INITIALIZED_PATHS.discard(key)


def test_init_db_failed_leader_releases_concurrent_waiter(monkeypatch, tmp_path):
    db = tmp_path / "contended.sqlite"
    key = str(db)
    real_connect = sqlite3.connect
    leader_inside = threading.Event()
    release_leader = threading.Event()
    waiter_inside = threading.Event()
    errors = []
    results = []
    calls = 0

    def gated_connect(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 1:
            leader_inside.set()
            if not release_leader.wait(timeout=5):
                raise TimeoutError("leader was not released")
            raise sqlite3.OperationalError("boom")
        return real_connect(*args, **kwargs)

    def leader():
        try:
            sl.init_db(db)
        except sqlite3.OperationalError as exc:
            errors.append(exc)

    def waiter():
        try:
            results.append(sl.init_db(db))
        except Exception as exc:
            errors.append(exc)

    monkeypatch.setattr(sl.sqlite3, "connect", gated_connect)
    t_leader = threading.Thread(target=leader, daemon=True)
    t_waiter = threading.Thread(target=waiter, daemon=True)
    try:
        t_leader.start()
        assert leader_inside.wait(timeout=5)
        pending = sl._INITIALIZING_PATHS[key]
        real_wait = pending.wait

        def observed_wait(*args, **kwargs):
            waiter_inside.set()
            return real_wait(*args, **kwargs)

        monkeypatch.setattr(pending, "wait", observed_wait)
        t_waiter.start()
        assert waiter_inside.wait(timeout=5)
        release_leader.set()
        t_leader.join(timeout=5)
        t_waiter.join(timeout=5)
        assert not t_leader.is_alive()
        assert not t_waiter.is_alive(), "waiter deadlocked after leader failure"
        assert len(errors) == 1 and isinstance(errors[0], sqlite3.OperationalError)
        assert results == [db]
        assert key in sl.INITIALIZED_PATHS
    finally:
        release_leader.set()
        sl.INITIALIZED_PATHS.discard(key)


def test_init_db_mkdir_failure_releases_path_for_retry(monkeypatch, tmp_path):
    db = tmp_path / "new" / "events.sqlite"
    key = str(db)
    real_mkdir = type(db).mkdir
    calls = 0

    def fail_once(path, *args, **kwargs):
        nonlocal calls
        if path == db.parent and calls == 0:
            calls += 1
            raise PermissionError("test failure")
        return real_mkdir(path, *args, **kwargs)

    monkeypatch.setattr(type(db), "mkdir", fail_once)
    try:
        with pytest.raises(PermissionError, match="test failure"):
            sl.init_db(db)
        assert key not in sl._INITIALIZING_PATHS
        assert key not in sl.INITIALIZED_PATHS
        assert sl.init_db(db) == db
        assert key in sl.INITIALIZED_PATHS
    finally:
        sl.INITIALIZED_PATHS.discard(key)
