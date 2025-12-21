# Codex AST Analysis Module

## Overview

The Codex AST Analysis module provides a unified framework for analyzing Abstract Syntax Trees (ASTs) across multiple languages. It offers language-agnostic representations, dependency analysis, code quality metrics, code smell detection, and multi-format export capabilities.

## Features

- **StandardizedASTNode**: Language-agnostic AST node representation
- **UniversalParser**: Parse Python code using libcst with ast fallback (FR-AST-001)
- **DependencyGraph**: Cycle detection using Tarjan's algorithm
- **MetricsAggregator**: Code quality metrics and correlation analysis
- **CodeSmellDetector**: Rules engine for detecting code quality issues (FR-AST-007)
- **KnowledgeGraphExporter**: Export to JSON, GraphML, DOT, SQLite, Markdown (FR-AST-011)
- **CLI Tools**: Command-line interface for AST analysis

## Installation

Core dependencies are included in the base installation:

```bash
pip install -e .
```

For optional features (tree-sitter, SQL parsing):

```bash
pip install -e ".[ast]"
```

## Quick Start

### Parsing Python Code

```python
from codex.ast import parse_python, UniversalParser

# Parse a file
tree = parse_python("path/to/file.py")

# Parse a string
tree = parse_python('''
def hello(name: str) -> str:
    """Say hello."""
    return f"Hello, {name}!"
''')

# Access parsed nodes
for node in tree.walk():
    print(f"{node.type.value}: {node.name}")
```

### Creating AST Nodes

```python
from pathlib import Path
from codex.ast import StandardizedASTNode, NodeType, SourceLocation

# Create a source location
loc = SourceLocation(
    file_path=Path("example.py"),
    line_start=1,
    column_start=0,
    line_end=10,
    column_end=0
)

# Create an AST node
node = StandardizedASTNode(
    node_id="func_1",
    type=NodeType.FUNCTION,
    name="my_function",
    source_location=loc,
    docstring="Example function"
)

# Traverse the tree
for n in node.walk():
    print(f"{n.name} at depth {n.get_depth()}")
```

### Dependency Analysis

```python
from codex.ast import DependencyGraph

# Create a dependency graph
graph = DependencyGraph()
graph.add_edge("module_a", "module_b")
graph.add_edge("module_b", "module_c")
graph.add_edge("module_c", "module_a")  # Creates a cycle

# Detect cycles
cycles = graph.detect_cycles()
print(f"Found {len(cycles)} cycle(s)")

# Topological sort (fails if cycles exist)
try:
    order = graph.topological_sort()
except ValueError as e:
    print(f"Cannot sort: {e}")
```

### Code Metrics

```python
from codex.ast import CodeMetrics, MetricsAggregator

# Create metrics
metrics = CodeMetrics(
    cyclomatic_complexity=5,
    cognitive_complexity=3.0,
    lines_of_code=100,
    comment_lines=10,
    maintainability_index=85.0
)

print(f"Quality tier: {metrics.quality_tier}")  # A-F grade

# Aggregate metrics
agg = MetricsAggregator()
agg.store_metrics("function_1", metrics)
summary = agg.summary()
```

### Code Smell Detection

```python
from codex.ast import CodeSmellDetector, detect_smells

# Quick detection
smells = detect_smells("path/to/file.py")
for smell in smells:
    print(f"{smell.rule_id}: {smell.message} (line {smell.line_start})")

# Full detector with configuration
detector = CodeSmellDetector()
detector.MAX_FUNCTION_LENGTH = 40  # Customize thresholds
detector.disable_rule("SMELL-M001")  # Disable specific rules

smells = detector.detect_file("path/to/file.py")

# Detect in entire directory
results = detector.detect_directory("src/", exclude_patterns=["**/test_*.py"])
```

#### Available Smell Rules

