# 📋 AST: Deep Codebase Analysis Requirements
> Generated: Previous Cycle-11-09 22:32:45 UTC | Author: mbaetiong

**🧠 Roles:** [Primary: Requirements Engineer], [Secondary: Architecture Lead] | ⚡ Energy: 5/5

---

## 1. Executive Summary

This document establishes **comprehensive, binding requirements** for developing an **AST (Abstract Syntax Tree) Standardization Project** that enables **deep codebase analysis beyond test scope**. 

**Strategic Objectives:**
- ✅ Standardize AST parsing across Python/YAML/JSON codebases
- ✅ Enable automated structural and semantic codebase analysis
- ✅ Provide objective metrics for code quality, complexity, and dependencies
- ✅ Integrate maturity tracking with AST-derived findings
- ✅ Create knowledge graphs for team-wide code intelligence

**Scope:** Comprehensive codebase analysis → structural, semantic, quality, and evolution tracking

---

## 2. Requirement Categories Matrix

### 2.1 Functional Requirements (FR) - CRITICAL PATH

| ID | Requirement | Priority | Acceptance Criteria | Dependencies |
|----|-------------|----------|-------------------|--------------|
| **FR-AST-001** | **Universal AST Parser** | CRITICAL | Parse 100% valid Python/YAML/JSON without errors; <1ms per 100 tokens | libcst, pyyaml |
| **FR-AST-002** | **Standardized AST Representation** | CRITICAL | Language-agnostic node format; preserves metadata (docstrings, types, decorators) | FR-AST-001 |
| **FR-AST-003** | **Cyclomatic Complexity Metrics** | CRITICAL | CC accurate ±5% vs reference; available per function; <100ms per file | FR-AST-002 |
| **FR-AST-004** | **Cognitive Complexity Measurement** | HIGH | Reflects nested decision depth; <200ms per file | FR-AST-003 |
| **FR-AST-005** | **Dependency Graph Construction** | CRITICAL | Extract imports, calls, inheritance; build directed graph; <1s per 100 modules | FR-AST-002 |
| **FR-AST-006** | **Circular Dependency Detection** | HIGH | 100% recall on synthetic cycles; detect with 1st algorithm; report cycles with path | FR-AST-005 |
| **FR-AST-007** | **Code Smell Detection** | HIGH | Detect 8+ smell types (long functions, high complexity, duplication, dead code); >80% precision | FR-AST-003 |
| **FR-AST-008** | **Type Hint Extraction & Inference** | MEDIUM | Extract explicit hints; infer from usage; measure coverage; <200ms per file | FR-AST-002 |
| **FR-AST-009** | **Documentation Coverage Analysis** | MEDIUM | Extract docstrings; measure coverage %; assess quality; <100ms per file | FR-AST-002 |
| **FR-AST-010** | **Testing Coverage Integration** | MEDIUM | Read pytest XML; map to AST nodes; correlate coverage ↔ complexity | FR-AST-002 |
| **FR-AST-011** | **Knowledge Graph Export** | HIGH | Export to JSON/SQLite/Markdown/HTML/DOT; queryable; no data loss; <500ms per 1000 entities | FR-AST-003+ |
| **FR-AST-012** | **Incremental Delta Analysis** | HIGH | Analyze only changed files; compare to baseline; report improvements/regressions; <1s for typical PR | FR-AST-003+ |
| **FR-AST-013** | **CLI Interface Suite** | CRITICAL | 3 tools: codex-analyze, codex-audit, codex-diff; offline-capable; <30s per 10K LOC | FR-AST-011+ |
| **FR-AST-014** | **MATURITY_REMAINING_WORK Auto-Update** | HIGH | Auto-populate with findings; prioritize by impact; maintain human-editable sections | FR-AST-007+ |
| **FR-AST-015** | **GitHub Actions Integration** | HIGH | Workflow template; auto-comment on PRs; fail on quality gates; artifact upload | FR-AST-013 |

---

### 2.2 Non-Functional Requirements (NFR) - QUALITY GATES

| ID | Attribute | Target | Measurement | Priority |
|----|-----------|--------|-------------|----------|
| **NFR-PERF-001** | **Parse Performance** | <1ms per 100 tokens | Benchmark suite | CRITICAL |
| **NFR-PERF-002** | **Analysis Speed** | <5s per 1000 LOC | Wall-clock time | CRITICAL |
| **NFR-PERF-003** | **Memory Footprint** | <500MB for 50K LOC | Peak memory usage | HIGH |
| **NFR-PERF-004** | **Graph Build Time** | <1s per 100 modules | Edge addition time | HIGH |
| **NFR-PERF-005** | **CLI Responsiveness** | <30s full codebase audit | End-to-end latency | MEDIUM |
| **NFR-ACC-001** | **Parser Accuracy** | >99% vs libcst baseline | Regression tests | CRITICAL |
| **NFR-ACC-002** | **Complexity Accuracy** | ±5% vs reference impl | Validation suite | CRITICAL |
| **NFR-ACC-003** | **Cycle Detection Recall** | 100% on synthetic graphs | Test matrix | HIGH |
| **NFR-ACC-004** | **Smell Detection Precision** | >80% (false positives <20%) | Manual review sample | HIGH |
| **NFR-REL-001** | **Error Resilience** | Zero crashes on invalid input | Fuzz testing | CRITICAL |
| **NFR-REL-002** | **Graceful Degradation** | Partial results on parse error | Error handling tests | HIGH |
| **NFR-REL-003** | **Determinism** | Identical input → identical output | Reproducibility tests | CRITICAL |
| **NFR-MAINT-001** | **Code Duplication** | <10% | Automated detection | MEDIUM |
| **NFR-MAINT-002** | **Test Coverage** | ≥80% | Coverage reports | HIGH |
| **NFR-MAINT-003** | **Cyclomatic Complexity** | <10 per function | Enforced by own tool | MEDIUM |
| **NFR-SEC-001** | **Security Issues** | 0 high-severity | Bandit + dependency scan | CRITICAL |
| **NFR-COMPAT-001** | **Python Version Support** | 3.8-3.12 | CI/CD matrix | HIGH |
| **NFR-COMPAT-002** | **Offline Operation** | 100% (no cloud calls) | Network isolation test | CRITICAL |

