"""
Tests for AST configuration.
"""

from codex_ml.ast.core.config import ASTConfig


class TestASTConfig:
    """Tests for ASTConfig dataclass."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = ASTConfig()
        assert config.parser_backend == "libcst"
        assert config.parse_timeout == 30
        assert config.complexity_threshold == 10
        assert config.max_function_lines == 50
        assert config.max_parallel == 4
        assert config.cache_enabled is True

    def test_custom_config(self) -> None:
        """Test custom configuration."""
        config = ASTConfig(
            parser_backend="tree-sitter",
            complexity_threshold=15,
            max_parallel=8,
        )
        assert config.parser_backend == "tree-sitter"
        assert config.complexity_threshold == 15
        assert config.max_parallel == 8

    def test_env_override_parser_backend(self, monkeypatch) -> None:
        """Test environment variable override for parser backend."""
        monkeypatch.setenv("AST_PARSER_BACKEND", "parso")
        config = ASTConfig()
        assert config.parser_backend == "parso"

    def test_env_override_invalid_backend(self, monkeypatch) -> None:
        """Test invalid backend is not applied."""
        monkeypatch.setenv("AST_PARSER_BACKEND", "invalid")
        config = ASTConfig()
        assert config.parser_backend == "libcst"  # Default preserved

    def test_env_override_complexity(self, monkeypatch) -> None:
        """Test environment variable override for complexity threshold."""
        monkeypatch.setenv("AST_COMPLEXITY_THRESHOLD", "20")
        config = ASTConfig()
        assert config.complexity_threshold == 20

    def test_env_override_invalid_number(self, monkeypatch) -> None:
        """Test invalid number is not applied."""
        monkeypatch.setenv("AST_COMPLEXITY_THRESHOLD", "not_a_number")
        config = ASTConfig()
        assert config.complexity_threshold == 10  # Default preserved

    def test_env_override_cache_enabled(self, monkeypatch) -> None:
        """Test environment variable override for cache enabled."""
        monkeypatch.setenv("AST_CACHE_ENABLED", "false")
        config = ASTConfig()
        assert config.cache_enabled is False

    def test_env_override_output_format(self, monkeypatch) -> None:
        """Test environment variable override for output format."""
        monkeypatch.setenv("AST_OUTPUT_FORMAT", "html")
        config = ASTConfig()
        assert config.output_format == "html"

    def test_to_dict(self) -> None:
        """Test dictionary serialization."""
        config = ASTConfig(complexity_threshold=15)
        d = config.to_dict()
        assert d["parser_backend"] == "libcst"
        assert d["complexity_threshold"] == 15
        assert "output_path" in d

    def test_from_dict(self) -> None:
        """Test dictionary deserialization."""
        data = {
            "parser_backend": "tree-sitter",
            "complexity_threshold": 20,
            "max_parallel": 8,
        }
        config = ASTConfig.from_dict(data)
        assert config.parser_backend == "tree-sitter"
        assert config.complexity_threshold == 20
        assert config.max_parallel == 8

    def test_validate_valid(self) -> None:
        """Test validation passes for valid config."""
        config = ASTConfig()
        errors = config.validate()
        assert len(errors) == 0

    def test_validate_invalid_backend(self) -> None:
        """Test validation catches invalid backend."""
        config = ASTConfig()
        config.parser_backend = "invalid"
        errors = config.validate()
        assert len(errors) == 1
        assert "parser_backend" in errors[0]

    def test_validate_invalid_timeout(self) -> None:
        """Test validation catches invalid timeout."""
        config = ASTConfig()
        config.parse_timeout = -1
        errors = config.validate()
        assert len(errors) == 1
        assert "parse_timeout" in errors[0]

    def test_validate_invalid_parallel(self) -> None:
        """Test validation catches invalid parallel count."""
        config = ASTConfig()
        config.max_parallel = 0
        errors = config.validate()
        assert len(errors) == 1
        assert "max_parallel" in errors[0]

    def test_supported_languages(self) -> None:
        """Test supported languages list."""
        config = ASTConfig()
        assert "python" in config.supported_languages
        assert "yaml" in config.supported_languages
        assert "json" in config.supported_languages
