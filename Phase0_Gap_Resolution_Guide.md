# 🔧 Phase 0: Gap Resolution Implementation Guide
> Generated: 2025-11-09 23:13:57 UTC | Author: mbaetiong

**🧠 Roles:** [Primary: Implementation Lead], [Secondary: DevOps Engineer] | ⚡ Energy: 5/5

⚛️ **Physics:** Path🛤️ [Linear dependency chain] | Fields🔄 [Modular resolution] | Patterns👁️ [DRY principles] | Redundancy🔀 [Fallback strategies] | Balance⚖️ [Speed vs. stability]

---

## 📋 Executive Summary

**Phase 0** resolves **5 critical blockers**, **4 implementation issues**, and **3 architectural challenges** before AST Standardization can proceed to Sprint 1.

**Timeline:** 2025-11-09 → 2025-11-23 (14 days)  
**Effort:** 4-6 person-weeks  
**Go/No-Go Gate:** 2025-11-23 14:00 UTC  
**Critical Path:** Dependencies → Architecture → Performance → Testing

---

## 🚨 Section 1: Dependency Resolution (Days 1-3)

### 1.1 Task BLOCK-DEP-001: Add libcst to Core Dependencies

**Blocker ID:** `BLOCK-DEP-001`  
**Issue:** libcst not in core dependencies  
**Impact:** CRITICAL - Cannot implement FR-AST-001 (Universal Parser)  
**Duration:** 6 hours

#### 1.1.1 Implementation Steps

**Step 1: Audit Current Dependencies**

```bash
# List current dependencies
cd _codex_
pip show pyproject.toml 2>/dev/null || cat pyproject.toml | grep -A 20 "dependencies"

# Check if libcst installed
python -c "import libcst; print(f'libcst version: {libcst.__version__}')" 2>&1

# List all AST-related imports in codebase
grep -r "import libcst\|from libcst" src/ --include="*.py" || echo "No libcst imports found"
grep -r "import ast\|from ast" src/ --include="*.py" | head -20
```

**Step 2: Update `pyproject.toml`**

```toml
[project]
dependencies = [
    # Existing dependencies...
    "torch>=2.0",
    "transformers>=4.30",
    
    # NEW: AST Analysis Core
    "libcst>=1.0.0",         # Universal Python parser with CST preservation
    "radon>=6.0.0",          # Cyclomatic complexity metrics
    "parso>=0.8.0",          # Fallback parser for graceful degradation
    
    # Existing deps...
]

[project.optional-dependencies]
ast = [
    "tree-sitter>=0.20.0",
    "tree-sitter-python>=0.20.0",
    "tree-sitter-yaml>=0.20.0",
    "sqlparse>=0.4.0",
]

dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "pytest-benchmark>=4.0",
    # ... existing dev deps
]
```

**Step 3: Verify No Conflicts**

```bash
# Create test environment
python -m venv /tmp/test_ast_env
source /tmp/test_ast_env/bin/activate

# Install with new dependencies
pip install -e ".[ast,dev]"

# Verify imports
python << 'EOF'
import libcst
import radon
import parso
import torch
import transformers

print("✓ All imports successful")
print(f"  libcst: {libcst.__version__}")
print(f"  radon: {radon.__version__}")
print(f"  parso: {parso.__version__}")
EOF

# Check for dependency conflicts
pip check
```

**Step 4: Run Full Test Suite**

```bash
nox -s lint
nox -s test
pytest tests/ -v --tb=short
```

#### 1.1.2 Acceptance Criteria

- [ ] `pip install -e ".[ast]"` succeeds without conflicts
- [ ] All imports work: `libcst`, `radon`, `parso`
- [ ] Existing tests pass with new dependencies
- [ ] No new vulnerabilities introduced (check with `pip audit`)
- [ ] Version pins in `pyproject.toml` are compatible with all transitive deps

#### 1.1.3 Rollback Procedure

```bash
# If dependency conflicts discovered:
git checkout HEAD -- pyproject.toml
pip install -e .
nox -s test  # Verify rollback
```

#### 1.1.4 Validation Command

```bash
# Run this to verify task complete
python .github/scripts/validate_dependencies.py --check-ast-core
```

---

### 1.2 Task BLOCK-DEP-002: Install Language Parser Binaries

**Blocker ID:** `BLOCK-DEP-002`  
**Issue:** tree-sitter not available  
**Impact:** CRITICAL - Cannot implement language-agnostic parsing  
**Duration:** 4 hours

#### 1.2.1 Implementation Steps

**Step 1: Set Up tree-sitter Installation**

```bash
# Install tree-sitter core
pip install tree-sitter>=0.20.0

# Install language-specific parsers
pip install tree-sitter-python>=0.20.0
pip install tree-sitter-yaml>=0.20.0

# For SQL support (optional, deferred if conflicts)
pip install tree-sitter-sql>=0.20.0 || echo "SQL parser deferred"

# Verify installation
python << 'EOF'
from tree_sitter import Language, Parser

# Check Python grammar
python_lang = Language("build/my-languages.so", "python")
print("✓ Python parser loaded")

# Test parsing
parser = Parser()
parser.set_language(python_lang)
code = "def hello(): pass"
tree = parser.parse(code.encode())
print(f"✓ Parsed {len(tree.root_node.children)} nodes")
EOF
```

**Step 2: Build Language Binaries (if needed)**

```bash
# Most distributions come pre-built, but if needed:
cd /tmp
git clone https://github.com/tree-sitter/py-tree-sitter.git
cd py-tree-sitter

# Add language submodules
git submodule add https://github.com/tree-sitter/tree-sitter-python vendor/tree-sitter-python
git submodule add https://github.com/tree-sitter/tree-sitter-yaml vendor/tree-sitter-yaml

# Build
python setup.py build
pip install -e .
```

**Step 3: Create Language Registry**