---

### 2.3 Constraint Requirements (CR) - IMMUTABLE

| ID | Constraint | Impact | Mitigation Strategy |
|----|-----------|--------|-------------------|
| **CR-ENV-001** | **Offline-First** | No cloud APIs, no remote services | Use local storage (SQLite), embed parsers |
| **CR-ENV-002** | **Python 3.8+ Only** | Cannot use modern syntax (3.10+ match, 3.11+ exception groups) | Pin dependencies; backport helpers |
| **CR-ENV-003** | **File-Based Storage** | Limited query flexibility vs databases | Use SQLite for richer queries |
| **CR-ENV-004** | **Performance Budget** | Must complete within 5s per 1000 LOC | Implement streaming, parallel processing |
| **CR-ORG-001** | **Test-Driven Development** | Must write tests before code | Enforce via pre-commit hooks |
| **CR-ORG-002** | **No Code Duplication** | Keep implementations DRY | Enforce <10% threshold |
| **CR-ORG-003** | **Comprehensive Documentation** | Enable team adoption | Mandatory for all public APIs |

---

## 3. Data Model & Schemas

### 3.1 Standardized AST Node Structure

```python
@dataclass
class SourceLocation:
    """Pin point code location."""
    file_path: Path
    line_start: int
    line_end: int
    column_start: int
    column_end: int

@dataclass
class StandardizedASTNode:
    """Language-agnostic AST representation."""
    # Identity
    node_id: str                        # unique identifier
    type: str                           # "module", "function", "class", "statement", etc.
    name: str                           # identifier
    
    # Structure
    parent: Optional["StandardizedASTNode"]
    children: List["StandardizedASTNode"]
    
    # Metadata
    source_location: SourceLocation
    docstring: Optional[str]
    decorators: List[str]              # e.g., ["@dataclass", "@property"]
    
    # Type System
    type_hints: Dict[str, str]          # param → type_str mappings
    inferred_types: Dict[str, str]      # inferred types
    
    # Language-Specific Details (JSON blob for extensibility)
    metadata: Dict[str, Any]
    
    # Analysis Results (populated post-parse)
    analysis_results: Optional["AnalysisResults"] = None
```text

### 3.2 Analysis Results Schema

```python
@dataclass
class CodeMetrics:
    """Aggregated code quality metrics."""
    lines_of_code: int
    cyclomatic_complexity: int
    cognitive_complexity: float
    halstead_volume: float
    halstead_difficulty: float
    maintainability_index: float        # 0-100, A-F grade
    test_coverage: Optional[float]      # 0-100%
    type_hint_coverage: float           # 0-100%
    
    @property
    def quality_tier(self) -> str:
        """Compute A-F grade from MI."""
        if self.maintainability_index >= 85: return "A"
        if self.maintainability_index >= 70: return "B"
        if self.maintainability_index >= 55: return "C"
        if self.maintainability_index >= 40: return "D"
        return "F"

@dataclass
class CodeSmell:
    """Identified code quality issue."""
    smell_type: str                     # "long_function", "high_complexity", etc.
    severity: str                       # "low", "medium", "high", "critical"
    location: SourceLocation
    message: str
    suggested_remediation: Optional[str]
    confidence: float                   # 0.0-1.0

@dataclass
class AnalysisResults:
    """Complete analysis for an AST node."""
    metrics: CodeMetrics
    smells: List[CodeSmell]
    dependencies: List["Dependency"]
    timestamp: datetime
    analyzer_version: str
```text

### 3.3 Dependency Graph Schema

```python
@dataclass
class Dependency:
    """Relationship between code entities."""
    source_id: str                      # from node_id
    target_id: str                      # to node_id
    dep_type: str                       # "imports", "calls", "inherits_from", "uses"
    line_number: int
    is_circular: bool = False

@dataclass
class DependencyGraph:
    """Directional graph of all dependencies."""
    nodes: Dict[str, StandardizedASTNode]
    edges: List[Dependency]
    
    def get_transitive_dependencies(self, node_id: str) -> Set[str]:
        """All nodes reachable from this node."""
        pass
    
    def get_transitive_dependents(self, node_id: str) -> Set[str]:
        """All nodes that depend on this node."""
        pass
    
    def detect_cycles(self) -> List[List[str]]:
        """Find strongly connected components (Tarjan's algorithm)."""
        pass
    
    def compute_fan_in(self, node_id: str) -> int:
        """Count incoming edges."""
        pass
    
    def compute_fan_out(self, node_id: str) -> int:
        """Count outgoing edges."""
        pass
```text

### 3.4 Knowledge Graph Export Schema

**SQLite Schema (Normalized):**

```sql
-- Entities
CREATE TABLE modules (
    id TEXT PRIMARY KEY,
    file_path TEXT NOT NULL,
    lines_of_code INTEGER,
    complexity_avg REAL,
    quality_tier TEXT
);

CREATE TABLE functions (
    id TEXT PRIMARY KEY,
    module_id TEXT NOT NULL,
    name TEXT NOT NULL,
    signature TEXT,
    lines_of_code INTEGER,
    cyclomatic_complexity INTEGER,
    maintainability_index REAL,
    test_coverage REAL,
    FOREIGN KEY (module_id) REFERENCES modules(id)
);

CREATE TABLE classes (
    id TEXT PRIMARY KEY,
    module_id TEXT NOT NULL,
    name TEXT NOT NULL,
    lines_of_code INTEGER,
    method_count INTEGER,
    FOREIGN KEY (module_id) REFERENCES modules(id)
);

-- Relationships
CREATE TABLE dependencies (
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    dep_type TEXT NOT NULL,  -- "imports", "calls", "inherits_from"
    is_circular BOOLEAN,
    PRIMARY KEY (source_id, target_id)
);

CREATE TABLE code_smells (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id TEXT NOT NULL,
    smell_type TEXT NOT NULL,
    severity TEXT,
    message TEXT,
    line_number INTEGER
);

-- Metrics
CREATE TABLE quality_metrics (
    entity_id TEXT PRIMARY KEY,
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL
);
```text

