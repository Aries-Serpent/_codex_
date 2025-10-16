"""Compatibility shims for legacy ``training`` imports."""

import sys as _sys

from src.training import trainer as _extended_trainer_module
from src.training.trainer import CheckpointConfig, ExtendedTrainer, TrainerConfig

_sys.modules.setdefault("training.trainer", _extended_trainer_module)

__all__ = ["CheckpointConfig", "ExtendedTrainer", "TrainerConfig"]