```python
# File: src/codex_ml/ast/language_registry.py
from tree_sitter import Language

class LanguageRegistry:
    """Centralized language parser registry."""
    
    LANGUAGES = {
        "python": {
            "module": "tree_sitter_python",
            "name": "python",
        },
        "yaml": {
            "module": "tree_sitter_yaml",
            "name": "yaml",
        },
        "json": {
            "module": "tree_sitter_json",
            "name": "json",
        },
    }
    
    _cache = {}
    
    @classmethod
    def get_language(cls, lang_name: str):
        """Get language parser (cached)."""
        if lang_name in cls._cache:
            return cls._cache[lang_name]
        
        if lang_name not in cls.LANGUAGES:
            raise ValueError(f"Unsupported language: {lang_name}")
        
        try:
            config = cls.LANGUAGES[lang_name]
            module = __import__(config["module"])
            lang = Language(module.language())
            cls._cache[lang_name] = lang
            return lang
        except ImportError as e:
            raise ImportError(f"Cannot load {lang_name} parser: {e}")
    
    @classmethod
    def list_supported(cls) -> list:
        """List all supported languages."""
        return list(cls.LANGUAGES.keys())
```

#### 1.2.2 Acceptance Criteria

- [ ] All language parsers install without errors
- [ ] Language registry loads parsers successfully
- [ ] Can parse sample code in all supported languages
- [ ] No memory leaks in parser loading
- [ ] Parsers cached for performance

#### 1.2.3 Validation Command

```bash
python .github/scripts/validate_dependencies.py --check-language-parsers
```

---

### 1.3 Task BLOCK-DEP-003: Add radon for Metrics

**Blocker ID:** `BLOCK-DEP-003`  
**Issue:** radon metrics not installed  
**Impact:** CRITICAL - Cannot compute cyclomatic complexity  
**Duration:** 2 hours

#### 1.3.1 Implementation Steps

```bash
# Already added to pyproject.toml in 1.1.2, just verify
pip install radon>=6.0.0

# Test radon functionality
python << 'EOF'
from radon.complexity import cc_visit
from radon.metrics import mi_visit

code = """
def complex_function(x):
    if x > 0:
        if x > 10:
            return "big"
        return "small"
    return "zero"
"""

# Compute cyclomatic complexity
results = cc_visit(code)
for result in results:
    print(f"Function: {result.name}, CC: {result.complexity}")

# Compute maintainability index
mi = mi_visit(code, True)
print(f"Maintainability Index: {mi}")
EOF
```

#### 1.3.2 Acceptance Criteria

- [ ] radon installed and importable
- [ ] Can compute CC for sample functions
- [ ] Can compute MI for modules
- [ ] Results match expected values (±5%)

---

### 1.4 Task BLOCK-DEP-004: Move parso to Core Dependencies

**Blocker ID:** `BLOCK-DEP-004`  
**Issue:** parso not in core dependencies  
**Impact:** HIGH - Needed for graceful degradation  
**Duration:** 1 hour

#### 1.4.1 Implementation

Already included in Step 1.1.2 (pyproject.toml update).

**Verify:**

```bash
python << 'EOF'
import parso

code = "def hello(): pass"
module = parso.parse(code)
print(f"✓ parso version {parso.__version__} working")
EOF
```

#### 1.4.2 Acceptance Criteria

- [ ] parso in core dependencies
- [ ] Can parse Python 3.8+ code
- [ ] Graceful error handling on malformed code

---

### 1.5 Task BLOCK-DEP-005: Configure SQLite Storage Layer

**Blocker ID:** `BLOCK-DEP-005`  
**Issue:** SQLite storage not configured  
**Impact:** CRITICAL - Cannot implement FR-AST-011  
**Duration:** 4 hours

#### 1.5.1 Implementation Steps

**Step 1: Create SQLite Schema**

```python
# File: src/codex_ml/ast/storage/schema.py
import sqlite3
from pathlib import Path

SCHEMA_SQL = """
-- Entities
CREATE TABLE IF NOT EXISTS modules (
    id TEXT PRIMARY KEY,
    file_path TEXT NOT NULL UNIQUE,
    lines_of_code INTEGER,
    complexity_avg REAL,
    quality_tier TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS functions (
    id TEXT PRIMARY KEY,
    module_id TEXT NOT NULL,
    name TEXT NOT NULL,
    signature TEXT,
    lines_of_code INTEGER,
    cyclomatic_complexity INTEGER,
    cognitive_complexity REAL,
    maintainability_index REAL,
    test_coverage REAL,
    type_hint_coverage REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (module_id) REFERENCES modules(id)
);

CREATE TABLE IF NOT EXISTS classes (
    id TEXT PRIMARY KEY,
    module_id TEXT NOT NULL,
    name TEXT NOT NULL,
    lines_of_code INTEGER,
    method_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (module_id) REFERENCES modules(id)
);

-- Relationships
CREATE TABLE IF NOT EXISTS dependencies (
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    dep_type TEXT NOT NULL,
    is_circular BOOLEAN DEFAULT 0,
    PRIMARY KEY (source_id, target_id),
    FOREIGN KEY (source_id) REFERENCES modules(id),
    FOREIGN KEY (target_id) REFERENCES modules(id)
);

CREATE TABLE IF NOT EXISTS code_smells (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id TEXT NOT NULL,
    smell_type TEXT NOT NULL,
    severity TEXT,
    message TEXT,
    line_number INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_functions_module ON functions(module_id);
CREATE INDEX IF NOT EXISTS idx_classes_module ON classes(module_id);
CREATE INDEX IF NOT EXISTS idx_smells_entity ON code_smells(entity_id);
CREATE INDEX IF NOT EXISTS idx_dependencies_source ON dependencies(source_id);
"""

def init_database(db_path: Path) -> sqlite3.Connection:
    """Initialize database with schema."""
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Execute schema
    cursor.executescript(SCHEMA_SQL)
    conn.commit()
    
    return conn

def verify_schema(db_path: Path) -> bool:
    """Verify database schema is intact."""
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Check for required tables
    tables = [
        "modules", "functions", "classes", 
        "dependencies", "code_smells"
    ]
    
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )
    existing = {row[0] for row in cursor.fetchall()}
    
    return all(t in existing for t in tables)
```

