# AST Standardization - Common Implementation Patterns

**Created:** Current Cycle-01-03  
**Status:** 📋 Review Ready  
**Purpose:** Identify common patterns from existing implementations to establish foundation  
**Source:** Analysis of 6 AST planning documents + Unified Agent Framework patterns

---

## Executive Summary

Analysis of the AST Standardization plans reveals **8 common implementation patterns** that can be directly reused from the completed Unified Agent Framework. This document maps existing patterns to AST requirements, reducing implementation effort by an estimated **40-60%**.

### Pattern Reuse Opportunity Matrix

| Pattern Category | Existing Implementation | AST Application | Reuse Level |
|-----------------|------------------------|-----------------|-------------|
| Data Structures | StandardizedASTNode (planned) | ≈ CognitiveAgent patterns | 80% |
| Plugin System | PatternRecognizer + Matchers | AST Analyzers | 90% |
| Graph Processing | DependencyGraph (planned) | ≈ Orchestrator DAG | 75% |
| CLI Interface | brain_cli.py | codex-analyze CLI | 95% |
| Configuration | FrameworkConfig | AST Config | 100% |
| Storage Layer | CognitiveBrain (SQLite) | AST Storage | 90% |
| Error Handling | Exception hierarchy | AST Exceptions | 100% |
| Testing Patterns | 39 tests in core/ | AST Test Suite | 85% |

---

## Part 1: Core Data Structure Patterns

### 1.1 Dataclass-Based Entity Pattern

**Existing Implementation:** `base_agent.py`, `orchestrator.py`

```python
# Pattern: Immutable dataclass with defaults and metadata
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class StandardizedASTNode:
    """Language-agnostic AST representation."""
    
    # Identity (required)
    node_id: str
    type: str
    name: str
    
    # Structure (with defaults)
    parent: Optional["StandardizedASTNode"] = None
    children: List["StandardizedASTNode"] = field(default_factory=list)
    
    # Metadata (extensible)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Computed properties
    @property
    def depth(self) -> int:
        """Calculate tree depth."""
        if self.parent is None:
            return 0
        return self.parent.depth + 1
```

**Reuse From:** `AgentTask` in orchestrator.py (lines 23-35)

### 1.2 Source Location Pattern

**Existing Implementation:** `pattern_recognizer.py`

```python
@dataclass
class SourceLocation:
    """Precise code location - matches Pattern.locations format."""
    file_path: Path
    line_start: int
    line_end: int
    column_start: int = 0
    column_end: int = 0
    
    def __str__(self) -> str:
        return f"{self.file_path}:{self.line_start}:{self.column_start}"
    
    @classmethod
    def from_string(cls, location: str) -> "SourceLocation":
        """Parse 'file:line:col' format."""
        parts = location.split(":")
        return cls(
            file_path=Path(parts[0]),
            line_start=int(parts[1]) if len(parts) > 1 else 1,
            column_start=int(parts[2]) if len(parts) > 2 else 0,
            line_end=int(parts[1]) if len(parts) > 1 else 1,
            column_end=int(parts[2]) if len(parts) > 2 else 0
        )
```

**Reuse From:** `Pattern` dataclass in pattern_recognizer.py (lines 16-24)

---

## Part 2: Plugin/Analyzer System Patterns

### 2.1 Abstract Matcher Pattern

**Existing Implementation:** `pattern_recognizer.py` (PatternMatcher ABC)

```python
from abc import ABC, abstractmethod

class ASTAnalyzer(ABC):
    """Abstract base class for AST analyzers."""
    
    @abstractmethod
    def analyze(self, node: StandardizedASTNode) -> List[Finding]:
        """Analyze a node and return findings."""
        pass
    
    @abstractmethod
    def get_analyzer_type(self) -> str:
        """Get the type of analysis this analyzer performs."""
        pass
    
    def supports_node_type(self, node_type: str) -> bool:
        """Override to filter which nodes this analyzer processes."""
        return True


class ComplexityAnalyzer(ASTAnalyzer):
    """Concrete analyzer for cyclomatic complexity."""
    
    def analyze(self, node: StandardizedASTNode) -> List[Finding]:
        if node.type != "function":
            return []
        complexity = self._calculate_complexity(node)
        if complexity > self.threshold:
            return [Finding(
                type="high_complexity",
                location=node.source_location,
                message=f"Complexity {complexity} exceeds threshold {self.threshold}"
            )]
        return []
    
    def get_analyzer_type(self) -> str:
        return "complexity"
```

**Reuse From:** `PatternMatcher` ABC + `ExceptionPatternMatcher` (lines 27-80)

### 2.2 Plugin Registry Pattern

**Existing Implementation:** `pattern_recognizer.py` (PatternRecognizer)

