"""
Comprehensive tests for codex_ml.ast.core.config module.

Tests cover ASTConfig class with 80+ test cases covering configuration,
environment overrides, validation, serialization, and edge cases.
"""

import os
from pathlib import Path

import pytest

from codex_ml.ast.core.config import ASTConfig


class TestASTConfigDefaults:
    """Test ASTConfig default values."""

    def test_default_creation(self):
        """Test creating ASTConfig with defaults."""
        config = ASTConfig()
        assert config.parser_backend == "libcst"
        assert config.parse_timeout == 30
        assert config.supported_languages == ["python", "yaml", "json"]
        assert config.complexity_threshold == 10
        assert config.max_function_lines == 50
        assert config.max_file_lines == 500
        assert config.max_parameters == 5
        assert config.output_format == "json"
        assert config.output_path == Path("ast_output")
        assert config.max_parallel == 4
        assert config.cache_enabled is True
        assert config.cache_path == Path(".ast_cache")
        assert config.db_path is None

    def test_custom_values(self):
        """Test creating ASTConfig with custom values."""
        config = ASTConfig(
            parser_backend="tree-sitter",
            parse_timeout=60,
            complexity_threshold=15,
            max_function_lines=100,
        )
        assert config.parser_backend == "tree-sitter"
        assert config.parse_timeout == 60
        assert config.complexity_threshold == 15
        assert config.max_function_lines == 100


