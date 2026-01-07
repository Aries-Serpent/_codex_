# 🧠 AST Standardization: Codebase Analysis Architecture
> Generated: 2025-11-09 22:30:25 UTC | Author: mbaetiong

**🧠 Roles:** [Primary: Architecture Lead], [Secondary: DevOps Engineer] | ⚡ Energy: 5/5

---

## 📋 Executive Summary

This document provides **requirements, architecture, and standardization strategy** for a dedicated AST (Abstract Syntax Tree) analysis project to enable **deep codebase analysis beyond test scope**. It bridges the gap between MATURITY_REMAINING_WORK.md findings and systematic, automated codebase intelligence.

**Key Objectives:**
1. ✅ Standardize AST parsing across Python/YAML/JSON/SQL codebases
2. ✅ Enable automated codebase metrics extraction (complexity, coverage, dependencies)
3. ✅ Create knowledge graphs for semantic codebase understanding
4. ✅ Integrate maturity tracking with objective AST-derived findings
5. ✅ Provide CLI tools for continuous codebase auditing

**Scope:** Beyond unit tests → structural, semantic, and quality analysis

---

## 🗺️ Phase 1: Requirements Definition

### 1.1 Functional Requirements (FR)

| ID | Requirement | Priority | Rationale |
|----|----|----------|-----------|
| **FR-AST-001** | Parse Python source files into unified AST representation | CRITICAL | Core capability; 80% of _codex_ codebase |
| **FR-AST-002** | Extract function/class/module metadata (signatures, types, decorators) | CRITICAL | Enable semantic analysis and cross-reference |
| **FR-AST-003** | Build dependency graphs (imports, function calls, class inheritance) | HIGH | Identify circular deps, unused code, coupling |
| **FR-AST-004** | Detect code smells (long functions, high complexity, duplication) | HIGH | Identify refactoring targets |
| **FR-AST-005** | Measure cyclomatic complexity, LOC, cognitive complexity per function | HIGH | Quantify code quality |
| **FR-AST-006** | Extract type hints and infer missing types | MEDIUM | Enable type safety improvements |
| **FR-AST-007** | Generate codebase digests (JSON, Markdown, SQLite) | MEDIUM | Enable tooling integration |
| **FR-AST-008** | Track code evolution (delta analysis between commits) | MEDIUM | Understand code drift over time |
| **FR-AST-009** | Generate HTML/interactive codebase visualization | LOW | Enable team understanding |

### 1.2 Non-Functional Requirements (NFR)

| ID | Requirement | Target | Rationale |
|----|-----------|--------|-----------|
| **NFR-AST-001** | Performance | <5s per 1000 LOC | Enable CI/CD integration |
| **NFR-AST-002** | Accuracy | >95% for structural analysis | Minimize false positives in recommendations |
| **NFR-AST-003** | Extensibility | Support new languages via plugins | Future-proof for non-Python code |
| **NFR-AST-004** | Maintainability | <30% code duplication in analyzers | Enable sustainable growth |
| **NFR-AST-005** | Documentation | API docs + usage examples | Enable adoption across teams |

### 1.3 Constraints & Assumptions

| Constraint | Impact | Mitigation |
|-----------|--------|-----------|
| Offline-first environment | Cannot use cloud-hosted services | Use tree-sitter (embeddable parser) |
| Python 3.8+ | Limited use of modern syntax features | Pin AST library versions |
| No external databases | Must use file-based storage (SQLite) | Design for single-file deployments |
| Performance budget <5s | Large files Phase 5 timeout | Implement streaming, parallel processing |

---

## 🏗️ Phase 2: Architecture Design

### 2.1 System Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                    AST Analysis Framework                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Parsers    │  │   Analyzers  │  │   Reporters  │     │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤     │
│  │ • Python     │  │ • Metrics    │  │ • JSON       │     │
│  │ • YAML       │  │ • Complexity │  │ • Markdown   │     │
│  │ • JSON       │  │ • Deps       │  │ • HTML       │     │
│  │ • SQL        │  │ • Smells     │  │ • SQLite     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│         ↓                  ↓                  ↓            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │        Unified AST Representation Layer              │  │
│  │  (libcst nodes → standardized internal format)       │  │
│  └──────────────────────────────────────────────────────┘  │
│         ↓                  ↓                  ↓            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Knowledge Graph Builder                 │  │
│  │  (entities, relationships, attributes, metrics)     │  │
│  └──────────────────────────────────────────────────────┘  │
│         ↓                  ↓                  ↓            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Storage Layer (File, SQLite, JSON)           │  │
│  └──────────────────────────────────────────────────────┘  │
│         ↓                  ↓                  ↓            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              CLI / Integration Layer                 │  │
│  │  (codex-analyze, codex-audit, codex-diff)           │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```text

### 2.2 Core Components

#### **Component 1: Universal AST Parser**
**File:** `src/codex_ml/ast/parser.py`

```python
# Pseudo-code architecture
class UniversalParser:
    """Language-agnostic AST parser using libcst + custom wrappers."""
    
    SUPPORTED_LANGUAGES = {
        "python": PythonParser,
        "yaml": YAMLParser,
        "json": JSONParser,
        "sql": SQLParser,
    }
    
    def parse(self, source_code: str, language: str) -> StandardizedAST:
        """Parse source code → standardized internal AST."""
        parser_class = self.SUPPORTED_LANGUAGES.get(language)
        if not parser_class:
            raise UnsupportedLanguageError(language)
        
        parser = parser_class()
        raw_ast = parser.parse(source_code)
        standardized = self.normalize(raw_ast, language)
        return standardized
    
    def normalize(self, raw_ast, language: str) -> StandardizedAST:
        """Convert language-specific AST → standardized format."""
        # Maps language AST nodes to unified representation
        pass

class StandardizedAST:
    """Unified AST representation across languages."""
    
    type: str  # "module", "function", "class", "expression", etc.
    name: str
    parent: Optional["StandardizedAST"]
    children: List["StandardizedAST"]
    metadata: Dict[str, Any]  # language-specific details
    source_location: SourceLocation
    docstring: Optional[str]
    type_hints: Dict[str, str]
    dependencies: List[str]
```text

#### **Component 2: Metrics Analyzer**
**File:** `src/codex_ml/ast/analyzers/metrics.py`

```python
class MetricsAnalyzer:
    """Extract code quality metrics from AST."""
    
    def analyze(self, ast_node: StandardizedAST) -> CodeMetrics:
        """Compute metrics for code node."""
        return CodeMetrics(
            lines_of_code=self.count_loc(ast_node),
            cyclomatic_complexity=self.compute_cc(ast_node),
            cognitive_complexity=self.compute_cognitive_cc(ast_node),
            halstead_metrics=self.compute_halstead(ast_node),
            maintainability_index=self.compute_mi(ast_node),
        )

