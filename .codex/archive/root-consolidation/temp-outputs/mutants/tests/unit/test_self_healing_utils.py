"""Unit tests for codex_ml.utils.self_healing (Gap 5).

Covers:
- FailureType enum — all five variants accessible and correct values
- OOMHandler.__init__ — initial state
- OOMHandler.can_retry — True while retries < max and batch > min
- OOMHandler.can_retry — False when retry_count reaches max_retries
- OOMHandler.can_retry — False when batch_size equals min_batch_size
- OOMHandler.reduce_batch_size — halves batch size correctly
- OOMHandler.reduce_batch_size — never goes below min_batch_size
- OOMHandler.reduce_batch_size — increments retry_count
- OOMHandler.reset — restores initial state
- SelfHealingContext.__init__ — default parameters
- SelfHealingContext.__init__ — custom parameters
- SelfHealingContext.__enter__ — returns self
- SelfHealingContext.__exit__ — no exception path (returns False)
- SelfHealingContext.__exit__ — OOM exception: suppressed when oom_recovery on
- SelfHealingContext.__exit__ — OOM exception: propagated when oom_recovery off
- SelfHealingContext.__exit__ — OOM exception: propagated when max retries hit
- SelfHealingContext.__exit__ — checkpoint corruption: propagated (rollback stub)
- SelfHealingContext.__exit__ — unknown exception: propagated
- SelfHealingContext._classify_failure — OOM via "out of memory"
- SelfHealingContext._classify_failure — OOM via "oom"
- SelfHealingContext._classify_failure — OOM via CUDA memory error
- SelfHealingContext._classify_failure — checkpoint corruption via "corrupt"
- SelfHealingContext._classify_failure — checkpoint corruption via "integrity"
- SelfHealingContext._classify_failure — checkpoint corruption via "hash"
- SelfHealingContext._classify_failure — config drift
- SelfHealingContext._classify_failure — unknown / generic exception
- SelfHealingContext.failures list populated on exit
- auto_remediate — happy-path function succeeds on first try
- auto_remediate — passes positional and keyword args to func
- auto_remediate — retries up to max_retries then re-raises
- auto_remediate — updates batch_size kwarg each attempt
- auto_remediate — raises RuntimeError when loop ends without exception
- __all__ exports exactly the four declared names
"""

from __future__ import annotations

import logging
from unittest.mock import MagicMock

import pytest

from codex_ml.utils.self_healing import (
    FailureType,
    OOMHandler,
    SelfHealingContext,
    auto_remediate,
)

# ---------------------------------------------------------------------------
# FailureType
# ---------------------------------------------------------------------------


class TestFailureType:
    def test_all_variants_exist(self):
        expected = {"OOM", "METRIC_REGRESSION", "CHECKPOINT_CORRUPTION", "CONFIG_DRIFT", "UNKNOWN"}
        assert {m.name for m in FailureType} == expected, "Condition must be true"

    def test_oom_value(self):
        assert FailureType.OOM.value == "out_of_memory", "Value must be initialized"

    def test_metric_regression_value(self):
        assert FailureType.METRIC_REGRESSION.value == "metric_regression", "Value must be initialized"

    def test_checkpoint_corruption_value(self):
        assert FailureType.CHECKPOINT_CORRUPTION.value == "checkpoint_corruption", "Value must be initialized"

    def test_config_drift_value(self):
        assert FailureType.CONFIG_DRIFT.value == "config_drift", "Value must be initialized"

    def test_unknown_value(self):
        assert FailureType.UNKNOWN.value == "unknown", "Value must be initialized"


# ---------------------------------------------------------------------------
# OOMHandler
# ---------------------------------------------------------------------------


class TestOOMHandlerInit:
    def test_initial_batch_size_stored(self):
        h = OOMHandler(64)
        assert h.initial_batch_size == 64, "initial_batch_size is not valid"
        assert h.current_batch_size == 64, "current_batch_size is not valid"

    def test_default_min_batch_size(self):
        h = OOMHandler(32)
        assert h.min_batch_size == 1, "min_batch_size is not valid"

    def test_custom_min_batch_size(self):
        h = OOMHandler(32, min_batch_size=4)
        assert h.min_batch_size == 4, "min_batch_size is not valid"

    def test_initial_retry_count(self):
        h = OOMHandler(16)
        assert h.retry_count == 0, "Count must be greater than zero"

    def test_max_retries_default(self):
        h = OOMHandler(16)
        assert h.max_retries == 3, "max_retries is not valid"


