"""Logging registry scaffolding for _codex_.

Provides a simple in-memory registry of logger-like callables. Real
implementations can plug in TensorBoard, MLflow, or other backends in offline
mode.
"""

from typing import Callable, Dict

_LOGGERS: Dict[str, Callable[[str], None]] = {}


def register_logger(name: str, fn: Callable[[str], None]) -> None:
    _LOGGERS[name] = fn


def get_logger(name: str) -> Callable[[str], None]:
    return _LOGGERS.get(name, lambda msg: None)
