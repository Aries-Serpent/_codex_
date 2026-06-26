"""
Test Base Config

Test module for base config.
"""

from pathlib import Path

import pytest

pytest.importorskip("torch")
pytest.importorskip("transformers")
pytest.importorskip("datasets")
pytest.importorskip("accelerate")
pytest.importorskip("omegaconf")
pytest.importorskip("yaml")


from training.engine_hf_trainer import load_training_arguments


def test_base_config_load(tmp_path):
    cfg = load_training_arguments(
        Path("configs/training/base.yaml"),
        tmp_path,
        None,
    )
    assert cfg.output_dir == str(tmp_path), "output_dir is not valid"
    assert cfg.gradient_accumulation_steps == 1, "gradient_accumulation_steps is not valid"
    assert cfg.per_device_eval_batch_size == 8, "per_device_eval_batch_size is not valid"
    # evaluation_strategy/eval_strategy defaults depend on config;
    # base.yaml doesn't set it so the default is NO (no eval dataset configured)
    eval_strategy = getattr(cfg, "eval_strategy", None) or getattr(cfg, "evaluation_strategy", None)
    assert eval_strategy is not None, "eval_strategy must be initialized"