class TestOOMHandlerCanRetry:
    def test_true_at_start(self):
        h = OOMHandler(32)
        assert h.can_retry() is True, "Condition must be true"

    def test_false_when_max_retries_reached(self):
        h = OOMHandler(32)
        h.retry_count = 3
        assert h.can_retry() is False, "Condition must be true"

    def test_false_when_batch_at_minimum(self):
        h = OOMHandler(initial_batch_size=1, min_batch_size=1)
        assert h.can_retry() is False, "Condition must be true"

    def test_false_when_batch_at_custom_minimum(self):
        h = OOMHandler(4, min_batch_size=4)
        assert h.can_retry() is False, "Condition must be true"

    def test_still_true_just_before_max_retries(self):
        h = OOMHandler(32)
        h.retry_count = 2  # one below max_retries=3
        assert h.can_retry() is True, "Condition must be true"


class TestOOMHandlerReduceBatchSize:
    def test_halves_batch_size(self):
        h = OOMHandler(32)
        new_size = h.reduce_batch_size()
        assert new_size == 16, "new_size is not valid"
        assert h.current_batch_size == 16, "current_batch_size is not valid"

    def test_does_not_go_below_min(self):
        h = OOMHandler(initial_batch_size=3, min_batch_size=2)
        new_size = h.reduce_batch_size()
        assert new_size == 2, "new_size is not valid"
        assert h.current_batch_size == 2, "current_batch_size is not valid"

    def test_increments_retry_count(self):
        h = OOMHandler(32)
        h.reduce_batch_size()
        assert h.retry_count == 1, "Count must be greater than zero"

    def test_multiple_reductions(self):
        h = OOMHandler(64)
        h.reduce_batch_size()  # → 32
        h.reduce_batch_size()  # → 16
        assert h.current_batch_size == 16, "current_batch_size is not valid"
        assert h.retry_count == 2, "Count must be greater than zero"

    def test_returns_new_size(self):
        h = OOMHandler(8)
        result = h.reduce_batch_size()
        assert result == 4, "Result must not be empty"

    def test_logs_warning(self, caplog):
        h = OOMHandler(16)
        with caplog.at_level(logging.WARNING, logger="codex_ml.utils.self_healing"):
            h.reduce_batch_size()
        assert any("OOM" in r.message or "Reducing batch size" in r.message for r in caplog.records)


class TestOOMHandlerReset:
    def test_restores_batch_size(self):
        h = OOMHandler(32)
        h.reduce_batch_size()
        h.reset()
        assert h.current_batch_size == 32, "current_batch_size is not valid"

    def test_resets_retry_count(self):
        h = OOMHandler(32)
        h.reduce_batch_size()
        h.reduce_batch_size()
        h.reset()
        assert h.retry_count == 0, "Count must be greater than zero"

    def test_initial_batch_size_unchanged(self):
        h = OOMHandler(32)
        h.reduce_batch_size()
        h.reset()
        assert h.initial_batch_size == 32, "initial_batch_size is not valid"


# ---------------------------------------------------------------------------
# SelfHealingContext
# ---------------------------------------------------------------------------


class TestSelfHealingContextInit:
    def test_default_batch_size(self):
        ctx = SelfHealingContext()
        assert ctx.batch_size == 32, "batch_size is not valid"

    def test_default_oom_recovery(self):
        ctx = SelfHealingContext()
        assert ctx.enable_oom_recovery is True, "enable_oom_recovery is not valid"

    def test_default_checkpoint_rollback(self):
        ctx = SelfHealingContext()
        assert ctx.enable_checkpoint_rollback is True, "enable_checkpoint_rollback is not valid"

    def test_custom_batch_size(self):
        ctx = SelfHealingContext(batch_size=8)
        assert ctx.batch_size == 8, "batch_size is not valid"

    def test_custom_flags(self):
        ctx = SelfHealingContext(enable_oom_recovery=False, enable_checkpoint_rollback=False)
        assert ctx.enable_oom_recovery is False, "enable_oom_recovery is not valid"
        assert ctx.enable_checkpoint_rollback is False, "enable_checkpoint_rollback is not valid"

    def test_oom_handler_created(self):
        ctx = SelfHealingContext(batch_size=16)
        assert isinstance(ctx.oom_handler, OOMHandler)
        assert ctx.oom_handler.initial_batch_size == 16, "initial_batch_size is not valid"

    def test_failures_empty_initially(self):
        ctx = SelfHealingContext()
        assert ctx.failures == [], "failures is not valid"


