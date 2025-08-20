import json
import sqlite3

import pytest

from src.codex.logging.config import DEFAULT_LOG_DB
from src.codex.logging.export import export_session


def test_export_session(tmp_path, monkeypatch):
    db = tmp_path / DEFAULT_LOG_DB
    db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db) as c:
        c.execute(
            "CREATE TABLE session_events("
            "session_id TEXT, timestamp TEXT, role TEXT, message TEXT)"
        )
        c.executemany(
            "INSERT INTO session_events VALUES (?,?,?,?)",
            [
                ("s1", "2024-01-01T00:00:00", "user", "hi"),
                ("s1", "2024-01-01T00:01:00", "assistant", "hello"),
            ],
        )
    monkeypatch.setenv("CODEX_LOG_DB_PATH", str(db))
    js = export_session("s1", "json")
    data = json.loads(js)
    assert data[0]["message"] == "hi"
    txt = export_session("s1", "text")
    assert "user" in txt and "assistant" in txt


@pytest.mark.parametrize("session_id", ["abc", "ABC_123", "a-b_c-9"])
def test_export_session_id_good(session_id, monkeypatch):
    monkeypatch.setattr("src.codex.logging.export._fetch_events", lambda db, sid: [])
    assert export_session(session_id) == "[]"


@pytest.mark.parametrize("session_id", ["..", "a b", "abc!", "../../etc/passwd"])
def test_export_session_id_bad(session_id, monkeypatch):
    monkeypatch.setattr("src.codex.logging.export._fetch_events", lambda db, sid: [])
    with pytest.raises(ValueError):
        export_session(session_id)
