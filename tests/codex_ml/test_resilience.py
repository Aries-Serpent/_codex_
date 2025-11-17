"""Tests for resilience patterns"""

import time
from unittest.mock import Mock

import pytest

from src.codex_ml.serving.resilience import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitState,
    FallbackHandler,
    retry_with_backoff,
)


class TestCircuitBreaker:
    """Test circuit breaker pattern"""

    def test_initialization(self):
        """Test circuit breaker initialization"""
        config = CircuitBreakerConfig(failure_threshold=3, timeout=10.0)
        cb = CircuitBreaker(config)

        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0
        assert cb.config.failure_threshold == 3

    def test_successful_calls(self):
        """Test successful calls keep circuit closed"""
        cb = CircuitBreaker()

        def success_func():
            return "success"

        for _ in range(10):
            result = cb.call(success_func)
            assert result == "success"

        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0

    def test_circuit_opens_on_failures(self):
        """Test circuit opens after threshold failures"""
        config = CircuitBreakerConfig(failure_threshold=3)
        cb = CircuitBreaker(config)

        def fail_func():
            raise ValueError("Failure")

        # Trigger failures up to threshold
        for i in range(3):
            with pytest.raises(ValueError):
                cb.call(fail_func)

        # Circuit should be open now
        assert cb.state == CircuitState.OPEN
        assert cb.failure_count == 3

    def test_circuit_rejects_when_open(self):
        """Test circuit rejects requests when open"""
        config = CircuitBreakerConfig(failure_threshold=2, timeout=10.0)
        cb = CircuitBreaker(config)

        def fail_func():
            raise ValueError("Failure")

        # Open the circuit
        for _ in range(2):
            with pytest.raises(ValueError):
                cb.call(fail_func)

        assert cb.state == CircuitState.OPEN

        # Subsequent calls should be rejected
        def success_func():
            return "success"

        with pytest.raises(Exception, match="Circuit breaker is open"):
            cb.call(success_func)

    def test_circuit_enters_half_open(self):
        """Test circuit enters half-open after timeout"""
        config = CircuitBreakerConfig(failure_threshold=2, timeout=0.1)  # 100ms timeout
        cb = CircuitBreaker(config)

        def fail_func():
            raise ValueError("Failure")

        # Open the circuit
        for _ in range(2):
            with pytest.raises(ValueError):
                cb.call(fail_func)

        assert cb.state == CircuitState.OPEN

        # Wait for timeout
        time.sleep(0.15)

        # Next call should enter half-open
        def success_func():
            return "success"

        result = cb.call(success_func)
        assert result == "success"
        assert cb.state == CircuitState.HALF_OPEN

    def test_circuit_closes_from_half_open(self):
        """Test circuit closes after successful calls in half-open"""
        config = CircuitBreakerConfig(
            failure_threshold=2,
            success_threshold=2,
            timeout=0.1,
        )
        cb = CircuitBreaker(config)

        def fail_func():
            raise ValueError("Failure")

        # Open the circuit
        for _ in range(2):
            with pytest.raises(ValueError):
                cb.call(fail_func)

        # Wait and enter half-open
        time.sleep(0.15)

        # Successful calls should close circuit
        def success_func():
            return "success"

        cb.call(success_func)  # First success
        assert cb.state == CircuitState.HALF_OPEN

        cb.call(success_func)  # Second success
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0

    def test_circuit_reopens_on_half_open_failure(self):
        """Test circuit reopens if half-open call fails"""
        config = CircuitBreakerConfig(failure_threshold=2, timeout=0.1)
        cb = CircuitBreaker(config)

        def fail_func():
            raise ValueError("Failure")

        # Open the circuit
        for _ in range(2):
            with pytest.raises(ValueError):
                cb.call(fail_func)

        # Wait and enter half-open
        time.sleep(0.15)

        # Failure in half-open should reopen circuit
        with pytest.raises(ValueError):
            cb.call(fail_func)

        assert cb.state == CircuitState.OPEN

    def test_manual_reset(self):
        """Test manual circuit breaker reset"""
        config = CircuitBreakerConfig(failure_threshold=2)
        cb = CircuitBreaker(config)

        def fail_func():
            raise ValueError("Failure")

        # Open the circuit
        for _ in range(2):
            with pytest.raises(ValueError):
                cb.call(fail_func)

        assert cb.state == CircuitState.OPEN

        # Manual reset
        cb.reset()

        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0

    def test_get_state(self):
        """Test get_state method"""
        cb = CircuitBreaker()

        state = cb.get_state()
        assert "state" in state
        assert "failure_count" in state
        assert "success_count" in state
        assert state["state"] == "closed"


