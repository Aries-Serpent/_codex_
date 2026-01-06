# Phase 9.1 Execution Plan: Critical Path Coverage

**Version**: 1.0.0  
**Created**: Previous Cycle-12-31  
**Target**: 72% → 85% test coverage  
**Status**: 🚀 In Progress (10%)

---

## 🎯 Mission

Add 150-200 targeted tests to cover critical business logic paths, achieving 85% test coverage.

---

## 📊 Analysis Summary

### Current State
- **Source Files**: 938 files (src/, agents/, scripts/)
- **Existing Tests**: 1,588 test files
- **Current Coverage**: ~72% (estimated)
- **Target Coverage**: 85%
- **Gap**: 13 percentage points = ~150-200 tests

### Test Infrastructure
- **Frameworks**: pytest ✅, pytest-cov ✅, hypothesis ✅
- **Patterns**: Unit, integration, property-based, e2e
- **Standards**: Documented in test files
- **CI**: Automated via GitHub Actions

---

## 🗺️ Module Priority Matrix

### Priority 1: HIGH (Immediate) - 110-130 tests

#### 1. MCP Package System (`scripts/mcp/`) - 40-50 tests
**Current Coverage**: ~60% (estimated)  
**Target**: 90%+  
**Business Impact**: CRITICAL (production packaging system)

**Test Targets**:
- `select_components.py` (20-25 tests)
  - Topic-based file selection
  - Glob pattern matching with **
  - Recursive directory traversal
  - Edge cases: empty dirs, symlinks, large files
  - Error handling: missing topics.json, invalid patterns

- `package_flatten.sh` (10-15 tests)
  - Flat filename generation (path → flat)
  - Duplicate name handling
  - Manifest generation accuracy
  - ZIP archive integrity
  - Edge cases: special chars, long paths

- `mcp-package` CLI (10 tests)
  - --list flag validation
  - --topic parameter
  - --custom with glob_filters
  - --dry-run behavior
  - --output path handling
  - Error messages and exit codes

**Test Files to Create**:
- `tests/scripts/test_mcp_select_components.py`
- `tests/scripts/test_mcp_package_flatten.py`
- `tests/scripts/test_mcp_cli.py`

#### 2. Agent Orchestration (`agents/`) - 30-40 tests
**Current Coverage**: ~75% (estimated)  
**Target**: 92%+  
**Business Impact**: CRITICAL (core agent logic)

**Test Targets**:
- `workflow_navigator.py` (15-20 tests)
  - Workflow state transitions
  - create_workflow → get_workflow flow
  - Step execution and tracking
  - Error recovery in workflows
  - Concurrent workflow handling

- `quantum_game_theory.py` (10-15 tests)
  - Strategy state management
  - Decision state coherence calculations
  - Nash equilibrium computation
  - Edge cases: empty strategies, invalid probabilities

- Integration patterns (5 tests)
  - Agent composition
  - Cross-agent communication
  - State synchronization

**Test Files to Create**:
- `tests/agents/test_workflow_navigator_extended.py`
- `tests/agents/test_quantum_game_theory_edge_cases.py`
- `tests/agents/test_agent_integration_patterns.py`

#### 3. Core Pipeline (`src/codex/`) - 40-50 tests
**Current Coverage**: ~70% (estimated)  
**Target**: 88%+  
**Business Impact**: HIGH (code processing pipeline)

**Test Targets**:
- Code ingestion (15-20 tests)
  - File parsing and validation
  - AST generation
  - Syntax error handling
  - Multi-language support

- AST transformation (15-20 tests)
  - Node transformations
  - Pattern matching
  - Tree mutations
  - Optimization passes

- RAG retrieval (10 tests)
  - Query processing
  - Similarity search
  - Result ranking
  - Edge cases: empty corpus, no matches

**Test Files to Create**:
- `tests/src/test_code_ingestion.py`
- `tests/src/test_ast_transformation.py`
- `tests/src/test_rag_retrieval.py`

### Priority 2: MEDIUM (Important) - 40-50 tests

#### 4. Configuration Management - 20-30 tests
**Current Coverage**: ~65% (estimated)  
**Target**: 85%+  
**Business Impact**: MEDIUM (affects all components)

**Test Targets**:
- Config validation (10-15 tests)
  - Schema validation
  - Type checking
  - Required field enforcement
  - Default value application

- Config edge cases (10-15 tests)
  - Missing config files
  - Malformed JSON/YAML
  - Environment variable override
  - Merge behavior

**Test Files to Create**:
- `tests/config/test_config_validation.py`
- `tests/config/test_config_edge_cases.py`

