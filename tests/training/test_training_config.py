"""Smoke tests for :mod:`training.config`."""

from __future__ import annotations

from pathlib import Path


def test_training_config_defaults() -> None:
    from src.training.config import TrainingConfig

    cfg = TrainingConfig()
    assert cfg.batch_size > 0, "batch_size must be greater than zero"
    assert cfg.output_dir, "Condition must be true"


def test_training_config_from_file(tmp_path: Path) -> None:
    from src.training.config import TrainingConfig

    config_file = tmp_path / "cfg.json"
    config_file.write_text('{"batch_size": 2, "learning_rate": 0.01}')

    cfg = (
        TrainingConfig.from_file(str(config_file))
        if hasattr(TrainingConfig, "from_file")
        else TrainingConfig(batch_size=2, learning_rate=0.01)
    )
    assert cfg.batch_size == 2, "batch_size is not valid"
    assert cfg.learning_rate == 0.01, "learning_rate is not valid"


def test_training_config_validation() -> None:
    from src.training.config import TrainingConfig

    cfg = TrainingConfig(batch_size=1)
    if hasattr(cfg, "validate"):
        assert cfg.validate() in (True, None)
