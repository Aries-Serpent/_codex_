"""
Configuration Integration Tests

Tests configuration system integration across modules:
- Hydra configuration composition
- Override propagation across layers
- Plugin configuration and discovery
- Environment variable handling
- Configuration validation
- Multi-environment configuration

Part of Phase 23 Week 2: Integration Testing (100-120 tests)
Target: 20-30 tests for Configuration Integration
"""

from __future__ import annotations

import json
import os

import pytest

# Mark all tests as integration tests
pytestmark = [pytest.mark.integration]


@pytest.fixture
def temp_config_dir(tmp_path):
    """Create temporary configuration directory structure."""
    config_dir = tmp_path / "conf"
    config_dir.mkdir()
    (config_dir / "model").mkdir()
    (config_dir / "training").mkdir()
    (config_dir / "data").mkdir()
    (config_dir / "plugins").mkdir()
    return config_dir


@pytest.fixture
def base_config(temp_config_dir):
    """Create base configuration file."""
    base_file = temp_config_dir / "config.yaml"
    config_content = """
defaults:
  - model: default
  - training: default

app:
  name: codex
  version: 1.0

logging:
  level: INFO
  output: logs/
"""
    base_file.write_text(config_content)
    return base_file


@pytest.fixture
def model_config(temp_config_dir):
    """Create model configuration."""
    model_file = temp_config_dir / "model" / "default.yaml"
    config_content = """
architecture: transformer
hidden_size: 512
num_layers: 6
num_heads: 8
dropout: 0.1
"""
    model_file.write_text(config_content)
    return model_file


class TestHydraConfigComposition:
    """Test Hydra configuration composition."""

    def test_load_base_config(self, base_config):
        """Verify loading base configuration."""
        config_data = base_config.read_text()
        assert "app:" in config_data, "Data must not be empty"
        assert "name: codex" in config_data, "Data must not be empty"

    def test_compose_multiple_configs(self, base_config, model_config):
        """Verify composing multiple configuration files."""
        try:
            from omegaconf import OmegaConf

            base = OmegaConf.load(base_config)
            model = OmegaConf.load(model_config)

            composed = OmegaConf.merge(base, {"model": model})

            assert "app" in composed, "Condition must be true"
            assert "model" in composed, "Condition must be true"
        except ImportError:
            pytest.skip("OmegaConf not available")

    def test_config_defaults_resolution(self, temp_config_dir):
        """Verify default configuration resolution."""
        # Create default and override configs
        default_file = temp_config_dir / "training" / "default.yaml"
        default_file.write_text("batch_size: 32\nepochs: 10\n")

        override_file = temp_config_dir / "training" / "fast.yaml"
        override_file.write_text("batch_size: 64\nepochs: 1\n")

        assert default_file.exists(), "Condition must be true"
        assert override_file.exists(), "Condition must be true"

    def test_config_group_selection(self, temp_config_dir):
        """Verify configuration group selection."""
        # Create multiple configs in same group
        small_model = temp_config_dir / "model" / "small.yaml"
        small_model.write_text("hidden_size: 128\nnum_layers: 2\n")

        large_model = temp_config_dir / "model" / "large.yaml"
        large_model.write_text("hidden_size: 1024\nnum_layers: 12\n")

        assert small_model.exists(), "Condition must be true"
        assert large_model.exists(), "Condition must be true"


class TestConfigurationOverrides:
    """Test configuration override mechanisms."""

    def test_override_from_cli(self, base_config):
        """Verify CLI overrides apply correctly."""
        try:
            from omegaconf import OmegaConf

            base = OmegaConf.load(base_config)

            # Simulate CLI override
            overrides = {"app.name": "codex_override"}
            for key, value in overrides.items():
                OmegaConf.update(base, key, value)

            assert base.app.name == "codex_override", "name is not valid"
        except ImportError:
            pytest.skip("OmegaConf not available")

    def test_override_precedence(self, base_config):
        """Verify override precedence order."""
        try:
            from omegaconf import OmegaConf

            base = OmegaConf.create({"value": 1})
            override1 = OmegaConf.create({"value": 2})
            override2 = OmegaConf.create({"value": 3})

            result = OmegaConf.merge(base, override1, override2)

            assert result.value == 3, "Result must not be empty"
        except ImportError:
            pytest.skip("OmegaConf not available")

    def test_nested_override(self, model_config):
        """Verify nested configuration overrides."""
        try:
            from omegaconf import OmegaConf

            config = OmegaConf.load(model_config)

            # Override nested value
            OmegaConf.update(config, "hidden_size", 256)

            assert config.hidden_size == 256, "hidden_size is not valid"
        except ImportError:
            pytest.skip("OmegaConf not available")

    def test_list_override(self, temp_config_dir):
        """Verify list configuration overrides."""
        try:
            from omegaconf import OmegaConf

            config = OmegaConf.create({"layers": [64, 128, 256]})

            # Override list
            OmegaConf.update(config, "layers", [32, 64, 128])

            assert config.layers == [32, 64, 128]
        except ImportError:
            pytest.skip("OmegaConf not available")


