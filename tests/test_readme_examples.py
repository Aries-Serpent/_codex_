import pathlib
import re
import sqlite3


def test_readme_session_logger_example(tmp_path, monkeypatch):
    readme = pathlib.Path("README.md").read_text()
    blocks = re.findall(r"```python\n(.*?)```", readme, re.DOTALL)
    snippet = next(
        b
        for b in blocks
        if "SessionLogger" in b and 'sl.log("assistant", "hello")' in b
    )
    db = tmp_path / "session_logs.db"
    monkeypatch.setenv("CODEX_LOG_DB_PATH", str(db))
    exec(snippet, {})
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
