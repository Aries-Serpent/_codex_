# [Module]: Offline logging helpers
# > Generated: 2025-08-26 20:36:12 | Author: mbaetiong
import os
import sys
import time
from contextlib import AbstractContextManager
from typing import Any, Dict, Iterable, Optional

try:
    from torch.utils.tensorboard import SummaryWriter  # type: ignore
except Exception:
    SummaryWriter = None  # type: ignore
try:
    import psutil  # type: ignore
except Exception:
    psutil = None  # type: ignore

try:  # pragma: no cover - ``resource`` missing on some platforms
    import resource  # type: ignore
except Exception:  # pragma: no cover - fallback path
    resource = None  # type: ignore


class OfflineTB(AbstractContextManager["OfflineTB"]):
    """Lightweight TensorBoard wrapper that silently degrades when disabled."""

    def __init__(self, log_dir: str = ".artifacts/tb"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.writer = SummaryWriter(log_dir) if SummaryWriter else None
        self._closed = False

    @property
    def enabled(self) -> bool:
        return self.writer is not None

    def log_scalar(self, tag: str, value: float, step: int) -> None:
        if self.writer is None:
            return
        self.writer.add_scalar(tag, value, step)

    def log_scalars(
        self, scalars: Iterable[tuple[str, float]] | Dict[str, float], step: int
    ) -> None:
        if isinstance(scalars, dict):
            items = scalars.items()
        else:
            items = scalars
        for tag, value in items:
            self.log_scalar(tag, float(value), step)

    def close(self) -> None:
        if self.writer is not None and not self._closed:
            try:
                self.writer.flush()
                self.writer.close()
            finally:
                self._closed = True

    def __enter__(self) -> "OfflineTB":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        self.close()
        return False


def _fallback_process_payload() -> Optional[Dict[str, float]]:
    """Return lightweight process metrics without psutil."""

    if resource is None:  # pragma: no cover - depends on platform
        return None
    try:
        usage = resource.getrusage(resource.RUSAGE_SELF)
        rss = float(usage.ru_maxrss)
        if sys.platform != "darwin":
            rss *= 1024.0  # Linux/macOS report units differently
        return {"rss_gb": rss / (1024.0**3)}
    except Exception:  # pragma: no cover - defensive guard
        return None


def sample_system_metrics() -> Dict[str, Any]:
    """Return a consistent metrics payload even when psutil is missing."""

    payload: Dict[str, Any] = {"time_unix": time.time()}
    if psutil is not None:
        try:
            virt = psutil.virtual_memory()
            payload.update(
                {
                    "cpu_percent": float(psutil.cpu_percent(interval=None)),
                    "mem_percent": float(virt.percent),
                    "mem_used_gb": float(virt.used) / (1024.0**3),
                    "process": None,
                }
            )
            try:
                proc = psutil.Process()
                proc_mem = proc.memory_info()
                payload["process"] = {
                    "cpu_percent": float(proc.cpu_percent(interval=None)),
                    "rss_gb": float(proc_mem.rss) / (1024.0**3),
                }
            except Exception:
                payload["process"] = None
            return payload
        except Exception:
            # fall back to the minimal sampler below
            pass

    cpu_percent = 0.0
    try:
        load1, _, _ = os.getloadavg()
        cores = os.cpu_count() or 1
        cpu_percent = max(0.0, min(100.0, (load1 / cores) * 100.0))
        payload["load_avg_1m"] = float(load1)
    except Exception:
        payload["load_avg_1m"] = None

    payload.update(
        {
            "cpu_percent": cpu_percent,
            "mem_percent": None,
            "mem_used_gb": None,
            "process": _fallback_process_payload(),
        }
    )
    return payload
