"""Unified optional logging and hardware sampling utilities."""

from __future__ import annotations

import argparse
import json
import logging
import os
import platform
import re
import shutil
import subprocess  # used with validated executable path
import sys
from dataclasses import dataclass
from datetime import datetime
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

MAX_LOG_BYTES = int(os.environ.get("CODEX_ML_MAX_LOG_BYTES", 5 * 1024 * 1024))
_LOG_SAFETY_FILTERS = None
_LOG_SAFETY_CFG = None
_SENSITIVE_LOG_KEYS = (
    "text",
    "prompt",
    "completion",
    "input",
    "output",
    "input_text",
    "output_text",
)

_SECRET_PATTERNS: Tuple[re.Pattern[str], ...] = (
    re.compile(r"(?i)(sk-[A-Za-z0-9]{10,})"),
    re.compile(r"(?i)(AKIA[0-9A-Z]{16})"),
    re.compile(r"(?i)(ASIA[0-9A-Z]{16})"),
    re.compile(r"(?i)(aws_secret_access_key\s*=\s*[A-Za-z0-9/+=]{40})"),
    re.compile(r"(?i)(AIza[0-9A-Za-z\-_]{35})"),
    re.compile(r"(?i)(ghp_[A-Za-z0-9]{36})"),
    re.compile(r"(?i)(xox[baprs]-[A-Za-z0-9\-]{10,})"),
)


def _apply_secret_patterns(value: str) -> str:
    if os.getenv("DISABLE_SECRET_FILTER", "0") == "1":
        return value
    masked = value
    for pattern in _SECRET_PATTERNS:
        masked = pattern.sub("[SECRET]", masked)
    return masked


def _try_git_commit() -> str | None:
    """Resolve the current git commit safely without shell usage."""

    git = shutil.which("git")
    if not git:
        return None
    try:
        root = Path(__file__).resolve().parents[3]
        return subprocess.check_output(  # nosec B603: static argv, shell disabled
            [git, "-C", str(root), "rev-parse", "HEAD"],
            text=True,
        ).strip()
    except Exception as exc:  # pragma: no cover - diagnostic only
        logger.debug("git commit detection failed", exc_info=exc)
        return None


_GIT_COMMIT = "unknown"
_commit_candidate = _try_git_commit()
if _commit_candidate:
    _GIT_COMMIT = _commit_candidate


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


def _get_safety_cfg():
    """Return a cached SafetyConfig instance for log redaction."""

    global _LOG_SAFETY_CFG
    if _LOG_SAFETY_CFG is None:
        try:
            from codex_ml.safety import SafetyConfig

            _LOG_SAFETY_CFG = SafetyConfig()
        except Exception:  # pragma: no cover - safety module optional
            _LOG_SAFETY_CFG = None
    return _LOG_SAFETY_CFG


def _get_safety_filters():
    """Return cached SafetyFilters instance when available."""

    global _LOG_SAFETY_FILTERS
    if _LOG_SAFETY_FILTERS is None:
        try:
            from codex_ml.safety import SafetyFilters

            _LOG_SAFETY_FILTERS = SafetyFilters.from_defaults()
        except Exception:  # pragma: no cover - optional dependency
            _LOG_SAFETY_FILTERS = None
    return _LOG_SAFETY_FILTERS


def _maybe_rotate_log(path: Path) -> None:
    """Rotate ``path`` if it exceeds :data:`MAX_LOG_BYTES`."""

    if MAX_LOG_BYTES <= 0 or not path.exists():
        return
    try:
        size = path.stat().st_size
    except OSError:  # pragma: no cover - filesystem edge cases
        return
    if size < MAX_LOG_BYTES:
        return
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    rotated = path.with_name(f"{path.name}.{timestamp}")
    try:
        os.replace(path, rotated)
    except OSError:  # pragma: no cover - rotation best-effort
        return
    logger.info("Log file rotated: %s -> %s", path, rotated)


def _redact_sensitive_fields(record: Dict[str, Any]) -> None:
    """Redact sensitive text fields before persisting NDJSON payloads."""

    cfg = _get_safety_cfg()
    filters = _get_safety_filters()
    redactions = record.get("redactions")
    if not isinstance(redactions, dict):
        redactions = {}
    from codex_ml.safety import sanitize_output  # local import to avoid cycles

    for key in _SENSITIVE_LOG_KEYS:
        value = record.get(key)
        if not isinstance(value, str) or not value:
            continue
        updated = value
        field_meta: Dict[str, Any] = {}
        if filters is not None:
            try:
                result = filters.sanitize(value, stage=f"log.{key}")
            except Exception:  # pragma: no cover - filters best-effort
                result = None
            else:
                updated = result.sanitized_text
                matches = getattr(result, "matches", ())
                if matches:
                    rule_ids = sorted({m.rule_id for m in matches if getattr(m, "rule_id", None)})
                    if rule_ids:
                        field_meta["rules"] = rule_ids
                        field_meta["match_count"] = len(matches)
        safe = sanitize_output(updated, cfg)
        updated = safe.get("text", updated)
        redacted_counts = safe.get("redactions", {})
        for label, count in redacted_counts.items():
            if count:
                field_meta[label] = field_meta.get(label, 0) + int(count)
        record[key] = updated
        if field_meta:
            redactions[key] = field_meta
        elif key in redactions:
            redactions.pop(key, None)
    if redactions:
        record["redactions"] = redactions
    elif "redactions" in record:
        record.pop("redactions", None)


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
                "mlflow",
                mlflow_available,
                None if mlflow_available else "not-installed",
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


def _git_commit() -> Optional[str]:
    """Return the cached git commit hash when available."""

    return None if _GIT_COMMIT == "unknown" else _GIT_COMMIT


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
        except Exception as exc:
            logger.debug("psutil metrics unavailable", exc_info=exc)
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
        except Exception as exc:
            logger.debug("NVML sampling failed", exc_info=exc)
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
                    except Exception as exc:
                        logger.debug("torch CUDA utilization unavailable", exc_info=exc)
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
        except Exception as exc:
            logger.debug("torch CUDA sampling failed", exc_info=exc)

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
        except Exception as exc:
            logger.debug("tensorboard add_scalar failed", exc_info=exc)

    if loggers.wb is not None:
        try:  # pragma: no cover - wandb optional
            loggers.wb.log({**values, "step": step})
        except Exception as exc:
            logger.debug("wandb log failed", exc_info=exc)

    if loggers.mlflow_active and mlflow is not None:
        try:  # pragma: no cover - mlflow optional
            mlflow.log_metrics(values, step=step)
        except Exception as exc:
            logger.debug("mlflow log_metrics failed", exc_info=exc)


def write_ndjson(path: str | os.PathLike[str], record: Dict[str, Any]) -> None:
    """Append ``record`` to ``path`` as NDJSON with rotation and redaction."""

    if not isinstance(record, dict):
        raise TypeError("record must be a mapping")
    _redact_sensitive_fields(record)
    path_obj = Path(path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    _maybe_rotate_log(path_obj)
    with path_obj.open("a", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=True)
        f.write("\n")


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
