import sqlite3
import threading

from src.codex.db import sqlite_patch


def test_sqlite_pool_allows_concurrent_writes(tmp_path, monkeypatch):
    """Enable CODEX_SQLITE_POOL and perform concurrent writes.

    The pooling layer should allow multiple threads to reuse a single connection
    per thread without raising database locked errors.
    """

    db = tmp_path / "pool.db"
    monkeypatch.setenv("CODEX_SQLITE_POOL", "1")
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

        # one main thread connection + 5 worker threads
        assert len(sqlite_patch._CONN_POOL) == 6

        total = sqlite3.connect(str(db)).execute("SELECT COUNT(*) FROM t").fetchone()[0]
        assert total == 100
    finally:
        sqlite_patch.disable_pooling()
        sqlite_patch._close_all()
