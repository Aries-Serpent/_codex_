"""Unified optional logging and hardware sampling utilities."""

from __future__ import annotations

import argparse
import json
import logging
import os
import platform
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple

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

from codex_ml.monitoring.prometheus import fallback_status as prometheus_fallback_status
from codex_ml.monitoring.system_metrics import SamplerStatus, sampler_status

logger = logging.getLogger(__name__)
_PSUTIL_WARNED = False
_TELEMETRY_BANNER_EMITTED = False


@dataclass(frozen=True)
class TelemetryComponentStatus:
    name: str
    available: bool
    detail: Optional[str] = None


@dataclass
class CodexLoggers:
    """Container for optional logger handles."""

    tb: Any = None
    wb: Any = None
    mlflow_active: bool = False
    gpu: bool = False  # Whether GPU telemetry is enabled/available
    degradations: Tuple[TelemetryComponentStatus, ...] = ()
    system_status: "SamplerStatus | None" = None
    prometheus: Tuple[bool, Optional[Path], Optional[str]] | None = None

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


def _emit_degradation_banner(loggers: CodexLoggers) -> CodexLoggers:
    global _TELEMETRY_BANNER_EMITTED

    issues: list[str] = []

    for status in loggers.degradations:
        if status.available:
            continue
        detail = f" ({status.detail})" if status.detail else ""
        issues.append(f"{status.name}{detail}")

    system_state = loggers.system_status
    if system_state is None:
        system_state = sampler_status()
        loggers.system_status = system_state
    if system_state.missing_dependencies:
        missing = ", ".join(system_state.missing_dependencies)
        note_suffix = ""
        if getattr(system_state, "notes", None):
            note_suffix = f" ({', '.join(system_state.notes)})"
        issues.append(f"system-metrics missing: {missing}{note_suffix}")
    elif system_state.degraded:
        note_suffix = ""
        if getattr(system_state, "notes", None):
            note_suffix = f" ({', '.join(system_state.notes)})"
        issues.append(f"system-metrics degraded{note_suffix}")

    prom = loggers.prometheus
    if prom is None:
        prom = prometheus_fallback_status()
        loggers.prometheus = prom
    prom_active, prom_path, prom_reason = prom
    if prom_active:
        detail = f" -> {prom_path}" if prom_path else ""
        if prom_reason:
            detail += f" ({prom_reason})"
        issues.append(f"prometheus fallback{detail}")

    if not (loggers.tb or loggers.wb or loggers.mlflow_active or loggers.gpu):
        issues.append("no telemetry sinks enabled")

    if issues and not _TELEMETRY_BANNER_EMITTED:
        print(f"[telemetry] degraded: {'; '.join(issues)}", file=sys.stderr)
        _TELEMETRY_BANNER_EMITTED = True
    return loggers


