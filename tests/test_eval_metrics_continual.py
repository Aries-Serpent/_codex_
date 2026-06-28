"""
Test Eval Metrics Continual

Test module for eval metrics continual.
"""

from __future__ import annotations

import pytest

from codex_ml.metrics.metrics_deprecated import (
    average_forgetting,
    backward_transfer,
    forward_transfer,
)


def test_forward_transfer_positive() -> None:
    assert forward_transfer([0.5, 0.6], [0.6, 0.8]) == pytest.approx(0.15)


def test_backward_transfer_negative() -> None:
    assert backward_transfer([0.7, 0.65], [0.65, 0.6]) == pytest.approx(-0.05)


def test_average_forgetting_curve() -> None:
    history = [
        [0.8, 0.7],
        [0.78, 0.69],
        [0.72, 0.66],
    ]
    score = average_forgetting(history)
    assert score == pytest.approx((0.8 - 0.72 + 0.7 - 0.66) / 2), "score is not valid"


def test_average_forgetting_requires_history() -> None:
    with pytest.raises(ValueError):
        average_forgetting([])


def test_average_forgetting_uniform_lengths() -> None:
    with pytest.raises(ValueError):
        average_forgetting([[0.1], [0.1, 0.2]])
