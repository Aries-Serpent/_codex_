"""Unit tests for codex.resilience.circuit_breaker (Gap 29).

Covers:
- CircuitState enum values
- CircuitBreaker initial state is CLOSED
- Successful calls don't change state
- Failures count correctly and open the circuit at threshold
- CircuitOpenError raised when circuit is OPEN
- CircuitOpenError.retry_after is populated
- Circuit transitions OPEN → HALF_OPEN after recovery_timeout
- Consecutive successes in HALF_OPEN close the circuit
- Any failure in HALF_OPEN re-opens the circuit
- manual reset() returns to CLOSED
- Thread-safety smoke test (concurrent calls)
- Invalid constructor arguments raise ValueError
"""

from __future__ import annotations

import threading
import time
from unittest.mock import MagicMock

import pytest

from codex.resilience import CircuitBreaker, CircuitOpenError, CircuitState


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_failing(exc: type[Exception] = RuntimeError, msg: str = "boom") -> MagicMock:
    fn = MagicMock(side_effect=exc(msg))
    return fn


def _make_success(return_value: object = "ok") -> MagicMock:
    fn = MagicMock(return_value=return_value)
    return fn


# ---------------------------------------------------------------------------
# 1. Initial state
# ---------------------------------------------------------------------------


def test_initial_state_is_closed():
    cb = CircuitBreaker()
    assert cb.state is CircuitState.CLOSED


# ---------------------------------------------------------------------------
# 2. Successful calls don't change state
# ---------------------------------------------------------------------------


def test_success_keeps_circuit_closed():
    cb = CircuitBreaker(failure_threshold=3)
    fn = _make_success()
    for _ in range(10):
        result = cb.call(fn)
    assert result == "ok"
    assert cb.state is CircuitState.CLOSED


# ---------------------------------------------------------------------------
# 3. Failures count toward threshold
# ---------------------------------------------------------------------------


def test_failures_below_threshold_keep_circuit_closed():
    cb = CircuitBreaker(failure_threshold=5)
    fn = _make_failing()
    for _ in range(4):
        with pytest.raises(RuntimeError):
            cb.call(fn)
    assert cb.state is CircuitState.CLOSED


def test_failures_at_threshold_open_circuit():
    cb = CircuitBreaker(failure_threshold=3)
    fn = _make_failing()
    for _ in range(3):
        with pytest.raises(RuntimeError):
            cb.call(fn)
    assert cb.state is CircuitState.OPEN


# ---------------------------------------------------------------------------
# 4. CircuitOpenError raised when OPEN
# ---------------------------------------------------------------------------


def test_open_circuit_raises_circuit_open_error():
    cb = CircuitBreaker(failure_threshold=2)
    fn = _make_failing()
    for _ in range(2):
        with pytest.raises(RuntimeError):
            cb.call(fn)

    with pytest.raises(CircuitOpenError):
        cb.call(_make_success())


def test_circuit_open_error_has_retry_after():
    cb = CircuitBreaker(failure_threshold=1, recovery_timeout=30)
    with pytest.raises(RuntimeError):
        cb.call(_make_failing())

    with pytest.raises(CircuitOpenError) as exc_info:
        cb.call(_make_success())

    assert exc_info.value.retry_after is not None
    assert 0 < exc_info.value.retry_after <= 30


def test_circuit_open_error_is_exception():
    err = CircuitOpenError("test")
    assert isinstance(err, Exception)
    assert str(err) == "test"


# ---------------------------------------------------------------------------
# 5. OPEN → HALF_OPEN transition after recovery_timeout
# ---------------------------------------------------------------------------


def test_open_transitions_to_half_open_after_timeout(monkeypatch):
    cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.05)
    with pytest.raises(RuntimeError):
        cb.call(_make_failing())
    assert cb.state is CircuitState.OPEN

    time.sleep(0.06)
    assert cb.state is CircuitState.HALF_OPEN


# ---------------------------------------------------------------------------
# 6. HALF_OPEN → CLOSED after success_threshold successes
# ---------------------------------------------------------------------------


def test_half_open_closes_after_consecutive_successes():
    cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.05, success_threshold=2)
    with pytest.raises(RuntimeError):
        cb.call(_make_failing())

    time.sleep(0.06)
    assert cb.state is CircuitState.HALF_OPEN

    cb.call(_make_success())
    assert cb.state is CircuitState.HALF_OPEN  # only 1 success

    cb.call(_make_success())
    assert cb.state is CircuitState.CLOSED


# ---------------------------------------------------------------------------
# 7. HALF_OPEN failure re-opens the circuit
# ---------------------------------------------------------------------------


def test_half_open_failure_reopens_circuit():
    cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.05, success_threshold=3)
    with pytest.raises(RuntimeError):
        cb.call(_make_failing())

    time.sleep(0.06)
    assert cb.state is CircuitState.HALF_OPEN

    with pytest.raises(RuntimeError):
        cb.call(_make_failing())
    assert cb.state is CircuitState.OPEN


# ---------------------------------------------------------------------------
# 8. Manual reset
# ---------------------------------------------------------------------------


def test_reset_closes_open_circuit():
    cb = CircuitBreaker(failure_threshold=1)
    with pytest.raises(RuntimeError):
        cb.call(_make_failing())
    assert cb.state is CircuitState.OPEN

    cb.reset()
    assert cb.state is CircuitState.CLOSED
    assert cb._failure_count == 0


def test_reset_allows_calls_again():
    cb = CircuitBreaker(failure_threshold=1)
    with pytest.raises(RuntimeError):
        cb.call(_make_failing())

    cb.reset()
    result = cb.call(_make_success(return_value=42))
    assert result == 42


# ---------------------------------------------------------------------------
# 9. Success in CLOSED state resets failure count
# ---------------------------------------------------------------------------


def test_success_resets_failure_count_in_closed():
    cb = CircuitBreaker(failure_threshold=3)
    fn_fail = _make_failing()
    fn_ok = _make_success()

    cb.call(fn_fail) if False else None  # suppress lint warning
    for _ in range(2):
        with pytest.raises(RuntimeError):
            cb.call(fn_fail)

    cb.call(fn_ok)  # success should reset count
    assert cb._failure_count == 0
    assert cb.state is CircuitState.CLOSED


# ---------------------------------------------------------------------------
# 10. Invalid constructor arguments
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "kwargs,match",
    [
        ({"failure_threshold": 0}, "failure_threshold"),
        ({"recovery_timeout": -1}, "recovery_timeout"),
        ({"success_threshold": 0}, "success_threshold"),
    ],
)
def test_invalid_constructor_raises_value_error(kwargs, match):
    with pytest.raises(ValueError, match=match):
        CircuitBreaker(**kwargs)


# ---------------------------------------------------------------------------
# 11. Thread-safety smoke test
# ---------------------------------------------------------------------------


def test_concurrent_calls_do_not_corrupt_state():
    """Multiple threads calling simultaneously must not corrupt internal counters."""
    cb = CircuitBreaker(failure_threshold=20)
    errors: list[Exception] = []

    def worker():
        try:
            cb.call(_make_success())
        except Exception as exc:  # noqa: BLE001
            errors.append(exc)

    threads = [threading.Thread(target=worker) for _ in range(50)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors
    assert cb.state is CircuitState.CLOSED
