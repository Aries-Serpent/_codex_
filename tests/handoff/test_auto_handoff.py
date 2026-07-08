#         assert ", "Condition must be true"
#         assert "Copilot → Codex" in comment, "Condition must be true"
#         assert "Plan 1 Complete" in comment, "Condition must be true"
#         assert "HO-001" in comment, "Condition must be true"
#         assert "Implemented feature X" in comment, "Condition must be true"
#         assert "feature.py" in comment, "Condition must be true"
# from datetime import datetime, timedelta, timezone
# 
#         assert ", "Condition must be true"
#         assert "Copilot → Codex" in comment, "Condition must be true"
#         assert "Plan 1 Complete" in comment, "Condition must be true"
#         assert "HO-001" in comment, "Condition must be true"
#         assert "Implemented feature X" in comment, "Condition must be true"
#         assert "feature.py" in comment, "Condition must be true"
# from auto_handoff import (
#     ACTION_LOG_PATH,
#     AutoHandoff,
#     HandoffContext,
# )
# 
#         assert ", "Condition must be true"
#         assert "Copilot → Codex" in comment, "Condition must be true"
#         assert "Plan 1 Complete" in comment, "Condition must be true"
#         assert "HO-001" in comment, "Condition must be true"
#         assert "Implemented feature X" in comment, "Condition must be true"
#         assert "feature.py" in comment, "Condition must be true"
#         context = HandoffContext()
#         assert context.from_agent == "copilot", "from_agent is not valid"
#         assert context.to_agent == "codex", "to_agent is not valid"
#         assert context.phase == "", "phase is not valid"
#         assert context.pr_number is None, "pr_number is not valid"
#         assert context.session_id is None, "session_id is not valid"
#         assert context.completed_tasks == [], "completed_tasks is not valid"
#         assert context.pending_tasks == [], "pending_tasks is not valid"
#         assert context.deliverables == [], "deliverables is not valid"
# 
#     def test_init_with_values(self):
#     def test_init_with_values(self):
#         """Test initialization with custom values."""
#         context = HandoffContext(
#             from_agent="user",
#             to_agent="copilot",
#             phase="Plan 1",
#             pr_number=3160,
#             session_id="test-session",
#         )
#         assert context.from_agent == "user", "from_agent is not valid"
#         assert context.to_agent == "copilot", "to_agent is not valid"
#         assert context.phase == "Plan 1", "phase is not valid"
#         assert context.pr_number == 3160, "pr_number is not valid"
#         assert context.session_id == "test-session", "session_id is not valid"
#     def test_to_dict(self):
#     def test_to_dict(self):
#         """Test conversion to dictionary."""
#         context = HandoffContext(from_agent="copilot", to_agent="codex", phase="Test Phase")
#         context.completed_tasks = ["Task 1", "Task 2"]
#         context.deliverables = [{"path": "file.py", "status": "created"}]
#         result = context.to_dict()
# 
#         assert result["from_agent"] == "copilot", "Result must not be empty"
#         assert result["to_agent"] == "codex", "Result must not be empty"
#         assert result["phase"] == "Test Phase", "Result must not be empty"
#         assert len(result["completed_tasks"]) == 2, "Collection must not be empty"
#         assert len(result["deliverables"]) == 1, "Collection must not be empty"
#         assert "timestamp" in result, "Result must not be empty"
# 
#         assert ", "Condition must be true"
#         assert "Copilot → Codex" in comment, "Condition must be true"
#         assert "Plan 1 Complete" in comment, "Condition must be true"
#         assert "HO-001" in comment, "Condition must be true"
#         assert "Implemented feature X" in comment, "Condition must be true"
#         assert "feature.py" in comment, "Condition must be true"
#         """Create a temporary directory for tests."""
#         with tempfile.TemporaryDirectory() as tmpdir:
#             yield Path(tmpdir)
# 
#     @pytest.fixture
#     def handoff(self):
#     def handoff(self):
#         """Create AutoHandoff instance."""
#         return AutoHandoff(hours=24)
#     def test_init_default_hours(self):
#     def test_init_default_hours(self):
#         """Test default hours initialization."""
#         handoff = AutoHandoff()
#         assert handoff.hours == 24, "hours is not valid"
#     def test_init_custom_hours(self):
#     def test_init_custom_hours(self):
#         """Test custom hours initialization."""
#         handoff = AutoHandoff(hours=48)
#         assert handoff.hours == 48, "hours is not valid"
#     def test_cutoff_time_calculated(self):
#     def test_cutoff_time_calculated(self):
#         """Test cutoff time is calculated correctly."""
#         handoff = AutoHandoff(hours=24)
#         now = datetime.now(timezone.utc)
#         expected_cutoff = now - timedelta(hours=24)
#         diff = abs((handoff.cutoff_time - expected_cutoff).total_seconds())
#         assert diff < 1, "diff is not valid"
#         assert diff < 1, "diff is not valid"
# 
#     def test_init_tracking_data_structure(self, handoff):
#     def test_init_tracking_data_structure(self, handoff):
#         """Test tracking data initialization structure."""
#         data = handoff._init_tracking_data()
#         assert "version" in data, "Data must not be empty"
#         assert "created" in data, "Data must not be empty"
#         assert "last_updated" in data, "Data must not be empty"
#         assert "handoffs" in data, "Data must not be empty"
#         assert "metrics" in data, "Data must not be empty"
#         assert "settings" in data, "Data must not be empty"
#         assert data["handoffs"] == [], "Data must not be empty"
#         assert data["metrics"]["total_handoffs"] == 0, "Data must not be empty"
# 
#     def test_generate_handoff_id_first(self, handoff):
#     def test_generate_handoff_id_first(self, handoff):
#         """Test first handoff ID generation."""
#         data = {"handoffs": []}
#         handoff_id = handoff.generate_handoff_id(data)
#         assert handoff_id == "HO-001", "handoff_id is not valid"
#     def test_generate_handoff_id_subsequent(self, handoff):
#     def test_generate_handoff_id_subsequent(self, handoff):
#         """Test subsequent handoff ID generation."""
#         data = {"handoffs": [{"id": "HO-001"}, {"id": "HO-002"}]}
#         handoff_id = handoff.generate_handoff_id(data)
#         assert handoff_id == "HO-003", "handoff_id is not valid"
#     def test_create_handoff_record(self, handoff):
#     def test_create_handoff_record(self, handoff):
#         """Test handoff record creation."""
#         context = HandoffContext(
#             from_agent="copilot", to_agent="codex", phase="Test Phase", pr_number=1234
#         )
#         context.completed_tasks = ["Task 1"]
#         context.deliverables = [{"path": "file.py"}]
#         record = handoff.create_handoff_record("HO-001", context)
# 
#         assert record["id"] == "HO-001", "rec is not valid"
#         assert record["from_agent"] == "copilot", "rec is not valid"
#         assert record["to_agent"] == "codex", "rec is not valid"
#         assert record["phase"] == "Test Phase", "rec is not valid"
#         assert record["pr_number"] == 1234, "rec is not valid"
#         assert record["status"] == "pending", "rec is not valid"
#         assert record["context_summary"]["completed_tasks"] == 1, "rec is not valid"
#         assert record["context_summary"]["deliverables"] == 1, "rec is not valid"
# 
#     def test_extract_session_context_no_log(self, handoff):
#     def test_extract_session_context_no_log(self, handoff):
#         """Test context extraction when no action log exists."""
#         with patch.object(type(ACTION_LOG_PATH), "exists", return_value=False):
#             context = handoff.extract_session_context()
#         assert context.files_modified == [], "files_modified is not valid"
#         assert context.completed_tasks == [], "completed_tasks is not valid"
# 
#     def test_generate_handoff_comment_structure(self, handoff):
#     def test_generate_handoff_comment_structure(self, handoff):
#         """Test generated comment has expected structure."""
#         context = HandoffContext(from_agent="copilot", to_agent="codex", phase="Plan 1 Complete")
#         context.completed_tasks = ["Implemented feature X"]
#         context.deliverables = [{"path": "feature.py", "status": "created"}]
#         comment = handoff.generate_handoff_comment(context, "HO-001")
# 
#         assert ", "Condition must be true"
#         assert "Copilot → Codex" in comment, "Condition must be true"
#         assert "Plan 1 Complete" in comment, "Condition must be true"
#         assert "HO-001" in comment, "Condition must be true"
#         assert "Implemented feature X" in comment, "Condition must be true"
#         assert "feature.py" in comment, "Condition must be true"
# 
#     def test_generate_handoff_comment_empty_context(self, handoff):
#     def test_generate_handoff_comment_empty_context(self, handoff):
#         """Test generated comment with empty context."""
#         context = HandoffContext()
#         comment = handoff.generate_handoff_comment(context, "HO-001")
#         assert "No deliverables" in comment or "No tasks recorded" in comment, "Condition must be true"
# 
#     def test_load_patterns_no_file(self, handoff):
#     def test_load_patterns_no_file(self, handoff):
#         """Test pattern loading when file doesn't exist."""
#         with patch("auto_handoff.PATTERN_STORE") as mock_path:
#             mock_path.exists.return_value = False
#             patterns = handoff.load_patterns()
#         assert patterns == [], "patterns is not valid"
# 
#     def test_load_tracking_data_no_file(self, handoff, temp_dir):
#     def test_load_tracking_data_no_file(self, handoff, temp_dir):
#         """Test tracking data loading when file doesn't exist."""
#         with patch("auto_handoff.TRACKING_FILE", temp_dir / "tracking.json"):
#             data = handoff.load_tracking_data()
#         assert "handoffs" in data, "Data must not be empty"
#         assert "metrics" in data, "Data must not be empty"
# 
#     def test_save_tracking_data(self, handoff, temp_dir):
#     def test_save_tracking_data(self, handoff, temp_dir):
#         """Test saving tracking data."""
#         tracking_file = temp_dir / "tracking.json"
#         with patch("auto_handoff.TRACKING_FILE", tracking_file):
#             data = {"handoffs": [], "metrics": {}}
#             handoff.save_tracking_data(data)
# 
#             assert tracking_file.exists(), "Condition must be true"
#             with open(tracking_file) as f:
#                 saved = json.load(f)
#             assert "last_updated" in saved, "Condition must be true"
# 
#     def test_update_handoff_status_success(self, handoff, temp_dir):
#     def test_update_handoff_status_success(self, handoff, temp_dir):
#         """Test successful status update."""
#         tracking_file = temp_dir / "tracking.json"
#         initial_data = {
#             "handoffs": [{"id": "HO-001", "status": "pending"}],
#             "metrics": {
#                 "total_handoffs": 1,
#                 "completed": 0,
#                 "pending": 1,
#                 "in_progress": 0,
#                 "failed": 0,
#             },
#         }
#         tracking_file.parent.mkdir(parents=True, exist_ok=True)
#         with open(tracking_file, "w") as f:
#             json.dump(initial_data, f)
# 
#         with patch("auto_handoff.TRACKING_FILE", tracking_file):
#             handoff.tracking_data = initial_data
#             result = handoff.update_handoff_status("HO-001", "complete")
# 
#         assert result is True, "Result must not be empty"
# 
#     def test_update_handoff_status_not_found(self, handoff):
#     def test_update_handoff_status_not_found(self, handoff):
#         """Test status update for non-existent handoff."""
#         with patch.object(
#             handoff, "load_tracking_data", return_value={"handoffs": [], "metrics": {}}
#         ):
#             result = handoff.update_handoff_status("HO-999", "complete")
#         assert result is False, "Result must not be empty"
# 
#     def test_list_handoffs_empty(self, handoff):
#     def test_list_handoffs_empty(self, handoff):
#         """Test listing handoffs when empty."""
#         with patch.object(handoff, "load_tracking_data", return_value={"handoffs": []}):
#             result = handoff.list_handoffs()
#         assert result == [], "Result must not be empty"
# 
#     def test_list_handoffs_with_filter(self, handoff):
#     def test_list_handoffs_with_filter(self, handoff):
#         """Test listing handoffs with status filter."""
#         mock_data = {
#             "handoffs": [
#                 {"id": "HO-001", "status": "pending", "created": "2026-02-05T10:00:00Z"},
#                 {"id": "HO-002", "status": "complete", "created": "2026-02-05T11:00:00Z"},
#                 {"id": "HO-003", "status": "pending", "created": "2026-02-05T12:00:00Z"},
#             ]
#         }
#         with patch.object(handoff, "load_tracking_data", return_value=mock_data):
#             result = handoff.list_handoffs(status_filter="pending")
# 
#         assert len(result) == 2, "Result must not be empty"
#         assert all(h["status"] == "pending" for h in result), "Result must not be empty"
# 
#     def test_list_handoffs_with_limit(self, handoff):
#     def test_list_handoffs_with_limit(self, handoff):
#         """Test listing handoffs with limit."""
#         mock_data = {
#             "handoffs": [
#                 {"id": f"HO-{i:03d}", "status": "pending", "created": f"2026-02-05T{i:02d}:00:00Z"}
#                 for i in range(15)
#             ]
#         }
#         with patch.object(handoff, "load_tracking_data", return_value=mock_data):
#             result = handoff.list_handoffs(limit=5)
# 
#         assert len(result) == 5, "Result must not be empty"
# 
#     def test_get_handoff_status_found(self, handoff):
#     def test_get_handoff_status_found(self, handoff):
#         """Test getting status of existing handoff."""
#         mock_data = {"handoffs": [{"id": "HO-001", "status": "complete", "from_agent": "copilot"}]}
#         with patch.object(handoff, "load_tracking_data", return_value=mock_data):
#             result = handoff.get_handoff_status("HO-001")
# 
#         assert result is not None, "result must be initialized"
#         assert result["id"] == "HO-001", "Result must not be empty"
#         assert result["status"] == "complete", "Result must not be empty"
# 
#     def test_get_handoff_status_not_found(self, handoff):
#     def test_get_handoff_status_not_found(self, handoff):
#         """Test getting status of non-existent handoff."""
#         with patch.object(handoff, "load_tracking_data", return_value={"handoffs": []}):
#             result = handoff.get_handoff_status("HO-999")
#         assert result is None, "Result must not be empty"


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

        with (
            patch("auto_handoff.TRACKING_FILE", tracking_file),
            patch("auto_handoff.ACTION_LOG_PATH", temp_env / "action_log.ndjson"),
            patch("auto_handoff.OUTPUT_DIR", temp_env / ".codex" / "handoffs"),
        ):

            handoff = AutoHandoff()
            handoff_id, comment = handoff.execute_handoff(
                from_agent="copilot",
                to_agent="codex",
                phase="Test Phase",
                pr_number=1234,
                output_path=output_file,
            )

        assert handoff_id == "HO-001", "handoff_id is not valid"
        assert "Test Phase" in comment, "Condition must be true"
        assert output_file.exists(), "Condition must be true"
        assert tracking_file.exists(), "Condition must be true"

    def test_full_handoff_workflow(self, temp_env):
        """Test complete handoff workflow."""
        tracking_file = temp_env / ".codex" / "handoff_tracking.json"

        with (
            patch("auto_handoff.TRACKING_FILE", tracking_file),
            patch("auto_handoff.ACTION_LOG_PATH", temp_env / "action_log.ndjson"),
        ):

            handoff = AutoHandoff()

            # Create first handoff
            handoff_id1, _ = handoff.execute_handoff(phase="Phase 1")
            assert handoff_id1 == "HO-001", "handoff_id1 is not valid"

            # Update status
            handoff.update_handoff_status(handoff_id1, "complete")

            # Reload and verify
            handoff2 = AutoHandoff()
            status = handoff2.get_handoff_status(handoff_id1)
            assert status["status"] == "complete", "Condition must be true"

            # Create second handoff
            handoff_id2, _ = handoff2.execute_handoff(phase="Phase 2")
            assert handoff_id2 == "HO-002", "handoff_id2 is not valid"
