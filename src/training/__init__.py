"""Training utilities supporting offline audits."""

from .trainer import CheckpointConfig, Trainer, TrainerConfig

# Preserve the historical ``ExtendedTrainer`` alias for downstream imports. This mirrors
# the public API exposed by :mod:`src.training.trainer` while remaining resilient if the
# alias is ever dropped from the underlying module.
ExtendedTrainer = Trainer

__all__ = [
    "CheckpointConfig",
    "ExtendedTrainer",
    "Trainer",
    "TrainerConfig",
]
