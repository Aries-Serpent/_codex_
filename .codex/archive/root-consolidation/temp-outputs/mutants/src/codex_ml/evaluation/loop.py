"""
Evaluation loop module (Iteration 1)
CPU-safe, deterministic-ready reference implementation.

Public API:
    evaluate_epoch(model, dataloader, criterion, device="cpu",
                    metrics=None, logger=None, max_batches=None, seed=None,
                    deterministic=False) -> dict[str, Any]

Notes:
- Lazy torch import to avoid heavy import cost if only metadata is inspected.
- Determinism: when deterministic=True, configures PyTorch deterministic algorithms;
  caller is responsible for seeded DataLoader/generator.
- Logging: Pass iterable of logger objects implementing .log(dict) and .close().
- Metrics: mapping name -> callable(outputs, targets) returning float.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)
_log = logger  # avoid shadowing by the `logger` parameter accepted by evaluate_epoch()

import inspect  # noqa: E402
import os  # noqa: E402
import time  # noqa: E402
from collections.abc import Callable, Iterable, Sequence  # noqa: E402
from dataclasses import dataclass  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import (  # noqa: E402
    Any,
    Optional,
    Protocol,
    runtime_checkable,
)
from uuid import uuid4  # noqa: E402

from codex_ml.metrics.api import get_metric  # noqa: E402
from codex_ml.metrics.writers import (  # noqa: E402
    BaseMetricsWriter,
)
from codex_ml.tracking.offline import decide_offline  # noqa: E402
from codex_ml.training.engine import TrainingEngine  # noqa: E402

try:
    import torch
except ImportError:  # pragma: no cover
    torch = None  # type: ignore[assignment]


@runtime_checkable
class Criterion(Protocol):
    def __call__(self, outputs, targets) -> torch.Tensor:
        """Compute loss given model outputs and ground-truth targets."""


@runtime_checkable
class Logger(Protocol):
    def log(self, record: dict[str, Any]) -> None:
        """Log a single evaluation record."""

    def close(self) -> None:
        """Flush and close the logger."""


@dataclass
class EvalResult:
    loss: float
    count: int
    metrics: dict[str, float]
    batches: int
    duration_sec: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "loss": self.loss,
            "count": self.count,
            "metrics": self.metrics,
            "batches": self.batches,
            "duration_sec": round(self.duration_sec, 6),
        }


def _safe_item(x) -> float:
    if hasattr(x, "item"):
        try:
            return float(x.item())
        except Exception:
            _log.warning("Exception occurred", exc_info=True)
            return float(x)
    return float(x)


def _check_needs_predictions(func: Callable) -> bool:
    """
    Check if a metric callable needs prediction/target arguments.
    Uses inspect.signature to handle functions, partials, methods, and callable objects.
    """
    try:
        sig = inspect.signature(func)
        # Count parameters (excluding self/cls and var-positional/keyword)
        params = [
            p
            for p in sig.parameters.values()
            if p.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
        ]
        return len(params) >= 2
    except (ValueError, TypeError):
        # If we can't inspect, assume it needs predictions
        return True


def _coerce_batch(batch: Any) -> list[Any]:
    if batch is None:
        return []
    if torch is not None and hasattr(batch, "detach"):
        data = batch.detach().cpu()
        if data.ndim == 0:
            return [data.item()]
        return data.reshape(-1).tolist()
    if isinstance(batch, (list, tuple)):
        result: list[Any] = []
        for item in batch:
            result.extend(_coerce_batch(item))
        return result
    if isinstance(batch, str):
        return [batch]
    return [batch]


def _batch_size(batch: Any) -> int:
    if torch is not None and hasattr(batch, "dim"):
        if batch.dim() == 0:
            return 1
        return int(batch.size(0))
    if isinstance(batch, (list, tuple)):
        return len(batch)
    return 1


def evaluate_epoch(
    model,
    dataloader: Iterable,
    criterion: Criterion,
    device: str = "cpu",
    metrics: Optional[dict[str, Callable]] = None,
    logger: Optional[Iterable[Logger]] = None,
    max_batches: Optional[int] = None,
    seed: Optional[int] = None,
    deterministic: bool = False,
    *,
    prediction_transform: Optional[Callable[[Any], Sequence[object]]] = None,
    target_transform: Optional[Callable[[Any], Sequence[object]]] = None,
) -> dict[str, Any]:
    if torch is None:
        raise RuntimeError("Torch not available for evaluation.")

    # Enable deterministic mode if requested
    if deterministic:
        torch.use_deterministic_algorithms(True)
        if seed is not None:
            torch.manual_seed(seed)

    started = time.time()
    target_device = torch.device(device)
    model = model.to(target_device)
    model.eval()
    running_loss = 0.0
    total = 0
    batches = 0

    # Collect predictions/targets if metrics need them
    collect_preds = metrics is not None and any(
        _check_needs_predictions(func) for func in metrics.values()
    )
    text_mode = collect_preds and (prediction_transform is not None or target_transform is not None)
    all_preds: list[Any] = []
    all_targets: list[Any] = []

    with torch.no_grad():
        for batch_idx, batch in enumerate(dataloader):
            if max_batches is not None and batch_idx >= max_batches:
                break
            batches += 1

            if isinstance(batch, (list, tuple)) and len(batch) >= 2:
                inputs, targets = batch[0], batch[1]
            else:
                raise ValueError("Dataloader must yield (inputs, targets) pairs.")

            inputs = inputs.to(target_device)
            targets = targets.to(target_device)

            outputs = model(inputs)
            loss = criterion(outputs, targets)
            loss_value = _safe_item(loss)
            batch_count = _batch_size(targets)
            running_loss += loss_value * batch_count
            total += batch_count

            if collect_preds:
                if text_mode:
                    outputs_for_transform = outputs
                    targets_for_transform = targets
                    if (
                        torch is not None
                        and hasattr(outputs_for_transform, "dim")
                        and outputs_for_transform.dim() == 1
                    ):
                        outputs_for_transform = outputs_for_transform.unsqueeze(0)
                    if (
                        torch is not None
                        and hasattr(targets_for_transform, "dim")
                        and targets_for_transform.dim() == 0
                    ):
                        targets_for_transform = targets_for_transform.unsqueeze(0)
                    batch_preds = (
                        prediction_transform(outputs_for_transform)
                        if prediction_transform
                        else outputs_for_transform
                    )
                    batch_targets = (
                        target_transform(targets_for_transform)
                        if target_transform
                        else targets_for_transform
                    )
                    all_preds.extend(_coerce_batch(batch_preds))
                    all_targets.extend(_coerce_batch(batch_targets))
                else:
                    # Use argmax classification assumption; adapt later for regression
                    preds = outputs.argmax(dim=-1) if hasattr(outputs, "argmax") else outputs
                    pred_tensor = preds.detach().cpu()
                    if pred_tensor.ndim == 0:
                        pred_tensor = pred_tensor.reshape(1)
                    else:
                        pred_tensor = pred_tensor.reshape(-1)
                    target_tensor = targets.detach().cpu()
                    if target_tensor.ndim == 0:
                        target_tensor = target_tensor.reshape(1)
                    else:
                        target_tensor = target_tensor.reshape(-1)
                    all_preds.append(pred_tensor)
                    all_targets.append(target_tensor)

            if logger:
                record = {
                    "type": "batch",
                    "batch_index": batch_idx,
                    "loss": loss_value,
                    "count": _batch_size(targets),
                    "cumulative_loss": running_loss,
                    "cumulative_count": total,
                    "wall_time": time.time(),
                }
                for lg in logger:
                    try:
                        lg.log(record)
                    except (ValueError, TypeError, RuntimeError):  # pragma: no cover (rare)
                        # Gracefully continue; avoid breaking evaluation on logger failure
                        logger.debug("Suppressed exception in handler", exc_info=True)  # type: ignore[attr-defined]
    avg_loss = running_loss / max(total, 1)

    metric_results: dict[str, float] = {}
    if metrics:
        if text_mode:
            preds_payload: Sequence[object] = list(all_preds)
            targets_payload: Sequence[object] = list(all_targets)
            for name, fn in metrics.items():
                try:
                    metric_results[name] = _safe_item(fn(preds_payload, targets_payload))
                except (ValueError, TypeError):
                    _log.warning("Exception occurred", exc_info=True)
                    metric_results[name] = float("nan")
        else:
            preds_cat = torch.cat(all_preds) if all_preds else None
            targets_cat = torch.cat(all_targets) if all_targets else None
            for name, fn in metrics.items():
                try:
                    if preds_cat is not None and targets_cat is not None:
                        metric_results[name] = _safe_item(fn(preds_cat, targets_cat))
                    else:
                        metric_results[name] = float("nan")
                except Exception:
                    _log.warning("Exception occurred", exc_info=True)
                    metric_results[name] = float("nan")

    result = EvalResult(
        loss=avg_loss,
        count=total,
        metrics=metric_results,
        batches=batches,
        duration_sec=time.time() - started,
    ).to_dict()

    if logger:
        epoch_record = {
            "type": "epoch",
            **result,
            "wall_time": time.time(),
        }
        for lg in logger:
            try:
                lg.log(epoch_record)
                lg.close()
            except (ValueError, TypeError, RuntimeError):  # pragma: no cover
                logger.debug("Suppressed exception in handler", exc_info=True)  # type: ignore[attr-defined]
    return result


def _resolve_metric_functions(
    metric_specs: dict[str, Callable] | Iterable[str | Callable],
) -> dict[str, Callable]:
    """Coerce metric specifications into callable form using the registry."""

    resolved: dict[str, Callable] = {}
    if isinstance(metric_specs, dict):
        items = metric_specs.items()
    else:
        items = ((getattr(fn, "__name__", str(fn)), fn) for fn in metric_specs)  # type: ignore[assignment]
    for name, fn in items:
        if isinstance(fn, str):
            resolved[name] = get_metric(fn)
        else:
            resolved[name] = fn
    return resolved


def _collect_system_metrics() -> dict[str, float]:
    """Best-effort system metrics (CPU/memory) without network calls."""

    cpu_percent = None
    memory_percent = None
    try:  # pragma: no cover - optional dependency path
        import psutil

        cpu_percent = float(psutil.cpu_percent(interval=None))
        memory_percent = float(psutil.virtual_memory().percent)
    except (IOError, OSError) as e:
        type(e).__name__
        logger.debug("Exception: <ERROR_TYPE>")
        logger.warning("Exception: <ERROR_TYPE>", exc_info=True)

    metrics: dict[str, float] = {}
    if cpu_percent is not None:
        metrics["system.cpu_percent"] = cpu_percent
    if memory_percent is not None:
        metrics["system.memory_percent"] = memory_percent
    return metrics


def run_metrics_evaluation(
    data: Iterable[tuple[Any, Any]],
    metric_specs: dict[str, Callable] | Iterable[str | Callable],
    *,
    metric_writers: Iterable[BaseMetricsWriter] | None = None,
    run_id: str | None = None,
    log_system_metrics: bool = True,
    enable_mlflow: bool = True,
    mlruns_dir: str | Path = "mlruns",
) -> dict[str, float]:
    """Evaluate predictions against targets using registry-backed metrics.

    Parameters
    ----------
    data:
        Iterable of ``(prediction, target)`` tuples.
    metric_specs:
        Mapping of metric name to callable or iterable of names/callables. Metric
        names are resolved through :mod:`codex_ml.metrics.api`.
    metric_writers:
        Optional collection of metrics writers (NDJSON/CSV) that receive structured
        records tagged with run id, step, and metric name.
    run_id:
        Optional run identifier. When omitted, a stable offline-safe id is
        generated.
    log_system_metrics:
        When ``True`` capture CPU/memory utilisation and emit to writers and the
        returned summary.
    enable_mlflow:
        When ``True`` attempt offline MLflow logging using :class:`TrainingEngine`.
        This is a best-effort operation; if mlflow is unavailable no error is
        raised.
    mlruns_dir:
        Path to the offline MLflow store used when ``enable_mlflow`` is true.
    """

    resolved_metrics = _resolve_metric_functions(metric_specs)
    run_identifier = run_id or os.getenv("CODEX_RUN_ID") or f"eval-{uuid4().hex}"
    writers = list(metric_writers or [])

    preds: list[Any] = []
    targets: list[Any] = []

    for step, pair in enumerate(data):
        try:
            pred, target = pair
        except Exception as exc:  # pragma: no cover - defensive unpacking
            raise ValueError("Each evaluation item must be a (prediction, target) tuple") from exc
        preds.append(pred)
        targets.append(target)

        for name, fn in resolved_metrics.items():
            try:
                value = float(fn([pred], [target]))
            except Exception:
                _log.warning("Exception occurred", exc_info=True)
                value = float("nan")
            record = {
                "metric": name,
                "value": value,
                "step": step,
                "split": "eval",
                "run_id": run_identifier,
                "tags": {"metric": name, "step": step, "phase": "per-sample"},
            }
            for writer in writers:
                writer.write(record)

    final_metrics: dict[str, float] = {}
    for name, fn in resolved_metrics.items():
        try:
            final_metrics[name] = float(fn(preds, targets))
        except Exception:
            _log.warning("Exception occurred", exc_info=True)
            final_metrics[name] = float("nan")

    summary_record = {
        "metric": "aggregate",
        "value": 1.0,
        "step": len(preds),
        "split": "eval",
        "run_id": run_identifier,
        "tags": {"phase": "summary", "step": len(preds)},
        "metrics": final_metrics,
    }

    system_metrics = _collect_system_metrics() if log_system_metrics else {}
    if system_metrics:
        summary_record["system"] = system_metrics

    for writer in writers:
        writer.write(summary_record)
        writer.close()

    mlflow_info: dict[str, str] = {}
    if enable_mlflow:
        decision = decide_offline(prefer_offline=True, allow_remote=False, mlruns_dir=mlruns_dir)
        os.environ["MLFLOW_TRACKING_URI"] = decision.mlflow_tracking_uri
        tracker = TrainingEngine(enable_mlflow=True, mlflow_dir=str(Path(mlruns_dir)))
        tracker.start_run(params={"run_id": run_identifier}, tags={"mode": "evaluation"})
        tracker.log_metrics(final_metrics, step=len(preds))
        tracker.end_run()
        if tracker.mlflow_error:
            mlflow_info["mlflow_error"] = tracker.mlflow_error
        mlflow_info["mlflow_tracking_uri"] = decision.mlflow_tracking_uri

    return {
        "run_id": run_identifier,  # type: ignore[dict-item]
        "metrics": final_metrics,  # type: ignore[dict-item]
        "system": system_metrics,  # type: ignore[dict-item]
        **({"mlflow": mlflow_info} if mlflow_info else {}),  # type: ignore[dict-item]
    }
