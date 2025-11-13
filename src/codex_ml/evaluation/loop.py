"""
Evaluation loop module (Iteration 1)
CPU-safe, deterministic-ready reference implementation.

Public API:
    evaluate_epoch(model, dataloader, criterion, device="cpu",
                   metrics=None, logger=None, max_batches=None, seed=None,
                   deterministic=False) -> Dict[str, Any]

Notes:
- Lazy torch import to avoid heavy import cost if only metadata is inspected.
- Determinism: when deterministic=True, configures PyTorch deterministic algorithms;
  caller is responsible for seeded DataLoader/generator.
- Logging: Pass iterable of logger objects implementing .log(dict) and .close().
- Metrics: mapping name -> callable(outputs, targets) returning float.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Dict, Any, Optional, Protocol, Callable, List, Sequence
import time
import inspect

try:
    import torch
except ImportError:  # pragma: no cover
    torch = None  # type: ignore


class Criterion(Protocol):
    def __call__(self, outputs, targets) -> "torch.Tensor": ...


class Logger(Protocol):
    def log(self, record: Dict[str, Any]) -> None: ...
    def close(self) -> None: ...


@dataclass
class EvalResult:
    loss: float
    count: int
    metrics: Dict[str, float]
    batches: int
    duration_sec: float

    def to_dict(self) -> Dict[str, Any]:
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
            p for p in sig.parameters.values()
            if p.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
        ]
        return len(params) >= 2
    except (ValueError, TypeError):
        # If we can't inspect, assume it needs predictions
        return True


def _coerce_batch(batch: Any) -> List[Any]:
    if batch is None:
        return []
    if torch is not None and hasattr(batch, "detach"):
        data = batch.detach().cpu()
        if data.ndim == 0:
            return [data.item()]
        return data.reshape(-1).tolist()
    if isinstance(batch, (list, tuple)):
        result: List[Any] = []
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
    metrics: Optional[Dict[str, Callable]] = None,
    logger: Optional[Iterable[Logger]] = None,
    max_batches: Optional[int] = None,
    seed: Optional[int] = None,
    deterministic: bool = False,
    *,
    prediction_transform: Optional[Callable[[Any], Sequence[object]]] = None,
    target_transform: Optional[Callable[[Any], Sequence[object]]] = None,
) -> Dict[str, Any]:
    if torch is None:
        raise RuntimeError("Torch not available for evaluation.")

    # Enable deterministic mode if requested
    if deterministic:
        torch.use_deterministic_algorithms(True)
        if seed is not None:
            torch.manual_seed(seed)

    started = time.time()
    model.eval()
    running_loss = 0.0
    total = 0
    batches = 0

    # Collect predictions/targets if metrics need them
    collect_preds = metrics is not None and any(
        _check_needs_predictions(func) for func in metrics.values()
    )
    text_mode = collect_preds and (prediction_transform is not None or target_transform is not None)
    all_preds: List[Any] = []
    all_targets: List[Any] = []

    with torch.no_grad():
        for batch_idx, batch in enumerate(dataloader):
            if max_batches is not None and batch_idx >= max_batches:
                break
            batches += 1

            if isinstance(batch, (list, tuple)) and len(batch) >= 2:
                inputs, targets = batch[0], batch[1]
            else:
                raise ValueError("Dataloader must yield (inputs, targets) pairs.")

            inputs = inputs.to(device)
            targets = targets.to(device)

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
                    if torch is not None and hasattr(outputs_for_transform, "dim") and outputs_for_transform.dim() == 1:
                        outputs_for_transform = outputs_for_transform.unsqueeze(0)
                    if torch is not None and hasattr(targets_for_transform, "dim") and targets_for_transform.dim() == 0:
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
                    if hasattr(outputs, "argmax"):
                        preds = outputs.argmax(dim=-1)
                    else:
                        preds = outputs
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
                    except Exception:  # pragma: no cover (rare)
                        # Gracefully continue; avoid breaking evaluation on logger failure
                        pass

    avg_loss = running_loss / max(total, 1)

    metric_results: Dict[str, float] = {}
    if metrics:
        if text_mode:
            preds_payload: Sequence[object] = list(all_preds)
            targets_payload: Sequence[object] = list(all_targets)
            for name, fn in metrics.items():
                try:
                    metric_results[name] = _safe_item(fn(preds_payload, targets_payload))
                except Exception:
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
            except Exception:  # pragma: no cover
                pass

    return result