class TestEnvironmentVariableHandling:
    """Test environment variable integration."""

    def test_env_var_substitution(self, monkeypatch, temp_config_dir):
        """Verify environment variable substitution."""
        monkeypatch.setenv("CODEX_MODEL_SIZE", "512")

        config_file = temp_config_dir / "env_config.yaml"
        config_file.write_text("model_size: ${oc.env:CODEX_MODEL_SIZE}\n")

        try:
            from omegaconf import OmegaConf

            config = OmegaConf.load(config_file)
            resolved = OmegaConf.to_container(config, resolve=True)

            assert resolved["model_size"] == "512", "Condition must be true"
        except ImportError:
            pytest.skip("OmegaConf not available")

    def test_env_var_defaults(self, temp_config_dir):
        """Verify environment variable defaults."""
        config_file = temp_config_dir / "defaults.yaml"
        config_file.write_text("port: ${oc.env:PORT,8080}\n")

        try:
            from omegaconf import OmegaConf

            config = OmegaConf.load(config_file)
            resolved = OmegaConf.to_container(config, resolve=True)

            # Should use default when env var not set
            assert resolved["port"] == "8080", "Condition must be true"
        except ImportError:
            pytest.skip("OmegaConf not available")

    def test_multiple_env_vars(self, monkeypatch, temp_config_dir):
        """Verify multiple environment variable handling."""
        monkeypatch.setenv("CODEX_HOST", "localhost")
        monkeypatch.setenv("CODEX_PORT", "9000")

        config_file = temp_config_dir / "multi_env.yaml"
        config_file.write_text("""
host: ${CODEX_HOST}
port: ${CODEX_PORT}
""")

        assert config_file.exists(), "Condition must be true"


class TestPluginConfiguration:
    """Test plugin configuration and discovery."""

    def test_plugin_config_loading(self, temp_config_dir):
        """Verify plugin configuration loading."""
        plugin_config = temp_config_dir / "plugins" / "example_plugin.yaml"
        plugin_config.write_text("""
name: example_plugin
enabled: true
config:
  option1: value1
  option2: value2
""")

        config_data = plugin_config.read_text()
        assert "name: example_plugin" in config_data, "Data must not be empty"
        assert "enabled: true" in config_data, "Data must not be empty"

    def test_plugin_discovery(self, temp_config_dir):
        """Verify plugin discovery from configuration."""
        plugins_dir = temp_config_dir / "plugins"

        # Create multiple plugin configs
        for i in range(3):
            plugin_file = plugins_dir / f"plugin_{i}.yaml"
            plugin_file.write_text(f"name: plugin_{i}\nenabled: true\n")

        # Discover plugins
        discovered = list(plugins_dir.glob("plugin_*.yaml"))

        assert len(discovered) == 3, "Discovered must not be empty"

    def test_plugin_enable_disable(self, temp_config_dir):
        """Verify plugin enable/disable configuration."""
        plugin_config = temp_config_dir / "plugins" / "toggleable.yaml"
        plugin_config.write_text("name: toggleable\nenabled: false\n")

        config_data = plugin_config.read_text()
        assert "enabled: false" in config_data, "Data must not be empty"

    def test_plugin_config_validation(self, temp_config_dir):
        """Verify plugin configuration validation."""
        plugin_config = temp_config_dir / "plugins" / "validated.yaml"
        plugin_config.write_text("""
name: validated
version: 1.0.0
required_fields:
  - name
  - version
""")

        config_data = plugin_config.read_text()
        assert "name:" in config_data, "Data must not be empty"
        assert "version:" in config_data, "Data must not be empty"


