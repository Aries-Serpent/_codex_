"""
Evaluation loop module (Iteration 1)
CPU-safe, deterministic reference implementation.

Public API:
    evaluate_epoch(model, dataloader, criterion, device="cpu",
                   metrics=None, logger=None, max_batches=None, seed=None) -> Dict[str, Any]

Notes:
- Lazy torch import to avoid heavy import cost if only metadata is inspected.
- Determinism: optional seed applied to DataLoader generator (caller must construct with generator).
- Logging: Pass iterable of logger objects implementing .log(dict) and .close().
- Metrics: mapping name -> callable(outputs, targets) returning float.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Dict, Any, Optional, Protocol, Callable, List
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


def evaluate_epoch(
    model,
    dataloader: Iterable,
    criterion: Criterion,
    device: str = "cpu",
    metrics: Optional[Dict[str, Callable]] = None,
    logger: Optional[Iterable[Logger]] = None,
    max_batches: Optional[int] = None,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    if torch is None:
        raise RuntimeError("Torch not available for evaluation.")

    started = time.time()
    model.eval()
    running_loss = 0.0
    total = 0
    batches = 0

    # Collect predictions/targets if metrics need them
    collect_preds = metrics is not None and any(
        _check_needs_predictions(func) for func in metrics.values()
    )
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
            running_loss += loss_value * targets.size(0)
            total += targets.size(0)

            if collect_preds:
                # Use argmax classification assumption; adapt later for regression
                if hasattr(outputs, "argmax"):
                    preds = outputs.argmax(dim=-1)
                else:
                    preds = outputs
                all_preds.append(preds.detach().cpu())
                all_targets.append(targets.detach().cpu())

            if logger:
                record = {
                    "type": "batch",
                    "batch_index": batch_idx,
                    "loss": loss_value,
                    "count": int(targets.size(0)),
                    "cumulative_loss": running_loss,
                    "cumulative_count": total,
                    "wall_time": time.time(),
                }
                for lg in logger:
                    try:
                        lg.log(record)
                    except Exception as e:  # pragma: no cover (rare)
                        # Gracefully continue; avoid breaking evaluation on logger failure
                        pass

    avg_loss = running_loss / max(total, 1)

    metric_results: Dict[str, float] = {}
    if metrics:
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