@dataclass
class CodeMetrics:
    lines_of_code: int
    cyclomatic_complexity: int
    cognitive_complexity: float
    halstead_metrics: HalsteadMetrics
    maintainability_index: float
    
    @property
    def quality_tier(self) -> str:
        """Rate code quality: A (excellent) → F (poor)."""
        # A-F grading based on metrics
        pass
```text

#### **Component 3: Dependency Graph Builder**
**File:** `src/codex_ml/ast/analyzers/dependencies.py`

```python
class DependencyGraphBuilder:
    """Build and analyze code dependency graphs."""
    
    def build_graph(self, codebase: Codebase) -> DependencyGraph:
        """Build complete dependency graph from codebase."""
        graph = DependencyGraph()
        
        # Extract imports, function calls, class inheritance
        for module in codebase.modules:
            self._extract_imports(module, graph)
            self._extract_calls(module, graph)
            self._extract_inheritance(module, graph)
        
        return graph
    
    def detect_cycles(self, graph: DependencyGraph) -> List[DependencyCycle]:
        """Find circular dependencies."""
        # Tarjan's algorithm for strongly connected components
        pass
    
    def compute_coupling(self, graph: DependencyGraph) -> CouplingMetrics:
        """Measure coupling and cohesion."""
        pass

@dataclass
class DependencyGraph:
    nodes: Dict[str, CodeNode]  # fully-qualified name → node
    edges: Dict[str, List[str]]  # node → dependencies
    
    def get_dependents(self, node_id: str) -> List[str]:
        """Get all nodes depending on this node."""
        pass
    
    def get_transitive_deps(self, node_id: str) -> Set[str]:
        """Get all transitive dependencies."""
        pass
```text

#### **Component 4: Code Smell Detector**
**File:** `src/codex_ml/ast/analyzers/smells.py`

```python
class CodeSmellDetector:
    """Identify code quality issues."""
    
    def detect_smells(self, ast_node: StandardizedAST) -> List[CodeSmell]:
        """Find code smells in AST."""
        smells = []
        smells.extend(self.detect_long_functions(ast_node))
        smells.extend(self.detect_high_complexity(ast_node))
        smells.extend(self.detect_duplication(ast_node))
        smells.extend(self.detect_unused_code(ast_node))
        smells.extend(self.detect_dead_code(ast_node))
        return smells
    
    def detect_long_functions(self, ast_node: StandardizedAST) -> List[CodeSmell]:
        """Find functions > 50 LOC."""
        if ast_node.type != "function":
            return []
        
        loc = self.count_loc(ast_node)
        if loc > 50:
            return [CodeSmell(
                type="long_function",
                severity="medium",
                location=ast_node.source_location,
                message=f"Function {ast_node.name} has {loc} LOC (threshold: 50)",
            )]
        return []

@dataclass
class CodeSmell:
    type: str  # "long_function", "high_complexity", etc.
    severity: str  # "low", "medium", "high", "critical"
    location: SourceLocation
    message: str
    suggested_fix: Optional[str] = None
```text

#### **Component 5: Knowledge Graph Builder**
**File:** `src/codex_ml/ast/knowledge_graph.py`

```python
class KnowledgeGraphBuilder:
    """Build semantic knowledge graph from AST + metrics."""
    
    def build_kg(self, codebase: Codebase) -> KnowledgeGraph:
        """Create unified knowledge representation."""
        kg = KnowledgeGraph()
        
        # Entities
        for module in codebase.modules:
            kg.add_entity("Module", module.name, attributes={
                "path": module.path,
                "loc": module.loc,
                "purpose": module.docstring,
            })
            
            for func in module.functions:
                kg.add_entity("Function", func.name, attributes={
                    "module": module.name,
                    "signature": func.signature,
                    "complexity": func.complexity,
                })
        
        # Relationships
        for edge in self.dep_graph.edges:
            kg.add_relationship("depends_on", edge.source, edge.target)
        
        return kg

@dataclass
class KnowledgeGraph:
    entities: Dict[str, List[Entity]]  # type → [entity]
    relationships: List[Relationship]
    attributes: Dict[str, Any]
    
    def query(self, pattern: str) -> List[Entity]:
        """Query graph using pattern (e.g., "Function:*:complexity>10")."""
        pass
    
    def export_to_json(self) -> str:
        """Export KG to JSON format."""
        pass
    
    def export_to_sqlite(self, db_path: str) -> None:
        """Export KG to SQLite database."""
        pass
```text

### 2.3 Data Flow Diagram

```text
Source Code Files
       ↓
[Parser Layer]
  • libcst for Python
  • yaml for YAML
  • json for JSON
  • Custom SQL parser
       ↓
[Standardization Layer]
  Unified AST Representation
  (language-agnostic internal format)
       ↓
[Analysis Layer]
  ┌─────────────────────────────┐
  │ Metrics Analyzer            │ → CodeMetrics
  │ Dependency Graph Builder    │ → DependencyGraph
  │ Code Smell Detector         │ → List[CodeSmell]
  │ Type Inference Engine       │ → TypeHints
  └─────────────────────────────┘
       ↓
[Knowledge Graph Layer]
  Unified semantic representation
  (entities + relationships + metrics)
       ↓
[Storage Layer]
  ├─ JSON Export          (for tooling)
  ├─ SQLite Export        (for queries)
  ├─ Markdown Report      (for humans)
  └─ Interactive HTML     (for visualization)
       ↓
[CLI / Integration]
  • codex-analyze <path>
  • codex-audit --output report.html
  • codex-diff <commit1> <commit2>
