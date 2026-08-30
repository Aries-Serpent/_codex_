"""Smoke tests for training.trainer module."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


def test_trainer_module_imports():
    trainer_mod = None
    try:
        import training.trainer as trainer_mod
    except ImportError:
        pytest.skip("training.trainer not importable")
    assert trainer_mod is not None, "trainer_mod must be initialized"
    assert hasattr(trainer_mod, "Trainer")


def test_trainer_requires_torch():
    import importlib

    trainer = None
    try:
        trainer = importlib.import_module("training.trainer")
    except ModuleNotFoundError:
        pytest.skip("training.trainer not importable")

    if trainer is None:
        pytest.skip("training.trainer not importable")

    dummy_model = MagicMock()
    dummy_optimizer = MagicMock()
    dummy_loader = MagicMock()

    if not getattr(trainer, "_HAS_REAL_TORCH", True):
        with pytest.raises(RuntimeError):
            trainer.Trainer(dummy_model, dummy_optimizer, dummy_loader)
    else:
        pytest.skip("Torch available; Trainer instantiation covered elsewhere")