| Rule ID | Name | Category | Severity |
|---------|------|----------|----------|
| SMELL-C001 | Long Function | complexity | warning |
| SMELL-C002 | Too Many Arguments | complexity | warning |
| SMELL-C003 | Deep Nesting | complexity | warning |
| SMELL-N001 | Short Name | naming | info |
| SMELL-N002 | Non-PEP8 Name | naming | info |
| SMELL-S001 | God Class | structure | error |
| SMELL-S002 | Empty Except | structure | error |
| SMELL-M001 | Missing Docstring | maintainability | info |
| SMELL-M002 | Magic Number | maintainability | info |

### Knowledge Graph Export

```python
from codex.ast import (
    KnowledgeGraphExporter, 
    ExportFormat, 
    export_knowledge_graph,
    parse_python
)

# Parse code and create exporter
tree = parse_python("src/module.py")

# Quick export to JSON
result = export_knowledge_graph([tree], format=ExportFormat.JSON)
print(result.content)

# Full export with graph and metrics
from codex.ast import DependencyGraph, MetricsAggregator, CodeMetrics

graph = DependencyGraph()
graph.add_edge("func1", "func2")

metrics = MetricsAggregator()
metrics.store_metrics("func1", CodeMetrics(5, 3.0, 50, 5, 85.0))

exporter = KnowledgeGraphExporter()
exporter.add_node(tree)
exporter.set_graph(graph)
exporter.set_metrics(metrics)
exporter.set_metadata("project", "my_project")

# Export to different formats
exporter.export(ExportFormat.JSON, "output/graph.json")
exporter.export(ExportFormat.GRAPHML, "output/graph.graphml")
exporter.export(ExportFormat.DOT, "output/graph.dot")
exporter.export(ExportFormat.SQLITE, "output/graph.db")
exporter.export(ExportFormat.MARKDOWN, "output/report.md")
```

#### Export Formats

| Format | Extension | Use Case |
|--------|-----------|----------|
| JSON | .json | API integration, data exchange |
| GraphML | .graphml | Graph visualization tools (Gephi, yEd) |
| DOT | .dot | Graphviz rendering |
| SQLite | .db | Query-based analysis |
| Markdown | .md | Human-readable documentation |

## CLI Usage

```bash
# Analyze a file or directory
python -m codex.ast.cli analyze src/mycode/

# Run a full audit
python -m codex.ast.cli audit . --json

# Compare metrics between paths
python -m codex.ast.cli diff pathA pathB --json
```

## Testing

Run the test suite:

```bash
pytest tests/ast/ -v
```

With coverage:

```bash
pytest tests/ast/ --cov=src/codex/ast --cov-report=term-missing
```

**Current coverage: 97 tests passing**

## Architecture

The module follows these design principles:

1. **Language Agnostic**: AST nodes are independent of source language
2. **Graceful Degradation**: libcst primary with ast fallback
3. **Efficient Algorithms**: Tarjan's SCC for O(V+E) cycle detection
4. **Extensible**: Easy to add new node types, metrics, and smell rules
5. **Multi-Format Export**: Support for various output formats
6. **Well-Tested**: 97 tests with unit and integration coverage

## Dependencies

**Core:**
- libcst >= 1.0.0 (Universal Python parser)
- radon >= 6.0.0 (Complexity metrics)
- parso >= 0.8.0 (Fallback parser)

**Optional:**
- tree-sitter >= 0.20.0 (Multi-language parsing)
- sqlparse >= 0.5.0 (SQL parsing, security-patched)

## API Reference

### StandardizedASTNode

Language-agnostic AST node representation with parent-child relationships, tree traversal, and JSON serialization.

### UniversalParser

Parse Python source code into StandardizedASTNode trees using libcst (primary) or stdlib ast (fallback).

### DependencyGraph

Directed graph for dependency analysis with cycle detection using Tarjan's strongly connected components algorithm (O(V+E) time complexity).

### MetricsAggregator

Aggregate and correlate code quality metrics including cyclomatic complexity, lines of code, and maintainability index.

### CodeSmellDetector

Rules engine for detecting code quality issues with configurable thresholds and rule enable/disable.

### KnowledgeGraphExporter

Export AST analysis results to multiple formats (JSON, GraphML, DOT, SQLite, Markdown).

See inline documentation for detailed API information.

## License

MIT License - see [LICENSE](../../LICENSE) for details.
