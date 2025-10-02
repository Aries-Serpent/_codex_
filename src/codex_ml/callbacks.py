"""Minimal callback primitives shared by the training loops."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

__all__ = [
    "Callback",
    "EvaluationCallback",
    "LoggingCallback",
    "merge_callback_results",
]


class Callback:
    """Base callback with no-op hooks and lightweight error tracking."""

    def __init__(self, name: str | None = None) -> None:
        self.name = name or self.__class__.__name__

    def on_train_start(self, state: Dict[str, Any]) -> None:  # pragma: no cover - default no-op
        return None

    def on_epoch_start(
        self, epoch: int, state: Dict[str, Any]
    ) -> None:  # pragma: no cover - default no-op
        return None

    def on_epoch_end(
        self, epoch: int, metrics: Dict[str, Any], state: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:  # pragma: no cover - default no-op
        return None

    def on_train_end(self, state: Dict[str, Any]) -> None:  # pragma: no cover - default no-op
        return None

    def record_error(self, stage: str, error: Exception | str, state: Dict[str, Any]) -> None:
        """Persist a structured error entry on ``state`` for diagnostics."""

        bucket = state.setdefault("callback_errors", [])
        if not isinstance(bucket, list):
            bucket = []
            state["callback_errors"] = bucket
        bucket.append(
            {
                "callback": self.name,
                "stage": stage,
                "error": str(error),
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
        )


class EvaluationCallback(Callback):
    """
    Run a user-provided evaluation function after each epoch.

    The ``eval_fn`` signature must be ``eval_fn(epoch: int, state: Dict[str, Any])``.
    Returned dictionaries are merged under ``metrics["eval"]``.
    """

    def __init__(self, eval_fn):
        super().__init__(name="EvaluationCallback")
        self.eval_fn = eval_fn

    def on_epoch_end(self, epoch: int, metrics: Dict[str, Any], state: Dict[str, Any]):
        if self.eval_fn is None:
            return None
        try:
            eval_metrics = self.eval_fn(epoch, state)
            return {"eval": eval_metrics} if isinstance(eval_metrics, dict) else None
        except Exception as exc:  # noqa: BLE001 - propagate via error bucket
            self.record_error("on_epoch_end", exc, state)
            return {"eval_error": str(exc)}


class LoggingCallback(Callback):
    """Capture per-epoch metrics in ``state['epoch_history']``."""

    def __init__(self) -> None:
        super().__init__(name="LoggingCallback")

    def on_train_start(self, state: Dict[str, Any]) -> None:
        state.setdefault("epoch_history", [])

    def on_epoch_end(self, epoch: int, metrics: Dict[str, Any], state: Dict[str, Any]):
        history = state.get("epoch_history")
        if isinstance(history, list):
            entry = {"epoch": epoch}
            entry.update(dict(metrics))
            history.append(entry)


def merge_callback_results(base: Dict[str, Any], addon: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge callback-returned dicts into ``base`` with minimal structure."""

    if not addon:
        return base
    if not isinstance(addon, dict):
        raise TypeError("callback result must be a mapping")
    for key, value in addon.items():
        if key == "eval" and isinstance(value, dict):
            existing = base.get("eval", {})
            if isinstance(existing, dict):
                existing.update(value)
                base["eval"] = existing
            else:
                base["eval"] = value
        else:
            base[key] = value
    return base
