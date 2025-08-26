# [Module]: Offline logging helpers
# > Generated: 2025-08-26 20:36:12 | Author: mbaetiong
import os
import time
from typing import Dict, Optional

try:
    from torch.utils.tensorboard import SummaryWriter  # type: ignore
except Exception:
    SummaryWriter = None  # type: ignore
try:
    import psutil  # type: ignore
except Exception:
    psutil = None  # type: ignore


class OfflineTB:
    def __init__(self, log_dir: str = ".artifacts/tb"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.writer = SummaryWriter(log_dir) if SummaryWriter else None

    def log_scalar(self, tag: str, value: float, step: int) -> None:
        if self.writer:
            self.writer.add_scalar(tag, value, step)

    def close(self) -> None:
        if self.writer:
            self.writer.flush()
            self.writer.close()


def sample_system_metrics() -> Optional[Dict[str, float]]:
    if not psutil:
        return None
    try:
        v = psutil.virtual_memory()
        return {
            "cpu_percent": float(psutil.cpu_percent(interval=None)),
            "mem_percent": float(v.percent),
            "mem_used_gb": float(v.used) / (1024**3),
            "time_unix": time.time(),
        }
    except Exception:
        return None
