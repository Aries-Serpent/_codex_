"""Comprehensive tests for error handling and recovery capability.

Tests cover:
- Exception hierarchy
- Retry logic with exponential backoff
- Circuit breakers
- Dead-letter queues
- Self-remediation scripts
"""

from __future__ import annotations

import time
from collections import deque
from collections.abc import Callable
from enum import Enum
from typing import Any

import pytest

pytest.importorskip("hypothesis")


pytest.importorskip("hypothesis", reason="hypothesis required for property tests")

from hypothesis import given, settings
from hypothesis import strategies as st

# --- Exception Hierarchy Tests ---


class CodexError(Exception):
    """Base exception for Codex errors."""

    def __init__(self, message: str, code: str | None = None):
        super().__init__(message)
        self.code = code
        self.timestamp = time.time()


class ConfigurationError(CodexError):
    """Configuration related errors."""


class ValidationError(CodexError):
    """Validation errors."""

    def __init__(self, message: str, field: str | None = None, value: Any = None):
        super().__init__(message, code="VALIDATION_ERROR")
        self.field = field
        self.value = value


class NetworkError(CodexError):
    """Network related errors."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message, code="NETWORK_ERROR")
        self.status_code = status_code


class ResourceNotFoundError(CodexError):
    """Resource not found errors."""

    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(f"{resource_type} not found: {resource_id}", code="NOT_FOUND")
        self.resource_type = resource_type
        self.resource_id = resource_id


class TimeoutError(CodexError):
    """Timeout errors."""

    def __init__(self, operation: str, timeout_seconds: float):
        super().__init__(
            f"Operation {operation} timed out after {timeout_seconds}s", code="TIMEOUT"
        )
        self.operation = operation
        self.timeout_seconds = timeout_seconds


class TestExceptionHierarchy:
    """Tests for exception hierarchy."""

    def test_base_error(self):
        """Base error has code and timestamp."""
        err = CodexError("Test error", code="TEST_001")
        assert err.code == "TEST_001", "code is not valid"
        assert err.timestamp > 0, "timestamp must be greater than zero"

    def test_configuration_error(self):
        """Configuration error inherits from base."""
        err = ConfigurationError("Invalid config")
        assert isinstance(err, CodexError)

    def test_validation_error(self):
        """Validation error has field info."""
        err = ValidationError("Invalid value", field="email", value="bad@")
        assert err.field == "email", "field is not valid"
        assert err.value == "bad@", "Value must be initialized"

    def test_network_error(self):
        """Network error has status code."""
        err = NetworkError("Connection failed", status_code=503)
        assert err.status_code == 503, "status_code is not valid"

    def test_resource_not_found(self):
        """Resource not found error."""
        err = ResourceNotFoundError("User", "123")
        assert err.resource_type == "User", "resource_type is not valid"
        assert err.resource_id == "123", "resource_id is not valid"

    def test_timeout_error(self):
        """Timeout error."""
        err = TimeoutError("fetch_data", 30.0)
        assert err.operation == "fetch_data", "Data must not be empty"
        assert err.timeout_seconds == 30.0, "timeout_seconds is not valid"


# --- Retry Logic Tests ---


class RetryConfig:
    """Retry configuration."""

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for attempt using exponential backoff."""
        delay = self.base_delay * (self.exponential_base**attempt)
        return min(delay, self.max_delay)


class Retrier:
    """Retry operations with backoff."""

    def __init__(self, config: RetryConfig):
        self.config = config
        self.attempts: list[dict[str, Any]] = []

    def execute(self, fn: Callable[[], Any], retryable_exceptions: tuple = (Exception,)) -> Any:
        """Execute function with retry."""
        last_error = None
        for attempt in range(self.config.max_retries + 1):
            try:
                result = fn()
                self.attempts.append({"attempt": attempt, "success": True})
                return result
            except retryable_exceptions as e:
                last_error = e
                self.attempts.append({"attempt": attempt, "success": False, "error": str(e)})
                if attempt < self.config.max_retries:
                    self.config.get_delay(attempt)
                    # In tests, we don't actually sleep
        if last_error is None:
            raise RuntimeError("Retry failed: no exception was captured")
        raise last_error