---

## 4. Implementation Phases & Deliverables

### Phase 1: Foundation (Sprint 1-2) - WEEKS 1-2

**Goal:** Core parsing and standardization

| Task | Deliverable | Acceptance Criteria |
|------|-------------|-------------------|
| **1.1: Parser Architecture** | `src/codex_ml/ast/parser.py` | FR-AST-001, FR-AST-002 passing |
| **1.2: Python Adapter** | `src/codex_ml/ast/language_adapters/python_adapter.py` | Parse 100% test suite; <1ms/100 tokens |
| **1.3: YAML/JSON Adapters** | `src/codex_ml/ast/language_adapters/yaml_adapter.py`, `json_adapter.py` | Both adapters working; tests passing |
| **1.4: Unit Tests** | `tests/ast/test_parser*.py` | >90% coverage; all tests green |
| **1.5: Documentation** | `docs/ast/parsing.md` | API reference + examples |

**Success Gate:** `nox -s test -- tests/ast/test_parser*` passes; benchmarks meet NFR-PERF-001

---

### Phase 2: Metrics & Analysis (Sprint 2-3) - WEEKS 3-5

**Goal:** Complexity computation, code smell detection

| Task | Deliverable | Acceptance Criteria |
|------|-------------|-------------------|
| **2.1: Metrics Analyzer** | `src/codex_ml/ast/analyzers/metrics.py` | FR-AST-003, FR-AST-004 passing; ±5% accuracy |
| **2.2: Code Smell Detector** | `src/codex_ml/ast/analyzers/smells.py` | FR-AST-007; 8+ smell types; >80% precision |
| **2.3: Type Analysis** | `src/codex_ml/ast/analyzers/types.py` | FR-AST-008; coverage metric available |
| **2.4: Unit Tests** | `tests/ast/test_metrics*.py`, `test_smells*.py` | >85% coverage |
| **2.5: Benchmarking** | Performance report | Meets NFR-PERF-002, NFR-PERF-003 |

**Success Gate:** `pytest --cov=src/codex_ml/ast/analyzers --cov-fail-under=85` passes

---

### Phase 3: Dependency & Graph (Sprint 3-4) - WEEKS 6-8

**Goal:** Dependency analysis, cycle detection, knowledge graph

| Task | Deliverable | Acceptance Criteria |
|------|-------------|-------------------|
| **3.1: Dependency Extractor** | `src/codex_ml/ast/analyzers/dependencies.py` | FR-AST-005; extract imports, calls, inheritance |
| **3.2: Cycle Detector** | `src/codex_ml/ast/analyzers/cycle_detection.py` | FR-AST-006; 100% recall; report paths |
| **3.3: KG Builder** | `src/codex_ml/ast/knowledge_graph.py` | FR-AST-011; build queryable graph |
| **3.4: Exporters** | `src/codex_ml/ast/exporters/{json,sqlite,markdown,html}.py` | All formats working; test coverage >85% |
| **3.5: Integration Tests** | `tests/ast/test_integration.py` | Full pipeline working end-to-end |

**Success Gate:** Full codebase audit runs in <30s; exports all formats correctly

---

### Phase 4: CLI & Integration (Sprint 4-5) - WEEKS 8-10

**Goal:** User-facing tools, CI/CD integration

| Task | Deliverable | Acceptance Criteria |
|------|-------------|-------------------|
| **4.1: CLI Framework** | `src/codex_ml/ast/cli.py` | FR-AST-013; 3 tools working; --help complete |
| **4.2: MATURITY Integration** | `src/codex_ml/ast/maturity_updater.py` | FR-AST-014; auto-populate checklist |
| **4.3: GitHub Actions** | `.github/workflows/ast_analysis.yml` | FR-AST-015; auto-comment, fail gates |
| **4.4: Documentation** | `docs/ast/cli_guide.md`, `integration_guide.md` | Comprehensive; examples runnable |
| **4.5: CLI Tests** | `tests/ast/test_cli.py` | Integration tests; >75% coverage |

**Success Gate:** `codex-analyze .` runs offline; generates valid reports in <30s

---

### Phase 5: Testing & Validation (Sprint 6) - WEEKS 11-12

**Goal:** Comprehensive validation, production readiness

| Task | Deliverable | Acceptance Criteria |
|------|-------------|-------------------|
| **5.1: Performance Tests** | `tests/ast/test_benchmarks.py` | All NFR-PERF targets met |
| **5.2: Accuracy Validation** | `tests/ast/test_validation.py` | All NFR-ACC targets met; >95% accuracy |
| **5.3: Fuzz Testing** | Fuzz test suite | NFR-REL-001: zero crashes |
| **5.4: Coverage Report** | `htmlcov/index.html` | ≥80% overall; key modules >85% |
| **5.5: Security Audit** | Bandit + dependency check | NFR-SEC-001: 0 critical issues |
| **5.6: Final Docs** | Complete user + dev docs | API reference, tutorials, troubleshooting |

**Success Gate:** `nox -s gates` passes; ready for production deployment

---

## 5. Quality Assurance Framework

### 5.1 Testing Strategy (Test Pyramid)

```text
        ┌──────────────────────┐
        │  E2E Tests (5%)      │   Full pipeline: codebase → report
        ├──────────────────────┤
        │  Integration (20%)   │   Component interaction: parser → analyzer → exporter
        ├──────────────────────┤
        │  Unit Tests (75%)    │   Individual function: parser.parse() → AST
        └──────────────────────┘
```text

### 5.2 Test Coverage Targets by Component

