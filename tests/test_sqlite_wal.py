import sqlite3
import threading
import time


def test_wal_mode_read_while_write(tmp_path):
    db = tmp_path / "codex.sqlite"
    init = sqlite3.connect(db)
    init.execute("PRAGMA journal_mode=WAL;")
    init.execute("CREATE TABLE t(x)")
    init.commit()
    init.close()

    def writer():
        with sqlite3.connect(db) as w:
            w.execute("PRAGMA journal_mode=WAL;")
            for i in range(5):
                w.execute("INSERT INTO t(x) VALUES(?)", (i,))
                w.commit()
                time.sleep(0.01)

    t = threading.Thread(target=writer)
    t.start()
    cxr = sqlite3.connect(db)
    cxr.execute("PRAGMA journal_mode=WAL;")
    rows = list(cxr.execute("SELECT COUNT(*) FROM t"))
    assert rows and isinstance(rows[0][0], int)
    t.join()
    cxr.close()
