"""
Comprehensive tests for ASTConfig module.

Covers default values, constructor overrides, environment variable overrides,
serialization/deserialization, validation, and edge cases.
"""

import tempfile
from pathlib import Path

import pytest

from src.codex_ml.ast.core.config import ASTConfig


class TestDefaultValues:
    """Test default configuration values."""

    def test_default_parser_backend(self):
        """Test default parser_backend is 'libcst'."""
        config = ASTConfig()
        assert config.parser_backend == "libcst", "parser_backend is not valid"

    def test_default_parse_timeout(self):
        """Test default parse_timeout is 30."""
        config = ASTConfig()
        assert config.parse_timeout == 30, "parse_timeout is not valid"

    def test_default_supported_languages(self):
        """Test default supported_languages includes python, yaml, json."""
        config = ASTConfig()
        assert config.supported_languages == ["python", "yaml", "json"]

    def test_default_complexity_threshold(self):
        """Test default complexity_threshold is 10."""
        config = ASTConfig()
        assert config.complexity_threshold == 10, "complexity_threshold is not valid"

    def test_default_max_function_lines(self):
        """Test default max_function_lines is 50."""
        config = ASTConfig()
        assert config.max_function_lines == 50, "max_function_lines is not valid"

    def test_default_max_file_lines(self):
        """Test default max_file_lines is 500."""
        config = ASTConfig()
        assert config.max_file_lines == 500, "max_file_lines is not valid"

    def test_default_output_format(self):
        """Test default output_format is 'json'."""
        config = ASTConfig()
        assert config.output_format == "json", "output_format is not valid"

    def test_default_output_path(self):
        """Test default output_path is 'ast_output'."""
        config = ASTConfig()
        assert config.output_path == Path("ast_output"), "output_path is not valid"

    def test_default_cache_enabled(self):
        """Test default cache_enabled is True."""
        config = ASTConfig()
        assert config.cache_enabled is True, "cache_enabled is not valid"

    def test_default_db_path_is_none(self):
        """Test default db_path is None."""
        config = ASTConfig()
        assert config.db_path is None, "db_path is not valid"


class TestConstructorOverrides:
    """Test constructor parameter overrides."""

    def test_override_parser_backend(self):
        """Test overriding parser_backend via constructor."""
        config = ASTConfig(parser_backend="tree-sitter")
        assert config.parser_backend == "tree-sitter", "parser_backend is not valid"

    def test_override_parse_timeout(self):
        """Test overriding parse_timeout via constructor."""
        config = ASTConfig(parse_timeout=60)
        assert config.parse_timeout == 60, "parse_timeout is not valid"

    def test_override_complexity_threshold(self):
        """Test overriding complexity_threshold via constructor."""
        config = ASTConfig(complexity_threshold=20)
        assert config.complexity_threshold == 20, "complexity_threshold is not valid"

    def test_override_max_function_lines(self):
        """Test overriding max_function_lines via constructor."""
        config = ASTConfig(max_function_lines=100)
        assert config.max_function_lines == 100, "max_function_lines is not valid"

    def test_override_max_file_lines(self):
        """Test overriding max_file_lines via constructor."""
        config = ASTConfig(max_file_lines=1000)
        assert config.max_file_lines == 1000, "max_file_lines is not valid"

    def test_override_output_format(self):
        """Test overriding output_format via constructor."""
        config = ASTConfig(output_format="html")
        assert config.output_format == "html", "output_format is not valid"

    def test_override_output_path(self):
        """Test overriding output_path via constructor."""
        config = ASTConfig(output_path=Path("/custom/path"))
        assert config.output_path == Path("/custom/path"), "output_path is not valid"

    def test_override_max_parallel(self):
        """Test overriding max_parallel via constructor."""
        config = ASTConfig(max_parallel=8)
        assert config.max_parallel == 8, "max_parallel is not valid"

    def test_override_cache_enabled(self):
        """Test overriding cache_enabled via constructor."""
        config = ASTConfig(cache_enabled=False)
        assert config.cache_enabled is False, "cache_enabled is not valid"

    def test_override_db_path(self):
        """Test overriding db_path via constructor."""
        config = ASTConfig(db_path=Path("/custom/db.sqlite"))
        assert config.db_path == Path("/custom/db.sqlite"), "db_path is not valid"


