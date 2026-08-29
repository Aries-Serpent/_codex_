# SPDX-License-Identifier: Apache-2.0
"""Lightweight, offline-safe system sampling helpers (psutil/NVML guarded)."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import datetime as _dt  # noqa: E402
from typing import Any  # noqa: E402

__all__ = ["get_gpu_stats", "get_proc_stats", "get_sys_stats", "sample"]

# ----- optional deps (never hard-crash) ---------------------------------------
try:  # psutil for CPU/RAM (process + system)
    import psutil as _psutil
except (ImportError, AttributeError):  # pragma: no cover
    _psutil = None

try:  # NVML for GPU stats via pynvml / nvidia-ml-py3
    from pynvml import (
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
except (IOError, OSError):  # pragma: no cover
    nvmlInit = nvmlShutdown = nvmlDeviceGetCount = None
    nvmlDeviceGetHandleByIndex = nvmlDeviceGetName = None
    nvmlDeviceGetUtilizationRates = nvmlDeviceGetMemoryInfo = None
    nvmlDeviceGetTemperature = NVML_TEMPERATURE_GPU = None
    NVMLError = Exception

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
    except (IOError, OSError):
        logger.warning("Exception occurred", exc_info=True)
        return False


def _shutdown_nvml() -> None:
    global _NVML_READY
    if _NVML_READY and nvmlShutdown is not None:
        try:
            nvmlShutdown()
        finally:
            _NVML_READY = False


def get_proc_stats() -> dict[str, Any]:
    """Returns process CPU% and RSS (MB). Missing psutil -> {}."""
    if _psutil is None:
        return {}
    try:
        p = _psutil.Process()
        cpu_pct = p.cpu_percent(interval=None)
        rss_mb = p.memory_info().rss / (1024 * 1024)
        return {"cpu_pct": float(cpu_pct), "rss_mb": float(rss_mb)}
    except (ValueError, TypeError, RuntimeError):
        logger.warning("Exception occurred", exc_info=True)
        return {}


def get_sys_stats() -> dict[str, Any]:
    """Returns system CPU% and memory%. Missing psutil -> {}."""
    if _psutil is None:
        return {}
    try:
        cpu_pct = _psutil.cpu_percent(interval=None)
        mem_pct = _psutil.virtual_memory().percent
        return {"cpu_pct": float(cpu_pct), "mem_pct": float(mem_pct)}
    except (ValueError, TypeError, RuntimeError):
        logger.warning("Exception occurred", exc_info=True)
        return {}


def get_gpu_stats() -> list[dict[str, Any]]:
    """Per-GPU: name, util%, mem_used_mb, mem_total_mb, temp_c. Missing NVML -> []."""
    if not _ensure_nvml():
        return []
    try:
        count = nvmlDeviceGetCount()
        out: list[dict[str, Any]] = []
        for i in range(int(count)):
            h = nvmlDeviceGetHandleByIndex(i)
            name = nvmlDeviceGetName(h)
            try:
                util = nvmlDeviceGetUtilizationRates(h)
                util_pct = float(getattr(util, "gpu", 0.0))
            except NVMLError as e:
                type(e).__name__
                logger.debug("NVMLError: <ERROR_TYPE>")
                logger.warning("NVMLError: <ERROR_TYPE>", exc_info=True)
                util_pct = 0.0
            try:
                mem = nvmlDeviceGetMemoryInfo(h)
                mem_used_mb = float(mem.used) / (1024 * 1024)
                mem_total_mb = float(mem.total) / (1024 * 1024)
            except NVMLError as e:
                type(e).__name__
                logger.debug("NVMLError: <ERROR_TYPE>")
                logger.warning("NVMLError: <ERROR_TYPE>", exc_info=True)
                mem_used_mb = mem_total_mb = 0.0
            try:
                temp_c = float(nvmlDeviceGetTemperature(h, NVML_TEMPERATURE_GPU))
            except NVMLError as e:
                type(e).__name__
                logger.debug("NVMLError: <ERROR_TYPE>")
                logger.warning("NVMLError: <ERROR_TYPE>", exc_info=True)
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
    except (ValueError, TypeError, RuntimeError):
        logger.warning("Exception occurred", exc_info=True)
        return []
    finally:
        # Keep NVML initialized to amortize cost; process exit will clean up.
        pass


def sample() -> dict[str, Any]:
    """One-shot snapshot; never raises."""
    ts = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")
    return {
        "ts": ts,
        "proc": get_proc_stats(),
        "sys": get_sys_stats(),
        "gpu": get_gpu_stats(),
    }


# WHY: Minimal observability for local/offline runs.
# RISK: None; optional deps guarded.
# TEST: see tests/test_microhelpers.py
