from __future__ import annotations

import os
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterator, Optional

try:  # Optional: TensorBoard
    from torch.utils.tensorboard import SummaryWriter  # type: ignore
except Exception:  # pragma: no cover
    SummaryWriter = None  # type: ignore

try:  # Optional: MLflow
    import mlflow  # type: ignore
except Exception:  # pragma: no cover
    mlflow = None  # type: ignore

try:  # Optional: psutil for system metrics
    import psutil  # type: ignore
except Exception:  # pragma: no cover
    psutil = None  # type: ignore

try:  # Optional: GPU stats via NVML (pynvml)
    import pynvml  # type: ignore
except Exception:  # pragma: no cover
    pynvml = None  # type: ignore


@dataclass
class LogHandles:
    tb: Optional["SummaryWriter"] = None
    mlflow_run_active: bool = False


def init_tensorboard(log_dir: str | Path) -> Optional["SummaryWriter"]:
    """Initialize TensorBoard writer if available."""
    if SummaryWriter is None:
        return None
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    return SummaryWriter(log_dir=str(log_dir))


@contextmanager
def mlflow_run(
    run_name: str = "run", *, offline: bool = True, tracking_dir: str | Path = "./mlruns"
) -> Iterator[None]:
    """Context manager starting an MLflow run; defaults to local file backend."""
    if mlflow is None:
        yield
        return
    if offline:
        os.environ.setdefault("MLFLOW_TRACKING_URI", f"file:{Path(tracking_dir).resolve()}")
        Path(tracking_dir).mkdir(parents=True, exist_ok=True)
    mlflow.start_run(run_name=run_name)
    try:
        yield
    finally:
        mlflow.end_run()


def log_scalar_tb(writer: Optional["SummaryWriter"], tag: str, value: float, step: int) -> None:
    if writer is None:
        return
    writer.add_scalar(tag, value, global_step=step)


def log_params_mlflow(params: Dict[str, Any]) -> None:
    if mlflow is None:
        return
    mlflow.log_params(
        {k: (str(v) if not isinstance(v, (int, float, str)) else v) for k, v in params.items()}
    )


def log_metrics_mlflow(metrics: Dict[str, float], step: Optional[int] = None) -> None:
    if mlflow is None:
        return
    mlflow.log_metrics(metrics, step=step)


def system_metrics() -> Dict[str, Any]:
    """Lightweight system metrics snapshot (CPU/RAM; GPU if NVML available)."""
    out: Dict[str, Any] = {"ts": time.time()}
    if psutil is not None:
        out.update(
            {
                "cpu_percent": psutil.cpu_percent(interval=None),
                "ram_used_bytes": psutil.virtual_memory().used,
                "ram_total_bytes": psutil.virtual_memory().total,
            }
        )
    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            n = pynvml.nvmlDeviceGetCount()
            gpus = []
            for i in range(n):
                h = pynvml.nvmlDeviceGetHandleByIndex(i)
                mem = pynvml.nvmlDeviceGetMemoryInfo(h)
                gpus.append(
                    {"index": i, "mem_used_bytes": int(mem.used), "mem_total_bytes": int(mem.total)}
                )
            out["gpus"] = gpus
        except Exception:
            pass
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:
                pass
    return out
