from pathlib import Path

from codex_ml.utils.config_loader import load_config


def test_load_config_defaults():
    base = Path(__file__).resolve().parents[2] / "configs" / "training" / "base.yaml"
    cfg = load_config(config_path=str(base))
    assert cfg.seed == 42
    assert cfg.model == "minilm"
    assert cfg.training.lr == 3e-4
    assert cfg.training.batch_size == 32
    assert cfg.logging.enable_tensorboard is True
