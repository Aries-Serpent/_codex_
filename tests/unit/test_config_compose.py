import importlib
import os
from pathlib import Path

import pytest
from omegaconf import OmegaConf


def _load_hydra():
    try:
        spec = importlib.util.find_spec("hydra")
    except ValueError:
        spec = None
    if spec is None:
        pytest.skip("hydra-core not installed", allow_module_level=True)
    module = importlib.import_module("hydra")
    compose_fn = getattr(module, "compose", None)
    init_dir = getattr(module, "initialize_config_dir", None)
    if compose_fn is None or init_dir is None:
        pytest.skip("hydra compose helpers unavailable", allow_module_level=True)
    return compose_fn, init_dir


compose, initialize_config_dir = _load_hydra()

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
