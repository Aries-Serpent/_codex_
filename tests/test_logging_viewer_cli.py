# -*- coding: utf-8 -*-
import json
import sqlite3
import subprocess
import sys
from pathlib import Path


def _make_db(tmp: Path) -> Path:
    db = tmp / "logs.db"
    conn = sqlite3.connect(str(db))
    conn.execute(
        """CREATE TABLE logs(
        session_id TEXT, ts TEXT, level TEXT, message TEXT
    )"""
    )
    rows = [
        ("S-1", "2025-08-18 01:00:00", "INFO", "start session"),
        ("S-1", "2025-08-18 01:01:00", "WARN", "minor warning"),
        ("S-2", "2025-08-18 01:02:00", "INFO", "other session"),
        ("S-1", "2025-08-18 01:03:00", "ERROR", "boom"),
    ]
    conn.executemany("INSERT INTO logs VALUES (?,?,?,?)", rows)
    conn.commit()
    conn.close()
    return db


def test_cli_text_output(tmp_path: Path):
    db = _make_db(tmp_path)
    cmd = [
        sys.executable,
        "-m",
        "src.codex.logging.viewer",
        "--session-id",
        "S-1",
        "--db",
        str(db),
        "--format",
        "text",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    out = proc.stdout.strip().splitlines()
    assert out[0].endswith("start session")
    assert out[-1].endswith("boom")
    assert len(out) == 3


def test_cli_json_output(tmp_path: Path):
    db = _make_db(tmp_path)
    cmd = [
        sys.executable,
        "-m",
        "src.codex.logging.viewer",
        "--session-id",
        "S-1",
        "--db",
        str(db),
        "--format",
        "json",
        "--level",
        "ERROR",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert len(data) == 1
    assert data[0]["message"] == "boom"

