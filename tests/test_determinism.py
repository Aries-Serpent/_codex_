"""
Test Determinism

Test module for determinism.
"""

import pytest

pytest.importorskip("torch")
pytest.importorskip("transformers")
pytest.importorskip("datasets")
pytest.importorskip("accelerate")
pytest.importorskip("yaml")

import torch  # noqa: E402
from src.training.engine_hf_trainer import _seed_everything  # noqa: E402


def test_seed_repeats():
    _seed_everything(123)
    a = torch.rand(5).tolist()
    _seed_everything(123)
    b = torch.rand(5).tolist()
    assert a == b
