"""
Training package public surface.
"""

from .unified_training import UnifiedTrainingConfig, run_unified_training  # re-export

__all__ = [
    "UnifiedTrainingConfig",
    "run_unified_training",
]