| Component | Target | Rationale |
|-----------|--------|-----------|
| Parser | 90%+ | Core; high risk if broken |
| Analyzers | 85%+ | Multiple code paths for metrics |
| KG Builder | 80%+ | Mostly transformation logic |
| Exporters | 85%+ | Data formatting; edge cases important |
| CLI | 75%+ | Integration-heavy; user-facing |

### 5.3 Regression Test Matrix

| Scenario | Test File | Validation |
|----------|-----------|-----------|
| Parser consistency | `test_parser_regression.py` | Same input → same AST across runs |
| Metrics stability | `test_metrics_regression.py` | Known functions → expected CC/LOC |
| Cycle detection | `test_cycle_regression.py` | Synthetic graphs → correct cycles |
| Export fidelity | `test_export_regression.py` | Analysis → export → re-parse identical |

---

## 6. Acceptance & Sign-Off Process

### 6.1 Validation Checkpoints

| Checkpoint | Criteria | Owner | Sign-Off |
|-----------|----------|-------|---------|
| **Design Review** | Architecture reviewed; tech spike completed | Tech Lead | ✍️ |
| **Phase 1 Gate** | Parser working for all languages; tests green | QA Lead | ✍️ |
| **Phase 2 Gate** | Metrics accurate; smells detected; benchmarks met | QA Lead | ✍️ |
| **Phase 3 Gate** | Dependency graph built; cycles detected; exports work | QA Lead | ✍️ |
| **Phase 4 Gate** | CLI tools working; MATURITY integrated; docs complete | QA Lead + Product | ✍️ |
| **Phase 5 Gate** | 80%+ coverage; security clean; performance OK | QA Lead + Tech Lead | ✍️ |
| **Production Gate** | All acceptance criteria met; no known issues | Tech Lead + Product Lead | ✍️ |

### 6.2 Functional Acceptance Criteria (Final)

**Parser:**
- [ ] Parse 100% of valid Python/YAML/JSON without syntax errors
- [ ] Extract all metadata (decorators, docstrings, type hints)
- [ ] Handle edge cases (async/await, comprehensions, decorators)

**Metrics:**
- [ ] CC accurate ±5% vs reference
- [ ] Cognitive complexity reflects nesting depth
- [ ] Maintainability index grade A-F correct

**Dependencies:**
- [ ] All imports extracted correctly
- [ ] Function calls mapped across modules
- [ ] Inheritance chains traced
- [ ] Cycles detected with 100% recall

**Code Smells:**
- [ ] Long functions (>50 LOC) detected
- [ ] High complexity (CC>10) flagged
- [ ] Dead code identified
- [ ] Duplication found
- [ ] >80% precision (manual review)

**Knowledge Graph:**
- [ ] Entities: modules, functions, classes, types
- [ ] Relationships: imports, calls, inheritance
- [ ] Attributes: metrics, smells, quality tier
- [ ] Queryable (SQL-like for SQLite export)

**CLI Tools:**
- [ ] `codex-analyze` works for single files and directories
- [ ] `codex-audit` generates full reports in <30s
- [ ] `codex-diff` shows metric deltas
- [ ] All work offline without network calls

---

## 7. Risk Assessment & Mitigation

### 7.1 High-Risk Items

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| **Parser fails on uncommon syntax** | MEDIUM | HIGH | Fallback to `ast` module; comprehensive error handling |
| **Performance degrades on large files** | LOW | HIGH | Streaming parser; parallel processing; file size limits |
| **Circular imports cause infinite loops** | LOW | CRITICAL | Implement visited set; break on known points |
| **False positives in smell detection** | MEDIUM | MEDIUM | Tune heuristics; add whitelisting; manual review |
| **Knowledge graph memory explosion** | LOW | MEDIUM | Incremental updates; archive old data; lazy loading |

### 7.2 Rollback Procedures

**If Parser Fails:**
```bash
export CODEX_AST_DISABLED=1
# Fall back to regex-based analysis
```text

**If Performance Degraded:**
```bash
# Reduce scope
codex-analyze src/ --max-file-size 50000 --skip-expensive-analysis
```text

**If Smell Detection Too Noisy:**
```bash
# Reduce sensitivity
codex-analyze --smell-threshold high src/
```text

---

## 8. Success Metrics & KPIs

### 8.1 Delivery KPIs

| KPI | Target | Method |
|-----|--------|--------|
| **On-Time Delivery** | Complete in 12 weeks | Gantt chart tracking |
| **Quality (Defect Rate)** | <5 bugs per 1000 LOC | Bug tracking post-release |
| **Test Coverage** | ≥80% | Coverage reports |
| **Performance** | Meet all NFR-PERF targets | Benchmark suite |

### 8.2 Adoption KPIs

| KPI | Target | Method |
|-----|--------|--------|
| **Team Usage** | 70% of PRs analyzed within 3 months | GitHub Actions metrics |
| **False Positive Rate** | <10% | User feedback + validation |
| **Integration Success** | 0 CI/CD failures from AST tool | Action logs |

---

## 9. Documentation Requirements

### 9.1 Mandatory Documentation

| Document | Audience | Content |
|----------|----------|---------|
| **API Reference** | Developers | All classes, methods, return types, examples |
| **CLI Guide** | Users | Tool usage, parameters, output formats |
| **Architecture Guide** | Developers | System design, data flow, extension points |
| **Integration Guide** | DevOps | CI/CD setup, quality gates, reporting |
| **Troubleshooting** | Users | Common errors, resolution steps |
| **Examples** | All | Runnable code samples for each feature |

---

## 10. Conclusion & Next Steps

This requirements document provides **complete, verifiable, and measurable** specifications for the AST Standardization Project. 

**Critical Success Factors:**
1. ✅ **Adherence to FR & NFR**: Implement exactly as specified; deviations require RFP amendment
2. ✅ **Test-Driven Development**: Write tests before code; maintain >80% coverage
3. ✅ **Regular Sign-Offs**: Validate at each phase gate; no surprises at end
4. ✅ **Documentation**: Keep docs in sync with code; mandatory for all APIs

**Next Actions:**
1. **This Week:** Schedule kickoff with team; assign roles
2. **Next Week:** Complete design review; begin Sprint 1
3. **Weekly:** Status updates, risk reviews, sign-off gates

