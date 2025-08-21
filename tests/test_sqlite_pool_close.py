"""Tests for SQLite connection pool cleanup."""

import sqlite3

import pytest

from src.codex.db import sqlite_patch


def test_sqlite_pool_close(tmp_path, monkeypatch):
    """Connections closed manually remain in the pool until ``_close_all``."""

    db = tmp_path / "pool.db"
    monkeypatch.setenv("CODEX_SQLITE_POOL", "1")
    sqlite_patch.auto_enable_from_env()

    conn = sqlite3.connect(str(db))
    conn.execute("CREATE TABLE t(x INTEGER)")
    conn.close()

    with pytest.raises(sqlite3.ProgrammingError):
        conn.execute("SELECT 1")
    assert sqlite_patch._CONN_POOL, "Closed connection should remain in pool"

    sqlite_patch._close_all()
    assert not sqlite_patch._CONN_POOL
    sqlite_patch.disable_pooling()
