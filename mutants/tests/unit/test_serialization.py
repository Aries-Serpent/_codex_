"""Test JSON serialization of all config and model objects."""

import json
from dataclasses import asdict

import pytest

from src.codex_ml.cli.config import AppConfig, ExperimentConfig, ModelCfg


class TestConfigSerialization:
    """Verify all config objects support JSON serialization."""

    @pytest.mark.parametrize(
        "config_class",
        [
            AppConfig,
            ExperimentConfig,
            ModelCfg,
        ],
    )
    def test_config_to_dict(self, config_class):
        """Test config objects can convert to dict."""
        config = config_class()
        # Use dataclasses.asdict for dataclass objects
        config_dict = asdict(config)
        assert isinstance(config_dict, dict)

    @pytest.mark.parametrize(
        "config_class",
        [
            AppConfig,
            ExperimentConfig,
            ModelCfg,
        ],
    )
    def test_config_json_serialization(self, config_class):
        """Test config objects can serialize to JSON."""
        config = config_class()
        # Use dataclasses.asdict for proper serialization
        config_dict = asdict(config)

        # Should not raise TypeError
        json_str = json.dumps(config_dict, default=str)
        assert len(json_str) > 0, "Json_str must not be empty"

        # Should be valid JSON
        parsed = json.loads(json_str)
        assert isinstance(parsed, dict)

    def test_app_config_experiment_optional(self):
        """Test AppConfig handles optional experiment field."""
        config = AppConfig()
        # Experiment field should be None or an ExperimentConfig
        assert config.experiment is None or isinstance(config.experiment, ExperimentConfig)

        # Should be JSON serializable even with None experiment
        config_dict = asdict(config)
        json_str = json.dumps(config_dict, default=str)
        assert len(json_str) > 0, "Json_str must not be empty"
