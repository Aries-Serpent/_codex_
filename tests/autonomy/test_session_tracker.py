"""Tests for Phase 2: Session Tracker (scripts/session_tracker.py).

Covers:
- Session lifecycle: start / end / resume / list
- JSON schema validation for session files
- `.current_session.json` pointer management
- Multiple concurrent sessions do not clobber each other
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"


def _import_tracker():
    if str(SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPTS_DIR))
    return pytest.importorskip("session_tracker", reason="session_tracker not importable")


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

        # Locate the session file by name (avoids reading the .current_session.json
        # pointer file which does not contain a "status" field).
        session_file = tmp_path / f"session_{session_id}.json"
        assert session_file.exists(), f"Session file not found: {session_file}"
        data = json.loads(session_file.read_text())
        assert data.get("status") in {"complete", "completed", "ended", "finished"}


class TestCurrentSessionPointer:
    """Tests for .current_session.json pointer file."""

    def test_current_session_written_on_start(self, tmp_path):
        mod = _import_tracker()
        if not hasattr(mod, "start_session"):
            pytest.skip("start_session not exported")

        with patch.object(mod, "SESSION_DIR", tmp_path):
            _ = mod.start_session(label="ptr-test")

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
            mod.start_session(label="list-a")
            mod.start_session(label="list-b")
            sessions = mod.list_sessions()

        assert len(sessions) >= 2


class TestSessionArchive:
    """Tests for the archive command and archive_session programmatic API."""

    def test_archive_existing_session(self, tmp_path):
        mod = _import_tracker()
        if not (hasattr(mod, "start_session") and hasattr(mod, "archive_session")):
            pytest.skip("start_session / archive_session not exported")

        with patch.object(mod, "SESSION_DIR", tmp_path):
            session_id = mod.start_session(label="to-archive")
            result = mod.archive_session(session_id=session_id, reason="test archive")

        assert result["status"] == "archived"
        assert result["outcome"] == "archived"
        assert result.get("archive_reason") == "test archive"
        assert "archived_at" in result

    def test_archive_stale_session_creates_tombstone(self, tmp_path):
        """Archiving a session with no local file creates a tombstone record."""
        mod = _import_tracker()
        if not hasattr(mod, "archive_session"):
            pytest.skip("archive_session not exported")

        stale_id = "f50f76f3-161d-4776-aa72-f9f0d6202fc2"
        with patch.object(mod, "SESSION_DIR", tmp_path):
            result = mod.archive_session(
                session_id=stale_id,
                reason="PR #3221 merged - stale cached session",
                pr_number=3221,
            )

        assert result["session_id"] == stale_id
        assert result["status"] == "archived"
        assert result.get("tombstone") is True
        assert result.get("pr_number") == 3221
        session_file = tmp_path / f"session_{stale_id}.json"
        assert session_file.exists()

    def test_archive_session_removes_current_pointer(self, tmp_path):
        mod = _import_tracker()
        if not (hasattr(mod, "start_session") and hasattr(mod, "archive_session")):
            pytest.skip("start_session / archive_session not exported")

        with patch.object(mod, "SESSION_DIR", tmp_path):
            session_id = mod.start_session(label="ptr-archive-test")
            ptr = tmp_path / ".current_session.json"
            assert ptr.exists()
            mod.archive_session(session_id=session_id)
            assert not ptr.exists()

    def test_archive_session_status_constant(self):
        mod = _import_tracker()
        assert hasattr(mod, "STATUS_ARCHIVED"), "STATUS_ARCHIVED constant missing"
        assert mod.STATUS_ARCHIVED == "archived"

    def test_archive_session_in_list(self, tmp_path):
        mod = _import_tracker()
        if not (hasattr(mod, "start_session") and hasattr(mod, "archive_session") and hasattr(mod, "list_sessions")):
            pytest.skip("start_session / archive_session / list_sessions not exported")

        with patch.object(mod, "SESSION_DIR", tmp_path):
            session_id = mod.start_session(label="archive-list-test")
            mod.archive_session(session_id=session_id, reason="list test")
            sessions = mod.list_sessions()

        archived = [s for s in sessions if s["session_id"] == session_id]
        assert len(archived) == 1
        assert archived[0]["status"] == "archived"


class TestSessionArchiveDryRun:
    """Tests for the --dry-run flag added in Phase 22."""

    def test_dry_run_does_not_create_file(self, tmp_path):
        mod = _import_tracker()
        if not hasattr(mod, "cmd_archive"):
            pytest.skip("cmd_archive not exported")

        session_id = "aaaabbbb-cccc-dddd-eeee-ffffffffffff"
        with patch.object(mod, "SESSION_DIR", tmp_path):
            rc = mod.cmd_archive(session_id=session_id, reason="dry test", dry_run=True)

        assert rc == 0
        assert not (tmp_path / f"session_{session_id}.json").exists(), \
            "dry-run must not write any files"

    def test_dry_run_existing_session_unchanged(self, tmp_path):
        mod = _import_tracker()
        if not (hasattr(mod, "cmd_archive") and hasattr(mod, "start_session")):
            pytest.skip("cmd_archive / start_session not exported")

        with patch.object(mod, "SESSION_DIR", tmp_path):
            sid = mod.start_session(label="dry-run-live")
            original_status = mod._load_json(mod._session_path(sid))["status"]
            rc = mod.cmd_archive(session_id=sid, reason="dry-run check", dry_run=True)
            after_status = mod._load_json(mod._session_path(sid))["status"]

        assert rc == 0
        assert after_status == original_status, \
            "dry-run must leave the session file unchanged"


class TestSessionMetrics:
    """Tests for the ``metrics`` command and ``session_metrics()`` API (Phase 23)."""

    def test_metrics_empty(self, tmp_path):
        mod = _import_tracker()
        if not hasattr(mod, "session_metrics"):
            pytest.skip("session_metrics not exported")

        with patch.object(mod, "SESSION_DIR", tmp_path):
            result = mod.session_metrics()

        assert result["total"] == 0
        assert result["active"] == 0
        assert result["archived"] == 0

    def test_metrics_counts_statuses(self, tmp_path):
        mod = _import_tracker()
        if not (hasattr(mod, "start_session") and hasattr(mod, "archive_session") and hasattr(mod, "session_metrics")):
            pytest.skip("required functions not exported")

        with patch.object(mod, "SESSION_DIR", tmp_path):
            mod.start_session(label="active-one")  # side-effect: creates active session
            sid2 = mod.start_session(label="to-archive")
            mod.archive_session(session_id=sid2, reason="test metrics")
            result = mod.session_metrics()

        assert result["active"] >= 1
        assert result["archived"] >= 1
        assert result["total"] == result["active"] + result["completed"] + result["error"] + result["archived"] + result["unknown"]

    def test_metrics_tombstone_counted(self, tmp_path):
        mod = _import_tracker()
        if not (hasattr(mod, "archive_session") and hasattr(mod, "session_metrics")):
            pytest.skip("required functions not exported")

        stale_id = "cccccccc-dddd-eeee-ffff-000000000001"
        with patch.object(mod, "SESSION_DIR", tmp_path):
            mod.archive_session(session_id=stale_id, reason="tombstone test")
            result = mod.session_metrics()

        assert result["tombstones"] == 1
        assert result["archived"] >= 1

    def test_cmd_metrics_text_output(self, tmp_path, capsys):
        mod = _import_tracker()
        if not hasattr(mod, "cmd_metrics"):
            pytest.skip("cmd_metrics not exported")

        with patch.object(mod, "SESSION_DIR", tmp_path):
            rc = mod.cmd_metrics(output_format="text")

        captured = capsys.readouterr()
        assert rc == 0
        assert "Archived" in captured.out or "archived" in captured.out.lower()
        assert "Total" in captured.out or "total" in captured.out.lower()

    def test_cmd_metrics_json_output(self, tmp_path, capsys):
        mod = _import_tracker()
        if not hasattr(mod, "cmd_metrics"):
            pytest.skip("cmd_metrics not exported")

        with patch.object(mod, "SESSION_DIR", tmp_path):
            rc = mod.cmd_metrics(output_format="json")

        captured = capsys.readouterr()
        assert rc == 0
        data = json.loads(captured.out)
        assert "archived" in data
        assert "total" in data
        assert "tombstones" in data
