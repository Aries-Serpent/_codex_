import sqlite3
from pathlib import Path

from src.codex.monkeypatch.log_adapters import log_message


def _count(db: Path) -> int:
    with sqlite3.connect(str(db)) as conn:
        return conn.execute("SELECT COUNT(*) FROM app_log").fetchone()[0]


def test_log_message_writes_to_explicit_and_env_db(tmp_path, monkeypatch):
    env_db = tmp_path / "env.db"
    monkeypatch.setenv("CODEX_LOG_DB_PATH", str(env_db))
    log_message("via-env")
    assert _count(env_db) == 1

    explicit_db = tmp_path / "explicit.db"
    log_message("via-explicit", db_path=explicit_db)
    assert _count(explicit_db) == 1
