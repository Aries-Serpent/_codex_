import json
import sqlite3
import subprocess
import sys


def test_tail_option(tmp_path):
    db = tmp_path / "events.sqlite"
    con = sqlite3.connect(str(db))
    con.execute(
        "CREATE TABLE session_events(session_id TEXT, timestamp TEXT, role TEXT, message TEXT)"
    )
    con.executemany(
        "INSERT INTO session_events VALUES (?,?,?,?)",
        [
            ("S1", "2025-01-01T00:00:00Z", "user", "first"),
            ("S1", "2025-01-01T00:00:01Z", "assistant", "second"),
            ("S1", "2025-01-01T00:00:02Z", "user", "third"),
        ],
    )
    con.commit()
    con.close()
    cmd = [
        sys.executable,
        "-m",
        "src.codex.logging.query_logs",
        "--db",
        str(db),
        "--tail",
        "1",
        "--format",
        "json",
    ]
    cp = subprocess.run(cmd, capture_output=True, text=True)
    assert cp.returncode == 0, cp.stderr
    data = json.loads(cp.stdout)
    assert [r["message"] for r in data] == ["third"]
