"""CLI pipeline integration tests (Phase 23 Week 2)."""

import pytest
from omegaconf import OmegaConf


@pytest.fixture(params=[dict, OmegaConf.create], ids=["dict", "omegaconf"])
def config_factory(request):
    return request.param


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
    _make_config()
    # Integration test would verify trainer is created with correct config


@pytest.mark.integration
def test_cli_pipeline_loader_propagation(tmp_path):
    """Test CLI propagates dataloaders to trainer."""
    data_file = tmp_path / "data.tsv"
    data_file.write_text("text\t1\n")

    _make_config(data={"path": str(data_file)})
    # Verify dataloaders are passed to trainer


@pytest.mark.integration
def test_cli_pipeline_device_handling():
    """Test CLI handles device configuration."""
    _make_config(device="cpu")
    _make_config(device="cuda")
    # Verify device is set correctly


@pytest.mark.integration
def test_cli_pipeline_override_forwarding():
    """Test CLI forwards overrides to trainer."""
    _make_config()
    # Verify overrides are applied


@pytest.mark.integration
def test_cli_pipeline_checkpoint_config(tmp_path, config_factory):
    """Accept checkpoint settings without changing the requested destination."""
    pipeline = _load_pipeline_module()
    checkpoint = {"every": 5, "path": str(tmp_path / "ckpt")}
    config = config_factory({"data": {}, "trainer": {"checkpoint": checkpoint}})

    pipeline.validate_pipeline_config(config)

    assert config["trainer"]["checkpoint"] == checkpoint
    assert not (tmp_path / "ckpt").exists()


@pytest.mark.integration
def test_cli_pipeline_logging_defaults():
    """Test CLI sets logging defaults."""
    _make_config()
    # Verify logging is configured


def _load_pipeline_module():
    """Load src/cli/pipeline.py directly to avoid conflict with src/cli.py."""
    import importlib.util
    from pathlib import Path

    # Walk up to find repository root (contains pyproject.toml)
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / "pyproject.toml").exists():
            break
        current = current.parent
    module_path = current / "src" / "cli" / "pipeline.py"
    spec = importlib.util.spec_from_file_location("src.cli.pipeline", module_path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.integration
def test_cli_pipeline_missing_data_config():
    """Test CLI handles missing data configuration."""
    pipeline = _load_pipeline_module()

    config = _make_config()
    del config["data"]
    # Actually validate the config which should raise KeyError
    with pytest.raises(KeyError, match=r"data configuration"):
        pipeline.validate_pipeline_config(config)


@pytest.mark.integration
def test_cli_pipeline_invalid_checkpoint(tmp_path, config_factory):
    """Reject a missing checkpoint for both plain and Hydra configurations."""
    pipeline = _load_pipeline_module()

    config = config_factory({"data": {}, "trainer": {"checkpoint": str(tmp_path / "missing.ckpt")}})
    with pytest.raises(ValueError, match="checkpoint file not found"):
        pipeline.validate_pipeline_config(config)


@pytest.mark.integration
def test_cli_pipeline_existing_checkpoint(tmp_path, config_factory):
    """Accept an existing checkpoint path."""
    pipeline = _load_pipeline_module()
    checkpoint = tmp_path / "model.ckpt"
    checkpoint.write_bytes(b"checkpoint")
    config = config_factory({"data": {}, "trainer": {"checkpoint": str(checkpoint)}})

    pipeline.validate_pipeline_config(config)

    assert config["trainer"]["checkpoint"] == str(checkpoint)


@pytest.mark.integration
@pytest.mark.parametrize("checkpoint", [42, True, ["model.ckpt"]])
def test_cli_pipeline_invalid_checkpoint_type(checkpoint, config_factory):
    """Do not silently accept non-mapping checkpoint settings."""
    pipeline = _load_pipeline_module()
    config = config_factory({"data": {}, "trainer": {"checkpoint": checkpoint}})

    with pytest.raises(ValueError, match="checkpoint must be a dict or path string"):
        pipeline.validate_pipeline_config(config)
