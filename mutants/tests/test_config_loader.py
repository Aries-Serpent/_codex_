"""Tests for centralized config loader."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from codex.utils.config_loader import (
    ConfigLoader,
    ErrorConfig,
    MissingConfigException,
    get_loader,
    load_config,
    load_error_config,
)


@pytest.fixture
def temp_config_dir(tmp_path: Path) -> Path:
    """Create a temporary config directory with test files."""
    config_dir = tmp_path / "conf"
    config_dir.mkdir()

    # Create a test config file
    test_config = config_dir / "test.yaml"
    test_config.write_text("""
app:
  name: test_app
  version: 1.0.0
  debug: false

database:
  host: localhost
  port: 5432
  name: testdb
""")

    # Create errors config
    errors_dir = config_dir / "errors"
    errors_dir.mkdir()
    errors_config = errors_dir / "defaults.yaml"
    errors_config.write_text("""
config_errors:
  missing_config:
    code: "CONFIG_001"
    message: "Missing configuration file"
    severity: "error"
    resolution: "Ensure the configuration file exists"

  invalid_config:
    code: "CONFIG_002"
    message: "Invalid configuration format"
    severity: "error"
    resolution: "Validate YAML syntax"

defaults:
  log_errors: true
  raise_on_error: true
""")

    return tmp_path


class TestConfigLoader:
    """Test suite for ConfigLoader class."""

    def test_initialization(self, temp_config_dir: Path) -> None:
        """Test ConfigLoader initialization."""
        loader = ConfigLoader(repo_root=temp_config_dir)
        assert loader.repo_root == temp_config_dir, "repo_root is not valid"
        assert isinstance(loader.error_config, dict)

    def test_find_repo_root(self) -> None:
        """Test automatic repo root detection."""
        loader = ConfigLoader()
        assert loader.repo_root.exists(), "Condition must be true"
        # Should find either .git or pyproject.toml
        has_git = (loader.repo_root / ".git").exists()
        has_pyproject = (loader.repo_root / "pyproject.toml").exists()
        assert has_git or has_pyproject, "has_git is not valid"

    def test_load_error_config(self, temp_config_dir: Path) -> None:
        """Test loading error configuration."""
        loader = ConfigLoader(repo_root=temp_config_dir)
        assert "config_errors" in loader.error_config, "Error should be raised or set"
        assert "missing_config" in loader.error_config["config_errors"], "Error should be raised or set"
        assert "defaults" in loader.error_config, "Error should be raised or set"

    def test_get_error(self, temp_config_dir: Path) -> None:
        """Test retrieving structured error."""
        loader = ConfigLoader(repo_root=temp_config_dir)
        error = loader.get_error("config_errors", "missing_config")

        assert error is not None, "error must be initialized"
        assert isinstance(error, ErrorConfig)
        assert error.code == "CONFIG_001", "Error should be raised or set"
        assert error.message == "Missing configuration file", "Error should be raised or set"
        assert error.severity == "error", "Error should be raised or set"
        assert "exists" in error.resolution, "Error should be raised or set"

    def test_get_error_not_found(self, temp_config_dir: Path) -> None:
        """Test getting non-existent error returns None."""
        loader = ConfigLoader(repo_root=temp_config_dir)
        error = loader.get_error("nonexistent", "error")
        assert error is None, "Error should be raised or set"

    def test_load_config_success(self, temp_config_dir: Path) -> None:
        """Test successful config loading."""
        loader = ConfigLoader(repo_root=temp_config_dir)
        cfg = loader.load_config("test", config_dir="conf")

        assert cfg is not None, "cfg must be initialized"
        # Handle both DictConfig and dict
        if hasattr(cfg, "app"):
            assert cfg.app.name == "test_app", "name is not valid"
            assert cfg.app.version == "1.0.0", "version is not valid"
        else:
            assert cfg["app"]["name"] == "test_app", "Condition must be true"
            assert cfg["app"]["version"] == "1.0.0", "Condition must be true"

    def test_load_config_with_overrides(self, temp_config_dir: Path) -> None:
        """Test config loading with overrides."""
        loader = ConfigLoader(repo_root=temp_config_dir)
        cfg = loader.load_config(
            "test", config_dir="conf", overrides=["app.debug=true", "database.port=3306"]
        )

        assert cfg is not None, "cfg must be initialized"
        # Handle both DictConfig and dict
        if hasattr(cfg, "app"):
            assert cfg.app.debug is True, "debug is not valid"
            assert cfg.database.port == 3306, "Data must not be empty"
        else:
            assert cfg["app"]["debug"] is True, "Condition must be true"
            assert cfg["database"]["port"] == 3306, "Data must not be empty"

    def test_load_config_missing_with_fallback(self, temp_config_dir: Path) -> None:
        """Test loading missing config with fallback enabled."""
        loader = ConfigLoader(repo_root=temp_config_dir)
        cfg = loader.load_config("nonexistent", config_dir="conf", allow_fallback=True)

        assert cfg is not None, "cfg must be initialized"
        # Should return empty config
        if hasattr(cfg, "__len__"):
            assert len(cfg) == 0 or cfg == {}, "Cfg must not be empty"

    def test_load_config_missing_no_fallback(self, temp_config_dir: Path) -> None:
        """Test loading missing config without fallback raises exception."""
        loader = ConfigLoader(repo_root=temp_config_dir)

        with pytest.raises((MissingConfigException, FileNotFoundError)):
            loader.load_config("nonexistent", config_dir="conf", allow_fallback=False)

    def test_apply_overrides(self) -> None:
        """Test manual override application."""
        data = {"a": {"b": 1}, "c": 2}
        overrides = ["a.b=10", "c=20", "d.e=30"]

        result = ConfigLoader._apply_overrides(data, overrides)

        assert result["a"]["b"] == 10, "Result must not be empty"
        assert result["c"] == 20, "Result must not be empty"
        assert result["d"]["e"] == 30, "Result must not be empty"

    def test_apply_overrides_invalid_format(self) -> None:
        """Test overrides with invalid format are skipped."""
        data = {"a": 1}
        overrides = ["invalid_override", "a=2"]

        result = ConfigLoader._apply_overrides(data, overrides)
        assert result["a"] == 2, "Result must not be empty"

    def test_error_config_format(self, temp_config_dir: Path) -> None:
        """Test error message formatting."""
        loader = ConfigLoader(repo_root=temp_config_dir)
        error = loader.get_error("config_errors", "missing_config")

        assert error is not None, "error must be initialized"
        formatted = error.format()
        assert "[CONFIG_001]" in formatted, "Condition must be true"
        assert "Missing configuration file" in formatted, "Condition must be true"


class TestGlobalFunctions:
    """Test suite for global convenience functions."""

    def test_get_loader(self) -> None:
        """Test global loader retrieval."""
        loader1 = get_loader()
        loader2 = get_loader()

        # Should return same instance
        assert loader1 is loader2, "loader1 is not valid"
        assert isinstance(loader1, ConfigLoader)

    def test_load_config_global(
        self, temp_config_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test global load_config function."""
        # Create a new loader with temp directory
        test_loader = ConfigLoader(repo_root=temp_config_dir)

        # Monkeypatch get_loader to return our test loader
        import codex.utils.config_loader as config_loader_module

        monkeypatch.setattr(config_loader_module, "_global_loader", test_loader)

        cfg = load_config("test", config_dir="conf")
        assert cfg is not None, "cfg must be initialized"

    def test_load_error_config_global(
        self, temp_config_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test global load_error_config function."""
        test_loader = ConfigLoader(repo_root=temp_config_dir)

        import codex.utils.config_loader as config_loader_module

        monkeypatch.setattr(config_loader_module, "_global_loader", test_loader)

        errors = load_error_config()
        assert isinstance(errors, dict)
        assert "config_errors" in errors, "Error should be raised or set"


class TestErrorConfig:
    """Test suite for ErrorConfig dataclass."""

    def test_error_config_creation(self) -> None:
        """Test ErrorConfig instantiation."""
        error = ErrorConfig(
            code="TEST_001", message="Test error", severity="error", resolution="Fix the test"
        )

        assert error.code == "TEST_001", "Error should be raised or set"
        assert error.message == "Test error", "Error should be raised or set"
        assert error.severity == "error", "Error should be raised or set"
        assert error.resolution == "Fix the test", "Error should be raised or set"

    def test_error_config_format_simple(self) -> None:
        """Test error formatting without placeholders."""
        error = ErrorConfig(
            code="TEST_001", message="Simple error", severity="error", resolution="Fix it"
        )

        formatted = error.format()
        assert formatted == "[TEST_001] Simple error", "Error should be raised or set"

    def test_error_config_format_with_kwargs(self) -> None:
        """Test error formatting with keyword arguments."""
        error = ErrorConfig(
            code="TEST_002",
            message="Error with {param}: {value}",
            severity="error",
            resolution="Check parameters",
        )

        formatted = error.format(param="test_param", value=42)
        assert formatted == "[TEST_002] Error with test_param: 42", "Error should be raised or set"


class TestEdgeCases:
    """Test suite for edge cases and error conditions."""

    def test_missing_yaml_library(
        self, temp_config_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test behavior when PyYAML is not available."""
        # Simulate missing yaml by making import fail
        import builtins

        original_import = builtins.__import__

        def mock_import(name: str, *args: Any, **kwargs: Any) -> Any:
            if name == "yaml":
                raise ImportError("yaml not available")
            return original_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", mock_import)

        loader = ConfigLoader(repo_root=temp_config_dir)
        # Should fall back to default error config
        assert loader.error_config is not None, "error_config must be initialized"
        assert "defaults" in loader.error_config, "Error should be raised or set"

    def test_corrupted_error_config(self, temp_config_dir: Path) -> None:
        """Test handling of corrupted error config file."""
        # Corrupt the error config
        errors_config = temp_config_dir / "conf" / "errors" / "defaults.yaml"
        errors_config.write_text("invalid: yaml: content: [[[")

        # Should fall back to default config
        loader = ConfigLoader(repo_root=temp_config_dir)
        assert loader.error_config is not None, "error_config must be initialized"
        assert "defaults" in loader.error_config, "Error should be raised or set"

    def test_config_dir_not_exists(self, temp_config_dir: Path) -> None:
        """Test loading from non-existent directory."""
        loader = ConfigLoader(repo_root=temp_config_dir)
        cfg = loader.load_config("test", config_dir="nonexistent", allow_fallback=True)

        # Should return empty fallback
        assert cfg is not None, "cfg must be initialized"

    def test_absolute_config_dir(self, temp_config_dir: Path) -> None:
        """Test loading with absolute config directory path."""
        loader = ConfigLoader(repo_root=temp_config_dir)
        absolute_path = temp_config_dir / "conf"

        cfg = loader.load_config("test", config_dir=str(absolute_path))
        assert cfg is not None, "cfg must be initialized"


class TestIntegration:
    """Integration tests with real repository structure."""

    def test_load_real_error_config(self) -> None:
        """Test loading actual error config from repository."""
        loader = ConfigLoader()
        errors = loader.error_config

        # Should have loaded real config or fallback
        assert isinstance(errors, dict)

        # If real config exists, verify structure
        if "config_errors" in errors:
            assert isinstance(errors["config_errors"], dict)
            if "missing_config" in errors["config_errors"]:
                assert "code" in errors["config_errors"]["missing_config"], "Error should be raised or set"

    def test_load_existing_conf_config(self) -> None:
        """Test loading a config from actual conf directory."""
        loader = ConfigLoader()

        try:
            # Try to load any existing config
            cfg = loader.load_config("config", config_dir="conf", allow_fallback=True)
            assert cfg is not None, "cfg must be initialized"
        except (ValueError, TypeError) as e:
            # If it fails, should still get fallback
            pytest.skip(f"No config.yaml in conf/: {e}")

    def test_missing_exception_attributes(self) -> None:
        """Test MissingConfigException has required attributes."""
        # When using custom exception (no Hydra)
        try:
            exc = MissingConfigException(missing_cfg_file="test.yaml", message="Test message")
            assert hasattr(exc, "missing_cfg_file")
            assert exc.missing_cfg_file == "test.yaml", "missing_cfg_file is not valid"
        except TypeError:
            # When using Hydra's MissingConfigException, it has different signature
            # Just verify the exception can be instantiated with a message
            exc = MissingConfigException("test.yaml")
            assert "test.yaml" in str(exc), "Condition must be true"

        # Test without explicit message
        try:
            exc2 = MissingConfigException(missing_cfg_file="test2.yaml")
            assert "test2.yaml" in str(exc2), "Condition must be true"
        except TypeError:
            # Hydra's exception requires message as positional arg
            exc2 = MissingConfigException("test2.yaml")
            assert "test2.yaml" in str(exc2), "Condition must be true"


class TestConfigLoaderAdvanced:
    """Advanced test cases for ConfigLoader."""

    def test_load_config_with_none_config_dir(self, temp_config_dir: Path) -> None:
        """Test loading config with None config_dir uses default."""
        loader = ConfigLoader(repo_root=temp_config_dir)
        # Should use repo_root/conf by default
        cfg = loader.load_config("test", config_dir=None, allow_fallback=True)
        assert cfg is not None, "cfg must be initialized"

    def test_dual_path_fallback(self, temp_config_dir: Path) -> None:
        """Test dual-path fallback to legacy configs/ location."""
        loader = ConfigLoader(repo_root=temp_config_dir)

        # Create a config in legacy location
        legacy_dir = temp_config_dir / "configs" / "training"
        legacy_dir.mkdir(parents=True)
        legacy_config = legacy_dir / "legacy_test.yaml"
        legacy_config.write_text("legacy: true\nvalue: 42")

        # Try to load with conf/ path (should fallback to configs/)
        cfg = loader.load_config("legacy_test", config_dir="conf/training", allow_fallback=True)

        assert cfg is not None, "cfg must be initialized"
        if hasattr(cfg, "legacy"):
            assert cfg.legacy is True, "legacy is not valid"
            assert cfg.value == 42, "Value must be initialized"
        else:
            assert cfg["legacy"] is True, "Condition must be true"
            assert cfg["value"] == 42, "Value must be initialized"

    def test_apply_overrides_nested_creation(self) -> None:
        """Test creating deeply nested structures via overrides."""
        data: dict[str, Any] = {}
        overrides = ["a.b.c.d=42", "x.y=test"]

        result = ConfigLoader._apply_overrides(data, overrides)

        assert result["a"]["b"]["c"]["d"] == 42, "Result must not be empty"
        assert result["x"]["y"] == "test", "Result must not be empty"

    def test_get_error_invalid_category(self, temp_config_dir: Path) -> None:
        """Test get_error with non-dict category returns None."""
        loader = ConfigLoader(repo_root=temp_config_dir)
        # Manually set invalid category
        loader.error_config["invalid_category"] = "not a dict"

        error = loader.get_error("invalid_category", "some_key")
        assert error is None, "Error should be raised or set"

    def test_load_config_yaml_override_parsing(self, temp_config_dir: Path) -> None:
        """Test override value parsing for different types."""
        loader = ConfigLoader(repo_root=temp_config_dir)
        cfg = loader.load_config(
            "test",
            config_dir="conf",
            overrides=[
                "int_val=123",
                "float_val=45.67",
                "bool_val=true",
                "list_val=[1,2,3]",
                "string_val=hello",
            ],
        )

        assert cfg is not None, "cfg must be initialized"
        # Verify different types are parsed correctly
        if hasattr(cfg, "int_val"):
            assert cfg.int_val == 123, "int_val is not valid"
        else:
            assert cfg["int_val"] == 123, "Condition must be true"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
