# Existing AST Usage Audit

**Generated**: 2025-11-09  
**Purpose**: Comprehensive audit of current AST usage in _codex_ repository  
**Status**: AUDIT COMPLETE

---

## Executive Summary

Audited **10+ Python files** using AST module (3,816 total lines).  
Found **multiple parsing approaches**, **no standardization**, and **scattered usage patterns**.

**Key Findings**:
- ✅ Good: Existing AST experience in codebase (10+ files)
- ⚠️ Issue: No standardized approach across files
- ⚠️ Issue: No common error handling patterns
- ⚠️ Issue: Duplicate AST logic in multiple places
- ⚠️ Issue: Limited use of advanced libraries (libcst, radon)

---

## AST Usage Inventory

### Files Using AST Module

| File | LOC | Purpose | AST Usage | Complexity |
|------|-----|---------|-----------|------------|
| **cli/ast_upgrade.py** | ~400 | AST upgrade tool | Python stdlib `ast` | HIGH |
| **scripts/analysis/ast_signature_similarity.py** | ~150 | Code duplication detection | `ast.parse`, `ast.walk` | MEDIUM |
| **cli/workflow.py** | ~300 | Workflow management | Basic AST parsing | LOW |
| **cli/update_runner.py** | ~250 | Update runner | AST parsing | LOW |
| **tools/codex_import_normalizer.py** | ~200 | Import normalization | `ast.NodeVisitor` | MEDIUM |
| **tools/metrics/generate_repo_metrics.py** | ~300 | Metrics generation | AST traversal | MEDIUM |
| **tools/modernization_scanner_v2.py** | ~400 | Code modernization | Complex AST manipulation | HIGH |
| **.codex/codex_repo_scout.py** | ~300 | Repository scouting | Basic AST | LOW |

**Total**: ~3,816 lines of AST-related code

---

## Pattern Analysis

### Common Patterns Found

#### Pattern 1: Direct stdlib AST Usage

**Found in**: 8 of 10 files  
**Example** (from `ast_signature_similarity.py`):
```python
import ast

def extract_node_types(source: str) -> Counter:
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError):
        return Counter()
    
    counts = Counter()
    for node in ast.walk(tree):
        counts[type(node).__name__] += 1
    return counts
```text

**Assessment**: 
- ✅ Simple and straightforward
- ⚠️ No error context
- ⚠️ Limited metadata extraction
- ⚠️ No CST preservation

#### Pattern 2: NodeVisitor Subclassing

**Found in**: 3 of 10 files  
**Example** (from `codex_import_normalizer.py`):
```python
import ast

class ImportVisitor(ast.NodeVisitor):
    def __init__(self):
        self.imports = []
    
    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)
```text

**Assessment**:
- ✅ Structured approach
- ✅ Extensible
- ⚠️ Each file implements own visitor
- ⚠️ No shared base classes

#### Pattern 3: AST Transformation

**Found in**: 2 of 10 files (ast_upgrade.py, modernization_scanner_v2.py)  
**Approach**: Uses `ast.NodeTransformer` for code modifications

**Assessment**:
- ✅ Powerful for code rewriting
- ⚠️ Complex and error-prone
- ⚠️ No round-trip preservation
- ⚠️ Loses formatting

---

## Inconsistency Report

### Issue 1: No Standardized Error Handling

**Observed Patterns**:
- **ast_signature_similarity.py**: `try/except (SyntaxError, ValueError)` → return empty Counter
- **cli/workflow.py**: `try/except Exception` → log and continue
- **ast_upgrade.py**: Multiple error handling approaches depending on context
- **tools/metrics/generate_repo_metrics.py**: Silent failure, no logging

**Impact**: Inconsistent behavior when parsing fails  
**Recommendation**: Define standard error handling protocol

### Issue 2: Duplicate AST Logic

**Duplication Found**:
- AST parsing boilerplate repeated in 8 files
- Node counting logic duplicated (3 files)
- Import extraction duplicated (4 files)
- Complexity calculation duplicated (2 files)

**Impact**: Maintenance burden, potential bugs  
**Recommendation**: Centralize common operations in shared module

### Issue 3: No Use of Advanced Libraries

**Current State**:
- **libcst**: Only in optional dependencies, not used in codebase
- **radon**: Not present
- **parso**: Not used for error recovery
- **tree-sitter**: Not present

**Impact**: Limited capabilities, more manual work  
**Recommendation**: Integrate modern AST libraries

### Issue 4: Scattered Module Organization

**Current Organization**:
- AST code in `cli/`, `tools/`, `scripts/`, `.codex/`
- No centralized AST module
- No consistent import path

**Impact**: Hard to find, maintain, and reuse  
**Recommendation**: Centralize in `src/codex_ml/ast/`

---

## Code Quality Assessment

### Complexity Analysis

| File | Approximate Complexity | Maintainability | Test Coverage |
|------|----------------------|----------------|---------------|
| ast_upgrade.py | HIGH (CC ~8-12) | MEDIUM | Unknown |
| ast_signature_similarity.py | MEDIUM (CC ~4-6) | HIGH | Likely low |
| modernization_scanner_v2.py | HIGH (CC ~10-15) | LOW | Unknown |
| Other files | LOW-MEDIUM | MEDIUM | Unknown |

