import sqlite3
from pathlib import Path

from src.codex.monkeypatch.log_adapters import log_message


def _count(db: Path) -> int:
    with sqlite3.connect(str(db)) as conn:
        return conn.execute("SELECT COUNT(*) FROM app_log").fetchone()[0]


def test_log_message_writes_to_env_and_default_db(tmp_path, monkeypatch):
    env_db = tmp_path / "env.db"
    env_db.parent.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("CODEX_LOG_DB_PATH", str(env_db))
    used_env = log_message("via-env")
    assert used_env == env_db
    assert _count(env_db) == 1

    monkeypatch.delenv("CODEX_LOG_DB_PATH", raising=False)
    monkeypatch.chdir(tmp_path)
    default_db = tmp_path / ".codex" / "session_logs.db"
    default_db.parent.mkdir(parents=True, exist_ok=True)
    used_default = log_message("via-default")
    assert used_default.resolve() == default_db.resolve()
    assert _count(default_db) == 1
