"""Disposable CLI coverage for the separate numeric CI issue-pattern domain."""

import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

RECORDER = Path(__file__).resolve().parents[2] / "scripts/ci/pattern_recorder.py"


def invoke(db: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(RECORDER), "--db", str(db), *args],
        capture_output=True,
        text=True,
        timeout=15,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )


def insert(db: Path, identity: str) -> subprocess.CompletedProcess[str]:
    return invoke(
        db,
        "--session",
        "0012'; DROP TABLE patterns; --",
        "insert",
        "--pattern-id",
        identity,
        "--pattern-name",
        "Line Length",
        "--description",
        "Disposable identity-domain fixture, not a measured improvement",
    )


def test_numeric_cli_roundtrip_reopens_without_session_id_coercion(tmp_path):
    db = tmp_path / "patterns.db"
    assert insert(db, "0012").returncode == 0
    assert insert(db, "12").returncode == 0
    with sqlite3.connect(db) as conn:
        rows = conn.execute(
            "SELECT pattern_id, typeof(pattern_id), session FROM patterns ORDER BY id"
        ).fetchall()
    assert rows == [(12, "integer", "0012'; DROP TABLE patterns; --")] * 2
    exported = invoke(db, "export")
    assert exported.returncode == 0
    data = json.loads(exported.stdout)
    assert [row["pattern_id"] for row in data["occurrences"]] == [12, 12]
    query = invoke(db, "query", "--session", "0012'; DROP TABLE patterns; --")
    assert query.returncode == 0
    assert query.stdout.count("Line Length") == 2


def test_opaque_pattern_rejected_before_database_creation(tmp_path):
    db = tmp_path / "absent" / "patterns.db"
    result = insert(db, "RP-019")
    assert result.returncode != 0
    assert "invalid int value" in result.stderr
    assert not db.parent.exists()


def test_failed_cli_write_is_explicit_and_preserves_rows(tmp_path):
    db = tmp_path / "patterns.db"
    assert insert(db, "12").returncode == 0
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TRIGGER reject_insert BEFORE INSERT ON patterns "
            "BEGIN SELECT RAISE(ABORT, 'fixture write denied'); END"
        )
        conn.commit()
        before = conn.execute("SELECT * FROM patterns").fetchall()
    result = insert(db, "18")
    assert result.returncode != 0
    assert "fixture write denied" in result.stderr
    with sqlite3.connect(db) as conn:
        assert conn.execute("SELECT * FROM patterns").fetchall() == before
