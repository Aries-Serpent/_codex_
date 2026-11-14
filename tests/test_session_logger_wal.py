"""
Test Session Logger Wal

Test module for session logger wal.
"""

import sqlite3

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
    """A waiter blocked on a failing leader must be released and then succeed."""
    import threading

    db = tmp_path / "contended.sqlite"
    key = str(db)
    sl.INITIALIZED_PATHS.discard(key)

    real_connect = sqlite3.connect
    leader_inside = threading.Event()
    release_leader = threading.Event()
    calls = {"count": 0}

    def gated_connect(*args, **kwargs):
        calls["count"] += 1
        if calls["count"] == 1:
            leader_inside.set()
            release_leader.wait(timeout=10)
            raise sqlite3.OperationalError("boom")
        return real_connect(*args, **kwargs)

    monkeypatch.setattr(sl.sqlite3, "connect", gated_connect)
    errors: list[BaseException] = []
    results: list[object] = []

    def leader():
        try:
            sl.init_db(db)
        except sqlite3.OperationalError as exc:
            errors.append(exc)

    def waiter():
        results.append(sl.init_db(db))

    try:
        t_leader = threading.Thread(target=leader)
        t_leader.start()
        assert leader_inside.wait(timeout=10), "leader never started initialising"
        waiter_blocked = threading.Event()
        leader_pending = sl._INITIALIZING_PATHS[key]

        class _ObservedPending:
            def wait(self, timeout=None):
                waiter_blocked.set()
                return leader_pending.wait(timeout)

        # Replace only the waiter-visible entry; the leader keeps and sets the
        # original event, so the handshake proves the waiter is blocked on it.
        sl._INITIALIZING_PATHS[key] = _ObservedPending()
        t_waiter = threading.Thread(target=waiter)
        t_waiter.start()
        assert waiter_blocked.wait(timeout=10), "waiter never blocked on the leader"
        release_leader.set()
        t_leader.join(timeout=10)
        t_waiter.join(timeout=10)

        assert not t_waiter.is_alive(), "waiter deadlocked after leader failure"
        assert len(errors) == 1, "leader must surface its error"
        assert results == [db], "waiter must complete initialisation itself"
        assert key in sl.INITIALIZED_PATHS, "path must be marked after success"
    finally:
        release_leader.set()
        sl.INITIALIZED_PATHS.discard(key)
