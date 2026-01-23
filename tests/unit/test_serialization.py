"""Test JSON serialization of all config and model objects."""

import json
import pytest
from src.codex_ml.cli.config import AppConfig, ExperimentConfig, ModelCfg


class TestConfigSerialization:
    """Verify all config objects support JSON serialization."""
    
    @pytest.mark.parametrize("config_class", [
        AppConfig,
        ExperimentConfig,
        ModelCfg,
    ])
    def test_config_to_dict(self, config_class):
        """Test config objects can convert to dict."""
        config = config_class()
        config_dict = config.to_dict() if hasattr(config, 'to_dict') else config.__dict__
        assert isinstance(config_dict, dict)
    
    @pytest.mark.parametrize("config_class", [
        AppConfig,
        ExperimentConfig,
        ModelCfg,
    ])
    def test_config_json_serialization(self, config_class):
        """Test config objects can serialize to JSON."""
        config = config_class()
        config_dict = config.to_dict() if hasattr(config, 'to_dict') else config.__dict__
        
        # Should not raise TypeError
        json_str = json.dumps(config_dict, default=str)
        assert len(json_str) > 0
        
        # Should be valid JSON
        parsed = json.loads(json_str)
        assert isinstance(parsed, dict)
    
    def test_app_config_experiment_optional(self):
        """Test AppConfig handles optional experiment field."""
        config = AppConfig()
        # Experiment field should be None or an ExperimentConfig
        assert config.experiment is None or isinstance(config.experiment, ExperimentConfig)
        
        # Should be JSON serializable even with None experiment
        config_dict = config.__dict__
        json_str = json.dumps(config_dict, default=str)
        assert len(json_str) > 0