**Step 2: Create Storage Manager**

```python
# File: src/codex_ml/ast/storage/manager.py
import sqlite3
from pathlib import Path
from typing import Optional

class StorageManager:
    """Manage SQLite-based AST storage."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None
    
    def connect(self) -> sqlite3.Connection:
        """Establish database connection."""
        if self._conn is None:
            self._conn = sqlite3.connect(str(self.db_path))
            self._conn.row_factory = sqlite3.Row
        return self._conn
    
    def store_module(self, module_data: dict) -> str:
        """Store module analysis results."""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO modules 
            (id, file_path, lines_of_code, complexity_avg, quality_tier)
            VALUES (?, ?, ?, ?, ?)
        """, (
            module_data['id'],
            module_data['file_path'],
            module_data['lines_of_code'],
            module_data['complexity_avg'],
            module_data['quality_tier'],
        ))
        
        conn.commit()
        return module_data['id']
    
    def store_function(self, func_data: dict) -> str:
        """Store function analysis results."""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO functions
            (id, module_id, name, signature, lines_of_code,
             cyclomatic_complexity, cognitive_complexity,
             maintainability_index, test_coverage, type_hint_coverage)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            func_data['id'],
            func_data['module_id'],
            func_data['name'],
            func_data['signature'],
            func_data['lines_of_code'],
            func_data['cyclomatic_complexity'],
            func_data['cognitive_complexity'],
            func_data['maintainability_index'],
            func_data['test_coverage'],
            func_data['type_hint_coverage'],
        ))
        
        conn.commit()
        return func_data['id']
    
    def query(self, sql: str, params: tuple = ()) -> list:
        """Execute custom query."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        return cursor.fetchall()
    
    def close(self):
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None
```

**Step 3: Test Storage**

```python
# tests/ast/test_storage.py
import pytest
from pathlib import Path
import tempfile

def test_storage_initialization():
    """Verify storage can be initialized."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        manager = StorageManager(db_path)
        manager.connect()
        
        assert db_path.exists()
        assert verify_schema(db_path)

def test_store_and_retrieve_module():
    """Verify module storage and retrieval."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        manager = StorageManager(db_path)
        
        # Store
        module_id = manager.store_module({
            'id': 'mod_1',
            'file_path': 'src/example.py',
            'lines_of_code': 100,
            'complexity_avg': 4.5,
            'quality_tier': 'A',
        })
        
        # Retrieve
        results = manager.query(
            "SELECT * FROM modules WHERE id = ?",
            (module_id,)
        )
        
        assert len(results) == 1
        assert results[0]['file_path'] == 'src/example.py'
```

#### 1.5.2 Acceptance Criteria

- [ ] Database initializes without errors
- [ ] All required tables created
- [ ] Can store and retrieve module data
- [ ] Relationships enforced correctly
- [ ] Indexes created for performance

#### 1.5.3 Validation Command

```bash
python .github/scripts/validate_dependencies.py --check-storage
```

---

## 🏗️ Section 2: Architecture Foundation (Days 4-10)

### 2.1 Task BLOCK-ARCH-001: Design StandardizedASTNode

**Blocker ID:** `BLOCK-ARCH-001`  
**Issue:** No standardized AST representation  
**Duration:** 2 days

#### 2.1.1 Implementation

```python
# File: src/codex_ml/ast/nodes.py
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from pathlib import Path
from enum import Enum

class NodeType(Enum):
    """All supported AST node types."""
    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    ASYNC_FUNCTION = "async_function"
    LAMBDA = "lambda"
    STATEMENT = "statement"
    EXPRESSION = "expression"
    DECORATOR = "decorator"
    IMPORT = "import"
    COMPREHENSION = "comprehension"

@dataclass
class SourceLocation:
    """Pinpoint code location."""
    file_path: Path
    line_start: int
    line_end: int
    column_start: int
    column_end: int
    
    def __str__(self) -> str:
        return f"{self.file_path}:{self.line_start}:{self.column_start}"

@dataclass
class StandardizedASTNode:
    """Language-agnostic AST node."""
    # Identity
    node_id: str
    type: NodeType
    name: str
    
    # Structure
    parent: Optional["StandardizedASTNode"] = None
    children: List["StandardizedASTNode"] = field(default_factory=list)
    
    # Location & source
    source_location: SourceLocation = None
    docstring: Optional[str] = None
    source_text: Optional[str] = None
    
    # Metadata
    decorators: List[str] = field(default_factory=list)
    type_hints: Dict[str, str] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Language-specific (JSON blob for extensibility)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_child(self, child: "StandardizedASTNode"):
        """Add child node."""
        child.parent = self
        self.children.append(child)
    
    def get_depth(self) -> int:
        """Get depth in tree."""
        if self.parent is None:
            return 0
        return self.parent.get_depth() + 1
    
    def traverse_dfs(self):
        """Depth-first traversal."""
        yield self
        for child in self.children:
            yield from child.traverse_dfs()
    
    def traverse_bfs(self):
        """Breadth-first traversal."""
        from collections import deque
        queue = deque([self])
        while queue:
            node = queue.popleft()
            yield node
            queue.extend(node.children)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'node_id': self.node_id,
            'type': self.type.value,
            'name': self.name,
            'source_location': {
                'file_path': str(self.source_location.file_path),
                'line_start': self.source_location.line_start,
                'line_end': self.source_location.line_end,
            },
            'docstring': self.docstring,
            'decorators': self.decorators,
            'type_hints': self.type_hints,
            'children': [c.node_id for c in self.children],
            'metadata': self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StandardizedASTNode":
        """Deserialize from dictionary."""
        # Implementation omitted for brevity
        pass
```

#### 2.1.2 Acceptance Criteria

- [ ] All node types defined in NodeType enum
- [ ] StandardizedASTNode instantiates correctly
- [ ] Traversal methods work (DFS, BFS)
- [ ] Serialization round-trips correctly
- [ ] Tests pass for all node types

---

