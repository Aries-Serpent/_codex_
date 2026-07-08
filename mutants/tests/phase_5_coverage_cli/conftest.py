"""Reusable fixtures for Phase 5 CLI coverage tests."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any, Generator

import pytest


@pytest.fixture
def temp_config_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for Hydra configs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_feature_store() -> Generator[Path, None, None]:
    """Create a temporary directory for feature store."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_hydra_config(temp_config_dir: Path) -> dict[str, Any]:
    """Create a mock Hydra configuration."""
    config = {
        "model": {
            "target": "torch.nn.Linear",
            "params": {"in_features": 10, "out_features": 2},
        },
        "optimizer": {
            "target": "torch.optim.SGD",
            "params": {"lr": 0.01},
        },
        "data": {
            "name": "synthetic_classification",
            "params": {"num_samples": 100, "num_features": 10},
        },
        "trainer": {
            "epochs": 1,
            "batch_size": 32,
        },
        "device": "cpu",
    }

    config_file = temp_config_dir / "config.yaml"
    import yaml

    with open(config_file, "w") as f:
        yaml.dump(config, f)

    return config


@pytest.fixture
def mock_yaml_configs(temp_config_dir: Path) -> list[Path]:
    """Create temporary YAML files for testing."""
    try:
        import yaml
    except ImportError:
        pytest.skip("PyYAML not available")

    configs = []
    for i in range(3):
        config = {"defaults": ["_self_"], "param": f"value_{i}"}
        config_file = temp_config_dir / f"config_{i}.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config, f)
        configs.append(config_file)

    return configs


@pytest.fixture
def argparse_namespace():
    """Create an argparse Namespace object for testing."""
    import argparse

    return argparse.Namespace()


@pytest.fixture
def mock_cli_runner():
    """Create a mock CLI runner using Click testing."""
    try:
        from click.testing import CliRunner

        return CliRunner()
    except ImportError:
        pytest.skip("Click not available")


@pytest.fixture
def mock_typer_runner():
    """Create a mock Typer runner."""
    try:
        from typer.testing import CliRunner

        return CliRunner()
    except ImportError:
        pytest.skip("Typer not available")


@pytest.fixture
def json_report_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for JSON reports."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)
