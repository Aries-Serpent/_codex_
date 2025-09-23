"""Utilities for logging host-level system metrics during offline runs."""

from __future__ import annotations

import atexit
import json
import logging
import os
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Set, Tuple

logger = logging.getLogger(__name__)
_IS_DARWIN = sys.platform.startswith("darwin")


def _env_flag(name: str, default: bool = True) -> bool:
    """Return ``True`` when environment variable ``name`` is truthy."""

    raw = os.getenv(name)
    if raw is None:
        return default
    raw = raw.strip().lower()
    if not raw:
        return default
    return raw in {"1", "true", "yes", "on"}


DEFAULT_ENABLE_PSUTIL = _env_flag("CODEX_MONITORING_ENABLE_PSUTIL", True)
_DEFAULT_ENABLE_NVML_FLAG = _env_flag("CODEX_MONITORING_ENABLE_NVML", True)
DEFAULT_DISABLE_NVML = _env_flag("CODEX_DISABLE_NVML", False)
DEFAULT_ENABLE_NVML = _DEFAULT_ENABLE_NVML_FLAG and not DEFAULT_DISABLE_NVML
DEFAULT_ENABLE_GPU = _env_flag("CODEX_MONITORING_ENABLE_GPU", False)
DEFAULT_POLL_GPU = DEFAULT_ENABLE_GPU and not _env_flag("CODEX_MONITORING_DISABLE_GPU", False)
DEFAULT_NVML_REQUESTED = DEFAULT_POLL_GPU and _DEFAULT_ENABLE_NVML_FLAG and not DEFAULT_DISABLE_NVML


try:  # pragma: no cover - optional dependency
    if DEFAULT_ENABLE_PSUTIL:
        import psutil  # type: ignore
    else:  # pragma: no cover - controlled via feature flag
        psutil = None  # type: ignore[assignment]
except Exception as exc:  # pragma: no cover - psutil missing
    logger.warning(
        "psutil import failed; falling back to minimal sampler",
        extra={
            "event": "system_metrics.dependency_missing",
            "dependency": "psutil",
            "error": repr(exc),
        },
    )
    psutil = None  # type: ignore[assignment]


try:  # pragma: no cover - optional dependency
    if DEFAULT_POLL_GPU and DEFAULT_ENABLE_NVML:
        import pynvml  # type: ignore
    else:  # pragma: no cover - GPU polling disabled via feature flag
        pynvml = None  # type: ignore[assignment]
except Exception as exc:  # pragma: no cover - pynvml missing
    logger.warning(
        "pynvml import failed; GPU metrics disabled",
        extra={
            "event": "system_metrics.dependency_missing",
            "dependency": "pynvml",
            "error": repr(exc),
        },
    )
    pynvml = None  # type: ignore[assignment]


try:  # pragma: no cover - optional dependency
    import resource  # type: ignore
except Exception:  # pragma: no cover - platform dependent
    resource = None  # type: ignore[assignment]


HAS_PSUTIL = "psutil" in globals() and psutil is not None
HAS_NVML = "pynvml" in globals() and pynvml is not None


@dataclass
class SystemMetricsConfig:
    """Runtime configuration for system metrics sampling."""

    use_psutil: bool = DEFAULT_ENABLE_PSUTIL and HAS_PSUTIL
    poll_gpu: bool = DEFAULT_POLL_GPU
    use_nvml: bool = DEFAULT_ENABLE_NVML and HAS_NVML and DEFAULT_POLL_GPU


_CONFIG = SystemMetricsConfig()
SYSTEM_METRICS_DEGRADED = not _CONFIG.use_psutil


_PSUTIL_REQUESTED = DEFAULT_ENABLE_PSUTIL
_NVML_REQUESTED = DEFAULT_NVML_REQUESTED
_NVML_FEATURE_DISABLED = DEFAULT_DISABLE_NVML