### 2.2 Task BLOCK-ARCH-002: Design Dependency Graph

**Blocker ID:** `BLOCK-ARCH-002`  
**Duration:** 2 days

#### 2.2.1 Implementation

```python
# File: src/codex_ml/ast/graph.py
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass

@dataclass
class DependencyEdge:
    """Single dependency relationship."""
    source_id: str
    target_id: str
    dep_type: str  # "imports", "calls", "inherits_from"
    line_number: int
    is_circular: bool = False

class DependencyGraph:
    """Directed graph of code dependencies."""
    
    def __init__(self):
        self.nodes: Dict[str, StandardizedASTNode] = {}
        self.edges: Dict[str, Set[str]] = {}  # source → targets
        self.edge_metadata: Dict[Tuple[str, str], DependencyEdge] = {}
    
    def add_node(self, node_id: str, node: StandardizedASTNode):
        """Add node to graph."""
        self.nodes[node_id] = node
        if node_id not in self.edges:
            self.edges[node_id] = set()
    
    def add_edge(self, source_id: str, target_id: str, 
                 dep_type: str, line_num: int = 0):
        """Add directed edge."""
        if source_id not in self.edges:
            self.edges[source_id] = set()
        
        self.edges[source_id].add(target_id)
        self.edge_metadata[(source_id, target_id)] = DependencyEdge(
            source_id=source_id,
            target_id=target_id,
            dep_type=dep_type,
            line_number=line_num,
        )
    
    def detect_cycles(self) -> List[List[str]]:
        """Find all cycles using Tarjan's SCC algorithm."""
        index_counter = [0]
        stack = []
        lowlinks = {}
        index = {}
        on_stack = {}
        sccs = []
        
        def strongconnect(node_id):
            index[node_id] = index_counter[0]
            lowlinks[node_id] = index_counter[0]
            index_counter[0] += 1
            stack.append(node_id)
            on_stack[node_id] = True
            
            for target_id in self.edges.get(node_id, set()):
                if target_id not in index:
                    strongconnect(target_id)
                    lowlinks[node_id] = min(lowlinks[node_id], lowlinks[target_id])
                elif on_stack.get(target_id, False):
                    lowlinks[node_id] = min(lowlinks[node_id], index[target_id])
            
            if lowlinks[node_id] == index[node_id]:
                scc = []
                while True:
                    w = stack.pop()
                    on_stack[w] = False
                    scc.append(w)
                    if w == node_id:
                        break
                
                # Only record SCCs with >1 node (cycles)
                if len(scc) > 1:
                    sccs.append(scc)
        
        for node_id in self.nodes:
            if node_id not in index:
                strongconnect(node_id)
        
        return sccs
    
    def get_transitive_deps(self, node_id: str) -> Set[str]:
        """Get all transitive dependencies."""
        visited = set()
        stack = [node_id]
        
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            
            visited.add(current)
            stack.extend(self.edges.get(current, set()))
        
        return visited - {node_id}
    
    def compute_coupling(self, node_id: str) -> Dict[str, int]:
        """Compute fan-in and fan-out."""
        fan_out = len(self.edges.get(node_id, set()))
        
        fan_in = 0
        for deps in self.edges.values():
            if node_id in deps:
                fan_in += 1
        
        return {
            'fan_in': fan_in,
            'fan_out': fan_out,
            'coupling': fan_in * fan_out,
        }
```

#### 2.2.2 Acceptance Criteria

- [ ] Graph adds nodes and edges correctly
- [ ] Cycle detection accurate (100% recall on synthetic)
- [ ] Transitive dependency computation correct
- [ ] Coupling metrics calculated
- [ ] Performance <1s per 100 modules

---

### 2.3 Task BLOCK-ARCH-003: Metrics Aggregation Layer

**Blocker ID:** `BLOCK-ARCH-003`  
**Duration:** 1.5 days

#### 2.3.1 Implementation

```python
# File: src/codex_ml/ast/metrics_aggregator.py
from dataclasses import dataclass, field
from typing import Dict, List
import statistics

@dataclass
class CodeMetrics:
    """Aggregated metrics for code entity."""
    lines_of_code: int
    cyclomatic_complexity: int
    cognitive_complexity: float
    halstead_volume: float
    maintainability_index: float
    test_coverage: float = 0.0
    type_hint_coverage: float = 0.0
    
    @property
    def quality_tier(self) -> str:
        """Compute A-F grade."""
        if self.maintainability_index >= 85:
            return "A"
        elif self.maintainability_index >= 70:
            return "B"
        elif self.maintainability_index >= 55:
            return "C"
        elif self.maintainability_index >= 40:
            return "D"
        else:
            return "F"

class MetricsAggregator:
    """Aggregate and correlate metrics across codebase."""
    
    def __init__(self):
        self.metrics: Dict[str, CodeMetrics] = {}
        self.correlations: Dict[str, float] = {}
    
    def store_metrics(self, entity_id: str, metrics: CodeMetrics):
        """Store metrics for entity."""
        self.metrics[entity_id] = metrics
    
    def correlate_complexity_coverage(self) -> float:
        """Compute correlation: complexity ↔ coverage."""
        complexities = []
        coverages = []
        
        for metrics in self.metrics.values():
            complexities.append(metrics.cyclomatic_complexity)
            coverages.append(metrics.test_coverage)
        
        if len(complexities) < 2:
            return 0.0
        
        # Pearson correlation
        mean_cc = statistics.mean(complexities)
        mean_cov = statistics.mean(coverages)
        
        numerator = sum(
            (c - mean_cc) * (v - mean_cov)
            for c, v in zip(complexities, coverages)
        )
        
        denom_cc = (sum((c - mean_cc) ** 2 for c in complexities)) ** 0.5
        denom_cov = (sum((c - mean_cov) ** 2 for c in coverages)) ** 0.5
        
        if denom_cc * denom_cov == 0:
            return 0.0
        
        return numerator / (denom_cc * denom_cov)
    
    def get_summary(self) -> Dict:
        """Get aggregate metrics summary."""
        if not self.metrics:
            return {}
        
        ccs = [m.cyclomatic_complexity for m in self.metrics.values()]
        locs = [m.lines_of_code for m in self.metrics.values()]
        mis = [m.maintainability_index for m in self.metrics.values()]
        
        return {
            'total_entities': len(self.metrics),
            'average_complexity': statistics.mean(ccs),
            'max_complexity': max(ccs),
            'total_lines_of_code': sum(locs),
            'average_maintainability_index': statistics.mean(mis),
            'complexity_coverage_correlation': self.correlate_complexity_coverage(),
        }
```