class TestRetryLogic:
    """Tests for retry logic."""

    def test_success_no_retry(self):
        """Successful operation doesn't retry."""
        config = RetryConfig(max_retries=3)
        retrier = Retrier(config)
        result = retrier.execute(lambda: "success")
        assert result == "success", "Result must not be empty"
        assert len(retrier.attempts) == 1, "Collection must not be empty"

    def test_retry_on_failure(self):
        """Retry on transient failure."""
        config = RetryConfig(max_retries=3)
        retrier = Retrier(config)
        counter = {"count": 0}

        def flaky():
            counter["count"] += 1
            if counter["count"] < 3:
                raise ValueError("Transient error")
            return "success"

        result = retrier.execute(flaky)
        assert result == "success", "Result must not be empty"
        assert len(retrier.attempts) == 3, "Collection must not be empty"

    def test_max_retries_exceeded(self):
        """Raise after max retries."""
        config = RetryConfig(max_retries=2)
        retrier = Retrier(config)

        def always_fail():
            raise ValueError("Always fails")

        with pytest.raises(ValueError):
            retrier.execute(always_fail)
        assert len(retrier.attempts) == 3, "Collection must not be empty"

    def test_exponential_backoff(self):
        """Exponential backoff calculation."""
        config = RetryConfig(base_delay=1.0, exponential_base=2.0, max_delay=60.0)
        assert config.get_delay(0) == 1.0, "Condition must be true"
        assert config.get_delay(1) == 2.0, "Condition must be true"
        assert config.get_delay(2) == 4.0, "Condition must be true"
        assert config.get_delay(3) == 8.0, "Condition must be true"

    def test_max_delay_cap(self):
        """Delay should be capped at max."""
        config = RetryConfig(base_delay=1.0, max_delay=10.0)
        assert config.get_delay(10) == 10.0, "Condition must be true"

    @given(st.integers(min_value=0, max_value=10))
    @settings(max_examples=20)
    def test_delay_non_negative(self, attempt: int):
        """Property: delay is always non-negative."""
        config = RetryConfig()
        assert config.get_delay(attempt) >= 0, "Value must be greater than zero"


