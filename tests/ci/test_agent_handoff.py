"""Focused tests for the repository-native agent handoff writer."""

from __future__ import annotations

from scripts.agents.agent_handoff import write_handoff


def test_write_handoff_writes_atomic_resume_record(tmp_path) -> None:
    state_dir = tmp_path / ".codex"
    record = write_handoff(
        {
            "task_id": "task-123",
            "objective": "Resume PR 5766 implementation",
            "branch": "0D_base_",
            "pr_number": "5766",
            "last_verified_sha": "b514285e75c4a9c47cb0d9334b3fb756cc43d5dd",
            "next_objective": "Complete Agent Tasks integration",
            "stop_conditions": "Do not merge without exact-SHA gates",
        },
        repo_root=tmp_path,
        state_dir=state_dir,
    )

    assert record["task_id"] == "task-123"
    assert record["next_objective"] == "Complete Agent Tasks integration"
    assert (state_dir / "copilot_agent_task_handoff.json").is_file()
