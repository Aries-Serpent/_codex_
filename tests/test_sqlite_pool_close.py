"""Tests for SQLite connection pool cleanup."""

import sqlite3

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
        "Connection should be removed from pool on close",
    )

    conn2 = sqlite3.connect(str(db))
    assert conn2 is not conn, "New connection should be a fresh instance"
    sqlite_patch.disable_pooling()


def test_proxy_close_handles_varied_pool_types():
    """Proxy ``close`` cleans up pools implemented as dict, set or list."""

    key = ("db", 0, 0, "")
    original_pool = sqlite_patch._CONN_POOL
    try:
        for pool in (dict(), set(), list()):
            sqlite_patch._CONN_POOL = pool
            conn = sqlite3.connect(":memory:")
            if isinstance(pool, dict):
                pool[key] = conn
            elif isinstance(pool, set):
                pool.add(conn)
            else:  # list
                pool.append(conn)
            proxy = sqlite_patch.PooledConnectionProxy(conn, key)
            proxy.close()
            assert not pool
    finally:
        sqlite_patch._CONN_POOL = original_pool

