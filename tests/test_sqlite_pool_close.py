"""Tests for SQLite connection pool cleanup."""

import sqlite3

import pytest

from src.codex.db import sqlite_patch


def test_sqlite_pool_close(tmp_path, monkeypatch):
    """Connections closed manually are removed from the pool."""

    db = tmp_path / "pool.db"
    monkeypatch.setenv("CODEX_SQLITE_POOL", "1")
    sqlite_patch.auto_enable_from_env()

    conn = sqlite3.connect(str(db))
    conn.execute("CREATE TABLE t(x INTEGER)")
    conn.close()

    assert not sqlite_patch._CONN_POOL, (
        "Connection should be removed from pool on close"
    )

    conn2 = sqlite3.connect(str(db))
    assert conn2 is not conn, "New connection should be a fresh instance"
    sqlite_patch.disable_pooling()
