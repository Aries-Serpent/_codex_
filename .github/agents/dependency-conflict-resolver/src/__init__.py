#!/usr/bin/env python3
"""
__init__.py for dependency-conflict-resolver agent
"""

from src.agent import (
    ConflictIssue,
    ConflictSeverity,
    ConflictType,
    DependencyConflictResolver,
    DependencyNode,
    PipResolverAnalyzer,
    ResolutionResult,
    SchemaCompatibility,
    SchemaValidator,
    VersionMatrix,
    VersionMatrixGenerator,
)

__version__ = "1.0.0"
__all__ = [
    "DependencyConflictResolver",
    "PipResolverAnalyzer",
    "VersionMatrixGenerator",
    "SchemaValidator",
    "ConflictSeverity",
    "ConflictType",
    "ConflictIssue",
    "VersionMatrix",
    "SchemaCompatibility",
    "ResolutionResult",
    "DependencyNode",
]
