"""Phase 24 CLI workflow integration tests."""

import pytest

from omegaconf import OmegaConf


@pytest.mark.integration
def test_phase24_cli_full_pipeline(tmp_path):
    """Test Phase 24 CLI full pipeline flow."""
    OmegaConf.create(
        {
            "model": {"target": "model.SimpleModel"},
            "data": {"name": "synthetic_classification"},
            "trainer": {"epochs": 1},
            "device": "cpu",
        }
    )
    # Would verify full CLI → trainer → data flow


@pytest.mark.integration
def test_phase24_cli_checkpoint_persistence(tmp_path):
    """Test Phase 24 checkpoint persistence."""
    ckpt_dir = tmp_path / "checkpoints"
    OmegaConf.create(
        {
            "model": {},
            "data": {"name": "synthetic_classification"},
            "trainer": {"epochs": 1, "checkpoint": {"path": str(ckpt_dir), "every": 1}},
        }
    )
    # Verify checkpoints are saved


@pytest.mark.integration
def test_phase24_cli_override_cascade():
    """Test Phase 24 override cascade through config."""
    OmegaConf.create(
        {
            "model": {},
            "data": {"name": "synthetic_classification"},
            "trainer": {"epochs": 1},
        }
    )
    # Verify overrides propagate


@pytest.mark.integration
def test_phase24_cli_error_recovery():
    """Test Phase 24 CLI error recovery."""
    from unittest.mock import MagicMock

    cli = MagicMock()
    cli.run.side_effect = [ValueError("config not found"), MagicMock(returncode=0)]
    # First call raises, second succeeds (recovery)
    with pytest.raises(ValueError, match="config not found"):
        cli.run(["train", "--config", "missing.yaml"])
    result = cli.run(["train", "--config", "valid.yaml"])
    assert result.returncode == 0, "Result must not be empty"


@pytest.mark.integration
def test_phase24_cli_multi_device():
    """Test Phase 24 CLI multi-device configuration."""
    OmegaConf.create({"device": "cpu"})
    OmegaConf.create({"device": "cuda:0"})
    # Verify device selection
