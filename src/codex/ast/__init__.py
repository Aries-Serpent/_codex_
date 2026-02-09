"""Codex AST Analysis Framework.

Provides unified AST analysis across multiple languages (Python, YAML, JSON).

Components:
- node: StandardizedASTNode dataclass hierarchy (BLOCK-ARCH-001)
- graph: DependencyGraph with cycle detection (BLOCK-ARCH-002)
- metrics: CodeMetrics and MetricsAggregator (BLOCK-ARCH-003)
- parser: UniversalParser using libcst/ast (FR-AST-001)
- smells: CodeSmellDetector rules engine (FR-AST-007)
- export: KnowledgeGraphExporter multi-format (FR-AST-011)
- cli: CLI tools (analyze, audit, diff) (FR-AST-013)
- language_registry: Multi-language support via tree-sitter
- baseline: SQLite-backed baseline storage for incremental analysis
- delta: Change detection (added/removed/modified)
"""

__version__ = "1.1.0"

# New components for incremental analysis
from .baseline import BaselineManager
from .delta import DeltaAnalyzer, DeltaResult
from .export import (
    ExportFormat,
    ExportResult,
    KnowledgeGraphExporter,
    export_knowledge_graph,
)
from .graph import DependencyGraph
from .language_registry import LanguageRegistry
from .metrics import CodeMetrics, MetricsAggregator
from .node import NodeType, SourceLocation, StandardizedASTNode
from .parser import ParseError, UniversalParser, parse_python
from .smells import (
    CodeSmell,
    CodeSmellDetector,
    SmellCategory,
    SmellSeverity,
    detect_smells,
)

__all__ = [
    # Node representation (BLOCK-ARCH-001)
    "StandardizedASTNode",
    "NodeType",
    "SourceLocation",
    # Dependency graph (BLOCK-ARCH-002)
    "DependencyGraph",
    # Metrics (BLOCK-ARCH-003)
    "CodeMetrics",
    "MetricsAggregator",
    # Parser (FR-AST-001)
    "UniversalParser",
    "ParseError",
    "parse_python",
    # Code smells (FR-AST-007)
    "CodeSmellDetector",
    "CodeSmell",
    "SmellSeverity",
    "SmellCategory",
    "detect_smells",
    # Export (FR-AST-011)
    "KnowledgeGraphExporter",
    "ExportFormat",
    "ExportResult",
    "export_knowledge_graph",
    # Language registry (multi-language support)
    "LanguageRegistry",
    # Baseline management (incremental analysis)
    "BaselineManager",
    # Delta analysis (change detection)
    "DeltaAnalyzer",
    "DeltaResult",
]
