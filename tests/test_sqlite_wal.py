import sqlite3
import threading
import time


def test_wal_mode_read_while_write(tmp_path):
    db = tmp_path / "codex.sqlite"
    cxw = sqlite3.connect(db)
    cxw.execute("PRAGMA journal_mode=WAL;")
    cxw.execute("CREATE TABLE IF NOT EXISTS t(x)")
    cxw.commit()

    def writer():
        for i in range(10):
            cxw.execute("INSERT INTO t(x) VALUES(?)", (i,))
            cxw.commit()
            time.sleep(0.01)

    t = threading.Thread(target=writer)
    t.start()
    cxr = sqlite3.connect(db)
    cxr.execute("PRAGMA journal_mode=WAL;")
    rows = list(cxr.execute("SELECT COUNT(*) FROM t"))
    assert rows and isinstance(rows[0][0], int)
    t.join()
    cxw.close()
    cxr.close()
