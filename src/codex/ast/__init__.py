"""Codex AST Analysis Framework.

Provides unified AST analysis across multiple languages (Python, YAML, JSON).
"""

__version__ = "1.0.0"

from .node import StandardizedASTNode, NodeType, SourceLocation
from .graph import DependencyGraph
from .metrics import CodeMetrics, MetricsAggregator

__all__ = [
    "StandardizedASTNode",
    "NodeType",
    "SourceLocation",
    "DependencyGraph",
    "CodeMetrics",
    "MetricsAggregator",
]
