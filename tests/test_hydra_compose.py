from __future__ import annotations

from pathlib import Path

from hydra import compose, initialize_config_dir
from omegaconf import DictConfig


def _config_dir() -> str:
    return str(Path(__file__).resolve().parent.parent / "configs")


def test_compose_base_cfg() -> None:
    with initialize_config_dir(version_base="1.3", config_dir=_config_dir()):
        cfg: DictConfig = compose(config_name="training/functional_base")
    assert cfg.training.seed == 42
    assert cfg.training.gradient_accumulation >= 1
    assert cfg.dataset.train_path


def test_override_flags() -> None:
    with initialize_config_dir(version_base="1.3", config_dir=_config_dir()):
        cfg: DictConfig = compose(
            config_name="training/functional_base",
            overrides=[
                "training.max_epochs=2",
                "training.amp_enable=true",
                "hydra.run.dir=.",
                "hydra.output_subdir=null",
            ],
        )
    assert cfg.training.max_epochs == 2
    assert cfg.training.amp_enable is True
