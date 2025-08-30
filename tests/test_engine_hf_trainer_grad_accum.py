from pathlib import Path

from training.engine_hf_trainer import load_training_arguments


def test_gradient_accumulation(tmp_path):
    args = load_training_arguments(None, tmp_path, None, gradient_accumulation_steps=3)
    assert args.gradient_accumulation_steps == 3