def configure_system_metrics(
    *,
    use_psutil: Optional[bool] = None,
    poll_gpu: Optional[bool] = None,
    use_nvml: Optional[bool] = None,
) -> None:
    """Update runtime system metrics configuration."""

    global _NVML_DISABLED, _PSUTIL_REQUESTED, _NVML_REQUESTED

    if use_psutil is not None:
        _PSUTIL_REQUESTED = bool(use_psutil)
        _CONFIG.use_psutil = bool(use_psutil) and _psutil_available()
    if poll_gpu is not None:
        _CONFIG.poll_gpu = bool(poll_gpu)
        if not _CONFIG.poll_gpu:
            _CONFIG.use_nvml = False
            _NVML_REQUESTED = False
        elif use_nvml is None and not _NVML_FEATURE_DISABLED:
            _NVML_REQUESTED = _DEFAULT_ENABLE_NVML_FLAG or _NVML_REQUESTED
    if use_nvml is not None:
        _NVML_REQUESTED = bool(use_nvml)

    if _NVML_FEATURE_DISABLED:
        _NVML_REQUESTED = False

    _CONFIG.use_nvml = (
        _CONFIG.poll_gpu and _NVML_REQUESTED and not _NVML_FEATURE_DISABLED and _nvml_available()
    )

    _NVML_DISABLED = not (_CONFIG.use_nvml and _CONFIG.poll_gpu)
    _update_degraded_flag()


def current_system_metrics_config() -> SystemMetricsConfig:
    """Return a shallow copy of the current configuration."""

    return SystemMetricsConfig(
        use_psutil=_CONFIG.use_psutil,
        poll_gpu=_CONFIG.poll_gpu,
        use_nvml=_CONFIG.use_nvml,
    )


_FALLBACK_CPU_COUNT = os.cpu_count() or 1
_FALLBACK_PROCESS_CPU_TIME: Optional[float] = None
_FALLBACK_PROCESS_TS: Optional[float] = None
_NVML_DISABLED = not _CONFIG.use_nvml
_PSUTIL_WARNING_CONTEXTS: Set[str] = set()
_NVML_WARNING_CONTEXTS: Set[str] = set()
_LOGGER_WARNING_CONTEXTS: Set[str] = set()


def _now() -> float:
    return time.time()


def _minimal_process_sample(ts: float) -> Optional[Dict[str, Any]]:
    """Return a lightweight snapshot of process metrics without psutil."""

    global _FALLBACK_PROCESS_CPU_TIME, _FALLBACK_PROCESS_TS

    proc_time = time.process_time()
    cpu_percent = None
    if _FALLBACK_PROCESS_CPU_TIME is not None and _FALLBACK_PROCESS_TS is not None:
        delta_cpu = proc_time - _FALLBACK_PROCESS_CPU_TIME
        delta_time = ts - _FALLBACK_PROCESS_TS
        if delta_time > 0:
            cpu_percent = max(
                0.0, min((delta_cpu / delta_time) * 100.0, 100.0 * _FALLBACK_CPU_COUNT)
            )

    _FALLBACK_PROCESS_CPU_TIME = proc_time
    _FALLBACK_PROCESS_TS = ts

    payload: Dict[str, Any] = {}
    if cpu_percent is not None:
        payload["cpu_percent"] = cpu_percent
    if resource is not None:
        try:
            usage = resource.getrusage(resource.RUSAGE_SELF)
            # ``ru_maxrss`` is reported in KiB on Linux and bytes on macOS; normalise to bytes when possible.
            rss = float(usage.ru_maxrss)
            if rss and not _IS_DARWIN:
                rss *= 1024.0
            payload["memory_info"] = {"rss": rss}
        except Exception:  # pragma: no cover - platform specific
            pass

    return payload or None


def _sample_cpu_minimal(ts: float) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "ts": ts,
        "cpu_count": _FALLBACK_CPU_COUNT,
        "memory": None,
        "swap": None,
    }
    try:
        load_avg = os.getloadavg()
        payload["load_avg"] = [float(v) for v in load_avg]
        cpu_percent = (load_avg[0] / max(_FALLBACK_CPU_COUNT, 1)) * 100.0
        payload["cpu_percent"] = max(0.0, min(cpu_percent, 100.0))
    except (AttributeError, OSError):  # pragma: no cover - platform specific
        payload["load_avg"] = None
        payload["cpu_percent"] = None

    proc_payload = _minimal_process_sample(ts)
    payload["process"] = proc_payload if proc_payload else None

    return payload


def _sample_cpu_psutil(ts: float) -> Dict[str, Any]:
    assert psutil is not None  # narrow type for type-checkers

    payload: Dict[str, Any] = {"ts": ts}

    try:
        payload["cpu_percent"] = psutil.cpu_percent(interval=None)
    except Exception:  # pragma: no cover - psutil call failure
        payload["cpu_percent"] = None

    try:
        payload["cpu_count"] = psutil.cpu_count(logical=True) or _FALLBACK_CPU_COUNT
    except Exception:  # pragma: no cover - psutil call failure
        payload["cpu_count"] = _FALLBACK_CPU_COUNT

    try:
        payload["memory"] = dict(psutil.virtual_memory()._asdict())
    except Exception:  # pragma: no cover - platform specific
        payload["memory"] = None

    try:
        payload["swap"] = dict(psutil.swap_memory()._asdict())
    except Exception:  # pragma: no cover - platform specific
        payload["swap"] = None

    try:
        payload["load_avg"] = list(os.getloadavg())  # type: ignore[arg-type]
    except Exception:  # pragma: no cover - platform specific
        payload["load_avg"] = None

    try:
        proc = psutil.Process()
        payload["process"] = {
            "cpu_percent": proc.cpu_percent(interval=None),
            "memory_info": dict(proc.memory_info()._asdict()),
        }
    except Exception:  # pragma: no cover - process metrics optional
        payload["process"] = _minimal_process_sample(ts)

    return payload


