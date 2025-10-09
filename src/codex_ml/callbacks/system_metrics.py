"""System metrics callback for optional CPU/GPU sampling."""

from __future__ import annotations

from typing import Any, Dict, Optional

from codex_ml.callbacks import Callback


def _psutil_snapshot() -> Dict[str, Any]:
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


def _nvml_snapshot() -> Dict[str, Any]:
    try:
        import pynvml  # type: ignore
    except Exception:  # pragma: no cover - optional dependency
        return {}

    snapshot: Dict[str, Any] = {}
    try:
        pynvml.nvmlInit()
        count = pynvml.nvmlDeviceGetCount()
        gpu_utils: list[float] = []
        gpu_mem: list[float] = []
        for idx in range(count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
            utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
            memory = pynvml.nvmlDeviceGetMemoryInfo(handle)
            gpu_utils.append(float(utilization.gpu))
            gpu_mem.append(round(memory.used / (1024**3), 3))
        if gpu_utils:
            snapshot["sys.gpu.util"] = sum(gpu_utils) / len(gpu_utils)
        if gpu_mem:
            snapshot["sys.gpu.mem_gb"] = sum(gpu_mem)
    finally:
        try:
            pynvml.nvmlShutdown()
        except Exception:
            pass
    return snapshot


class SystemMetricsCallback(Callback):
    """Collect basic system metrics at the end of each epoch."""

    def __init__(self) -> None:
        super().__init__(name="SystemMetrics")

    def on_epoch_end(
        self,
        epoch: int,
        metrics: Dict[str, Any],
        state: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        snapshot: Dict[str, Any] = {}
        snapshot.update(_psutil_snapshot())
        snapshot.update(_nvml_snapshot())
        if snapshot:
            metrics.update(snapshot)
        return None
