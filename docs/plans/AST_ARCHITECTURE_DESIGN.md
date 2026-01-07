# AST Standardization - Architecture Design

**Generated**: 2025-11-09  
**Purpose**: Comprehensive architecture design for AST standardization  
**Status**: DESIGN - Not yet implemented

---

## Module Organization

```text
src/codex_ml/ast/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── standardized_node.py      # StandardizedASTNode dataclass
│   ├── source_location.py        # SourceLocation dataclass
│   └── node_types.py             # Enum of node types
├── parsers/
│   ├── __init__.py
│   ├── base_parser.py            # Abstract parser interface
│   ├── python_parser.py          # libcst-based Python parser
│   ├── yaml_parser.py            # YAML parser
│   └── fallback_parser.py        # Parso-based fallback
├── analysis/
│   ├── __init__.py
│   ├── complexity.py             # Cyclomatic/cognitive complexity
│   ├── dependencies.py           # Dependency graph builder
│   ├── metrics.py                # Metrics aggregation
│   └── smells.py                 # Code smell detection
├── graph/
│   ├── __init__.py
│   ├── dependency_graph.py       # Graph data structure
│   ├── cycles.py                 # Circular dependency detection
│   └── exporters.py              # JSON/SQLite/DOT export
├── plugins/
│   ├── __init__.py
│   ├── registry.py               # Plugin registration system
│   └── base_plugin.py            # Plugin interface
├── cli/
│   ├── __init__.py
│   ├── analyze.py                # codex-analyze command
│   ├── audit.py                  # codex-audit command
│   └── diff.py                   # codex-diff command
└── utils/
    ├── __init__.py
    ├── error_handling.py         # Standard error handling
    └── caching.py                # Parse result caching
```text

---

## Core Data Structures

### StandardizedASTNode

```python
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from pathlib import Path

@dataclass
class SourceLocation:
    """Precise code location."""
    file_path: Path
    line_start: int
    line_end: int
    column_start: int
    column_end: int
    
    def __str__(self) -> str:
        return f"{self.file_path}:{self.line_start}:{self.column_start}"

@dataclass
class StandardizedASTNode:
    """Language-agnostic AST representation."""
    
    # Identity
    node_id: str                                    # Unique identifier (UUID)
    type: str                                       # "module", "function", "class", etc.
    name: str                                       # Identifier name
    
    # Structure
    parent: Optional["StandardizedASTNode"] = None
    children: List["StandardizedASTNode"] = field(default_factory=list)
    
    # Location
    source_location: SourceLocation = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)  # Docstrings, decorators, etc.
    
    # Metrics
    complexity: int = 0                             # Cyclomatic complexity
    cognitive_complexity: int = 0                   # Cognitive complexity
    lines_of_code: int = 0                          # Physical LOC
    
    # Typing
    type_hint: Optional[str] = None                 # Type annotation
    return_type: Optional[str] = None               # Return type annotation
    
    def add_child(self, child: "StandardizedASTNode") -> None:
        """Add child node and set parent relationship."""
        child.parent = self
        self.children.append(child)
    
    def get_depth(self) -> int:
        """Calculate depth in AST tree."""
        depth = 0
        node = self.parent
        while node:
            depth += 1
            node = node.parent
        return depth
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for JSON export."""
        return {
            "id": self.node_id,
            "type": self.type,
            "name": self.name,
            "location": str(self.source_location),
            "complexity": self.complexity,
            "children": [c.node_id for c in self.children],
            "metadata": self.metadata,
        }
```text

---

## Parser Architecture

### Abstract Parser Interface

```python
from abc import ABC, abstractmethod
from typing import Optional

class BaseParser(ABC):
    """Abstract base for all parsers."""
    
    @abstractmethod
    def parse(self, source_code: str, file_path: Path) -> StandardizedASTNode:
        """Parse source code into standardized AST.
        
        Args:
            source_code: Source code string
            file_path: Path to source file
            
        Returns:
            Root StandardizedASTNode
            
        Raises:
            ParseError: If parsing fails
        """
        pass
    
    @abstractmethod
    def can_parse(self, file_path: Path) -> bool:
        """Check if parser can handle this file.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if parser supports this file type
        """
        pass
    
    def parse_with_fallback(
        self,
        source_code: str,
        file_path: Path
    ) -> Optional[StandardizedASTNode]:
        """Parse with graceful degradation."""
        try:
            return self.parse(source_code, file_path)
        except ParseError as e:
            logger.warning(f"Primary parse failed for {file_path}: {e}")
            # Fallback to parso or partial parse
            return self._fallback_parse(source_code, file_path)
    
    def _fallback_parse(
        self,
        source_code: str,
        file_path: Path
    ) -> Optional[StandardizedASTNode]:
        """Fallback parsing strategy."""
        # Implementation uses parso for tolerant parsing
        pass
```text