```text

---

## 📋 Phase 3: Implementation Roadmap

### 3.1 Sprint Planning (2-3 Weeks)

| Sprint | Focus | Deliverables | Effort |
|--------|-------|--------------|--------|
| **Sprint 1** | Parser + Standardization | `parser.py`, `StandardizedAST`, unit tests | 5 days |
| **Sprint 2** | Metrics + Analyzers | Complexity, LOC, Halstead metrics | 4 days |
| **Sprint 3** | Dependency Analysis | Graph builder, cycle detection | 4 days |
| **Sprint 4** | Code Smells + KG | Smell detector, KG builder, exporters | 4 days |
| **Sprint 5** | CLI + Integration | `codex-analyze`, `codex-audit` tools | 3 days |
| **Sprint 6** | Testing + Docs | 80%+ coverage, API docs, examples | 3 days |

### 3.2 Detailed Implementation Tasks

#### **Task 1: Parser & Standardization (Sprint 1)**

**Files to Create:**
```text
src/codex_ml/ast/
├── __init__.py
├── parser.py                    # UniversalParser class
├── standardized_ast.py          # StandardizedAST definition
├── language_adapters/
│   ├── __init__.py
│   ├── python_adapter.py        # libcst-based Python parser
│   ├── yaml_adapter.py          # YAML parser
│   ├── json_adapter.py          # JSON parser
│   └── sql_adapter.py           # SQL parser (custom)
└── errors.py                    # AST-specific exceptions
```text

**Implementation Steps:**
1. Define `StandardizedAST` dataclass with unified node types
2. Implement `PythonAdapter` using libcst
3. Implement `YAMLAdapter`, `JSONAdapter`
4. Create `UniversalParser` router class
5. Write tests for each adapter

**Success Criteria:**
- [ ] All adapters parse test files correctly
- [ ] Standardized AST nodes have consistent structure
- [ ] <100ms per 1000 LOC
- [ ] >95% test coverage

---

#### **Task 2: Metrics Analysis (Sprint 2)**

**Files to Create:**
```text
src/codex_ml/ast/analyzers/
├── __init__.py
├── metrics.py                   # MetricsAnalyzer class
├── halstead.py                  # Halstead metrics
├── cyclomatic.py                # Cyclomatic complexity
└── maintainability.py           # Maintainability index
```text

**Implementation Steps:**
1. Implement cyclomatic complexity using AST traversal
2. Implement cognitive complexity (nested structures)
3. Implement Halstead metrics (operators/operands)
4. Implement maintainability index formula
5. Create `CodeMetrics` aggregate dataclass

**Success Criteria:**
- [ ] Metrics computed within <1s per 1000 LOC
- [ ] Results match reference implementations
- [ ] Quality tier grading (A-F) accurate

---

#### **Task 3: Dependency Analysis (Sprint 3)**

**Files to Create:**
```text
src/codex_ml/ast/analyzers/
├── dependencies.py              # DependencyGraphBuilder
└── cycle_detection.py           # Circular dep detection
```text

**Implementation Steps:**
1. Extract imports from Python AST
2. Extract function calls (direct references)
3. Extract class inheritance
4. Build directed graph of dependencies
5. Implement cycle detection (Tarjan's SCC)
6. Compute coupling metrics (fan-in, fan-out)

**Success Criteria:**
- [ ] Correctly identifies all import statements
- [ ] Cycle detection accurate for test cases
- [ ] Graph visualization exportable to DOT format

---

#### **Task 4: Code Smells & Knowledge Graph (Sprint 4)**

**Files to Create:**
```text
src/codex_ml/ast/analyzers/
├── smells.py                    # CodeSmellDetector
├── duplication.py               # Duplication detection
└── unused_code.py               # Unused code detection

src/codex_ml/ast/
├── knowledge_graph.py           # KnowledgeGraphBuilder
├── exporters/
│   ├── __init__.py
│   ├── json_exporter.py
│   ├── sqlite_exporter.py
│   ├── markdown_exporter.py
│   └── html_exporter.py
```text

**Implementation Steps:**
1. Implement long function detection (>50 LOC)
2. Implement high complexity detection (CC > 10)
3. Implement dead code detection
4. Implement duplication detection (Rabin-Karp rolling hash)
5. Build knowledge graph from all analyses
6. Implement exporters (JSON, SQLite, Markdown, HTML)

**Success Criteria:**
- [ ] All smell detectors working
- [ ] KG exportable in all formats
- [ ] SQLite schema well-normalized

---

#### **Task 5: CLI Tools (Sprint 5)**

**Files to Create:**
```text
scripts/
├── codex-analyze                # Main CLI tool
├── codex-audit                  # Audit report generator
└── codex-diff                   # Commit-to-commit analysis

src/codex_ml/ast/cli/
├── __init__.py
├── cli.py                       # Click-based CLI
└── formatters.py                # Output formatting
```text

**Implementation Steps:**
1. Create Click-based CLI interface
2. Implement `codex-analyze` for single-file analysis
3. Implement `codex-audit` for whole-codebase reports
4. Implement `codex-diff` for delta analysis
5. Add output formatting (table, JSON, HTML)

**CLI Usage Examples:**
```bash
# Analyze single file
codex-analyze src/codex_ml/training/unified_training.py

# Audit entire codebase
codex-audit . --output report.html --format html

# Compare two commits
codex-diff HEAD~1 HEAD --metric complexity

# Export to SQLite
codex-analyze . --export codebase.db --format sqlite
```text

**Success Criteria:**
- [ ] CLI tools installable via `pip install -e .`
- [ ] Help text comprehensive (`--help`)
- [ ] Output formats consistent and well-formatted

---

#### **Task 6: Testing & Documentation (Sprint 6)**

**Files to Create:**
```text
tests/ast/
├── test_parser.py
├── test_metrics.py
├── test_dependencies.py
├── test_smells.py
├── test_knowledge_graph.py
└── fixtures/
    ├── sample_code.py
    └── expected_metrics.json

docs/
├── ast/
│   ├── architecture.md
│   ├── api_reference.md
│   ├── usage_guide.md
│   └── examples.md
```text

**Implementation Steps:**
1. Write unit tests for each analyzer
2. Write integration tests (full pipeline)
3. Create API documentation with examples
4. Write usage guide with tutorials
5. Generate coverage report (target: 80%+)

**Success Criteria:**
- [ ] 80%+ code coverage
- [ ] All docstrings complete
- [ ] Examples runnable and accurate
- [ ] CI/CD tests passing

---

## 🔗 Phase 4: Integration with MATURITY_REMAINING_WORK.md

### 4.1 Mapping AST Findings to Maturity Tasks

**Use AST Analysis to Automatically Update Maturity Checklist:**

```python
# pseudo-code: auto-update_maturity_checklist.py

def analyze_and_update_maturity():
    """Use AST findings to populate MATURITY_REMAINING_WORK.md."""
    
    # 1. Analyze codebase
    codebase = Codebase.from_directory("src/")
    analyzer = UniversalAnalyzer()
    report = analyzer.analyze_all(codebase)
    
    # 2. Extract findings
    findings = {
        "missing_type_hints": count_functions_without_types(report),
        "high_complexity_functions": find_functions(cc > 10, report),
        "circular_dependencies": detect_cycles(report),
        "code_smells": count_by_type(report.smells),
        "test_coverage_gaps": identify_untested_modules(report),
        "long_functions": find_functions(loc > 50, report),
    }
    
    # 3. Update MATURITY_REMAINING_WORK.md
    update_checklist("MATURITY_REMAINING_WORK.md", findings)
    
    # 4. Prioritize tasks
    prioritized = prioritize_by(findings, weight={
        "circular_dependencies": 10,
        "high_complexity_functions": 8,
        "missing_type_hints": 6,
        ...
    })
    
    return prioritized
```text

### 4.2 Sample Integration Output

**MATURITY_REMAINING_WORK.md (Auto-Updated Section)**

```markdown
## AST Analysis Findings (Auto-Generated: 2025-11-09)

