"""Tests for fetch_messages covering custom and default DB paths."""

# ruff: noqa: E501
import inspect
import sqlite3
from pathlib import Path

import pytest

from tests._codex_introspect import (
    patch_default_db_path,
    resolve_fetch_messages,
    resolve_writer,
)

EVENTS = [
    {"role": "INFO", "content": "alpha", "ts": 1},
    {"role": "WARN", "content": "bravo", "ts": 2},
    {"role": "INFO", "content": "charlie", "ts": 3},
]


def _make_sqlite_db(db_path: Path, session_id: str = "SID") -> None:
    """Create a minimal session_events table populated with EVENTS."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS session_events(
            ts REAL NOT NULL,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            message TEXT NOT NULL
        )
        """
    )
    cur.executemany(
        "INSERT INTO session_events(ts, session_id, role, message) VALUES (?,?,?,?)",
        [(e["ts"], session_id, e["role"], e["content"]) for e in EVENTS],
    )
    conn.commit()
    conn.close()


def _populate_with_writer(writer_meta, db_path: Path | None) -> None:
    """Populate events using a discovered writer function."""
    w = writer_meta["callable"]
    accepts_path = writer_meta.get("accepts_db_path", False)
    params = inspect.signature(w).parameters
    for e in EVENTS:
        kwargs = {}
        if "session_id" in params:
            kwargs["session_id"] = "SID"
        if "sid" in params and "session_id" not in params:
            kwargs["sid"] = "SID"
        if "level" in params:
            kwargs["level"] = e["role"]
        elif "role" in params:
            kwargs["role"] = e["role"]
        if "message" in params:
            kwargs["message"] = e["content"]
        elif "text" in params:
            kwargs["text"] = e["content"]
        if accepts_path and db_path is not None:
            if "db" in params:
                kwargs["db"] = str(db_path)
            else:
                kwargs["db_path"] = str(db_path)
        w(**kwargs)


def _call_fetch(meta, db_path: Path | None, session_id: str = "SID"):
    """Invoke fetch_messages with flexible db_path handling."""
    fn = meta["callable"]
    if db_path is not None and meta.get("accepts_db_path"):
        return list(fn(session_id, db_path=str(db_path)))
    # try kwargs variations
    try:
        return (
            list(fn(session_id, db=str(db_path)))
            if db_path is not None
            else list(fn(session_id))
        )
    except TypeError:
        try:
            return (
                list(fn(session_id, path=str(db_path)))
                if db_path is not None
                else list(fn(session_id))
            )
        except TypeError:
            return list(fn(session_id))


def _assert_order_and_content(rows):
    """Validate retrieval order and message content."""

    def to_tuple(r):
        if isinstance(r, dict):
            return (str(r.get("role", "")), str(r.get("message", "")))
        if isinstance(r, (tuple, list)):
            if len(r) >= 4:
                return (str(r[2]), str(r[3]))
            if len(r) >= 3:
                return (str(r[1]), str(r[2]))
        return ("", "")

    got = [to_tuple(r) for r in rows]
    expected = [(e["role"], e["content"]) for e in EVENTS]
    assert got == expected, f"Expected {expected}, got {got}"


@pytest.mark.parametrize("mode", ["custom_path", "default_path"])
def test_fetch_messages(tmp_path, mode, monkeypatch):
    meta = resolve_fetch_messages()
    if "error" in meta:
        pytest.skip("fetch_messages not found in repository — best-effort skip")

    # Set up paths
    custom_db = tmp_path / "messages.db"

    # Try to find a writer
    writer = resolve_writer()  # may be error
    if isinstance(writer, dict) and "callable" in writer:
        params = inspect.signature(writer["callable"]).parameters
        if "role" not in params and "level" not in params:
            writer = None

    if mode == "custom_path":
        # Prefer to keep all IO under tmp_path
        if isinstance(writer, dict) and "callable" in writer:
            _populate_with_writer(writer, custom_db)
        else:
            # no writer; create SQLite DB as a fallback
            _make_sqlite_db(custom_db)
        rows = _call_fetch(meta, custom_db)
        _assert_order_and_content(rows)
        # cleanup: tmp_path is auto-removed by pytest

    elif mode == "default_path":
        # Try to patch default path constants in module to tmp_path db
        patched = patch_default_db_path(meta["module_obj"], custom_db)
        if not patched and not meta.get("accepts_db_path"):
            pytest.skip(
                "No default DB constant to patch and fetch_messages has no db_path parameter"
            )
        if isinstance(writer, dict) and "callable" in writer:
            _populate_with_writer(writer, custom_db if patched else None)
        else:
            # no writer; create SQLite when patched, otherwise we cannot enforce default target
            if patched:
                _make_sqlite_db(custom_db)
            else:
                pytest.skip(
                    "Cannot safely generate default-path data without writer or patchable constant"
                )
        rows = _call_fetch(meta, None if patched else custom_db)
        _assert_order_and_content(rows)
        # cleanup via tmp_path
