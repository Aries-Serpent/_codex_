"""Evaluation utilities and runners."""

from . import metrics

try:  # pragma: no cover - optional heavy dependencies
    from . import eval_runner
except Exception:  # pragma: no cover - torch/datasets may be missing
    eval_runner = None  # type: ignore

try:  # pragma: no cover - new structured runner
    from . import runner
except Exception:  # pragma: no cover
    runner = None  # type: ignore

__all__ = ["metrics"]
if eval_runner is not None:
    __all__.append("eval_runner")
if runner is not None:
    __all__.append("runner")