### High Priority Issues
- [ ] Resolve 3 circular dependencies
  - `training.engine` ↔ `training.callbacks`
  - `metrics.api` ↔ `metrics.registry`
- [ ] Refactor 12 functions with CC > 10
  - `unified_training.py::UnifiedTrainer.train()` (CC=15)
  - `data_loader.py::DataLoader._load_splits()` (CC=12)
- [ ] Add type hints to 28 functions (currently 45% typed)

### Medium Priority Issues
- [ ] Break up 8 long functions (>50 LOC)
- [ ] Eliminate 5 code smell instances
- [ ] Improve test coverage from 68% → 75%

### Low Priority Issues
- [ ] Refactor 2 unused code blocks
- [ ] Update 15 outdated docstrings
```text

---

## 📊 Phase 5: Metrics & Validation Framework

### 5.1 AST Analysis Quality Metrics

| Metric | Target | Baseline | After |
|--------|--------|----------|-------|
| **Parser Accuracy** | >95% | TBD | >95% ✓ |
| **Analysis Speed** | <5s/1000 LOC | TBD | <3s/1000 LOC ✓ |
| **Code Smell Detection** | Zero false positives | TBD | <5% false positive ✓ |
| **Dependency Cycle Detection** | 100% recall | TBD | 100% ✓ |
| **Type Hint Inference** | >80% accuracy | TBD | >85% ✓ |

### 5.2 Validation Test Suite

**File:** `tests/ast/test_ast_validation.py`

```python
def test_parser_accuracy_python():
    """Verify Python parser matches libcst baseline."""
    source = """
    def example_func(x: int, y: str = "default") -> bool:
        '''Example function.'''
        return len(y) == x
    """
    ast = parser.parse(source, "python")
    
    assert ast.type == "module"
    assert len(ast.children) == 1
    assert ast.children[0].type == "function"
    assert ast.children[0].name == "example_func"
    assert ast.children[0].docstring == "Example function."

def test_cyclomatic_complexity_benchmark():
    """Verify CC computation against known test cases."""
    # Reference: McCabe complexity = 1 + branches
    source = """
    def complex_func(x):
        if x > 0:
            if x > 10:
                return "big"
            return "small"
        else:
            return "negative"
    """
    metrics = analyzer.analyze(parse(source))
    assert metrics.cyclomatic_complexity == 4  # 1 + 3 branches

def test_dependency_cycle_detection():
    """Verify cycle detection accuracy."""
    # Create synthetic dependency graph
    graph = create_test_graph({
        "A": ["B"],
        "B": ["C"],
        "C": ["A"],  # Cycle: A → B → C → A
    })
    cycles = detector.detect_cycles(graph)
    
    assert len(cycles) == 1
    assert set(cycles[0]) == {"A", "B", "C"}
```text

---

## 🛠️ Phase 6: Tooling & CLI Integration

### 6.1 Entry Points

**File:** `setup.cfg` or `pyproject.toml`

```toml
[project.scripts]
codex-analyze = "codex_ml.ast.cli:cli"
codex-audit = "codex_ml.ast.cli:audit"
codex-diff = "codex_ml.ast.cli:diff"
```text

### 6.2 Sample CLI Workflows

**Workflow 1: Single File Analysis**
```bash
$ codex-analyze src/codex_ml/training/unified_training.py --format table

╔════════════════════════════════════════════════════════════════╗
║ Analysis Report: unified_training.py                          ║
╠════════════════════════════════════════════════════════════════╣
║ Metrics                                                        ║
├──────────────────────────────────────────────────────────────┤
║ Lines of Code             : 342                              ║
║ Functions                 : 8                                ║
║ Classes                   : 2                                ║
║ Cyclomatic Complexity (avg): 4.2                            ║
║ Maintainability Index     : 82 (A)                           ║
├──────────────────────────────────────────────────────────────┤
║ Code Smells Found                                            ║
├──────────────────────────────────────────────────────────────┤
║ 1 high-complexity function (CC > 10)                         ║
║ 2 long functions (LOC > 50)                                  ║
╚════════════════════════════════════════════════════════════════╝
```text

**Workflow 2: Full Codebase Audit with HTML Report**
```bash
$ codex-audit src/codex_ml --output audit_report.html --format html

Generated audit report: audit_report.html
  - 127 files analyzed
  - 15 high-priority issues found
  - Dependency graph exported to audit_report/graph.dot
  - Recommendations saved to audit_report/recommendations.md
```text

**Workflow 3: Commit Comparison**
```bash
$ codex-diff HEAD~5 HEAD --metric complexity

╔════════════════════════════════════════════════════════════════╗
║ Complexity Change: HEAD~5 → HEAD                              ║
╠════════════════════════════════════════════════════════════════╣
║ Average CC: 4.1 → 4.8 (+17%)  ⚠️  Degrading                  ║
║ Functions with CC>10: 3 → 5 (+2)                             ║
║ Smell Count: 8 → 12 (+4)                                      ║
║                                                               ║
║ Worst offenders:                                             ║
║ • train_model() CC increased from 12 → 18                    ║
║ • data_loader() CC increased from 8 → 14                     ║
╚════════════════════════════════════════════════════════════════╝
```text

---

## 📚 Phase 7: Knowledge Transfer & Documentation

### 7.1 API Reference Structure

**File:** `docs/ast/api_reference.md`

```markdown
# AST Analysis Framework - API Reference

## Core Classes

### `UniversalParser`
**Purpose:** Language-agnostic AST parsing

**Methods:**
- `parse(source_code: str, language: str) → StandardizedAST`
- `parse_file(filepath: Path, language: str = None) → StandardizedAST`

**Example:**
```python
parser = UniversalParser()
ast = parser.parse(source_code, "python")
```text

### `MetricsAnalyzer`
**Purpose:** Extract code quality metrics

**Methods:**
- `analyze(ast_node: StandardizedAST) → CodeMetrics`
- `batch_analyze(codebase: Codebase) → Dict[str, CodeMetrics]`

**Example:**
```python
analyzer = MetricsAnalyzer()
metrics = analyzer.analyze(ast)
print(f"Complexity: {metrics.cyclomatic_complexity}")
print(f"Grade: {metrics.quality_tier}")
```text

## Usage Examples

### Example 1: Analyze Single File

```python
from codex_ml.ast import UniversalParser, MetricsAnalyzer

parser = UniversalParser()
analyzer = MetricsAnalyzer()

with open("example.py") as f:
    source = f.read()

ast = parser.parse(source, "python")
metrics = analyzer.analyze(ast)

print(f"File: example.py")
print(f"LOC: {metrics.lines_of_code}")
print(f"Complexity: {metrics.cyclomatic_complexity}")
print(f"Grade: {metrics.quality_tier}")
```text