```python
class AnalyzerRegistry:
    """Registry for AST analyzers."""
    
    def __init__(self):
        self.analyzers: Dict[str, ASTAnalyzer] = {}
        self._register_defaults()
    
    def _register_defaults(self):
        """Register built-in analyzers."""
        self.register(ComplexityAnalyzer())
        self.register(DependencyAnalyzer())
        self.register(CodeSmellAnalyzer())
    
    def register(self, analyzer: ASTAnalyzer):
        """Register an analyzer."""
        self.analyzers[analyzer.get_analyzer_type()] = analyzer
    
    def analyze_all(self, tree: StandardizedASTNode) -> List[Finding]:
        """Run all registered analyzers on tree."""
        findings = []
        for node in self._walk_tree(tree):
            for analyzer in self.analyzers.values():
                if analyzer.supports_node_type(node.type):
                    findings.extend(analyzer.analyze(node))
        return findings
```

**Reuse From:** `PatternRecognizer` class (lines 110-200)

---

## Part 3: Graph Processing Patterns

### 3.1 DAG Validation Pattern

**Existing Implementation:** `orchestrator.py` (_validate_dependencies)

```python
class DependencyGraph:
    """Dependency graph with cycle detection."""
    
    def __init__(self):
        self.nodes: Dict[str, Set[str]] = {}  # node -> dependencies
    
    def add_node(self, node_id: str, dependencies: List[str] = None):
        """Add a node with its dependencies."""
        self.nodes[node_id] = set(dependencies or [])
    
    def has_cycle(self) -> bool:
        """Check for cycles using DFS (Tarjan's algorithm)."""
        visited = set()
        rec_stack = set()
        
        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in self.nodes.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in self.nodes:
            if node not in visited:
                if dfs(node):
                    return True
        return False
    
    def topological_sort(self) -> List[str]:
        """Return nodes in topological order."""
        if self.has_cycle():
            raise ValueError("Cannot sort graph with cycles")
        
        visited = set()
        order = []
        
        def visit(node: str):
            if node in visited:
                return
            visited.add(node)
            for dep in self.nodes.get(node, []):
                visit(dep)
            order.append(node)
        
        for node in self.nodes:
            visit(node)
        
        return order
```

**Reuse From:** `_validate_dependencies()` method (lines 107-140)

---

## Part 4: CLI Interface Patterns

### 4.1 Subcommand CLI Pattern

**Existing Implementation:** `brain_cli.py`

```python
# Pattern: argparse with subparsers and command functions
def main():
    parser = argparse.ArgumentParser(description="AST Analysis CLI")
    parser.add_argument("--config", help="Config file path")
    
    subparsers = parser.add_subparsers(dest="command")
    
    # Analyze command
    analyze = subparsers.add_parser("analyze", help="Analyze codebase")
    analyze.add_argument("path", help="Path to analyze")
    analyze.add_argument("--format", choices=["json", "text"], default="text")
    analyze.set_defaults(func=cmd_analyze)
    
    # Audit command
    audit = subparsers.add_parser("audit", help="Run full audit")
    audit.add_argument("--baseline", help="Compare against baseline")
    audit.set_defaults(func=cmd_audit)
    
    # Diff command
    diff = subparsers.add_parser("diff", help="Compare two analyses")
    diff.add_argument("before", help="Before analysis file")
    diff.add_argument("after", help="After analysis file")
    diff.set_defaults(func=cmd_diff)
    
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)
```

**Reuse From:** `brain_cli.py` (100% reusable pattern)

---

## Part 5: Storage Layer Patterns

### 5.1 SQLite Context Manager Pattern

**Existing Implementation:** `cognitive_brain.py`

```python
class ASTStorage:
    """SQLite storage for AST analysis results."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_schema()
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _initialize_schema(self):
        """Create database schema."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analyses (
                    analysis_id TEXT PRIMARY KEY,
                    file_path TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    node_count INTEGER,
                    metrics TEXT,
                    findings TEXT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS nodes (
                    node_id TEXT PRIMARY KEY,
                    analysis_id TEXT NOT NULL,
                    type TEXT NOT NULL,
                    name TEXT,
                    parent_id TEXT,
                    line_start INTEGER,
                    line_end INTEGER,
                    metadata TEXT,
                    FOREIGN KEY (analysis_id) REFERENCES analyses(analysis_id)
                )
            """)
```

**Reuse From:** `CognitiveBrain` class (lines 16-100)

---

## Part 6: Configuration Patterns

### 6.1 Environment-Override Config Pattern

**Existing Implementation:** `config.py`

```python
@dataclass
class ASTConfig:
    """AST analysis configuration."""
    
    # Parser configuration
    parser_backend: str = "libcst"  # or "tree-sitter", "parso"
    parse_timeout: int = 30  # seconds
    
    # Analysis configuration
    complexity_threshold: int = 10
    max_function_lines: int = 50
    max_file_lines: int = 500
    
    # Output configuration
    output_format: str = "json"
    output_path: Path = field(default_factory=lambda: Path("ast_output"))
    
    # Performance configuration
    max_parallel: int = 4
    cache_enabled: bool = True
    cache_path: Path = field(default_factory=lambda: Path(".ast_cache"))
    
    def __post_init__(self):
        """Apply environment variable overrides."""
        if env_backend := os.getenv("AST_PARSER_BACKEND"):
            self.parser_backend = env_backend
        
        if env_threshold := os.getenv("AST_COMPLEXITY_THRESHOLD"):
            try:
                self.complexity_threshold = int(env_threshold)
            except ValueError:
                pass
        
        if env_parallel := os.getenv("AST_MAX_PARALLEL"):
            try:
                self.max_parallel = int(env_parallel)
            except ValueError:
                pass
```

