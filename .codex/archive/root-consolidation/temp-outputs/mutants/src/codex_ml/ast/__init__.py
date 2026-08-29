"""
AST Standardization Module for Codex ML.

This module provides language-agnostic AST parsing, analysis, and storage
capabilities for codebase intelligence and quality metrics.

Components:
- core: Data structures (StandardizedASTNode, SourceLocation, Finding)
- graph: Dependency graph with cycle detection
- analysis: Pluggable analyzers (complexity, smells, dependencies)
- storage: SQLite-based persistence layer
- cli: Command-line interface for analysis

Example:
    from codex_ml.ast import StandardizedASTNode, AnalyzerRegistry

    # Parse and analyze code
    registry = AnalyzerRegistry()
    findings = registry.analyze_all(ast_tree)
"""

from codex_ml.ast.analysis import AnalyzerRegistry, ASTAnalyzer
from codex_ml.ast.core import (
    ASTConfig,
    Finding,
    SourceLocation,
    StandardizedASTNode,
)
from codex_ml.ast.core.exceptions import (
    AnalysisError,
    ASTError,
    ConfigurationError,
    ParseError,
    StorageError,
)
from codex_ml.ast.graph import DependencyGraph

__all__ = [
    # Core data structures
    "StandardizedASTNode",
    "SourceLocation",
    "Finding",
    "ASTConfig",
    # Exceptions
    "ASTError",
    "ParseError",
    "AnalysisError",
    "StorageError",
    "ConfigurationError",
    # Graph
    "DependencyGraph",
    # Analysis
    "ASTAnalyzer",
    "AnalyzerRegistry",
]

__version__ = "0.1.0"