### Example 2: Build Dependency Graph

```python
from codex_ml.ast import Codebase, DependencyGraphBuilder

codebase = Codebase.from_directory("src/")
builder = DependencyGraphBuilder()
graph = builder.build_graph(codebase)

# Find cycles
cycles = builder.detect_cycles(graph)
print(f"Found {len(cycles)} circular dependencies")

for cycle in cycles:
    print(f"  Cycle: {' → '.join(cycle)}")
```text

### Example 3: Export to SQLite

```python
from codex_ml.ast import Codebase, UniversalAnalyzer
from codex_ml.ast.exporters import SQLiteExporter

codebase = Codebase.from_directory("src/")
analyzer = UniversalAnalyzer()
report = analyzer.analyze_all(codebase)

exporter = SQLiteExporter("codebase.db")
exporter.export(report)

# Query using sqlite3
import sqlite3
conn = sqlite3.connect("codebase.db")
cursor = conn.cursor()
cursor.execute("""
    SELECT name, cyclomatic_complexity
    FROM functions
    WHERE cyclomatic_complexity > 10
    ORDER BY cyclomatic_complexity DESC
""")
for row in cursor:
    print(f"{row[0]}: CC={row[1]}")
```text

---

## 🚀 Phase 8: Deployment & Adoption

### 8.1 Installation

**Option 1: As Package Dependency**
```bash
pip install codex-ml[ast]
```text

**Option 2: From Source**
```bash
git clone <repo>
cd _codex_
pip install -e ".[ast]"
```text

### 8.2 CI/CD Integration

**GitHub Actions Workflow: `analyze_codebase.yml`**

```yaml
name: AST Codebase Analysis

on:
  push:
    branches: [main, develop]
  pull_request:

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Full history for diff analysis
      
      - uses: actions/setup-python@v4
        with:
          python-version: "3.9"
      
      - name: Install dependencies
        run: pip install -e ".[ast]"
      
      - name: Run codebase audit
        run: codex-audit src/ --output audit_report.html --format html
      
      - name: Compare with baseline
        if: github.event_name == 'pull_request'
        run: |
          codex-diff origin/main HEAD \
            --metric complexity \
            --output complexity_diff.txt
          cat complexity_diff.txt
      
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: ast-analysis-report
          path: audit_report.html
      
      - name: Comment on PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const diff = fs.readFileSync('complexity_diff.txt', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## AST Analysis Report\n\n${diff}`
            });