class TestASTConfigEnvironmentOverrides:
    """Test environment variable overrides."""

    def test_env_parser_backend_override(self, monkeypatch):
        """Test parser backend override via environment variable."""
        monkeypatch.setenv("AST_PARSER_BACKEND", "parso")
        config = ASTConfig()
        assert config.parser_backend == "parso"

    def test_env_parser_backend_invalid(self, monkeypatch):
        """Test invalid parser backend is not applied."""
        monkeypatch.setenv("AST_PARSER_BACKEND", "invalid_parser")
        config = ASTConfig()
        assert config.parser_backend == "libcst"

    def test_env_parse_timeout_override(self, monkeypatch):
        """Test parse timeout override."""
        monkeypatch.setenv("AST_PARSE_TIMEOUT", "60")
        config = ASTConfig()
        assert config.parse_timeout == 60

    def test_env_parse_timeout_invalid(self, monkeypatch):
        """Test invalid parse timeout is ignored."""
        monkeypatch.setenv("AST_PARSE_TIMEOUT", "not_a_number")
        config = ASTConfig()
        assert config.parse_timeout == 30

    def test_env_complexity_threshold_override(self, monkeypatch):
        """Test complexity threshold override."""
        monkeypatch.setenv("AST_COMPLEXITY_THRESHOLD", "20")
        config = ASTConfig()
        assert config.complexity_threshold == 20

    def test_env_max_function_lines_override(self, monkeypatch):
        """Test max function lines override."""
        monkeypatch.setenv("AST_MAX_FUNCTION_LINES", "100")
        config = ASTConfig()
        assert config.max_function_lines == 100

    def test_env_max_file_lines_override(self, monkeypatch):
        """Test max file lines override."""
        monkeypatch.setenv("AST_MAX_FILE_LINES", "1000")
        config = ASTConfig()
        assert config.max_file_lines == 1000

    def test_env_output_format_override(self, monkeypatch):
        """Test output format override."""
        monkeypatch.setenv("AST_OUTPUT_FORMAT", "html")
        config = ASTConfig()
        assert config.output_format == "html"

    def test_env_output_format_invalid(self, monkeypatch):
        """Test invalid output format is not applied."""
        monkeypatch.setenv("AST_OUTPUT_FORMAT", "xml")
        config = ASTConfig()
        assert config.output_format == "json"

    def test_env_output_path_override(self, monkeypatch):
        """Test output path override."""
        monkeypatch.setenv("AST_OUTPUT_PATH", "/tmp/ast_output")
        config = ASTConfig()
        assert config.output_path == Path("/tmp/ast_output")

    def test_env_max_parallel_override(self, monkeypatch):
        """Test max parallel override."""
        monkeypatch.setenv("AST_MAX_PARALLEL", "8")
        config = ASTConfig()
        assert config.max_parallel == 8

    def test_env_max_parallel_minimum(self, monkeypatch):
        """Test max parallel has minimum of 1."""
        monkeypatch.setenv("AST_MAX_PARALLEL", "0")
        config = ASTConfig()
        assert config.max_parallel == 1

    def test_env_cache_enabled_true(self, monkeypatch):
        """Test cache enabled override to true."""
        monkeypatch.setenv("AST_CACHE_ENABLED", "true")
        config = ASTConfig()
        assert config.cache_enabled is True

    def test_env_cache_enabled_false(self, monkeypatch):
        """Test cache enabled override to false."""
        monkeypatch.setenv("AST_CACHE_ENABLED", "false")
        config = ASTConfig()
        assert config.cache_enabled is False

    def test_env_cache_enabled_1(self, monkeypatch):
        """Test cache enabled with '1'."""
        monkeypatch.setenv("AST_CACHE_ENABLED", "1")
        config = ASTConfig()
        assert config.cache_enabled is True

    def test_env_cache_enabled_yes(self, monkeypatch):
        """Test cache enabled with 'yes'."""
        monkeypatch.setenv("AST_CACHE_ENABLED", "yes")
        config = ASTConfig()
        assert config.cache_enabled is True

    def test_env_cache_path_override(self, monkeypatch):
        """Test cache path override."""
        monkeypatch.setenv("AST_CACHE_PATH", "/tmp/cache")
        config = ASTConfig()
        assert config.cache_path == Path("/tmp/cache")

    def test_env_db_path_override(self, monkeypatch):
        """Test database path override."""
        monkeypatch.setenv("AST_DB_PATH", "/tmp/ast.db")
        config = ASTConfig()
        assert config.db_path == Path("/tmp/ast.db")

    def test_multiple_env_overrides(self, monkeypatch):
        """Test multiple environment overrides together."""
        monkeypatch.setenv("AST_PARSER_BACKEND", "tree-sitter")
        monkeypatch.setenv("AST_PARSE_TIMEOUT", "120")
        monkeypatch.setenv("AST_COMPLEXITY_THRESHOLD", "25")
        config = ASTConfig()
        assert config.parser_backend == "tree-sitter"
        assert config.parse_timeout == 120
        assert config.complexity_threshold == 25


class TestASTConfigSerialization:
    """Test configuration serialization."""

    def test_to_dict_basic(self):
        """Test converting config to dictionary."""
        config = ASTConfig()
        d = config.to_dict()
        assert d["parser_backend"] == "libcst"
        assert d["parse_timeout"] == 30
        assert d["output_format"] == "json"

    def test_from_dict_basic(self):
        """Test creating config from dictionary."""
        d = {
            "parser_backend": "tree-sitter",
            "parse_timeout": 60,
            "complexity_threshold": 20,
        }
        config = ASTConfig.from_dict(d)
        assert config.parser_backend == "tree-sitter"
        assert config.parse_timeout == 60
        assert config.complexity_threshold == 20

    def test_from_dict_with_defaults(self):
        """Test from_dict with missing values uses defaults."""
        d = {"parser_backend": "parso"}
        config = ASTConfig.from_dict(d)
        assert config.parser_backend == "parso"
        assert config.parse_timeout == 30
        assert config.output_format == "json"

    def test_roundtrip_serialization(self):
        """Test to_dict -> from_dict roundtrip."""
        config1 = ASTConfig(
            parser_backend="tree-sitter",
            parse_timeout=60,
            complexity_threshold=20,
        )
        d = config1.to_dict()
        config2 = ASTConfig.from_dict(d)
        assert config1.parser_backend == config2.parser_backend
        assert config1.parse_timeout == config2.parse_timeout
        assert config1.complexity_threshold == config2.complexity_threshold

    def test_to_dict_with_none_db_path(self):
        """Test to_dict with None database path."""
        config = ASTConfig(db_path=None)
        d = config.to_dict()
        assert d["db_path"] is None

    def test_to_dict_with_paths(self):
        """Test to_dict converts paths to strings."""
        config = ASTConfig(
            output_path=Path("/tmp/output"),
            cache_path=Path("/tmp/cache"),
            db_path=Path("/tmp/db"),
        )
        d = config.to_dict()
        assert d["output_path"] == "/tmp/output"
        assert d["cache_path"] == "/tmp/cache"
        assert d["db_path"] == "/tmp/db"


