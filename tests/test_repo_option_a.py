import sqlite3

import pytest

from tools.build_sqlite_snapshot import ARTIFACT_DB, build_snapshot


def test_build_snapshot_and_search_and_immutable():
    if ARTIFACT_DB.exists():
        ARTIFACT_DB.unlink()
    build_snapshot()
    assert ARTIFACT_DB.exists()
    con = sqlite3.connect(ARTIFACT_DB)
    try:
        rows = con.execute(
            "SELECT body FROM snippet_fts WHERE snippet_fts MATCH ?",
            ("hello",),
        ).fetchall()
    finally:
        con.close()
    assert ("hello world",) in rows
    con = sqlite3.connect(f"file:{ARTIFACT_DB}?immutable=1", uri=True)
    with pytest.raises(sqlite3.OperationalError):
        con.execute("INSERT INTO snippet(body) VALUES ('new')")
    con.close()
