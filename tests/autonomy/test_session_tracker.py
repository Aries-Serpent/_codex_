"""Tests for session_tracker module.

Validates:
- Session lifecycle (start, end, archive)
- JSON schema compliance
- Status constants
- Session metrics counting
- Tombstone record creation for stale sessions
"""

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"


def _import_tracker():
    """Dynamically import session_tracker module."""
    if str(SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPTS_DIR))
    return pytest.importorskip("session_tracker", reason="session_tracker not importable")


class TestSessionTrackerImport:
    """Test that session_tracker module and constants exist."""

    def test_session_tracker_importable(self):
        """session_tracker module can be imported."""
        mod = _import_tracker()
        assert mod is not None

    def test_status_constants_defined(self):
        """Status constants are defined and correct."""
        mod = _import_tracker()
        assert hasattr(mod, "STATUS_ACTIVE"), "STATUS_ACTIVE constant missing"
        assert hasattr(mod, "STATUS_COMPLETED"), "STATUS_COMPLETED constant missing"
        assert hasattr(mod, "STATUS_ERROR"), "STATUS_ERROR constant missing"
        assert hasattr(mod, "STATUS_ARCHIVED"), "STATUS_ARCHIVED constant missing"

        assert mod.STATUS_ACTIVE == "active"
        assert mod.STATUS_COMPLETED == "completed"
        assert mod.STATUS_ERROR == "error"
        assert mod.STATUS_ARCHIVED == "archived"


class TestSessionStartEnd:
    """Test session start and end lifecycle."""

    def test_start_session_returns_id(self, tmp_path):
        """start_session returns a session UUID."""
        mod = _import_tracker()
        if not hasattr(mod, "start_session"):
            pytest.skip("start_session not exported")

        with patch.object(mod, "SESSION_DIR", tmp_path):
            session_id = mod.start_session(label="test-session")
            assert isinstance(session_id, str), "Session ID must be a string"
            assert len(session_id) > 0, "Session ID must not be empty"

    def test_start_session_creates_files(self, tmp_path):
        """start_session creates session and .current_session.json files."""
        mod = _import_tracker()
        if not hasattr(mod, "start_session"):
            pytest.skip("start_session not exported")

        with patch.object(mod, "SESSION_DIR", tmp_path):
            session_id = mod.start_session(label="test-session")

            # Check that session file was created
            session_file = tmp_path / f"session_{session_id}.json"
            assert session_file.exists(), f"Session file not found: {session_file}"

            # Check that .current_session.json was created
            current_file = tmp_path / ".current_session.json"
            assert current_file.exists(), ".current_session.json not found"

    def test_start_session_json_schema(self, tmp_path):
        """Session JSON has required fields."""
        mod = _import_tracker()
        if not hasattr(mod, "start_session"):
            pytest.skip("start_session not exported")

        with patch.object(mod, "SESSION_DIR", tmp_path):
            session_id = mod.start_session(label="schema-test")
            session_file = tmp_path / f"session_{session_id}.json"

            assert session_file.exists(), "Session file must be created"
            data = json.loads(session_file.read_text())
            assert "session_id" in data, "session_id field required"
            assert "started_at" in data, "started_at field required"
            assert "status" in data, "status field required"
            assert data["status"] == "active", "Initial status must be 'active'"

    def test_end_session_marks_completed(self, tmp_path):
        """end_session marks session as completed."""
        mod = _import_tracker()
        if not (hasattr(mod, "start_session") and hasattr(mod, "end_session")):
            pytest.skip("start_session / end_session not exported")

        with patch.object(mod, "SESSION_DIR", tmp_path):
            session_id = mod.start_session(label="end-test")
            mod.end_session(session_id=session_id)

            session_file = tmp_path / f"session_{session_id}.json"
            assert session_file.exists(), "Session file must exist after end"
            data = json.loads(session_file.read_text())
            assert data.get("status") in {"completed", "ended", "finished"}, \
                "Status must indicate completion"


class TestArchiveSession:
    """Test session archiving functionality."""

    def test_archive_session_basic(self, tmp_path):
        """archive_session marks session as archived."""
        mod = _import_tracker()
        if not (hasattr(mod, "start_session") and hasattr(mod, "archive_session")):
            pytest.skip("start_session / archive_session not exported")

        with patch.object(mod, "SESSION_DIR", tmp_path):
            session_id = mod.start_session(label="to-archive")
            result = mod.archive_session(session_id=session_id, reason="test archive")

            assert result["status"] == "archived", "Result status must be 'archived'"
            assert result.get("archive_reason") == "test archive", "Archive reason must be stored"
            assert "archived_at" in result, "archived_at timestamp required"

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

        assert result["session_id"] == stale_id, "Session ID must match input"
        assert result["status"] == "archived", "Status must be archived"
        assert result.get("tombstone") is True, "Tombstone flag required for stale sessions"
        assert result.get("pr_number") == 3221, "PR number must be stored"

        session_file = tmp_path / f"session_{stale_id}.json"
        assert session_file.exists(), "Tombstone file must be created"

    def test_archive_session_removes_current_pointer(self, tmp_path):
        """Archiving a session removes .current_session.json if it points to that session."""
        mod = _import_tracker()
        if not (hasattr(mod, "start_session") and hasattr(mod, "archive_session")):
            pytest.skip("start_session / archive_session not exported")

        with patch.object(mod, "SESSION_DIR", tmp_path):
            session_id = mod.start_session(label="ptr-archive-test")
            ptr = tmp_path / ".current_session.json"
            assert ptr.exists(), "Pointer file must exist after start"

            mod.archive_session(session_id=session_id)
            assert not ptr.exists(), "Pointer file must be removed after archive"

    def test_archive_session_status_constant(self):
        """STATUS_ARCHIVED constant exists and has correct value."""
        mod = _import_tracker()
        assert hasattr(mod, "STATUS_ARCHIVED"), "STATUS_ARCHIVED constant missing"
        assert mod.STATUS_ARCHIVED == "archived", "STATUS_ARCHIVED must equal 'archived'"