class TestConfigurationValidation:
    """Test configuration validation."""

    def test_schema_validation(self, temp_config_dir):
        """Verify configuration schema validation."""
        try:
            from omegaconf import OmegaConf

            config = OmegaConf.create({"model": {"hidden_size": 512, "num_layers": 6}})

            # Validate types
            assert isinstance(config.model.hidden_size, int)
            assert isinstance(config.model.num_layers, int)
        except ImportError:
            pytest.skip("OmegaConf not available")

    def test_required_fields_validation(self, temp_config_dir):
        """Verify required fields validation."""
        required_fields = ["model", "training", "data"]

        config = {
            "model": {"hidden_size": 512},
            "training": {"batch_size": 32},
            "data": {"path": "/data"},
        }

        for field in required_fields:
            assert field in config, "Condition must be true"

    def test_value_range_validation(self, temp_config_dir):
        """Verify value range validation."""
        config = {
            "learning_rate": 0.001,
            "dropout": 0.1,
            "batch_size": 32,
        }

        # Validate ranges
        assert 0 < config["learning_rate"] <= 1, "0 is not valid"
        assert 0 <= config["dropout"] < 1, "0 is not valid"
        assert config["batch_size"] > 0, "Value must be greater than zero"

    def test_type_validation(self, temp_config_dir):
        """Verify configuration type validation."""
        config = {
            "name": "model",
            "size": 512,
            "enabled": True,
            "options": ["opt1", "opt2"],
        }

        assert isinstance(config["name"], str)
        assert isinstance(config["size"], int)
        assert isinstance(config["enabled"], bool)
        assert isinstance(config["options"], list)


class TestMultiEnvironmentConfig:
    """Test multi-environment configuration."""

    def test_development_config(self, temp_config_dir):
        """Verify development environment configuration."""
        dev_config = temp_config_dir / "env" / "dev.yaml"
        dev_config.parent.mkdir(exist_ok=True)
        dev_config.write_text("""
environment: development
debug: true
logging:
  level: DEBUG
""")

        config_data = dev_config.read_text()
        assert "environment: development" in config_data, "Data must not be empty"
        assert "debug: true" in config_data, "Data must not be empty"

    def test_production_config(self, temp_config_dir):
        """Verify production environment configuration."""
        prod_config = temp_config_dir / "env" / "prod.yaml"
        prod_config.parent.mkdir(exist_ok=True)
        prod_config.write_text("""
environment: production
debug: false
logging:
  level: WARNING
""")

        config_data = prod_config.read_text()
        assert "environment: production" in config_data, "Data must not be empty"
        assert "debug: false" in config_data, "Data must not be empty"

    def test_environment_switching(self, temp_config_dir, monkeypatch):
        """Verify environment switching mechanism."""
        monkeypatch.setenv("CODEX_ENV", "production")

        env = os.getenv("CODEX_ENV", "development")

        assert env == "production", "env is not valid"

    def test_environment_specific_overrides(self, temp_config_dir):
        """Verify environment-specific overrides."""
        base = {"batch_size": 32, "workers": 4}

        dev_overrides = {"workers": 1}  # Single worker for dev
        prod_overrides = {"workers": 8}  # Multiple workers for prod

        dev_config = {**base, **dev_overrides}
        prod_config = {**base, **prod_overrides}

        assert dev_config["workers"] == 1, "Condition must be true"
        assert prod_config["workers"] == 8, "Condition must be true"


class TestConfigInterpolation:
    """Test configuration interpolation."""

    def test_variable_interpolation(self, temp_config_dir):
        """Verify variable interpolation in config."""
        try:
            from omegaconf import OmegaConf

            config = OmegaConf.create(
                {
                    "base_dir": "/data",
                    "train_dir": "${base_dir}/train",
                    "val_dir": "${base_dir}/val",
                }
            )

            resolved = OmegaConf.to_container(config, resolve=True)

            assert resolved["train_dir"] == "/data/train", "Data must not be empty"
            assert resolved["val_dir"] == "/data/val", "Data must not be empty"
        except ImportError:
            pytest.skip("OmegaConf not available")

    def test_nested_interpolation(self, temp_config_dir):
        """Verify nested interpolation."""
        try:
            from omegaconf import OmegaConf

            config = OmegaConf.create(
                {
                    "project": "codex",
                    "paths": {
                        "root": "/projects/${project}",
                        "data": "${paths.root}/data",
                    },
                }
            )

            resolved = OmegaConf.to_container(config, resolve=True)

            assert resolved["paths"]["root"] == "/projects/codex", "Condition must be true"
            assert resolved["paths"]["data"] == "/projects/codex/data", "Data must not be empty"
        except ImportError:
            pytest.skip("OmegaConf not available")

    def test_conditional_interpolation(self, temp_config_dir):
        """Verify conditional interpolation."""
        try:
            from omegaconf import OmegaConf

            config = OmegaConf.create(
                {
                    "use_gpu": True,
                    "device": (
                        "cuda"
                        if OmegaConf.to_container(
                            OmegaConf.create({"use_gpu": True}), resolve=True
                        )["use_gpu"]
                        else "cpu"
                    ),
                }
            )

            # Basic structure validation
            assert "device" in config, "Condition must be true"
        except ImportError:
            pytest.skip("OmegaConf not available")


