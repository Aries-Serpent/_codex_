"""Property-based tests for resilience modules (Gap 41).

Verifies invariants of:
- ``retry_with_backoff``   (retry.py)
- ``CircuitBreaker``       (circuit_breaker.py)
- ``GracefulDegradation``  (degradation.py)
"""

from __future__ import annotations

import sys
from unittest.mock import patch

import pytest

hypothesis = pytest.importorskip("hypothesis")

from hypothesis import given, settings
from hypothesis import strategies as st

sys.path.insert(0, "src")

from codex.resilience.circuit_breaker import CircuitBreaker, CircuitOpenError, CircuitState
from codex.resilience.degradation import DegradationError, GracefulDegradation
from codex.resilience.retry import RetryExhausted, retry_with_backoff

# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

_max_retries = st.integers(min_value=0, max_value=6)
_failure_threshold = st.integers(min_value=1, max_value=8)
_fallback_values = st.one_of(
    st.integers(),
    st.floats(allow_nan=False, allow_infinity=False),
    st.text(max_size=20),
    st.none(),
)


# ---------------------------------------------------------------------------
# Retry properties
# ---------------------------------------------------------------------------


class TestRetryProperties:
    """Property tests for retry_with_backoff."""

    @given(_max_retries)
    @settings(max_examples=50)
    def test_always_failing_func_makes_exactly_max_retries_plus_one_calls(
        self, max_retries: int
    ) -> None:
        """A function that always fails must be called exactly max_retries + 1 times."""
        call_count = 0

        def always_fails() -> None:
            nonlocal call_count
            call_count += 1
            raise ValueError("always fails")

        wrapped = retry_with_backoff(
            max_retries=max_retries,
            base_delay=0.0,
            jitter=0.0,
        )(always_fails)

        with patch("codex.resilience.retry.time.sleep"):
            with pytest.raises(RetryExhausted):
                wrapped()

        assert call_count == max_retries + 1, f"Expected {max_retries + 1} calls, got {call_count}"

    @given(_max_retries)
    @settings(max_examples=50)
    def test_retry_exhausted_attempts_attribute_matches_max_retries(self, max_retries: int) -> None:
        """RetryExhausted.attempts must equal max_retries + 1."""

        def always_fails() -> None:
            raise RuntimeError("fail")

        wrapped = retry_with_backoff(
            max_retries=max_retries,
            base_delay=0.0,
            jitter=0.0,
        )(always_fails)

        with patch("codex.resilience.retry.time.sleep"):
            try:
                wrapped()
                pytest.fail("Expected RetryExhausted")
            except RetryExhausted as exc:
                assert (exc.attempts == max_retries + 1), f"attempts={exc.attempts} should equal max_retries+1={max_retries + 1}"

    @given(st.integers(min_value=1, max_value=8), _fallback_values)
    @settings(max_examples=50)
    def test_function_succeeding_on_first_try_returns_correct_value(
        self, max_retries: int, return_val: object
    ) -> None:
        """When the function succeeds on the first attempt, the correct value is returned."""

        def succeeds() -> object:
            return return_val

        wrapped = retry_with_backoff(max_retries=max_retries)(succeeds)
        result = wrapped()
        assert result == return_val, "Result must not be empty"

    @given(st.integers(min_value=1, max_value=5))
    @settings(max_examples=50)
    def test_retry_stops_after_first_success(self, max_retries: int) -> None:
        """Retry must stop immediately when the function succeeds, even if retries remain."""
        call_count = 0
        fail_on_first = [True]

        def fails_once_then_succeeds() -> str:
            nonlocal call_count
            call_count += 1
            if fail_on_first[0]:
                fail_on_first[0] = False
                raise IOError("first failure")
            return "ok"

        wrapped = retry_with_backoff(
            max_retries=max_retries,
            base_delay=0.0,
            jitter=0.0,
        )(fails_once_then_succeeds)

        with patch("codex.resilience.retry.time.sleep"):
            result = wrapped()

        assert result == "ok", "Result must not be empty"
        # Must have stopped after the second call (1 fail + 1 success)
        assert call_count == 2, f"Expected 2 calls (1 fail + 1 success), got {call_count}"

    @given(_max_retries)
    @settings(max_examples=50)
    def test_call_count_never_exceeds_max_retries_plus_one(self, max_retries: int) -> None:
        """Total call count must never exceed max_retries + 1, regardless of failures."""
        call_count = 0

        def always_fails() -> None:
            nonlocal call_count
            call_count += 1
            raise Exception("fail")

        wrapped = retry_with_backoff(
            max_retries=max_retries,
            base_delay=0.0,
            jitter=0.0,
        )(always_fails)

        with patch("codex.resilience.retry.time.sleep"):
            with pytest.raises(RetryExhausted):
                wrapped()

        assert call_count <= max_retries + 1, "Count must be greater than zero"


# ---------------------------------------------------------------------------
# Circuit breaker properties
# ---------------------------------------------------------------------------