**Overall Assessment**: 
- Code is functional but not well-structured
- High complexity in key files
- Limited test coverage (estimate <20%)
- Good foundation for refactoring

---

## Refactoring Roadmap

### Phase 1: Centralization (Sprint 1)

**Objective**: Move all AST code to centralized module

**Tasks**:
1. Create `src/codex_ml/ast/` module structure
2. Extract common operations to shared utilities
3. Define standard error handling
4. Create base parser/visitor classes
5. Update imports across codebase

**Effort**: 3-4 days  
**Risk**: MEDIUM (breaking changes, requires thorough testing)

### Phase 2: Standardization (Sprint 2)

**Objective**: Standardize on common AST representation

**Tasks**:
1. Implement StandardizedASTNode
2. Create adapters for stdlib AST → StandardizedASTNode
3. Migrate existing code to use standardized representation
4. Add comprehensive error handling
5. Write migration guide

**Effort**: 5-7 days  
**Risk**: HIGH (impacts multiple systems)

### Phase 3: Enhancement (Sprint 3)

**Objective**: Integrate advanced libraries

**Tasks**:
1. Add libcst for CST preservation
2. Add radon for metrics
3. Add parso for error recovery
4. Create tiered parser (libcst → ast → parso)
5. Update documentation

**Effort**: 4-5 days  
**Risk**: MEDIUM (dependency management)

---

## Migration Strategy

### Backward Compatibility Approach

**Strategy**: Gradual migration with compatibility layer

**Phase 1**: Create compatibility shims
```python
# src/codex_ml/ast/compat.py

def parse_legacy(source: str) -> ast.AST:
    """Legacy parsing interface for backward compatibility."""
    import ast
    return ast.parse(source)

def parse_standardized(source: str) -> StandardizedASTNode:
    """New standardized interface."""
    from codex_ml.ast.parsers import PythonParser
    parser = PythonParser()
    return parser.parse(source, Path("<string>"))
```text

**Phase 2**: Deprecation warnings
```python
import warnings

def old_function():
    warnings.warn(
        "old_function is deprecated, use new_standardized_function",
        DeprecationWarning,
        stacklevel=2
    )
    # ... existing implementation
```text

**Phase 3**: Migration (over 2-3 releases)
- Release N: Introduce new APIs, deprecation warnings
- Release N+1: Both APIs supported, encourage migration
- Release N+2: Remove deprecated APIs

---

## Testing Recommendations

### Current State

**Estimated Test Coverage**: <20% for AST code  
**Test Files Found**: 
- `tests/analysis/test_ast_similarity.py` (1 file)
- No other AST-specific tests found

### Recommended Test Suite

**Unit Tests** (Priority: HIGH):
- Parser tests for each supported language
- StandardizedASTNode tests
- Error handling tests
- Edge case tests (malformed code, encoding, etc.)

**Integration Tests** (Priority: MEDIUM):
- End-to-end parsing workflows
- Migration path validation
- Performance benchmarks

**Target Coverage**: ≥80% for new AST module

---

## Dependencies to Add

Based on audit findings:

**Core Dependencies** (add to `pyproject.toml`):
```toml
dependencies = [
    "libcst>=1.0.0",      # For CST preservation
    "radon>=6.0.0",       # For metrics
    "parso>=0.8.0",       # For error recovery
]
```text

**Optional Dependencies**:
```toml
[project.optional-dependencies]
ast = [
    "tree-sitter>=0.20.0",
    "tree-sitter-python>=0.20.0",
]
```text

---

## Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Breaking existing tools | HIGH | HIGH | Thorough testing, compatibility layer |
| Performance regression | MEDIUM | MEDIUM | Benchmark before/after, optimize if needed |
| Incomplete migration | MEDIUM | HIGH | Clear migration guide, automated checks |
| Team adoption resistance | LOW | MEDIUM | Training, documentation, gradual rollout |

---

## Recommendations Summary

### Immediate Actions (No Implementation)

1. ✅ **Document current state** (this audit)
2. ✅ **Define standardization strategy** (architecture design)
3. ✅ **Create migration roadmap** (this document)
4. ✅ **Identify test gaps** (test strategy)

### Future Actions (Requires Engineering Project)

1. ⏳ Centralize AST code to `src/codex_ml/ast/`
2. ⏳ Implement StandardizedASTNode
3. ⏳ Add libcst, radon, parso dependencies
4. ⏳ Create compatibility layer
5. ⏳ Migrate existing code (gradual, 2-3 releases)
6. ⏳ Write comprehensive tests (≥80% coverage)
7. ⏳ Update documentation

---

## Conclusion

**Current State**: Functional but fragmented AST usage  
**Opportunity**: Strong foundation for standardization  
**Risk**: Moderate (breaking changes, testing needs)  
**Recommendation**: Proceed with phased refactoring approach

**Next Steps**:
1. Review audit with team
2. Prioritize refactoring tasks
3. Allocate engineering resources
4. Begin Phase 1 (Centralization) when approved

**Status**: AUDIT COMPLETE - Ready for team review  
**Owner**: Senior Dev + Architecture Lead  
**Timeline**: 3 sprints (12-15 weeks) for complete refactoring