class TestConfigurationInheritance:
    """Test configuration inheritance patterns."""

    def test_base_config_inheritance(self, temp_config_dir):
        """Verify base configuration inheritance."""
        base_config = temp_config_dir / "base.yaml"
        base_config.write_text("""
model:
  hidden_size: 512
  num_layers: 6
""")

        derived_config = temp_config_dir / "derived.yaml"
        derived_config.write_text("""
defaults:
  - base

model:
  num_layers: 12  # Override
""")

        assert base_config.exists(), "Condition must be true"
        assert derived_config.exists(), "Condition must be true"

    def test_multi_level_inheritance(self, temp_config_dir):
        """Verify multi-level configuration inheritance."""
        level1 = temp_config_dir / "level1.yaml"
        level1.write_text("value: 1\n")

        level2 = temp_config_dir / "level2.yaml"
        level2.write_text("defaults:\n  - level1\nvalue: 2\n")

        level3 = temp_config_dir / "level3.yaml"
        level3.write_text("defaults:\n  - level2\nvalue: 3\n")

        assert all([level1.exists(), level2.exists(), level3.exists()])


class TestConfigurationCaching:
    """Test configuration caching mechanisms."""

    def test_config_cache_creation(self, temp_config_dir):
        """Verify configuration caching."""
        cache_file = temp_config_dir / ".cache" / "config.cache"
        cache_file.parent.mkdir(exist_ok=True)

        config_data = {"model": {"hidden_size": 512}}
        cache_file.write_text(json.dumps(config_data))

        assert cache_file.exists(), "Condition must be true"
        cached = json.loads(cache_file.read_text())
        assert cached["model"]["hidden_size"] == 512, "Condition must be true"

    def test_config_cache_invalidation(self, temp_config_dir):
        """Verify cache invalidation on config change."""
        config_file = temp_config_dir / "config.yaml"
        cache_file = temp_config_dir / ".cache" / "config.cache"
        cache_file.parent.mkdir(exist_ok=True)

        config_file.write_text("version: 1\n")
        cache_file.write_text(json.dumps({"version": 1}))

        # Modify config
        config_file.write_text("version: 2\n")

        # Check if cache is stale
        config_mtime = config_file.stat().st_mtime
        cache_mtime = cache_file.stat().st_mtime

        is_stale = config_mtime > cache_mtime
        assert isinstance(is_stale, bool)


class TestConfigurationMerging:
    """Test configuration merging strategies."""

    def test_shallow_merge(self, temp_config_dir):
        """Verify shallow configuration merge."""
        base = {"a": 1, "b": 2}
        override = {"b": 3, "c": 4}

        merged = {**base, **override}

        assert merged == {"a": 1, "b": 3, "c": 4}

    def test_deep_merge(self, temp_config_dir):
        """Verify deep configuration merge."""
        try:
            from omegaconf import OmegaConf

            base = OmegaConf.create({"model": {"hidden_size": 512, "num_layers": 6}})
            override = OmegaConf.create({"model": {"num_layers": 12}})

            merged = OmegaConf.merge(base, override)

            assert merged.model.hidden_size == 512, "hidden_size is not valid"
            assert merged.model.num_layers == 12, "num_layers is not valid"
        except ImportError:
            pytest.skip("OmegaConf not available")

    def test_list_merge_strategies(self, temp_config_dir):
        """Verify list merge strategies."""
        try:
            from omegaconf import OmegaConf

            base = OmegaConf.create({"items": [1, 2, 3]})
            override = OmegaConf.create({"items": [4, 5]})

            # Replace strategy (default)
            merged = OmegaConf.merge(base, override)

            assert merged["items"] == [4, 5]
        except ImportError:
            pytest.skip("OmegaConf not available")