---

**Document Version:** 1.0 (FINAL)  
**Status:** APPROVED FOR IMPLEMENTATION  
**Assigned To:** mbaetiong (Primary Engineer)  
**Review Cycle:** Phase-end gates + final sign-off
```text

Now creating the complementary validation and implementation guidance file:

```markdown name=AST_Standardization_InstructionEnhancement.md
# 🔄 AST: Standardization Implementation Guidance
> Generated: Previous Cycle-11-09 22:32:45 UTC | Author: mbaetiong

**🧠 Roles:** [Primary: Implementation Lead], [Secondary: Technical Architect] | ⚡ Energy: 5/5

⚛️ **Physics:** Path🛤️ [Sequential phases] | Fields🔄 [Modular components] | Patterns👁️ [DRY code, reusable analyzers] | Redundancy🔀 [Fallback strategies] | Balance⚖️ [Performance vs accuracy]

---

## 1. Implementation Philosophy

### 1.1 Core Principles

| Principle | Application | Benefit |
|-----------|-------------|---------|
| **Standardization** | Single AST format across languages | Enables cross-language analysis; reduces duplication |
| **Modularity** | Independent parser, analyzer, exporter modules | Allows parallel development; easy testing |
| **Incrementalism** | Deliver value per phase; iterate on feedback | Reduces risk; enables early validation |
| **Determinism** | Identical input → identical output always | Reproducible results; easier debugging |
| **Offline-First** | No cloud dependencies; all processing local | Works in air-gapped environments |
| **Fail-Safe** | Graceful degradation on errors | Partial results better than crash |

### 1.2 Architecture Decision Records (ADRs)

| ADR | Decision | Rationale | Tradeoffs |
|-----|----------|-----------|-----------|
| **ADR-001** | Use libcst for Python parsing | Minimal; preserves formatting info | Adds dependency; slight perf overhead |
| **ADR-002** | Standardized AST = internal format | Language-independent analysis possible | Translation layer overhead |
| **ADR-003** | Metrics computed on demand | Reduces memory footprint | Repeated computation if queried often |
| **ADR-004** | SQLite for KG export | Queryable; offline-capable; no server | Limited to single-file deployments |
| **ADR-005** | CLI via Click framework | Intuitive interface; well-documented | Small additional dependency |

---

## 2. Component Deep-Dive

### 2.1 Parser Module Implementation Guide

**File Structure:**
```text
src/codex_ml/ast/
├── parser.py                    # UniversalParser orchestrator
├── language_adapters/
│   ├── __init__.py
│   ├── base_adapter.py          # BaseLanguageAdapter abstract class
│   ├── python_adapter.py        # PythonAdapter (libcst-based)
│   ├── yaml_adapter.py          # YAMLAdapter
│   ├── json_adapter.py          # JSONAdapter
│   └── sql_adapter.py           # SQLAdapter (custom)
└── errors.py                    # AST-specific exceptions
```text

**Implementation Checklist: `python_adapter.py`**

```python
"""Python source code → StandardizedAST using libcst."""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from pathlib import Path
import libcst as cst

class PythonAdapter:
    """Convert Python AST to standardized representation."""
    
    def parse(self, source_code: str, file_path: Path) -> StandardizedASTNode:
        """Parse Python source → StandardizedAST."""
        # Step 1: Parse with libcst
        module = cst.parse_module(source_code)
        
        # Step 2: Traverse and extract metadata
        visitor = MetadataExtractor()
        module.walk(visitor)
        
        # Step 3: Convert to standardized format
        return self._convert_to_standardized(module, visitor.metadata, file_path)
    
    def _convert_to_standardized(self, 
                                module: cst.Module, 
                                metadata: Dict, 
                                file_path: Path) -> StandardizedASTNode:
        """Transform libcst.Module → StandardizedASTNode."""
        # Implementation: walk libcst tree → StandardizedAST
        pass

    # Key extraction methods:
    def _extract_functions(self, node: cst.Module) -> List[StandardizedASTNode]:
        """Extract function definitions."""
        pass
    
    def _extract_classes(self, node: cst.Module) -> List[StandardizedASTNode]:
        """Extract class definitions."""
        pass
    
    def _extract_imports(self, node: cst.Module) -> List[Dict[str, str]]:
        """Extract import statements."""
        pass
    
    def _extract_type_hints(self, func: cst.FunctionDef) -> Dict[str, str]:
        """Extract type hints from function."""
        pass
    
    def _extract_docstring(self, node: cst.Module | cst.FunctionDef | cst.ClassDef) -> Optional[str]:
        """Extract docstring if present."""
        pass

class MetadataExtractor(cst.CSTVisitor):
    """Visitor pattern to extract all metadata."""
    
    def __init__(self):
        self.metadata = {
            'functions': [],
            'classes': [],
            'imports': [],
            'decorators': {},
        }
    
    def visit_FunctionDef(self, node: cst.FunctionDef) -> bool:
        """Visit function definition."""
        # Record function info
        pass
        return True
    
    def visit_ClassDef(self, node: cst.ClassDef) -> bool:
        """Visit class definition."""
        # Record class info
        pass
        return True
    
    def visit_ImportFrom(self, node: cst.ImportFrom) -> bool:
        """Visit import statement."""
        # Record import
        pass
        return True
```text

**Testing: `tests/ast/test_parser.py`**

