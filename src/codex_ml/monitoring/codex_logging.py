"""Unified optional logging and hardware sampling utilities."""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:  # pragma: no cover - typing only
    pass

# Optional dependencies -----------------------------------------------------
try:  # pragma: no cover - optional
    from torch.utils.tensorboard import SummaryWriter  # type: ignore
except Exception:  # pragma: no cover - tensorboard not installed
    SummaryWriter = None  # type: ignore

try:  # pragma: no cover - optional
    import wandb  # type: ignore
except Exception:  # pragma: no cover - wandb not installed
    wandb = None  # type: ignore

try:  # pragma: no cover - optional
    import mlflow  # type: ignore
except Exception:  # pragma: no cover - mlflow not installed
    mlflow = None  # type: ignore

try:  # pragma: no cover - optional
    import psutil  # type: ignore
except Exception:  # pragma: no cover - psutil not installed
    psutil = None  # type: ignore

try:  # pragma: no cover - optional
    import pynvml  # type: ignore
except Exception:  # pragma: no cover - nvml not installed
    pynvml = None  # type: ignore

try:  # pragma: no cover - optional
    import torch  # type: ignore
except Exception:  # pragma: no cover - torch not installed
    torch = None  # type: ignore


@dataclass
class CodexLoggers:
    """Container for optional logger handles."""

    tb: Any = None
    wb: Any = None
    mlflow_active: bool = False
    gpu: bool = False  # Whether GPU telemetry is enabled/available

    # Back-compat convenience: allow dict-like access for common keys.
    def __getitem__(self, key: str) -> Any:  # pragma: no cover - convenience
        if key == "tb":
            return self.tb
        if key == "wb":
            return self.wb
        if key in {"mlflow", "mlflow_active"}:
            return self.mlflow_active
        if key == "gpu":
            return self.gpu
        raise KeyError(key)


def init_telemetry(profile: str = "off") -> CodexLoggers:
    """Initialise telemetry components based on profile.

    When ``profile`` is "full" we attempt NVML-based GPU metrics but fall back
    to psutil-only sampling if NVML is unavailable.

    Parameters
    ----------
    profile : {"off", "min", "full"}
        Selects which logging backends to enable.

    Returns
    -------
    CodexLoggers
        Handles/flags for enabled logging backends and GPU telemetry.
    """
    tb = wb = mlf = False
    gpu = False
    if profile == "min":
        tb = True
        mlf = True
    elif profile == "full":
        tb = wb = mlf = True
        gpu = True

    # Try to initialise NVML when GPU telemetry requested; gracefully disable on failure.
    if gpu:
        try:  # pragma: no cover - depends on NVML
            import pynvml as _nv  # type: ignore

            _nv.nvmlInit()
            # If init succeeds, immediately shutdown to avoid leaking handles; we sample later.
            _nv.nvmlShutdown()
        except Exception:
            gpu = False

    return CodexLoggers(tb=tb if tb else None, wb=wb if wb else None, mlflow_active=mlf, gpu=gpu)


# ---------------------------------------------------------------------------
# Argparse integration


