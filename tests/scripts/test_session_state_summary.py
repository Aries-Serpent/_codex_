"""Tests for bounded session-state summaries."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent


def _load_module(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader, "spec is not valid"
    spec.loader.exec_module(module)
    return module


def test_context_window_summary_is_compact() -> None:
    """Large session payloads should be reduced to compact summaries."""
    module = _load_module(
        "context_window_optimizer",
        ROOT / "scripts" / "cognitive" / "context_window_optimizer.py",
    )

    summary = module.summarize_session_state(
        {
            "session_id": "abc",
            "branch": "feature/test",
            "last_commit": "deadbeef",
            "completed": ["task-" + str(i) for i in range(20)],
            "pending": ["pending-" + str(i) for i in range(20)],
            "context": "X" * 20_000,
            "files_modified": {f"file{i}.py": i for i in range(20)},
            "decisions": "Y" * 20_000,
        }
    )

    assert summary["context_summary"].endswith("limit]"), "Condition must be true"
    assert summary["decisions_made_and_rationale"].endswith("limit]"), "Condition must be true"
    assert summary["completed"].count("\n") <= 8, "Count must be greater than zero"
    assert summary["file_list_with_line_counts"].count("\n") <= 8, "Count must be greater than zero"


def test_session_manager_end_session_remains_bounded(tmp_path) -> None:
    """End-session payloads should stay compact even with large task lists."""
    module = _load_module(
        "session_manager",
        ROOT / "scripts" / "cognitive" / "session_manager.py",
    )

    manager = module.CognitiveBrainSessionManager(repo_root=str(tmp_path))
    manager.current_session = module.SessionState(
        session_id="session-123",
        pr_number=42,
        phase="review",
        started="2026-08-01T00:00:00Z",
        status="in_progress",
        completed_tasks=["done-" + str(i) for i in range(50)],
        pending_tasks=["todo-" + str(i) for i in range(50)],
        patterns_applied=["pattern-" + str(i) for i in range(50)],
        patterns_learned=["learned-" + str(i) for i in range(50)],
        files_created=[f"created-{i}.py" for i in range(50)],
        files_modified=[f"modified-{i}.py" for i in range(50)],
    )

    summary = manager.end_session()
    payload = json.dumps(summary)

    assert len(payload) < 8_000, "Payload must not be empty"
    assert "done-0" in payload, "Condition must be true"
    assert "done-49" not in payload, "Condition must be true"
