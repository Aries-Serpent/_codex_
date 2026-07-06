"""Tests for src/codex/cognitive/okr_tracker.py — Phase 2 coverage gap-fill.

Covers TaskStatus, OKRTask, KeyResult, Objective, OKRSummary, and OKRTracker.
"""

from __future__ import annotations

import pytest

from codex.cognitive.okr_tracker import (
    KeyResult,
    Objective,
    OKRSummary,
    OKRTask,
    OKRTracker,
    TaskStatus,
)

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class TestTaskStatus:
    def test_values_exist(self) -> None:
        assert TaskStatus.COMPLETE == "complete"
        assert TaskStatus.IN_PROGRESS == "in_progress"
        assert TaskStatus.PENDING == "pending"
        assert TaskStatus.BLOCKED == "blocked"

    def test_is_str_enum(self) -> None:
        assert isinstance(TaskStatus.COMPLETE, str)


# ---------------------------------------------------------------------------
# OKRTask
# ---------------------------------------------------------------------------


class TestOKRTask:
    def test_default_status(self) -> None:
        task = OKRTask(task_id="T-001", description="Fix CI")
        assert task.status == TaskStatus.PENDING

    def test_custom_status(self) -> None:
        task = OKRTask(
            task_id="T-002",
            description="Write docs",
            status=TaskStatus.COMPLETE,
        )
        assert task.status == TaskStatus.COMPLETE

    def test_notes_default_empty(self) -> None:
        task = OKRTask(task_id="T-003", description="Deploy")
        assert task.notes == ""

    def test_completed_at_default_none(self) -> None:
        task = OKRTask(task_id="T-004", description="Review")
        assert task.completed_at is None

    def test_completed_at_set(self) -> None:
        ts = "2026-01-01T00:00:00+00:00"
        task = OKRTask(task_id="T-005", description="Merge", completed_at=ts)
        assert task.completed_at == ts


# ---------------------------------------------------------------------------
# KeyResult
# ---------------------------------------------------------------------------


class TestKeyResult:
    def test_defaults(self) -> None:
        kr = KeyResult(
            kr_id="KR-01",
            description="Coverage > 80%",
            metric="coverage_pct",
        )
        assert kr.status == TaskStatus.PENDING
        assert kr.current_value == ""
        assert kr.target_value == ""

    def test_values_set(self) -> None:
        kr = KeyResult(
            kr_id="KR-02",
            description="Zero CVEs",
            metric="cve_count",
            current_value="0",
            target_value="0",
            status=TaskStatus.COMPLETE,
        )
        assert kr.current_value == "0"
        assert kr.status == TaskStatus.COMPLETE


# ---------------------------------------------------------------------------
# Objective
# ---------------------------------------------------------------------------


class TestObjective:
    @pytest.fixture()
    def obj_no_tasks(self) -> Objective:
        return Objective(
            obj_id="OBJ-TEST",
            title="Test Objective",
            description="For unit tests",
            deadline="2099-12-31",
        )

    @pytest.fixture()
    def obj_with_tasks(self) -> Objective:
        tasks = [
            OKRTask("T-A", "task A", TaskStatus.COMPLETE),
            OKRTask("T-B", "task B", TaskStatus.PENDING),
        ]
        return Objective(
            obj_id="OBJ-WT",
            title="With Tasks",
            description="Testing task completion",
            deadline="2099-12-31",
            tasks=tasks,
        )

    def test_pct_complete_no_tasks(self, obj_no_tasks: Objective) -> None:
        assert obj_no_tasks.pct_complete == 0.0

    def test_pct_complete_partial(self, obj_with_tasks: Objective) -> None:
        assert obj_with_tasks.pct_complete == 50.0

    def test_pct_complete_all_done(self) -> None:
        tasks = [
            OKRTask("T-1", "a", TaskStatus.COMPLETE),
            OKRTask("T-2", "b", TaskStatus.COMPLETE),
        ]
        obj = Objective(
            obj_id="OBJ-ALL",
            title="All done",
            description="",
            deadline="2099-12-31",
            tasks=tasks,
        )
        assert obj.pct_complete == 100.0

    def test_is_complete_false_when_pending(self, obj_with_tasks: Objective) -> None:
        assert obj_with_tasks.is_complete is False

    def test_is_complete_true_when_all_done(self) -> None:
        tasks = [OKRTask("T-X", "done", TaskStatus.COMPLETE)]
        obj = Objective(
            obj_id="OBJ-DONE",
            title="Complete",
            description="",
            deadline="2099-12-31",
            tasks=tasks,
        )
        assert obj.is_complete is True

    def test_is_complete_no_tasks(self, obj_no_tasks: Objective) -> None:
        # vacuously True: all() over empty iterable
        assert obj_no_tasks.is_complete is True


