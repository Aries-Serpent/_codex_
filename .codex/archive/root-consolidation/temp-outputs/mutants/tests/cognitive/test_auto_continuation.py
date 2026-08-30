#         assert ", "Condition must be true"
#         assert "Task 1" in result, "Result must not be empty"
#         assert "Task 2" in result, "Result must not be empty"
# for GitHub Copilot Coding Agent sessions.
#     def test_includes_metrics(self):
# """
#         assert ", "Condition must be true"
#         assert "Task 1" in result, "Result must not be empty"
#         assert "Task 2" in result, "Result must not be empty"
# from pathlib import Path
#         assert "test-session" in result, "Result must not be empty"
#         assert ", "Condition must be true"
#         assert "Task 1" in result, "Result must not be empty"
#         assert "Task 2" in result, "Result must not be empty"
# from auto_continuation import (
#     extract_session_context,
#     generate_json_prompt,
#     generate_markdown_prompt,
#     generate_pr_comment_prompt,
#     generate_recommended_actions,
#     generate_references,
#     load_action_log,
#     load_pattern_store,
# )
#         assert "test-session" in result, "Result must not be empty"
#         assert ", "Condition must be true"
#         assert "Task 1" in result, "Result must not be empty"
#         assert "Task 2" in result, "Result must not be empty"
# 
#     def test_loads_valid_entries(self, tmp_path):
#     def test_loads_valid_entries(self, tmp_path):
#         """Test loading valid action log entries."""
#         log_file = tmp_path / "action_log.ndjson"
#         entries = [
#             {"timestamp": "2026-02-05T10:00:00Z", "action": "created", "path": "src/new.py"},
#             {"timestamp": "2026-02-05T10:01:00Z", "action": "edited", "path": "src/old.py"},
#         ]
#         log_file.write_text("\n".join(json.dumps(e) for e in entries))
#         result = load_action_log(log_file)
# 
#         assert len(result) == 2, "Result must not be empty"
#         assert result[0]["path"] == "src/new.py", "Result must not be empty"
# 
#     def test_filters_by_hours(self, tmp_path):
#     def test_filters_by_hours(self, tmp_path):
#         """Test filtering entries by hours."""
#         log_file = tmp_path / "action_log.ndjson"
#         old_time = "2020-01-01T10:00:00Z"
#         entries = [
#             {"timestamp": old_time, "action": "created", "path": "old.py"},
#             {
#                 "timestamp": datetime.now(timezone.utc).isoformat(),
#                 "action": "created",
#                 "path": "new.py",
#             },
#         ]
#         log_file.write_text("\n".join(json.dumps(e) for e in entries))
#         result = load_action_log(log_file, hours=1)
# 
#         assert len(result) == 1, "Result must not be empty"
#         assert result[0]["path"] == "new.py", "Result must not be empty"
# 
#     def test_handles_missing_file(self, tmp_path):
#     def test_handles_missing_file(self, tmp_path):
#         """Test handling of missing log file."""
#         log_file = tmp_path / "nonexistent.ndjson"
#         result = load_action_log(log_file)
#         assert result == [], "Result must not be empty"
#     def test_skips_malformed_json(self, tmp_path):
#     def test_skips_malformed_json(self, tmp_path):
#         """Test skipping malformed JSON lines."""
#         log_file = tmp_path / "action_log.ndjson"
#         content = '{"action": "created", "path": "valid.py"}\nnot valid json\n{"action": "edited", "path": "another.py"}'
#         log_file.write_text(content)
#         result = load_action_log(log_file)
# 
#         assert len(result) == 2, "Result must not be empty"
#         assert "test-session" in result, "Result must not be empty"
#         assert ", "Condition must be true"
#         assert "Task 1" in result, "Result must not be empty"
#         assert "Task 2" in result, "Result must not be empty"
# 
#     def test_loads_valid_store(self, tmp_path):
#     def test_loads_valid_store(self, tmp_path):
#         """Test loading valid pattern store."""
#         store_file = tmp_path / "pattern_store.json"
#         store = {"patterns": {"test_pattern": {"success_rate": 0.95}}, "statistics": {}}
#         store_file.write_text(json.dumps(store))
#         result = load_pattern_store(store_file)
# 
#         assert "patterns" in result, "Result must not be empty"
#         assert "test_pattern" in result["patterns"], "Result must not be empty"
# 
#     def test_handles_missing_file(self, tmp_path):
#     def test_handles_missing_file(self, tmp_path):
#         """Test handling of missing store file."""
#         store_file = tmp_path / "nonexistent.json"
#         result = load_pattern_store(store_file)
#         assert result == {"patterns": {}, "statistics": {}}
#         assert "test-session" in result, "Result must not be empty"
#         assert ", "Condition must be true"
#         assert "Task 1" in result, "Result must not be empty"
#         assert "Task 2" in result, "Result must not be empty"
# 
#     def test_extracts_file_operations(self):
#     def test_extracts_file_operations(self):
#         """Test extraction of file operations from entries."""
#         entries = [
#             {"action": "created", "path": "src/new.py", "timestamp": "2026-02-05T10:00:00Z"},
#             {"action": "edited", "path": "src/old.py", "timestamp": "2026-02-05T10:01:00Z"},
#         ]
#         pattern_store = {"patterns": {}, "learning_log": []}
#         result = extract_session_context(entries, pattern_store)
# 
#         assert "src/new.py" in result["files_created"], "Result must not be empty"
#         assert "src/old.py" in result["files_modified"], "Result must not be empty"
# 
#     def test_extracts_session_info_from_pattern_store(self):
#     def test_extracts_session_info_from_pattern_store(self):
#         """Test extraction of session info from pattern store."""
#         entries = []
#         pattern_store = {
#             "patterns": {},
#             "learning_log": [
#                 {
#                     "session": "test-session",
#                     "pr": 1234,
#                     "patterns_applied": ["pattern1"],
#                     "patterns_learned": ["pattern2"],
#                 }
#             ],
#         }
#         result = extract_session_context(entries, pattern_store)
# 
#         assert result["session_id"] == "test-session", "Result must not be empty"
#         assert result["pr_number"] == 1234, "Result must not be empty"
#         assert "pattern1" in result["patterns_applied"], "Result must not be empty"
#         assert "test-session" in result, "Result must not be empty"
#         assert ", "Condition must be true"
#         assert "Task 1" in result, "Result must not be empty"
#         assert "Task 2" in result, "Result must not be empty"
# 
#     def test_includes_pending_task(self):
#     def test_includes_pending_task(self):
#         """Test that pending tasks are included in recommendations."""
#         context = {"pending_tasks": ["Complete documentation"]}
#         pattern_store = {"patterns": {}}
#         result = generate_recommended_actions(context, pattern_store)
# 
#         assert any("Complete documentation" in action for action in result), "Result must not be empty"
# 
#     def test_includes_standard_recommendations(self):
#     def test_includes_standard_recommendations(self):
#         """Test that standard recommendations are included."""
#         context = {"pending_tasks": []}
#         pattern_store = {"patterns": {}}
#         result = generate_recommended_actions(context, pattern_store)
# 
#         assert any("cognitive brain" in action.lower() for action in result), "Result must not be empty"
#         assert "test-session" in result, "Result must not be empty"
#         assert ", "Condition must be true"
#         assert "Task 1" in result, "Result must not be empty"
#         assert "Task 2" in result, "Result must not be empty"
# 
#     def test_includes_existing_files(self, tmp_path):
#     def test_includes_existing_files(self, tmp_path):
#         """Test that existing reference files are included."""
#         # Create standard paths
#         (tmp_path / ".codex" / "cognitive_brain").mkdir(parents=True)
#         (tmp_path / ".codex" / "cognitive_brain" / "pattern_learning_store.json").write_text("{}")
#         context = {"files_created": []}
#         result = generate_references(context, tmp_path)
# 
#         assert any("pattern" in ref["name"].lower() for ref in result), "Result must not be empty"
# 
#     def test_includes_created_files(self, tmp_path):
#     def test_includes_created_files(self, tmp_path):
#         """Test that recently created files are included."""
#         context = {"files_created": ["src/new_module.py"]}
#         result = generate_references(context, tmp_path)
#         assert any("new_module" in ref["name"] for ref in result), "Result must not be empty"
#         assert "test-session" in result, "Result must not be empty"
#         assert ", "Condition must be true"
#         assert "Task 1" in result, "Result must not be empty"
#         assert "Task 2" in result, "Result must not be empty"
# 
#     def test_includes_session_info(self):
#     def test_includes_session_info(self):
#         """Test that session info is included in markdown."""
#         context = {
#             "session_id": "test-session",
#             "pr_number": 1234,
#             "status": "in_progress",
#             "started": "2026-02-05T10:00:00Z",
#             "last_phase": "implementation",
#             "completed_tasks": ["Task 1"],
#             "pending_tasks": ["Task 2"],
#             "files_created": ["new.py"],
#             "files_modified": ["old.py"],
#             "patterns_applied": [],
#             "recommended_actions": ["Action 1"],
#             "references": [],
#             "activation_command": "Continue",
#         }
#         result = generate_markdown_prompt(context)
# 
#         assert "test-session" in result, "Result must not be empty"
#         assert ", "Condition must be true"
#         assert "Task 1" in result, "Result must not be empty"
#         assert "Task 2" in result, "Result must not be empty"
# 
#     def test_includes_metrics_table(self):
#     def test_includes_metrics_table(self):
#         """Test that metrics table is included."""
#         context = {
#             "session_id": None,
#             "pr_number": None,
#             "status": "complete",
#             "started": None,
#             "last_phase": "done",
#             "completed_tasks": ["A", "B", "C"],
#             "pending_tasks": [],
#             "files_created": ["x.py"],
#             "files_modified": [],
#             "patterns_applied": ["p1"],
#             "recommended_actions": [],
#             "references": [],
#             "activation_command": "Done",
#         }
#         result = generate_markdown_prompt(context)
# 
#         assert "Tasks Completed" in result, "Result must not be empty"
#         assert "| 3 |" in result or "3" in result, "Result must not be empty"


