"""Compat re-export for legacy imports of ``configs.base_config``."""

from .base.base_config import BASE_TRAINING_CONFIG, get_base_training_config

__all__ = ["BASE_TRAINING_CONFIG", "get_base_training_config"]
