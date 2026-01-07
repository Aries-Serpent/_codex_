# AST Implementation Roadmap - Based on Deep Research Analysis

> **Source**: AST_BLOCKERS_DEEPRESEARCH_COMPREHENSIVE.md (777 lines, 25+ OSS references)  
> **Generated**: 2024-11-10  
> **Purpose**: Executable implementation roadmap for AST standardization based on comprehensive blocker research

---

## Executive Summary

**Context**: Deep research document analyzed 46 AST blockers with comprehensive solutions from OSS, academia, and internal repositories. This roadmap translates research into **actionable implementation phases** with clear go/no-go criteria.

**Key Findings**:
- **46 blockers** identified (15 critical, 23 implementation issues, 8 architectural challenges)
- **25+ OSS references** provide proven solutions
- **3 implementation phases** with distinct risk/effort profiles
- **Phase 1 (Quick Wins)**: 5 days, can implement immediately
- **Phase 2-3**: Require stakeholder approval and dedicated resources

**Recommendation**: ✅ **Implement Phase 1 Quick Wins ONLY** (5 days, low risk, high value)

---

## Implementation Assessment Matrix

### ✅ CAN IMPLEMENT NOW (Phase 1: Quick Wins)

| # | Item | Effort | Risk | Value | Blocker(s) Resolved |
|---|------|--------|------|-------|---------------------|
| 1 | Add core dependencies to pyproject.toml | 0.5d | LOW | HIGH | BLOCK-DEP-001, 003, 004 |
| 2 | Create StandardizedASTNode dataclass | 1d | LOW | HIGH | BLOCK-ARCH-001 |
| 3 | Implement basic DependencyGraph | 1d | LOW | MED | BLOCK-ARCH-002 |
| 4 | Add simple MetricsAggregator | 0.5d | LOW | MED | BLOCK-ARCH-003 |
| 5 | Create basic test suite (20+ tests) | 1d | LOW | HIGH | BLOCK-TEST-001 |
| 6 | Add documentation templates | 0.5d | LOW | MED | BLOCK-DOC-001 |
| 7 | Create minimal CLI interface | 0.5d | LOW | MED | BLOCK-CLI-001 |
| 8 | Add pre-commit hook skeleton | 0.25d | LOW | LOW | BLOCK-INT-001 |

**Total Phase 1**: 5.25 person-days  
**Blockers Resolved**: 8 of 46 (17%)  
**Risk**: LOW (no architectural changes, reversible)  
**Value**: HIGH (foundation for future work)

---

### ⚠️ REQUIRES STAKEHOLDER APPROVAL (Phase 2: Medium Scope)

| # | Item | Effort | Risk | Value | Prerequisites |
|---|------|--------|------|-------|---------------|
| 9 | Performance baseline benchmarks | 1d | MED | HIGH | Phase 1 complete |
| 10 | Streaming parser for large files | 2d | MED | MED | Phase 1 complete |
| 11 | Parallel processing framework | 2d | MED | HIGH | Phase 1 complete |
| 12 | Plugin system architecture | 2d | HIGH | MED | Architecture approval |
| 13 | Basic knowledge graph exporter | 1.5d | MED | LOW | Phase 1 complete |
| 14 | Integration with existing AST code | 3d | HIGH | HIGH | Migration plan |
| 15 | Security hardening (SQLite, input) | 1.5d | HIGH | HIGH | Security review |
| 16 | Comprehensive test suite (150+ tests) | 3d | MED | HIGH | Phase 1 complete |
| 17 | Enhanced CLI tools | 2d | MED | MED | Phase 1 complete |
| 18 | Code smell detector | 1.5d | MED | MED | Phase 1 complete |

**Total Phase 2**: 19.5 person-days  
**Blockers Resolved**: +15 of 46 (total 50%)  
**Risk**: MEDIUM (requires approval, testing, review)  
**Value**: HIGH (production-ready features)

---

### ❌ REQUIRES DEDICATED PROJECT (Phase 3: Full Implementation)

| Category | Items | Effort | Prerequisites |
|----------|-------|--------|---------------|
| Complete architecture | 5 items | 10d | Phases 1-2, architecture approval |
| Full metrics suite | 4 items | 8d | Phases 1-2, performance testing |
| Production CLI tools | 3 items | 6d | Phases 1-2, UX design |
| GitHub Actions integration | 3 items | 5d | Phases 1-2, CI/CD setup |
| Migration of existing code | 4 items | 12d | Phases 1-2, migration plan |
| Performance optimization | 3 items | 6d | Phases 1-2, benchmarks |
| Security audit | 2 items | 4d | Phases 1-2, security review |
| Full documentation | 3 items | 6d | Phases 1-2, content complete |

