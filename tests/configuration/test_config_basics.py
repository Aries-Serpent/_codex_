"""
Configuration loading and validation tests.

Tests basic configuration patterns without heavy dependencies.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import pytest


class TestConfigFileOperations:
    """Test configuration file loading and saving."""

    def test_load_yaml_config(self):
        """Test loading YAML configuration file."""
        yaml = pytest.importorskip("yaml")

        # Use context manager for safe tempfile cleanup
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir)
            config_file = test_dir / "config.yaml"

            config_data = {
                "app_name": "test-app",
                "version": "1.0",
                "settings": {
                    "debug": True,
                    "port": 8080,
                },
            }

            config_file.write_text(yaml.dump(config_data))
            loaded = yaml.safe_load(config_file.read_text())

            assert loaded["app_name"] == "test-app", "Condition must be true"
            assert loaded["settings"]["debug"] is True, "Condition must be true"
            # Cleanup is automatic via context manager

    def test_load_json_config(self):
        """Test loading JSON configuration file."""
        # Use context manager for safe tempfile cleanup
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir)
            config_file = test_dir / "config.json"

            config_data = {
                "app_name": "test-app",
                "version": "1.0",
                "settings": {
                    "debug": True,
                    "port": 8080,
                },
            }

            config_file.write_text(json.dumps(config_data, indent=2))
            loaded = json.loads(config_file.read_text())

            assert loaded["app_name"] == "test-app", "Condition must be true"
            assert loaded["settings"]["debug"] is True, "Condition must be true"
            # Cleanup is automatic via context manager

    def test_config_file_not_found_handling(self):
        """Test handling of missing configuration file."""
        # Use context manager for safe tempfile cleanup
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir)
            missing_file = test_dir / "nonexistent.json"

            assert not missing_file.exists(), "Condition must be true"
            # Cleanup is automatic via context manager


class TestEnvironmentVariableConfig:
    """Test configuration via environment variables."""

    def test_read_env_variable(self, monkeypatch):
        """Test reading configuration from environment variable."""
        monkeypatch.setenv("TEST_CONFIG_VALUE", "test-value")

        value = os.getenv("TEST_CONFIG_VALUE")
        assert value == "test-value", "Value must be initialized"

    def test_env_variable_default(self):
        """Test environment variable with default value."""
        value = os.getenv("NONEXISTENT_VAR", "default-value")
        assert value == "default-value", "Value must be initialized"

    def test_env_variable_type_conversion(self, monkeypatch):
        """Test converting environment variable to appropriate type."""
        monkeypatch.setenv("TEST_PORT", "8080")
        monkeypatch.setenv("TEST_DEBUG", "true")

        port = int(os.getenv("TEST_PORT", "0"))
        debug = os.getenv("TEST_DEBUG", "false").lower() == "true"

        assert port == 8080, "port is not valid"
        assert debug is True, "debug is not valid"


class TestConfigValidation:
    """Test configuration validation."""

    def test_validate_required_fields(self):
        """Test validation of required configuration fields."""
        config = {
            "name": "test",
            "version": "1.0",
        }

        required_fields = ["name", "version"]
        for field in required_fields:
            assert field in config, "Condition must be true"

    def test_validate_field_types(self):
        """Test validation of configuration field types."""
        config = {
            "name": "test",
            "port": 8080,
            "enabled": True,
        }

        assert isinstance(config["name"], str)
        assert isinstance(config["port"], int)
        assert isinstance(config["enabled"], bool)

    def test_validate_value_ranges(self):
        """Test validation of configuration value ranges."""
        config = {
            "port": 8080,
            "workers": 4,
        }

        # Port should be in valid range
        assert 1 <= config["port"] <= 65535, "1 is not valid"

        # Workers should be positive
        assert config["workers"] > 0, "Value must be greater than zero"


class TestConfigMerging:
    """Test configuration merging and overrides."""

    def test_merge_configs(self):
        """Test merging two configuration dictionaries."""
        base_config = {
            "name": "app",
            "version": "1.0",
            "settings": {
                "debug": False,
                "port": 8080,
            },
        }

        override_config = {
            "settings": {
                "debug": True,
                "timeout": 30,
            },
        }

        # Merge configurations (shallow merge for simplicity)
        merged = base_config.copy()
        merged["settings"] = {**base_config["settings"], **override_config["settings"]}

        assert merged["settings"]["debug"] is True, "Condition must be true"
        assert merged["settings"]["port"] == 8080, "Condition must be true"
        assert merged["settings"]["timeout"] == 30, "Condition must be true"

    def test_override_precedence(self):
        """Test that overrides take precedence over defaults."""
        defaults = {"timeout": 30, "retries": 3}
        overrides = {"timeout": 60}

        config = {**defaults, **overrides}

        assert config["timeout"] == 60, "Condition must be true"
        assert config["retries"] == 3, "Condition must be true"

    def test_nested_config_merge(self):
        """Test merging nested configuration structures."""
        base = {
            "database": {
                "host": "localhost",
                "port": 5432,
            }
        }

        override = {
            "database": {
                "port": 5433,
                "user": "admin",
            }
        }

        # Deep merge helper
        def deep_merge(base_dict, override_dict):
            result = base_dict.copy()
            for key, value in override_dict.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result

        merged = deep_merge(base, override)

        assert merged["database"]["host"] == "localhost", "Data must not be empty"
        assert merged["database"]["port"] == 5433, "Data must not be empty"
        assert merged["database"]["user"] == "admin", "Data must not be empty"


class TestOfflineConfig:
    """Test offline mode configuration."""

    def test_offline_mode_flag(self, monkeypatch):
        """Test offline mode configuration via environment variable."""
        monkeypatch.setenv("OFFLINE_MODE", "true")

        offline = os.getenv("OFFLINE_MODE", "false").lower() == "true"
        assert offline is True, "offline is not valid"

    def test_offline_data_path(self, monkeypatch):
        """Test offline data path configuration."""
        test_path = os.path.join(tempfile.gettempdir(), "offline_data")
        monkeypatch.setenv("OFFLINE_DATA_PATH", test_path)

        data_path = os.getenv("OFFLINE_DATA_PATH", "/default/path")
        assert data_path == test_path, "Data must not be empty"

    def test_offline_catalog_config(self):
        """Test offline catalog configuration structure."""
        catalog_config = {
            "offline_mode": True,
            "catalog_path": "/data/catalog",
            "cache_dir": "/data/cache",
        }

        assert catalog_config["offline_mode"] is True, "Condition must be true"
        assert "catalog_path" in catalog_config, "Condition must be true"
        assert "cache_dir" in catalog_config, "Condition must be true"


class TestConfigSchema:
    """Test configuration schema validation."""

    def test_schema_validation_basic(self):
        """Test basic schema validation."""
        valid_config = {"name": "test", "age": 25}

        # Manual validation
        assert "name" in valid_config, "Condition must be true"
        assert isinstance(valid_config["name"], str)

    def test_schema_default_values(self):
        """Test applying default values from schema."""
        defaults = {
            "timeout": 30,
            "retries": 3,
            "debug": False,
        }

        config = {"timeout": 60}  # Only override timeout

        # Apply defaults
        final_config = {**defaults, **config}

        assert final_config["timeout"] == 60, "Condition must be true"
        assert final_config["retries"] == 3, "Condition must be true"
        assert final_config["debug"] is False, "Condition must be true"

    def test_schema_type_validation(self):
        """Test schema type validation."""
        config = {
            "name": "test",
            "count": 42,
            "enabled": True,
        }

        # Validate types
        assert isinstance(config["name"], str)
        assert isinstance(config["count"], int)
        assert isinstance(config["enabled"], bool)


class TestConfigPaths:
    """Test configuration file path resolution."""

    def test_config_path_resolution(self):
        """Test resolving configuration file paths."""
        from pathlib import Path

        # Typical config paths
        paths = [
            Path(".") / "config.yaml",
            Path.home() / ".config" / "app" / "config.yaml",
            Path("/etc") / "app" / "config.yaml",
        ]

        # All should be Path objects
        assert all(isinstance(p, Path) for p in paths)

    def test_config_directory_creation(self):
        """Test creating configuration directory if it doesn't exist."""
        test_dir = Path(tempfile.mkdtemp())
        config_dir = test_dir / "config"

        config_dir.mkdir(parents=True, exist_ok=True)

        assert config_dir.exists(), "Condition must be true"
        assert config_dir.is_dir(), "Condition must be true"

        # Cleanup
        import shutil

        shutil.rmtree(test_dir)

    def test_config_file_existence_check(self):
        """Test checking if configuration file exists."""
        test_dir = Path(tempfile.mkdtemp())

        existing_file = test_dir / "exists.yaml"
        existing_file.write_text("test: value")

        missing_file = test_dir / "missing.yaml"

        assert existing_file.exists(), "Condition must be true"
        assert not missing_file.exists(), "Condition must be true"

        # Cleanup
        import shutil

        shutil.rmtree(test_dir)
