import shutil
from pathlib import Path

import pytest
from omegaconf import DictConfig

from codex_ml.utils.config_loader import load_training_cfg

CFG_DIR = Path("configs/training")
BASE = CFG_DIR / "base.yaml"


@pytest.fixture
def ensure_cfg_dir(tmp_path, monkeypatch):
    """Work inside a temp copy of the repo root."""

    cwd = Path.cwd()
    tmp_repo = tmp_path / "repo"
    shutil.copytree(cwd, tmp_repo, dirs_exist_ok=True)
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
    assert "training" in cfg
    expected_lr = 0.002 if with_file else 0.001
    assert pytest.approx(cfg.training.lr) == expected_lr


def test_compose_api_when_file_exists(ensure_cfg_dir):
    from hydra import compose, initialize_config_dir

    CFG_DIR.mkdir(parents=True, exist_ok=True)
    BASE.write_text("defaults: []\ntraining:\n  lr: 0.003\n", encoding="utf-8")
    with initialize_config_dir(version_base=None, config_dir=str(CFG_DIR.resolve())):
        # Compose API with simple override to ensure dynamic config handling
        cfg = compose(config_name="base", overrides=["training.batch_size=8"])
    assert cfg.training.lr == 0.003
    assert cfg.training.batch_size == 8


def test_missing_config_hard_fail(ensure_cfg_dir):
    from hydra.errors import MissingConfigException

    if BASE.exists():
        BASE.unlink()
    with pytest.raises(MissingConfigException):
        load_training_cfg(allow_fallback=False)


@pytest.mark.skipif(not BASE.exists(), reason="Config file missing; skip file-only invariant")
def test_file_mode_invariant(ensure_cfg_dir):
    from hydra import compose, initialize_config_dir

    with initialize_config_dir(version_base=None, config_dir=str(CFG_DIR.resolve())):
        cfg = compose(config_name="base")
        assert "training" in cfg