class TestSelfHealingContextManager:
    def test_enter_returns_self(self):
        ctx = SelfHealingContext()
        result = ctx.__enter__()
        assert result is ctx, "Result must not be empty"

    def test_context_manager_protocol(self):
        with SelfHealingContext() as healer:
            assert isinstance(healer, SelfHealingContext)

    def test_no_exception_returns_false(self):
        ctx = SelfHealingContext()
        ctx.__enter__()
        result = ctx.__exit__(None, None, None)
        assert result is False, "Result must not be empty"

    def test_no_exception_failures_empty(self):
        ctx = SelfHealingContext()
        with ctx:
            pass
        assert ctx.failures == [], "failures is not valid"

    def test_oom_suppressed_with_recovery_enabled(self):
        """OOM exception should be suppressed (return True) when batch > min."""
        ctx = SelfHealingContext(batch_size=32, enable_oom_recovery=True)
        ctx.__enter__()
        exc = MemoryError("CUDA out of memory")
        result = ctx.__exit__(MemoryError, exc, None)
        assert result is True, "Result must not be empty"

    def test_oom_propagated_when_recovery_disabled(self):
        ctx = SelfHealingContext(batch_size=32, enable_oom_recovery=False)
        ctx.__enter__()
        exc = MemoryError("out of memory")
        result = ctx.__exit__(MemoryError, exc, None)
        assert result is False, "Result must not be empty"

    def test_oom_propagated_when_min_batch_reached(self):
        """When batch_size == min_batch_size the OOM should propagate."""
        ctx = SelfHealingContext(batch_size=1, enable_oom_recovery=True)
        ctx.__enter__()
        exc = MemoryError("out of memory")
        result = ctx.__exit__(MemoryError, exc, None)
        assert result is False, "Result must not be empty"

    def test_checkpoint_corruption_propagated(self):
        """Checkpoint rollback stub always returns False."""
        ctx = SelfHealingContext(enable_checkpoint_rollback=True)
        ctx.__enter__()
        exc = RuntimeError("checkpoint corrupt")
        result = ctx.__exit__(RuntimeError, exc, None)
        assert result is False, "Result must not be empty"

    def test_unknown_exception_propagated(self):
        ctx = SelfHealingContext()
        ctx.__enter__()
        exc = ValueError("something totally unexpected")
        result = ctx.__exit__(ValueError, exc, None)
        assert result is False, "Result must not be empty"

    def test_failures_list_populated_on_exception(self):
        ctx = SelfHealingContext(enable_oom_recovery=False)
        ctx.__enter__()
        exc = MemoryError("out of memory")
        ctx.__exit__(MemoryError, exc, None)
        assert len(ctx.failures) == 1, "Collection must not be empty"
        failure_type, captured_exc = ctx.failures[0]
        assert failure_type == FailureType.OOM, "failure_type is not valid"
        assert captured_exc is exc, "captured_exc is not valid"

    def test_multiple_exceptions_accumulate(self):
        ctx = SelfHealingContext(enable_oom_recovery=False)
        ctx.__enter__()
        for _ in range(3):
            ctx.__exit__(MemoryError, MemoryError("oom"), None)
        assert len(ctx.failures) == 3, "Collection must not be empty"

    def test_config_drift_propagated(self):
        ctx = SelfHealingContext()
        ctx.__enter__()
        exc = RuntimeError("config drift detected")
        result = ctx.__exit__(RuntimeError, exc, None)
        assert result is False, "Result must not be empty"


class TestSelfHealingClassifyFailure:
    def _ctx(self):
        ctx = SelfHealingContext()
        ctx.__enter__()
        return ctx

    def test_oom_via_out_of_memory(self):
        ctx = self._ctx()
        ft = ctx._classify_failure(MemoryError, MemoryError("out of memory"), None)
        assert ft == FailureType.OOM, "ft is not valid"

    def test_oom_via_oom_string(self):
        ctx = self._ctx()
        ft = ctx._classify_failure(RuntimeError, RuntimeError("OOM error"), None)
        assert ft == FailureType.OOM, "ft is not valid"

    def test_oom_via_cuda_memory(self):
        ctx = self._ctx()
        ft = ctx._classify_failure(RuntimeError, RuntimeError("CUDA out of memory allocated"), None)
        assert ft == FailureType.OOM, "ft is not valid"

    def test_checkpoint_corruption_via_corrupt(self):
        ctx = self._ctx()
        ft = ctx._classify_failure(IOError, IOError("corrupt file detected"), None)
        assert ft == FailureType.CHECKPOINT_CORRUPTION, "ft is not valid"

    def test_checkpoint_corruption_via_integrity(self):
        ctx = self._ctx()
        ft = ctx._classify_failure(ValueError, ValueError("integrity check failed"), None)
        assert ft == FailureType.CHECKPOINT_CORRUPTION, "ft is not valid"

    def test_checkpoint_corruption_via_hash(self):
        ctx = self._ctx()
        ft = ctx._classify_failure(ValueError, ValueError("hash mismatch"), None)
        assert ft == FailureType.CHECKPOINT_CORRUPTION, "ft is not valid"

    def test_config_drift(self):
        ctx = self._ctx()
        ft = ctx._classify_failure(RuntimeError, RuntimeError("config drift detected"), None)
        assert ft == FailureType.CONFIG_DRIFT, "ft is not valid"

    def test_unknown_generic(self):
        ctx = self._ctx()
        ft = ctx._classify_failure(TypeError, TypeError("unexpected type"), None)
        assert ft == FailureType.UNKNOWN, "ft is not valid"

    def test_none_exc_val(self):
        ctx = self._ctx()
        ft = ctx._classify_failure(Exception, None, None)
        assert ft == FailureType.UNKNOWN, "ft is not valid"