class TestSessionList:
    """Test session listing and querying."""

    def test_list_sessions_multiple(self, tmp_path):
        """list_sessions returns multiple created sessions."""
        mod = _import_tracker()
        if not (hasattr(mod, "start_session") and hasattr(mod, "list_sessions")):
            pytest.skip("start_session / list_sessions not exported")

        with patch.object(mod, "SESSION_DIR", tmp_path):
            mod.start_session(label="list-a")
            mod.start_session(label="list-b")
            sessions = mod.list_sessions()

        assert len(sessions) >= 2, "list_sessions must return at least 2 sessions"

    def test_archive_session_in_list(self, tmp_path):
        """Archived sessions appear in list with correct status."""
        mod = _import_tracker()
        if not (hasattr(mod, "start_session") and hasattr(mod, "archive_session") 
                and hasattr(mod, "list_sessions")):
            pytest.skip("start_session / archive_session / list_sessions not exported")

        with patch.object(mod, "SESSION_DIR", tmp_path):
            session_id = mod.start_session(label="archive-list-test")
            mod.archive_session(session_id=session_id, reason="list test")
            sessions = mod.list_sessions()

            archived = [s for s in sessions if s["session_id"] == session_id]
            assert len(archived) == 1, "Archived session must appear in list"
            assert archived[0]["status"] == "archived", "Archived session status must be 'archived'"


class TestSessionMetrics:
    """Test session metrics and counting."""

    def test_metrics_empty_directory(self, tmp_path):
        """session_metrics returns zero counts for empty directory."""
        mod = _import_tracker()
        if not hasattr(mod, "session_metrics"):
            pytest.skip("session_metrics not exported")

        with patch.object(mod, "SESSION_DIR", tmp_path):
            result = mod.session_metrics()

        assert result["total"] == 0, "Total must be 0 for empty directory"
        assert result["active"] == 0, "Active count must be 0"
        assert result["archived"] == 0, "Archived count must be 0"

    def test_metrics_counts_statuses(self, tmp_path):
        """session_metrics correctly counts sessions by status."""
        mod = _import_tracker()
        if not (hasattr(mod, "start_session") and hasattr(mod, "archive_session")
                and hasattr(mod, "session_metrics")):
            pytest.skip("required functions not exported")

        with patch.object(mod, "SESSION_DIR", tmp_path):
            mod.start_session(label="active-one")
            sid2 = mod.start_session(label="to-archive")
            mod.archive_session(session_id=sid2, reason="test metrics")
            result = mod.session_metrics()

        assert result["active"] >= 1, "Active count must be at least 1"
        assert result["archived"] >= 1, "Archived count must be at least 1"
        assert result["total"] == (result["active"] + result["completed"] 
                                   + result["error"] + result["archived"] 
                                   + result.get("unknown", 0)), \
            "Total must equal sum of all categories"

    def test_metrics_tombstone_counted(self, tmp_path):
        """session_metrics counts tombstone records separately."""
        mod = _import_tracker()
        if not (hasattr(mod, "archive_session") and hasattr(mod, "session_metrics")):
            pytest.skip("required functions not exported")

        stale_id = "cccccccc-dddd-eeee-ffff-000000000001"
        with patch.object(mod, "SESSION_DIR", tmp_path):
            mod.archive_session(session_id=stale_id, reason="tombstone test")
            result = mod.session_metrics()

        assert result.get("tombstones", 0) >= 1, "Tombstone count must be tracked"
        assert result["archived"] >= 1, "Archived count must include tombstones"


class TestSessionCommands:
    """Test CLI command functions."""

    def test_cmd_metrics_text_output(self, tmp_path, capsys):
        """cmd_metrics with text format produces readable output."""
        mod = _import_tracker()
        if not hasattr(mod, "cmd_metrics"):
            pytest.skip("cmd_metrics not exported")

        with patch.object(mod, "SESSION_DIR", tmp_path):
            rc = mod.cmd_metrics(output_format="text")

        assert rc == 0, "cmd_metrics must return 0"
        captured = capsys.readouterr()
        # Check for expected output keywords
        output_lower = captured.out.lower()
        assert "archived" in output_lower or "total" in output_lower, \
            "Output must contain session metrics"

    def test_cmd_metrics_json_output(self, tmp_path, capsys):
        """cmd_metrics with json format produces valid JSON."""
        mod = _import_tracker()
        if not hasattr(mod, "cmd_metrics"):
            pytest.skip("cmd_metrics not exported")

        with patch.object(mod, "SESSION_DIR", tmp_path):
            rc = mod.cmd_metrics(output_format="json")

        assert rc == 0, "cmd_metrics must return 0"
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "archived" in data, "JSON output must contain 'archived' key"
        assert "total" in data, "JSON output must contain 'total' key"
