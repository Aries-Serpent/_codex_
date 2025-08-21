import importlib
import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path


def test_import():
    mod = importlib.import_module("codex.logging.query_logs")
    assert hasattr(mod, "main")


def test_cli_smoke(tmp_path):
    db = tmp_path / "events.sqlite"
    con = sqlite3.connect(str(db))
    con.execute(
        "CREATE TABLE session_events("  #
        "session_id TEXT, timestamp TEXT, "
        "role TEXT, message TEXT, seq INTEGER, meta TEXT)"
    )
    con.executemany(
        "INSERT INTO session_events(session_id, timestamp, role, message) "
        "VALUES (?,?,?,?)",
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
        "codex.logging.query_logs",
        "--db",
        str(db),
        "--session-id",
        "S1",
        "--format",
        "json",
    ]
    env = os.environ.copy()
    src_dir = Path(__file__).resolve().parents[1] / "src"
    env["PYTHONPATH"] = os.pathsep.join([str(src_dir), env.get("PYTHONPATH", "")])
    cp = subprocess.run(cmd, capture_output=True, text=True, env=env)
    assert cp.returncode == 0, cp.stderr
    data = json.loads(cp.stdout)
    messages = [r["message"] for r in data]
    assert "hi" in messages and "yo" in messages