class TestEnvironmentVariableOverrides:
    """Test environment variable overrides in __post_init__."""

    def test_env_parser_backend_libcst(self, monkeypatch):
        """Test AST_PARSER_BACKEND override with libcst."""
        monkeypatch.setenv("AST_PARSER_BACKEND", "libcst")
        config = ASTConfig()
        assert config.parser_backend == "libcst", "parser_backend is not valid"

    def test_env_parser_backend_tree_sitter(self, monkeypatch):
        """Test AST_PARSER_BACKEND override with tree-sitter."""
        monkeypatch.setenv("AST_PARSER_BACKEND", "tree-sitter")
        config = ASTConfig()
        assert config.parser_backend == "tree-sitter", "parser_backend is not valid"

    def test_env_parser_backend_parso(self, monkeypatch):
        """Test AST_PARSER_BACKEND override with parso."""
        monkeypatch.setenv("AST_PARSER_BACKEND", "parso")
        config = ASTConfig()
        assert config.parser_backend == "parso", "parser_backend is not valid"

    def test_env_parser_backend_invalid(self, monkeypatch):
        """Test AST_PARSER_BACKEND with invalid value keeps default."""
        monkeypatch.setenv("AST_PARSER_BACKEND", "invalid")
        config = ASTConfig()
        assert config.parser_backend == "libcst", "parser_backend is not valid"

    def test_env_parse_timeout(self, monkeypatch):
        """Test AST_PARSE_TIMEOUT override."""
        monkeypatch.setenv("AST_PARSE_TIMEOUT", "60")
        config = ASTConfig()
        assert config.parse_timeout == 60, "parse_timeout is not valid"

    def test_env_parse_timeout_invalid(self, monkeypatch):
        """Test AST_PARSE_TIMEOUT with invalid value keeps default."""
        monkeypatch.setenv("AST_PARSE_TIMEOUT", "not_a_number")
        config = ASTConfig()
        assert config.parse_timeout == 30, "parse_timeout is not valid"

    def test_env_complexity_threshold(self, monkeypatch):
        """Test AST_COMPLEXITY_THRESHOLD override."""
        monkeypatch.setenv("AST_COMPLEXITY_THRESHOLD", "25")
        config = ASTConfig()
        assert config.complexity_threshold == 25, "complexity_threshold is not valid"

    def test_env_complexity_threshold_invalid(self, monkeypatch):
        """Test AST_COMPLEXITY_THRESHOLD with invalid value keeps default."""
        monkeypatch.setenv("AST_COMPLEXITY_THRESHOLD", "abc")
        config = ASTConfig()
        assert config.complexity_threshold == 10, "complexity_threshold is not valid"

    def test_env_max_function_lines(self, monkeypatch):
        """Test AST_MAX_FUNCTION_LINES override."""
        monkeypatch.setenv("AST_MAX_FUNCTION_LINES", "100")
        config = ASTConfig()
        assert config.max_function_lines == 100, "max_function_lines is not valid"

    def test_env_max_function_lines_invalid(self, monkeypatch):
        """Test AST_MAX_FUNCTION_LINES with invalid value keeps default."""
        monkeypatch.setenv("AST_MAX_FUNCTION_LINES", "xyz")
        config = ASTConfig()
        assert config.max_function_lines == 50, "max_function_lines is not valid"

    def test_env_max_file_lines(self, monkeypatch):
        """Test AST_MAX_FILE_LINES override."""
        monkeypatch.setenv("AST_MAX_FILE_LINES", "1000")
        config = ASTConfig()
        assert config.max_file_lines == 1000, "max_file_lines is not valid"

    def test_env_max_file_lines_invalid(self, monkeypatch):
        """Test AST_MAX_FILE_LINES with invalid value keeps default."""
        monkeypatch.setenv("AST_MAX_FILE_LINES", "bad")
        config = ASTConfig()
        assert config.max_file_lines == 500, "max_file_lines is not valid"

    def test_env_output_format_json(self, monkeypatch):
        """Test AST_OUTPUT_FORMAT override with json."""
        monkeypatch.setenv("AST_OUTPUT_FORMAT", "json")
        config = ASTConfig()
        assert config.output_format == "json", "output_format is not valid"

    def test_env_output_format_text(self, monkeypatch):
        """Test AST_OUTPUT_FORMAT override with text."""
        monkeypatch.setenv("AST_OUTPUT_FORMAT", "text")
        config = ASTConfig()
        assert config.output_format == "text", "output_format is not valid"

    def test_env_output_format_html(self, monkeypatch):
        """Test AST_OUTPUT_FORMAT override with html."""
        monkeypatch.setenv("AST_OUTPUT_FORMAT", "html")
        config = ASTConfig()
        assert config.output_format == "html", "output_format is not valid"

    def test_env_output_format_invalid(self, monkeypatch):
        """Test AST_OUTPUT_FORMAT with invalid value keeps default."""
        monkeypatch.setenv("AST_OUTPUT_FORMAT", "xml")
        config = ASTConfig()
        assert config.output_format == "json", "output_format is not valid"

    def test_env_output_path(self, monkeypatch):
        """Test AST_OUTPUT_PATH override."""
        monkeypatch.setenv("AST_OUTPUT_PATH", os.path.join(tempfile.gettempdir(), "ast_output"))
        config = ASTConfig()
        assert config.output_path == Path(os.path.join(tempfile.gettempdir(), "ast_output")), "output_path is not valid"

    def test_env_max_parallel(self, monkeypatch):
        """Test AST_MAX_PARALLEL override."""
        monkeypatch.setenv("AST_MAX_PARALLEL", "8")
        config = ASTConfig()
        assert config.max_parallel == 8, "max_parallel is not valid"

    def test_env_max_parallel_enforces_minimum(self, monkeypatch):
        """Test AST_MAX_PARALLEL minimum of 1 is enforced."""
        monkeypatch.setenv("AST_MAX_PARALLEL", "0")
        config = ASTConfig()
        assert config.max_parallel == 1, "max_parallel is not valid"

    def test_env_max_parallel_negative(self, monkeypatch):
        """Test AST_MAX_PARALLEL with negative value becomes 1."""
        monkeypatch.setenv("AST_MAX_PARALLEL", "-5")
        config = ASTConfig()
        assert config.max_parallel == 1, "max_parallel is not valid"

    def test_env_max_parallel_invalid(self, monkeypatch):
        """Test AST_MAX_PARALLEL with invalid value keeps default."""
        monkeypatch.setenv("AST_MAX_PARALLEL", "not_int")
        config = ASTConfig()
        assert config.max_parallel == 4, "max_parallel is not valid"

    def test_env_cache_enabled_true(self, monkeypatch):
        """Test AST_CACHE_ENABLED with 'true'."""
        monkeypatch.setenv("AST_CACHE_ENABLED", "true")
        config = ASTConfig()
        assert config.cache_enabled is True, "cache_enabled is not valid"

    def test_env_cache_enabled_one(self, monkeypatch):
        """Test AST_CACHE_ENABLED with '1'."""
        monkeypatch.setenv("AST_CACHE_ENABLED", "1")
        config = ASTConfig()
        assert config.cache_enabled is True, "cache_enabled is not valid"

    def test_env_cache_enabled_yes(self, monkeypatch):
        """Test AST_CACHE_ENABLED with 'yes'."""
        monkeypatch.setenv("AST_CACHE_ENABLED", "yes")
        config = ASTConfig()
        assert config.cache_enabled is True, "cache_enabled is not valid"

    def test_env_cache_enabled_false(self, monkeypatch):
        """Test AST_CACHE_ENABLED with 'false'."""
        monkeypatch.setenv("AST_CACHE_ENABLED", "false")
        config = ASTConfig()
        assert config.cache_enabled is False, "cache_enabled is not valid"

    def test_env_cache_path(self, monkeypatch):
        """Test AST_CACHE_PATH override."""
        monkeypatch.setenv("AST_CACHE_PATH", os.path.join(tempfile.gettempdir(), "custom_cache"))
        config = ASTConfig()
        assert config.cache_path == Path(os.path.join(tempfile.gettempdir(), "custom_cache")), "cache_path is not valid"

    def test_env_db_path(self, monkeypatch):
        """Test AST_DB_PATH override."""
        monkeypatch.setenv("AST_DB_PATH", os.path.join(tempfile.gettempdir(), "ast.db"))
        config = ASTConfig()
        assert config.db_path == Path(os.path.join(tempfile.gettempdir(), "ast.db")), "db_path is not valid"


