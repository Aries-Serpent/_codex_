import pytest
from pydantic import ValidationError

from codex_ml.config.settings import EvalRow


def test_eval_row_validates_required_fields() -> None:
    row = EvalRow(step=1, loss=0.1)
    assert row.step == 1
    assert row.loss == pytest.approx(0.1)
    assert row.accuracy is None


def test_eval_row_requires_positive_step() -> None:
    with pytest.raises(ValidationError):
        EvalRow(step=0)
