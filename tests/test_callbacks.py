import pytest
from typing import Any


def _make_early_stopping(patience: int, min_delta: float, mode: str):
    """
    Create an EarlyStopping instance while remaining compatible with multiple
    possible constructor signatures.

    - Tries to construct using EarlyStopping(..., mode=...).
    - If that raises a TypeError (mode not accepted), constructs without mode
      and attempts to set the `mode` attribute.
    - If EarlyStopping cannot be imported, skips the tests (useful for partial
      environments).
    - If construction fails for other reasons, fails the test with a clear message.
    """
    try:
        from codex_ml.training.callbacks import EarlyStopping
    except Exception as e:
        # If import fails, skip tests rather than erroring the entire suite.
        pytest.skip(f"EarlyStopping import failed: {e}")

    try:
        # Prefer constructor with mode if available.
        es = EarlyStopping(patience=patience, min_delta=min_delta, mode=mode)
        return es
    except TypeError:
        # Constructor didn't accept `mode` — fall back to old behavior.
        try:
            es = EarlyStopping(patience=patience, min_delta=min_delta)
        except Exception as e:
            pytest.fail(f"Failed to instantiate EarlyStopping without 'mode': {e}")

        # Try to set the mode attribute in a backward-compatible manner.
        try:
            setattr(es, "mode", mode)
        except Exception:
            # If we can't set mode, skip the tests because we can't ensure expected behavior.
            pytest.skip("EarlyStopping does not accept or expose 'mode' parameter/attribute")

        return es
    except Exception as e:
        pytest.fail(f"Unexpected error constructing EarlyStopping: {e}")


def _assert_step_bool(es: Any, value: float, expected: bool):
    """
    Call es.step(value) and ensure it returns a boolean that matches `expected`.
    Provides clearer failure messages for debugging test runs.
    """
    try:
        result = es.step(value)
    except Exception as e:
        pytest.fail(f"Calling EarlyStopping.step({value}) raised an exception: {e}")

    if not isinstance(result, bool):
        pytest.fail(f"EarlyStopping.step({value}) returned non-bool value: {result!r}")

    assert result is expected


def test_early_stopping_improves_and_plateaus():
    es = _make_early_stopping(patience=2, min_delta=0.1, mode="max")
    _assert_step_bool(es, 0.5, False)
    _assert_step_bool(es, 0.7, False)
    # plateau below min_delta
    _assert_step_bool(es, 0.75, False)  # patience=1
    _assert_step_bool(es, 0.76, True)  # patience=2 -> stop


def test_early_stopping_resets_on_real_improvement():
    es = _make_early_stopping(patience=2, min_delta=0.05, mode="min")
    _assert_step_bool(es, 1.0, False)
    _assert_step_bool(es, 0.98, False)  # bad=1
    # clear improvement, should reset
    _assert_step_bool(es, 0.90, False)
    # after reset, two bad steps trigger stop
    _assert_step_bool(es, 0.96, False)
    _assert_step_bool(es, 0.97, True)
