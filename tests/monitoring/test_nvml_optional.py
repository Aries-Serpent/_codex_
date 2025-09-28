from __future__ import annotations

from numbers import Number

import pytest

try:
    import pynvml as _pynvml  # type: ignore
    _HAS_NVML = True
except Exception:
    _HAS_NVML = False

from codex_ml.monitoring.microhelpers import get_gpu_stats


def test_nvml_absent_graceful(monkeypatch):
    # Force module-level symbols to None so we exercise the fallback
    import codex_ml.monitoring.microhelpers as mh

    for name in [
        "nvmlInit",
        "nvmlShutdown",
        "nvmlDeviceGetCount",
        "nvmlDeviceGetHandleByIndex",
        "nvmlDeviceGetName",
        "nvmlDeviceGetUtilizationRates",
        "nvmlDeviceGetMemoryInfo",
        "nvmlDeviceGetTemperature",
        "NVML_TEMPERATURE_GPU",
        "NVMLError",
    ]:
        monkeypatch.setitem(mh.__dict__, name, None)
    g = get_gpu_stats()
    assert isinstance(g, list)


@pytest.mark.skipif(not _HAS_NVML, reason="pynvml not installed")
def test_nvml_present_has_numeric_fields():
    g = get_gpu_stats()
    # Not asserting non-empty; on CPU hosts this may be empty.
    for entry in g:
        for k in ("util_pct", "mem_used_mb", "mem_total_mb", "temp_c"):
            v = entry.get(k)
            if v is not None:
                assert isinstance(v, Number)

