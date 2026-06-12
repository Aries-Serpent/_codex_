"""Smoke tests for training.simple_trainer module."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


def test_simple_trainer_imports():
    simple_trainer = pytest.importorskip("training.simple_trainer")
    assert hasattr(simple_trainer, "SimpleTrainer")


def test_simple_trainer_requires_torch():
    module = pytest.importorskip("training.simple_trainer")
    mock_model = MagicMock()
    mock_optimizer = MagicMock()

    if getattr(module, "torch", None) is None:
        with pytest.raises(RuntimeError):
            module.SimpleTrainer(mock_model, mock_optimizer)
    else:
        pytest.skip("Torch available; skipping runtime error assertion")