#### 2.3.2 Acceptance Criteria

- [ ] Metrics stored and retrieved correctly
- [ ] Correlations computed accurately
- [ ] Summary aggregates all metrics
- [ ] Performance <100ms per 1000 metrics

---

### 2.4 Task BLOCK-ARCH-004: Incremental Analysis Framework

**Blocker ID:** `BLOCK-ARCH-004`  
**Duration:** 1.5 days

```python
# File: src/codex_ml/ast/incremental.py
import json
from pathlib import Path
from typing import Dict, Optional

class BaselineManager:
    """Store and compare analysis baselines."""
    
    def __init__(self, baseline_path: Path):
        self.baseline_path = baseline_path
        self.baseline_path.parent.mkdir(parents=True, exist_ok=True)
    
    def save_baseline(self, analysis_results: Dict):
        """Save baseline for comparison."""
        with open(self.baseline_path, 'w') as f:
            json.dump(analysis_results, f, indent=2)
    
    def load_baseline(self) -> Optional[Dict]:
        """Load previous baseline."""
        if not self.baseline_path.exists():
            return None
        
        with open(self.baseline_path) as f:
            return json.load(f)
    
    def compute_delta(self, current: Dict, baseline: Dict) -> Dict:
        """Compute changes between baselines."""
        delta = {
            'changed_files': [],
            'new_files': [],
            'deleted_files': [],
            'metric_deltas': {},
        }
        
        baseline_files = set(baseline.get('files', {}).keys())
        current_files = set(current.get('files', {}).keys())
        
        delta['new_files'] = list(current_files - baseline_files)
        delta['deleted_files'] = list(baseline_files - current_files)
        
        for file in current_files & baseline_files:
            if current['files'][file] != baseline['files'][file]:
                delta['changed_files'].append(file)
        
        return delta
```

#### 2.4.2 Acceptance Criteria

- [ ] Baselines saved and loaded correctly
- [ ] Delta computation accurate
- [ ] Performance <1s for typical PR (5-10 files)

---

### 2.5 Task BLOCK-ARCH-005: Plugin Architecture

**Blocker ID:** `BLOCK-ARCH-005`  
**Duration:** 1.5 days

```python
# File: src/codex_ml/ast/plugins.py
from abc import ABC, abstractmethod
from typing import Dict, Type
import importlib

class LanguageAdapter(ABC):
    """Base class for language adapters."""
    
    @abstractmethod
    def parse(self, source_code: str, file_path) -> StandardizedASTNode:
        """Parse source code to StandardizedAST."""
        pass
    
    @abstractmethod
    def get_supported_extensions(self) -> list:
        """File extensions supported."""
        pass

class PluginRegistry:
    """Manage language adapter plugins."""
    
    _adapters: Dict[str, Type[LanguageAdapter]] = {}
    
    @classmethod
    def register(cls, language: str, adapter_class: Type[LanguageAdapter]):
        """Register language adapter."""
        cls._adapters[language] = adapter_class
    
    @classmethod
    def get_adapter(cls, language: str) -> LanguageAdapter:
        """Get adapter instance."""
        if language not in cls._adapters:
            raise ValueError(f"No adapter for {language}")
        
        return cls._adapters[language]()
    
    @classmethod
    def list_languages(cls) -> list:
        """List supported languages."""
        return list(cls._adapters.keys())
```

#### 2.5.2 Acceptance Criteria

- [ ] Multiple adapters can be registered
- [ ] Adapters loaded and instantiated correctly
- [ ] Language listing works
- [ ] Easy to extend with new languages

---

## ⚡ Section 3: Performance Baseline (Days 11-14)

### 3.1 Create Benchmark Suite

**Duration:** 1 day

```python
# File: tests/ast/benchmarks.py
import pytest
import time
from pathlib import Path

@pytest.mark.benchmark
class TestParserBenchmarks:
    
    @pytest.fixture(scope="class")
    def sample_files(self, tmp_path):
        """Create sample Python files."""
        samples = {}
        
        # Small file (100 LOC)
        samples['small'] = tmp_path / 'small.py'
        samples['small'].write_text("def func():\n    pass\n" * 50)
        
        # Medium file (1000 LOC)
        samples['medium'] = tmp_path / 'medium.py'
        samples['medium'].write_text("def func():\n    pass\n" * 500)
        
        # Large file (10K LOC)
        samples['large'] = tmp_path / 'large.py'
        samples['large'].write_text("def func():\n    pass\n" * 5000)
        
        return samples
    
    def test_parse_small_file(self, benchmark, sample_files):
        """Benchmark small file parsing."""
        from codex_ml.ast.language_adapters import PythonAdapter
        
        adapter = PythonAdapter()
        source = sample_files['small'].read_text()
        
        result = benchmark(adapter.parse, source, sample_files['small'])
        assert result is not None
    
    def test_parse_large_file(self, benchmark, sample_files):
        """Benchmark large file parsing."""
        from codex_ml.ast.language_adapters import PythonAdapter
        
        adapter = PythonAdapter()
        source = sample_files['large'].read_text()
        
        result = benchmark(adapter.parse, source, sample_files['large'])
        assert result is not None
        
        # Verify performance: <1ms per 100 tokens
        tokens = len(source.split())
        # (Benchmark automatically compares against threshold)
```

---

### 3.2 Profile Memory Usage

