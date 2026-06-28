"""Lightweight logging utilities (TensorBoard + MLflow)."""

from __future__ import annotations

import importlib
import json
import logging
import os
import time
from collections.abc import Iterator, Mapping, MutableMapping
from contextlib import contextmanager, suppress
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from codex_ml.utils.optional import optional_dependency_error

try:  # pragma: no cover - tensorboard is optional in lightweight envs
    from torch.utils.tensorboard import SummaryWriter
except (IOError, OSError):  # pragma: no cover - fall back to a stub
    SummaryWriter = None

try:  # pragma: no cover - MLflow is optional for offline smoke tests
    import mlflow
except (IOError, OSError):  # pragma: no cover - guard offline runs that skip mlflow install
    mlflow = None

try:  # pragma: no cover - optional runtime dependency
    import psutil
except (ImportError, AttributeError):  # pragma: no cover - allow execution without psutil
    psutil = None

try:  # pragma: no cover - optional GPU metrics dependency
    import pynvml
except (ImportError, AttributeError):  # pragma: no cover - allow execution without NVML bindings
    pynvml = None


LOGGER = logging.getLogger(__name__)


def import_module(name: str) -> Any:
    return importlib.import_module(name)


@dataclass(slots=True)
class LoggingConfig:
    enable_tensorboard: bool = False
    tensorboard_log_dir: str = "runs"
    enable_mlflow: bool = False
    mlflow_run_name: str = "codex-training"
    mlflow_tracking_uri: str | None = None
    mlflow_offline: bool = True
    mlflow_tracking_dir: str | Path = "./mlruns"
    enable_fallback_metrics: bool = True
    fallback_metrics_path: str | Path = ".codex/metrics/metrics_fallback.ndjson"


@dataclass(slots=True)
class LoggingSession:
    tensorboard: SummaryWriter | None
    mlflow_active: bool
    fallback_writer: FallbackMetricsWriter | None


@dataclass(slots=True)
class LogHandles:
    """Lightweight container for optional logging backends."""

    tb: SummaryWriter | None = None
    mlflow_run_active: bool = False


