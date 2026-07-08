"""
Test Reward Metrics

Comprehensive unit tests for the reward metrics module.
Tests reward_mean and reward_success_rate functions.
"""

from __future__ import annotations

from codex_ml.metrics.reward import _coerce_reward, reward_mean, reward_success_rate


class TestCoerceReward:
    """Tests for _coerce_reward helper function."""

    def test_float_passthrough(self) -> None:
        assert _coerce_reward(1.5) == 1.5, "Condition must be true"

    def test_int_conversion(self) -> None:
        assert _coerce_reward(5) == 5.0, "Condition must be true"

    def test_dict_with_reward_key(self) -> None:
        data = {"reward": 2.5, "other": "value"}
        assert _coerce_reward(data) == 2.5, "Data must not be empty"

    def test_nested_dict_reward(self) -> None:
        # Should extract top-level reward key
        data = {"reward": 3.0}
        assert _coerce_reward(data) == 3.0, "Data must not be empty"

    def test_string_number_conversion(self) -> None:
        assert _coerce_reward("2.5") == 2.5, "Condition must be true"

    def test_invalid_value_returns_zero(self) -> None:
        # Non-convertible values should return 0.0
        assert _coerce_reward("not_a_number") == 0.0, "Condition must be true"
        assert _coerce_reward(None) == 0.0, "Condition must be true"

    def test_dict_without_reward_key(self) -> None:
        # Dict without "reward" key should try to convert whole dict
        data = {"score": 1.0}
        # This should fail conversion and return 0.0
        assert _coerce_reward(data) == 0.0, "Data must not be empty"


class TestRewardMean:
    """Tests for reward_mean function."""

    def test_empty_predictions(self) -> None:
        assert reward_mean([]) == 0.0, "Condition must be true"

    def test_single_value(self) -> None:
        assert reward_mean([5.0]) == 5.0, "Condition must be true"

    def test_multiple_values(self) -> None:
        result = reward_mean([1.0, 2.0, 3.0, 4.0])
        assert result == 2.5, "Result must not be empty"

    def test_with_dict_payloads(self) -> None:
        predictions = [
            {"reward": 1.0},
            {"reward": 2.0},
            {"reward": 3.0},
        ]
        assert reward_mean(predictions) == 2.0, "Condition must be true"

    def test_mixed_types(self) -> None:
        predictions = [1.0, {"reward": 2.0}, 3]
        assert reward_mean(predictions) == 2.0, "Condition must be true"

    def test_with_zero_rewards(self) -> None:
        predictions = [0.0, 0.0, 0.0]
        assert reward_mean(predictions) == 0.0, "Condition must be true"

    def test_negative_rewards(self) -> None:
        predictions = [-1.0, -2.0, 3.0]
        assert reward_mean(predictions) == 0.0, "Condition must be true"

    def test_ignores_targets_parameter(self) -> None:
        # targets parameter should be ignored
        result = reward_mean([1.0, 2.0, 3.0], targets=[10.0, 20.0, 30.0])
        assert result == 2.0, "Result must not be empty"


class TestRewardSuccessRate:
    """Tests for reward_success_rate function."""

    def test_empty_predictions(self) -> None:
        assert reward_success_rate([]) == 0.0, "Condition must be true"

    def test_all_above_threshold(self) -> None:
        predictions = [1.0, 2.0, 3.0]
        result = reward_success_rate(predictions, threshold=0.0)
        assert result == 1.0, "Result must not be empty"

    def test_all_below_threshold(self) -> None:
        predictions = [1.0, 2.0, 3.0]
        result = reward_success_rate(predictions, threshold=5.0)
        assert result == 0.0, "Result must not be empty"

    def test_partial_success(self) -> None:
        predictions = [1.0, 2.0, 3.0, 4.0]
        result = reward_success_rate(predictions, threshold=2.5)
        # 3.0 and 4.0 are >= 2.5
        assert result == 0.5, "Result must not be empty"

    def test_default_threshold_zero(self) -> None:
        predictions = [-1.0, 0.0, 1.0]
        result = reward_success_rate(predictions)
        # 0.0 and 1.0 are >= 0.0
        assert abs(result - 2 / 3) < 1e-6, "Result must not be empty"

    def test_with_dict_payloads(self) -> None:
        predictions = [
            {"reward": 1.0},
            {"reward": 5.0},
            {"reward": 10.0},
        ]
        result = reward_success_rate(predictions, threshold=5.0)
        # 5.0 and 10.0 are >= 5.0
        assert abs(result - 2 / 3) < 1e-6, "Result must not be empty"

    def test_exact_threshold_match(self) -> None:
        predictions = [1.0, 2.0, 3.0]
        result = reward_success_rate(predictions, threshold=2.0)
        # 2.0 and 3.0 are >= 2.0
        assert abs(result - 2 / 3) < 1e-6, "Result must not be empty"

    def test_negative_threshold(self) -> None:
        predictions = [-2.0, -1.0, 0.0, 1.0]
        result = reward_success_rate(predictions, threshold=-1.0)
        # -1.0, 0.0, 1.0 are >= -1.0
        assert result == 0.75, "Result must not be empty"

    def test_ignores_targets_parameter(self) -> None:
        result = reward_success_rate([1.0, 2.0], targets=[10.0, 20.0], threshold=1.0)
        # Both predictions >= 1.0
        assert result == 1.0, "Result must not be empty"
