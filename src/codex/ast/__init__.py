"""Codex AST Analysis Framework.

Provides unified AST analysis across multiple languages (Python, YAML, JSON).
"""

__version__ = "1.0.0"

from .graph import DependencyGraph
from .metrics import CodeMetrics, MetricsAggregator
from .node import NodeType, SourceLocation, StandardizedASTNode

__all__ = [
    "StandardizedASTNode",
    "NodeType",
    "SourceLocation",
    "DependencyGraph",
    "CodeMetrics",
    "MetricsAggregator",
]
