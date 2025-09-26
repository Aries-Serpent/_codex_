import pytest

pytest.importorskip("torch")  # noqa: F401

from codex_ml.metrics.registry import get_metric


def test_token_accuracy_alias() -> None:
    metric = get_metric("token_accuracy")
    value = metric([1, 2, 3, 4], [1, 0, 3, 9])
    assert 0.4 <= value <= 0.6