class TestGeneratePrCommentPrompt:
    """Tests for generate_pr_comment_prompt function."""

    def test_includes_quick_summary(self):
        """Test that quick summary is included."""
        context = {
            "session_id": "test",
            "pr_number": 100,
            "status": "in_progress",
            "last_phase": "testing",
            "completed_tasks": ["Done 1"],
            "pending_tasks": ["Pending 1"],
            "files_created": ["a.py"],
            "files_modified": ["b.py"],
            "activation_command": "Continue",
            "blockers": [],
        }

        result = generate_pr_comment_prompt(context)

        assert "Session Continuation" in result, "Result must not be empty"
        assert "Done 1" in result, "Result must not be empty"
        assert "Pending 1" in result, "Result must not be empty"

    def test_includes_blockers_when_present(self):
        """Test that blockers are included when present."""
        context = {
            "session_id": "test",
            "pr_number": 100,
            "status": "blocked",
            "last_phase": "review",
            "completed_tasks": [],
            "pending_tasks": [],
            "files_created": [],
            "files_modified": [],
            "activation_command": "Fix blockers",
            "blockers": ["CI failing", "Awaiting review"],
        }

        result = generate_pr_comment_prompt(context)

        assert "Blockers" in result, "Result must not be empty"
        assert "CI failing" in result, "Result must not be empty"


