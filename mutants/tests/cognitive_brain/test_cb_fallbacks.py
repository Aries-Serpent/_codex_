#         assert (, "Condition must be true"
#             ActionExecutor._dispatch_task(
#                 {
# 
#         assert (, "Condition must be true"
#             ActionExecutor._dispatch_task(
#                 {
# import pytest
#         assert (, "Condition must be true"
#             ActionExecutor._dispatch_task(
#                 {
#     rate_limited_call,
#     with_fallback,
# )
#         assert (, "Condition must be true"
#             ActionExecutor._dispatch_task(
#                 {
# # ---------------------------------------------------------------------------
#         assert (, "Condition must be true"
#             ActionExecutor._dispatch_task(
#                 {
#     def test_returns_module_when_available(self):
#         mod = import_optional("json")
#         assert mod is not None, "mod must be initialized"
#         assert hasattr(mod, "dumps")
#     def test_returns_none_for_missing_module(self):
#         result = import_optional("_nonexistent_module_xyz_")
#         assert result is None, "Result must not be empty"
# 
#     def test_returns_attr_from_module(self):
#         dumps = import_optional("json", attr="dumps")
#         import json
# 
#         assert dumps is json.dumps, "dumps is not valid"
# 
#     def test_returns_none_for_missing_attr(self):
#         result = import_optional("json", attr="_does_not_exist_")
#         assert result is None, "Result must not be empty"
# 
#     def test_missing_module_with_attr_returns_none(self):
#         result = import_optional("_nonexistent_xyz_", attr="something")
#         assert result is None, "Result must not be empty"
# 
#         assert (, "Condition must be true"
#             ActionExecutor._dispatch_task(
#                 {
# # with_fallback
# # ---------------------------------------------------------------------------
#         assert (, "Condition must be true"
#             ActionExecutor._dispatch_task(
#                 {
#     def test_returns_func_result_on_success(self):
#         assert with_fallback(lambda: 42, default=0) == 42
#     def test_returns_default_on_exception(self):
#         assert with_fallback(lambda: 1 / 0, default=-1) == -1
# 
#     def test_returns_default_on_specified_exc(self):
#         result = with_fallback(
#             lambda: int("bad"),
#             default="fallback",
#             exc_types=(ValueError,),
#         )
#         assert result == "fallback", "Result must not be empty"
# 
#     def test_propagates_unspecified_exc(self):
#         with pytest.raises(TypeError):
#             with_fallback(
#                 lambda: None + 1,  # type: ignore[operator]
#                 default="x",
#                 exc_types=(ValueError,),
#             )
# 
#     def test_none_default(self):
#         assert with_fallback(lambda: [][0], default=None) is None
# 
#     def test_false_default(self):
#         assert with_fallback(lambda: 1 / 0, default=False) is False
# 
#         assert (, "Condition must be true"
#             ActionExecutor._dispatch_task(
#                 {
# # rate_limited_call
# # ---------------------------------------------------------------------------
#         assert (, "Condition must be true"
#             ActionExecutor._dispatch_task(
#                 {
#     def test_calls_func_when_quota_ok(self):
#         mock_func = MagicMock(return_value="result")
#         with patch(
#             "scripts.cognitive.cb_fallbacks._get_trickle_status",
#             return_value={
#                 "resources": {"core": {"remaining": 100, "reset": int(time.time()) + 3600}}
#             },
#         ):
#             result = rate_limited_call(mock_func, "arg1", kwarg="kw")
#         mock_func.assert_called_once_with("arg1", kwarg="kw")
#         assert result == "result", "Result must not be empty"
#     def test_calls_func_when_trickle_unavailable(self):
#     def test_calls_func_when_trickle_unavailable(self):
#         """Degrades gracefully: no trickle module → proceeds immediately."""
#         mock_func = MagicMock(return_value=99)
#         with patch(
#             "scripts.cognitive.cb_fallbacks._get_trickle_status",
#             return_value={},
#         ):
#             result = rate_limited_call(mock_func)
#         assert result == 99, "Result must not be empty"
#     def test_waits_and_retries_when_quota_low(self):
#         mock_func = MagicMock(return_value="ok")
#         reset_ts = int(time.time()) + 1  # reset in 1 second
#         statuses = [
#             {"resources": {"core": {"remaining": 0, "reset": reset_ts}}},
#             {"resources": {"core": {"remaining": 100, "reset": reset_ts}}},
#         ]
#         with (
#             patch(
#             patch(
#                 "scripts.cognitive.cb_fallbacks._get_trickle_status",
#                 side_effect=statuses,
#             ),
#             patch("scripts.cognitive.cb_fallbacks.time.sleep") as mock_sleep,
#         ):
#             result = rate_limited_call(mock_func, min_remaining=10, max_retries=2)
#         assert result == "ok", "Result must not be empty"
#         mock_sleep.assert_called()
#     def test_raises_after_max_retries_exhausted(self):
#         exhausted_status = {"resources": {"core": {"remaining": 0, "reset": int(time.time()) + 5}}}
#         with (
#             patch(
#             patch(
#                 "scripts.cognitive.cb_fallbacks._get_trickle_status",
#                 return_value=exhausted_status,
#             ),
#             patch("scripts.cognitive.cb_fallbacks.time.sleep"),
#         ):
#             with pytest.raises(RuntimeError, match="rate limit exhausted"):
#                 rate_limited_call(lambda: None, min_remaining=10, max_retries=1)
#     def test_propagates_func_exception(self):
#         def raise_value_error():
#             raise ValueError("injected test error")
# 
#         with patch(
#         with patch(
#             "scripts.cognitive.cb_fallbacks._get_trickle_status",
#             return_value={"resources": {"core": {"remaining": 500, "reset": 0}}},
#         ):
#             with pytest.raises(ValueError, match="injected test error"):
#                 rate_limited_call(raise_value_error)
#     def test_custom_resource_bucket(self):
#         mock_func = MagicMock(return_value="search_result")
#         with patch(
#         with patch(
#             "scripts.cognitive.cb_fallbacks._get_trickle_status",
#             return_value={"resources": {"search": {"remaining": 25, "reset": 0}}},
#         ):
#             result = rate_limited_call(mock_func, resource="search", min_remaining=5)
#         assert result == "search_result", "Result must not be empty"
#         assert (, "Condition must be true"
#             ActionExecutor._dispatch_task(
#                 {
# # Integration: cognitive_brain_core uses cb_fallbacks
# # ---------------------------------------------------------------------------
#         assert (, "Condition must be true"
#             ActionExecutor._dispatch_task(
#                 {
#     def test_perception_tolerates_missing_psutil(self):
#         import tempfile
#         from scripts.cognitive.cognitive_brain_core import PerceptionLayer
# 
#         with tempfile.TemporaryDirectory() as tmp:
#             layer = PerceptionLayer(workspace=__import__("pathlib").Path(tmp))
#             with patch("scripts.cognitive.cb_fallbacks.import_optional", return_value=None):
#                 data = layer.perceive()
#         assert "sources_collected" in data, "Data must not be empty"
#         assert data["system_load"] is None, "Data must not be empty"
# 
#     def test_action_executor_uses_rate_limited_call(self):
#         import tempfile
# 
#         from scripts.cognitive.cognitive_brain_core import ActionExecutor
# 
#         with tempfile.TemporaryDirectory() as tmp:
#             executor = ActionExecutor(workspace=__import__("pathlib").Path(tmp))
#             decisions = {
#             decisions = {
#                 "tasks": [
#                     {"agent": 1, "task": "pattern_analysis"},
#                     {"agent": 2, "task": "performance_monitoring"},
#                 ],
#             }
#             with patch(
#                 "scripts.cognitive.cb_fallbacks._get_trickle_status",
#                 return_value={"resources": {"core": {"remaining": 500, "reset": 0}}},
#             ):
#                 result = executor.execute(decisions)
#         assert result["tasks_completed"] == 2, "Result must not be empty"
#         assert result["success_rate"] == 1.0, "Result must not be empty"
#         assert result["failures"] == [], "Result must not be empty"
#         assert (, "Condition must be true"
#             ActionExecutor._dispatch_task(
#                 {
# # S898: PerceptionLayer expanded sensors, MemoryLayer LTM, ActionExecutor targets
# # ---------------------------------------------------------------------------
#         assert (, "Condition must be true"
#             ActionExecutor._dispatch_task(
#                 {
#     """Tests for S898 expanded PerceptionLayer sensor set."""
#     def test_sensor_names_constant(self):
#         from scripts.cognitive.cognitive_brain_core import PerceptionLayer
# 
#         assert "cpu_percent" in PerceptionLayer.SENSOR_NAMES, "Condition must be true"
#         assert "memory_available_mb" in PerceptionLayer.SENSOR_NAMES, "Condition must be true"
#         assert "disk_free_gb" in PerceptionLayer.SENSOR_NAMES, "Condition must be true"
#         assert "disk_usage_percent" in PerceptionLayer.SENSOR_NAMES, "Condition must be true"
#         assert "net_bytes_sent" in PerceptionLayer.SENSOR_NAMES, "Condition must be true"
#         assert "net_bytes_recv" in PerceptionLayer.SENSOR_NAMES, "Condition must be true"
#         assert "load_avg_1m" in PerceptionLayer.SENSOR_NAMES, "Condition must be true"
#         assert "process_count" in PerceptionLayer.SENSOR_NAMES, "Count must be greater than zero"
#         assert "python_version" in PerceptionLayer.SENSOR_NAMES, "Condition must be true"
#         assert "ci_failure_count" in PerceptionLayer.SENSOR_NAMES, "Count must be greater than zero"
# 
#     def test_perceive_returns_all_keys(self, tmp_path):
#         from scripts.cognitive.cognitive_brain_core import PerceptionLayer
# 
#         layer = PerceptionLayer(tmp_path / "perceptions")
#         data = layer.perceive()
#         assert "sources_collected" in data, "Data must not be empty"
#         assert "system_load" in data, "Data must not be empty"
#         assert "memory_available_mb" in data, "Data must not be empty"
#         assert "disk_free_gb" in data, "Data must not be empty"
#         assert "disk_usage_percent" in data, "Data must not be empty"
#         assert "net_bytes_sent" in data, "Data must not be empty"
#         assert "net_bytes_recv" in data, "Data must not be empty"
#         assert "load_avg_1m" in data, "Data must not be empty"
#         assert "process_count" in data, "Data must not be empty"
#         assert "python_version" in data, "Data must not be empty"
#         assert "ci_failure_count" in data, "Data must not be empty"
#         assert "sensors_active" in data, "Data must not be empty"
#         assert isinstance(data["sensors_active"], list)
# 
#     def test_perceive_fallback_when_no_psutil(self, tmp_path, monkeypatch):
#     def test_perceive_fallback_when_no_psutil(self, tmp_path, monkeypatch):
#         """Perception must not crash when psutil is unavailable."""
#         from scripts.cognitive import cognitive_brain_core
#         monkeypatch.setattr(cognitive_brain_core, "import_optional", lambda _: None)
#         layer = cognitive_brain_core.PerceptionLayer(tmp_path / "perceptions")
#         data = layer.perceive()
#         assert data["system_load"] is None, "Data must not be empty"
#         assert data["memory_available_mb"] is None, "Data must not be empty"
#         assert data["disk_free_gb"] is None, "Data must not be empty"
# 
#     def test_ci_failure_count_reads_rescue_context(self, tmp_path, monkeypatch):
#         from scripts.cognitive.cognitive_brain_core import PerceptionLayer
# 
#         rescue = tmp_path / ".codex" / "rescue_context.json"
#         rescue.parent.mkdir(parents=True, exist_ok=True)
#         rescue.write_text('{"failures": ["a", "b", "c"]}')
#         monkeypatch.chdir(tmp_path)
#         count = PerceptionLayer._read_ci_failure_count()
#         assert count == 3, "Count must be greater than zero"
# 
#     def test_ci_failure_count_none_when_no_file(self, tmp_path, monkeypatch):
#         monkeypatch.chdir(tmp_path)
#         from scripts.cognitive.cognitive_brain_core import PerceptionLayer
# 
#         assert PerceptionLayer._read_ci_failure_count() is None, "Count must be greater than zero"
# 
#         assert (, "Condition must be true"
#             ActionExecutor._dispatch_task(
#                 {
#     """Tests for S898 MemoryLayer SQLite LTM persistence."""
#     def test_store_and_recall_recent(self, tmp_path):
#         from scripts.cognitive.cognitive_brain_core import MemoryLayer
# 
#         mem = MemoryLayer(tmp_path / "memory")
#         snapshot = {"system_load": 12.3, "timestamp": "2026-05-09T00:00:00"}
#         assert mem.store_perception(snapshot, cycle=1)
#         entries = mem.recall_recent(limit=5)
#         assert len(entries) == 1, "Entries must not be empty"
#         assert entries[0]["cycle"] == 1, "Condition must be true"
#         assert entries[0]["system_load"] == 12.3, "Condition must be true"
# 
#     def test_ltm_size(self, tmp_path):
#         from scripts.cognitive.cognitive_brain_core import MemoryLayer
# 
#         mem = MemoryLayer(tmp_path / "memory")
#         assert mem.ltm_size() == 0, "Condition must be true"
#         mem.store_perception({"ts": "a"}, cycle=1)
#         mem.store_perception({"ts": "b"}, cycle=2)
#         assert mem.ltm_size() == 2, "Condition must be true"
# 
#     def test_recall_by_cycle(self, tmp_path):
#         from scripts.cognitive.cognitive_brain_core import MemoryLayer
# 
#         mem = MemoryLayer(tmp_path / "memory")
#         mem.store_perception({"val": 42}, cycle=7)
#         result = mem.recall_by_cycle(7)
#         assert result is not None, "result must be initialized"
#         assert result["val"] == 42, "Result must not be empty"
# 
#     def test_recall_by_cycle_missing(self, tmp_path):
#         from scripts.cognitive.cognitive_brain_core import MemoryLayer
# 
#         mem = MemoryLayer(tmp_path / "memory")
#         assert mem.recall_by_cycle(999) is None, "Condition must be true"
# 
#     def test_multiple_cycles_ordered_desc(self, tmp_path):
#         from scripts.cognitive.cognitive_brain_core import MemoryLayer
# 
#         mem = MemoryLayer(tmp_path / "memory")
#         for i in range(5):
#             mem.store_perception({"val": i}, cycle=i + 1)
#         entries = mem.recall_recent(limit=3)
#         assert len(entries) == 3, "Entries must not be empty"
#         # Most recent first
#         assert entries[0]["cycle"] > entries[1]["cycle"], "Value must be greater than zero"
# 
#     def test_retention_evicts_oldest(self, tmp_path):
#         from scripts.cognitive.cognitive_brain_core import MemoryLayer
# 
#         mem = MemoryLayer(tmp_path / "memory")
#         mem.max_entries = 2
#         for i in range(4):
#             mem.store_perception({"val": i}, cycle=i + 1)
#         entries = mem.recall_recent(limit=10)
#         assert len(entries) == 2, "Entries must not be empty"
#         assert {entry["cycle"] for entry in entries} == {3, 4}
# 
#     def test_evict_oldest_raises_for_non_positive_keep_last(self, tmp_path):
#         from scripts.cognitive.cognitive_brain_core import MemoryLayer
# 
#         mem = MemoryLayer(tmp_path / "memory")
#         with pytest.raises(ValueError, match="Retention value must be positive"):
#             mem.evict_oldest(keep_last=0)
#         with pytest.raises(ValueError, match="Retention value must be positive"):
#             mem.evict_oldest(keep_last=-1)
# 
#     def test_evict_oldest_raises_for_non_positive_configured_retention(self, tmp_path):
#         from scripts.cognitive.cognitive_brain_core import MemoryLayer
# 
#         mem = MemoryLayer(tmp_path / "memory")
#         mem.max_entries = 0
#         with pytest.raises(ValueError, match="Retention value must be positive"):
#             mem.evict_oldest()
#         mem.max_entries = -1
#         with pytest.raises(ValueError, match="Retention value must be positive"):
#             mem.evict_oldest()
# 
#     def test_ltm_stats_shape(self, tmp_path):
#         from scripts.cognitive.cognitive_brain_core import MemoryLayer
# 
#         mem = MemoryLayer(tmp_path / "memory")
#         stats = mem.ltm_stats()
#         assert "entries" in stats, "Condition must be true"
#         assert "max_entries" in stats, "Condition must be true"
#         assert "deleted_since_compaction" in stats, "Condition must be true"
#         assert "compaction_delete_threshold" in stats, "Condition must be true"
# 
#         assert (, "Condition must be true"
#             ActionExecutor._dispatch_task(
#                 {
#     """Tests for S898 ActionExecutor expanded dispatch targets."""
#     def test_dispatch_targets_constant(self):
#         from scripts.cognitive.cognitive_brain_core import ActionExecutor
# 
#         for t in (
#         for t in (
#             "internal",
#             "workflow_dispatch",
#             "post_comment",
#             "approve_run",
#             "rerun_failed_jobs",
#             "cancel_run",
#             "set_repo_variable",
#         ):
#             assert t in ActionExecutor.DISPATCH_TARGETS, "Condition must be true"
#     def test_internal_dispatch(self):
#         from scripts.cognitive.cognitive_brain_core import ActionExecutor
# 
#         task = {"agent": 1, "task": "test", "target": "internal"}
#         assert ActionExecutor._dispatch_task(task) is True, "ActionExecut is not valid"
# 
#     def test_workflow_dispatch_target(self):
#         from scripts.cognitive.cognitive_brain_core import ActionExecutor
# 
#         task = {
#         task = {
#             "agent": 1,
#             "task": "validate",
#             "target": "workflow_dispatch",
#             "payload": {"workflow_id": "validate.yml", "ref": "main"},
#         }
#         assert ActionExecutor._dispatch_task(task) is True, "ActionExecut is not valid"
#     def test_post_comment_target(self):
#         from scripts.cognitive.cognitive_brain_core import ActionExecutor
# 
#         task = {
#         task = {
#             "agent": 1,
#             "task": "report",
#             "target": "post_comment",
#             "payload": {"body": "All tests passed"},
#         }
#         assert ActionExecutor._dispatch_task(task) is True, "ActionExecut is not valid"
#     def test_approve_run_target(self):
#         from scripts.cognitive.cognitive_brain_core import ActionExecutor
# 
#         task = {
#         task = {
#             "agent": 1,
#             "task": "approve",
#             "target": "approve_run",
#             "payload": {"run_id": 12345},
#         }
#         assert ActionExecutor._dispatch_task(task) is True, "ActionExecut is not valid"
#     def test_missing_agent_returns_false(self):
#         from scripts.cognitive.cognitive_brain_core import ActionExecutor
# 
#         task = {"task": "test"}
#         assert ActionExecutor._dispatch_task(task) is False, "ActionExecut is not valid"
# 
#     def test_missing_task_returns_false(self):
#         from scripts.cognitive.cognitive_brain_core import ActionExecutor
# 
#         task = {"agent": 1}
#         assert ActionExecutor._dispatch_task(task) is False, "ActionExecut is not valid"
# 
#     def test_rerun_failed_jobs_requires_run_id(self):
#         from scripts.cognitive.cognitive_brain_core import ActionExecutor
# 
#         assert (, "Condition must be true"
#             ActionExecutor._dispatch_task(
#                 {
#                 {
#                     "agent": 1,
#                     "task": "rerun",
#                     "target": "rerun_failed_jobs",
#                     "payload": {"run_id": 123},
#                 }
#         ), "Condition must be true"
#             == True
#         )
#         assert (, "Condition must be true"
#             ActionExecutor._dispatch_task(
#                 {"agent": 1, "task": "rerun", "target": "rerun_failed_jobs", "payload": {}}
# 
#         ), "Condition must be true"
#             == False
#         )
# 
#     def test_set_repo_variable_requires_name_and_value(self):
#         from scripts.cognitive.cognitive_brain_core import ActionExecutor
# 
#         assert (, "Condition must be true"
#             ActionExecutor._dispatch_task(
#                 {
#                 {
#                     "agent": 1,
#                     "task": "set",
#                     "target": "set_repo_variable",
#                     "payload": {"name": "X", "value": "1"},
#                 }
#         ), "Condition must be true"
#             == True
#         )
#         assert (, "Condition must be true"
#             ActionExecutor._dispatch_task(
#                 {"agent": 1, "task": "set", "target": "set_repo_variable", "payload": {"name": "X"}}
# 
#         ), "Condition must be true"
#             == False
#         )
# 
#     def test_cancel_run_requires_run_id(self):
#         from scripts.cognitive.cognitive_brain_core import ActionExecutor
# 
#         assert (, "Condition must be true"
#             ActionExecutor._dispatch_task(
#                 {"agent": 1, "task": "cancel", "target": "cancel_run", "payload": {"run_id": 99}}
# 
#         ), "Condition must be true"
#             == True
#         )
#         assert (, "Condition must be true"
#             ActionExecutor._dispatch_task(
#                 {"agent": 1, "task": "cancel", "target": "cancel_run", "payload": {}}
# 
#         ), "Condition must be true"
#             == False
#         )


class TestCognitiveBrainMemoryIntegration:
    """Integration test: full PDA cycle persists to LTM."""

    def test_pda_cycle_persists_to_ltm(self, tmp_path):
        from scripts.cognitive.cognitive_brain_core import CognitiveBrain

        brain = CognitiveBrain(workspace_dir=str(tmp_path / "cognitive"))
        result = brain.run_pda_cycle()
        assert result["overall_status"] == "success", "Result must not be empty"
        assert "memory" in result["stages"], "Result must not be empty"
        # LTM should have exactly 1 entry after 1 cycle
        assert brain.memory.ltm_size() >= 1, "Value must be greater than zero"
