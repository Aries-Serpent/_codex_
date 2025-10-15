from __future__ import annotations

import importlib
import sys


def test_nvml_missing_fallback() -> None:
    sys.modules.pop("pynvml", None)
    sys.modules.pop("codex_ml.callbacks.system_metrics", None)
    module = importlib.import_module("codex_ml.callbacks.system_metrics")
    callback = module.SystemMetricsCallback()
    metrics: dict[str, float] = {}
    callback.on_epoch_end(epoch=0, metrics=metrics, state={})
    assert "gpu0_util" in metrics
    assert "gpu0_mem" in metrics
    assert isinstance(metrics["gpu0_util"], int | float)
    assert isinstance(metrics["gpu0_mem"], int | float)