# ---------------------------------------------------------------------------
# OKRSummary
# ---------------------------------------------------------------------------


class TestOKRSummary:
    @pytest.fixture()
    def summary(self) -> OKRSummary:
        return OKRSummary(
            generated_at="2026-01-01T00:00:00+00:00",
            aais_score="B+",
            session_number=42,
            last_green_sha="abc123",
            objectives_total=4,
            objectives_complete=1,
            tasks_total=10,
            tasks_complete=8,
            tasks_remaining=["OBJ-001/T-X: final task (owner=Copilot)"],
            next_admin_actions=["Review PR"],
        )

    def test_pct_complete(self, summary: OKRSummary) -> None:
        assert summary.pct_complete == 80.0

    def test_pct_complete_zero_total(self) -> None:
        s = OKRSummary(
            generated_at="",
            aais_score="N/A",
            session_number=0,
            last_green_sha="",
            objectives_total=0,
            objectives_complete=0,
            tasks_total=0,
            tasks_complete=0,
            tasks_remaining=[],
            next_admin_actions=[],
        )
        assert s.pct_complete == 0.0

    def test_tasks_remaining_list(self, summary: OKRSummary) -> None:
        assert len(summary.tasks_remaining) == 1


# ---------------------------------------------------------------------------
# OKRTracker
# ---------------------------------------------------------------------------


class TestOKRTracker:
    @pytest.fixture()
    def tracker(self, tmp_path) -> OKRTracker:
        """Fresh tracker backed by tmp_path to avoid real filesystem state."""
        progress_path = tmp_path / "okr_progress.json"
        return OKRTracker(
            context_path=tmp_path / "agent_context.json",
            progress_path=progress_path,
        )

    def test_get_summary_returns_okr_summary(self, tracker: OKRTracker) -> None:
        summary = tracker.get_summary()
        assert isinstance(summary, OKRSummary)

    def test_get_summary_has_objectives(self, tracker: OKRTracker) -> None:
        summary = tracker.get_summary()
        # Must have at least one objective from the hard-coded build methods
        assert summary.tasks_total > 0

    def test_get_objective_found(self, tracker: OKRTracker) -> None:
        obj = tracker.get_objective("OBJ-001")
        assert obj is not None
        assert obj.obj_id.upper() == "OBJ-001"

    def test_get_objective_case_insensitive(self, tracker: OKRTracker) -> None:
        assert tracker.get_objective("obj-001") is not None

    def test_get_objective_missing_returns_none(self, tracker: OKRTracker) -> None:
        result = tracker.get_objective("OBJ-NONEXISTENT-999")
        assert result is None

    def test_mark_task_complete_valid(self, tracker: OKRTracker) -> None:
        obj = tracker.get_objective("OBJ-001")
        assert obj is not None, "OBJ-001 must exist"
        # Get the first task ID
        first_task_id = obj.tasks[0].task_id
        result = tracker.mark_task_complete("OBJ-001", first_task_id, notes="automated test")
        assert result is True

    def test_mark_task_complete_notes_saved(self, tracker: OKRTracker) -> None:
        obj = tracker.get_objective("OBJ-001")
        assert obj is not None
        first_task_id = obj.tasks[0].task_id
        tracker.mark_task_complete("OBJ-001", first_task_id, notes="test note")
        # Re-fetch and verify
        updated_obj = tracker.get_objective("OBJ-001")
        assert updated_obj is not None
        task = next(t for t in updated_obj.tasks if t.task_id == first_task_id)
        assert task.notes == "test note"

    def test_mark_task_complete_nonexistent_obj(self, tracker: OKRTracker) -> None:
        result = tracker.mark_task_complete("OBJ-GHOST", "T-000")
        assert result is False

    def test_mark_task_complete_nonexistent_task(self, tracker: OKRTracker) -> None:
        result = tracker.mark_task_complete("OBJ-001", "T-NOPE-9999")
        assert result is False

    def test_save_creates_progress_file(self, tracker: OKRTracker, tmp_path) -> None:
        tracker.save()
        progress_file = tmp_path / "okr_progress.json"
        assert progress_file.exists()

    def test_pct_complete_float(self, tracker: OKRTracker) -> None:
        summary = tracker.get_summary()
        assert isinstance(summary.pct_complete, float)
        assert 0.0 <= summary.pct_complete <= 100.0