def _sample_gpu_metrics() -> Optional[Dict[str, Any]]:
    global _NVML_DISABLED

    if _NVML_DISABLED or not _CONFIG.poll_gpu:
        return None

    if not _CONFIG.use_nvml or not HAS_NVML or "pynvml" not in globals() or pynvml is None:
        _NVML_DISABLED = True
        return None

    try:  # pragma: no cover - depends on NVML
        pynvml.nvmlInit()
    except Exception as exc:  # pragma: no cover - NVML init failure
        logger.warning(
            "NVML initialisation failed; disabling GPU polling",
            extra={
                "event": "system_metrics.nvml_init_failed",
                "error": repr(exc),
            },
        )
        _NVML_DISABLED = True
        _CONFIG.use_nvml = False
        return None

    try:  # pragma: no cover - depends on NVML
        count = pynvml.nvmlDeviceGetCount()
        devices = []
        util_sum = 0.0
        for idx in range(count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
            util = pynvml.nvmlDeviceGetUtilizationRates(handle)
            memory = pynvml.nvmlDeviceGetMemoryInfo(handle)
            entry: Dict[str, Any] = {
                "index": idx,
                "util": float(util.gpu),
                "mem_used": float(memory.used),
                "mem_total": float(memory.total),
            }
            util_sum += float(util.gpu)
            try:
                entry["temp_c"] = float(
                    pynvml.nvmlDeviceGetTemperature(
                        handle, getattr(pynvml, "NVML_TEMPERATURE_GPU", 0)
                    )
                )
            except Exception:
                entry["temp_c"] = None
            try:
                entry["power_w"] = float(pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0)
            except Exception:
                entry["power_w"] = None
            devices.append(entry)

        return {
            "gpu_count": count,
            "gpus": devices,
            "gpu_util_mean": util_sum / max(len(devices), 1) if devices else None,
        }
    except Exception as exc:  # pragma: no cover - NVML query failure
        logger.warning(
            "NVML sampling failed; disabling GPU polling",
            extra={
                "event": "system_metrics.nvml_sampling_failed",
                "error": repr(exc),
            },
        )
        _NVML_DISABLED = True
        _CONFIG.use_nvml = False
        return None
    finally:  # pragma: no cover - depends on NVML
        try:
            pynvml.nvmlShutdown()
        except Exception:
            pass


def sample_system_metrics() -> Dict[str, Any]:
    """Return a snapshot of system utilisation.

    When :mod:`psutil` or NVML are unavailable the function falls back to a
    minimal CPU-only sampler. Enable GPU polling explicitly with
    ``CODEX_MONITORING_ENABLE_GPU=1`` (optionally
    ``CODEX_MONITORING_ENABLE_NVML=1``); disable it at runtime with
    ``CODEX_MONITORING_DISABLE_GPU=1`` or :func:`configure_system_metrics`.
    """

    ts = _now()
    if _CONFIG.use_psutil and HAS_PSUTIL and "psutil" in globals() and psutil is not None:
        payload = _sample_cpu_psutil(ts)
    else:
        payload = _sample_cpu_minimal(ts)

    gpu_payload = _sample_gpu_metrics()
    if gpu_payload:
        payload.update(gpu_payload)

    return payload


def _write_record(path: Path, record: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")


def log_system_metrics(out_path: Path | str, interval: float = 60.0) -> None:
    """Continuously append system metrics to ``out_path``.

    This is a blocking helper that only returns when interrupted. It mirrors the
    minimal functionality sketched in the remediation plan so that automation can
    invoke it from a subprocess when needed.
    """

    target = Path(out_path)
    status = _ensure_sampler_dependencies(
        "log_system_metrics", warn_key="log_system_metrics", path=target
    )
    if not status.enabled:
        _log_logger_disabled(
            "log_system_metrics",
            warn_key="log_system_metrics",
            missing=status.missing_dependencies,
            path=target,
        )
        return
    stop_event = threading.Event()

    def _loop() -> None:
        while not stop_event.is_set():
            try:
                _write_record(target, sample_system_metrics())
            except Exception:
                # Avoid killing the loop due to transient psutil errors.
                pass
            stop_event.wait(max(0.1, float(interval)))

    thread = threading.Thread(target=_loop, name="codex-system-metrics", daemon=True)
    thread.start()

    try:
        while thread.is_alive():
            thread.join(timeout=0.5)
    except KeyboardInterrupt:  # pragma: no cover - manual stop
        stop_event.set()
        thread.join()


@dataclass
class SystemMetricsLogger:
    """Background logger that writes metrics to a JSONL file."""

    path: Path | str
    interval: float = 60.0

    def __post_init__(self) -> None:
        self._path = Path(self.path)
        self._interval = max(0.1, float(self.interval))
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._atexit_registered = False
        status = _ensure_sampler_dependencies(
            "SystemMetricsLogger",
            warn_key="SystemMetricsLogger",
            path=self._path,
            hook="__post_init__",
        )
        self._sampler_status: SamplerStatus = status
        self._noop: bool = not status.enabled
        if self._noop:
            _log_logger_disabled(
                "SystemMetricsLogger",
                warn_key="SystemMetricsLogger",
                missing=status.missing_dependencies,
                path=self._path,
                hook="__post_init__",
            )

    def start(self) -> None:
        """Start logging metrics in the background."""

        if getattr(self, "_noop", False):
            return

        if self._thread is not None and self._thread.is_alive():
            return

        self._stop.clear()
        self._thread = threading.Thread(target=self._run, name="codex-system-metrics", daemon=True)
        self._thread.start()
        if not self._atexit_registered:
            atexit.register(self.stop)
            self._atexit_registered = True

    def stop(self) -> None:
        """Signal the logger to stop and wait for completion."""

        self._stop.set()
        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=self._interval + 1.0)
        self._thread = None

    def __enter__(self) -> "SystemMetricsLogger":  # pragma: no cover - convenience
        self.start()
        return self

    def __exit__(self, *_exc: object) -> None:  # pragma: no cover - convenience
        self.stop()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                _write_record(self._path, sample_system_metrics())
            except Exception:
                pass
            self._stop.wait(self._interval)


@dataclass(frozen=True)
class SamplerStatus:
    """Lightweight container describing sampler availability."""

    cpu_enabled: bool
    degraded: bool
    gpu_enabled: bool
    missing_dependencies: Tuple[str, ...] = ()
    notes: Tuple[str, ...] = ()

    @property
    def enabled(self) -> bool:
        return self.cpu_enabled or self.gpu_enabled


__all__ = [
    "HAS_PSUTIL",
    "HAS_NVML",
    "SYSTEM_METRICS_DEGRADED",
    "SystemMetricsConfig",
    "configure_system_metrics",
    "current_system_metrics_config",
    "SystemMetricsLogger",
    "log_system_metrics",
    "sample_system_metrics",
    "sampler_status",
]


def _psutil_available() -> bool:
    return HAS_PSUTIL and "psutil" in globals() and psutil is not None


def _nvml_available() -> bool:
    return HAS_NVML and "pynvml" in globals() and pynvml is not None


def _update_degraded_flag() -> None:
    global SYSTEM_METRICS_DEGRADED

    SYSTEM_METRICS_DEGRADED = not (_CONFIG.use_psutil and _psutil_available())


def _ensure_psutil_sampler(
    context: str,
    *,
    warn_key: Optional[str] = None,
    **metadata: Any,
) -> bool:
    """Ensure psutil-backed sampling is available or downgrade gracefully."""

    psutil_ok = _psutil_available() and _CONFIG.use_psutil
    if psutil_ok:
        _update_degraded_flag()
        return True

    _CONFIG.use_psutil = False
    _update_degraded_flag()

    if not _PSUTIL_REQUESTED:
        return False

    key = warn_key or context
    if key in _PSUTIL_WARNING_CONTEXTS:
        return False

    extra: Dict[str, Any] = {
        "event": "system_metrics.psutil_missing",
        "dependency": "psutil",
        "sampler": "minimal",
        "component": context,
    }

    if metadata:
        extra.update({k: (str(v) if isinstance(v, Path) else v) for k, v in metadata.items()})

    logger.warning("psutil is unavailable; using minimal sampler", extra=extra)
    _PSUTIL_WARNING_CONTEXTS.add(key)
    return False


def _ensure_nvml_sampler(
    context: str,
    *,
    warn_key: Optional[str] = None,
    **metadata: Any,
) -> bool:
    """Ensure NVML-backed GPU sampling is available or disable gracefully."""

    global _NVML_DISABLED

    if not _CONFIG.poll_gpu:
        return False

    key = warn_key or context
    requested = _CONFIG.poll_gpu and _NVML_REQUESTED and not _NVML_FEATURE_DISABLED

    if requested and _nvml_available() and not _NVML_DISABLED:
        return True

    _CONFIG.use_nvml = False

    if not requested:
        _NVML_DISABLED = True
        if _CONFIG.poll_gpu and _NVML_FEATURE_DISABLED and key not in _NVML_WARNING_CONTEXTS:
            extra: Dict[str, Any] = {
                "event": "system_metrics.nvml_disabled",
                "dependency": "pynvml",
                "component": context,
                "reason": "feature_flag",
            }
            if metadata:
                extra.update(
                    {k: (str(v) if isinstance(v, Path) else v) for k, v in metadata.items()}
                )
            logger.info("NVML probing disabled via CODEX_DISABLE_NVML", extra=extra)
            _NVML_WARNING_CONTEXTS.add(key)
        return False

    if key in _NVML_WARNING_CONTEXTS:
        _NVML_DISABLED = True
        return False

    extra = {
        "event": "system_metrics.nvml_missing",
        "dependency": "pynvml",
        "component": context,
        "sampler": "cpu_only",
    }
    if metadata:
        extra.update({k: (str(v) if isinstance(v, Path) else v) for k, v in metadata.items()})

    logger.warning("NVML is unavailable; GPU metrics disabled", extra=extra)
    _NVML_WARNING_CONTEXTS.add(key)
    _NVML_DISABLED = True
    return False


def _ensure_sampler_dependencies(
    context: str,
    *,
    warn_key: Optional[str] = None,
    **metadata: Any,
) -> SamplerStatus:
    """Ensure runtime samplers downgrade gracefully when dependencies miss."""

    _ensure_psutil_sampler(context, warn_key=warn_key, **metadata)
    _ensure_nvml_sampler(context, warn_key=warn_key, **metadata)

    return sampler_status()


def sampler_status() -> SamplerStatus:
    """Return the current sampler status without mutating configuration."""

    psutil_ok = _psutil_available() and _CONFIG.use_psutil
    nvml_requested = _CONFIG.poll_gpu and _NVML_REQUESTED and not _NVML_FEATURE_DISABLED
    nvml_ok = nvml_requested and _CONFIG.use_nvml and not _NVML_DISABLED and _nvml_available()

    missing: list[str] = []
    notes: list[str] = []

    if not psutil_ok and _PSUTIL_REQUESTED:
        missing.append("psutil")
        if not _psutil_available():
            notes.append("psutil-missing")
        else:
            notes.append("psutil-disabled")

    if nvml_requested and not nvml_ok:
        missing.append("nvml")
        if _NVML_FEATURE_DISABLED:
            notes.append("nvml-disabled")
        elif not _CONFIG.use_nvml or _NVML_DISABLED:
            notes.append("nvml-disabled-runtime")
        elif not _nvml_available():
            notes.append("nvml-missing")

    cpu_active = psutil_ok or _PSUTIL_REQUESTED

    unique_missing = tuple(dict.fromkeys(missing))
    unique_notes = tuple(dict.fromkeys(notes))

    return SamplerStatus(
        cpu_enabled=cpu_active,
        degraded=SYSTEM_METRICS_DEGRADED,
        gpu_enabled=nvml_ok,
        missing_dependencies=unique_missing,
        notes=unique_notes,
    )


def _log_logger_disabled(
    context: str,
    *,
    warn_key: Optional[str] = None,
    missing: Tuple[str, ...] = (),
    **metadata: Any,
) -> None:
    """Emit a structured warning when the logger becomes a no-op."""

    key = warn_key or context
    if key in _LOGGER_WARNING_CONTEXTS:
        return

    extra: Dict[str, Any] = {
        "event": "system_metrics.logger_disabled",
        "component": context,
        "mode": "noop",
        "degraded": SYSTEM_METRICS_DEGRADED,
    }
    if missing:
        extra["missing"] = list(missing)
    if metadata:
        extra.update({k: (str(v) if isinstance(v, Path) else v) for k, v in metadata.items()})

    logger.warning("system metrics logger disabled; skipping sampling", extra=extra)
    _LOGGER_WARNING_CONTEXTS.add(key)
