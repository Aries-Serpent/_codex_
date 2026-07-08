"""
Test Config Loading

Test module for config loading.
"""

from pathlib import Path

import pytest

from codex_ml.utils.config_loader import load_training_cfg
from omegaconf import DictConfig

CFG_DIR = Path("configs/training")
BASE = CFG_DIR / "base.yaml"


@pytest.fixture
def ensure_cfg_dir(tmp_path, monkeypatch):
    """Work inside a temp copy and redirect config loader to temp directory."""
    import codex_ml.utils.config_loader as loader_module

    tmp_repo = tmp_path / "repo"
    tmp_repo.mkdir(parents=True, exist_ok=True)

    # Create the config directory structure in temp
    tmp_cfg_dir = tmp_repo / "configs" / "training"
    tmp_cfg_dir.mkdir(parents=True, exist_ok=True)

    # Patch the module-level _CFG_DIR to point to our temp directory
    monkeypatch.setattr(loader_module, "_CFG_DIR", tmp_cfg_dir)

    monkeypatch.chdir(tmp_repo)
    yield tmp_repo


@pytest.mark.parametrize("with_file", [True, False], ids=["file_based", "no_file_fallback"])
def test_loader_file_and_fallback(ensure_cfg_dir, with_file):
    if with_file:
        CFG_DIR.mkdir(parents=True, exist_ok=True)
        BASE.write_text(
            "defaults: []\n"
            "training:\n"
            "  seed: 123\n"
            "  lr: 0.002\n"
            "  batch_size: 16\n"
            "  epochs: 1\n",
            encoding="utf-8",
        )
    else:
        if BASE.exists():
            BASE.unlink()

    cfg: DictConfig = load_training_cfg(allow_fallback=True)
    assert "training" in cfg, "Condition must be true"
    expected_lr = 0.002 if with_file else 0.001
    assert pytest.approx(cfg.training.lr) == expected_lr, "Condition must be true"


def test_compose_api_when_file_exists(ensure_cfg_dir):
    from hydra import compose, initialize_config_dir

    CFG_DIR.mkdir(parents=True, exist_ok=True)
    # Include batch_size in the config so we can override it (Hydra struct mode)
    BASE.write_text("defaults: []\ntraining:\n  lr: 0.003\n  batch_size: 4\n", encoding="utf-8")
    with initialize_config_dir(version_base=None, config_dir=str(CFG_DIR.resolve())):
        # Compose API with simple override to ensure dynamic config handling
        cfg = compose(config_name="base", overrides=["training.batch_size=8"])
    assert cfg.training.lr == 0.003, "lr is not valid"
    assert cfg.training.batch_size == 8, "batch_size is not valid"


def test_missing_config_hard_fail(ensure_cfg_dir):
    from hydra.errors import MissingConfigException

    if BASE.exists():
        BASE.unlink()
    with pytest.raises(MissingConfigException):
        load_training_cfg(allow_fallback=False)


def test_file_mode_invariant(ensure_cfg_dir):
    """Test that file mode works when config file exists."""
    from hydra import compose, initialize_config_dir

    # Create the config file in the temp directory
    CFG_DIR.mkdir(parents=True, exist_ok=True)
    BASE.write_text("defaults: []\ntraining:\n  lr: 0.001\n", encoding="utf-8")

    with initialize_config_dir(version_base=None, config_dir=str(CFG_DIR.resolve())):
        cfg = compose(config_name="base")
        assert "training" in cfg, "Condition must be true"


def test_fallback_overrides_keep_types(ensure_cfg_dir):
    if BASE.exists():
        BASE.unlink()
    cfg = load_training_cfg(
        allow_fallback=True, overrides=["training.batch_size=2", "training.lr=0.5"]
    )
    assert cfg.training.batch_size == 2, "batch_size is not valid"
    assert isinstance(cfg.training.batch_size, int)
    assert cfg.training.lr == 0.5, "lr is not valid"
    assert isinstance(cfg.training.lr, float)
