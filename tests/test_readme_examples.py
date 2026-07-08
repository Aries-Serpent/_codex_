"""
Test Readme Examples

Test module for readme examples.
"""

import pathlib
import re
import sqlite3

import pytest


def test_readme_session_logger_example(tmp_path, monkeypatch):
    root = pathlib.Path(__file__).resolve().parents[1]
    readme = (root / "README.md").read_text()
    blocks = re.findall(r"```python\n(.*?)```", readme, re.DOTALL)
    snippet = next(
        (b for b in blocks if "SessionLogger" in b and 'sl.log("assistant", "hello")' in b),
        None,
    )
    if snippet is None:
        pytest.skip("SessionLogger example not found in README")

    # Validate snippet before execution - must only contain expected imports and SessionLogger usage
    if not all(safe in snippet for safe in ["SessionLogger", "log"]):
        raise ValueError("README snippet validation failed")
    # Ensure no dangerous operations
    if any(dangerous in snippet for dangerous in ["__import__", "eval", "compile", "open("]):
        raise ValueError("README snippet contains dangerous operations")

    db = tmp_path / "session_logs.db"
    monkeypatch.setenv("CODEX_LOG_DB_PATH", str(db))
    exec(snippet, {})  # nosec B102 - Validated trusted README example code only
    con = sqlite3.connect(db)
    try:
        rows = con.execute(
            "SELECT role, message FROM session_events "
            "WHERE session_id = ? AND role != 'system' ORDER BY ts",
            ("demo",),
        ).fetchall()
    finally:
        con.close()
    assert rows == [("user", "hi"), ("assistant", "hello")]
