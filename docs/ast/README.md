# Codex AST Analysis Module

## Overview

The Codex AST Analysis module provides a unified framework for analyzing Abstract Syntax Trees (ASTs) across multiple languages. It offers language-agnostic representations, dependency analysis, and code quality metrics.

## Features

- **StandardizedASTNode**: Language-agnostic AST node representation
- **DependencyGraph**: Cycle detection using Tarjan's algorithm
- **MetricsAggregator**: Code quality metrics and correlation analysis
- **CLI Tools**: Command-line interface for AST analysis

## Installation

Core dependencies are included in the base installation:

```bash
pip install -e .
```text

For optional features (tree-sitter, SQL parsing):

```bash
pip install -e ".[ast]"
```text

## Quick Start

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
```text

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
```text

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
```text

## CLI Usage

```bash
# Analyze a file or directory
python -m codex.ast.cli analyze src/mycode/

# Run a full audit
python -m codex.ast.cli audit . --output audit_report.html

# Compare metrics between commits
python -m codex.ast.cli diff HEAD~1 HEAD --metric complexity
```text

## Testing

Run the test suite:

```bash
pytest tests/ast/ -v
```text

With coverage:

```bash
pytest tests/ast/ --cov=src/codex/ast --cov-report=term-missing
```text

**Current coverage: 96.38%** (25 tests, all passing)

## Architecture

The module follows these design principles:

1. **Language Agnostic**: AST nodes are independent of source language
2. **Efficient Algorithms**: Tarjan's SCC for O(V+E) cycle detection
3. **Extensible**: Easy to add new node types and metrics
4. **Well-Tested**: 96%+ test coverage with unit and integration tests

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

### DependencyGraph

Directed graph for dependency analysis with cycle detection using Tarjan's strongly connected components algorithm (O(V+E) time complexity).

### MetricsAggregator

Aggregate and correlate code quality metrics including cyclomatic complexity, lines of code, and maintainability index.

See inline documentation for detailed API information.

## License

MIT License - see [LICENSE](../../LICENSE) for details.
