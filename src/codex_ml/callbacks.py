"""
Callback / Evaluation skeleton (P1.10).

Lightweight, optional hooks for the training loop:
- on_train_start(state)
- on_epoch_start(epoch, state)
- on_epoch_end(epoch, metrics, state)
- on_train_end(state)

Evaluation:
A dedicated EvaluationCallback can compute evaluation metrics after each epoch.
Returned dict from on_epoch_end is merged under 'eval' key inside epoch metrics.

Design Goals:
- Zero cost when not used.
- Backward compatible: training loop works without callbacks.
- Simple state dict (mutable) shared across callbacks.

Future Extensions (deferred):
- Ordered execution priorities
- Exception handling policies
- Asynchronous evaluation
"""

from __future__ import annotations
from typing import Dict, Any, Optional, List

__all__ = [
    "Callback",
    "EvaluationCallback",
    "LoggingCallback",
    "merge_callback_results",
]


class Callback:
    """Base callback with no-op hooks."""

    def on_train_start(self, state: Dict[str, Any]) -> None:
        pass

    def on_epoch_start(self, epoch: int, state: Dict[str, Any]) -> None:
        pass

    def on_epoch_end(self, epoch: int, metrics: Dict[str, Any], state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return None

    def on_train_end(self, state: Dict[str, Any]) -> None:
        pass


class EvaluationCallback(Callback):
    """
    Run a user-provided evaluation function after each epoch.

    eval_fn signature:
        eval_fn(epoch: int, state: Dict[str, Any]) -> Dict[str, Any]

    Returned dict is nested under metrics['eval'].
    """

    def __init__(self, eval_fn):
        self.eval_fn = eval_fn

    def on_epoch_end(self, epoch: int, metrics: Dict[str, Any], state: Dict[str, Any]):
        if self.eval_fn is None:
            return None
        try:
            eval_metrics = self.eval_fn(epoch, state)
            return {"eval": eval_metrics} if isinstance(eval_metrics, dict) else None
        except Exception as e:  # noqa: broad-except
            return {"eval_error": str(e)}


class LoggingCallback(Callback):
    """Simple callback capturing per-epoch metrics history into state['epoch_history'] list."""

    def on_train_start(self, state: Dict[str, Any]) -> None:
        state.setdefault("epoch_history", [])

    def on_epoch_end(self, epoch: int, metrics: Dict[str, Any], state: Dict[str, Any]):
        history = state.get("epoch_history")
        if isinstance(history, list):
            history.append({"epoch": epoch, **metrics})


def merge_callback_results(base: Dict[str, Any], addon: Optional[Dict[str, Any]]):
    """
    Merge callback-returned dict into base metrics (shallow).
    Does not deep-merge nested maps except for 'eval' dict.
    """
    if not addon:
        return
    for k, v in addon.items():
        if k == "eval" and isinstance(v, dict):
            existing = base.get("eval", {})
            if isinstance(existing, dict):
                existing.update(v)
                base["eval"] = existing
            else:
                base["eval"] = v
        else:
            base[k] = v