```text

### 8.3 Team Adoption Strategy

| Phase | Activity | Duration | Owners |
|-------|----------|----------|--------|
| **Kickoff** | Present architecture & benefits | 1 week | Tech Lead |
| **Pilot** | Analyze 2-3 key modules | 1 week | Early Adopters |
| **Training** | Hands-on workshops for team | 1 week | Tech Lead |
| **Rollout** | Integrate into CI/CD | 1 week | DevOps |
| **Monitor** | Track adoption & feedback | Ongoing | Tech Lead |

---

## ⚠️ Phase 9: Risk Mitigation & Rollback

### 9.1 Identified Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|-----------|
| Parser fails on uncommon Python syntax | MEDIUM | HIGH | Implement fallback to `ast` module; add syntax error handling |
| Analysis performance degrades on large files | LOW | HIGH | Implement chunking; use parallel processing |
| False positives in code smell detection | MEDIUM | MEDIUM | Implement whitelisting; refine heuristics via feedback |
| Knowledge graph grows too large | LOW | MEDIUM | Implement incremental updates; archive old data |
| Integration breaks existing tooling | LOW | MEDIUM | Version API; maintain backwards compatibility |

### 9.2 Rollback Procedures

**If Parser Fails:**
```bash
# Disable AST parsing; fall back to regex-based analysis
export CODEX_AST_DISABLED=1
codex-audit src/ --format markdown
```text

**If Performance Degraded:**
```bash
# Reduce analysis scope
codex-analyze src/ --max-file-size 50000 --skip-heavy-analysis
```text

**If False Positives Too High:**
```bash
# Update configuration to reduce sensitivity
codex-analyze --smell-threshold high src/
```text

---

## 📋 Phase 10: Success Criteria & Acceptance

### 10.1 Definition of Done

- [ ] All 5 core components implemented (Parser, Metrics, Deps, Smells, KG)
- [ ] 80%+ code coverage for AST module
- [ ] All CLI tools working and documented
- [ ] Performance benchmarks met (<5s per 1000 LOC)
- [ ] API documentation complete with examples
- [ ] Integration tests passing
- [ ] Team training completed
- [ ] Integrated into CI/CD pipeline
- [ ] MATURITY_REMAINING_WORK.md auto-updated successfully
- [ ] Zero critical bugs in production

### 10.2 Acceptance Criteria

✅ Acceptance Test Suite

1. Parser Test
   - Parse 100% of codebase without errors
   - StandardizedAST representation correct for all 4 languages

2. Metrics Test
   - Cyclomatic complexity accurate within 5% of reference
   - Performance < 3s per 1000 LOC
   - Grade calculation (A-F) consistent across runs

3. Dependency Test
   - Cycle detection catches 100% of synthetic cycles
   - Graph exports correctly to DOT format

4. CLI Test
   - codex-analyze produces valid JSON/HTML output
   - codex-audit generates report in <30s
   - codex-diff correctly shows delta

5. Integration Test
   - MATURITY_REMAINING_WORK.md auto-updated with findings
   - GitHub Actions workflow executes successfully
   - No breaking changes to existing APIs

---

## 🎯 Conclusion

This **AST Standardization Project** provides a **foundation for deep codebase analysis** that extends far beyond test coverage. By standardizing AST parsing, building comprehensive metrics frameworks, and integrating with maturity tracking, you enable:

✅ **Objective Codebase Health Assessment**  
✅ **Automated Refactoring Recommendations**  
✅ **Data-Driven Architecture Decisions**  
✅ **Reproducible Code Quality Tracking**  
✅ **Team-Wide Code Intelligence**  

**Next Steps:**
1. AI Assistant autonomous document review
2. Allocate 2-3 weeks for dedicated engineering effort
3. Start with Sprint 1 (Parser + Standardization)
4. Deliver CLI tools by end of Sprint 5
5. Integrate into CI/CD in parallel

---

**Document Version:** 1.0  
**Status:** Ready for Implementation  
**Assigned To:** mbaetiong (Architecture Lead)  
**Review Cycle:** Bi-weekly

---

# 📊 Deep Codebase Analysis: Requirements Specification
> Generated: 2025-11-09 22:30:25 UTC | Author: mbaetiong

**🧠 Roles:** [Primary: Requirements Engineer], [Secondary: QA Lead] | ⚡ Energy: 5/5

---

## 1. Scope Definition

### 1.1 What is "Deep Codebase Analysis"?

**Definition:** Beyond-test analysis that examines **structural, semantic, and quality dimensions** of source code to enable **automated recommendations, complexity tracking, and architecture insights**.

**Analysis Dimensions:**

| Dimension | Examples | Tools |
|-----------|----------|-------|
| **Structural** | Module organization, dependency trees, import chains | AST parser, graph analysis |
| **Semantic** | Function purpose, type relationships, data flow | AST + inference, doc parsing |
| **Complexity** | Cyclomatic complexity, cognitive load, coupling | Graph metrics, AST traversal |
| **Quality** | Code smells, duplication, dead code, unused imports | Pattern matching, diff analysis |
| **Evolution** | Code churn, refactoring intensity, stability | Git history, commit analysis |
| **Standards** | Naming conventions, documentation completeness, type hints | Linting, pattern matching |

### 1.2 Scope Boundaries

**IN SCOPE:**
- ✅ Python source code analysis (primary)
- ✅ Configuration files (YAML, JSON, SQL)
- ✅ Static analysis (no runtime execution)
- ✅ Offline operation (no cloud services)
- ✅ CLI tools + integrations
- ✅ Knowledge graph building
- ✅ Metrics aggregation & reporting

**OUT OF SCOPE:**
- ❌ Runtime profiling (requires execution)
- ❌ Security vulnerability scanning (use specialized tools: bandit, safety)
- ❌ Performance optimization (requires benchmarking)
- ❌ Automated code generation/refactoring

---

## 2. Requirements Categories

### 2.1 Functional Requirements (Detailed)

#### **FR-ANALYSIS-001: Universal AST Parsing**

**Requirement:** The system shall parse Python, YAML, JSON, and SQL source code into a standardized, language-agnostic AST representation.

**Acceptance Criteria:**
- AC1: Parse 100% of valid Python files without syntax errors
- AC2: Extract function/class/module metadata (name, signature, location)
- AC3: Preserve docstrings and type hints
- AC4: Handle edge cases (decorators, comprehensions, async/await)
- AC5: Performance: <1ms per 100 tokens

**Test Cases:**
```python
test_parse_simple_function()
test_parse_decorated_class()
test_parse_async_function()
test_parse_comprehension()
test_parse_lambda()
test_parse_nested_structures()
```text

**Dependencies:** libcst, pyyaml, json (stdlib)

---

#### **FR-ANALYSIS-002: Complexity Metrics Extraction**

**Requirement:** The system shall compute cyclomatic complexity, cognitive complexity, and maintainability index for all functions.

**Acceptance Criteria:**
- AC1: Cyclomatic complexity accurate within ±5% of reference implementation
- AC2: Cognitive complexity reflects nested decision structures
- AC3: Maintainability index (0-100) computed per ISO/IEC 20926
- AC4: Metrics available for all function types (sync, async, decorated)
- AC5: Performance: <100ms per file

**Test Cases:**
```python
test_complexity_linear_function()  # CC = 1
test_complexity_if_else()          # CC = 2
test_complexity_nested_loops()     # CC = 4
test_complexity_exception_handling()  # CC = N + 1
```text

**Reference:**
- Cyclomatic Complexity (CC) = 1 + (branches)
- Cognitive Complexity ≈ CC + (nesting depth × 0.1)
- Maintainability Index = 171 - 5.2 × ln(Halstead Volume) - 0.23 × CC - 16.2 × ln(LOC)

---

#### **FR-ANALYSIS-003: Dependency Graph Construction**

**Requirement:** The system shall build a complete dependency graph showing imports, function calls, and class inheritance.

**Acceptance Criteria:**
- AC1: Extract all import statements (from/import variations)
- AC2: Extract function calls across module boundaries
- AC3: Extract class inheritance chains
- AC4: Detect circular dependencies with 100% recall
- AC5: Export graph in DOT format for visualization
- AC6: Performance: <1s per 100 modules

**Test Cases:**
```python
test_extract_simple_import()
test_extract_relative_import()
test_extract_star_import()
test_detect_cycle_simple()    # A → B → A
test_detect_cycle_complex()   # A → B → C → D → A
test_transitive_dependencies()
```text

---

#### **FR-ANALYSIS-004: Code Smell Detection**

**Requirement:** The system shall identify common code quality issues.

**Smell Types:**

| Smell | Threshold | Detection Method |
|-------|-----------|------------------|
| **Long Function** | LOC > 50 | Line counting |
| **High Complexity** | CC > 10 | Cyclomatic complexity |
| **High Cognitive Load** | CC_cog > 15 | Cognitive complexity |
| **Code Duplication** | >3 identical blocks | AST hash matching |
| **Dead Code** | Unused functions | Dependency graph analysis |
| **Unused Imports** | Not referenced | Import → usage tracking |
| **Long Parameter List** | >5 params | Function signature parsing |
| **Large Class** | >500 LOC | Line counting |
| **Deep Nesting** | >3 levels | AST depth tracking |
| **Magic Numbers** | Hardcoded literals | Pattern matching |

**Acceptance Criteria:**
- AC1: Detect all smell types with >80% precision
- AC2: Report smell location (file, line, column)
- AC3: Provide severity rating (low, medium, high, critical)
- AC4: Suggest remediation steps
- AC5: Allow whitelisting of false positives
- AC6: Performance: <500ms per 1000 LOC

**Test Cases:**
```python
test_detect_long_function()
test_detect_high_complexity()
test_detect_unused_import()
test_detect_duplication()
test_detect_dead_code()
```text

---

#### **FR-ANALYSIS-005: Type Hint Analysis**

**Requirement:** The system shall extract type hints and infer missing types.

**Acceptance Criteria:**
- AC1: Extract explicit type hints (function args, return types)
- AC2: Infer types from assignments and usage patterns
- AC3: Report type coverage percentage (% functions with hints)
- AC4: Identify type mismatches (e.g., None return but non-optional)
- AC5: Performance: <200ms per file

**Test Cases:**
```python
test_extract_function_types()
test_extract_class_attributes()
test_infer_from_assignment()
test_detect_type_mismatch()
```text

---

#### **FR-ANALYSIS-006: Documentation Coverage**

**Requirement:** The system shall assess documentation completeness.

**Acceptance Criteria:**
- AC1: Extract docstrings from modules, classes, functions
- AC2: Measure docstring coverage (% documented entities)
- AC3: Check docstring quality (length, structure, examples)
- AC4: Identify missing or outdated docstrings
- AC5: Performance: <100ms per file

**Metrics:**
- Docstring coverage: # documented / # total
- Docstring quality score (0-100)

---

#### **FR-ANALYSIS-007: Testing Coverage Integration**

**Requirement:** The system shall integrate with pytest coverage data.

**Acceptance Criteria:**
- AC1: Read pytest coverage reports (XML format)
- AC2: Map coverage to AST nodes (function level)
- AC3: Identify untested functions and code paths
- AC4: Correlate coverage with complexity (high-complexity = should be highly tested)
- AC5: Performance: <100ms per report

---

#### **FR-ANALYSIS-008: Knowledge Graph Export**

**Requirement:** The system shall export analysis results as queryable knowledge graph.

**Export Formats:**
- JSON (hierarchical, easy for tooling)
- SQLite (queryable, scalable)
- Markdown (human-readable reports)
- HTML (interactive visualization)
- DOT (graph visualization)

**Acceptance Criteria:**
- AC1: All analysis results representable in KG
- AC2: Export to all formats without data loss
- AC3: KG queries executable (e.g., "find all functions with CC > 10")
- AC4: Performance: <500ms per 1000 entities

---

#### **FR-ANALYSIS-009: Incremental Analysis**

**Requirement:** The system shall support incremental analysis for CI/CD integration.

**Acceptance Criteria:**
- AC1: Analyze only changed files (delta analysis)
- AC2: Compare metrics to baseline (e.g., previous commit)
- AC3: Report deltas (improvements, regressions)
- AC4: Flag breaking changes (e.g., new circular dependencies)
- AC5: Performance: <1s for typical PR (5-10 files changed)

---

#### **FR-ANALYSIS-010: CLI Interface**

**Requirement:** The system shall provide command-line tools for analysis.

**CLI Tools:**

```bash
codex-analyze <path>              # Analyze single file/directory
  --metric <metric>               # Filter by metric
  --output <format>               # JSON, Markdown, HTML, SQLite
  --threshold <value>             # Filter by value
  --exclude <pattern>             # Exclude files

