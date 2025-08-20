import importlib
import json
import sqlite3
import subprocess
import sys


def test_import():
    mod = importlib.import_module("src.codex.logging.query_logs")
    assert hasattr(mod, "main")


def test_cli_smoke(tmp_path):
    db = tmp_path / "events.sqlite"
    con = sqlite3.connect(str(db))
    con.execute(
        "CREATE TABLE session_events("  #
        "session_id TEXT, timestamp TEXT, "
        "role TEXT, message TEXT)"
    )
    con.executemany(
        "INSERT INTO session_events VALUES (?,?,?,?)",
        [
            ("S1", "2025-01-01T00:00:00Z", "user", "hi"),
            ("S1", "2025-01-01T00:00:01Z", "assistant", "yo"),
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
        "--session-id",
        "S1",
        "--format",
        "json",
    ]
    cp = subprocess.run(cmd, capture_output=True, text=True)
    assert cp.returncode == 0, cp.stderr
    data = json.loads(cp.stdout)
    messages = [r["message"] for r in data]
    assert "hi" in messages and "yo" in messages
