import os
import sqlite3
import subprocess
import sys
from pathlib import Path


def test_session_query_cli(tmp_path):
    db = tmp_path / "events.db"
    con = sqlite3.connect(str(db))
    con.execute(
        "CREATE TABLE session_events(timestamp TEXT, session_id TEXT, role TEXT, message TEXT)"
    )
    rows = [
        ("2025-01-01T00:00:00Z", "S1", "user", "hi"),
        ("2025-01-01T00:00:01Z", "S1", "assistant", "yo"),
    ]
    con.executemany("INSERT INTO session_events VALUES (?,?,?,?)", rows)
    con.commit()
    con.close()

    cmd = [
        sys.executable,
        "-m",
        "codex.logging.session_query",
        "--session-id",
        "S1",
        "--db",
        str(db),
    ]
    env = os.environ.copy()
    src_dir = Path(__file__).resolve().parents[1] / "src"
    env["PYTHONPATH"] = os.pathsep.join([str(src_dir), env.get("PYTHONPATH", "")])
    proc = subprocess.run(cmd, capture_output=True, text=True, env=env)
    assert proc.returncode == 0, proc.stderr
    lines = proc.stdout.strip().splitlines()
    assert lines[0].split("\t") == ["timestamp", "session_id", "role", "message"]
    assert lines[1].endswith("\thi")
    assert lines[2].endswith("\tyo")
    assert len(lines) == 3
