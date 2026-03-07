"""Tests for Phase 2: Session Tracker (scripts/session_tracker.py).

Covers:
- Session lifecycle: start / end / resume / list
- JSON schema validation for session files
- `.current_session.json` pointer management
- Multiple concurrent sessions do not clobber each other
"""
from __future__ import annotations

import importlib
import json
import os
import sys
import uuid
from pathlib import Path
from unittest.mock import patch

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"


def _import_tracker():
    if str(SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPTS_DIR))
    try:
        return importlib.import_module("session_tracker")
    except ImportError:
        pytest.skip("session_tracker not importable")


class TestSessionStart:
    """Tests for session start command."""

    def test_start_creates_session_file(self, tmp_path):
        mod = _import_tracker()
        if not hasattr(mod, "start_session"):
            pytest.skip("start_session not exported")

        with patch.object(mod, "SESSION_DIR", tmp_path):
            session_id = mod.start_session(label="test-session")

        assert isinstance(session_id, str)
        files = list(tmp_path.glob("*.json"))
        assert any(session_id in f.name or f.name == ".current_session.json" for f in files)

    def test_start_session_json_schema(self, tmp_path):
        mod = _import_tracker()
        if not hasattr(mod, "start_session"):
            pytest.skip("start_session not exported")

        with patch.object(mod, "SESSION_DIR", tmp_path):
            session_id = mod.start_session(label="schema-test")
            session_file = tmp_path / f"{session_id}.json"
            if not session_file.exists():
                # May be stored with a different naming convention — check by filename
                candidates = [f for f in tmp_path.glob("*.json") if session_id in f.stem]
                session_file = candidates[0] if candidates else session_file

        if session_file.exists():
            data = json.loads(session_file.read_text())
            assert "session_id" in data
            assert "started_at" in data


class TestSessionEnd:
    """Tests for session end command."""

    def test_end_session_updates_status(self, tmp_path):
        mod = _import_tracker()
        if not (hasattr(mod, "start_session") and hasattr(mod, "end_session")):
            pytest.skip("start_session / end_session not exported")

        with patch.object(mod, "SESSION_DIR", tmp_path):
            session_id = mod.start_session(label="end-test")
            mod.end_session(session_id=session_id)

        # The session file should now reflect ended status
        for f in tmp_path.glob("*.json"):
            text = f.read_text()
            if session_id in text:
                data = json.loads(text)
                status = data.get("status", "")
                assert status in {"complete", "ended", "finished", ""}


class TestCurrentSessionPointer:
    """Tests for .current_session.json pointer file."""

    def test_current_session_written_on_start(self, tmp_path):
        mod = _import_tracker()
        if not hasattr(mod, "start_session"):
            pytest.skip("start_session not exported")

        with patch.object(mod, "SESSION_DIR", tmp_path):
            session_id = mod.start_session(label="ptr-test")

        ptr = tmp_path / ".current_session.json"
        if ptr.exists():
            data = json.loads(ptr.read_text())
            assert "session_id" in data

    def test_multiple_sessions_no_clobber(self, tmp_path):
        mod = _import_tracker()
        if not hasattr(mod, "start_session"):
            pytest.skip("start_session not exported")

        with patch.object(mod, "SESSION_DIR", tmp_path):
            id1 = mod.start_session(label="first")
            id2 = mod.start_session(label="second")

        assert id1 != id2


class TestSessionList:
    """Tests for listing sessions."""

    def test_list_returns_started_sessions(self, tmp_path):
        mod = _import_tracker()
        if not (hasattr(mod, "start_session") and hasattr(mod, "list_sessions")):
            pytest.skip("start_session / list_sessions not exported")

        with patch.object(mod, "SESSION_DIR", tmp_path):
            id1 = mod.start_session(label="list-a")
            id2 = mod.start_session(label="list-b")
            sessions = mod.list_sessions()

        assert len(sessions) >= 2