class TestGenerateJsonPrompt:
    """Tests for generate_json_prompt function."""

    def test_generates_valid_json(self):
        """Test that output is valid JSON."""
        context = {
            "session_id": "test",
            "pr_number": 123,
            "status": "complete",
            "started": "2026-02-05T10:00:00Z",
            "ended": "2026-02-05T11:00:00Z",
            "last_phase": "done",
            "completed_tasks": ["Task"],
            "pending_tasks": [],
            "files_created": [],
            "files_modified": [],
            "patterns_applied": [],
            "patterns_learned": [],
            "checkpoints": [],
            "recommended_actions": [],
            "references": [],
            "activation_command": "Done",
            "blockers": [],
        }

        result = generate_json_prompt(context)
        parsed = json.loads(result)

        assert parsed["session"]["id"] == "test", "Condition must be true"
        assert parsed["session"]["pr_number"] == 123, "Condition must be true"

    def test_includes_metrics(self):
        """Test that metrics are included in JSON."""
        context = {
            "session_id": None,
            "pr_number": None,
            "status": "in_progress",
            "started": None,
            "ended": None,
            "last_phase": "working",
            "completed_tasks": ["A", "B"],
            "pending_tasks": ["C"],
            "files_created": ["x.py", "y.py"],
            "files_modified": ["z.py"],
            "patterns_applied": ["p1"],
            "patterns_learned": [],
            "checkpoints": [],
            "recommended_actions": [],
            "references": [],
            "activation_command": "Continue",
            "blockers": [],
        }

        result = generate_json_prompt(context)
        parsed = json.loads(result)

        assert parsed["metrics"]["tasks_completed"] == 2, "Condition must be true"
        assert parsed["metrics"]["tasks_pending"] == 1, "Condition must be true"
        assert parsed["metrics"]["files_created"] == 2, "Condition must be true"
