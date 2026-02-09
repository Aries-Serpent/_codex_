"""Tests for auto_handoff.py - Automated Agent Handoff Generator."""

import json

# Import the module under test
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "handoff"))

from auto_handoff import (
    ACTION_LOG_PATH,
    AutoHandoff,
    HandoffContext,
)


class TestHandoffContext:
    """Tests for HandoffContext class."""

    def test_init_default(self):
        """Test default initialization."""
        context = HandoffContext()
        assert context.from_agent == "copilot"
        assert context.to_agent == "codex"
        assert context.phase == ""
        assert context.pr_number is None
        assert context.session_id is None
        assert context.completed_tasks == []
        assert context.pending_tasks == []
        assert context.deliverables == []

    def test_init_with_values(self):
        """Test initialization with custom values."""
        context = HandoffContext(
            from_agent="user",
            to_agent="copilot",
            phase="Plan 1",
            pr_number=3160,
            session_id="test-session"
        )
        assert context.from_agent == "user"
        assert context.to_agent == "copilot"
        assert context.phase == "Plan 1"
        assert context.pr_number == 3160
        assert context.session_id == "test-session"

    def test_to_dict(self):
        """Test conversion to dictionary."""
        context = HandoffContext(
            from_agent="copilot",
            to_agent="codex",
            phase="Test Phase"
        )
        context.completed_tasks = ["Task 1", "Task 2"]
        context.deliverables = [{"path": "file.py", "status": "created"}]

        result = context.to_dict()

        assert result["from_agent"] == "copilot"
        assert result["to_agent"] == "codex"
        assert result["phase"] == "Test Phase"
        assert len(result["completed_tasks"]) == 2
        assert len(result["deliverables"]) == 1
        assert "timestamp" in result


