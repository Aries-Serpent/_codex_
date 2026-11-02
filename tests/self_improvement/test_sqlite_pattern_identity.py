"""Session pattern identifiers remain opaque TEXT in the maintained adapters."""

from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any

import pytest

from aries_serpent_core.logging.pattern_event_recorder import PatternEventRecorder
from aries_serpent_core.logging.session_database import SessionDatabase
from aries_serpent_core.logging.session_db import SessionDB

Adapter = SessionDatabase | SessionDB
AdapterType = type[SessionDatabase] | type[SessionDB]
ADAPTERS = [SessionDatabase, SessionDB]
IDENTIFIERS = ("RP-019", "0012", "12", "000", "0", "pattern'); DROP TABLE sessions; --")


def _session(session_id: str, identifiers: tuple[str | int, ...] = ()) -> dict[str, Any]:
    return {
        "session_id": session_id,
        "timestamp": "2026-11-02T00:00:00Z",
        "status": "pending",
        "patterns": [
            {"pattern_id": identifier, "pattern_name": "identity", "success": True}
            for identifier in identifiers
        ],
    }


def _record(db: Adapter, session_id: str, pattern_id: str) -> bool:
    recorder = db if isinstance(db, SessionDB) else PatternEventRecorder(db)
    return recorder.add_pattern_to_session(session_id, pattern_id, "identity", success=True)


def _raw_rows(path: Path) -> list[tuple[Any, ...]]:
    with closing(sqlite3.connect(path)) as connection:
        return connection.execute(
            "SELECT *, typeof(pattern_id) FROM session_patterns ORDER BY id"
        ).fetchall()


def _identifiers(db: Adapter, session_id: str) -> list[str]:
    details = db.get_session_with_details(session_id)
    assert details is not None
    return [pattern["pattern_id"] for pattern in details["patterns"]]


@pytest.mark.parametrize("adapter_type", ADAPTERS, ids=lambda adapter: adapter.__name__)
@pytest.mark.parametrize("writer", ["insert", "recorder"])
def test_text_identity_survives_closed_connections_and_reopen(
    tmp_path: Path, adapter_type: AdapterType, writer: str
) -> None:
    path = tmp_path / "sessions.db"
    db = adapter_type(str(path))
    if writer == "insert":
        assert db.insert_session(_session("identity", IDENTIFIERS)) is True
    else:
        assert db.insert_session(_session("identity")) is True
        for identifier in IDENTIFIERS:
            assert _record(db, "identity", identifier) is True

    before = _raw_rows(path)
    assert [row[2] for row in before] == list(IDENTIFIERS)
    assert all(row[-1] == "text" for row in before)
    assert _identifiers(db, "identity") == list(IDENTIFIERS)

    # Adapter operations close their connections; reopening must not normalize rows.
    database = db._database if isinstance(db, SessionDB) else db
    with database.get_connection() as connection:
        columns = connection.execute("PRAGMA table_info(session_patterns)").fetchall()
    with pytest.raises(sqlite3.ProgrammingError, match="closed"):
        connection.execute("SELECT 1")
    assert next(column[2] for column in columns if column[1] == "pattern_id") == "TEXT"
    del database, db

    reopened = adapter_type(str(path))
    assert _identifiers(reopened, "identity") == list(IDENTIFIERS)
    assert _raw_rows(path) == before


@pytest.mark.parametrize("adapter_type", ADAPTERS, ids=lambda adapter: adapter.__name__)
def test_legacy_numeric_insert_uses_text_affinity_without_collapsing_leading_zeros(
    tmp_path: Path, adapter_type: AdapterType
) -> None:
    path = tmp_path / "sessions.db"
    db = adapter_type(str(path))
    assert db.insert_session(_session("numeric", (12, "0012", "12", 0, "000", "0"))) is True
    before = _raw_rows(path)
    expected = ["12", "0012", "12", "0", "000", "0"]
    assert [row[2] for row in before] == expected
    assert all(row[-1] == "text" for row in before)
    del db

    reopened = adapter_type(str(path))
    assert _identifiers(reopened, "numeric") == expected
    assert _raw_rows(path) == before


@pytest.mark.parametrize("adapter_type", ADAPTERS, ids=lambda adapter: adapter.__name__)
@pytest.mark.parametrize("writer", ["insert", "recorder"])
def test_pattern_write_errors_propagate_without_partial_rows(
    tmp_path: Path, adapter_type: AdapterType, writer: str
) -> None:
    path = tmp_path / "sessions.db"
    db = adapter_type(str(path))
    assert db.insert_session(_session("existing", ("0007",))) is True
    before = _raw_rows(path)
    with closing(sqlite3.connect(path)) as connection:
        connection.execute(
            "CREATE TRIGGER reject_pattern BEFORE INSERT ON session_patterns "
            "BEGIN SELECT RAISE(ABORT, 'injected pattern write failure'); END"
        )
        connection.commit()

    with pytest.raises(sqlite3.IntegrityError, match="injected pattern write failure"):
        if writer == "insert":
            db.insert_session(_session("rejected", ("RP-019",)))
        else:
            _record(db, "existing", "RP-019")
    assert db.get_session("rejected") is None
    assert _raw_rows(path) == before
    del db

    reopened = adapter_type(str(path))
    assert reopened.get_session("rejected") is None
    assert _identifiers(reopened, "existing") == ["0007"]
    assert _raw_rows(path) == before


@pytest.mark.parametrize("adapter_type", ADAPTERS, ids=lambda adapter: adapter.__name__)
def test_recorder_foreign_key_errors_are_not_reported_as_success(
    tmp_path: Path, adapter_type: AdapterType
) -> None:
    path = tmp_path / "sessions.db"
    db = adapter_type(str(path))
    with pytest.raises(sqlite3.IntegrityError, match="FOREIGN KEY"):
        _record(db, "missing-session", "0012")
    del db

    reopened = adapter_type(str(path))
    assert reopened.get_session("missing-session") is None
    assert _raw_rows(path) == []