---

## Dependency Graph

### Graph Data Structure

```python
from typing import Set, Dict, List
from dataclasses import dataclass, field

@dataclass
class DependencyNode:
    """Node in dependency graph."""
    module_path: str
    imports: Set[str] = field(default_factory=set)
    imported_by: Set[str] = field(default_factory=set)
    functions: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)

class DependencyGraph:
    """Directed graph of module dependencies."""
    
    def __init__(self):
        self.nodes: Dict[str, DependencyNode] = {}
        self.edges: List[tuple[str, str]] = []
    
    def add_module(self, module_path: str) -> None:
        """Add module to graph."""
        if module_path not in self.nodes:
            self.nodes[module_path] = DependencyNode(module_path)
    
    def add_dependency(self, from_module: str, to_module: str) -> None:
        """Add dependency edge."""
        self.add_module(from_module)
        self.add_module(to_module)
        
        self.nodes[from_module].imports.add(to_module)
        self.nodes[to_module].imported_by.add(from_module)
        self.edges.append((from_module, to_module))
    
    def find_cycles(self) -> List[List[str]]:
        """Detect circular dependencies using Tarjan's algorithm."""
        # Implementation of strongly connected components detection
        pass
    
    def to_dot(self) -> str:
        """Export to GraphViz DOT format."""
        lines = ["digraph dependencies {"]
        for from_mod, to_mod in self.edges:
            lines.append(f'  "{from_mod}" -> "{to_mod}";')
        lines.append("}")
        return "\n".join(lines)
    
    def to_json(self) -> Dict:
        """Export to JSON."""
        return {
            "nodes": [
                {
                    "module": path,
                    "imports": list(node.imports),
                    "imported_by": list(node.imported_by),
                }
                for path, node in self.nodes.items()
            ],
            "edges": self.edges,
        }
```text

---

## Metrics Aggregation

### Metrics Aggregator

```python
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class CodebaseMetrics:
    """Aggregated metrics for entire codebase."""
    
    # Counts
    total_files: int = 0
    total_modules: int = 0
    total_functions: int = 0
    total_classes: int = 0
    total_lines: int = 0
    
    # Complexity
    avg_complexity: float = 0.0
    max_complexity: int = 0
    high_complexity_count: int = 0  # >10
    
    # Dependencies
    total_imports: int = 0
    circular_dependencies: int = 0
    
    # Code Quality
    code_smells: Dict[str, int] = field(default_factory=dict)
    duplication_ratio: float = 0.0
    
    # Coverage (if integrated)
    test_coverage: float = 0.0
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            "totals": {
                "files": self.total_files,
                "modules": self.total_modules,
                "functions": self.total_functions,
                "classes": self.total_classes,
                "lines": self.total_lines,
            },
            "complexity": {
                "average": self.avg_complexity,
                "maximum": self.max_complexity,
                "high_count": self.high_complexity_count,
            },
            "dependencies": {
                "imports": self.total_imports,
                "circular": self.circular_dependencies,
            },
            "quality": {
                "smells": self.code_smells,
                "duplication": self.duplication_ratio,
                "coverage": self.test_coverage,
            },
        }

class MetricsAggregator:
    """Aggregate metrics from AST analysis."""
    
    def __init__(self):
        self.metrics = CodebaseMetrics()
    
    def aggregate_from_ast(self, root: StandardizedASTNode) -> None:
        """Walk AST and accumulate metrics."""
        # Recursive tree walk to collect metrics
        pass
    
    def aggregate_from_graph(self, graph: DependencyGraph) -> None:
        """Extract dependency metrics from graph."""
        self.metrics.total_imports = len(graph.edges)
        self.metrics.circular_dependencies = len(graph.find_cycles())
    
    def export(self, format: str = "json") -> str:
        """Export metrics in specified format."""
        if format == "json":
            import json
            return json.dumps(self.metrics.to_dict(), indent=2)
        elif format == "markdown":
            return self._to_markdown()
        else:
            raise ValueError(f"Unsupported format: {format}")
```text

---

## Plugin Architecture

### Plugin Registry

