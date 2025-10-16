"""System metrics callback for optional CPU/GPU sampling."""

from __future__ import annotations

from contextlib import suppress
from typing import Any

from codex_ml.callbacks import Callback

try:  # pragma: no cover - optional dependency import
    import pynvml  # type: ignore[import-not-found]

    _NVML_AVAILABLE = True
except Exception:  # pragma: no cover - optional dependency
    pynvml = None  # type: ignore[assignment]
    _NVML_AVAILABLE = False


def _psutil_snapshot() -> dict[str, Any]:
    try:
        import psutil  # type: ignore
    except Exception:  # pragma: no cover - optional dependency
        return {}

    cpu = psutil.cpu_percent(interval=None)
    vm = psutil.virtual_memory()
    return {
        "sys.cpu": cpu,
        "sys.ram_gb": round(vm.used / (1024**3), 3),
    }


def _nvml_snapshot() -> dict[str, Any]:
    fallback: dict[str, Any] = {"gpu0_util": 0.0, "gpu0_mem": 0.0}
    if not _NVML_AVAILABLE or pynvml is None:
        # Provide deterministic keys so downstream dashboards remain stable on CPU-only hosts.
        return fallback.copy()

    snapshot: dict[str, Any] = {}
    initialized = False
    try:
        pynvml.nvmlInit()
        initialized = True
        count = pynvml.nvmlDeviceGetCount()
        for idx in range(count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
            utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
            memory = pynvml.nvmlDeviceGetMemoryInfo(handle)
            snapshot[f"gpu{idx}_util"] = float(utilization.gpu)
            snapshot[f"gpu{idx}_mem"] = round(memory.used / (1024**3), 3)
    except Exception:  # pragma: no cover - optional dependency
        return fallback.copy()
    finally:
        if initialized:
            with suppress(Exception):
                pynvml.nvmlShutdown()
    if not snapshot:
        snapshot.update(fallback)
    return snapshot


class SystemMetricsCallback(Callback):
    """Collect basic system metrics at the end of each epoch."""

    def __init__(self) -> None:
        super().__init__(name="SystemMetrics")

    def on_epoch_end(
        self,
        epoch: int,
        metrics: dict[str, Any],
        state: dict[str, Any],
    ) -> dict[str, Any] | None:
        snapshot: dict[str, Any] = {}
        snapshot.update(_psutil_snapshot())
        snapshot.update(_nvml_snapshot())
        if snapshot:
            metrics.update(snapshot)
        return None