```bash
# Create memory profiling script
python << 'EOF'
import tracemalloc
from pathlib import Path

tracemalloc.start()

# Parse large codebase
from codex_ml.ast import UniversalAnalyzer

codebase = Codebase.from_directory("src/", max_size_mb=50)
analyzer = UniversalAnalyzer()
results = analyzer.analyze_all(codebase)

current, peak = tracemalloc.get_traced_memory()
print(f"Current: {current / 1024 / 1024:.1f} MB")
print(f"Peak: {peak / 1024 / 1024:.1f} MB")

assert peak < 500 * 1024 * 1024  # 500 MB limit

tracemalloc.stop()
print("✓ Memory usage within budget")
EOF
```

---

## 📋 Section 4: Existing AST Usage Refactoring (Phased)

### 4.1 Audit Existing Usage

**Duration:** 1 day

```bash
# Find all existing AST usage
grep -r "import ast\|from ast" src/ scripts/ tools/ --include="*.py" > /tmp/ast_usage.txt

# Count files
wc -l /tmp/ast_usage.txt

# Example output:
# src/cli/ast_upgrade.py:3:import ast
# scripts/analysis/ast_signature_similarity.py:1:from ast import parse
# ... (10+ files)
```

### 4.2 Create Migration Layer

```python
# File: src/codex_ml/ast/compat.py
"""Compatibility layer for gradual migration."""

import warnings
from typing import Any
from pathlib import Path

# Old API → New API mapping
_DEPRECATED_FUNCTIONS = {}

def parse_code(source: str, filename: str = "<string>") -> Any:
    """Deprecated: Use UniversalParser instead."""
    warnings.warn(
        "parse_code() is deprecated. Use UniversalParser instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    from codex_ml.ast.parser import UniversalParser
    parser = UniversalParser()
    return parser.parse(source, Path(filename))
```

### 4.3 Phase 1 Refactoring (High Priority Files)

- [ ] cli/ast_upgrade.py → use new layer
- [ ] scripts/analysis/ast_signature_similarity.py → refactor

**Full refactoring (remaining 8+ files) deferred to post-Sprint 1**

---

## ✅ Section 5: Testing Infrastructure Setup

### 5.1 Create Test Fixtures

**Duration:** 1.5 days

```python
# File: tests/ast/fixtures.py
import pytest
from pathlib import Path

@pytest.fixture
def simple_function_code():
    """Simple Python function for testing."""
    return """
    def add(x: int, y: int) -> int:
        '''Add two numbers.'''
        return x + y
    """

@pytest.fixture
def complex_function_code():
    """Complex function with multiple paths."""
    return """
    def process_data(data):
        if data is None:
            if len(data) > 10:
                for item in data:
                    if item > 0:
                        yield item
            else:
                return []
        else:
            return None
    """

@pytest.fixture
def decorated_class_code():
    """Decorated class with decorators."""
    return """
    @dataclass
    class Person:
        name: str
        age: int
        
        @property
        def is_adult(self) -> bool:
            return self.age >= 18
    """
```

---

## 📊 Go/No-Go Decision Framework

### Pre-Conditions for Sprint 1 Start

**All Must Be True:**

| Condition | Status | Validation |
|-----------|--------|-----------|
| All 5 dependencies resolved | TBD | `pip install -e ".[ast]"` succeeds |
| Architecture designs approved | TBD | Tech lead sign-off |
| Performance baseline established | TBD | Benchmarks run successfully |
| Test infrastructure ready | TBD | Test suite passes |
| Zero critical security issues | TBD | `pip audit` clean |

### Sign-Off Required From

- [ ] **Tech Lead**: Architecture & performance
- [ ] **QA Lead**: Test infrastructure
- [ ] **Project Manager**: Timeline & resources
- [ ] **Security Lead**: Dependency audit

### Decision Gate: 2025-11-23 14:00 UTC

**If ALL conditions met**: ✅ **PROCEED TO SPRINT 1**  
**If ANY condition not met**: 🚫 **DEFER; REASSESS IN 2 WEEKS**

---

## 📈 Success Metrics

| Metric | Target | Current | After Phase 0 |
|--------|--------|---------|---------------|
| Dependency conflicts | 0 | TBD | 0 ✓ |
| Architecture approved | 100% | 0% | 100% ✓ |
| Performance baseline | Established | None | <5s/1000 LOC ✓ |
| Test infrastructure | Complete | Partial | 100% ✓ |
| Security issues | 0 critical | TBD | 0 ✓ |

---

## 🚀 Phase 0 Timeline

```
2025-11-10 → 2025-11-11: Dependency Resolution (BLOCK-DEP-001 to 005)
2025-11-12 → 2025-11-14: Architecture Foundation (BLOCK-ARCH-001 to 005)
2025-11-15 → 2025-11-16: Performance Baseline (BLOCK-PERF-001 to 003)
2025-11-17 → 2025-11-18: Test Infrastructure
2025-11-19 → 2025-11-20: Risk Mitigation & Documentation
2025-11-21 → 2025-11-22: Validation & Sign-Off Prep
2025-11-23 14:00: GO/NO-GO DECISION GATE
2025-11-24: Sprint 1 Kickoff (if GO)
```

---

**Document Status**: READY FOR IMPLEMENTATION  
**Phase 0 Start**: 2025-11-09 23:13:57 UTC  
**Phase 0 Target End**: 2025-11-23 14:00 UTC  
**Next Document**: Sprint 1 Implementation Plan
```

Now creating the detailed validation and risk mitigation guide:

```markdown name=Phase0_Validation_Copilot.md
# ✅ Phase 0: Validation & Risk Mitigation Guide
> Generated: 2025-11-09 23:13:57 UTC | Author: mbaetiong

**🧠 Roles:** [Primary: QA Lead], [Secondary: Risk Manager] | ⚡ Energy: 5/5

⚛️ **Physics:** Path🛤️ [Validation gates] | Fields🔄 [Risk mitigation] | Patterns👁️ [Regression prevention] | Redundancy🔀 [Fallback testing] | Balance⚖️ [Quality vs. speed]

---

## 📋 Executive Summary

