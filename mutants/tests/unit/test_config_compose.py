"""
Test Config Compose

Test module for config compose.
"""

import os
import tempfile
from pathlib import Path

import pytest

from omegaconf import OmegaConf

# Use pytest.importorskip for collection-safe conditional imports
hydra = pytest.importorskip("hydra", reason="hydra-core not installed")

# Validate that required hydra functions are available
compose = getattr(hydra, "compose", None)
initialize_config_dir = getattr(hydra, "initialize_config_dir", None)
if compose is None or initialize_config_dir is None:
    pytest.skip("hydra compose helpers unavailable", allow_module_level=True)

os.environ.setdefault("CODEX_ALLOW_MISSING_HYDRA_EXTRA", "1")

CONF_DIR = Path(__file__).resolve().parents[2] / "configs" / "deployment" / "hhg_logistics"


def test_compose_overrides(monkeypatch):
    """Test that Hydra compose works with overrides.

    Mocks required environment variables (e.g., DATA_DIR) so that config interpolations
    can resolve successfully. This test validates the override mechanism and config structure
    with a fully resolved configuration.
    """
    monkeypatch.setenv("DATA_DIR", os.path.join(tempfile.gettempdir(), "data"))
    with initialize_config_dir(version_base="1.3", config_dir=str(CONF_DIR)):
        cfg = compose(config_name="config", overrides=["train.epochs=2"])
    container = cfg if isinstance(cfg, dict) else OmegaConf.to_container(cfg)

    assert container["train"]["epochs"] == 2, "Condition must be true"
    # Verify that model config is present
    assert "model" in container, "Condition must be true"
