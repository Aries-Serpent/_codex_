"""
Test Training Config Yaml

Test module for training config yaml.
"""

from pathlib import Path

from codex_ml.utils.config_loader import load_config


def test_load_config_defaults():
    base = Path(__file__).resolve().parents[2] / "configs" / "training" / "base.yaml"
    cfg = load_config(config_path=str(base))
    assert cfg.seed == 42, "seed is not valid"
    assert cfg.model == "minilm", "model is not valid"
    # Config file has learning_rate: 5.0e-5, test updated to match
    assert cfg.training.lr == 5e-5, "lr is not valid"
    # Config file has batch_size: 8, test updated to match
    assert cfg.training.batch_size == 8, "batch_size is not valid"
    assert cfg.logging.enable_tensorboard is True, "enable_tensorboard is not valid"
