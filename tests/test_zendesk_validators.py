import pytest
from pydantic import ValidationError

from codex.zendesk.plan.validators import validate_plan


def test_validate_minimal_plan() -> None:
    plan = validate_plan(
        {
            "resource": "fields",
            "operations": [
                {
                    "op": "add",
                    "path": "/fields/New%20Field",
                    "value": {"title": "New Field"},
                },
            ],
        }
    )
    assert plan.resource == "fields"
    first_operation = plan.operations[0]
    assert first_operation.op == "add"
    assert first_operation.path == "/fields/New%20Field"


def test_reject_scalar_plan() -> None:
    with pytest.raises(ValidationError):
        validate_plan({"resource": "views", "operations": "oops"})  # type: ignore[arg-type]


def test_validate_patch_operation() -> None:
    plan = validate_plan(
        {
            "resource": "triggers",
            "operations": [
                {
                    "op": "patch",
                    "name": "Notify Agent",
                    "patches": [
                        {"op": "replace", "path": "/position", "value": 1},
                    ],
                }
            ],
        }
    )
    patch_operation = plan.operations[0]
    assert patch_operation.op == "patch"
    assert patch_operation.patches[0].path == "/position"


def test_validate_action_style_operations() -> None:
    plan = validate_plan(
        {
            "resource": "macros",
            "operations": [
                {
                    "action": "create",
                    "resource": "macros",
                    "name": "Create Macro",
                    "data": {"title": "Create Macro"},
                },
                {
                    "action": "update",
                    "resource": "macros",
                    "name": "Update Macro",
                    "changes": [
                        {"op": "replace", "path": "/title", "value": "Updated"},
                    ],
                },
                {
                    "action": "delete",
                    "resource": "macros",
                    "name": "Delete Macro",
                },
            ],
        }
    )

    create, update, delete = plan.operations
    assert create.op == "add"
    assert create.value == {"title": "Create Macro"}
    assert update.op == "patch"
    assert update.patches[0].path == "/title"
    assert delete.op == "remove"
