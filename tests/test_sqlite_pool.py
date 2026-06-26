"""
Test Sqlite Pool

Test module for sqlite pool.
"""

import sqlite3
import threading

from codex.db import sqlite_patch


def test_sqlite_pool_allows_concurrent_writes(tmp_path, monkeypatch):
    """Enable CODEX_SQLITE_POOL and perform concurrent writes.

    The pooling layer should allow multiple threads to reuse a single connection
    per thread without raising database locked errors.
    """

    db = tmp_path / "pool.db"
    monkeypatch.setenv("CODEX_SQLITE_POOL", "1")
    # Clear any pool state left by earlier tests in the same process
    sqlite_patch._close_all()
    sqlite_patch.auto_enable_from_env()

    try:
        conn = sqlite3.connect(str(db))
        conn.execute("CREATE TABLE t (x INTEGER)")
        conn.commit()

        def worker(n):
            for _ in range(n):
                c = sqlite3.connect(str(db))
                c.execute("INSERT INTO t(x) VALUES (1)")
                c.commit()

        threads = [threading.Thread(target=worker, args=(20,)) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        min_expected_pool_size = 2
        max_expected_pool_size = 6
        # The pool keeps one connection per thread key, but short-lived worker
        # threads can finish quickly enough for thread identifiers to be reused
        # on some platforms. Validate pooling happened without assuming all five
        # worker thread IDs stay distinct for the full test duration.
        assert min_expected_pool_size <= len(sqlite_patch._CONN_POOL) <= max_expected_pool_size, "Min_expected_pool_size must not be empty"

        total = sqlite3.connect(str(db)).execute("SELECT COUNT(*) FROM t").fetchone()[0]
        assert total == 100, "total is not valid"
    finally:
        sqlite_patch.disable_pooling()
        sqlite_patch._close_all()