class FallbackMetricsWriter:
    """Persist metrics to JSONL when richer telemetry backends are unavailable."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, metrics: Mapping[str, float], step: int) -> None:
        payload = {
            "ts": time.time(),
            "step": step,
            "metrics": {k: float(v) for k, v in metrics.items()},
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False))
            handle.write("\n")


def _create_tensorboard_writer(log_dir: str | Path) -> SummaryWriter | None:
    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None
    try:
        path = Path(log_dir)
        path.mkdir(parents=True, exist_ok=True)
    except (IOError, OSError) as exc:  # pragma: no cover - propagate context
        LOGGER.warning("Unable to create TensorBoard log directory '%s': %s", log_dir, exc)
        return None
    try:
        return SummaryWriter(str(path))
    except (IOError, OSError) as exc:  # pragma: no cover - e.g. tensorboard not installed
        LOGGER.warning("Failed to initialise TensorBoard writer: %s", exc)
        return None


def init_tensorboard(
    enabled: bool | str | Path,
    log_dir: str | Path | None = None,
) -> SummaryWriter | None:
    """Compatibility wrapper returning a TensorBoard writer when available."""

    if isinstance(enabled, (str, Path)):
        log_dir = enabled
        enabled_flag = True
    else:
        enabled_flag = bool(enabled)

    if not enabled_flag:
        return None
    resolved_dir = log_dir or "runs"

    if isinstance(enabled, bool):
        try:
            module = import_module("torch.utils.tensorboard")
            writer = getattr(module, "SummaryWriter", None)
        except ModuleNotFoundError:
            writer = None
        if writer is None:
            LOGGER.warning(
                "%s",
                optional_dependency_error(
                    "tensorboard",
                    purpose="TensorBoard logging",
                ),
            )
            return None
        return writer(str(resolved_dir))

    if SummaryWriter is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "tensorboard",
                purpose="TensorBoard logging",
            ),
        )
        return None

    return _create_tensorboard_writer(resolved_dir)


class MLflowHandle:
    def __init__(self, module: Any) -> None:
        self._module = module

    def log_metrics(self, metrics: Mapping[str, float], *, step: int | None = None) -> None:
        self._module.log_metrics(metrics, step=step)

    def log_params(self, params: Mapping[str, Any]) -> None:
        self._module.log_params(params)

    def end(self) -> None:
        self._module.end_run()


def _start_mlflow_run(config: LoggingConfig) -> bool:
    if not config.enable_mlflow:
        return False
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
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
    except (IOError, OSError) as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to start MLflow run '%s': %s", config.mlflow_run_name, exc)
        return False
    return True


def _create_fallback_writer(config: LoggingConfig) -> FallbackMetricsWriter | None:
    if not config.enable_fallback_metrics:
        return None
    if psutil is not None and pynvml is not None:
        return None
    try:
        return FallbackMetricsWriter(Path(config.fallback_metrics_path))
    except (IOError, OSError) as exc:  # pragma: no cover - best-effort fallback
        LOGGER.debug(
            "Unable to initialise fallback metrics writer at '%s': %s",
            config.fallback_metrics_path,
            exc,
        )
        return None


def _init_mlflow_bool(
    enabled: bool,
    run_name: str | None,
    *,
    tracking_uri: str | None,
    experiment: str | None,
) -> object | None:
    """Internal helper: initialise MLflow from a bool-mode call."""
    if not enabled:
        return None
    resolved_run = run_name or "codex-run"
    try:
        module = import_module("mlflow")
    except ModuleNotFoundError:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None
    if tracking_uri:
        module.set_tracking_uri(tracking_uri)
    if experiment:
        module.set_experiment(experiment)
    module.start_run(run_name=resolved_run)
    return MLflowHandle(module)


def _init_mlflow_experiment(
    experiment_name: str,
    run_name: str | None,
    *,
    tracking_uri: str | None,
    tags: Mapping[str, str] | None,
) -> tuple[object | None, object | None]:
    """Internal helper: initialise MLflow from a legacy experiment-name call."""
    if mlflow is None:
        LOGGER.warning(
            "%s",
            optional_dependency_error(
                "mlflow",
                purpose="experiment tracking",
            ),
        )
        return None, None
    try:
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        run = mlflow.start_run(
            run_name=run_name or experiment_name,
            tags=dict(tags) if tags else None,
        )
        return mlflow, run
    except (ValueError, TypeError, RuntimeError) as exc:  # pragma: no cover - offline guard
        LOGGER.warning("Failed to initialise MLflow for '%s': %s", experiment_name, exc)
        return mlflow, None


def init_mlflow(
    enabled: bool | str,
    run_name: str | None = None,
    *,
    tracking_uri: str | None = None,
    tags: Mapping[str, str] | None = None,
    experiment: str | None = None,
) -> object | tuple[object | None, object | None] | None:
    """Compatibility wrapper to initialise MLflow under the legacy API."""

    if isinstance(enabled, bool):
        return _init_mlflow_bool(
            enabled,
            run_name,
            tracking_uri=tracking_uri,
            experiment=experiment,
        )

    return _init_mlflow_experiment(
        enabled,
        run_name,
        tracking_uri=tracking_uri,
        tags=tags,
    )


def setup_logging(
    config: LoggingConfig | Mapping[str, object] | None,
) -> LoggingSession:
    """Initialise optional logging backends based on configuration."""

    if config is None:
        resolved = LoggingConfig()
    elif isinstance(config, LoggingConfig):
        resolved = config
    else:
        data: MutableMapping[str, object]
        if hasattr(config, "to_container"):
            data = config.to_container(resolve=True)
        else:
            # Use asdict() for dataclasses to handle slots=True compatibility
            # Fall back to dict() for regular mappings
            if hasattr(config, "__dataclass_fields__"):
                data = asdict(config)  # type: ignore[call-overload]
            else:
                data = dict(config)
        resolved = LoggingConfig(**data)  # type: ignore[arg-type]

    writer = (
        _create_tensorboard_writer(resolved.tensorboard_log_dir)
        if resolved.enable_tensorboard
        else None
    )
    mlflow_active = _start_mlflow_run(resolved)
    fallback_writer = _create_fallback_writer(resolved)
    return LoggingSession(
        tensorboard=writer,
        mlflow_active=mlflow_active,
        fallback_writer=fallback_writer,
    )


def log_scalar_tb(writer: SummaryWriter | None, tag: str, value: float, step: int) -> None:
    """Log a scalar metric to TensorBoard when a writer is provided."""

    if writer is None:
        return
    try:
        writer.add_scalar(tag, value, global_step=step)
    except (IOError, OSError):  # pragma: no cover - robustness guard
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
    except (ValueError, TypeError, RuntimeError):  # pragma: no cover - robustness guard
        LOGGER.debug("MLflow parameter logging failed", exc_info=True)


def log_metrics_mlflow(metrics: Mapping[str, float], step: int | None = None) -> None:
    """Log metrics to MLflow if available."""

    if mlflow is None or not metrics:
        return
    try:
        mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
    except (ValueError, TypeError, RuntimeError):  # pragma: no cover - robustness guard
        LOGGER.debug("MLflow metric logging failed", exc_info=True)


def log_metrics(session: LoggingSession, metrics: Mapping[str, float], step: int) -> None:
    """Log scalar metrics to the configured backends."""

    if not metrics:
        return
    if session.tensorboard is not None:
        for key, value in metrics.items():
            try:
                session.tensorboard.add_scalar(key, value, step)
            except (IOError, OSError) as exc:  # pragma: no cover - robustness guard
                LOGGER.debug("TensorBoard logging failed for %s=%s: %s", key, value, exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.log_metrics({k: float(v) for k, v in metrics.items()}, step=step)
        except (IOError, OSError) as exc:  # pragma: no cover - offline guard
            LOGGER.debug("MLflow logging failed at step %s: %s", step, exc)
    if session.fallback_writer is not None:
        session.fallback_writer.write(metrics, step)


def shutdown_logging(session: LoggingSession) -> None:
    """Tear down logging resources gracefully."""

    if session.tensorboard is not None:
        try:
            session.tensorboard.flush()
            session.tensorboard.close()
        except (IOError, OSError) as exc:  # pragma: no cover - flush errors should not raise
            LOGGER.debug("TensorBoard writer shutdown encountered an error: %s", exc)
    if session.mlflow_active and mlflow is not None:
        try:
            mlflow.end_run()
        except (IOError, OSError) as exc:  # pragma: no cover - offline guard
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
        offline_uri = f"file:{tracking_path.resolve()}"
        os.environ.setdefault("MLFLOW_TRACKING_URI", offline_uri)
        with suppress(Exception):  # pragma: no cover - directory creation best-effort
            tracking_path.mkdir(parents=True, exist_ok=True)
        with suppress(Exception):  # pragma: no cover - mlflow optional semantics
            mlflow.set_tracking_uri(offline_uri)
        with suppress(Exception):  # pragma: no cover - recreate default experiment when missing
            mlflow.set_experiment("Default")

    # End any stale active run from a previous test to prevent "run already active" errors
    with suppress(Exception):
        if mlflow.active_run() is not None:
            mlflow.end_run()
    mlflow.start_run(run_name=run_name)
    try:
        yield
    finally:
        try:
            mlflow.end_run()
        except (ValueError, TypeError, RuntimeError):  # pragma: no cover - best-effort shutdown
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
        except (
            ValueError,
            TypeError,
            RuntimeError,
        ):  # pragma: no cover - psutil metrics best-effort
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
        except (ValueError, TypeError, RuntimeError):  # pragma: no cover - NVML metrics best-effort
            LOGGER.debug("NVML metrics collection failed", exc_info=True)
        finally:
            try:
                pynvml.nvmlShutdown()
            except (IOError, OSError):  # pragma: no cover - best-effort shutdown
                LOGGER.debug("NVML shutdown failed", exc_info=True)

    return snapshot


__all__ = [
    "FallbackMetricsWriter",
    "LogHandles",
    "LoggingConfig",
    "LoggingSession",
    "init_mlflow",
    "init_tensorboard",
    "log_metrics",
    "log_metrics_mlflow",
    "log_params_mlflow",
    "log_scalar_tb",
    "mlflow_run",
    "setup_logging",
    "shutdown_logging",
    "system_metrics",
]
