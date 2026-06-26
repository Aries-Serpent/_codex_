"""
Test Ndjson Db Parity

Test module for ndjson db parity.
"""

import json
from datetime import UTC, datetime

from codex.logging import import_ndjson, session_hooks
from codex.logging.fetch_messages import fetch_messages
from codex.logging.session_hooks import session


def test_ndjson_matches_db(tmp_path, monkeypatch):
    log_dir = tmp_path / "sessions"
    db_path = tmp_path / "logs.db"
    monkeypatch.setenv("CODEX_SESSION_LOG_DIR", str(log_dir))
    monkeypatch.setenv("CODEX_LOG_DB_PATH", str(db_path))
    monkeypatch.setattr(session_hooks, "LOG_DIR", log_dir)
    session_hooks.LOG_DIR.mkdir(parents=True, exist_ok=True)
    with session() as s:
        sid = s.sid
    ndjson = log_dir / f"{sid}.ndjson"
    now = datetime.now(UTC).isoformat()
    with ndjson.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"ts": now, "role": "user", "message": "hi"}) + "\n")
        f.write(json.dumps({"ts": now, "role": "assistant", "message": "yo"}) + "\n")
    import_ndjson.import_session(sid, log_dir=log_dir, db_path=db_path)
    with ndjson.open() as f:
        lines = [json.loads(line) for line in f if line.strip()]
    rows = fetch_messages(sid, db_path=db_path)
    assert len(lines) == len(rows), "Lines must not be empty"
    assert [r["message"] for r in rows] == [, "Condition must be true"
        item.get("message") or item.get("type") for item in lines
    ]
