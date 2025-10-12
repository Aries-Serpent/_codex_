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
