"""Tests for default callback wiring in unified training."""

from __future__ import annotations

from codex_ml.callbacks.base import Callback
from codex_ml.training import unified_training


class SpyCallback(Callback):
    def __init__(self) -> None:
        super().__init__(name="SpyCallback")
        self.state_reference = None

    def on_epoch_end(self, epoch, metrics, state):
        del epoch, metrics
        self.state_reference = state


def test_default_callbacks_auto_added() -> None:
    cfg = unified_training.UnifiedTrainingConfig(model_name="dummy", epochs=1)
    spy = SpyCallback()
    _ = unified_training.run_unified_training(cfg, callbacks=[spy])
    assert spy.state_reference is not None, "Training did not produce state"
    history = spy.state_reference.get("epoch_history")
    assert isinstance(history, list) and history, "epoch_history not present or empty"
    assert (
        "epoch" in history[0] and "status" in history[0]
    ), "LoggingCallback did not log expected metrics"


def test_disable_default_callbacks() -> None:
    cfg = unified_training.UnifiedTrainingConfig(
        model_name="dummy",
        epochs=1,
        enable_eval_callback=False,
        enable_logging_callback=False,
    )
    spy = SpyCallback()
    _ = unified_training.run_unified_training(cfg, callbacks=[spy])
    assert spy.state_reference is not None
    assert (
        "epoch_history" not in spy.state_reference
    ), "LoggingCallback was added despite disable flag"