codex-audit .                     # Full codebase audit
  --output <report.html>          # Report path
  --format <html|markdown>        # Report format
  --baseline <ref>                # Compare to baseline

codex-diff <ref1> <ref2>          # Compare two commits
  --metric <metric>               # Which metrics to compare
  --threshold <delta>             # Report only changes > threshold

codex-export <path> <format>      # Export to specific format
  --include-metrics               # Include computed metrics
  --include-graph                 # Include dependency graph
```text

**Acceptance Criteria:**
- AC1: All CLI tools work offline (no network calls)
- AC2: Help text comprehensive (--help)
- AC3: Exit codes meaningful (0=success, 1=analysis errors, 2=quality gates failed)
- AC4: Output consistent across formats
- AC5: Performance: <30s for typical codebase (10K LOC)

---

### 2.2 Non-Functional Requirements

#### **Performance (NFR-P)**

| Metric | Target | Rationale |
|--------|--------|-----------|
| **Parse Speed** | <1ms per 100 tokens | Enable real-time IDE integration |
| **Analyze Speed** | <5s per 1000 LOC | Enable CI/CD without slowdown |
| **Memory Usage** | <500MB for 50K LOC | Run on developer machines |
| **Graph Build** | <1s per 100 modules | Enable interactive queries |

**Performance Tests:**
```python
@pytest.mark.benchmark
def test_parse_speed_benchmark(benchmark):
    result = benchmark(parser.parse, large_file, "python")
    assert result is not None

@pytest.mark.benchmark
def test_analyze_speed_benchmark(benchmark):
    result = benchmark(analyzer.analyze, large_codebase)
    assert result is not None
```text

---

#### **Accuracy (NFR-A)**

| Metric | Target | Method |
|--------|--------|--------|
| **Parser Accuracy** | >99% | Compare against libcst/ast baseline |
| **Complexity Accuracy** | >95% | Validate against reference implementations |
| **Cycle Detection** | 100% recall, >95% precision | Synthetic test graphs |
| **Smell Detection** | >80% precision | Manual review of sample results |

---

#### **Reliability (NFR-R)**

| Metric | Target | Method |
|--------|--------|--------|
| **Error Handling** | No crashes on invalid input | Fuzz testing with malformed code |
| **Graceful Degradation** | Partial results on parse error | Fallback analysis strategies |
| **Consistency** | Same input = same output | Deterministic algorithms only |

---

#### **Maintainability (NFR-M)**

| Metric | Target | Method |
|--------|--------|--------|
| **Code Duplication** | <10% | Automated duplication detection |
| **Test Coverage** | >80% | Coverage reports |
| **Documentation** | 100% of public API | Automated doc generation |
| **Cyclomatic Complexity** | <10 per function | Enforce via analysis tool itself |

---

#### **Usability (NFR-U)**

| Metric | Target | Method |
|--------|--------|--------|
| **Learning Time** | <30 min to first analysis | Quick-start guide + examples |
| **Error Messages** | Actionable | Include suggestions and remediation |
| **Integration** | One-line install | pip install codex-ml[ast] |

---

### 2.3 Constraint Requirements (CR)

| Constraint | Impact | Mitigation |
|-----------|--------|-----------|
| **Offline-first** | No cloud APIs (no remote parsing, no remote KG) | Use local storage; embed required libraries |
| **Python 3.8+** | Limited modern syntax | Pin library versions; test on min version |
| **Single-threaded by default** | Phase 5 bottleneck on large codebases | Offer optional multiprocessing mode |
| **File-based storage** | Limited query capabilities | Use SQLite for richer queries |
| **No external dependencies (optional)** | Keep it lightweight | Make heavy deps optional (libcst, etc.) |

---

## 3. Quality Attributes

### 3.1 Quality Model (ISO/IEC 25010)

| Attribute | Target | Measurement |
|-----------|--------|-------------|
| **Functional Completeness** | 100% FR coverage | All FR acceptance criteria met |
| **Performance Efficiency** | NFR-P targets met | Benchmark tests passing |
| **Reliability** | 99.5% uptime | Zero crashes on valid input |
| **Usability** | <30 min learning time | User feedback survey |
| **Maintainability** | <10% duplication, >80% coverage | Code metrics |
| **Security** | No injection attacks, no hardcoded secrets | Security scan (bandit) |
| **Compatibility** | Works on Python 3.8-3.12 | CI/CD matrix testing |

---

### 3.2 Testing Strategy

**Test Pyramid:**

```text
        ┌─────────────────┐
        │  E2E Tests (5%) │  - Full pipeline tests
        ├─────────────────┤
        │  Integration    │  - Component interaction tests
        │  Tests (25%)    │
        ├─────────────────┤
        │  Unit Tests     │  - Individual function tests
        │  (70%)          │
        └─────────────────┘