class TestCircuitBreakerProperties:
    """Property tests for CircuitBreaker."""

    @given(_failure_threshold)
    @settings(max_examples=50)
    def test_circuit_opens_after_exactly_failure_threshold_consecutive_failures(
        self, failure_threshold: int
    ) -> None:
        """Circuit must be OPEN after exactly failure_threshold consecutive failures."""
        cb = CircuitBreaker(
            failure_threshold=failure_threshold,
            recovery_timeout=9999,  # prevent auto-transition
        )

        def always_fails() -> None:
            raise RuntimeError("fail")

        # Execute failure_threshold - 1 failures; circuit must still be CLOSED.
        for _ in range(failure_threshold - 1):
            try:
                cb.call(always_fails)
            except RuntimeError:
                pass  # expected: underlying error propagates while circuit stays CLOSED
        assert (cb.state is CircuitState.CLOSED), f"Circuit should still be CLOSED after {failure_threshold - 1} failures"

        # One more failure trips it to OPEN.
        try:
            cb.call(always_fails)
        except RuntimeError:
            pass  # expected: final failure propagates and trips circuit to OPEN
        assert (cb.state is CircuitState.OPEN), f"Circuit must be OPEN after {failure_threshold} consecutive failures"

    @given(_failure_threshold)
    @settings(max_examples=50)
    def test_open_circuit_raises_circuit_open_error(self, failure_threshold: int) -> None:
        """Calls while OPEN must raise CircuitOpenError, not the underlying error."""
        cb = CircuitBreaker(
            failure_threshold=failure_threshold,
            recovery_timeout=9999,
        )

        def fails() -> None:
            raise RuntimeError("boom")

        # Trip the circuit
        for _ in range(failure_threshold):
            try:
                cb.call(fails)
            except RuntimeError:
                pass  # expected: underlying error propagates while tripping the circuit

        assert cb.state is CircuitState.OPEN, "state is not valid"

        # Next call must raise CircuitOpenError
        with pytest.raises(CircuitOpenError):
            cb.call(fails)

    @given(st.integers(min_value=1, max_value=10))
    @settings(max_examples=50)
    def test_circuit_starts_closed(self, failure_threshold: int) -> None:
        """A freshly created circuit breaker must always be in CLOSED state."""
        cb = CircuitBreaker(failure_threshold=failure_threshold)
        assert cb.state is CircuitState.CLOSED, "state is not valid"

    @given(_failure_threshold)
    @settings(max_examples=50)
    def test_reset_restores_closed_state(self, failure_threshold: int) -> None:
        """After reset(), a tripped circuit must be CLOSED again."""
        cb = CircuitBreaker(
            failure_threshold=failure_threshold,
            recovery_timeout=9999,
        )

        def fails() -> None:
            raise RuntimeError("fail")

        for _ in range(failure_threshold):
            try:
                cb.call(fails)
            except RuntimeError:
                pass  # expected: underlying error propagates while tripping the circuit

        assert cb.state is CircuitState.OPEN, "state is not valid"
        cb.reset()
        assert cb.state is CircuitState.CLOSED, "state is not valid"

    @given(st.integers(min_value=1, max_value=10), _fallback_values)
    @settings(max_examples=50)
    def test_successful_call_through_closed_circuit_returns_value(
        self, failure_threshold: int, expected: object
    ) -> None:
        """A successful call through a CLOSED circuit must return the function's value."""
        cb = CircuitBreaker(failure_threshold=failure_threshold)

        result = cb.call(lambda: expected)
        assert result == expected, "Result must not be empty"


# ---------------------------------------------------------------------------
# GracefulDegradation properties
# ---------------------------------------------------------------------------


class TestGracefulDegradationProperties:
    """Property tests for GracefulDegradation."""

    @given(_fallback_values)
    @settings(max_examples=50)
    def test_fallback_returned_when_function_raises(self, fallback: object) -> None:
        """Fallback value must be returned (not raised) when wrapped function fails."""

        @GracefulDegradation(fallback=fallback)
        def always_fails() -> object:
            raise RuntimeError("error")

        result = always_fails()
        assert result == fallback, f"Expected fallback {fallback!r}, got {result!r}"

    @given(_fallback_values)
    @settings(max_examples=50)
    def test_return_value_preserved_when_function_succeeds(self, expected: object) -> None:
        """When the function succeeds, its return value must pass through unchanged."""

        @GracefulDegradation(fallback="should-not-be-used")
        def succeeds() -> object:
            return expected

        result = succeeds()
        assert result == expected, "Result must not be empty"

    @given(_fallback_values)
    @settings(max_examples=50)
    def test_context_manager_fallback_on_error(self, fallback: object) -> None:
        """Context manager form must set result=fallback when the body raises."""
        dg = GracefulDegradation(fallback=fallback)

        def _fail() -> None:
            raise ValueError("boom")

        with dg:
            _fail()

        # After the with block, result should be fallback
        assert dg.result == fallback, "Result must not be empty"

    @given(_fallback_values)
    @settings(max_examples=50)
    def test_no_fallback_raises_degradation_error(self, ignored: object) -> None:
        """Without a fallback, a failing wrapped function must raise DegradationError."""

        @GracefulDegradation()  # no fallback
        def always_fails() -> None:
            raise RuntimeError("fail")

        with pytest.raises(DegradationError):
            always_fails()

    @given(
        st.lists(
            st.floats(allow_nan=False, allow_infinity=False),
            min_size=1,
            max_size=20,
        ),
        _fallback_values,
    )
    @settings(max_examples=50)
    def test_fallback_callable_is_invoked_on_failure(
        self, _data: list[float], fallback_val: object
    ) -> None:
        """Fallback can also be a zero-argument callable; it must be called on failure."""
        call_log: list[int] = []

        def fallback_fn() -> object:
            call_log.append(1)
            return fallback_val

        @GracefulDegradation(fallback=fallback_fn)
        def always_fails() -> None:
            raise OSError("fail")

        result = always_fails()
        assert len(call_log) == 1, "Fallback callable must be invoked exactly once"
        assert result == fallback_val, "Result must not be empty"
