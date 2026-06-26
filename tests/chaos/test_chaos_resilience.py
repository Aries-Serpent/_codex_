"""Chaos engineering tests for the resilience layer.

Exercises CircuitBreaker, retry_with_backoff, and GracefulDegradation under
random failures, flaky services, and combined fault scenarios.
"""

from __future__ import annotations

import random
import time

import pytest

from codex.resilience.circuit_breaker import CircuitBreaker, CircuitOpenError, CircuitState
from codex.resilience.degradation import DegradationError, GracefulDegradation
from codex.resilience.retry import RetryExhausted, retry_with_backoff

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class _FlakyService:
    """A service that fails exactly *fail_count* times then always succeeds."""

    def __init__(self, fail_count: int, success_value: str = "ok") -> None:
        self._fail_count = fail_count
        self._calls = 0
        self.success_value = success_value

    def call(self) -> str:
        self._calls += 1
        if self._calls <= self._fail_count:
            raise RuntimeError(f"Flaky failure #{self._calls}")
        return self.success_value


class _AlwaysFailingService:
    """A service that always raises."""

    def call(self) -> str:
        raise RuntimeError("permanent failure")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestCircuitBreakerUnderRandomFailures:
    """test_circuit_breaker_under_random_failures"""

    def test_circuit_opens_after_threshold_failures(self) -> None:
        """Random mix of successes/failures — circuit opens once failure_threshold
        consecutive failures are accumulated in a closed state."""
        rng = random.Random(42)
        failure_threshold = 3
        cb = CircuitBreaker(
            failure_threshold=failure_threshold,
            recovery_timeout=60,
            success_threshold=2,
            name="chaos_random",
        )

        def _succeed() -> str:
            return "success"

        def _fail() -> str:
            raise RuntimeError("injected failure")

        # Drive enough failures to open the circuit
        failures_injected = 0
        with pytest.raises(CircuitOpenError):
            for _ in range(200):
                if cb.state is CircuitState.OPEN:
                    # Circuit is open — next call must raise CircuitOpenError
                    cb.call(_fail)  # This triggers CircuitOpenError
                    break
                fn = _fail if rng.random() < 0.7 else _succeed
                try:
                    cb.call(fn)
                    if fn is _succeed:
                        failures_injected = 0  # reset streak on success
                except RuntimeError:
                    failures_injected += 1

        assert cb.state is CircuitState.OPEN, "state is not valid"

    def test_circuit_stays_closed_under_mostly_success(self) -> None:
        """With very low failure rate the circuit stays closed."""
        rng = random.Random(99)
        cb = CircuitBreaker(failure_threshold=5, recovery_timeout=60, name="mostly_ok")

        def _succeed() -> str:
            return "ok"

        def _fail() -> str:
            raise RuntimeError("rare failure")

        for _ in range(50):
            if cb.state is CircuitState.OPEN:
                break
            fn = _fail if rng.random() < 0.05 else _succeed
            try:
                cb.call(fn)
            except RuntimeError:
                pass  # counted internally

        # With only ~5% failures, threshold of 5 should not be breached
        # (consecutive runs rarely produce 5 failures in a row at 5%)
        # We only assert state is not open — this is a probabilistic check.
        assert cb.state is CircuitState.CLOSED, "state is not valid"


class TestRetryExhaustionUnderFlakyService:
    """test_retry_exhaustion_under_flaky_service"""

    def test_eventually_succeeds_after_n_minus_1_failures(self) -> None:
        """Service fails N-1 times then succeeds → retry_with_backoff succeeds."""
        svc = _FlakyService(fail_count=2, success_value="done")

        @retry_with_backoff(max_retries=3, base_delay=0.0, jitter=0.0)
        def call() -> str:
            return svc.call()

        result = call()
        assert result == "done", "Result must not be empty"
        assert svc._calls == 3, "_calls is not valid"

    def test_raises_retry_exhausted_when_always_failing(self) -> None:
        """Service that never succeeds → RetryExhausted is raised."""
        svc = _AlwaysFailingService()

        @retry_with_backoff(max_retries=2, base_delay=0.0, jitter=0.0)
        def call() -> str:
            return svc.call()

        with pytest.raises(RetryExhausted) as exc_info:
            call()
        assert exc_info.value.attempts == 3, "Value must be initialized"


