from __future__ import annotations

from typing import Optional

try:  # pragma: no cover - optional dependency
    from torch.utils.tensorboard import SummaryWriter  # type: ignore
except Exception:  # pragma: no cover - optional dependency path
    SummaryWriter = None  # type: ignore[assignment]


class TBWriter:
    """Minimal TensorBoard wrapper that degrades to a no-op when unavailable."""

    def __init__(self, enabled: bool, logdir: str = "runs/codex") -> None:
        self.enabled = bool(enabled and SummaryWriter is not None)
        self._writer: Optional[SummaryWriter] = None
        if self.enabled and SummaryWriter is not None:
            try:
                self._writer = SummaryWriter(log_dir=logdir)
            except Exception:  # pragma: no cover - tensorboard initialisation failures
                self._writer = None

    def add_scalar(self, tag: str, value: float, step: int) -> None:
        if self._writer is None:
            return
        try:
            self._writer.add_scalar(tag, value, step)
        except Exception:  # pragma: no cover - tensorboard runtime errors
            pass

    def close(self) -> None:
        if self._writer is None:
            return
        try:
            self._writer.flush()
        except Exception:  # pragma: no cover - flushing is best-effort
            pass
        try:
            self._writer.close()
        except Exception:  # pragma: no cover - closing is best-effort
            pass


__all__ = ["TBWriter"]
