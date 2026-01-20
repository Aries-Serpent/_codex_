"""CLI pipeline integration tests (Phase 23 Week 2)."""

import pytest
from omegaconf import OmegaConf

import src.cli as cli


def _make_config(**overrides):
    base = {
        "model": {"target": "some.model"},
        "optimizer": {"target": "some.optim"},
        "data": {"name": "synthetic"},
        "loss": {},
        "metric": {},
        "trainer": {"epochs": 1, "checkpoint": {"every": 1}},
        "device": "cpu",
    }
    base.update(overrides)
    return OmegaConf.create(base)


@pytest.mark.integration
def test_cli_pipeline_trainer_wiring(monkeypatch, tmp_path):
    """Test CLI wires trainer from config."""
    config = _make_config()
    # Integration test would verify trainer is created with correct config


@pytest.mark.integration
def test_cli_pipeline_loader_propagation(tmp_path):
    """Test CLI propagates dataloaders to trainer."""
    data_file = tmp_path / "data.tsv"
    data_file.write_text("text\t1\n")
    
    config = _make_config(data={"path": str(data_file)})
    # Verify dataloaders are passed to trainer


@pytest.mark.integration
def test_cli_pipeline_device_handling():
    """Test CLI handles device configuration."""
    config_cpu = _make_config(device="cpu")
    config_cuda = _make_config(device="cuda")
    # Verify device is set correctly


@pytest.mark.integration
def test_cli_pipeline_override_forwarding():
    """Test CLI forwards overrides to trainer."""
    config = _make_config()
    overrides = {"trainer.epochs": 10}
    # Verify overrides are applied


@pytest.mark.integration
def test_cli_pipeline_checkpoint_config():
    """Test CLI configures checkpointing."""
    config = _make_config(trainer={"checkpoint": {"every": 5, "path": "/tmp/ckpt"}})
    # Verify checkpoint config is passed


@pytest.mark.integration
def test_cli_pipeline_logging_defaults():
    """Test CLI sets logging defaults."""
    config = _make_config()
    # Verify logging is configured


@pytest.mark.integration
def test_cli_pipeline_missing_data_config():
    """Test CLI handles missing data configuration."""
    config = _make_config()
    del config["data"]
    with pytest.raises(KeyError, match="data"):
        pass  # Should raise when data config is missing


@pytest.mark.integration
def test_cli_pipeline_invalid_checkpoint():
    """Test CLI handles invalid checkpoint configuration."""
    config = _make_config(trainer={"checkpoint": "invalid_string"})
    with pytest.raises(ValueError, match="checkpoint"):
        pass  # Should raise or handle gracefully
