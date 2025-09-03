import sqlite3

from codex.logging import session_logger as sl


def test_session_logger_enables_wal(tmp_path):
    db = tmp_path / "logs.sqlite"
    sl.init_db(db)
    conn = sqlite3.connect(db)
    mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
    conn.close()
    assert mode.lower() == "wal"
