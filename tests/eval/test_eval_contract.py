"""
Test Eval Contract

Test module for eval contract.
"""

from __future__ import annotations

from codex_ml.config.settings import EvalRow


def test_eval_row_validates_required_fields() -> None:
    row = EvalRow(step=1, loss=0.1)
    assert row.step == 1, "step is not valid"
    assert row.loss == 0.1, "loss is not valid"
    assert row.accuracy is None, "accuracy is not valid"
