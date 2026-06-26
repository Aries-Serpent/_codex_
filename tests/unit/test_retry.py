"""Unit tests for src/codex/resilience/retry.py.

All tests mock ``time.sleep`` so the suite runs instantly without real delays.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from codex.resilience.retry import RetryExhausted, retry_with_backoff

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class _TransientError(Exception):
    """Simulated transient failure used in tests."""


class _PermanentError(Exception):
    """Simulated non-retryable error used in tests."""


def _make_flaky(fail_times: int, exc: type[Exception] = _TransientError) -> MagicMock:
    """Return a MagicMock that raises *exc* the first *fail_times* calls."""
    mock = MagicMock()
    calls: list[int] = [0]

    def side_effect(*args: object, **kwargs: object) -> str:
        calls[0] += 1
        if calls[0] <= fail_times:
            raise exc(f"transient failure #{calls[0]}")
        return "ok"

    mock.side_effect = side_effect
    return mock


# ---------------------------------------------------------------------------
# Test 1 — succeeds on first attempt (no retries needed)
# ---------------------------------------------------------------------------


def test_succeeds_on_first_attempt() -> None:
    """Function that never raises should be called exactly once."""
    func = MagicMock(return_value="success")
    wrapped = retry_with_backoff(max_retries=3)(func)

    with patch("codex.resilience.retry.time.sleep") as mock_sleep:
        result = wrapped()

    assert result == "success", "Result must not be empty"
    func.assert_called_once()
    mock_sleep.assert_not_called()


# ---------------------------------------------------------------------------
# Test 2 — retries then succeeds
# ---------------------------------------------------------------------------


def test_retries_and_eventually_succeeds() -> None:
    """Function failing twice should succeed on the third call."""
    func = _make_flaky(fail_times=2)
    wrapped = retry_with_backoff(
        max_retries=3,
        base_delay=1.0,
        jitter=0.0,
        exceptions=(_TransientError,),
    )(func)

    with patch("codex.resilience.retry.time.sleep") as mock_sleep:
        result = wrapped()

    assert result == "ok", "Result must not be empty"
    assert func.call_count == 3, "Count must be greater than zero"
    assert mock_sleep.call_count == 2, "Count must be greater than zero"


# ---------------------------------------------------------------------------
# Test 3 — raises RetryExhausted after all retries exhausted
# ---------------------------------------------------------------------------


def test_raises_retry_exhausted_when_all_retries_fail() -> None:
    """RetryExhausted must be raised when every attempt fails."""
    func = _make_flaky(fail_times=999)
    wrapped = retry_with_backoff(
        max_retries=3,
        base_delay=1.0,
        jitter=0.0,
        exceptions=(_TransientError,),
    )(func)

    with patch("codex.resilience.retry.time.sleep"):
        with pytest.raises(RetryExhausted) as exc_info:
            wrapped()

    err = exc_info.value
    assert err.attempts == 4, "attempts is not valid"
    assert func.call_count == 4, "Count must be greater than zero"
    # The original exception must be chained as __cause__
    assert isinstance(err.__cause__, _TransientError)


# ---------------------------------------------------------------------------
# Test 4 — exponential backoff delays follow the formula
# ---------------------------------------------------------------------------


def test_backoff_delays_follow_exponential_formula() -> None:
    """Verify sleep is called with the correct exponential delay values."""
    func = _make_flaky(fail_times=3)
    base = 2.0
    wrapped = retry_with_backoff(
        max_retries=3,
        base_delay=base,
        max_delay=1000.0,
        jitter=0.0,  # no jitter → deterministic
        exceptions=(_TransientError,),
    )(func)

    with patch("codex.resilience.retry.time.sleep") as mock_sleep:
        wrapped()

    # Expected: delay = min(base * 2**attempt, max_delay)  for attempt in (0,1,2)
    expected_delays = [
        base * 2**0,  # 2.0
        base * 2**1,  # 4.0
        base * 2**2,  # 8.0
    ]
    actual_delays = [c.args[0] for c in mock_sleep.call_args_list]
    assert actual_delays == pytest.approx(expected_delays), "actual_delays is not valid"


# ---------------------------------------------------------------------------
# Test 5 — max_delay cap is respected
# ---------------------------------------------------------------------------


def test_max_delay_cap_is_respected() -> None:
    """Computed delay must never exceed max_delay."""
    func = _make_flaky(fail_times=4)
    wrapped = retry_with_backoff(
        max_retries=4,
        base_delay=100.0,
        max_delay=5.0,
        jitter=0.0,
        exceptions=(_TransientError,),
    )(func)

    with patch("codex.resilience.retry.time.sleep") as mock_sleep:
        wrapped()

    for c in mock_sleep.call_args_list:
        assert c.args[0] <= 5.0, "Condition must be true"


# ---------------------------------------------------------------------------
# Test 6 — non-retryable exceptions propagate immediately
# ---------------------------------------------------------------------------


def test_non_retryable_exception_propagates_immediately() -> None:
    """Exceptions outside the *exceptions* tuple must NOT trigger retries."""
    func = MagicMock(side_effect=_PermanentError("fatal"))
    wrapped = retry_with_backoff(
        max_retries=3,
        exceptions=(_TransientError,),  # _PermanentError NOT listed
    )(func)

    with patch("codex.resilience.retry.time.sleep") as mock_sleep:
        with pytest.raises(_PermanentError):
            wrapped()

    func.assert_called_once()  # called only once — no retries
    mock_sleep.assert_not_called()


# ---------------------------------------------------------------------------
# Test 7 — RetryExhausted.attempts equals max_retries + 1
# ---------------------------------------------------------------------------


def test_retry_exhausted_attempts_count() -> None:
    """RetryExhausted.attempts must equal max_retries + 1."""
    max_retries = 5
    func = MagicMock(side_effect=_TransientError("boom"))
    wrapped = retry_with_backoff(
        max_retries=max_retries,
        base_delay=0.0,
        jitter=0.0,
        exceptions=(_TransientError,),
    )(func)

    with patch("codex.resilience.retry.time.sleep"):
        with pytest.raises(RetryExhausted) as exc_info:
            wrapped()

    assert exc_info.value.attempts == max_retries + 1, "Value must be initialized"
    assert func.call_count == max_retries + 1, "Count must be greater than zero"


# ---------------------------------------------------------------------------
# Test 8 — decorator preserves wrapped function metadata
# ---------------------------------------------------------------------------


def test_decorator_preserves_function_metadata() -> None:
    """functools.wraps must preserve __name__ and __doc__."""

    @retry_with_backoff(max_retries=1)
    def my_special_function() -> None:
        """Docstring here."""

    assert my_special_function.__name__ == "my_special_function", "__name__ is not valid"
    assert my_special_function.__doc__ == "Docstring here.", "__doc__ is not valid"


# ---------------------------------------------------------------------------
# Test 9 — jitter adds random noise within expected range
# ---------------------------------------------------------------------------


def test_jitter_adds_noise_within_bounds() -> None:
    """With jitter > 0 each sleep value should be in [base_delay, base_delay + jitter]."""
    func = _make_flaky(fail_times=1)
    base = 1.0
    jitter = 0.5
    wrapped = retry_with_backoff(
        max_retries=1,
        base_delay=base,
        max_delay=1000.0,
        jitter=jitter,
        exceptions=(_TransientError,),
    )(func)

    recorded: list[float] = []
    with patch("codex.resilience.retry.time.sleep", side_effect=recorded.append):
        wrapped()

    assert len(recorded) == 1, "Recorded must not be empty"
    lo = base * 2**0  # attempt 0 → base * 1
    hi = lo + jitter
    assert lo <= recorded[0] <= hi, "lo is not valid"