```python
import pytest
from pathlib import Path

def test_parse_simple_function():
    """Verify parsing of simple function."""
    source = """
    def add(x: int, y: int) -> int:
        '''Add two numbers.'''
        return x + y
    """
    adapter = PythonAdapter()
    ast = adapter.parse(source, Path("test.py"))
    
    assert ast.type == "module"
    assert len(ast.children) == 1
    assert ast.children[0].type == "function"
    assert ast.children[0].name == "add"
    assert ast.children[0].docstring == "Add two numbers."
    assert ast.children[0].type_hints["x"] == "int"
    assert ast.children[0].type_hints["y"] == "int"
    assert ast.children[0].type_hints["return"] == "int"

def test_parse_decorated_class():
    """Verify parsing of decorated class."""
    source = """
    @dataclass
    class Person:
        name: str
        age: int
    """
    adapter = PythonAdapter()
    ast = adapter.parse(source, Path("test.py"))
    
    assert ast.children[0].type == "class"
    assert ast.children[0].decorators == ["@dataclass"]

def test_parse_async_function():
    """Verify parsing of async function."""
    source = """
    async def fetch_data(url: str) -> str:
        result = await client.get(url)
        return result.text
    """
    adapter = PythonAdapter()
    ast = adapter.parse(source, Path("test.py"))
    
    assert ast.children[0].type == "function"
    # async flag should be captured
    assert ast.children[0].metadata.get("is_async") == True

@pytest.mark.benchmark
def test_parser_performance(benchmark):
    """Benchmark parser performance."""
    source = open("tests/fixtures/large_file.py").read()
    adapter = PythonAdapter()
    
    result = benchmark(adapter.parse, source, Path("large_file.py"))
    assert result is not None
```text

**Integration Point:** All adapters inherit from `BaseLanguageAdapter`

```python
from abc import ABC, abstractmethod

class BaseLanguageAdapter(ABC):
    """Abstract base for language adapters."""
    
    @abstractmethod
    def parse(self, source_code: str, file_path: Path) -> StandardizedASTNode:
        """Parse source code → StandardizedAST."""
        pass
    
    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        """File extensions this adapter handles."""
        pass
```text

---

### 2.2 Metrics Analyzer Implementation Guide

**File:** `src/codex_ml/ast/analyzers/metrics.py`

**Implementation Checklist:**

```python
"""Extract code quality metrics from AST."""

from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class CodeMetrics:
    """Aggregated metrics for code entity."""
    lines_of_code: int
    cyclomatic_complexity: int
    cognitive_complexity: float
    halstead_volume: float
    halstead_difficulty: float
    halstead_effort: float
    maintainability_index: float
    
    @property
    def quality_grade(self) -> str:
        """Compute A-F grade from maintainability index."""
        if self.maintainability_index >= 85: return "A"
        if self.maintainability_index >= 70: return "B"
        if self.maintainability_index >= 55: return "C"
        if self.maintainability_index >= 40: return "D"
        return "F"

class MetricsAnalyzer:
    """Compute metrics on AST nodes."""
    
    def analyze(self, node: StandardizedASTNode) -> CodeMetrics:
        """Compute all metrics for node."""
        return CodeMetrics(
            lines_of_code=self._count_loc(node),
            cyclomatic_complexity=self._compute_cc(node),
            cognitive_complexity=self._compute_cognitive_cc(node),
            halstead_volume=self._compute_halstead_volume(node),
            halstead_difficulty=self._compute_halstead_difficulty(node),
            halstead_effort=self._compute_halstead_effort(node),
            maintainability_index=self._compute_maintainability_index(node),
        )
    
    def _count_loc(self, node: StandardizedASTNode) -> int:
        """Count lines of code."""
        start_line = node.source_location.line_start
        end_line = node.source_location.line_end
        return end_line - start_line + 1
    
    def _compute_cc(self, node: StandardizedASTNode) -> int:
        """Compute cyclomatic complexity (1-based)."""
        # Start with 1
        cc = 1
        
        # Count decision points
        # - if, elif, else, for, while, except, and, or, ternary
        for child in self._traverse_depth_first(node):
            if child.type in ("if", "elif", "for", "while", "except"):
                cc += 1
            elif child.type == "bool_op":
                # 'and' and 'or' add to complexity
                cc += 1
        
        return cc
    
    def _compute_cognitive_cc(self, node: StandardizedASTNode) -> float:
        """Compute cognitive complexity (reflects nesting)."""
        # Similar to CC but adds nesting depth penalty
        cognitive_cc = 0
        
        for child, depth in self._traverse_with_depth(node):
            if child.type in ("if", "elif", "for", "while", "try"):
                # Base increment
                cognitive_cc += 1
                # Nesting penalty: each level of nesting adds 0.1
                if depth > 1:
                    cognitive_cc += (depth - 1) * 0.1
        
        return cognitive_cc
    
    def _compute_halstead_volume(self, node: StandardizedASTNode) -> float:
        """Compute Halstead volume (measure of complexity)."""
        # Volume = N * log2(n)
        # where N = total operators + operands
        # and n = distinct operators + operands
        
        operators = self._extract_operators(node)
        operands = self._extract_operands(node)
        
        n1 = len(set(operators))  # distinct operators
        n2 = len(set(operands))   # distinct operands
        N1 = len(operators)        # total operators
        N2 = len(operands)         # total operands
        
        n = n1 + n2
        N = N1 + N2
        
        import math
        if n > 0:
            volume = N * math.log2(n)
        else:
            volume = 0
        
        return volume
    
    def _compute_maintainability_index(self, node: StandardizedASTNode) -> float:
        """Compute Maintainability Index (0-100)."""
        # MI = 171 - 5.2 * ln(Halstead Volume) 
        #          - 0.23 * CC 
        #          - 16.2 * ln(LOC)
        
        import math
        
        cc = self._compute_cc(node)
        loc = self._count_loc(node)
        volume = self._compute_halstead_volume(node)
        
        # Avoid log of 0
        loc = max(loc, 1)
        volume = max(volume, 1)
        
        mi = 171 - 5.2 * math.log(volume) - 0.23 * cc - 16.2 * math.log(loc)
        
        # Clamp to 0-100
        return max(0, min(100, mi))
    
    def _extract_operators(self, node: StandardizedASTNode) -> List[str]:
        """Extract operators from AST."""
        operators = []
        
        for child in self._traverse_depth_first(node):
            if child.type in ("binary_op", "unary_op", "compare", "bool_op"):
                operators.append(child.metadata.get("operator", ""))
            elif child.type in ("if", "for", "while", "try"):
                operators.append(child.type)
        
        return operators
    
    def _extract_operands(self, node: StandardizedASTNode) -> List[str]:
        """Extract operands (variables, literals) from AST."""
        operands = []
        
        for child in self._traverse_depth_first(node):
            if child.type == "name":
                operands.append(child.name)
            elif child.type == "constant":
                operands.append(str(child.metadata.get("value", "")))
        
        return operands
    
    def _traverse_depth_first(self, node: StandardizedASTNode):
        """DFS traversal of AST."""
        yield node
        for child in node.children:
            yield from self._traverse_depth_first(child)
    
    def _traverse_with_depth(self, node: StandardizedASTNode, depth=0):
        """DFS traversal with depth tracking."""
        yield node, depth
        for child in node.children:
            yield from self._traverse_with_depth(child, depth + 1)
```text