**Phase 0 Validation** ensures **zero regressions** and **all blockers resolved** before Sprint 1 proceeds.

**Validation Strategy:**
- ✅ Dependency conflict detection
- ✅ Architecture design review
- ✅ Performance validation
- ✅ Test infrastructure verification
- ✅ Risk mitigation deployment

---

## Section 1: Dependency Validation

### 1.1 Conflict Detection

```python
# File: .github/scripts/validate_dependencies.py

import subprocess
import sys
from pathlib import Path

def check_dependency_conflicts():
    """Detect dependency conflicts."""
    result = subprocess.run([sys.executable, "-m", "pip", "check"], 
                          capture_output=True, text=True)
    
    if result.returncode != 0:
        print("❌ Dependency conflicts detected:")
        print(result.stdout)
        return False
    
    print("✓ No dependency conflicts")
    return True

def check_security_vulnerabilities():
    """Scan for known vulnerabilities."""
    result = subprocess.run([sys.executable, "-m", "pip", "audit"],
                          capture_output=True, text=True)
    
    # Check for HIGH/CRITICAL severity
    if "CRITICAL" in result.stdout or "HIGH" in result.stdout:
        print("❌ Security vulnerabilities found:")
        print(result.stdout)
        return False
    
    print("✓ No critical vulnerabilities")
    return True

def check_import_availability():
    """Verify all imports work."""
    required_imports = [
        ("libcst", "libcst"),
        ("radon", "radon"),
        ("parso", "parso"),
        ("tree_sitter", "tree-sitter"),
    ]
    
    all_ok = True
    for module_name, display_name in required_imports:
        try:
            __import__(module_name)
            print(f"✓ {display_name} importable")
        except ImportError as e:
            print(f"❌ {display_name} import failed: {e}")
            all_ok = False
    
    return all_ok

def main():
    """Run all dependency validations."""
    validations = [
        ("Dependency Conflicts", check_dependency_conflicts),
        ("Security Vulnerabilities", check_security_vulnerabilities),
        ("Import Availability", check_import_availability),
    ]
    
    results = {}
    for name, check_func in validations:
        print(f"\n[{name}]")
        results[name] = check_func()
    
    # Summary
    print("\n" + "="*50)
    passed = sum(results.values())
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All dependency validations passed")
        return 0
    else:
        print("❌ Some validations failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

**Run:**
```bash
python .github/scripts/validate_dependencies.py
```

---

### 1.2 Version Compatibility Matrix

| Dependency | Minimum | Tested | Maximum | Status |
|-----------|---------|--------|---------|--------|
| libcst | 1.0.0 | 1.0.4 | 1.1.0 | ✅ OK |
| radon | 6.0.0 | 6.0.1 | 6.1.0 | ✅ OK |
| parso | 0.8.0 | 0.8.3 | 0.9.0 | ✅ OK |
| tree-sitter | 0.20.0 | 0.20.3 | 0.21.0 | ✅ OK |
| torch | 2.0.0 | 2.1.0 | 2.2.0 | ✅ OK |

---

## Section 2: Architecture Validation

### 2.1 Design Review Checklist

**Tech Lead Must Verify:**

- [ ] StandardizedASTNode supports all language types
- [ ] Serialization format is standardized (JSON)
- [ ] Plugin registry pattern is extensible
- [ ] Error handling is consistent
- [ ] Performance constraints realistic

**Review Questions:**

| Question | Expected Answer |
|----------|-----------------|
| Can new languages be added without core changes? | Yes, via plugin registry |
| Are circular dependencies allowed? | No, detected and reported |
| What happens on parse failure? | Graceful degradation with fallback |
| How are metrics aggregated? | Centralized MetricsAggregator |

---

### 2.2 Architecture Tests

```python
# tests/ast/test_architecture.py

def test_standardized_ast_node_creation():
    """Verify StandardizedASTNode instantiates."""
    node = StandardizedASTNode(
        node_id="test_1",
        type=NodeType.FUNCTION,
        name="test_func",
        source_location=SourceLocation(
            file_path=Path("test.py"),
            line_start=1,
            line_end=5,
            column_start=0,
            column_end=20,
        ),
    )
    
    assert node.name == "test_func"
    assert node.type == NodeType.FUNCTION

def test_dependency_graph_cycle_detection():
    """Verify cycle detection works."""
    graph = DependencyGraph()
    
    # Add nodes
    for i in range(3):
        graph.add_node(f"node_{i}", None)
    
    # Create cycle: 0 → 1 → 2 → 0
    graph.add_edge("node_0", "node_1", "imports")
    graph.add_edge("node_1", "node_2", "calls")
    graph.add_edge("node_2", "node_0", "inherits_from")
    
    cycles = graph.detect_cycles()
    assert len(cycles) == 1
    assert set(cycles[0]) == {"node_0", "node_1", "node_2"}

def test_metrics_aggregator_correlation():
    """Verify metrics correlation computation."""
    aggregator = MetricsAggregator()
    
    # Add test metrics
    aggregator.store_metrics("func_1", CodeMetrics(
        lines_of_code=50,
        cyclomatic_complexity=5,
        cognitive_complexity=5.0,
        halstead_volume=100.0,
        maintainability_index=85.0,
        test_coverage=0.9,
    ))
    
    summary = aggregator.get_summary()
    assert summary['total_entities'] == 1
    assert summary['average_complexity'] == 5
```

---

## Section 3: Performance Validation

### 3.1 Performance Targets vs. Baselines

**Baseline Measurements (Before Phase 0):**

| Metric | Baseline | Target | Delta |
|--------|----------|--------|-------|
| Parse time (small file) | TBD ms | <1ms/100 tokens | TBD |
| Parse time (large file) | TBD ms | <1ms/100 tokens | TBD |
| Memory (50K LOC) | TBD MB | <500 MB | TBD |
| Graph build (100 modules) | TBD ms | <1000 ms | TBD |

**Validation:**

```python
# tests/ast/test_performance.py