def _codex_patch_argparse(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """Add monitoring flags to ``parser``."""

    add = parser.add_argument
    add("--enable-wandb", action="store_true", help="Enable Weights & Biases logging.")
    add("--mlflow-enable", action="store_true", help="Enable MLflow tracking.")
    add(
        "--mlflow-tracking-uri",
        type=str,
        default="",
        help="MLflow tracking URI (defaults to local ./mlruns).",
    )
    add(
        "--mlflow-experiment",
        type=str,
        default="codex",
        help="MLflow experiment name.",
    )
    add(
        "--tb-logdir",
        type=str,
        default="./runs",
        help="TensorBoard log directory.",
    )
    add("--wandb-project", type=str, default="codex-offline", help="W&B project name.")
    return parser


# ---------------------------------------------------------------------------
# Bootstrap helpers


def _codex_logging_bootstrap(args: argparse.Namespace) -> CodexLoggers:
    """Initialise enabled loggers based on ``args``."""

    tb = None
    if SummaryWriter is not None:
        logdir = getattr(args, "tb_logdir", "") or "./runs"
        try:  # pragma: no cover - depends on tensorboard install
            os.makedirs(logdir, exist_ok=True)
            # SummaryWriter typically accepts log_dir keyword, but positional works for TB's Writer.
            tb = SummaryWriter(logdir)  # type: ignore[arg-type]
        except Exception:
            tb = None

    wb = None
    if getattr(args, "enable_wandb", False) and wandb is not None:
        try:  # pragma: no cover - wandb may not be installed
            mode = os.getenv("WANDB_MODE", "offline")
            if mode not in {"offline", "disabled"}:
                mode = "disabled"
            wb = wandb.init(
                project=getattr(args, "wandb_project", "codex-offline"),
                mode=mode,
                dir=getattr(args, "tb_logdir", "./runs"),
            )
        except Exception:
            wb = None

    mlflow_active = False
    if getattr(args, "mlflow_enable", False) and mlflow is not None:
        try:  # pragma: no cover - mlflow optional
            uri = getattr(args, "mlflow_tracking_uri", "") or "./mlruns"
            mlflow.set_tracking_uri(uri)
            exp = getattr(args, "mlflow_experiment", "codex")
            mlflow.set_experiment(exp)
            mlflow.start_run()
            mlflow_active = True
        except Exception:
            mlflow_active = False

    return CodexLoggers(tb=tb, wb=wb, mlflow_active=mlflow_active)


# ---------------------------------------------------------------------------
# System metrics


def _codex_sample_system() -> Dict[str, Optional[float]]:
    """Gather CPU/GPU metrics."""

    metrics: Dict[str, Optional[float]] = {}
    if psutil is not None:
        try:
            metrics["cpu_percent"] = float(psutil.cpu_percent(interval=0.0))
            metrics["ram_percent"] = float(psutil.virtual_memory().percent)
        except Exception:
            pass

    # Prefer NVML for GPU stats
    gpu_done = False
    if pynvml is not None:
        try:  # pragma: no cover - depends on GPU/NVML availability
            pynvml.nvmlInit()
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            util = pynvml.nvmlDeviceGetUtilizationRates(handle)
            mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
            metrics["gpu_util"] = float(util.gpu)
            metrics["gpu_mem_used"] = float(mem.used)
            metrics["gpu_mem_total"] = float(mem.total)
            pynvml.nvmlShutdown()
            gpu_done = True
        except Exception:
            gpu_done = False

    if not gpu_done and torch is not None and hasattr(torch, "cuda") and torch.cuda.is_available():
        try:  # pragma: no cover - optional
            free, total = torch.cuda.mem_get_info()
            metrics["gpu_mem_free"] = float(free)
            metrics["gpu_mem_total"] = float(total)
        except Exception:
            pass

    return metrics


# ---------------------------------------------------------------------------
# Logging


def _filter_scalars(values: Dict[str, Any]) -> Dict[str, float]:
    out: Dict[str, float] = {}
    for k, v in values.items():
        try:
            out[k] = float(v)  # type: ignore[arg-type]
        except Exception:
            continue
    return out


def _codex_log_all(step: int, scalars: Dict[str, Any], loggers: CodexLoggers) -> None:
    """Log ``scalars`` at ``step`` to all enabled sinks."""

    values = _filter_scalars(scalars)

    if loggers.tb is not None:
        try:  # pragma: no cover - tensorboard optional
            for k, v in values.items():
                loggers.tb.add_scalar(k, v, step)
        except Exception:
            pass

    if loggers.wb is not None:
        try:  # pragma: no cover - wandb optional
            loggers.wb.log({**values, "step": step})
        except Exception:
            pass

    if loggers.mlflow_active and mlflow is not None:
        try:  # pragma: no cover - mlflow optional
            mlflow.log_metrics(values, step=step)
        except Exception:
            pass


def write_ndjson(path: str | os.PathLike[str], record: Dict[str, Any]) -> None:
    """Append ``record`` to ``path`` as NDJSON with basic redaction."""

    from codex_ml.safety import SafetyConfig, sanitize_output

    cfg = SafetyConfig()
    text = record.get("text")
    if isinstance(text, str):
        safe = sanitize_output(text, cfg)
        record["text"] = safe["text"]
        record.setdefault("redactions", {}).update(safe["redactions"])
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=True) + "\n")


__all__ = [
    "CodexLoggers",
    "_codex_patch_argparse",
    "_codex_logging_bootstrap",
    "_codex_sample_system",
    "_codex_log_all",
    "init_telemetry",
    "write_ndjson",
]
