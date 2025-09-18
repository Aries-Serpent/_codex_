import sqlite3

import pytest

from codex.logging import session_logger as sl


def test_session_logger_enables_wal(tmp_path):
    db = tmp_path / "logs.sqlite"
    sl.init_db(db)
    conn = sqlite3.connect(db)
    mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
    conn.close()
    assert mode.lower() == "wal"


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
        assert key not in sl.INITIALIZED_PATHS

        result = sl.init_db(db)
        assert result == db
        assert key in sl.INITIALIZED_PATHS
    finally:
        sl.INITIALIZED_PATHS.discard(key)