class TestRetryWithBackoff:
    """Test retry with exponential backoff"""

    def test_successful_first_attempt(self):
        """Test function succeeds on first attempt"""
        mock_func = Mock(return_value="success")

        result = retry_with_backoff(mock_func, max_retries=3)

        assert result == "success"
        assert mock_func.call_count == 1

    def test_retries_on_failure(self):
        """Test function retries on failure"""
        mock_func = Mock(side_effect=[ValueError("fail"), ValueError("fail"), "success"])

        result = retry_with_backoff(
            mock_func,
            max_retries=3,
            initial_delay=0.01,  # Short delay for testing
        )

        assert result == "success"
        assert mock_func.call_count == 3

    def test_exhausts_retries(self):
        """Test all retries exhausted"""
        mock_func = Mock(side_effect=ValueError("fail"))

        with pytest.raises(ValueError, match="fail"):
            retry_with_backoff(
                mock_func,
                max_retries=2,
                initial_delay=0.01,
            )

        assert mock_func.call_count == 3  # Initial + 2 retries

    def test_exponential_backoff(self):
        """Test exponential backoff delays"""
        call_times = []

        def failing_func():
            call_times.append(time.time())
            raise ValueError("fail")

        with pytest.raises(ValueError):
            retry_with_backoff(
                failing_func,
                max_retries=2,
                initial_delay=0.05,
                backoff_factor=2.0,
            )

        # Check delays are increasing
        assert len(call_times) == 3
        delay1 = call_times[1] - call_times[0]
        delay2 = call_times[2] - call_times[1]

        # Second delay should be roughly 2x first delay
        assert delay2 > delay1
        assert 0.04 <= delay1 <= 0.08  # ~50ms
        assert 0.08 <= delay2 <= 0.15  # ~100ms

    def test_max_delay_cap(self):
        """Test maximum delay cap"""
        call_times = []

        def failing_func():
            call_times.append(time.time())
            raise ValueError("fail")

        with pytest.raises(ValueError):
            retry_with_backoff(
                failing_func,
                max_retries=5,
                initial_delay=0.01,
                max_delay=0.05,  # Cap at 50ms
                backoff_factor=10.0,  # Aggressive factor
            )

        # All delays should be capped at max_delay
        for i in range(1, len(call_times)):
            delay = call_times[i] - call_times[i - 1]
            assert delay <= 0.06  # Should be near max_delay


class TestFallbackHandler:
    """Test fallback handler"""

    def test_successful_primary_call(self):
        """Test primary function succeeds"""
        fallback_func = Mock(return_value="fallback")
        handler = FallbackHandler(fallback_func=fallback_func, use_cache=False)

        def primary_func():
            return "primary"

        result = handler.call_with_fallback(primary_func)

        assert result == "primary"
        assert not fallback_func.called

    def test_fallback_on_failure(self):
        """Test fallback function called on primary failure"""
        fallback_func = Mock(return_value="fallback")
        handler = FallbackHandler(fallback_func=fallback_func, use_cache=False)

        def primary_func():
            raise ValueError("Primary failed")

        result = handler.call_with_fallback(primary_func)

        assert result == "fallback"
        assert fallback_func.called

    def test_cache_fallback(self):
        """Test cache used as fallback"""
        mock_cache = Mock()
        mock_cache.get = Mock(return_value="cached_result")

        handler = FallbackHandler(use_cache=True, cache=mock_cache)

        def primary_func():
            raise ValueError("Primary failed")

        result = handler.call_with_fallback(primary_func, fallback_key="test_key")

        assert result == "cached_result"
        mock_cache.get.assert_called_once_with("test_key")

    def test_no_fallback_available(self):
        """Test re-raises exception when no fallback available"""
        handler = FallbackHandler(fallback_func=None, use_cache=False)

        def primary_func():
            raise ValueError("Primary failed")

        with pytest.raises(ValueError, match="Primary failed"):
            handler.call_with_fallback(primary_func)

    def test_cache_then_function_fallback(self):
        """Test fallback priority: cache first, then function"""
        mock_cache = Mock()
        mock_cache.get = Mock(return_value=None)  # Cache miss
        fallback_func = Mock(return_value="fallback_func_result")

        handler = FallbackHandler(
            fallback_func=fallback_func,
            use_cache=True,
            cache=mock_cache,
        )

        def primary_func():
            raise ValueError("Primary failed")

        result = handler.call_with_fallback(primary_func, fallback_key="test_key")

        assert result == "fallback_func_result"
        mock_cache.get.assert_called_once()
        fallback_func.assert_called_once()
