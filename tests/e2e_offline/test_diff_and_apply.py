"""Offline end-to-end tests for the Zendesk diff workflow."""

from codex.zendesk.model import Action, Condition, Trigger
from codex.zendesk.plan import diff_engine


def test_diff_and_apply_no_changes() -> None:
    diffs = diff_engine.diff_triggers([], [])
    assert diffs == []


def test_diff_triggers_add_new() -> None:
    desired = [
        Trigger(
            name="New Trigger",
            category="assignment",
            conditions={"all": [Condition(field="priority", operator="is", value="urgent")]},
            actions=[Action(field="group_id", value=2)],
            position=1,
        )
    ]
    actual: list[Trigger] = []

    diffs = diff_engine.diff_triggers(desired, actual)

    assert diffs and diffs[0]["op"] == "add"