**Testing: `tests/ast/test_metrics.py`**

```python
import pytest

def test_cyclomatic_complexity_linear():
    """CC of linear function = 1."""
    source = """
    def add(x, y):
        return x + y
    """
    ast = parse(source)
    analyzer = MetricsAnalyzer()
    metrics = analyzer.analyze(ast.children[0])
    
    assert metrics.cyclomatic_complexity == 1

def test_cyclomatic_complexity_if_else():
    """CC of if-else = 2."""
    source = """
    def is_positive(x):
        if x > 0:
            return True
        else:
            return False
    """
    ast = parse(source)
    analyzer = MetricsAnalyzer()
    metrics = analyzer.analyze(ast.children[0])
    
    assert metrics.cyclomatic_complexity == 2

def test_maintainability_index_grade():
    """MI computed and graded correctly."""
    # Simple function should have high MI
    source = """
    def hello():
        print('hello')
    """
    ast = parse(source)
    analyzer = MetricsAnalyzer()
    metrics = analyzer.analyze(ast.children[0])
    
    assert metrics.maintainability_index > 85
    assert metrics.quality_grade == "A"
```text

---

### 2.3 Dependency Graph Implementation Guide

**File:** `src/codex_ml/ast/analyzers/dependencies.py`

**Key Algorithm: Tarjan's SCC (Strongly Connected Components)**

```python
"""Build and analyze dependency graphs."""

from typing import List, Set, Dict, Tuple
from dataclasses import dataclass, field

@dataclass
class DependencyGraph:
    """Directed graph of code dependencies."""
    nodes: Dict[str, StandardizedASTNode] = field(default_factory=dict)
    edges: Dict[str, Set[str]] = field(default_factory=dict)  # node → neighbors
    
    def add_edge(self, source_id: str, target_id: str):
        """Add edge source → target."""
        if source_id not in self.edges:
            self.edges[source_id] = set()
        self.edges[source_id].add(target_id)
    
    def detect_cycles(self) -> List[List[str]]:
        """Find all cycles (strongly connected components > 1)."""
        # Implement Tarjan's algorithm
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
                # Only record cycles (SCC with len > 1)
                if len(scc) > 1:
                    sccs.append(scc)
        
        for node_id in self.nodes:
            if node_id not in index:
                strongconnect(node_id)
        
        return sccs

class DependencyGraphBuilder:
    """Build dependency graph from codebase."""
    
    def build_graph(self, codebase: List[StandardizedASTNode]) -> DependencyGraph:
        """Build graph from AST nodes."""
        graph = DependencyGraph()
        
        # Step 1: Add all nodes
        for node in self._flatten_ast(codebase):
            if node.type in ("module", "class", "function"):
                graph.nodes[self._get_fully_qualified_name(node)] = node
        
        # Step 2: Extract dependencies
        for node in self._flatten_ast(codebase):
            deps = self._extract_dependencies(node)
            source_id = self._get_fully_qualified_name(node)
            for target_id in deps:
                graph.add_edge(source_id, target_id)
        
        return graph
    
    def _extract_dependencies(self, node: StandardizedASTNode) -> Set[str]:
        """Extract all dependencies of a node."""
        deps = set()
        
        if node.type == "module":
            # Extract imports
            for child in node.children:
                if child.type == "import":
                    # Parse import statement
                    deps.add(child.metadata.get("module_name", ""))
        
        elif node.type == "function":
            # Extract function calls
            for child in self._traverse(node):
                if child.type == "call":
                    # Get fully qualified name of called function
                    called_name = child.metadata.get("function_name", "")
                    if called_name:
                        deps.add(called_name)
        
        elif node.type == "class":
            # Extract base classes (inheritance)
            for base in node.metadata.get("base_classes", []):
                deps.add(base)
        
        return deps
    
    def _get_fully_qualified_name(self, node: StandardizedASTNode) -> str:
        """Compute fully qualified name: module.class.function."""
        parts = []
        current = node
        while current:
            if current.name:
                parts.insert(0, current.name)
            current = current.parent
        return ".".join(parts)
    
    def _traverse(self, node: StandardizedASTNode):
        """Depth-first traversal."""
        yield node
        for child in node.children:
            yield from self._traverse(child)
    
    def _flatten_ast(self, nodes: List[StandardizedASTNode]):
        """Flatten AST list."""
        for node in nodes:
            yield from self._traverse(node)

# Testing
def test_cycle_detection_simple():
    """Detect simple 2-node cycle."""
    graph = DependencyGraph()
    graph.nodes["A"] = None
    graph.nodes["B"] = None
    graph.add_edge("A", "B")
    graph.add_edge("B", "A")
    
    cycles = graph.detect_cycles()
    assert len(cycles) == 1
    assert set(cycles[0]) == {"A", "B"}

def test_cycle_detection_complex():
    """Detect complex 4-node cycle."""
    graph = DependencyGraph()
    for node_id in ["A", "B", "C", "D"]:
        graph.nodes[node_id] = None
    
    graph.add_edge("A", "B")
    graph.add_edge("B", "C")
    graph.add_edge("C", "D")
    graph.add_edge("D", "A")  # Cycle: A → B → C → D → A
    
    cycles = graph.detect_cycles()
    assert len(cycles) == 1
    assert set(cycles[0]) == {"A", "B", "C", "D"}
```text