def init_telemetry(profile: str = "min") -> CodexLoggers:
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
    if profile is None:
        profile = "min"

    # Default to minimal profile: enable TensorBoard and MLflow, disable W&B and GPU.
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

    components: list[TelemetryComponentStatus] = []
    tb_available = bool(tb and SummaryWriter is not None)
    if tb:
        components.append(
            TelemetryComponentStatus(
                "tensorboard", tb_available, None if tb_available else "not-installed"
            )
        )
    mlflow_available = bool(mlf and mlflow is not None)
    if mlf:
        components.append(
            TelemetryComponentStatus(
                "mlflow", mlflow_available, None if mlflow_available else "not-installed"
            )
        )
    wandb_available = bool(wb and wandb is not None)
    if wb:
        components.append(
            TelemetryComponentStatus(
                "wandb", wandb_available, None if wandb_available else "not-installed"
            )
        )

    loggers = CodexLoggers(
        tb=True if tb_available else None,
        wb=True if wandb_available else None,
        mlflow_active=mlflow_available,
        gpu=gpu,
        degradations=tuple(components),
    )
    loggers.system_status = sampler_status()
    loggers.prometheus = prometheus_fallback_status()
    return _emit_degradation_banner(loggers)


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
    """Initialise enabled loggers based on ``args`` or Hydra config."""

    cfg = getattr(args, "hydra_cfg", None) or {}

    if cfg:
        component_statuses: list[TelemetryComponentStatus] = []

        tb_handle = None
        tb_detail = None
        tb_cfg = cfg.get("tensorboard", {})
        if tb_cfg.get("enable"):
            if SummaryWriter is None:
                tb_detail = "not-installed"
            else:
                logdir = tb_cfg.get("logdir", "runs/tb")
                try:  # pragma: no cover - depends on tensorboard install
                    os.makedirs(logdir, exist_ok=True)
                    tb_handle = SummaryWriter(logdir)  # type: ignore[arg-type]
                except Exception as exc:  # pragma: no cover - optional
                    tb_detail = f"error:{exc.__class__.__name__}"
            component_statuses.append(
                TelemetryComponentStatus("tensorboard", tb_handle is not None, tb_detail)
            )

        wb_handle = None
        wb_detail = None
        if cfg.get("wandb", {}).get("enable"):
            if wandb is None:
                wb_detail = "not-installed"
            else:
                try:  # pragma: no cover - wandb optional
                    project = cfg["wandb"].get("project", "codex")
                    mode = cfg["wandb"].get("mode", "offline")
                    wb_handle = wandb.init(project=project, mode=mode)
                except Exception as exc:  # pragma: no cover - optional
                    wb_detail = f"error:{exc.__class__.__name__}"
                    wb_handle = None
            component_statuses.append(
                TelemetryComponentStatus("wandb", wb_handle is not None, wb_detail)
            )

        mlflow_active = False
        mlflow_detail = None
        if cfg.get("mlflow", {}).get("enable"):
            if mlflow is None:
                mlflow_detail = "not-installed"
            else:
                try:  # pragma: no cover - mlflow optional
                    uri = cfg["mlflow"].get("tracking_uri", "./mlruns")
                    mlflow.set_tracking_uri(uri)
                    exp = cfg["mlflow"].get("experiment", "codex")
                    mlflow.set_experiment(exp)
                    mlflow.start_run()
                    mlflow_active = True
                except Exception as exc:  # pragma: no cover - optional
                    mlflow_detail = f"error:{exc.__class__.__name__}"
            component_statuses.append(
                TelemetryComponentStatus("mlflow", mlflow_active, mlflow_detail)
            )

        loggers = CodexLoggers(
            tb=tb_handle,
            wb=wb_handle,
            mlflow_active=mlflow_active,
            degradations=tuple(component_statuses),
        )
        loggers.system_status = sampler_status()
        loggers.prometheus = prometheus_fallback_status()
        return _emit_degradation_banner(loggers)

    # Fallback to argparse flags
    component_statuses: list[TelemetryComponentStatus] = []

    logdir = getattr(args, "tb_logdir", "") or "./runs"
    tb_handle = None
    tb_detail = None
    if SummaryWriter is None:
        tb_detail = "not-installed"
    else:
        try:  # pragma: no cover - depends on tensorboard install
            os.makedirs(logdir, exist_ok=True)
            tb_handle = SummaryWriter(logdir)  # type: ignore[arg-type]
        except Exception as exc:  # pragma: no cover - optional
            tb_detail = f"error:{exc.__class__.__name__}"
            tb_handle = None
    component_statuses.append(
        TelemetryComponentStatus("tensorboard", tb_handle is not None, tb_detail)
    )

    wb_handle = None
    wb_detail = None
    if getattr(args, "enable_wandb", False):
        if wandb is None:
            wb_detail = "not-installed"
        else:
            try:  # pragma: no cover - wandb may not be installed
                mode = os.getenv("WANDB_MODE", "offline")
                if mode not in {"offline", "disabled"}:
                    mode = "disabled"
                wb_handle = wandb.init(
                    project=getattr(args, "wandb_project", "codex-offline"),
                    mode=mode,
                    dir=logdir,
                )
            except Exception as exc:  # pragma: no cover - optional
                wb_detail = f"error:{exc.__class__.__name__}"
                wb_handle = None
        component_statuses.append(
            TelemetryComponentStatus("wandb", wb_handle is not None, wb_detail)
        )

    mlflow_active = False
    mlflow_detail = None
    if getattr(args, "mlflow_enable", False):
        if mlflow is None:
            mlflow_detail = "not-installed"
        else:
            try:  # pragma: no cover - mlflow optional
                uri = getattr(args, "mlflow_tracking_uri", "") or "./mlruns"
                mlflow.set_tracking_uri(uri)
                exp = getattr(args, "mlflow_experiment", "codex")
                mlflow.set_experiment(exp)
                mlflow.start_run()
                mlflow_active = True
            except Exception as exc:  # pragma: no cover - optional
                mlflow_detail = f"error:{exc.__class__.__name__}"
                mlflow_active = False
        component_statuses.append(TelemetryComponentStatus("mlflow", mlflow_active, mlflow_detail))

    loggers = CodexLoggers(
        tb=tb_handle,
        wb=wb_handle,
        mlflow_active=mlflow_active,
        degradations=tuple(component_statuses),
    )
    loggers.system_status = sampler_status()
    loggers.prometheus = prometheus_fallback_status()
    return _emit_degradation_banner(loggers)