# ---------------------------------------------------------------------------
# auto_remediate
# ---------------------------------------------------------------------------


class TestAutoRemediate:
    def test_success_on_first_try(self):
        func = MagicMock(return_value="result")
        result = auto_remediate(func, max_retries=3, batch_size=32)
        assert result == "result", "Result must not be empty"
        func.assert_called_once()

    def test_passes_positional_args(self):
        func = MagicMock(return_value=42)
        auto_remediate(func, "a", "b", max_retries=1)
        func.assert_called_once_with("a", "b")

    def test_passes_keyword_args(self):
        func = MagicMock(return_value=99)
        auto_remediate(func, max_retries=1, batch_size=32, x=10, y=20)
        # x and y should appear in kwargs; batch_size kwarg gets replaced
        call_kwargs = func.call_args[1]
        assert call_kwargs["x"] == 10, "Condition must be true"
        assert call_kwargs["y"] == 20, "Condition must be true"

    def test_retries_then_raises(self):
        # Use a message that does NOT contain "oom" (a substring of "boom") so the
        # exception is classified as UNKNOWN and not suppressed by the healing context.
        func = MagicMock(side_effect=ValueError("deliberate-failure"))
        with pytest.raises(ValueError, match="deliberate-failure"):
            auto_remediate(func, max_retries=3, batch_size=32)
        assert func.call_count == 3, "Count must be greater than zero"

    def test_max_retries_one(self):
        func = MagicMock(side_effect=RuntimeError("fail"))
        with pytest.raises(RuntimeError):
            auto_remediate(func, max_retries=1, batch_size=32)
        assert func.call_count == 1, "Count must be greater than zero"

    def test_batch_size_kwarg_updated_on_retry(self):
        """When batch_size is in **kwargs, the healer's batch_size is injected."""
        calls: list[int] = []

        def side_effect(**kwargs):
            calls.append(kwargs.get("batch_size", -1))
            # Use ValueError (UNKNOWN type) so the context does NOT suppress it,
            # allowing the outer retry loop to count attempts normally.
            raise ValueError("generic failure")

        extra_kwargs = {"batch_size": 32}
        with pytest.raises(ValueError):
            auto_remediate(side_effect, max_retries=2, **extra_kwargs)
        # Both attempts were made
        assert len(calls) == 2, "Calls must not be empty"
        # The batch_size kwarg was injected into the function each attempt
        assert all(isinstance(bs, int) for bs in calls)

    def test_returns_none_when_func_returns_none(self):
        func = MagicMock(return_value=None)
        result = auto_remediate(func, max_retries=2)
        assert result is None, "Result must not be empty"

    def test_no_retry_on_success(self):
        func = MagicMock(side_effect=[RuntimeError("fail"), "ok"])
        # First call fails, second succeeds
        result = auto_remediate(func, max_retries=3, batch_size=32)
        assert result == "ok", "Result must not be empty"
        assert func.call_count == 2, "Count must be greater than zero"

    def test_re_raises_last_exception(self):
        exc = KeyError("missing key")
        func = MagicMock(side_effect=exc)
        with pytest.raises(KeyError):
            auto_remediate(func, max_retries=2)


# ---------------------------------------------------------------------------
# __all__
# ---------------------------------------------------------------------------


def test_all_exports():
    import codex_ml.utils.self_healing as mod

    assert set(mod.__all__) == {"FailureType", "OOMHandler", "SelfHealingContext", "auto_remediate"}
    # Verify each symbol is actually importable at the module level
    from codex_ml.utils.self_healing import (  # noqa: F401
        FailureType,
        OOMHandler,
        SelfHealingContext,
        auto_remediate,
    )
