import os
import sqlite3

from codex.cli import _fix_pool


def test_fix_pool_enables_pooled_connect(monkeypatch, tmp_path):
    db = tmp_path / "log.db"
    monkeypatch.setenv("CODEX_LOG_DB_PATH", str(db))
    _fix_pool(max_workers=1)
    from codex.db import sqlite_patch

    assert os.getenv("CODEX_SQLITE_POOL") == "1"
    assert sqlite3.connect is sqlite_patch.pooled_connect
