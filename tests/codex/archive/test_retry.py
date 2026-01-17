"""
Tests for codex.archive.retry module.

This module contains tests for retry helpers with exponential backoff.
"""

import pytest
import random
from unittest.mock import patch, MagicMock


class TestRetryConfig:
    """Tests for RetryConfig dataclass."""

    def test_default_values(self):
        """Test RetryConfig default values."""
        from codex.archive.retry import RetryConfig
        
        config = RetryConfig()
        
        assert config.enabled is True
        assert config.max_attempts == 5
        assert config.initial_delay == 1.0
        assert config.max_delay == 32.0
        assert config.multiplier == 2.0
        assert config.jitter == 0.1
        assert config.seed is None
        assert ConnectionError in config.transient_exceptions
        assert TimeoutError in config.transient_exceptions
        assert OSError in config.transient_exceptions

    def test_custom_values(self):
        """Test RetryConfig with custom values."""
        from codex.archive.retry import RetryConfig
        
        config = RetryConfig(
            enabled=False,
            max_attempts=3,
            initial_delay=0.5,
            max_delay=10.0,
            multiplier=3.0,
            jitter=0.2,
            seed=42
        )
        
        assert config.enabled is False
        assert config.max_attempts == 3
        assert config.seed == 42

    def test_create_rng(self):
        """Test create_rng method."""
        from codex.archive.retry import RetryConfig
        
        config = RetryConfig(seed=123)
        rng = config.create_rng()
        
        assert isinstance(rng, random.Random)
        # Same seed produces deterministic results
        rng2 = config.create_rng()
        # Both start from same seed, so first value should be same
        val1 = rng.random()
        val2 = rng2.random()
        assert val1 == val2  # Same seed produces same sequence

    def test_frozen(self):
        """Test RetryConfig is frozen (immutable)."""
        from codex.archive.retry import RetryConfig
        
        config = RetryConfig()
        
        with pytest.raises(AttributeError):
            config.enabled = False


class TestCalculateBackoff:
    """Tests for calculate_backoff function."""

    def test_first_attempt(self):
        """Test backoff for first attempt."""
        from codex.archive.retry import RetryConfig, calculate_backoff
        
        config = RetryConfig(initial_delay=1.0, multiplier=2.0, jitter=0)
        
        delay = calculate_backoff(1, config=config)
        
        assert delay == 1.0  # First attempt uses initial delay

    def test_exponential_growth(self):
        """Test exponential growth of backoff."""
        from codex.archive.retry import RetryConfig, calculate_backoff
        
        config = RetryConfig(initial_delay=1.0, multiplier=2.0, jitter=0, max_delay=100.0)
        
        assert calculate_backoff(1, config=config) == 1.0
        assert calculate_backoff(2, config=config) == 2.0
        assert calculate_backoff(3, config=config) == 4.0
        assert calculate_backoff(4, config=config) == 8.0

    def test_max_delay_cap(self):
        """Test max delay capping."""
        from codex.archive.retry import RetryConfig, calculate_backoff
        
        config = RetryConfig(initial_delay=1.0, multiplier=2.0, jitter=0, max_delay=5.0)
        
        # Attempt 4 would be 8.0, but capped at 5.0
        delay = calculate_backoff(4, config=config)
        assert delay == 5.0

    def test_jitter_applied(self):
        """Test jitter is applied to delay."""
        from codex.archive.retry import RetryConfig, calculate_backoff
        
        config = RetryConfig(initial_delay=10.0, jitter=0.1, seed=42)
        rng = config.create_rng()
        
        delay = calculate_backoff(1, config=config, rng=rng)
        
        # With 10% jitter on 10.0, delay should be between 9.0 and 11.0
        assert 9.0 <= delay <= 11.0

    def test_zero_jitter(self):
        """Test with zero jitter."""
        from codex.archive.retry import RetryConfig, calculate_backoff
        
        config = RetryConfig(initial_delay=5.0, jitter=0)
        
        delay = calculate_backoff(1, config=config)
        
        assert delay == 5.0  # Exact value with no jitter


class TestRetryWithBackoff:
    """Tests for retry_with_backoff decorator."""

    def test_decorator_success(self):
        """Test decorator with successful function."""
        from codex.archive.retry import RetryConfig, retry_with_backoff
        
        config = RetryConfig()
        
        @retry_with_backoff(config)
        def successful_func():
            return "success"
        
        result = successful_func()
        assert result == "success"

    def test_decorator_disabled(self):
        """Test decorator when disabled."""
        from codex.archive.retry import RetryConfig, retry_with_backoff
        
        config = RetryConfig(enabled=False)
        call_count = 0
        
        @retry_with_backoff(config)
        def failing_func():
            nonlocal call_count
            call_count += 1
            raise ConnectionError("Failed")
        
        with pytest.raises(ConnectionError):
            failing_func()
        
        # Should not retry when disabled
        assert call_count == 1

    def test_decorator_default_config(self):
        """Test decorator with default config."""
        from codex.archive.retry import retry_with_backoff
        
        @retry_with_backoff()
        def successful_func():
            return "ok"
        
        result = successful_func()
        assert result == "ok"


class TestModuleLevel:
    """Tests for module-level elements."""

    def test_logger_exists(self):
        """Test logger is configured."""
        from codex.archive.retry import logger
        
        assert logger is not None
        assert logger.name == "codex.archive.retry"
