"""Lightweight system metrics collection utilities."""

from __future__ import annotations

import logging

LOGGER = logging.getLogger(__name__)

try:  # pragma: no cover - optional dependency
    import psutil  # type: ignore
except Exception:  # pragma: no cover - optional dependency may be absent
    psutil = None  # type: ignore[assignment]

try:  # pragma: no cover - optional dependency
    import pynvml  # type: ignore
except Exception:  # pragma: no cover - optional dependency may be absent
    pynvml = None  # type: ignore[assignment]
else:  # pragma: no cover - NVML initialisation best effort
    try:
        pynvml.nvmlInit()
    except Exception:  # pragma: no cover - unavailable runtime
        LOGGER.debug("NVML initialisation failed", exc_info=True)
        pynvml = None  # type: ignore[assignment]


def collect_metrics() -> dict[str, float]:
    """Collect CPU, memory and GPU utilisation metrics.

    Missing optional dependencies are handled gracefully by returning an
    empty mapping. Metric keys are prefixed according to their origin to
    avoid collisions with training metrics.
    """

    metrics: dict[str, float] = {}

    if psutil is not None:
        try:
            metrics["cpu_percent"] = float(psutil.cpu_percent(interval=None))
            memory = psutil.virtual_memory()
            metrics["mem_used_mb"] = float(memory.used) / 1024.0 / 1024.0
            metrics["mem_available_mb"] = float(memory.available) / 1024.0 / 1024.0
        except Exception:  # pragma: no cover - psutil runtime errors best effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            device_count = pynvml.nvmlDeviceGetCount()
        except Exception:  # pragma: no cover - NVML failure
            LOGGER.debug("NVML device enumeration failed", exc_info=True)
        else:
            for index in range(device_count):
                try:
                    handle = pynvml.nvmlDeviceGetHandleByIndex(index)
                    utilisation = pynvml.nvmlDeviceGetUtilizationRates(handle)
                    memory = pynvml.nvmlDeviceGetMemoryInfo(handle)
                except Exception:  # pragma: no cover - per-device failure best effort
                    LOGGER.debug("NVML metrics failed for device %s", index, exc_info=True)
                    continue
                metrics[f"gpu{index}_util_percent"] = float(utilisation.gpu)
                metrics[f"gpu{index}_mem_used_mb"] = float(memory.used) / 1024.0 / 1024.0
                metrics[f"gpu{index}_mem_total_mb"] = float(memory.total) / 1024.0 / 1024.0

    return metrics