```text

**Test Coverage by Component:**

| Component | Target Coverage | Strategy |
|-----------|-----------------|----------|
| Parser | 90%+ | Unit tests per language adapter |
| Analyzers | 85%+ | Unit tests per metric; synthetic data |
| KG Builder | 80%+ | Unit tests; integration tests |
| Exporters | 85%+ | Unit tests per format |
| CLI | 75%+ | Integration tests; mock I/O |

**Regression Test Suite:**
```python
# tests/regression/
test_parser_regression.py       # Ensure parser doesn't break on known files
test_metrics_regression.py       # Ensure metrics consistent over time
test_cycle_detection_regression.py  # Ensure cycles detected correctly
```text

---

## 4. Data Model & Schemas

### 4.1 Core Data Model

```python
# Standardized AST Node
@dataclass
class ASTNode:
    type: str                           # "module", "function", "class", etc.
    name: str
    parent: Optional[ASTNode]
    children: List[ASTNode]
    source_location: SourceLocation    # file, line, column
    metadata: Dict[str, Any]           # language-specific
    docstring: Optional[str]
    type_hints: Dict[str, str]
    decorators: List[str]

# Analysis Result
@dataclass
class AnalysisResult:
    file_path: Path
    ast: ASTNode
    metrics: CodeMetrics
    smells: List[CodeSmell]
    dependencies: List[Dependency]
    coverage_data: Optional[CoverageData]
    timestamp: datetime

# Code Metrics
@dataclass
class CodeMetrics:
    lines_of_code: int
    cyclomatic_complexity: int
    cognitive_complexity: float
    halstead_volume: float
    maintainability_index: float
    test_coverage_percent: Optional[float]
    type_hint_coverage: float

# Code Smell
@dataclass
class CodeSmell:
    type: str                           # "long_function", etc.
    severity: str                       # "low", "medium", "high", "critical"
    location: SourceLocation
    message: str
    suggested_fix: Optional[str]
```text

### 4.2 Knowledge Graph Schema

**Entities:**
- Module (path, LOC, imports)
- Function (name, signature, complexity, coverage)
- Class (name, methods, attributes)
- Variable (name, type, usage_count)
- Dependency (source, target, type)

**Relationships:**
- contains (Module → Function/Class)
- imports (Module → Module)
- calls (Function → Function)
- inherits_from (Class → Class)
- type_of (Variable → Type)
- depends_on (Any → Any)

**Attributes:**
- Metrics (CC, LOC, coverage)
- Smells (list of detected smells)
- Quality tier (A-F grade)

---

## 5. Integration Points

### 5.1 CI/CD Integration

**GitHub Actions:**
```yaml
- Trigger: Push to main, PR creation
- Steps:
  1. Run codex-audit on changed files
  2. Compare metrics to baseline
  3. Fail if critical quality gates breached
  4. Comment on PR with findings
  5. Upload report as artifact
```text

**Quality Gates:**
```text
PASS if:
  - No new circular dependencies introduced
  - Average complexity not increased >10%
  - Code smell count not increased
  - Type hint coverage not decreased
  - Test coverage not decreased

FAIL if:
  - Any of above violated
```text

---

### 5.2 IDE Integration

**VSCode Extension (Future):**
```text
- Show inline complexity warnings
- Hover for metric details
- Quick-fix suggestions
- Code smell highlighting
```text

---

### 5.3 MATURITY_REMAINING_WORK.md Integration

**Auto-Update Mechanism:**
```bash
# After each analysis run:
codex-audit src/ --update-maturity MATURITY_REMAINING_WORK.md

# Output: Updated checklist with findings
```text

---

## 6. Error Handling & Edge Cases

### 6.1 Error Categories

| Category | Example | Handling |
|----------|---------|----------|
| **Parse Errors** | Syntax errors, unsupported syntax | Log warning; skip file; continue |
| **Analysis Errors** | Circular import during graph build | Detect cycle; break at known point |
| **File Access Errors** | Permission denied, file not found | Skip file; log error; continue |
| **Memory Pressure** | Out of memory on huge file | Implement streaming; chunk analysis |
| **Timeout** | Analysis takes >timeout threshold | Kill process; return partial results |

### 6.2 Edge Cases

| Edge Case | Expected Behavior |
|-----------|-------------------|
| Empty file | Return empty AST; zero metrics |
| Single-line file | Parse correctly; no complexity |
| File with only comments | Parse correctly; zero metrics |
| Circular imports | Detect and report; don't crash |
| Very deeply nested code | Parse correctly; report high complexity |
| File with encoding issues | Handle gracefully; attempt fallback encoding |
| Binary files in directory | Skip gracefully; continue analysis |

---

## 7. Acceptance & Validation

### 7.1 Validation Checkpoints

| Checkpoint | Criteria | Owner |
|-----------|----------|-------|
| **Design Review** | Architecture review; sign-off | Tech Lead |
| **Sprint 1 Gate** | Parser working for all languages | Dev Lead |
| **Sprint 2 Gate** | Metrics accurate within tolerance | QA Lead |
| **Sprint 3 Gate** | Dependency graph correct | Dev Lead |
| **Sprint 4 Gate** | Code smells detecting correctly | QA Lead |
| **Sprint 5 Gate** | CLI tools working end-to-end | QA Lead |
| **Sprint 6 Gate** | 80%+ coverage; docs complete | QA Lead |
| **Production Gate** | All NFRs met; no regressions | Tech Lead |

---

### 7.2 Sign-Off Criteria

**Functional Sign-Off:**
- [ ] All FR acceptance criteria verified
- [ ] All test cases passing
- [ ] No critical bugs remaining
- [ ] Documentation complete and reviewed

**Non-Functional Sign-Off:**
- [ ] All performance benchmarks met
- [ ] Test coverage ≥80%
- [ ] Zero security vulnerabilities
- [ ] Offline operation verified

**Stakeholder Sign-Off:**
- [ ] Product owner approves feature set
- [ ] Tech lead approves architecture
- [ ] QA lead approves test coverage
- [ ] DevOps lead approves CI/CD integration

---

## 8. Traceability Matrix

**Requirements → Tests → Acceptance:**

| FR ID | Requirement | Test Case | Acceptance Criteria | Status |
|-------|-------------|-----------|-------------------|--------|
| FR-AST-001 | Parse Python | test_parse_function | Parses 100% without error | ⏳ |
| FR-AST-002 | Extract metadata | test_extract_signature | Correct signature extracted | ⏳ |
| ... | ... | ... | ... | ... |

---

## Conclusion

This **Requirements Specification** provides **comprehensive, verifiable, and measurable** requirements for the deep codebase analysis system. By following this specification, the implementation team can ensure:

✅ **Completeness** — All necessary functionality covered  
✅ **Quality** — Non-functional requirements met  
✅ **Testability** — Clear acceptance criteria  
✅ **Traceability** — All features verified  

**Next Steps:**
1. Review with stakeholders
2. Estimate effort per FR
3. Prioritize requirements
4. Allocate

```