#### 5. Error Handling Paths - 20 tests
**Current Coverage**: ~50% (estimated)  
**Target**: 80%+  
**Business Impact**: MEDIUM (reliability)

**Test Targets**:
- Exception paths (10 tests)
  - ValueError handling
  - IOError recovery
  - Type errors
  - Custom exceptions

- Error recovery (10 tests)
  - Retry logic
  - Fallback mechanisms
  - Graceful degradation
  - Error logging

**Test Files to Create**:
- `tests/error_handling/test_exception_paths.py`
- `tests/error_handling/test_error_recovery.py`

---

## 📝 Implementation Strategy

### Phase 1: MCP System Tests (Session 1, 40-50 tests)
1. Create test file structure
2. Implement select_components.py tests (20-25)
3. Implement package_flatten.sh tests (10-15)
4. Implement CLI tests (10)
5. Validate coverage improvement (+5-7%)

### Phase 2: Agent & Pipeline Tests (Session 2, 70-90 tests)
1. Implement agent orchestration tests (30-40)
2. Implement core pipeline tests (40-50)
3. Validate coverage improvement (+7-9%)

### Phase 3: Config & Error Tests (Session 3, 40-50 tests)
1. Implement configuration tests (20-30)
2. Implement error handling tests (20)
3. Final validation (coverage ≥ 85%)

---

## ✅ Success Criteria

### Phase 9.1 Complete When:
- [ ] 150-200 new tests added
- [ ] Coverage reaches ≥ 85% (stretch: 87%)
- [ ] All new tests passing (100% pass rate)
- [ ] No flaky tests introduced
- [ ] No performance regressions
- [ ] Documentation updated
- [ ] Self-review complete (5/5 passes, 0 concerns)

### Quality Standards:
- All tests must be deterministic
- Use fixtures for setup/teardown
- Follow existing test patterns
- Mock external dependencies
- Clear test names and docstrings
- Use `mental_mapping.set_clock()` for time-dependent tests

---

## 📊 Progress Tracking

| Priority | Module | Tests Planned | Tests Added | Coverage | Status |
|----------|--------|---------------|-------------|----------|--------|
| HIGH | MCP System | 40-50 | 0 | 60% → 90% | 🔴 Not Started |
| HIGH | Agent Orchestration | 30-40 | 0 | 75% → 92% | 🔴 Not Started |
| HIGH | Core Pipeline | 40-50 | 0 | 70% → 88% | 🔴 Not Started |
| MEDIUM | Configuration | 20-30 | 0 | 65% → 85% | 🔴 Not Started |
| MEDIUM | Error Handling | 20 | 0 | 50% → 80% | 🔴 Not Started |
| **TOTAL** | **All Modules** | **150-200** | **0** | **72% → 85%** | **🟡 10% (Plan)** |

---

## 🔧 Testing Patterns & Best Practices

### Test Structure
```python
import pytest
from agents.mental_mapping import set_clock, reset_clock

@pytest.fixture(scope="function")
def setup_test_environment():
    """Fixture for test environment setup."""
    # Setup
    set_clock("Previous Cycle-01-01T00:00:00Z")
    yield
    # Teardown
    reset_clock()

def test_feature_happy_path(setup_test_environment):
    """Test the happy path for feature X."""
    # Arrange
    input_data = create_test_data()
    
    # Act
    result = feature_function(input_data)
    
    # Assert
    assert result.status == "success"
    assert result.data is not None
```

### Edge Case Testing
```python
@pytest.mark.parametrize("input,expected", [
    ("", ValueError),  # Empty input
    (None, TypeError),  # None input
    ("x" * 10000, ValueError),  # Too large
    ("/../../etc/passwd", SecurityError),  # Path traversal
])
def test_feature_edge_cases(input, expected):
    """Test edge cases for feature X."""
    with pytest.raises(expected):
        feature_function(input)
```

### Integration Testing
```python
def test_end_to_end_workflow():
    """Test complete workflow from input to output."""
    # Step 1: Ingest
    data = ingest_code("sample.py")
    
    # Step 2: Transform
    ast = transform_code(data)
    
    # Step 3: Analyze
    results = analyze_ast(ast)
    
    # Assert complete flow
    assert results.is_valid
    assert len(results.findings) > 0
```

---

## 📚 Reference Documents

- [Coverage 100% Roadmap](COVERAGE_100_ROADMAP.md)
- [Testing Guide](../guides/TESTING_GUIDE.md)
- [Agent README](../../agents/README.md)
- [MCP System README](../../scripts/mcp/README.md)

---

**Status**: Execution plan complete ✅  
**Next**: Implement MCP system tests (Priority 1, HIGH)  
**Created**: Previous Cycle-12-31 00:55 UTC