class TestAutoHandoff:
    """Tests for AutoHandoff class."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def handoff(self):
        """Create AutoHandoff instance."""
        return AutoHandoff(hours=24)

    def test_init_default_hours(self):
        """Test default hours initialization."""
        handoff = AutoHandoff()
        assert handoff.hours == 24

    def test_init_custom_hours(self):
        """Test custom hours initialization."""
        handoff = AutoHandoff(hours=48)
        assert handoff.hours == 48

    def test_cutoff_time_calculated(self):
        """Test cutoff time is calculated correctly."""
        handoff = AutoHandoff(hours=24)
        now = datetime.now(timezone.utc)
        expected_cutoff = now - timedelta(hours=24)

        # Allow 1 second tolerance
        diff = abs((handoff.cutoff_time - expected_cutoff).total_seconds())
        assert diff < 1

    def test_init_tracking_data_structure(self, handoff):
        """Test tracking data initialization structure."""
        data = handoff._init_tracking_data()

        assert "version" in data
        assert "created" in data
        assert "last_updated" in data
        assert "handoffs" in data
        assert "metrics" in data
        assert "settings" in data
        assert data["handoffs"] == []
        assert data["metrics"]["total_handoffs"] == 0

    def test_generate_handoff_id_first(self, handoff):
        """Test first handoff ID generation."""
        data = {"handoffs": []}
        handoff_id = handoff.generate_handoff_id(data)
        assert handoff_id == "HO-001"

    def test_generate_handoff_id_subsequent(self, handoff):
        """Test subsequent handoff ID generation."""
        data = {"handoffs": [{"id": "HO-001"}, {"id": "HO-002"}]}
        handoff_id = handoff.generate_handoff_id(data)
        assert handoff_id == "HO-003"

    def test_create_handoff_record(self, handoff):
        """Test handoff record creation."""
        context = HandoffContext(
            from_agent="copilot",
            to_agent="codex",
            phase="Test Phase",
            pr_number=1234
        )
        context.completed_tasks = ["Task 1"]
        context.deliverables = [{"path": "file.py"}]

        record = handoff.create_handoff_record("HO-001", context)

        assert record["id"] == "HO-001"
        assert record["from_agent"] == "copilot"
        assert record["to_agent"] == "codex"
        assert record["phase"] == "Test Phase"
        assert record["pr_number"] == 1234
        assert record["status"] == "pending"
        assert record["context_summary"]["completed_tasks"] == 1
        assert record["context_summary"]["deliverables"] == 1

    def test_extract_session_context_no_log(self, handoff):
        """Test context extraction when no action log exists."""
        with patch.object(
            type(ACTION_LOG_PATH), 'exists',
            return_value=False
        ):
            context = handoff.extract_session_context()

        assert context.files_modified == []
        assert context.completed_tasks == []

    def test_generate_handoff_comment_structure(self, handoff):
        """Test generated comment has expected structure."""
        context = HandoffContext(
            from_agent="copilot",
            to_agent="codex",
            phase="Plan 1 Complete"
        )
        context.completed_tasks = ["Implemented feature X"]
        context.deliverables = [{"path": "feature.py", "status": "created"}]

        comment = handoff.generate_handoff_comment(context, "HO-001")

        assert "## 📤 HANDOFF:" in comment
        assert "Copilot → Codex" in comment
        assert "Plan 1 Complete" in comment
        assert "HO-001" in comment
        assert "Implemented feature X" in comment
        assert "feature.py" in comment

    def test_generate_handoff_comment_empty_context(self, handoff):
        """Test generated comment with empty context."""
        context = HandoffContext()
        comment = handoff.generate_handoff_comment(context, "HO-001")

        assert "No deliverables" in comment or "No tasks recorded" in comment

    def test_load_patterns_no_file(self, handoff):
        """Test pattern loading when file doesn't exist."""
        with patch('auto_handoff.PATTERN_STORE') as mock_path:
            mock_path.exists.return_value = False
            patterns = handoff.load_patterns()

        assert patterns == []

    def test_load_tracking_data_no_file(self, handoff, temp_dir):
        """Test tracking data loading when file doesn't exist."""
        with patch('auto_handoff.TRACKING_FILE', temp_dir / "tracking.json"):
            data = handoff.load_tracking_data()

        assert "handoffs" in data
        assert "metrics" in data

    def test_save_tracking_data(self, handoff, temp_dir):
        """Test saving tracking data."""
        tracking_file = temp_dir / "tracking.json"

        with patch('auto_handoff.TRACKING_FILE', tracking_file):
            data = {"handoffs": [], "metrics": {}}
            handoff.save_tracking_data(data)

            assert tracking_file.exists()
            with open(tracking_file) as f:
                saved = json.load(f)
            assert "last_updated" in saved

    def test_update_handoff_status_success(self, handoff, temp_dir):
        """Test successful status update."""
        tracking_file = temp_dir / "tracking.json"
        initial_data = {
            "handoffs": [
                {"id": "HO-001", "status": "pending"}
            ],
            "metrics": {
                "total_handoffs": 1,
                "completed": 0,
                "pending": 1,
                "in_progress": 0,
                "failed": 0
            }
        }

        tracking_file.parent.mkdir(parents=True, exist_ok=True)
        with open(tracking_file, 'w') as f:
            json.dump(initial_data, f)

        with patch('auto_handoff.TRACKING_FILE', tracking_file):
            handoff.tracking_data = initial_data
            result = handoff.update_handoff_status("HO-001", "complete")

        assert result is True

    def test_update_handoff_status_not_found(self, handoff):
        """Test status update for non-existent handoff."""
        with patch.object(
            handoff, 'load_tracking_data',
            return_value={"handoffs": [], "metrics": {}}
        ):
            result = handoff.update_handoff_status("HO-999", "complete")

        assert result is False

    def test_list_handoffs_empty(self, handoff):
        """Test listing handoffs when empty."""
        with patch.object(
            handoff, 'load_tracking_data',
            return_value={"handoffs": []}
        ):
            result = handoff.list_handoffs()

        assert result == []

    def test_list_handoffs_with_filter(self, handoff):
        """Test listing handoffs with status filter."""
        mock_data = {
            "handoffs": [
                {"id": "HO-001", "status": "pending", "created": "2026-02-05T10:00:00Z"},
                {"id": "HO-002", "status": "complete", "created": "2026-02-05T11:00:00Z"},
                {"id": "HO-003", "status": "pending", "created": "2026-02-05T12:00:00Z"}
            ]
        }

        with patch.object(handoff, 'load_tracking_data', return_value=mock_data):
            result = handoff.list_handoffs(status_filter="pending")

        assert len(result) == 2
        assert all(h["status"] == "pending" for h in result)

    def test_list_handoffs_with_limit(self, handoff):
        """Test listing handoffs with limit."""
        mock_data = {
            "handoffs": [
                {"id": f"HO-{i:03d}", "status": "pending", "created": f"2026-02-05T{i:02d}:00:00Z"}
                for i in range(15)
            ]
        }

        with patch.object(handoff, 'load_tracking_data', return_value=mock_data):
            result = handoff.list_handoffs(limit=5)

        assert len(result) == 5

    def test_get_handoff_status_found(self, handoff):
        """Test getting status of existing handoff."""
        mock_data = {
            "handoffs": [
                {"id": "HO-001", "status": "complete", "from_agent": "copilot"}
            ]
        }

        with patch.object(handoff, 'load_tracking_data', return_value=mock_data):
            result = handoff.get_handoff_status("HO-001")

        assert result is not None
        assert result["id"] == "HO-001"
        assert result["status"] == "complete"

    def test_get_handoff_status_not_found(self, handoff):
        """Test getting status of non-existent handoff."""
        with patch.object(
            handoff, 'load_tracking_data',
            return_value={"handoffs": []}
        ):
            result = handoff.get_handoff_status("HO-999")

        assert result is None


