from __future__ import annotations

import types

from codex_ml.monitoring import codex_logging


class _DummyNVML:
    def nvmlInit(self):
        pass

    def nvmlShutdown(self):
        pass

    def nvmlDeviceGetCount(self):
        return 2

    def nvmlDeviceGetHandleByIndex(self, i):
        return i

    def nvmlDeviceGetUtilizationRates(self, handle):
        return types.SimpleNamespace(gpu=50)

    def nvmlDeviceGetMemoryInfo(self, handle):
        return types.SimpleNamespace(used=1000, total=2000)

    def nvmlDeviceGetTemperature(self, handle, which):
        return 60

    def nvmlDeviceGetPowerUsage(self, handle):
        return 1000


def test_sampler_multi_gpu(monkeypatch):
    dummy = _DummyNVML()
    monkeypatch.setattr(codex_logging, "pynvml", dummy)
    metrics = codex_logging._codex_sample_system()
    assert "gpus" in metrics
    assert len(metrics["gpus"]) == 2
    assert metrics["gpu_util_mean"] == 50
