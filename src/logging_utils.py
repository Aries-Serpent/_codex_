"""Lightweight logging utilities (TensorBoard + MLflow)."""

from __future__ import annotations

import logging
import os
import time
from collections.abc import Mapping, MutableMapping
from contextlib import contextmanager, suppress
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

try:  # pragma: no cover - tensorboard is optional in lightweight envs
    from torch.utils.tensorboard import SummaryWriter
except Exception:  # pragma: no cover - fall back to a stub
    SummaryWriter = None  # type: ignore[assignment]

try:  # pragma: no cover - MLflow is optional for offline smoke tests
    import mlflow
except Exception:  # pragma: no cover - guard offline runs that skip mlflow install
    mlflow = None  # type: ignore[assignment]

try:  # pragma: no cover - optional runtime dependency
    import psutil
except Exception:  # pragma: no cover - allow execution without psutil
    psutil = None  # type: ignore[assignment]

try:  # pragma: no cover - optional GPU metrics dependency
    import pynvml
except Exception:  # pragma: no cover - allow execution without NVML bindings
    pynvml = None  # type: ignore[assignment]


LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class LoggingConfig:
    enable_tensorboard: bool = False
    tensorboard_log_dir: str = "runs"
    enable_mlflow: bool = False
    mlflow_run_name: str = "codex-training"
    mlflow_tracking_uri: str | None = None
    mlflow_offline: bool = True
    mlflow_tracking_dir: str | Path = "./mlruns"


@dataclass(slots=True)
class LoggingSession:
    tensorboard: SummaryWriter | None
    mlflow_active: bool


@dataclass(slots=True)
class LogHandles:
    """Lightweight container for optional logging backends."""

    tb: SummaryWriter | None = None
    mlflow_run_active: bool = False


def _create_tensorboard_writer(log_dir: str | Path) -> SummaryWriter | None:
    if SummaryWriter is None:
        LOGGER.info("TensorBoard unavailable; skipping SummaryWriter initialisation")
        return None
    try:
        path = Path(log_dir)
        path.mkdir(parents=True, exist_ok=True)
    except Exception as exc:  # pragma: no cover - propagate context
        LOGGER.warning("Unable to create TensorBoard log directory '%s': %s", log_dir, exc)
        return None
    try:
        return SummaryWriter(str(path))
    except Exception as exc:  # pragma: no cover - e.g. tensorboard not installed
        LOGGER.warning("Failed to initialise TensorBoard writer: %s", exc)
        return None


def init_tensorboard(log_dir: str | Path) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    # The legacy API exposed ``init_tensorboard`` directly; delegate to the new helper
    # so external callers and older tests continue to function unchanged.
    return _create_tensorboard_writer(log_dir)


def _start_mlflow_run(config: LoggingConfig) -> bool:
    if not config.enable_mlflow:
        return False
    if mlflow is None:
        LOGGER.info("MLflow unavailable; skipping run creation")
        return False
    try:
        if config.mlflow_tracking_uri:
            mlflow.set_tracking_uri(config.mlflow_tracking_uri)
        elif config.mlflow_offline:
            tracking_path = Path(config.mlflow_tracking_dir)
            with suppress(Exception):  # pragma: no cover - directory creation best-effort
                tracking_path.mkdir(parents=True, exist_ok=True)
            mlflow.set_tracking_uri(f"file:{tracking_path.resolve()}")
        mlflow.start_run(run_name=config.mlflow_run_name)
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to start MLflow run '%s': %s", config.mlflow_run_name, exc)
        return False
    return True


def init_mlflow(
    experiment_name: str,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
) -> tuple[object | None, object | None]:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if mlflow is None:
        LOGGER.info("MLflow unavailable; init_mlflow returning no-op handles")
        return None, None

    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(run_name=experiment_name, tags=dict(tags) if tags else None)
        return mlflow, run
    except Exception as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def setup_logging(config: LoggingConfig | Mapping[str, object] | None) -> LoggingSession:
    """Initialise optional logging backends based on configuration."""

    if config is None:
        resolved = LoggingConfig()
    elif isinstance(config, LoggingConfig):
        resolved = config
    else:
        data: MutableMapping[str, object]
        if hasattr(config, "to_container"):
            data = config.to_container(resolve=True)  # type: ignore[attr-defined]
        else:
            data = dict(config)
        resolved = LoggingConfig(**data)

    writer = (
        _create_tensorboard_writer(resolved.tensorboard_log_dir)
        if resolved.enable_tensorboard
        else None
    )
    mlflow_active = _start_mlflow_run(resolved)
    return LoggingSession(tensorboard=writer, mlflow_active=mlflow_active)


