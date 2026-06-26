"""
Test Zendesk Validators

Test module for zendesk validators.
"""

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
    assert plan.resource == "fields", "resource is not valid"
    first_operation = plan.operations[0]
    assert first_operation.op == "add", "op is not valid"
    assert first_operation.path == "/fields/New%20Field", "path is not valid"


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
    assert patch_operation.op == "patch", "op is not valid"
    assert patch_operation.patches[0].path == "/position", "path is not valid"


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
    assert create.op == "add", "op is not valid"
    assert create.value == {"title": "Create Macro"}, "Value must be initialized"
    assert update.op == "patch", "op is not valid"
    assert update.patches[0].path == "/title", "path is not valid"
    assert delete.op == "remove", "op is not valid"
