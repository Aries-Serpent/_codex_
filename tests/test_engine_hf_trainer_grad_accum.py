"""
Test Engine Hf Trainer Grad Accum

Test module for engine hf trainer grad accum.
"""

import pytest

pytest.importorskip("omegaconf")
pytest.importorskip("torch")
pytest.importorskip("transformers")
pytest.importorskip("datasets")
pytest.importorskip("accelerate")
pytest.importorskip("yaml")

from src.training.engine_hf_trainer import load_training_arguments


def test_gradient_accumulation(tmp_path):
    args = load_training_arguments(
        None, tmp_path, None, hydra_cfg={"gradient_accumulation_steps": 3}
    )
    assert args.gradient_accumulation_steps == 3, "gradient_accumulation_steps is not valid"

    alias_args = load_training_arguments(None, tmp_path, None, hydra_cfg={"grad_accum": 0})
    assert alias_args.gradient_accumulation_steps == 1, "gradient_accumulation_steps is not valid"
