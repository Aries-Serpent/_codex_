import os
import sqlite3
import subprocess
import sys
from pathlib import Path


def _run_cli(db: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
    cmd = [
        sys.executable,
        "-m",
        "codex.logging.session_query",
        "--db",
        str(db),
        *extra_args,
    ]
    env = os.environ.copy()
    src_dir = Path(__file__).resolve().parents[1] / "src"
    env["PYTHONPATH"] = os.pathsep.join([str(src_dir), env.get("PYTHONPATH", "")])
    return subprocess.run(cmd, capture_output=True, text=True, env=env)


def test_session_query_cli(tmp_path):
    db = tmp_path / "events.db"
    with sqlite3.connect(db) as con:
        con.execute(
            "CREATE TABLE session_events("
            "timestamp TEXT, session_id TEXT, role TEXT, "
            "message TEXT, seq INTEGER, meta TEXT)"
        )
        con.executemany(
            "INSERT INTO session_events(timestamp, session_id, role, message) " "VALUES (?,?,?,?)",
            [
                ("2025-01-01T00:00:00Z", "S1", "user", "hi"),
                ("2025-01-01T00:00:01Z", "S1", "assistant", "yo"),
            ],
        )

    proc = _run_cli(db, "--session-id", "S1")
    assert proc.returncode == 0, proc.stderr
    lines = proc.stdout.strip().splitlines()
    expected = [
        "timestamp\tsession_id\trole\tmessage",
        "2025-01-01T00:00:00Z\tS1\tuser\thi",
        "2025-01-01T00:00:01Z\tS1\tassistant\tyo",
    ]
    assert lines == expected


def test_session_query_cli_session_with_last(tmp_path):
    db = tmp_path / "events.db"
    with sqlite3.connect(db) as con:
        con.execute(
            "CREATE TABLE session_events("
            "timestamp TEXT, session_id TEXT, role TEXT, "
            "message TEXT, seq INTEGER, meta TEXT)"
        )
        con.executemany(
            "INSERT INTO session_events(timestamp, session_id, role, message) " "VALUES (?,?,?,?)",
            [
                ("2025-01-01T00:00:00Z", "S1", "user", "hi"),
                ("2025-01-01T00:00:01Z", "S1", "assistant", "yo"),
                ("2025-01-01T00:00:02Z", "S1", "tool", "step"),
                ("2025-01-01T00:00:03Z", "S2", "user", "other"),
            ],
        )

    proc = _run_cli(db, "--session-id", "S1", "--last", "2")
    assert proc.returncode == 0, proc.stderr
    lines = proc.stdout.strip().splitlines()
    expected = [
        "timestamp\tsession_id\trole\tmessage",
        "2025-01-01T00:00:01Z\tS1\tassistant\tyo",
        "2025-01-01T00:00:02Z\tS1\ttool\tstep",
    ]
    assert lines == expected
