import sqlite3

from src.codex.monkeypatch import log_adapters as la


def test_log_adapters_write(tmp_path):
    db = tmp_path / "codex_data.sqlite3"
    la.log_event("INFO", "test event", db_path=db)
    la.log_message("another event", db_path=db)
    con = sqlite3.connect(str(db))
    cur = con.cursor()
    cur.execute("SELECT level, message, meta FROM app_log ORDER BY id")
    rows = cur.fetchall()
    con.close()
    assert rows == [
        ("INFO", "test event", None),
        ("INFO", "another event", None),
    ]