def log_scalar_tb(writer: SummaryWriter | None, tag: str, value: float, step: int) -> None:
    """Log a scalar metric to TensorBoard when a writer is provided."""

    if writer is None:
        return
    try:
        writer.add_scalar(tag, value, global_step=step)
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug("TensorBoard scalar logging failed", exc_info=True)


def log_params_mlflow(params: Mapping[str, Any]) -> None:
    """Log parameters to MLflow, coercing unsupported value types to strings."""

    if mlflow is None or not params:
        return
    try:
        mlflow.log_params(
            {
                key: value if isinstance(value, int | float | str) else str(value)
                for key, value in params.items()
            }
        )
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug("MLflow parameter logging failed", exc_info=True)


def log_metrics_mlflow(metrics: Mapping[str, float], step: int | None = None) -> None:
    """Log metrics to MLflow if available."""

    if mlflow is None or not metrics:
        return
    try:
        mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
    except Exception:  # pragma: no cover - robustness guard
        LOGGER.debug("MLflow metric logging failed", exc_info=True)


def log_metrics(session: LoggingSession, metrics: Mapping[str, float], step: int) -> None:
    """Log scalar metrics to the configured backends."""

    if not metrics:
        return
    if session.tensorboard is not None:
        for key, value in metrics.items():
            try:
                session.tensorboard.add_scalar(key, value, step)
            except Exception as exc:  # pragma: no cover - robustness guard
                LOGGER.debug("TensorBoard logging failed for %s=%s: %s", key, value, exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("MLflow logging failed at step %s: %s", step, exc)


def shutdown_logging(session: LoggingSession) -> None:
    """Tear down logging resources gracefully."""

    if session.tensorboard is not None:
        try:
            session.tensorboard.flush()
            session.tensorboard.close()
        except Exception as exc:  # pragma: no cover - flush errors should not raise
            LOGGER.debug("TensorBoard writer shutdown encountered an error: %s", exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.end_run()
        except Exception as exc:  # pragma: no cover - offline guard
            LOGGER.debug("Failed to end MLflow run cleanly: %s", exc)


@contextmanager
def mlflow_run(
    run_name: str = "run",
    *,
    offline: bool = True,
    tracking_dir: str | Path = "./mlruns",
) -> Iterator[None]:
    """Context manager that starts an MLflow run if MLflow is available."""

    if mlflow is None:
        yield
        return

    tracking_path = Path(tracking_dir)
    if offline:
        os.environ.setdefault("MLFLOW_TRACKING_URI", f"file:{tracking_path.resolve()}")
        with suppress(Exception):  # pragma: no cover - directory creation best-effort
            tracking_path.mkdir(parents=True, exist_ok=True)

    mlflow.start_run(run_name=run_name)
    try:
        yield
    finally:
        try:
            mlflow.end_run()
        except Exception:  # pragma: no cover - best-effort shutdown
            LOGGER.debug("Failed to end MLflow run via context manager", exc_info=True)


def system_metrics() -> dict[str, Any]:
    """Return a lightweight snapshot of CPU, RAM, and optional GPU utilisation."""

    snapshot: dict[str, Any] = {"ts": time.time()}

    if psutil is not None:
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            snapshot.update(
                {
                    "cpu_percent": float(cpu_percent),
                    "ram_used_bytes": int(memory.used),
                    "ram_total_bytes": int(memory.total),
                }
            )
        except Exception:  # pragma: no cover - psutil metrics best-effort
            LOGGER.debug("psutil metrics collection failed", exc_info=True)

    if pynvml is not None:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            gpus: list[dict[str, Any]] = []
            for idx in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(idx)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpus.append(
                    {
                        "index": idx,
                        "mem_used_bytes": int(memory_info.used),
                        "mem_total_bytes": int(memory_info.total),
                    }
                )
            snapshot["gpus"] = gpus
        except Exception:  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except Exception:  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


__all__ = [
    "init_mlflow",
    "init_tensorboard",
    "LoggingConfig",
    "LoggingSession",
    "LogHandles",
    "log_metrics",
    "log_metrics_mlflow",
    "log_params_mlflow",
    "log_scalar_tb",
    "setup_logging",
    "shutdown_logging",
    "system_metrics",
    "mlflow_run",
]
