from __future__ import annotations

from codex_ml.config.settings import EvalRow


def test_eval_row_validates_required_fields() -> None:
    row = EvalRow(step=1, loss=0.1)
    assert row.step == 1
    assert row.loss == 0.1
    assert row.accuracy is None