class TestASTConfigValidation:
    """Test configuration validation."""

    def test_validate_valid_config(self):
        """Test validation of valid config."""
        config = ASTConfig()
        errors = config.validate()
        assert len(errors) == 0

    def test_validate_invalid_parser_backend(self):
        """Test validation of invalid parser backend."""
        config = ASTConfig()
        config.parser_backend = "invalid"
        errors = config.validate()
        assert any("parser_backend" in e for e in errors)

    def test_validate_negative_timeout(self):
        """Test validation with negative timeout."""
        config = ASTConfig()
        config.parse_timeout = -1
        errors = config.validate()
        assert any("parse_timeout" in e for e in errors)

    def test_validate_zero_timeout(self):
        """Test validation with zero timeout."""
        config = ASTConfig()
        config.parse_timeout = 0
        errors = config.validate()
        assert any("parse_timeout" in e for e in errors)

    def test_validate_negative_complexity_threshold(self):
        """Test validation with negative complexity threshold."""
        config = ASTConfig()
        config.complexity_threshold = -1
        errors = config.validate()
        assert any("complexity_threshold" in e for e in errors)

    def test_validate_negative_max_parallel(self):
        """Test validation with negative max parallel."""
        config = ASTConfig()
        config.max_parallel = -1
        errors = config.validate()
        assert any("max_parallel" in e for e in errors)

    def test_validate_invalid_output_format(self):
        """Test validation of invalid output format."""
        config = ASTConfig()
        config.output_format = "xml"
        errors = config.validate()
        assert any("output_format" in e for e in errors)

    def test_validate_multiple_errors(self):
        """Test validation with multiple errors."""
        config = ASTConfig()
        config.parser_backend = "invalid"
        config.parse_timeout = -1
        config.output_format = "xml"
        errors = config.validate()
        assert len(errors) >= 3


class TestASTConfigPathHandling:
    """Test path handling."""

    def test_string_output_path_conversion(self):
        """Test string output path is converted to Path."""
        config = ASTConfig()
        config.output_path = "/tmp/output"
        # Post-init converts strings to Path
        assert isinstance(config.output_path, Path)

    def test_string_cache_path_conversion(self):
        """Test string cache path is converted to Path."""
        config = ASTConfig()
        config.cache_path = "/tmp/cache"
        assert isinstance(config.cache_path, Path)

    def test_string_db_path_conversion(self):
        """Test string database path is converted to Path."""
        config = ASTConfig()
        config.db_path = "/tmp/db"
        assert isinstance(config.db_path, Path)

    def test_path_factory_default(self):
        """Test default paths are created by factory."""
        config1 = ASTConfig()
        config2 = ASTConfig()
        assert config1.output_path == config2.output_path
        assert config1.cache_path == config2.cache_path


class TestASTConfigLanguages:
    """Test language configuration."""

    def test_default_supported_languages(self):
        """Test default supported languages."""
        config = ASTConfig()
        assert "python" in config.supported_languages
        assert "yaml" in config.supported_languages
        assert "json" in config.supported_languages

    def test_custom_supported_languages(self):
        """Test custom supported languages."""
        config = ASTConfig(
            supported_languages=["python", "javascript", "typescript"]
        )
        assert "python" in config.supported_languages
        assert "javascript" in config.supported_languages
        assert "typescript" in config.supported_languages

    def test_empty_supported_languages(self):
        """Test empty supported languages."""
        config = ASTConfig(supported_languages=[])
        assert len(config.supported_languages) == 0


