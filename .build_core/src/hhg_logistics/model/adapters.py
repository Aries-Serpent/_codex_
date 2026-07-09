"""
Adapters Module

This module provides functionality for adapters.

Usage:
    from model.adapters import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

try:  # pragma: no cover - optional dependency
    from peft import PeftModel
except (IOError, OSError):  # pragma: no cover
    PeftModel = None


def load_adapters_into(base_model, adapter_dir: Path):
    """Load PEFT adapters saved via ``save_pretrained`` into an existing base model."""

    if PeftModel is None:
        raise RuntimeError("peft not installed")

    adapter_path = Path(adapter_dir)
    if not adapter_path.exists():
        raise FileNotFoundError(f"Adapter directory not found: {adapter_path}")

    logger.info("Loading adapters from %s", adapter_path)
    return PeftModel.from_pretrained(base_model, model_id=str(adapter_path), is_trainable=False)
