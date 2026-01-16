"""
Test Reward Metrics

Test module for reward metrics.
"""

import pytest

from codex_ml.metrics.reward import reward_mean, reward_success_rate


def test_reward_mean_handles_mapping_and_numbers() -> None:
    data = [1, 2, {"reward": 3}]
    assert reward_mean(data, []) == 2.0


def test_reward_success_rate_threshold() -> None:
    data = [{"reward": -0.1}, {"reward": 0.5}, 1.0]
    assert reward_success_rate(data, [], threshold=0.0) == pytest.approx(2 / 3)
    assert reward_success_rate(data, [], threshold=0.8) == pytest.approx(1 / 3)
