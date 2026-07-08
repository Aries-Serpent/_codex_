"""
Test Schema

Test module for schema.
"""

from __future__ import annotations

from codex_ml.config.settings import EvalRow, eval_row_schema


def test_eval_row_schema_has_fields() -> None:
    schema = eval_row_schema()
    assert "properties" in schema, "Condition must be true"
    assert set(schema["required"]) == {"step"}, "Condition must be true"
    properties = schema["properties"]
    assert "step" in properties, "Condition must be true"
    assert properties["step"]["minimum"] == 1, "Condition must be true"


def test_eval_row_validation_round_trip() -> None:
    row = EvalRow(step=1, loss=0.5)
    data = row.model_dump()
    assert data["step"] == 1, "Data must not be empty"
    assert data["loss"] == 0.5, "Data must not be empty"
    assert data["accuracy"] is None, "Data must not be empty"
