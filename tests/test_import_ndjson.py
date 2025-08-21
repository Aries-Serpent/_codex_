import json
import sqlite3
from pathlib import Path

from codex.logging import import_ndjson


def _write_ndjson(path: Path, events: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for obj in events:
            f.write(json.dumps(obj) + "\n")


def test_import_session_and_watermark(tmp_path, monkeypatch):
    session_id = "S1"
    sessions_dir = tmp_path / ".codex" / "sessions"
    ndjson_file = sessions_dir / f"{session_id}.ndjson"
    events = [
        {
            "ts": "2024-01-01T00:00:00Z",
            "type": "session_start",
            "session_id": session_id,
        },
        {"ts": "2024-01-01T00:00:01Z", "type": "session_end", "session_id": session_id},
    ]
    _write_ndjson(ndjson_file, events)

    db_path = tmp_path / "session.db"
    monkeypatch.setenv("CODEX_SESSION_LOG_DIR", str(sessions_dir))
    monkeypatch.setenv("CODEX_LOG_DB_PATH", str(db_path))

    # first import
    inserted = import_ndjson.import_session(session_id)
    assert inserted == 2

    # re-import should be idempotent
    inserted = import_ndjson.import_session(session_id)
    assert inserted == 0

    # append new event and re-import
    with ndjson_file.open("a", encoding="utf-8") as f:
        f.write(
            json.dumps({"ts": "2024-01-01T00:00:02Z", "role": "user", "message": "hi"})
            + "\n"
        )
    inserted = import_ndjson.import_session(session_id)
    assert inserted == 1

    con = sqlite3.connect(str(db_path))
    try:
        rows = list(
            con.execute(
                "SELECT session_id, seq, message FROM session_events ORDER BY seq"
            )
        )
        assert rows == [
            (session_id, 1, "session_start"),
            (session_id, 2, "session_end"),
            (session_id, 3, "hi"),
        ]
        wm = con.execute(
            "SELECT seq FROM session_ingest_watermark WHERE session_id=?",
            (session_id,),
        ).fetchone()[0]
        assert wm == 3
        idxs = con.execute("PRAGMA index_list('session_events')").fetchall()
        assert any(r[1] == "session_events_sid_ts_idx" for r in idxs)
    finally:
        con.close()
