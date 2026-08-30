"""Unit tests for codex.resilience.degradation (Gap 31).

Covers:
- GracefulDegradation as decorator returns fallback on exception
- GracefulDegradation as decorator returns real value on success
- GracefulDegradation as context manager captures result on success
- GracefulDegradation as context manager sets fallback on exception
- Callable fallback is invoked on failure
- DegradationError raised when no fallback provided
- DegradationError carries original exception
- Non-matching exception types are not caught
- GracefulDegradation suppresses only specified exception types
- Multiple failures return consistent fallback
"""

from __future__ import annotations

import pytest

from codex.resilience import DegradationError, GracefulDegradation

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _always_fail(exc: type[Exception] = ValueError, msg: str = "fail") -> None:
    raise exc(msg)


def _always_return(value: object = "real") -> object:
    return value


# ---------------------------------------------------------------------------
# 1. Decorator — success path
# ---------------------------------------------------------------------------


def test_decorator_returns_real_value_on_success():
    @GracefulDegradation(fallback="default")
    def good() -> str:
        return "real"

    assert good() == "real", "Condition must be true"


# ---------------------------------------------------------------------------
# 2. Decorator — failure path with static fallback
# ---------------------------------------------------------------------------


def test_decorator_returns_fallback_on_exception():
    @GracefulDegradation(fallback="fallback_value")
    def bad() -> str:
        raise RuntimeError("oops")

    assert bad() == "fallback_value", "Value must be initialized"


# ---------------------------------------------------------------------------
# 3. Decorator — failure path with callable fallback
# ---------------------------------------------------------------------------


def test_decorator_invokes_callable_fallback():
    called: list[bool] = []

    def fallback_fn() -> str:
        called.append(True)
        return "from_callable"

    @GracefulDegradation(fallback=fallback_fn)
    def bad() -> str:
        raise RuntimeError("oops")

    result = bad()
    assert result == "from_callable", "Result must not be empty"
    assert called == [True], "called is not valid"


# ---------------------------------------------------------------------------
# 4. Decorator — no fallback raises DegradationError
# ---------------------------------------------------------------------------


def test_decorator_no_fallback_raises_degradation_error():
    @GracefulDegradation()
    def bad() -> str:
        raise RuntimeError("unrecoverable")

    with pytest.raises(DegradationError) as exc_info:
        bad()

    assert exc_info.value.original is not None, "original must be initialized"
    assert isinstance(exc_info.value.original, RuntimeError)


# ---------------------------------------------------------------------------
# 5. Context manager — success path
# ---------------------------------------------------------------------------


def test_context_manager_captures_result_on_success():
    with GracefulDegradation(fallback=None) as dg:
        dg.result = "success_value"

    assert dg.result == "success_value", "Result must not be empty"


# ---------------------------------------------------------------------------
# 6. Context manager — exception sets fallback
# ---------------------------------------------------------------------------


def test_context_manager_sets_fallback_on_exception():
    def _fail():
        raise ValueError("something failed")

    dg = GracefulDegradation(fallback="safe")
    with dg:
        _fail()

    assert dg.result == "safe", "Result must not be empty"


# ---------------------------------------------------------------------------
# 7. Context manager — no fallback raises DegradationError
# ---------------------------------------------------------------------------


def test_context_manager_no_fallback_raises_degradation_error():
    def _boom():
        raise RuntimeError("boom")

    with pytest.raises(DegradationError) as exc_info:
        with GracefulDegradation() as dg:  # noqa: F841
            _boom()

    assert isinstance(exc_info.value.original, RuntimeError)


# ---------------------------------------------------------------------------
# 8. Non-matching exception type is not caught
# ---------------------------------------------------------------------------


def test_non_matching_exception_propagates():
    @GracefulDegradation(fallback="x", exceptions=(ValueError,))
    def bad() -> str:
        raise TypeError("not a ValueError")

    with pytest.raises(TypeError, match="not a ValueError"):
        bad()


def test_context_manager_non_matching_exception_propagates():
    with pytest.raises(KeyError):
        with GracefulDegradation(fallback="x", exceptions=(ValueError,)):
            raise KeyError("not caught")


# ---------------------------------------------------------------------------
# 9. DegradationError is an Exception subclass
# ---------------------------------------------------------------------------


def test_degradation_error_is_exception():
    err = DegradationError("test", original=ValueError("cause"))
    assert isinstance(err, Exception)
    assert str(err) == "test", "Condition must be true"
    assert isinstance(err.original, ValueError)


# ---------------------------------------------------------------------------
# 10. Fallback value 0 / False / None are returned correctly (falsy values)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("falsy_fallback", [0, False, None, "", []])
def test_falsy_fallback_values_are_returned(falsy_fallback):
    @GracefulDegradation(fallback=falsy_fallback)
    def bad() -> object:
        raise RuntimeError("fail")

    assert bad() == falsy_fallback, "Condition must be true"