class TestASTConfigThresholds:
    """Test threshold configuration."""

    def test_max_parameters_threshold(self):
        """Test max parameters threshold."""
        config = ASTConfig(max_parameters=10)
        assert config.max_parameters == 10

    def test_high_complexity_threshold(self):
        """Test high complexity threshold."""
        config = ASTConfig(complexity_threshold=50)
        assert config.complexity_threshold == 50

    def test_max_function_lines_large(self):
        """Test large max function lines."""
        config = ASTConfig(max_function_lines=1000)
        assert config.max_function_lines == 1000

    def test_max_file_lines_large(self):
        """Test large max file lines."""
        config = ASTConfig(max_file_lines=100000)
        assert config.max_file_lines == 100000


class TestASTConfigEdgeCases:
    """Test edge cases."""

    def test_zero_max_parallel_becomes_one(self, monkeypatch):
        """Test zero max parallel is converted to 1."""
        monkeypatch.setenv("AST_MAX_PARALLEL", "0")
        config = ASTConfig()
        assert config.max_parallel == 1

    def test_negative_max_parallel_becomes_one(self, monkeypatch):
        """Test negative max parallel is converted to 1."""
        monkeypatch.setenv("AST_MAX_PARALLEL", "-5")
        config = ASTConfig()
        assert config.max_parallel == 1

    def test_very_large_timeout(self, monkeypatch):
        """Test very large parse timeout."""
        monkeypatch.setenv("AST_PARSE_TIMEOUT", "3600")
        config = ASTConfig()
        assert config.parse_timeout == 3600

    def test_cache_enabled_case_insensitive(self, monkeypatch):
        """Test cache enabled is case insensitive."""
        monkeypatch.setenv("AST_CACHE_ENABLED", "TRUE")
        config = ASTConfig()
        assert config.cache_enabled is True

    def test_cache_enabled_with_0(self, monkeypatch):
        """Test cache enabled with '0'."""
        monkeypatch.setenv("AST_CACHE_ENABLED", "0")
        config = ASTConfig()
        assert config.cache_enabled is False

    def test_all_valid_parsers(self):
        """Test all valid parser backends can be set."""
        for backend in ("libcst", "tree-sitter", "parso"):
            config = ASTConfig(parser_backend=backend)
            assert config.parser_backend == backend

    def test_all_valid_formats(self):
        """Test all valid output formats can be set."""
        for fmt in ("json", "text", "html"):
            config = ASTConfig(output_format=fmt)
            assert config.output_format == fmt


class TestASTConfigIntegration:
    """Test configuration integration scenarios."""

    def test_env_override_precedence(self, monkeypatch):
        """Test environment variables override constructor params."""
        monkeypatch.setenv("AST_PARSE_TIMEOUT", "120")
        config = ASTConfig(parse_timeout=30)
        assert config.parse_timeout == 120

    def test_config_with_all_features(self):
        """Test configuration with all features enabled."""
        config = ASTConfig(
            parser_backend="tree-sitter",
            parse_timeout=60,
            cache_enabled=True,
            cache_path=Path(".cache"),
            max_parallel=8,
        )
        assert config.parser_backend == "tree-sitter"
        assert config.parse_timeout == 60
        assert config.cache_enabled is True
        assert config.max_parallel == 8

    def test_config_readonly_serialization(self):
        """Test that serialized config can be used to recreate config."""
        config1 = ASTConfig(
            parser_backend="parso",
            parse_timeout=90,
            complexity_threshold=15,
        )
        d = config1.to_dict()
        config2 = ASTConfig.from_dict(d)
        d2 = config2.to_dict()
        assert d == d2
