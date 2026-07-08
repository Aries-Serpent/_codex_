"""
AST Plugin Architecture.

Provides base interface for extending AST analysis to new languages
and custom analysis tools.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from codex.ast.node import StandardizedASTNode


@dataclass
class PluginMetadata:
    """Metadata about a plugin."""

    name: str
    version: str
    author: str
    description: str
    languages: list[str]
    file_extensions: list[str]


class ASTPlugin(ABC):
    """
    Base class for AST analysis plugins.

    Implement this interface to add support for new languages
    or custom analysis capabilities.
    """

    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""

    @property
    @abstractmethod
    def language(self) -> str:
        """
        Return primary language name this plugin handles.

        Examples: 'python', 'javascript', 'rust'
        """

    @property
    @abstractmethod
    def file_extensions(self) -> list[str]:
        """
        Return list of file extensions this plugin handles.

        Examples: ['.py', '.pyw'], ['.js', '.jsx']
        """

    @abstractmethod
    def can_parse(self, file_path: str) -> bool:
        """
        Check if this plugin can parse the given file.

        Args:
            file_path: Path to file to check

        Returns:
            True if plugin can handle this file
        """

    @abstractmethod
    def parse(self, code: str, file_path: str) -> StandardizedASTNode:
        """
        Parse code and return standardized AST node.

        Args:
            code: Source code to parse
            file_path: Path to source file

        Returns:
            StandardizedASTNode representing the AST

        Raises:
            SyntaxError: If code cannot be parsed
        """

    def analyze(self, node: StandardizedASTNode) -> dict[str, Any]:
        """
        Perform custom analysis on AST node.

        Optional hook for plugins to provide additional analysis.

        Args:
            node: AST node to analyze

        Returns:
            Dictionary of analysis results
        """
        return {}

    def validate(self) -> bool:
        """
        Validate plugin is properly configured.

        Returns:
            True if plugin is ready to use
        """
        return True


class AnalysisPlugin(ABC):
    """
    Base class for custom analysis plugins.

    Use this for plugins that analyze existing AST nodes
    rather than parsing new languages.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return plugin name."""

    @abstractmethod
    def analyze(self, node: StandardizedASTNode) -> dict[str, Any]:
        """
        Analyze an AST node.

        Args:
            node: Node to analyze

        Returns:
            Analysis results
        """


__all__ = ["ASTPlugin", "AnalysisPlugin", "PluginMetadata"]
