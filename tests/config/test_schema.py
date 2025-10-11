from __future__ import annotations

from codex_ml.config.settings import EvalRow, eval_row_schema


def test_eval_row_schema_has_fields() -> None:
    schema = eval_row_schema()
    assert "properties" in schema
    assert set(schema["required"]) == {"step"}
    properties = schema["properties"]
    assert "step" in properties
    assert properties["step"]["minimum"] == 1


def test_eval_row_validation_round_trip() -> None:
    row = EvalRow(step=1, loss=0.5)
    data = row.model_dump()
    assert data["step"] == 1
    assert data["loss"] == 0.5
    assert data["accuracy"] is None
