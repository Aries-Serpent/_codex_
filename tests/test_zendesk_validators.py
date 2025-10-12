import pytest
from pydantic import ValidationError

from codex.zendesk.plan.validators import validate_plan


def test_validate_minimal_plan() -> None:
    plan = validate_plan(
        {
            "resource": "fields",
            "operations": [
                {"op": "create", "payload": {"title": "New Field"}},
            ],
        }
    )
    assert plan.resource == "fields"
    assert plan.operations[0].op == "create"


def test_reject_scalar_plan() -> None:
    with pytest.raises(ValidationError):
        validate_plan({"resource": "views", "operations": "oops"})  # type: ignore[arg-type]
