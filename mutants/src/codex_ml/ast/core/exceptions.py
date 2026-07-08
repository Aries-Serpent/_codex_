"""
Exception hierarchy for AST operations.

Provides a structured exception hierarchy for consistent error handling
across the AST analysis framework.
"""

from typing import Any


class ASTError(Exception):
    """Base exception for all AST operations."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ParseError(ASTError):
    """Error during source code parsing.

    Attributes:
        file_path: Path to the file that failed to parse
        line: Line number where the error occurred
        column: Column number where the error occurred
    """

    def __init__(
        self,
        message: str,
        file_path: str = None,  # type: ignore[assignment]
        line: int = None,  # type: ignore[assignment]
        column: int | None = None,
    ):
        super().__init__(message)
        self.file_path = file_path
        self.line = line
        self.column = column

    def __str__(self) -> str:
        location = ""
        if self.file_path:
            location = f"{self.file_path}"
            if self.line is not None:
                location += f":{self.line}"
                if self.column is not None:
                    location += f":{self.column}"
            location += ": "
        return f"{location}{self.message}"


class AnalysisError(ASTError):
    """Error during AST analysis.

    Raised when an analyzer encounters an unexpected condition
    or cannot complete its analysis.
    """

    def __init__(self, message: str, analyzer_type: str | None = None):
        super().__init__(message)
        self.analyzer_type = analyzer_type


class StorageError(ASTError):
    """Error during storage operations.

    Raised when reading/writing analysis results to storage fails.
    """

    def __init__(self, message: str, operation: str | None = None):
        super().__init__(message)
        self.operation = operation


class ConfigurationError(ASTError):
    """Error in configuration.

    Raised when configuration values are invalid or missing.
    """

    def __init__(self, message: str, key: str | None = None):
        super().__init__(message)
        self.key = key


class CycleDetectedError(ASTError):
    """Circular dependency detected in graph.

    Raised when topological sort is attempted on a graph with cycles.
    """

    def __init__(
        self, message: str = "Circular dependency detected", cycle: list[Any] | None = None
    ):
        super().__init__(message)
        self.cycle = cycle or []