```python
from typing import Dict, Type, Callable
from abc import ABC, abstractmethod

class BasePlugin(ABC):
    """Base class for all AST plugins."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name."""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version."""
        pass
    
    @abstractmethod
    def analyze(self, ast: StandardizedASTNode) -> Dict:
        """Analyze AST and return findings."""
        pass

class PluginRegistry:
    """Registry for AST analysis plugins."""
    
    def __init__(self):
        self._plugins: Dict[str, Type[BasePlugin]] = {}
    
    def register(self, plugin_class: Type[BasePlugin]) -> None:
        """Register a plugin."""
        plugin = plugin_class()
        self._plugins[plugin.name] = plugin_class
    
    def get_plugin(self, name: str) -> BasePlugin:
        """Get plugin instance by name."""
        if name not in self._plugins:
            raise KeyError(f"Plugin not found: {name}")
        return self._plugins[name]()
    
    def run_all(self, ast: StandardizedASTNode) -> Dict[str, Dict]:
        """Run all registered plugins."""
        results = {}
        for name, plugin_class in self._plugins.items():
            plugin = plugin_class()
            results[name] = plugin.analyze(ast)
        return results

# Global registry
registry = PluginRegistry()
```text

---

## Error Handling Standards

### Standard Exceptions

```python
class ASTError(Exception):
    """Base exception for AST operations."""
    pass

class ParseError(ASTError):
    """Raised when parsing fails."""
    pass

class AnalysisError(ASTError):
    """Raised when analysis fails."""
    pass

class ExportError(ASTError):
    """Raised when export fails."""
    pass

# Standard error handling pattern
def safe_parse(source: str, file_path: Path) -> Optional[StandardizedASTNode]:
    """Parse with standard error handling."""
    try:
        parser = get_parser_for_file(file_path)
        return parser.parse(source, file_path)
    except ParseError as e:
        logger.error(f"Parse failed for {file_path}: {e}")
        return None
    except Exception as e:
        logger.exception(f"Unexpected error parsing {file_path}: {e}")
        return None
```text

---

## Performance Considerations

### Caching Strategy

```python
from functools import lru_cache
from typing import Tuple
import hashlib

class ParseCache:
    """Cache parsed ASTs to avoid re-parsing."""
    
    def __init__(self, max_size: int = 1000):
        self.cache: Dict[str, StandardizedASTNode] = {}
        self.max_size = max_size
    
    def _get_cache_key(self, source: str, file_path: Path) -> str:
        """Generate cache key from content hash."""
        content_hash = hashlib.sha256(source.encode()).hexdigest()[:16]
        return f"{file_path}:{content_hash}"
    
    def get(self, source: str, file_path: Path) -> Optional[StandardizedASTNode]:
        """Get cached AST if available."""
        key = self._get_cache_key(source, file_path)
        return self.cache.get(key)
    
    def put(self, source: str, file_path: Path, ast: StandardizedASTNode) -> None:
        """Cache parsed AST."""
        key = self._get_cache_key(source, file_path)
        
        # LRU eviction if cache full
        if len(self.cache) >= self.max_size:
            # Remove oldest entry (simplified - use OrderedDict for true LRU)
            first_key = next(iter(self.cache))
            del self.cache[first_key]
        
        self.cache[key] = ast
```text

---

## Integration Points

### MATURITY_REMAINING_WORK.md Auto-Update

```python
def update_maturity_report(metrics: CodebaseMetrics, report_path: Path) -> None:
    """Update MATURITY_REMAINING_WORK.md with AST findings."""
    
    # Load existing report
    content = report_path.read_text()
    
    # Find AST findings section
    ast_section = f"""
## AST Analysis Findings

**Generated**: {datetime.now().isoformat()}

### Code Complexity
- Average Complexity: {metrics.avg_complexity:.2f}
- High Complexity Functions: {metrics.high_complexity_count}
- Maximum Complexity: {metrics.max_complexity}

### Dependencies
- Total Imports: {metrics.total_imports}
- Circular Dependencies: {metrics.circular_dependencies}

### Code Quality
{_format_code_smells(metrics.code_smells)}

### Recommendations
{_generate_recommendations(metrics)}
"""
    
    # Replace or append AST section
    if "## AST Analysis Findings" in content:
        # Update existing section
        pass
    else:
        # Append new section
        content += "\n" + ast_section
    
    # Write back
    report_path.write_text(content)
```text

---

## Next Steps

1. ✅ AI Assistant autonomous architecture review
2. ⏳ Prototype StandardizedASTNode
3. ⏳ Implement Python parser
4. ⏳ Create dependency graph
5. ⏳ Build metrics aggregator
6. ⏳ Develop plugin system
7. ⏳ Create CLI tools
8. ⏳ Write comprehensive tests

**Status**: DESIGN COMPLETE - Awaiting implementation approval  
**Owner**: Architecture Lead  
**Timeline**: Sprint 1-3 (6-9 weeks) once approved
