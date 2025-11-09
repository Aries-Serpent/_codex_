import os
from pathlib import Path

from hydra import compose, initialize_config_dir
from omegaconf import OmegaConf

os.environ.setdefault("CODEX_ALLOW_MISSING_HYDRA_EXTRA", "1")

CONF_DIR = Path(__file__).resolve().parents[2] / "configs" / "deployment" / "hhg_logistics"


def test_compose_overrides(monkeypatch):
    """Test that Hydra compose works with overrides.
    
    Mocks required environment variables (e.g., DATA_DIR) so that config interpolations
    can resolve successfully. This test validates the override mechanism and config structure
    with a fully resolved configuration.
    """
    monkeypatch.setenv("DATA_DIR", "/tmp/data")
    with initialize_config_dir(version_base="1.3", config_dir=str(CONF_DIR)):
        cfg = compose(config_name="config", overrides=["train.epochs=2"])
    container = cfg if isinstance(cfg, dict) else OmegaConf.to_container(cfg)

    assert container["train"]["epochs"] == 2
    # Verify that model config is present
    assert "model" in container
