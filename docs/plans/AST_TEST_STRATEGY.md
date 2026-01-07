# AST Standardization - Test Strategy

**Generated**: 2025-11-09  
**Purpose**: Comprehensive testing strategy for AST standardization  
**Status**: PLANNING - Tests not yet implemented

---

## Test Coverage Targets

### Overall Coverage Goals

| Component | Unit Test Coverage | Integration Test Coverage | E2E Test Coverage |
|-----------|-------------------|--------------------------|-------------------|
| Parsers | ≥90% | ≥80% | ≥70% |
| Analysis | ≥85% | ≥75% | N/A |
| Graph | ≥90% | ≥80% | ≥70% |
| CLI | ≥70% | ≥90% | ≥90% |
| Plugins | ≥80% | ≥70% | N/A |

**Minimum Acceptable**: 80% overall coverage

---

## Test Fixtures

### Sample Code Fixtures

Key test fixtures for parser validation:
- **SIMPLE_FUNCTION**: Basic function with type hints
- **COMPLEX_FUNCTION**: High cyclomatic complexity (CC=8)
- **CLASS_WITH_METHODS**: Class hierarchy testing
- **CIRCULAR_IMPORT**: Circular dependency detection
- **MALFORMED_CODE**: Error handling verification
- **EDGE_CASE_EMPTY**: Empty file handling
- **EDGE_CASE_COMMENTS_ONLY**: Comment-only files

---

## Benchmark Specifications

### Performance Benchmarks

Required performance targets:
- **Small file (<100 LOC)**: <1ms parse time
- **Large file (1000 LOC)**: <5s parse time
- **Complexity analysis**: <100ms per file
- **Full codebase (10K LOC)**: <30s total analysis

---

## Edge Case Catalog

### Parser Edge Cases

| Edge Case | Expected Behavior |
|-----------|-------------------|
| Empty file | Return empty module node |
| Comments only | Return module with no functions |
| Syntax error | Raise ParseError or return None |
| Encoding issues | Try fallback encodings |
| Very long lines (>500 chars) | Parse correctly |
| Deep nesting (>20 levels) | Parse + report high complexity |
| Unicode identifiers | Parse correctly |
| Complex type hints | Extract correctly |
| Multiple decorators | Extract all decorators |
| Async/await | Mark as async |

### Analysis Edge Cases

| Edge Case | Expected Behavior |
|-----------|-------------------|
| Circular imports | Detect and report |
| Self-referential imports | Detect and report |
| Missing imports | Log warning, continue |
| Dynamic imports | Best effort extraction |
| Complexity at threshold | Handle boundary correctly |

---

## Test Organization

```text
tests/ast/
├── unit/                    # Unit tests (90%+ coverage target)
│   ├── core/
│   ├── parsers/
│   ├── analysis/
│   └── graph/
├── integration/             # Integration tests (80%+ coverage)
│   ├── test_parse_analyze_flow.py
│   ├── test_graph_building.py
│   └── test_metrics_aggregation.py
├── e2e/                     # End-to-end tests
│   ├── test_full_codebase_analysis.py
│   └── test_report_generation.py
├── benchmarks/              # Performance benchmarks
│   ├── test_parse_performance.py
│   └── test_analysis_performance.py
└── fixtures/                # Test fixtures
    ├── sample_code.py
    └── test_files/
```text

---

## Golden File Tests

Strategy for regression detection:
- Maintain "golden" reference outputs for known inputs
- Serialize AST to JSON and compare with reference
- Use parametrized tests for multiple test cases
- Update golden files only with explicit approval

---

## Coverage Validation

### Pre-merge Coverage Gate

```bash
pytest tests/ast/ \
  --cov=src/codex_ml/ast \
  --cov-report=term-missing \
  --cov-fail-under=80
```text

---

## Next Steps

1. ✅ AI Assistant autonomous test strategy review
2. ⏳ Create fixture library
3. ⏳ Implement unit tests (Sprint 1)
4. ⏳ Implement integration tests (Sprint 2)
5. ⏳ Create benchmark suite (Sprint 2)
6. ⏳ Implement golden file tests (Sprint 3)
7. ⏳ Achieve 80%+ coverage (Sprint 3)

**Status**: STRATEGY COMPLETE - Awaiting implementation approval  
**Owner**: QA Lead  
**Timeline**: Tests developed alongside implementation (Sprints 1-3)
