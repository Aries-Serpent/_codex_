import pytest

pytest.importorskip("torch")
pytest.importorskip("transformers")

import torch

from training.engine_hf_trainer import _seed_everything


def test_seed_repeats():
    _seed_everything(123)
    a = torch.rand(5).tolist()
    _seed_everything(123)
    b = torch.rand(5).tolist()
    assert a == b