**Total Phase 3**: 57 person-days  
**Blockers Resolved**: +23 of 46 (total 100%)  
**Risk**: HIGH (major project, resources, timeline)  
**Value**: VERY HIGH (complete AST standardization)

---

## Phase 1: Quick Wins - Detailed Implementation Guide

### 1. Add Core Dependencies (0.5 days)

**Blockers Resolved**: BLOCK-DEP-001, BLOCK-DEP-003, BLOCK-DEP-004

**Implementation**:
```toml
# pyproject.toml
[project]
dependencies = [
    # ... existing ...
    "libcst>=1.0.0",     # Universal Python parser (MIT license)
    "radon>=6.0.0",      # Complexity metrics (MIT license)
    "parso>=0.8.0",      # Fallback parser (MIT license)
]

[project.optional-dependencies]
ast_extended = [
    "tree-sitter>=0.20.0",
    "tree-sitter-python>=0.20.0",
]
```text

**OSS References**:
- [libcst (Instagram)](https://github.com/Instagram/LibCST) - Universal Python parser
- [radon (Michele Lacchia)](https://github.com/rubik/radon) - Complexity analysis
- [parso (David Halter)](https://github.com/davidhalter/parso) - Fallback parser

**Verification**:
```bash
pip install -e .
python -c "import libcst; import radon; import parso; print('✓ Dependencies OK')"
```text

**Risk Mitigation**:
- All licenses are MIT (permissive)
- No breaking changes to existing code
- Optional dependencies isolate experimental features

---

### 2. Create StandardizedASTNode Dataclass (1 day)

**Blocker Resolved**: BLOCK-ARCH-001

**Implementation**:
```python
# src/codex/ast/node.py
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class SourceLocation:
    """Source code location."""
    file: str
    line: int
    column: int
    end_line: int
    end_column: int

@dataclass
class StandardizedASTNode:
    """Language-agnostic AST node representation.
    
    Design inspired by:
    - libcst.MetadataWrapper
    - tree-sitter Node
    - Roslyn SyntaxNode
    """
    node_id: str
    type: str  # "module", "function", "class", "import", etc.
    name: str
    source_location: SourceLocation
    children: List['StandardizedASTNode'] = field(default_factory=list)
    parent: Optional['StandardizedASTNode'] = None
    docstring: Optional[str] = None
    decorators: List[str] = field(default_factory=list)
    type_hints: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for JSON export."""
        return {
            "id": self.node_id,
            "type": self.type,
            "name": self.name,
            "location": {
                "file": self.source_location.file,
                "start": (self.source_location.line, self.source_location.column),
                "end": (self.source_location.end_line, self.source_location.end_column),
            },
            "children": [child.node_id for child in self.children],
            "docstring": self.docstring,
            "decorators": self.decorators,
            "type_hints": self.type_hints,
            "metadata": self.metadata,
        }
    
    def walk(self):
        """Depth-first traversal of tree."""
        yield self
        for child in self.children:
            yield from child.walk()
```text

**OSS References**:
- [libcst MetadataWrapper](https://libcst.readthedocs.io/en/latest/metadata.html)
- [tree-sitter Node API](https://tree-sitter.github.io/tree-sitter/using-parsers#walking-trees-with-tree-cursors)
- [Roslyn SyntaxNode](https://github.com/dotnet/roslyn/blob/main/docs/wiki/Roslyn-Overview.md)

**Tests**:
```python
# tests/ast/test_node.py
def test_standardized_node_creation():
    """Test basic node creation."""
    loc = SourceLocation("test.py", 1, 0, 1, 10)
    node = StandardizedASTNode(
        node_id="func_1",
        type="function",
        name="test_func",
        source_location=loc
    )
    assert node.node_id == "func_1"
    assert node.type == "function"

def test_node_serialization():
    """Test node serialization to dict."""
    loc = SourceLocation("test.py", 1, 0, 1, 10)
    node = StandardizedASTNode("n1", "function", "test", loc)
    data = node.to_dict()
    assert data["id"] == "n1"
    assert data["type"] == "function"
```text

---

### 3. Implement Basic DependencyGraph (1 day)

**Blocker Resolved**: BLOCK-ARCH-002

**Implementation**:
```python
# src/codex/ast/graph.py
from typing import Dict, List, Set
from collections import defaultdict

class DependencyGraph:
    """Directed graph with cycle detection using Tarjan's SCC algorithm.
    
    Reference: NetworkX strongly_connected_components
    https://github.com/networkx/networkx/blob/main/networkx/algorithms/components/strongly_connected.py
    """
    
    def __init__(self):
        self.nodes: Set[str] = set()
        self.edges: Dict[str, Set[str]] = defaultdict(set)
    
    def add_node(self, node_id: str):
        """Add a node to the graph."""
        self.nodes.add(node_id)
    
    def add_edge(self, source: str, target: str):
        """Add a directed edge from source to target."""
        self.nodes.add(source)
        self.nodes.add(target)
        self.edges[source].add(target)
    
    def detect_cycles(self) -> List[List[str]]:
        """Find strongly connected components (cycles) using Tarjan's algorithm.
        
        Returns:
            List of cycles (each cycle is a list of node IDs)
        """
        index_counter = [0]
        stack = []
        lowlinks = {}
        index = {}
        on_stack = {}
        sccs = []
        
        def strongconnect(node_id: str):
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
                
                if len(scc) > 1:  # Only record actual cycles
                    sccs.append(scc)
        
        for node_id in self.nodes:
            if node_id not in index:
                strongconnect(node_id)
        
        return sccs
    
    def topological_sort(self) -> List[str]:
        """Return topological ordering if DAG, else raise ValueError."""
        cycles = self.detect_cycles()
        if cycles:
            raise ValueError(f"Graph has cycles: {cycles}")
        
        visited = set()
        stack = []
        
        def dfs(node_id: str):
            visited.add(node_id)
            for target in self.edges.get(node_id, set()):
                if target not in visited:
                    dfs(target)
            stack.append(node_id)
        
        for node_id in self.nodes:
            if node_id not in visited:
                dfs(node_id)
        
        return stack[::-1]
```text

**OSS References**:
- [NetworkX Tarjan's SCC](https://github.com/networkx/networkx/blob/main/networkx/algorithms/components/strongly_connected.py)
- [Wikipedia: Tarjan's Algorithm](https://en.wikipedia.org/wiki/Tarjan%27s_strongly_connected_components_algorithm)

**Tests**:
```python
# tests/ast/test_graph.py
def test_cycle_detection():
    """Test cycle detection with simple cycle."""
    graph = DependencyGraph()
    graph.add_edge("A", "B")
    graph.add_edge("B", "C")
    graph.add_edge("C", "A")  # Creates cycle
    
    cycles = graph.detect_cycles()
    assert len(cycles) == 1
    assert set(cycles[0]) == {"A", "B", "C"}

def test_topological_sort_dag():
    """Test topological sort on DAG."""
    graph = DependencyGraph()
    graph.add_edge("A", "B")
    graph.add_edge("B", "C")
    
    order = graph.topological_sort()
    assert order.index("A") < order.index("B")
    assert order.index("B") < order.index("C")
```text

---

### 4. Add Simple MetricsAggregator (0.5 days)

**Blocker Resolved**: BLOCK-ARCH-003

**Implementation**:
```python
# src/codex/ast/metrics.py
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class CodeMetrics:
    """Aggregated code metrics."""
    cyclomatic_complexity: int
    cognitive_complexity: int
    lines_of_code: int
    comment_lines: int
    maintainability_index: float
    
    def to_dict(self) -> Dict:
        return {
            "cyclomatic": self.cyclomatic_complexity,
            "cognitive": self.cognitive_complexity,
            "loc": self.lines_of_code,
            "comments": self.comment_lines,
            "maintainability": self.maintainability_index,
        }

class MetricsAggregator:
    """Aggregate metrics from multiple sources."""
    
    def aggregate(self, metrics_list: List[CodeMetrics]) -> CodeMetrics:
        """Aggregate multiple metrics into summary."""
        if not metrics_list:
            return CodeMetrics(0, 0, 0, 0, 100.0)
        
        return CodeMetrics(
            cyclomatic_complexity=sum(m.cyclomatic_complexity for m in metrics_list),
            cognitive_complexity=sum(m.cognitive_complexity for m in metrics_list),
            lines_of_code=sum(m.lines_of_code for m in metrics_list),
            comment_lines=sum(m.comment_lines for m in metrics_list),
            maintainability_index=sum(m.maintainability_index for m in metrics_list) / len(metrics_list),
        )
```text

**Tests**:
```python
# tests/ast/test_metrics.py
def test_metrics_aggregation():
    """Test basic metrics aggregation."""
    m1 = CodeMetrics(5, 3, 100, 10, 80.0)
    m2 = CodeMetrics(3, 2, 50, 5, 90.0)
    
    agg = MetricsAggregator()
    result = agg.aggregate([m1, m2])
    
    assert result.cyclomatic_complexity == 8
    assert result.lines_of_code == 150
    assert result.maintainability_index == 85.0
```text

---

### 5. Create Basic Test Suite (1 day)

**Blocker Resolved**: BLOCK-TEST-001

**Test Coverage Plan**:
- `tests/ast/test_node.py` - 5 tests (node creation, serialization, traversal)
- `tests/ast/test_graph.py` - 5 tests (graph operations, cycle detection, topological sort)
- `tests/ast/test_metrics.py` - 3 tests (metrics creation, aggregation)
- `tests/ast/test_integration.py` - 7 tests (end-to-end workflows)

**Total**: 20 tests, targeting 80%+ coverage of new code

---

### 6-8. Documentation, CLI, Pre-commit (1.25 days)

Minimal implementations to complete Phase 1 foundation.

---

## Go/No-Go Decision Framework

### ✅ GO Criteria for Phase 1

| Criterion | Status | Notes |
|-----------|--------|-------|
| Effort < 1 week | ✅ YES | 5.25 days |
| No architectural approval needed | ✅ YES | Additive only, no changes |
| No external dependencies (license issues) | ✅ YES | All MIT licensed |
| Aligns with maturity goals | ✅ YES | Improves code quality |
| Provides immediate value | ✅ YES | Foundation + 8 blockers resolved |
| Reversible if needed | ✅ YES | Can be removed easily |
| Does not disrupt current work | ✅ YES | 75% maturity complete, no conflict |

**Decision**: ✅ **RECOMMEND GO FOR PHASE 1**

---

### ❌ NO-GO Criteria for Phase 2-3

| Criterion | Status | Notes |
|-----------|--------|-------|
| Requires stakeholder approval | ❌ BLOCK | Need architecture review |
| Needs dedicated engineering | ❌ BLOCK | 19.5 - 57 days effort |
| Performance impact assessment | ❌ BLOCK | Benchmarking required |
| Security review required | ❌ BLOCK | SQLite, input validation |
| Beyond current scope | ❌ BLOCK | 75% maturity work complete |

**Decision**: ❌ **DEFER PHASE 2-3 TO DEDICATED PROJECT**

---

## Success Metrics (Phase 1 Only)

| Metric | Target | Verification Method |
|--------|--------|-------------------|
| Dependencies installed | 100% | `pip check && python -c "import libcst, radon, parso"` |
| Test coverage (new code) | >80% | `pytest --cov=codex.ast tests/ast/` |
| Tests passing | 100% | `pytest tests/ast/ -v` |
| Documentation complete | 100% | All classes/functions have docstrings |
| No breaking changes | 100% | Existing tests still pass |
| Blockers resolved | 8 of 46 | Manual verification against blocker list |

---

## Risk Assessment

### Phase 1 Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Dependency conflicts | LOW | MED | Pin versions, test in isolation |
| Performance regression | LOW | LOW | No changes to existing code paths |
| Code complexity increase | LOW | LOW | Minimal, well-documented code |
| Integration issues | LOW | MED | Isolated namespace, optional import |

### Phase 2-3 Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Scope creep | HIGH | HIGH | Strict phase boundaries, stakeholder alignment |
| Performance degradation | MED | HIGH | Comprehensive benchmarking required |
| Security vulnerabilities | MED | HIGH | Security audit before production |
| Resource availability | HIGH | HIGH | Dedicated team allocation required |

---

## Recommendations

### Immediate (Pre-commit -1-0)

1. **✅ APPROVE Phase 1 Quick Wins** (5 days, low risk, high value)
   - Add dependencies to pyproject.toml
   - Create basic AST infrastructure (node, graph, metrics)
   - Add 20+ tests
   - Update documentation

2. **⏸️ HOLD Phase 2-3** for future dedicated project
   - Requires stakeholder alignment
   - Needs dedicated resources (3-8 weeks)
   - Performance and security review required

### Short-term (Pre-commit 1-4)

- Execute Phase 1 implementation
- Verify all success metrics met
- Document lessons learned
- Prepare Phase 2 proposal (if desired)

### Long-term (Months 1-3)

- Review Phase 1 outcomes
- Decide on Phase 2-3 project funding
- Allocate dedicated engineering resources
- Execute full AST standardization project

---

## Conclusion

**Phase 1 Quick Wins** represents the **optimal balance** of:
- ✅ Low effort (5 days)
- ✅ Low risk (reversible, additive)
- ✅ High value (foundation, 8 blockers resolved)
- ✅ Aligned with current goals (maturity improvement)

**Recommendation**: Execute Phase 1 immediately, defer Phase 2-3 to dedicated project.

**Total Planning Documentation**: 14 documents, 4,200+ lines
- Maturity improvement (5 docs)
- AST Phase 0 planning (7 docs)
- AST engineering guide (1 doc)
- AST implementation roadmap (1 doc - THIS)

**Status**: Ready for Phase 1 execution upon stakeholder approval.
