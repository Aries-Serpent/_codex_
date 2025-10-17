"""Tests for retry logic with exponential backoff."""

from __future__ import annotations

import time
from unittest.mock import Mock

import pytest

from codex.archive.retry import RetryConfig, calculate_backoff, retry_with_backoff


class TestRetryConfig:
    def test_default_config(self) -> None:
        config = RetryConfig()
        assert config.max_attempts == 3
        assert config.initial_delay == 1.0
        assert config.max_delay == 32.0
        assert config.backoff_factor == 2.0
        assert config.jitter is True

    def test_custom_config(self) -> None:
        config = RetryConfig(
            max_attempts=5,
            initial_delay=0.5,
            max_delay=16.0,
            backoff_factor=3.0,
            jitter=False,
        )
        assert config.max_attempts == 5
        assert config.initial_delay == 0.5
        assert config.max_delay == 16.0
        assert config.backoff_factor == 3.0
        assert config.jitter is False


class TestCalculateBackoff:
    def test_exponential_growth(self) -> None:
        delay_0 = calculate_backoff(0, initial_delay=1.0, jitter=False)
        delay_1 = calculate_backoff(1, initial_delay=1.0, jitter=False)
        delay_2 = calculate_backoff(2, initial_delay=1.0, jitter=False)
        assert delay_0 == 1.0
        assert delay_1 == 2.0
        assert delay_2 == 4.0

    def test_max_delay_cap(self) -> None:
        delay = calculate_backoff(
            10,
            initial_delay=1.0,
            max_delay=32.0,
            backoff_factor=2.0,
            jitter=False,
        )
        assert delay == 32.0

    def test_deterministic_seed(self) -> None:
        delay_1 = calculate_backoff(5, jitter=True, seed=42)
        delay_2 = calculate_backoff(5, jitter=True, seed=42)
        assert delay_1 == delay_2

    def test_jitter_adds_randomness(self) -> None:
        delays = [calculate_backoff(5, jitter=True, seed=i) for i in range(10)]
        assert len(set(delays)) > 1


class TestRetryDecorator:
    def test_success_first_attempt(self) -> None:
        mock_func = Mock(return_value="success")
        config = RetryConfig(max_attempts=3, jitter=False)

        @retry_with_backoff(config)
        def test_func() -> str:
            return mock_func()

        result = test_func()
        assert result == "success"
        assert mock_func.call_count == 1

    def test_retry_on_transient_error(self) -> None:
        mock_func = Mock(side_effect=[ConnectionError(), ConnectionError(), "success"])
        config = RetryConfig(max_attempts=3, initial_delay=0.01, jitter=False)

        @retry_with_backoff(config, transient_errors=(ConnectionError,))
        def test_func() -> str:
            return mock_func()

        result = test_func()
        assert result == "success"
        assert mock_func.call_count == 3

    def test_max_attempts_exceeded(self) -> None:
        mock_func = Mock(side_effect=ConnectionError("timeout"))
        config = RetryConfig(max_attempts=2, initial_delay=0.01, jitter=False)

        @retry_with_backoff(config, transient_errors=(ConnectionError,))
        def test_func() -> str:
            return mock_func()

        with pytest.raises(ConnectionError):
            test_func()
        assert mock_func.call_count == 2

    def test_non_transient_error_no_retry(self) -> None:
        mock_func = Mock(side_effect=ValueError("invalid"))
        config = RetryConfig(max_attempts=3, initial_delay=0.01)

        @retry_with_backoff(config, transient_errors=(ConnectionError,))
        def test_func() -> str:
            return mock_func()

        with pytest.raises(ValueError):
            test_func()
        assert mock_func.call_count == 1


class TestRetryTiming:
    def test_backoff_delays_execution(self) -> None:
        call_times: list[float] = []

        def failing_func() -> str:
            call_times.append(time.time())
            if len(call_times) < 2:
                raise ConnectionError()
            return "success"

        config = RetryConfig(
            max_attempts=3,
            initial_delay=0.1,
            backoff_factor=2.0,
            jitter=False,
        )

        @retry_with_backoff(config, transient_errors=(ConnectionError,))
        def test_func() -> str:
            return failing_func()

        start = time.time()
        test_func()
        elapsed = time.time() - start
        assert elapsed >= 0.08
