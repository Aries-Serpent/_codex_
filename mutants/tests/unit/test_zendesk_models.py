"""Unit tests for Zendesk model diff logic."""

from codex.zendesk.model import (
    Action,
    Condition,
    Group,
    Membership,
    TicketField,
    Trigger,
)


def test_trigger_diff_changes_position_and_category() -> None:
    trigger_current = Trigger(
        name="Assign to L2",
        category="assignment",
        conditions={"all": [Condition(field="priority", operator="is", value="high")]},
        actions=[Action(field="group_id", value=1)],
        position=2,
    )
    trigger_desired = Trigger(
        name="Assign to L2",
        category="notifications",
        conditions={"all": [Condition(field="priority", operator="is", value="high")]},
        actions=[Action(field="group_id", value=1)],
        position=1,
    )

    patches = trigger_desired.diff(trigger_current)

    assert any(patch["path"] == "/position" for patch in patches)
    assert any(patch["path"] == "/category" for patch in patches)


def test_ticketfield_diff_detects_options_change() -> None:
    field_current = TicketField(
        name="Relocation_Type",
        type="dropdown",
        options=["A", "C"],
        active=True,
    )
    field_desired = TicketField(
        name="Relocation_Type",
        type="dropdown",
        options=["A", "B"],
        active=True,
    )

    patches = field_desired.diff(field_current)

    assert patches and patches[0]["path"] == "/options"


def test_group_diff_membership_change() -> None:
    group_current = Group(
        name="Ops",
        description="Ops group",
        memberships=[],
    )
    group_desired = Group(
        name="Ops",
        description="Ops group",
        memberships=[Membership(user_id=1, group_id=1)],
    )

    patches = group_desired.diff(group_current)

    assert patches and patches[0]["path"] == "/memberships"