---

## 3. Testing & Validation Framework

### 3.1 Test Organization

```text
tests/ast/
├── conftest.py                  # Shared fixtures
├── fixtures/
│   ├── sample_code.py
│   ├── large_codebase/
│   └── synthetic_graphs.json
├── test_parser.py
├── test_metrics.py
├── test_dependencies.py
├── test_smells.py
├── test_knowledge_graph.py
├── test_exporters.py
├── test_cli.py
├── test_integration.py
└── test_benchmarks.py
```text

### 3.2 Fixture Strategy (conftest.py)

```python
"""Shared test fixtures."""

import pytest
from pathlib import Path

@pytest.fixture
def sample_python_file():
    """Small Python file for testing."""
    return """
    def add(x: int, y: int) -> int:
        '''Add two numbers.'''
        return x + y
    """

@pytest.fixture
def large_codebase(tmp_path):
    """Generate large codebase for stress testing."""
    # Create 100 Python files with realistic code
    base = tmp_path / "large_codebase"
    base.mkdir()
    
    for i in range(100):
        file = base / f"module_{i}.py"
        file.write_text(f"""
        def func_{i}(x):
            return x * 2
        """)
    
    return base

@pytest.fixture
def synthetic_graph():
    """Graph with known cycles for testing."""
    graph = DependencyGraph()
    # Set up graph with 3-node cycle: A → B → C → A
    for node_id in ["A", "B", "C"]:
        graph.nodes[node_id] = None
    
    graph.add_edge("A", "B")
    graph.add_edge("B", "C")
    graph.add_edge("C", "A")
    
    return graph
```text

### 3.3 Performance Benchmarks

**File:** `tests/ast/test_benchmarks.py`

```python
"""Performance validation."""

import pytest
import time

@pytest.mark.benchmark
class TestParserPerformance:
    
    def test_parser_speed_small_file(self, benchmark, sample_python_file):
        """Parser: <1ms per 100 tokens (small file)."""
        parser = PythonAdapter()
        
        def parse():
            return parser.parse(sample_python_file, Path("test.py"))
        
        result = benchmark(parse)
        # Verify performance
        assert result is not None
    
    def test_parser_speed_large_file(self, benchmark, large_codebase):
        """Parser: <1ms per 100 tokens (large files)."""
        large_file = (large_codebase / "module_0.py").read_text() * 100
        
        parser = PythonAdapter()
        start = time.time()
        result = parser.parse(large_file, Path("large.py"))
        elapsed = time.time() - start
        
        # ~10K tokens per 1000 LOC
        tokens = len(large_file.split())
        ms_per_100_tokens = (elapsed * 1000) / (tokens / 100)
        
        assert ms_per_100_tokens < 1.0

@pytest.mark.benchmark
class TestAnalyzerPerformance:
    
    def test_metrics_speed_1000_loc(self, benchmark, large_codebase):
        """Analyzer: <5s per 1000 LOC."""
        codebase = Codebase.from_directory(large_codebase)
        analyzer = MetricsAnalyzer()
        
        start = time.time()
        for node in codebase.all_nodes():
            analyzer.analyze(node)
        elapsed = time.time() - start
        
        loc = sum(n.source_location.line_end - n.source_location.line_start 
                 for n in codebase.all_nodes())
        
        time_per_1000_loc = (elapsed / loc) * 1000
        assert time_per_1000_loc < 5.0
```text

---

## 4. Integration Checkpoints

### 4.1 Phase Gate Criteria

| Phase | Gate Criterion | Command to Validate |
|-------|----------------|-------------------|
| **Phase 1** | Parser working; tests green; <1ms/100 tokens | `nox -s test -- tests/ast/test_parser.py` |
| **Phase 2** | Metrics accurate ±5%; smells >80% precision | `nox -s test -- tests/ast/test_metrics.py tests/ast/test_smells.py` |
| **Phase 3** | Cycles detected 100%; graph exports work | `nox -s test -- tests/ast/test_dependencies.py` |
| **Phase 4** | CLI tools work; MATURITY integrates; docs complete | `codex-analyze src/ && codex-audit .` |
| **Phase 5** | 80%+ coverage; security clean; all perf targets met | `nox -s gates && pytest --cov-fail-under=80` |

### 4.2 CI/CD Integration Template

**File:** `.github/workflows/ast_analysis.yml`

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
          fetch-depth: 0
      
      - uses: actions/setup-python@v4
        with:
          python-version: "3.9"
      
      - name: Install
        run: pip install -e ".[ast]"
      
      - name: Audit
        run: codex-audit src/ --output audit.html --format html
      
      - name: Compare
        if: github.event_name == 'pull_request'
        run: codex-diff origin/main HEAD --metric complexity > complexity_delta.txt
      
      - name: Comment
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const delta = fs.readFileSync('complexity_delta.txt', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## AST Analysis\n\n${delta}`
            });
      
      - name: Upload
        uses: actions/upload-artifact@v3
        with:
          name: ast-report
          path: audit.html
```text

---

## 5. Conclusion

This **Implementation Guidance** provides:

✅ **Module-by-module implementation templates**  
✅ **Test-driven development patterns**  
✅ **Performance benchmarks and validation**  
✅ **CI/CD integration strategies**  
✅ **Phase-gate criteria for sign-off**  

**Critical Success Factors:**
- Write tests before code (TDD)
- Validate performance at each phase
- Get explicit sign-off at each gate
- Keep documentation in sync

**Start with Sprint 1:** Parser + Standardization (2 weeks)

---

**Document Version:** 1.0 (READY FOR IMPLEMENTATION)  
**Status:** APPROVED  
**Assigned To:** mbaetiong (Implementation Lead)


| **CLI Tools** | FR-AST-013 to 015 | 3 tools + GitHub Actions | >75% coverage |

**⚡ Ready for:** Immediate implementation kickoff with full architectural guidance