**Reuse From:** `FrameworkConfig` class (100% pattern match)

---

## Part 7: Error Handling Patterns

### 7.1 Exception Hierarchy Pattern

**Existing Implementation:** Derived from `agents/exceptions.py`

```python
class ASTError(Exception):
    """Base exception for AST operations."""
    pass


class ParseError(ASTError):
    """Error during parsing."""
    def __init__(self, file_path: Path, line: int, message: str):
        self.file_path = file_path
        self.line = line
        super().__init__(f"{file_path}:{line}: {message}")


class AnalysisError(ASTError):
    """Error during analysis."""
    pass


class StorageError(ASTError):
    """Error during storage operations."""
    pass


class ConfigurationError(ASTError):
    """Error in configuration."""
    pass
```

---

## Part 8: Testing Patterns

### 8.1 Fixture-Based Testing Pattern

**Existing Implementation:** `tests/test_*.py`

```python
import pytest
import tempfile
from pathlib import Path

@pytest.fixture
def temp_workspace():
    """Create temporary workspace for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        # Create test Python file
        (workspace / "test_module.py").write_text('''
def complex_function(x):
    if x > 0:
        if x > 10:
            return "big"
        return "small"
    return "negative"
''')
        yield workspace

@pytest.fixture
def sample_ast_node():
    """Create sample AST node for testing."""
    return StandardizedASTNode(
        node_id="test-001",
        type="function",
        name="test_function",
        metadata={"docstring": "Test function"}
    )

def test_complexity_analyzer(temp_workspace, sample_ast_node):
    """Test complexity calculation."""
    analyzer = ComplexityAnalyzer(threshold=5)
    findings = analyzer.analyze(sample_ast_node)
    assert isinstance(findings, list)
```

**Reuse From:** Test fixtures in `test_integration.py`, `test_cognitive_brain.py`

---

## Implementation Recommendations

### Phase 1: Quick Wins (5 days) - Using Patterns

| Day | Task | Pattern Source | New Code Needed |
|-----|------|---------------|-----------------|
| 1 | Create StandardizedASTNode | Dataclass pattern | 30% |
| 1 | Create SourceLocation | Pattern.locations | 20% |
| 2 | Implement DependencyGraph | Orchestrator DAG | 25% |
| 2 | Add cycle detection | _validate_dependencies | 0% (copy) |
| 3 | Create ASTAnalyzer ABC | PatternMatcher | 20% |
| 3 | Implement ComplexityAnalyzer | ExceptionPatternMatcher | 40% |
| 4 | Create ASTStorage | CognitiveBrain | 30% |
| 4 | Add codex-analyze CLI | brain_cli.py | 20% |
| 5 | Create ASTConfig | FrameworkConfig | 10% |
| 5 | Add test suite (20+ tests) | test_*.py patterns | 30% |

**Estimated Effort Reduction:** 45% (from patterns reuse)

---

## Files to Create (Mapped to Patterns)

```text
src/codex_ml/ast/
├── __init__.py                     # Module exports
├── core/
│   ├── __init__.py
│   ├── node.py                     # Pattern 1.1 + 1.2
│   ├── exceptions.py               # Pattern 7.1
│   └── config.py                   # Pattern 6.1 (copy from core/)
├── analysis/
│   ├── __init__.py
│   ├── base_analyzer.py            # Pattern 2.1
│   ├── registry.py                 # Pattern 2.2
│   ├── complexity.py               # Custom (uses radon)
│   └── smells.py                   # Custom
├── graph/
│   ├── __init__.py
│   └── dependency_graph.py         # Pattern 3.1
├── storage/
│   ├── __init__.py
│   └── sqlite_storage.py           # Pattern 5.1
├── cli/
│   ├── __init__.py
│   └── main.py                     # Pattern 4.1
└── tests/
    ├── __init__.py
    ├── conftest.py                 # Pattern 8.1
    ├── test_node.py
    ├── test_analyzers.py
    ├── test_graph.py
    └── test_storage.py
```

---

## Validation Checklist

Before starting AST implementation:

- [x] All patterns documented with source references
- [x] Reuse percentages estimated
- [x] File structure mapped
- [x] Implementation order defined
- [ ] Dependencies added to pyproject.toml
- [ ] Team allocated for Phase 1

---

## Related Documents

| Document | Purpose | Status |
|----------|---------|--------|
| AST_IMPLEMENTATION_ROADMAP.md | Full roadmap | Reference |
| AST_ARCHITECTURE_DESIGN.md | Architecture spec | Reference |
| AST_Standardization_Requirements.md | Requirements | Reference |
| COGNITIVE_BRAIN_UNIFIED_IMPLEMENTATION_TASKS.md | Completed tasks | ✅ Complete |

---

**Next Steps:** 
1. Stakeholder review of pattern reuse approach
2. Approve Phase 1 Quick Wins (5 days)
3. Add dependencies to pyproject.toml
4. Begin implementation using documented patterns
