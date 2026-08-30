"""
Base Module

This module provides functionality for base.

Usage:
    from callbacks.base import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

from datetime import UTC, datetime  # noqa: E402
from typing import Any, Optional  # noqa: E402

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

    def on_train_start(self, state: dict[str, Any]) -> None:  # pragma: no cover - default no-op
        return None

    def on_epoch_start(
        self, epoch: int, state: dict[str, Any]
    ) -> None:  # pragma: no cover - default no-op
        return None

    def on_epoch_end(
        self, epoch: int, metrics: dict[str, Any], state: dict[str, Any]
    ) -> Optional[dict[str, Any]]:  # pragma: no cover - default no-op
        return None

    def on_train_end(self, state: dict[str, Any]) -> None:  # pragma: no cover - default no-op
        return None

    def record_error(self, stage: str, error: Exception | str, state: dict[str, Any]) -> None:
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
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )


class EvaluationCallback(Callback):
    """
    Run a user-provided evaluation function after each epoch.

    The ``eval_fn`` signature must be ``eval_fn(epoch: int, state: dict[str, Any])``.
    Returned dictionaries are merged under ``metrics["eval"]``.
    """

    def __init__(self, eval_fn) -> None:
        super().__init__(name="EvaluationCallback")
        self.eval_fn = eval_fn

    def on_epoch_end(self, epoch: int, metrics: dict[str, Any], state: dict[str, Any]):
        if self.eval_fn is None:
            return None
        try:
            eval_metrics = self.eval_fn(epoch, state)
            return {"eval": eval_metrics} if isinstance(eval_metrics, dict) else None
        except Exception as exc:
            self.record_error("on_epoch_end", exc, state)
            return {"eval_error": str(exc)}


class LoggingCallback(Callback):
    """Capture per-epoch metrics in ``state['epoch_history']``."""

    def __init__(self) -> None:
        super().__init__(name="LoggingCallback")

    def on_train_start(self, state: dict[str, Any]) -> None:
        state.setdefault("epoch_history", [])

    def on_epoch_end(self, epoch: int, metrics: dict[str, Any], state: dict[str, Any]):
        history = state.get("epoch_history")
        if isinstance(history, list):
            entry = {"epoch": epoch}
            entry.update(dict(metrics))
            history.append(entry)


def merge_callback_results(base: dict[str, Any], addon: Optional[dict[str, Any]]) -> dict[str, Any]:
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