# ---------------------------------------------------------------------------
# System metrics


_GIT_COMMIT: Optional[str] = None


def _git_commit() -> Optional[str]:
    """Return current git commit hash if available."""

    global _GIT_COMMIT
    if _GIT_COMMIT is None:
        try:  # pragma: no cover - git may be missing
            root = Path(__file__).resolve().parents[3]
            _GIT_COMMIT = subprocess.check_output(
                ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
            ).strip()
        except Exception:
            _GIT_COMMIT = None
    return _GIT_COMMIT


def _codex_sample_system() -> Dict[str, Any]:
    """Gather CPU/GPU metrics and basic environment details."""

    metrics: Dict[str, Any] = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
    }
    commit = _git_commit()
    if commit:
        metrics["git_commit"] = commit
    if torch is not None:
        torch_version = getattr(torch, "__version__", None)
        if torch_version:
            metrics["torch"] = torch_version
        version_mod = getattr(torch, "version", None)
        cuda_version = getattr(version_mod, "cuda", None)
        if cuda_version:
            metrics["cuda"] = cuda_version
    global _PSUTIL_WARNED
    if psutil is not None:
        try:
            metrics["cpu_percent"] = float(psutil.cpu_percent(interval=0.0))
            metrics["ram_percent"] = float(psutil.virtual_memory().percent)
        except Exception:
            pass
    elif not _PSUTIL_WARNED:
        logger.warning("psutil not installed; system metrics will be unavailable")
        _PSUTIL_WARNED = True

    # Prefer NVML for GPU stats with per-device enumeration
    gpu_done = False
    if pynvml is not None:
        try:  # pragma: no cover - depends on GPU/NVML availability
            pynvml.nvmlInit()
            count = pynvml.nvmlDeviceGetCount()
            gpus = []
            util_sum = 0.0
            for i in range(count):
                h = pynvml.nvmlDeviceGetHandleByIndex(i)
                util = pynvml.nvmlDeviceGetUtilizationRates(h)
                mem = pynvml.nvmlDeviceGetMemoryInfo(h)
                temp = pynvml.nvmlDeviceGetTemperature(h, 0)
                power = pynvml.nvmlDeviceGetPowerUsage(h) / 1000.0
                util_sum += float(util.gpu)
                gpus.append(
                    {
                        "device": i,
                        "util": float(util.gpu),
                        "mem_used": float(mem.used),
                        "mem_total": float(mem.total),
                        "temp_c": float(temp),
                        "power_w": float(power),
                    }
                )
            metrics["gpus"] = gpus
            metrics["gpu_util_mean"] = util_sum / max(1, len(gpus))
            pynvml.nvmlShutdown()
            gpu_done = True
        except Exception:
            gpu_done = False

    if not gpu_done and torch is not None and hasattr(torch, "cuda") and torch.cuda.is_available():
        gpus = []
        util_sum = 0.0
        try:  # pragma: no cover - optional
            for i in range(torch.cuda.device_count()):
                props = torch.cuda.get_device_properties(i)
                used = float(torch.cuda.memory_allocated(i))
                total = float(props.total_memory)
                util = None
                if hasattr(torch.cuda, "utilization"):
                    try:
                        util = float(torch.cuda.utilization(i))
                    except Exception:
                        util = None
                if util:
                    util_sum += util
                gpus.append(
                    {
                        "device": i,
                        "util": util,
                        "mem_used": used,
                        "mem_total": total,
                    }
                )
            if gpus:
                metrics["gpus"] = gpus
                metrics["gpu_util_mean"] = util_sum / max(1, len(gpus))
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
    path_obj = Path(path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    with path_obj.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=True) + "\n")


__all__ = [
    "CodexLoggers",
    "TelemetryComponentStatus",
    "_codex_patch_argparse",
    "_codex_logging_bootstrap",
    "_codex_sample_system",
    "_codex_log_all",
    "init_telemetry",
    "write_ndjson",
]
