import os
from pathlib import Path

from hydra import compose, initialize_config_dir
from omegaconf import OmegaConf

os.environ.setdefault("CODEX_ALLOW_MISSING_HYDRA_EXTRA", "1")

# Use absolute path resolved from test location for initialize_config_dir
CONF_DIR = Path(__file__).resolve().parents[2] / "configs" / "deployment" / "hhg_logistics"


def test_compose_overrides():
    with initialize_config_dir(version_base="1.3", config_dir=str(CONF_DIR)):
        cfg = compose(config_name="config", overrides=["train.epochs=2", "model=baseline"])
    # Don't resolve interpolations to avoid config dependency issues
    container = cfg if isinstance(cfg, dict) else OmegaConf.to_container(cfg, resolve=False)

    assert container["train"]["epochs"] == 2
    model_section = container.get("model")
    if isinstance(model_section, dict):
        assert model_section.get("type") == "BaselineModel"
    else:
        assert model_section == "baseline"
