# SPDX-License-Identifier: Apache-2.0
"""Lightweight, offline-safe system sampling helpers (psutil/NVML guarded)."""

from __future__ import annotations

import datetime as _dt
from typing import Any, Dict, List

__all__ = ["sample", "get_proc_stats", "get_sys_stats", "get_gpu_stats"]

# ----- optional deps (never hard-crash) ---------------------------------------
try:  # psutil for CPU/RAM (process + system)
    import psutil as _psutil  # type: ignore
except Exception:  # pragma: no cover
    _psutil = None  # type: ignore

try:  # NVML for GPU stats via pynvml / nvidia-ml-py3
    from pynvml import (  # type: ignore
        NVML_TEMPERATURE_GPU,
        NVMLError,
        nvmlDeviceGetCount,
        nvmlDeviceGetHandleByIndex,
        nvmlDeviceGetMemoryInfo,
        nvmlDeviceGetName,
        nvmlDeviceGetTemperature,
        nvmlDeviceGetUtilizationRates,
        nvmlInit,
        nvmlShutdown,
    )
except Exception:  # pragma: no cover
    nvmlInit = nvmlShutdown = nvmlDeviceGetCount = None  # type: ignore
    nvmlDeviceGetHandleByIndex = nvmlDeviceGetName = None  # type: ignore
    nvmlDeviceGetUtilizationRates = nvmlDeviceGetMemoryInfo = None  # type: ignore
    nvmlDeviceGetTemperature = NVML_TEMPERATURE_GPU = None  # type: ignore
    NVMLError = Exception  # type: ignore

_NVML_READY = False


def _ensure_nvml() -> bool:
    global _NVML_READY
    if nvmlInit is None:
        return False
    if _NVML_READY:
        return True
    try:
        nvmlInit()
        _NVML_READY = True
        return True
    except Exception:
        return False


def _shutdown_nvml() -> None:
    global _NVML_READY
    if _NVML_READY and nvmlShutdown is not None:
        try:
            nvmlShutdown()
        finally:
            _NVML_READY = False


def get_proc_stats() -> Dict[str, Any]:
    """Returns process CPU% and RSS (MB). Missing psutil -> {}."""
    if _psutil is None:
        return {}
    try:
        p = _psutil.Process()
        cpu_pct = p.cpu_percent(interval=None)
        rss_mb = p.memory_info().rss / (1024 * 1024)
        return {"cpu_pct": float(cpu_pct), "rss_mb": float(rss_mb)}
    except Exception:
        return {}


def get_sys_stats() -> Dict[str, Any]:
    """Returns system CPU% and memory%. Missing psutil -> {}."""
    if _psutil is None:
        return {}
    try:
        cpu_pct = _psutil.cpu_percent(interval=None)
        mem_pct = _psutil.virtual_memory().percent
        return {"cpu_pct": float(cpu_pct), "mem_pct": float(mem_pct)}
    except Exception:
        return {}


def get_gpu_stats() -> List[Dict[str, Any]]:
    """Per-GPU: name, util%, mem_used_mb, mem_total_mb, temp_c. Missing NVML -> []."""
    if not _ensure_nvml():
        return []
    try:
        count = nvmlDeviceGetCount()  # type: ignore
        out: List[Dict[str, Any]] = []
        for i in range(int(count)):
            h = nvmlDeviceGetHandleByIndex(i)  # type: ignore
            name = nvmlDeviceGetName(h)  # type: ignore
            try:
                util = nvmlDeviceGetUtilizationRates(h)  # type: ignore
                util_pct = float(getattr(util, "gpu", 0.0))
            except NVMLError:  # type: ignore
                util_pct = 0.0
            try:
                mem = nvmlDeviceGetMemoryInfo(h)  # type: ignore
                mem_used_mb = float(mem.used) / (1024 * 1024)
                mem_total_mb = float(mem.total) / (1024 * 1024)
            except NVMLError:  # type: ignore
                mem_used_mb = mem_total_mb = 0.0
            try:
                temp_c = float(nvmlDeviceGetTemperature(h, NVML_TEMPERATURE_GPU))  # type: ignore
            except NVMLError:  # type: ignore
                temp_c = 0.0
            out.append(
                {
                    "name": name.decode() if isinstance(name, (bytes, bytearray)) else str(name),
                    "util_pct": util_pct,
                    "mem_used_mb": mem_used_mb,
                    "mem_total_mb": mem_total_mb,
                    "temp_c": temp_c,
                }
            )
        return out
    except Exception:
        return []
    finally:
        # Keep NVML initialized to amortize cost; process exit will clean up.
        pass


def sample() -> Dict[str, Any]:
    """One-shot snapshot; never raises."""
    ts = _dt.datetime.now().astimezone().isoformat(timespec="seconds")
    return {"ts": ts, "proc": get_proc_stats(), "sys": get_sys_stats(), "gpu": get_gpu_stats()}


# WHY: Minimal observability for local/offline runs.
# RISK: None; optional deps guarded.
# TEST: see tests/test_microhelpers.py