class TestSerializationDeserialization:
    """Test to_dict() and from_dict() methods."""

    def test_to_dict_returns_dict(self):
        """Test to_dict() returns a dictionary."""
        config = ASTConfig()
        result = config.to_dict()
        assert isinstance(result, dict)

    def test_to_dict_contains_all_keys(self):
        """Test to_dict() contains all expected keys."""
        config = ASTConfig()
        result = config.to_dict()
        expected_keys = {
            "parser_backend",
            "parse_timeout",
            "supported_languages",
            "complexity_threshold",
            "max_function_lines",
            "max_file_lines",
            "max_parameters",
            "output_format",
            "output_path",
            "max_parallel",
            "cache_enabled",
            "cache_path",
            "db_path",
        }
        assert set(result.keys()) == expected_keys, "Result must not be empty"

    def test_to_dict_paths_as_strings(self):
        """Test to_dict() converts paths to strings."""
        config = ASTConfig(output_path=Path("/custom/path"))
        result = config.to_dict()
        assert isinstance(result["output_path"], str)
        assert isinstance(result["cache_path"], str)

    def test_to_dict_with_none_db_path(self):
        """Test to_dict() with None db_path."""
        config = ASTConfig(db_path=None)
        result = config.to_dict()
        assert result["db_path"] is None, "Result must not be empty"

    def test_to_dict_with_db_path(self):
        """Test to_dict() with non-None db_path."""
        config = ASTConfig(db_path=Path("/custom/db.sqlite"))
        result = config.to_dict()
        assert result["db_path"] == "/custom/db.sqlite", "Result must not be empty"

    def test_from_dict_creates_config(self):
        """Test from_dict() creates ASTConfig instance."""
        data = {"parser_backend": "parso", "parse_timeout": 45}
        config = ASTConfig.from_dict(data)
        assert isinstance(config, ASTConfig)

    def test_from_dict_applies_values(self):
        """Test from_dict() applies provided values."""
        data = {
            "parser_backend": "tree-sitter",
            "parse_timeout": 60,
            "complexity_threshold": 15,
        }
        config = ASTConfig.from_dict(data)
        assert config.parser_backend == "tree-sitter", "parser_backend is not valid"
        assert config.parse_timeout == 60, "parse_timeout is not valid"
        assert config.complexity_threshold == 15, "complexity_threshold is not valid"

    def test_from_dict_roundtrip(self):
        """Test to_dict() and from_dict() roundtrip."""
        original = ASTConfig(
            parser_backend="parso",
            parse_timeout=45,
            complexity_threshold=20,
            max_parallel=6,
        )
        data = original.to_dict()
        restored = ASTConfig.from_dict(data)
        assert restored.parser_backend == original.parser_backend, "parser_backend is not valid"
        assert restored.parse_timeout == original.parse_timeout, "parse_timeout is not valid"
        assert restored.complexity_threshold == original.complexity_threshold, "complexity_threshold is not valid"
        assert restored.max_parallel == original.max_parallel, "max_parallel is not valid"

    def test_from_dict_missing_keys_use_defaults(self):
        """Test from_dict() uses defaults for missing keys."""
        data = {}
        config = ASTConfig.from_dict(data)
        assert config.parser_backend == "libcst", "parser_backend is not valid"
        assert config.parse_timeout == 30, "parse_timeout is not valid"
        assert config.complexity_threshold == 10, "complexity_threshold is not valid"


