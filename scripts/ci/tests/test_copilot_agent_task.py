"""Focused smoke wrapper for the repository Copilot Agent Task controller."""

from __future__ import annotations

from scripts.ci import copilot_agent_task as task


def test_launch_key_and_preflight_contract() -> None:
    launch_key = task.generate_launch_key("Fix tests", owner="Aries-Serpent", repo="_codex_")
    assert len(launch_key) == 40
    assert task.validate_launch_key(launch_key)


def test_sub_pr_and_promotion_branch_contract() -> None:
    assert task.validate_branch_pair("0D_base_", "copilot/session-resume")
    assert task.validate_branch_pair("main", "0D_base_", promotion=True)
    assert not task.validate_branch_pair("0D_base_", "feature/tests")
