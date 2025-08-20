import importlib
import sqlite3
import sys
from pathlib import Path


def test_session_logger_falls_back_to_log_adapters(monkeypatch, tmp_path):
    repo_root = Path(__file__).resolve().parents[1]
    monkeypatch.syspath_prepend(str(repo_root / "src"))
    monkeypatch.setitem(sys.modules, "src.codex.logging.db", None)
    monkeypatch.delitem(sys.modules, "src.codex.logging.session_logger", raising=False)
    monkeypatch.delitem(sys.modules, "codex.monkeypatch.log_adapters", raising=False)
    db = tmp_path / "codex_data.sqlite3"
    monkeypatch.setenv("CODEX_LOG_DB_PATH", str(db))

    sl = importlib.import_module("src.codex.logging.session_logger")

    sl.log_message("S1", "user", "hello")
    with sl.SessionLogger(session_id="S2") as logger:
        logger.log("assistant", "hi")

    con = sqlite3.connect(str(db))
    cur = con.cursor()
    cur.execute("SELECT level, message, meta FROM app_log")
    rows = cur.fetchall()
    con.close()

    assert ("S1", "user", "hello") in rows
    assert ("S2", "system", "session_start") in rows
    assert ("S2", "assistant", "hi") in rows
