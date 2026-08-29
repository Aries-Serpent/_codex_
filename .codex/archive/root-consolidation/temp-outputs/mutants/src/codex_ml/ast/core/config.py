"""
Configuration management for AST analysis.

Provides configuration dataclass with environment variable overrides
and sensible defaults.
"""

import contextlib
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


@dataclass
class ASTConfig:
    """AST analysis configuration.

    Configuration can be overridden by environment variables:
    - AST_PARSER_BACKEND: Parser backend ('libcst', 'tree-sitter', 'parso')
    - AST_PARSE_TIMEOUT: Parse timeout in seconds
    - AST_COMPLEXITY_THRESHOLD: Complexity warning threshold
    - AST_MAX_FUNCTION_LINES: Max function lines threshold
    - AST_MAX_FILE_LINES: Max file lines threshold
    - AST_OUTPUT_FORMAT: Output format ('json', 'text', 'html')
    - AST_OUTPUT_PATH: Output directory path
    - AST_MAX_PARALLEL: Max parallel analysis workers
    - AST_CACHE_ENABLED: Enable caching ('true', 'false')
    - AST_CACHE_PATH: Cache directory path
    - AST_DB_PATH: SQLite database path
    """

    # Parser configuration
    parser_backend: str = "libcst"
    parse_timeout: int = 30
    supported_languages: list[str] = field(default_factory=lambda: ["python", "yaml", "json"])

    # Analysis thresholds
    complexity_threshold: int = 10
    max_function_lines: int = 50
    max_file_lines: int = 500
    max_parameters: int = 5

    # Output configuration
    output_format: str = "json"
    output_path: Path = field(default_factory=lambda: Path("ast_output"))

    # Performance configuration
    max_parallel: int = 4
    cache_enabled: bool = True
    cache_path: Path = field(default_factory=lambda: Path(".ast_cache"))

    # Storage configuration
    db_path: Optional[Path] = None

    def __post_init__(self) -> None:
        """Apply environment variable overrides."""
        # Parser backend
        if env_backend := os.getenv("AST_PARSER_BACKEND"):
            if env_backend in ("libcst", "tree-sitter", "parso"):
                self.parser_backend = env_backend

        # Parse timeout
        if env_timeout := os.getenv("AST_PARSE_TIMEOUT"):
            with contextlib.suppress(ValueError):
                self.parse_timeout = int(env_timeout)

        # Complexity threshold
        if env_threshold := os.getenv("AST_COMPLEXITY_THRESHOLD"):
            with contextlib.suppress(ValueError):
                self.complexity_threshold = int(env_threshold)

        # Max function lines
        if env_lines := os.getenv("AST_MAX_FUNCTION_LINES"):
            with contextlib.suppress(ValueError):
                self.max_function_lines = int(env_lines)

        # Max file lines
        if env_file_lines := os.getenv("AST_MAX_FILE_LINES"):
            with contextlib.suppress(ValueError):
                self.max_file_lines = int(env_file_lines)

        # Output format
        if env_format := os.getenv("AST_OUTPUT_FORMAT"):
            if env_format in ("json", "text", "html"):
                self.output_format = env_format

        # Output path
        if env_output := os.getenv("AST_OUTPUT_PATH"):
            self.output_path = Path(env_output)

        # Max parallel workers
        if env_parallel := os.getenv("AST_MAX_PARALLEL"):
            with contextlib.suppress(ValueError):
                self.max_parallel = max(1, int(env_parallel))

        # Cache enabled
        if env_cache := os.getenv("AST_CACHE_ENABLED"):
            self.cache_enabled = env_cache.lower() in ("true", "1", "yes")

        # Cache path
        if env_cache_path := os.getenv("AST_CACHE_PATH"):
            self.cache_path = Path(env_cache_path)

        # Database path
        if env_db := os.getenv("AST_DB_PATH"):
            self.db_path = Path(env_db)

        # Ensure paths are Path objects
        if isinstance(self.output_path, str):
            self.output_path = Path(self.output_path)
        if isinstance(self.cache_path, str):
            self.cache_path = Path(self.cache_path)
        if isinstance(self.db_path, str):
            self.db_path = Path(self.db_path)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "parser_backend": self.parser_backend,
            "parse_timeout": self.parse_timeout,
            "supported_languages": self.supported_languages,
            "complexity_threshold": self.complexity_threshold,
            "max_function_lines": self.max_function_lines,
            "max_file_lines": self.max_file_lines,
            "max_parameters": self.max_parameters,
            "output_format": self.output_format,
            "output_path": str(self.output_path),
            "max_parallel": self.max_parallel,
            "cache_enabled": self.cache_enabled,
            "cache_path": str(self.cache_path),
            "db_path": str(self.db_path) if self.db_path else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ASTConfig":
        """Create from dictionary."""
        return cls(
            parser_backend=data.get("parser_backend", "libcst"),
            parse_timeout=data.get("parse_timeout", 30),
            supported_languages=data.get("supported_languages", ["python", "yaml", "json"]),
            complexity_threshold=data.get("complexity_threshold", 10),
            max_function_lines=data.get("max_function_lines", 50),
            max_file_lines=data.get("max_file_lines", 500),
            max_parameters=data.get("max_parameters", 5),
            output_format=data.get("output_format", "json"),
            output_path=Path(data.get("output_path", "ast_output")),
            max_parallel=data.get("max_parallel", 4),
            cache_enabled=data.get("cache_enabled", True),
            cache_path=Path(data.get("cache_path", ".ast_cache")),
            db_path=Path(data["db_path"]) if data.get("db_path") else None,
        )

    def validate(self) -> list[str]:
        """Validate configuration and return list of errors."""
        errors = []

        if self.parser_backend not in ("libcst", "tree-sitter", "parso"):
            errors.append(f"Invalid parser_backend: {self.parser_backend}")

        if self.parse_timeout < 1:
            errors.append(f"parse_timeout must be positive: {self.parse_timeout}")

        if self.complexity_threshold < 1:
            errors.append(f"complexity_threshold must be positive: {self.complexity_threshold}")

        if self.max_parallel < 1:
            errors.append(f"max_parallel must be positive: {self.max_parallel}")

        if self.output_format not in ("json", "text", "html"):
            errors.append(f"Invalid output_format: {self.output_format}")

        return errors


# Default configuration instance
default_config = ASTConfig()