class TestGracefulDegradationUnderTotalFailure:
    """test_graceful_degradation_under_total_failure"""

    def test_fallback_returned_100_percent(self) -> None:
        """Primary always raises; fallback value is returned on every call."""
        FALLBACK = "safe_default"
        dg = GracefulDegradation(fallback=FALLBACK)

        @dg
        def primary() -> str:
            raise RuntimeError("primary down")

        results = [primary() for _ in range(20)]
        assert all(r == FALLBACK for r in results), "fallback must be returned every time"

    def test_no_fallback_raises_degradation_error(self) -> None:
        """Without a fallback, GracefulDegradation raises DegradationError."""
        dg = GracefulDegradation()  # no fallback

        @dg
        def primary() -> str:
            raise RuntimeError("boom")

        with pytest.raises(DegradationError):
            primary()


class TestCircuitHalfOpenRecovery:
    """test_circuit_half_open_recovery"""

    def test_half_open_probe_succeeds_closes_circuit(self) -> None:
        """Open circuit → wait reset_timeout → verify half-open probe → success → closed."""
        cb = CircuitBreaker(
            failure_threshold=2,
            recovery_timeout=0.05,  # 50 ms for fast tests
            success_threshold=1,
            name="half_open_test",
        )

        def _fail() -> None:
            raise RuntimeError("forced failure")

        # Trip the circuit open
        for _ in range(2):
            with pytest.raises(RuntimeError):
                cb.call(_fail)

        assert cb.state is CircuitState.OPEN, "state is not valid"

        # Wait for recovery timeout to elapse
        time.sleep(0.06)

        # State should now be HALF_OPEN (lazily evaluated on .state access)
        assert cb.state is CircuitState.HALF_OPEN, "state is not valid"

        # A successful call in HALF_OPEN should close the circuit
        result = cb.call(lambda: "probe_ok")
        assert result == "probe_ok", "Result must not be empty"
        assert cb.state is CircuitState.CLOSED, "state is not valid"

    def test_half_open_failure_reopens_circuit(self) -> None:
        """A failure during HALF_OPEN re-opens the circuit."""
        cb = CircuitBreaker(
            failure_threshold=2,
            recovery_timeout=0.05,
            success_threshold=2,
            name="half_open_reopen",
        )

        def _fail() -> None:
            raise RuntimeError("forced")

        for _ in range(2):
            with pytest.raises(RuntimeError):
                cb.call(_fail)

        time.sleep(0.06)
        assert cb.state is CircuitState.HALF_OPEN, "state is not valid"

        with pytest.raises(RuntimeError):
            cb.call(_fail)

        assert cb.state is CircuitState.OPEN, "state is not valid"


class TestCombinedCircuitPlusRetry:
    """test_combined_circuit_plus_retry"""

    def test_combined_behaviour_circuit_wraps_retry(self) -> None:
        """Circuit breaker wrapping a flaky function with retry — combined behaviour.

        The inner function is wrapped with retry (3 attempts, 0 delay).
        If it needs >3 attempts the RetryExhausted propagates to the CB,
        which counts it as a circuit failure.
        """
        call_log: list[str] = []

        svc = _FlakyService(fail_count=1, success_value="combined_ok")

        @retry_with_backoff(max_retries=2, base_delay=0.0, jitter=0.0)
        def inner() -> str:
            val = svc.call()
            call_log.append("success")
            return val

        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60, name="combined")

        result = cb.call(inner)
        assert result == "combined_ok", "Result must not be empty"
        assert "success" in call_log, "Condition must be true"
        assert cb.state is CircuitState.CLOSED, "state is not valid"

    def test_combined_behaviour_circuit_opens_when_retry_always_exhausted(self) -> None:
        """When every retry is exhausted the circuit eventually opens."""
        svc = _AlwaysFailingService()

        @retry_with_backoff(max_retries=1, base_delay=0.0, jitter=0.0)
        def inner() -> str:
            return svc.call()

        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60, name="combined_open")

        for _ in range(3):
            with pytest.raises(RetryExhausted):
                cb.call(inner)

        assert cb.state is CircuitState.OPEN, "state is not valid"
        with pytest.raises(CircuitOpenError):
            cb.call(inner)