# --- Circuit Breaker Tests ---


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Circuit breaker implementation."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        success_threshold: int = 2,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: float | None = None

    def record_success(self) -> None:
        """Record successful call."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self._close()
        else:
            self.failure_count = 0

    def record_failure(self) -> None:
        """Record failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.state == CircuitState.HALF_OPEN or self.failure_count >= self.failure_threshold:
            self._open()

    def can_execute(self) -> bool:
        """Check if call can proceed."""
        if self.state == CircuitState.CLOSED:
            return True
        if self.state == CircuitState.OPEN:
            if (
                self.last_failure_time
                and time.time() - self.last_failure_time >= self.recovery_timeout
            ):
                self._half_open()
                return True
            return False
        return True  # HALF_OPEN

    def _open(self) -> None:
        """Open the circuit."""
        self.state = CircuitState.OPEN
        self.success_count = 0

    def _half_open(self) -> None:
        """Half-open the circuit."""
        self.state = CircuitState.HALF_OPEN
        self.success_count = 0

    def _close(self) -> None:
        """Close the circuit."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0


class TestCircuitBreaker:
    """Tests for circuit breaker."""

    def test_initially_closed(self):
        """Circuit starts closed."""
        cb = CircuitBreaker()
        assert cb.state == CircuitState.CLOSED, "state is not valid"
        assert cb.can_execute(), "Condition must be true"

    def test_open_after_failures(self):
        """Circuit opens after failure threshold."""
        cb = CircuitBreaker(failure_threshold=3)
        cb.record_failure()
        cb.record_failure()
        assert cb.state == CircuitState.CLOSED, "state is not valid"
        cb.record_failure()
        assert cb.state == CircuitState.OPEN, "state is not valid"
        assert not cb.can_execute(), "Condition must be true"

    def test_success_resets_count(self):
        """Success resets failure count."""
        cb = CircuitBreaker(failure_threshold=3)
        cb.record_failure()
        cb.record_failure()
        cb.record_success()
        assert cb.failure_count == 0, "Count must be greater than zero"

    def test_half_open_after_recovery(self):
        """Circuit half-opens after recovery timeout."""
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.01)
        cb.record_failure()
        assert cb.state == CircuitState.OPEN, "state is not valid"
        time.sleep(0.02)
        assert cb.can_execute(), "Condition must be true"
        assert cb.state == CircuitState.HALF_OPEN, "state is not valid"

    def test_close_after_success_threshold(self):
        """Circuit closes after success threshold in half-open."""
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.01, success_threshold=2)
        cb.record_failure()
        time.sleep(0.02)
        cb.can_execute()  # Transitions to HALF_OPEN
        cb.record_success()
        assert cb.state == CircuitState.HALF_OPEN, "state is not valid"
        cb.record_success()
        assert cb.state == CircuitState.CLOSED, "state is not valid"


# --- Dead Letter Queue Tests ---


class DeadLetterQueue:
    """Dead letter queue for failed messages."""

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.queue: deque[dict[str, Any]] = deque(maxlen=max_size)

    def add(self, message: Any, error: str, metadata: dict[str, Any] | None = None) -> None:
        """Add message to DLQ."""
        entry = {
            "message": message,
            "error": error,
            "metadata": metadata or {},
            "timestamp": time.time(),
            "retry_count": 0,
        }
        self.queue.append(entry)

    def get_all(self) -> list[dict[str, Any]]:
        """Get all messages."""
        return list(self.queue)

    def retry(self, processor: Callable[[Any], bool]) -> int:
        """Retry processing messages. Returns count of successful retries."""
        successful = 0
        remaining = []
        for entry in self.queue:
            try:
                if processor(entry["message"]):
                    successful += 1
                else:
                    entry["retry_count"] += 1
                    remaining.append(entry)
            except Exception as _err:
                entry["retry_count"] += 1
                remaining.append(entry)
        self.queue.clear()
        self.queue.extend(remaining)
        return successful

    def size(self) -> int:
        """Get queue size."""
        return len(self.queue)

    def clear(self) -> None:
        """Clear the queue."""
        self.queue.clear()


class TestDeadLetterQueue:
    """Tests for dead letter queue."""

    def test_add_message(self):
        """Add message to DLQ."""
        dlq = DeadLetterQueue()
        dlq.add("failed message", "Processing error")
        assert dlq.size() == 1, "Condition must be true"

    def test_max_size(self):
        """DLQ respects max size."""
        dlq = DeadLetterQueue(max_size=3)
        for i in range(5):
            dlq.add(f"msg_{i}", "error")
        assert dlq.size() == 3, "Condition must be true"

    def test_retry_success(self):
        """Retry successfully processes messages."""
        dlq = DeadLetterQueue()
        dlq.add("msg1", "error")
        dlq.add("msg2", "error")
        successful = dlq.retry(lambda m: True)
        assert successful == 2, "successful is not valid"
        assert dlq.size() == 0, "Condition must be true"

    def test_retry_partial(self):
        """Partial retry success."""
        dlq = DeadLetterQueue()
        dlq.add("good", "error")
        dlq.add("bad", "error")
        successful = dlq.retry(lambda m: m == "good")
        assert successful == 1, "successful is not valid"
        assert dlq.size() == 1, "Condition must be true"


# --- Self-Remediation Tests ---


class RemediationAction:
    """Remediation action definition."""

    def __init__(self, name: str, handler: Callable[[], bool]):
        self.name = name
        self.handler = handler
        self.last_run: float | None = None
        self.success_count = 0
        self.failure_count = 0

    def execute(self) -> bool:
        """Execute remediation action."""
        self.last_run = time.time()
        try:
            result = self.handler()
            if result:
                self.success_count += 1
            else:
                self.failure_count += 1
            return result
        except Exception as _err:
            self.failure_count += 1
            return False


class RemediationManager:
    """Manage self-remediation actions."""

    def __init__(self):
        self.actions: dict[str, RemediationAction] = {}
        self.error_mapping: dict[str, str] = {}

    def register_action(self, action: RemediationAction) -> None:
        """Register remediation action."""
        self.actions[action.name] = action

    def map_error_to_action(self, error_code: str, action_name: str) -> None:
        """Map error code to remediation action."""
        self.error_mapping[error_code] = action_name

    def remediate(self, error: CodexError) -> bool:
        """Attempt to remediate error."""
        if not error.code or error.code not in self.error_mapping:
            return False
        action_name = self.error_mapping[error.code]
        action = self.actions.get(action_name)
        if not action:
            return False
        return action.execute()


class TestRemediationManager:
    """Tests for remediation manager."""

    def test_register_action(self):
        """Register remediation action."""
        manager = RemediationManager()
        action = RemediationAction("restart", lambda: True)
        manager.register_action(action)
        assert "restart" in manager.actions, "Condition must be true"

    def test_map_error_to_action(self):
        """Map error to action."""
        manager = RemediationManager()
        manager.register_action(RemediationAction("restart", lambda: True))
        manager.map_error_to_action("SERVICE_DOWN", "restart")
        assert manager.error_mapping["SERVICE_DOWN"] == "restart", "Error should be raised or set"

    def test_remediate_success(self):
        """Successful remediation."""
        manager = RemediationManager()
        manager.register_action(RemediationAction("fix", lambda: True))
        manager.map_error_to_action("FIXABLE", "fix")
        error = CodexError("Fixable error", code="FIXABLE")
        result = manager.remediate(error)
        assert result is True, "Result must not be empty"

    def test_remediate_no_mapping(self):
        """No remediation for unmapped error."""
        manager = RemediationManager()
        error = CodexError("Unknown error", code="UNKNOWN")
        result = manager.remediate(error)
        assert result is False, "Result must not be empty"


# --- Fallback Tests ---


class FallbackChain:
    """Chain of fallback handlers."""

    def __init__(self):
        self.handlers: list[Callable[[], Any]] = []

    def add_handler(self, handler: Callable[[], Any]) -> None:
        """Add fallback handler."""
        self.handlers.append(handler)

    def execute(self) -> Any:
        """Execute handlers until one succeeds."""
        errors = []
        for handler in self.handlers:
            try:
                return handler()
            except Exception as e:
                errors.append(e)
        raise RuntimeError(f"All handlers failed: {errors}")


class TestFallbackChain:
    """Tests for fallback chain."""

    def test_first_succeeds(self):
        """First handler succeeds."""
        chain = FallbackChain()
        chain.add_handler(lambda: "first")
        chain.add_handler(lambda: "second")
        result = chain.execute()
        assert result == "first", "Result must not be empty"

    def test_fallback_to_second(self):
        """Fallback to second handler."""
        chain = FallbackChain()
        chain.add_handler(lambda: (_ for _ in ()).throw(ValueError("fail")))
        chain.add_handler(lambda: "second")
        result = chain.execute()
        assert result == "second", "Result must not be empty"

    def test_all_fail(self):
        """All handlers fail."""
        chain = FallbackChain()
        chain.add_handler(lambda: (_ for _ in ()).throw(ValueError("fail1")))
        chain.add_handler(lambda: (_ for _ in ()).throw(ValueError("fail2")))
        with pytest.raises(RuntimeError):
            chain.execute()
