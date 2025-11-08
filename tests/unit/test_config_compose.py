import os
from pathlib import Path

from hydra import compose, initialize_config_dir
from omegaconf import OmegaConf

os.environ.setdefault("CODEX_ALLOW_MISSING_HYDRA_EXTRA", "1")

CONF_DIR = Path(__file__).resolve().parents[2] / "configs" / "deployment" / "hhg_logistics"


def test_compose_overrides():
    """Test that Hydra compose works with overrides.
    
    Uses resolve=False because the config contains interpolations (e.g., ${oc.env:DATA_DIR})
    that reference environment variables not available in the test environment.
    This test validates the override mechanism and config structure without requiring
    a fully resolved configuration.
    """
    with initialize_config_dir(version_base="1.3", config_dir=str(CONF_DIR)):
        cfg = compose(config_name="config", overrides=["train.epochs=2"])
    container = cfg if isinstance(cfg, dict) else OmegaConf.to_container(cfg, resolve=False)

    assert container["train"]["epochs"] == 2
    # Verify that model config is present
    assert "model" in container
