from __future__ import annotations

from codex_ml.config.settings import EvalRow, eval_row_schema


def test_eval_row_schema_has_fields() -> None:
    schema = eval_row_schema()
    assert "properties" in schema
    assert "step" in schema["properties"]
    row = EvalRow(step=1, loss=0.5)
    assert row.model_dump()["step"] == 1