class TestAutoHandoffIntegration:
    """Integration tests for AutoHandoff."""

    @pytest.fixture
    def temp_env(self):
        """Create temporary environment for integration tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create directory structure
            (tmppath / ".codex").mkdir()
            (tmppath / ".codex" / "cognitive_brain").mkdir()
            (tmppath / ".codex" / "handoffs").mkdir()

            yield tmppath

    def test_execute_handoff_creates_record(self, temp_env):
        """Test that execute_handoff creates a tracking record."""
        tracking_file = temp_env / ".codex" / "handoff_tracking.json"
        output_file = temp_env / ".codex" / "handoffs" / "test.md"

        with patch('auto_handoff.TRACKING_FILE', tracking_file), \
             patch('auto_handoff.ACTION_LOG_PATH', temp_env / "action_log.ndjson"), \
             patch('auto_handoff.OUTPUT_DIR', temp_env / ".codex" / "handoffs"):

            handoff = AutoHandoff()
            handoff_id, comment = handoff.execute_handoff(
                from_agent="copilot",
                to_agent="codex",
                phase="Test Phase",
                pr_number=1234,
                output_path=output_file
            )

        assert handoff_id == "HO-001"
        assert "Test Phase" in comment
        assert output_file.exists()
        assert tracking_file.exists()

    def test_full_handoff_workflow(self, temp_env):
        """Test complete handoff workflow."""
        tracking_file = temp_env / ".codex" / "handoff_tracking.json"

        with patch('auto_handoff.TRACKING_FILE', tracking_file), \
             patch('auto_handoff.ACTION_LOG_PATH', temp_env / "action_log.ndjson"):

            handoff = AutoHandoff()

            # Create first handoff
            handoff_id1, _ = handoff.execute_handoff(
                phase="Phase 1"
            )
            assert handoff_id1 == "HO-001"

            # Update status
            handoff.update_handoff_status(handoff_id1, "complete")

            # Reload and verify
            handoff2 = AutoHandoff()
            status = handoff2.get_handoff_status(handoff_id1)
            assert status["status"] == "complete"

            # Create second handoff
            handoff_id2, _ = handoff2.execute_handoff(
                phase="Phase 2"
            )
            assert handoff_id2 == "HO-002"