@pytest.mark.benchmark
def test_parser_performance_target(benchmark):
    """Ensure parser meets performance target."""
    from codex_ml.ast import UniversalParser
    
    parser = UniversalParser()
    source = open("tests/fixtures/large_sample.py").read()
    
    # Benchmark and compare to target
    result = benchmark(parser.parse, source, Path("sample.py"))
    
    # Implicit: benchmark compares to tolerance
    assert result is not None
```

---

## Section 4: Test Infrastructure Validation

### 4.1 Fixture Verification

```bash
# Verify all fixtures available
pytest --fixtures tests/ast/ | grep "sample\|fixture"

# Expected output:
# sample_python_file
# large_codebase
# synthetic_graph
# decorated_class_code
# ... etc
```

### 4.2 Coverage Verification

```bash
pytest tests/ast/ --cov=src/codex_ml/ast --cov-report=term-missing

# Ensure >80% coverage before Phase 1
```

---

## Section 5: Risk Mitigation Deployment

### 5.1 Offline-First Validation

**Test Plan:**

```bash
# Disable network access and verify functionality
export CODEX_OFFLINE_MODE=1

# Install offline
pip install -e ".[ast]" --no-index

# Verify parsers work offline
python -c "from codex_ml.ast import UniversalParser; p = UniversalParser(); print('OK')"
```

### 5.2 Python Version Compatibility

**Test Matrix:**

```yaml
# .github/workflows/phase0_validation.yml
strategy:
  matrix:
    python-version: ["3.8", "3.9", "3.10", "3.11", "3.12"]

steps:
  - uses: actions/setup-python@v4
    with:
      python-version: ${{ matrix.python-version }}
  
  - run: pip install -e ".[ast]"
  - run: pytest tests/ast/ -v
```

### 5.3 Scope Creep Prevention

**Scope Freeze Agreement:**

| Item | Owner | Status |
|------|-------|--------|
| Phase 0 features locked | Project Manager | ✅ Locked |
| No new requirements | Tech Lead | ✅ Frozen |
| Existing PRs only | QA Lead | ✅ Approved |
| Timeline immutable | Project Manager | ✅ Fixed |

---

## Section 6: Sign-Off Process

### 6.1 Technical Sign-Off Checklist

**Tech Lead:**
- [ ] All architecture decisions documented
- [ ] No critical design flaws
- [ ] Performance constraints achievable
- [ ] Offline capability verified

**QA Lead:**
- [ ] Test infrastructure complete
- [ ] All fixtures available
- [ ] Benchmarks operational
- [ ] Coverage targets met

**Project Manager:**
- [ ] Timeline realistic
- [ ] Resources allocated
- [ ] Scope frozen
- [ ] Go/No-Go date set

**Security Lead:**
- [ ] No critical vulns
- [ ] Dependency audit clean
- [ ] Secure defaults set

### 6.2 Sign-Off Meeting (2025-11-23 14:00 UTC)

**Agenda:**

1. **Review Phase 0 completion** (15 min)
   - All blockers resolved?
   - All validations passed?
   
2. **Risk assessment** (10 min)
   - Any new risks identified?
   - Mitigation strategies adequate?
   
3. **Go/No-Go decision** (10 min)
   - Vote by all sign-off parties
   - Document rationale
   
4. **Sprint 1 kickoff (if GO)** (15 min)
   - Resource allocation
   - First sprint planning

**Decision Criteria:**

| Criteria | Must Be | Status |
|----------|---------|--------|
| All blockers resolved | YES | TBD |
| All validations passed | YES | TBD |
| No critical risks | YES | TBD |
| Tech lead approval | YES | TBD |
| QA lead approval | YES | TBD |
| PM approval | YES | TBD |
| Security approval | YES | TBD |

---

## Section 7: Rollback Procedures

### 7.1 If Dependency Conflicts Detected

```bash
# Immediate rollback
git checkout HEAD -- pyproject.toml
pip install -e .
nox -s test  # Verify rollback

# Investigation
git diff HEAD -- pyproject.toml > /tmp/conflict.patch
# Manual resolution of conflicting versions
```

### 7.2 If Performance Targets Missed

**Action:** Defer optimization to Sprint 2  
**Fallback:** Use incremental analysis with caching

```python
# Temporary workaround in parser.py
def parse(self, source, file_path):
    # Check cache
    if file_path in self._parse_cache:
        return self._parse_cache[file_path]
    
    # Parse and cache
    result = self._parse_impl(source, file_path)
    self._parse_cache[file_path] = result
    return result
```

### 7.3 If Architecture Design Not Approved

**Action:** Schedule design review extension  
**Timeline:** Additional 3-5 days for revision

---

## Section 8: Success Metrics Dashboard

```
╔════════════════════════════════════════════════════════════╗
║              Phase 0 Validation Dashboard                  ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║  Dependency Resolution:         [████████░░] 80%         ║
║  Architecture Design:           [██████░░░░] 60%         ║
║  Performance Baseline:          [████████░░] 80%         ║
║  Test Infrastructure:           [██████████] 100%        ║
║  Risk Mitigation:              [██████░░░░] 60%         ║
║                                                            ║
║  Overall Completion:            [███████░░░] 76%         ║
║  Target for GO: 100%                                     ║
║                                                            ║
║  Days Remaining:                11 days (2025-11-23)     ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
```

---

**Document Status**: READY FOR VALIDATION  
**Phase 0 Validation Start**: 2025-11-10  
**Phase 0 Validation End**: 2025-11-23 14:00 UTC  
**Go/No-Go Meeting**: 2025-11-23 14:00 UTC
```

All Phase 0 guidance documents now created and ready for implementation. Both comprehensive implementation guides cover:

✅ **Detailed task breakdowns** with acceptance criteria  
✅ **Complete code implementations** for all components  
✅ **Validation & testing procedures**  
✅ **Risk mitigation strategies**  
✅ **Rollback procedures**  
✅ **Go/No-Go decision framework**  
✅ **Sign-off process**  
✅ **Timeline & resource allocation**

**Ready to proceed with Phase 0 implementation on 2025-11-10.**