class TestValidation:
    """Test validate() method."""

    def test_validate_returns_list(self):
        """Test validate() returns a list."""
        config = ASTConfig()
        result = config.validate()
        assert isinstance(result, list)

    def test_validate_no_errors_valid_config(self):
        """Test validate() returns empty list for valid config."""
        config = ASTConfig()
        errors = config.validate()
        assert errors == [], "Error should be raised or set"

    def test_validate_invalid_parser_backend(self):
        """Test validate() catches invalid parser_backend."""
        config = ASTConfig(parser_backend="invalid")
        errors = config.validate()
        assert any("parser_backend" in err for err in errors), "Error should be raised or set"

    def test_validate_negative_parse_timeout(self):
        """Test validate() catches negative parse_timeout."""
        config = ASTConfig(parse_timeout=-1)
        errors = config.validate()
        assert any("parse_timeout" in err for err in errors), "Error should be raised or set"

    def test_validate_zero_parse_timeout(self):
        """Test validate() catches zero parse_timeout."""
        config = ASTConfig(parse_timeout=0)
        errors = config.validate()
        assert any("parse_timeout" in err for err in errors), "Error should be raised or set"

    def test_validate_negative_complexity_threshold(self):
        """Test validate() catches negative complexity_threshold."""
        config = ASTConfig(complexity_threshold=-1)
        errors = config.validate()
        assert any("complexity_threshold" in err for err in errors), "Error should be raised or set"

    def test_validate_zero_complexity_threshold(self):
        """Test validate() catches zero complexity_threshold."""
        config = ASTConfig(complexity_threshold=0)
        errors = config.validate()
        assert any("complexity_threshold" in err for err in errors), "Error should be raised or set"

    def test_validate_negative_max_parallel(self):
        """Test validate() catches negative max_parallel."""
        config = ASTConfig(max_parallel=-1)
        errors = config.validate()
        assert any("max_parallel" in err for err in errors), "Error should be raised or set"

    def test_validate_zero_max_parallel(self):
        """Test validate() catches zero max_parallel."""
        config = ASTConfig(max_parallel=0)
        errors = config.validate()
        assert any("max_parallel" in err for err in errors), "Error should be raised or set"

    def test_validate_invalid_output_format(self):
        """Test validate() catches invalid output_format."""
        config = ASTConfig(output_format="pdf")
        errors = config.validate()
        assert any("output_format" in err for err in errors), "Error should be raised or set"

    def test_validate_multiple_errors(self):
        """Test validate() can return multiple errors."""
        config = ASTConfig(
            parser_backend="invalid",
            parse_timeout=-1,
            output_format="pdf",
        )
        errors = config.validate()
        assert len(errors) >= 3, "Errors must not be empty"

    def test_validate_error_messages_informative(self):
        """Test validate() error messages include details."""
        config = ASTConfig(parser_backend="badbackend")
        errors = config.validate()
        assert any("badbackend" in err for err in errors), "Error should be raised or set"

    def test_validate_all_backends_valid(self):
        """Test validate() accepts all valid backends."""
        for backend in ("libcst", "tree-sitter", "parso"):
            config = ASTConfig(parser_backend=backend)
            errors = config.validate()
            parser_errors = [e for e in errors if "parser_backend" in e]
            assert not parser_errors, "Error should be raised or set"

    def test_validate_all_formats_valid(self):
        """Test validate() accepts all valid formats."""
        for fmt in ("json", "text", "html"):
            config = ASTConfig(output_format=fmt)
            errors = config.validate()
            format_errors = [e for e in errors if "output_format" in e]
            assert not format_errors, "Error should be raised or set"

    def test_validate_positive_values(self):
        """Test validate() accepts positive threshold values."""
        config = ASTConfig(
            parse_timeout=1,
            complexity_threshold=1,
            max_parallel=1,
        )
        errors = config.validate()
        assert errors == [], "Error should be raised or set"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_multiple_env_vars_combined(self, monkeypatch):
        """Test multiple environment variables applied together."""
        monkeypatch.setenv("AST_PARSER_BACKEND", "parso")
        monkeypatch.setenv("AST_PARSE_TIMEOUT", "90")
        monkeypatch.setenv("AST_OUTPUT_FORMAT", "html")
        config = ASTConfig()
        assert config.parser_backend == "parso", "parser_backend is not valid"
        assert config.parse_timeout == 90, "parse_timeout is not valid"
        assert config.output_format == "html", "output_format is not valid"

    def test_env_var_overrides_constructor(self, monkeypatch):
        """Test environment variable overrides constructor parameter."""
        monkeypatch.setenv("AST_PARSER_BACKEND", "tree-sitter")
        config = ASTConfig(parser_backend="libcst")
        assert config.parser_backend == "tree-sitter", "parser_backend is not valid"

    def test_cache_enabled_case_insensitive_true(self, monkeypatch):
        """Test AST_CACHE_ENABLED is case insensitive for 'true'."""
        monkeypatch.setenv("AST_CACHE_ENABLED", "TRUE")
        config = ASTConfig()
        assert config.cache_enabled is True, "cache_enabled is not valid"

    def test_cache_enabled_case_insensitive_false(self, monkeypatch):
        """Test AST_CACHE_ENABLED is case insensitive for false."""
        monkeypatch.setenv("AST_CACHE_ENABLED", "FALSE")
        config = ASTConfig()
        assert config.cache_enabled is False, "cache_enabled is not valid"

    def test_path_conversion_from_string(self):
        """Test path fields properly convert from string to Path."""
        config = ASTConfig()
        assert isinstance(config.output_path, Path)
        assert isinstance(config.cache_path, Path)

    def test_large_timeout_value(self, monkeypatch):
        """Test large parse_timeout value."""
        monkeypatch.setenv("AST_PARSE_TIMEOUT", "999999")
        config = ASTConfig()
        assert config.parse_timeout == 999999, "parse_timeout is not valid"

    def test_large_parallel_value(self, monkeypatch):
        """Test large max_parallel value."""
        monkeypatch.setenv("AST_MAX_PARALLEL", "512")
        config = ASTConfig()
        assert config.max_parallel == 512, "max_parallel is not valid"

    def test_special_characters_in_path(self, monkeypatch):
        """Test special characters in path environment variable."""
        monkeypatch.setenv("AST_OUTPUT_PATH", "/path/with-special_chars/output")
        config = ASTConfig()
        assert config.output_path == Path("/path/with-special_chars/output"), "output_path is not valid"

    def test_supported_languages_not_modified(self):
        """Test supported_languages field is not affected by env vars."""
        config = ASTConfig()
        assert config.supported_languages == ["python", "yaml", "json"]

    def test_max_parameters_default(self):
        """Test max_parameters has correct default."""
        config = ASTConfig()
        assert config.max_parameters == 5, "max_parameters is not valid"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
